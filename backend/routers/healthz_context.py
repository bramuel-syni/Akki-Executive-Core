"""Phase 4.3 — Healthcheck Triad: per-context probes + composite.

Each bounded-context app (Akki, SyniSense, Solva) exposes a tiny
unauthenticated probe at::

    GET /api/healthz/akki
    GET /api/healthz/synisense
    GET /api/healthz/solva

The probe returns 200 with a static snapshot when the process is up:

    {
      "context": "synisense",
      "status": "ok",
      "process": "synisense_app" | "server",
      "ts": "<iso 8601 utc>"
    }

When running mounted-into-server (the default Phase 4.3 process
topology — supervisor is locked read-only per /etc/supervisor/conf.d/
supervisord.conf), all three probes resolve in the same process, but
each declares its `context` independently so external monitors can
ratchet on the per-context surface.

The composite probe at ``GET /api/healthz/composite`` is registered
ONLY on Akki and aggregates the three sub-probes via the same internal
transport layer used by the contract adapters
(`BOUNDED_CONTEXT_TRANSPORT={inproc,http}`). In `http` mode it calls
the sibling processes over HTTP; in `inproc` mode it dispatches the
sub-probe in-memory. Either way the wire shape is identical so flipping
the env var is invisible.

This module is import-cheap so each sub-app can mount its router
without pulling in cross-context dependencies.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter
from fastapi.responses import JSONResponse


def _process_name() -> str:
    """Best-effort identifier for the running process.

    Reads ``AKKI_PROCESS_NAME`` if the operator set one
    (`akki_app`/`synisense_app`/`solva_app` when running standalone);
    falls back to ``"server"`` for the bundled supervisor process.
    """
    return os.environ.get("AKKI_PROCESS_NAME", "server")


def _build_probe(context_name: str) -> Dict[str, Any]:
    return {
        "context": context_name,
        "status": "ok",
        "process": _process_name(),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def make_context_healthz_router(context_name: str) -> APIRouter:
    """Build a router with a single ``GET /api/healthz/<context>`` route.

    Each context owns its own sub-router so the public OpenAPI cleanly
    documents the triad. The path is hard-coded per context (not a path
    parameter) to keep the route table flat and let the invariant
    snapshot ratchet path counts deterministically. Routes are
    `include_in_schema=False` so the public OpenAPI hash stays stable
    while the endpoints remain reachable for K8s probes / monitors.
    """
    router = APIRouter(
        prefix="/api/healthz",
        tags=["healthz"],
        include_in_schema=False,
    )
    path = f"/{context_name}"

    @router.get(path, include_in_schema=False)
    async def _probe() -> JSONResponse:
        return JSONResponse(status_code=200, content=_build_probe(context_name))

    return router


# Composite probe — registered only on the Akki app. Aggregates every
# context probe so a single dashboard call returns the triad status.
def make_composite_healthz_router() -> APIRouter:
    """Composite probe at ``GET /api/healthz/composite``.

    In Phase 4.3 the three sub-apps live in one process so the composite
    short-circuits to in-process probe building. If/when supervisor is
    unlocked and each app runs standalone, set
    ``BOUNDED_CONTEXT_TRANSPORT=http`` plus the per-context base URLs and
    this endpoint will fan-out to each sibling app over HTTP. The wire
    shape is identical either way:

        {
          "status": "ok" | "degraded" | "error",
          "checks": [
            {"context": "akki",      "status": "ok", ...},
            {"context": "synisense", "status": "ok", ...},
            {"context": "solva",     "status": "ok", ...}
          ],
          "ts": "<iso 8601 utc>"
        }

    Top-level status is "ok" iff every check is "ok"; "degraded" when at
    least one but not all succeed; "error" when every check fails.
    """
    router = APIRouter(
        prefix="/api/healthz",
        tags=["healthz"],
        include_in_schema=False,
    )

    @router.get("/composite", include_in_schema=False)
    async def _composite() -> JSONResponse:
        contexts = ("akki", "synisense", "solva")
        checks: List[Dict[str, Any]] = []
        ok_count = 0
        for cname in contexts:
            check = await _probe_context(cname)
            if check.get("status") == "ok":
                ok_count += 1
            checks.append(check)
        if ok_count == len(contexts):
            top_status = "ok"
            http_status = 200
        elif ok_count == 0:
            top_status = "error"
            http_status = 503
        else:
            top_status = "degraded"
            http_status = 207
        return JSONResponse(
            status_code=http_status,
            content={
                "status": top_status,
                "checks": checks,
                "ts": datetime.now(timezone.utc).isoformat(),
            },
        )

    return router


async def _probe_context(context_name: str) -> Dict[str, Any]:
    """Resolve a single context probe respecting the transport toggle."""
    transport = os.environ.get("BOUNDED_CONTEXT_TRANSPORT", "inproc").strip().lower()
    if transport == "http":
        return await _probe_via_http(context_name)
    # inproc — short-circuit to the same payload the per-context route returns
    return _build_probe(context_name)


async def _probe_via_http(context_name: str) -> Dict[str, Any]:
    """HTTP-transport fan-out. Reads the per-context base URL from env.

    Env vars (Phase 4.3 Part C):
      • INTERNAL_TRANSPORT_BASE_URL_AKKI       (default: same-process)
      • INTERNAL_TRANSPORT_BASE_URL_SYNISENSE  (default: same-process)
      • INTERNAL_TRANSPORT_BASE_URL_SOLVA      (default: same-process)
    """
    import httpx

    env_key = f"INTERNAL_TRANSPORT_BASE_URL_{context_name.upper()}"
    base = os.environ.get(env_key, "").strip()
    if not base:
        # Fallback — sibling app not yet broken out into a separate
        # process. Probe in-proc so the composite still answers green.
        return _build_probe(context_name)
    url = f"{base.rstrip('/')}/api/healthz/{context_name}"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
        if resp.status_code == 200:
            payload = resp.json()
            if isinstance(payload, dict):
                payload.setdefault("context", context_name)
                payload.setdefault("status", "ok")
                return payload
            return {"context": context_name, "status": "ok", "process": "remote"}
        return {
            "context": context_name,
            "status": "error",
            "process": "remote",
            "http_status": resp.status_code,
        }
    except Exception as exc:  # explicit fail-open is dishonest — surface the error
        return {
            "context": context_name,
            "status": "error",
            "process": "remote",
            "error": f"{type(exc).__name__}: {exc}",
        }


__all__ = [
    "make_context_healthz_router",
    "make_composite_healthz_router",
]
