"""Phase 4.2 — HTTP transport adapters for cross-context contracts.

`HTTPAkkiAdapter` / `HTTPSyniSenseAdapter` / `HTTPSolvaAdapter` share
this base. Each method on the in-process adapter has a parallel
method here that:

  1. Sends the kwargs as JSON to the matching internal endpoint
     (`POST /api/internal/v1/<context>/method/<name>`) on the same
     uvicorn host (Phase 4.2; Phase 4.3 splits hosts).
  2. Reads `{"result": ...}` and reconstructs the DTO.
  3. On transient failure, retries up to 3 times with jittered
     exponential back-off. On permanent failure, surfaces the
     exception (no silent fallback to direct DB — Honesty Protocol).

Activated by `BOUNDED_CONTEXT_TRANSPORT=http` in the environment.
The shared secret `INTERNAL_TRANSPORT_SECRET` is required on both
ends.

The base accepts a `dto_classes` map keyed by method name — each
entry is the return type's dataclass. Lists return a list of that
dataclass; `Optional[X]` returns either `X` or `None`. The
dispatcher introspects the in-process adapter's annotations once at
class load to build this map automatically.

Phase 5.5.2 (2026-06-24) — kwargs sanitization. When a contract
method accepts a Pydantic model (`narrate_analysis.workbook_analysis`
is the known site; future-Pydantic-kwarg sites are also covered),
`json=kwargs` would raise `TypeError` because httpx's encoder
doesn't know how to serialize `BaseModel`. The central fix is the
`_sanitize_kwargs_for_json` helper that walks `kwargs` recursively
and converts `BaseModel` → `.model_dump(mode='json')` dict +
dataclass → `dataclasses.asdict` dict. Plain dicts / primitives /
lists pass through unchanged. Build-breaking invariant at
`tests/invariants/test_invariant_http_transport_pydantic_kwargs.py`.
"""
from __future__ import annotations

import asyncio
import dataclasses
import inspect
import logging
import os
import random
import typing
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Type

import httpx
from pydantic import BaseModel

logger = logging.getLogger("contracts.http_transport")


# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────
DEFAULT_BASE_URL = os.environ.get(
    "INTERNAL_TRANSPORT_BASE_URL",
    "http://127.0.0.1:8001",
)
DEFAULT_TIMEOUT_S = float(os.environ.get("INTERNAL_TRANSPORT_TIMEOUT_S", "5.0"))
DEFAULT_RETRIES = int(os.environ.get("INTERNAL_TRANSPORT_RETRIES", "3"))
DEFAULT_BACKOFF_BASE_S = 0.1


def _per_context_base_url(context_name: str) -> str:
    """Resolve the per-context base URL.

    Phase 4.3 adds per-context base URL overrides so the three apps can
    eventually run as independent uvicorn processes on distinct ports:

      • ``INTERNAL_TRANSPORT_BASE_URL_AKKI``      (default port 8001)
      • ``INTERNAL_TRANSPORT_BASE_URL_SYNISENSE`` (default port 8011)
      • ``INTERNAL_TRANSPORT_BASE_URL_SOLVA``     (default port 8012)

    When the per-context env var is empty/absent, falls back to the
    composite ``INTERNAL_TRANSPORT_BASE_URL`` (loopback to the bundled
    process — the supervisor-locked default in Phase 4.3).
    """
    env_key = f"INTERNAL_TRANSPORT_BASE_URL_{context_name.upper()}"
    return os.environ.get(env_key, "").strip() or DEFAULT_BASE_URL


def _internal_secret() -> str:
    return os.environ.get("INTERNAL_TRANSPORT_SECRET", "")


def _is_optional(annotation: Any) -> Tuple[bool, Any]:
    """If `annotation` is `Optional[X]` (= `Union[X, None]`), return `(True, X)`. Otherwise `(False, annotation)`."""
    origin = typing.get_origin(annotation)
    if origin is typing.Union:
        args = [a for a in typing.get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return True, args[0]
    return False, annotation


def _is_list_of(annotation: Any) -> Optional[Any]:
    """If `annotation` is `List[X]`, return `X`. Otherwise None."""
    origin = typing.get_origin(annotation)
    if origin in (list, typing.List):
        args = typing.get_args(annotation)
        if args:
            return args[0]
    return None


def _reconstruct(value: Any, dto_class: Optional[Type[Any]]) -> Any:
    """Reconstruct a DTO instance (or list / Optional / scalar) from a JSON-safe value."""
    if value is None:
        return None
    if dto_class is None or not dataclasses.is_dataclass(dto_class):
        return value
    if isinstance(value, list):
        return [_reconstruct(v, dto_class) for v in value]
    if isinstance(value, dict):
        # Pop unknown keys gracefully (forward-compat).
        field_names = {f.name for f in dataclasses.fields(dto_class)}
        clean = {k: v for k, v in value.items() if k in field_names}
        return dto_class(**clean)
    return value


def _sanitize_kwargs_for_json(value: Any) -> Any:
    """Phase 5.5.2 — walk a kwargs tree and convert non-JSON-serializable
    Pydantic models and dataclass instances to JSON-safe dicts.

    Why: `httpx.AsyncClient.post(json=kwargs)` uses `json.dumps` under
    the hood, which doesn't know how to serialize `pydantic.BaseModel`
    or `@dataclass` instances. Without this helper, the single known
    call site (`narrate_analysis(workbook_analysis=wba)` at
    `routers/workbook_analysis.py:1089`) raises `TypeError: Object of
    type WorkbookAnalysis is not JSON serializable`.

    Recursion rules:
    - `BaseModel` instances → `.model_dump(mode='json')` (Pydantic v2;
      preserves datetimes/Enums as ISO/value strings).
    - Dataclass instances → `dataclasses.asdict` (recursive).
    - Plain dicts → recurse into values, preserving key order.
    - Plain lists / tuples → recurse into elements.
    - Everything else (str, int, float, bool, None) → passed through.

    The original kwargs object is NOT mutated; this returns a fresh
    JSON-safe copy.
    """
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    if isinstance(value, dict):
        return {k: _sanitize_kwargs_for_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_kwargs_for_json(v) for v in value]
    return value


def _build_return_map(adapter_cls: Type[Any]) -> Dict[str, Tuple[Optional[Type[Any]], bool]]:
    """Inspect the in-process adapter class to build a method-name →
    (dto_class, is_list) map. `dto_class=None` for primitives.

    Adapter modules opt into ``from __future__ import annotations`` (PEP
    563 string annotations), so we resolve via ``typing.get_type_hints``
    to turn the string forms back into real types. Resolution runs in
    the adapter module's namespace so context DTOs (``Signal``,
    ``ShieldResult``, etc.) bind correctly.
    """
    out: Dict[str, Tuple[Optional[Type[Any]], bool]] = {}
    for name, member in inspect.getmembers(adapter_cls, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        try:
            hints = typing.get_type_hints(member)
        except Exception:  # pragma: no cover — defensive (forward-ref the module can't resolve)
            hints = {}
        ret = hints.get("return")
        if ret is None:
            out[name] = (None, False)
            continue
        is_optional, inner = _is_optional(ret)
        list_of = _is_list_of(inner)
        if list_of is not None:
            out[name] = (list_of if dataclasses.is_dataclass(list_of) else None, True)
        elif dataclasses.is_dataclass(inner):
            out[name] = (inner, False)
        else:
            out[name] = (None, False)
        _ = is_optional  # serialization treats None as None either way
    return out


# ─────────────────────────────────────────────────────────────────────
# Base HTTP adapter
# ─────────────────────────────────────────────────────────────────────
class _HTTPAdapterBase:
    """Shared HTTP transport machinery for context adapters."""

    context_name: str = ""
    return_map: Dict[str, Tuple[Optional[Type[Any]], bool]] = {}

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        timeout_s: Optional[float] = None,
        retries: Optional[int] = None,
    ) -> None:
        # Phase 4.3 — resolve per-context base URL first, then allow
        # caller-explicit override. Falls back to composite default.
        resolved = base_url or _per_context_base_url(self.context_name)
        self._base_url = resolved.rstrip("/")
        self._timeout_s = timeout_s if timeout_s is not None else DEFAULT_TIMEOUT_S
        self._retries = retries if retries is not None else DEFAULT_RETRIES

    async def _call(self, method_name: str, **kwargs: Any) -> Any:
        url = f"{self._base_url}/api/internal/v1/{self.context_name}/method/{method_name}"
        headers = {"X-Internal-Auth": _internal_secret(), "Content-Type": "application/json"}
        # Phase 5.5.2 — sanitize Pydantic / dataclass kwargs into JSON-
        # safe dicts before the httpx.post(json=...) call. Plain dicts
        # / primitives / lists pass through unchanged. See the
        # `_sanitize_kwargs_for_json` docstring for the contract.
        json_kwargs = _sanitize_kwargs_for_json(kwargs)
        last_exc: Optional[Exception] = None
        attempts = max(1, self._retries)
        for attempt in range(1, attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout_s) as client:
                    resp = await client.post(url, json=json_kwargs, headers=headers)
                if resp.status_code == 200:
                    payload = resp.json()
                    raw_result = payload.get("result")
                    dto_cls, _is_list = self.return_map.get(method_name, (None, False))
                    return _reconstruct(raw_result, dto_cls)
                # Non-2xx — log honestly and retry on 5xx, fail-fast on 4xx.
                if 400 <= resp.status_code < 500:
                    detail = resp.text[:500]
                    logger.error(
                        "HTTP transport %s.%s 4xx (status=%d) — fail-fast: %s",
                        self.context_name, method_name, resp.status_code, detail,
                    )
                    raise httpx.HTTPStatusError(
                        f"HTTP {resp.status_code}: {detail}",
                        request=resp.request,
                        response=resp,
                    )
                last_exc = httpx.HTTPStatusError(
                    f"HTTP {resp.status_code}: {resp.text[:500]}",
                    request=resp.request,
                    response=resp,
                )
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_exc = exc
                logger.warning(
                    "HTTP transport %s.%s attempt %d/%d failed: %s",
                    self.context_name, method_name, attempt, attempts, exc,
                    exc_info=True,
                )
            if attempt < attempts:
                # Jittered exponential back-off.
                sleep_s = DEFAULT_BACKOFF_BASE_S * (2 ** (attempt - 1)) + random.uniform(0, 0.05)
                await asyncio.sleep(sleep_s)
        # All retries exhausted — surface the failure.
        logger.error(
            "HTTP transport %s.%s exhausted %d retries — surfacing failure",
            self.context_name, method_name, attempts,
            exc_info=True,
        )
        raise last_exc or RuntimeError(
            f"HTTP transport: {self.context_name}.{method_name} failed after {attempts} retries"
        )


# ─────────────────────────────────────────────────────────────────────
# Context-specific adapter classes — generated dynamically
# ─────────────────────────────────────────────────────────────────────
def _make_http_adapter(
    *,
    contract_protocol: Type[Any],
    inproc_adapter: Type[Any],
    context_name: str,
) -> Type[_HTTPAdapterBase]:
    """Build an HTTP adapter class that exposes the same method
    surface as the in-process adapter, but routes every call through
    `_call(method_name, **kwargs)`.

    Returns a class (not an instance) so callers can `cls()` it the
    same way as the in-process variant.
    """
    return_map = _build_return_map(inproc_adapter)

    cls_dict: Dict[str, Any] = {
        "context_name": context_name,
        "return_map": return_map,
    }

    # For each public async method on the in-process adapter, wire up
    # an HTTP-call thunk on the new class.
    for name, member in inspect.getmembers(inproc_adapter, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue

        # Capture `name` in the default-arg trick to avoid late-binding.
        async def _thunk(self: "_HTTPAdapterBase", *args: Any, _method_name: str = name, **kwargs: Any) -> Any:
            if args:
                # All contract methods are kwarg-only by convention. Reject positional.
                raise TypeError(
                    f"{_method_name}: contract methods are kwarg-only; got positional: {args!r}"
                )
            return await self._call(_method_name, **kwargs)

        _thunk.__name__ = name
        cls_dict[name] = _thunk

    cls_name = f"HTTP{inproc_adapter.__name__.replace('InProcess', '')}"
    return type(cls_name, (_HTTPAdapterBase,), cls_dict)


# Lazy-build at import — the in-process adapter modules import `core.db`
# which requires `MONGO_URL`, so we defer the actual class generation
# until first use via `get_http_<context>` factories below.
_HTTPSyniSense: Optional[Type[_HTTPAdapterBase]] = None
_HTTPSolva: Optional[Type[_HTTPAdapterBase]] = None
_HTTPAkki: Optional[Type[_HTTPAdapterBase]] = None


def get_http_synisense() -> _HTTPAdapterBase:
    global _HTTPSyniSense
    if _HTTPSyniSense is None:
        from ..synisense import SyniSenseContract
        from .synisense import InProcessSyniSenseAdapter
        _HTTPSyniSense = _make_http_adapter(
            contract_protocol=SyniSenseContract,
            inproc_adapter=InProcessSyniSenseAdapter,
            context_name="synisense",
        )
    return _HTTPSyniSense()


def get_http_solva() -> _HTTPAdapterBase:
    global _HTTPSolva
    if _HTTPSolva is None:
        from ..solva import SolvaContract
        from .solva import InProcessSolvaAdapter
        _HTTPSolva = _make_http_adapter(
            contract_protocol=SolvaContract,
            inproc_adapter=InProcessSolvaAdapter,
            context_name="solva",
        )
    return _HTTPSolva()


def get_http_akki() -> _HTTPAdapterBase:
    global _HTTPAkki
    if _HTTPAkki is None:
        from ..akki import AkkiContract
        from .akki import InProcessAkkiAdapter
        _HTTPAkki = _make_http_adapter(
            contract_protocol=AkkiContract,
            inproc_adapter=InProcessAkkiAdapter,
            context_name="akki",
        )
    return _HTTPAkki()


__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT_S",
    "DEFAULT_RETRIES",
    "get_http_synisense",
    "get_http_solva",
    "get_http_akki",
]
