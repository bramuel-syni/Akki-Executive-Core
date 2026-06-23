"""Phase 4.2 — internal HTTP transport for cross-context contracts.

Each context-bound FastAPI app (`synisense_app`, `solva_app`,
`akki_app`) mounts an instance of this router under
`/api/internal/v1/{context}/*`. External contexts reach it via
`httpx` + a shared secret in the `X-Internal-Auth` header.

Endpoints are excluded from the public OpenAPI surface
(`include_in_schema=False`) so the master `/api/openapi.json`
hash remains byte-identical to Phase 4.1.

Generic dispatch shape:
    POST /api/internal/v1/{context}/method/{method_name}
    Header: X-Internal-Auth: <INTERNAL_TRANSPORT_SECRET>
    Body  : {"<kwarg1>": ..., "<kwarg2>": ..., ...}
    Resp  : {"result": <serialized_value>}

The dispatch:
    * Validates the secret (401 if missing/wrong).
    * Looks up the method on the in-process adapter for the
      named context (404 if not found / starts with `_`).
    * Calls `await adapter.<method_name>(**body)`.
    * Returns `{"result": dataclass.asdict(result)}` (or list / dict /
      primitive — whatever the method returned).

The matching `_adapters/_http_client.py` httpx adapters know each
method's return type and reconstruct the DTO from the JSON dict.

Phase 4.2 ships with `BOUNDED_CONTEXT_TRANSPORT=inproc` as the
default — these endpoints exist but are not exercised. Set the env
var to `http` to flip every `get_synisense()` / `get_solva()` /
`get_akki()` accessor to its HTTP variant. Phase 4.3 will run each
app on its own port, at which point this transport becomes the
real cross-context boundary.
"""
from __future__ import annotations

import dataclasses
import logging
import os
from typing import Any, Awaitable, Callable, Dict

from fastapi import APIRouter, Header, HTTPException, status

logger = logging.getLogger("contracts.internal_transport")


INTERNAL_TRANSPORT_SECRET = os.environ.get("INTERNAL_TRANSPORT_SECRET", "")


def _auth_or_403(x_internal_auth: str | None) -> None:
    """Raise 401/503 unless the request carries a valid secret."""
    if not INTERNAL_TRANSPORT_SECRET:
        # Fail closed — the transport must be explicitly enabled.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal transport not configured (set INTERNAL_TRANSPORT_SECRET).",
        )
    if not x_internal_auth or x_internal_auth != INTERNAL_TRANSPORT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Internal transport: unauthorised.",
        )


def serialize_value(value: Any) -> Any:
    """Recursively convert dataclasses / lists / dicts / primitives to
    JSON-safe values. Mirror by `_http_client.deserialize_value`.
    """
    if value is None:
        return None
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if isinstance(value, list):
        return [serialize_value(x) for x in value]
    if isinstance(value, tuple):
        return [serialize_value(x) for x in value]
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, (str, int, float, bool)):
        return value
    # Last resort — best-effort string repr (rare).
    return str(value)


def make_internal_router(
    *,
    context_name: str,
    adapter_factory: Callable[[], Any],
) -> APIRouter:
    """Build an APIRouter that dispatches POSTs to the named context's
    in-process adapter. `adapter_factory` is `lambda: InProcessAkkiAdapter()`
    or similar.
    """
    router = APIRouter(
        prefix=f"/api/internal/v1/{context_name}",
        tags=[f"internal-{context_name}"],
        include_in_schema=False,
    )

    @router.post(
        "/method/{method_name}",
        include_in_schema=False,
    )
    async def _dispatch(
        method_name: str,
        body: Dict[str, Any],
        x_internal_auth: str | None = Header(default=None, alias="X-Internal-Auth"),
    ) -> Dict[str, Any]:
        _auth_or_403(x_internal_auth)
        if method_name.startswith("_") or "." in method_name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Method {method_name!r} not on contract.",
            )
        adapter = adapter_factory()
        method: Callable[..., Awaitable[Any]] | None = getattr(adapter, method_name, None)
        if method is None or not callable(method):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Method {method_name!r} not on {context_name} contract.",
            )
        kwargs = body or {}
        try:
            result = await method(**kwargs)
        except TypeError as exc:
            # Keyword-mismatch / shape error.
            logger.exception(
                "Internal transport: %s.%s call failed with TypeError",
                context_name,
                method_name,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bad call shape for {context_name}.{method_name}: {exc}",
            ) from exc
        return {"result": serialize_value(result)}

    return router


__all__ = [
    "INTERNAL_TRANSPORT_SECRET",
    "make_internal_router",
    "serialize_value",
]
