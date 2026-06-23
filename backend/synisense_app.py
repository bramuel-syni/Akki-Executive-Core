"""Phase 4.1 — SyniSense FastAPI app.

Standalone FastAPI instance that owns the SyniSense HTTP surface
(Shield, trust center, signal engine, observability, healthz). Mounted
into the master `server.py` app via its `ROUTERS` list so the existing
single-process composition continues serving every `/api/*` path
unchanged. Phase 4.3 will run this app as its own uvicorn process on
port 8002; Phase 4.4 adds dual-mount `/v1/synisense/*` versioned paths.

Router ownership (12 modules):
  Shield / engine / observability / healthz cluster:
    synisense, synisense_engine, synisense_metrics,
    synisense_observability, synisense_shield, healthz_shield
  Trust + signal customer-facing:
    trust_center, signal_actions, signals_ask, governance
  Admin surfaces:
    admin_shield_backfill, admin_signal_kpi
"""
from __future__ import annotations

from fastapi import FastAPI

from routers import admin_shield_backfill as _admin_shield_backfill
from routers import admin_signal_kpi as _admin_signal_kpi
from routers import governance as _governance
from routers import healthz_shield as _healthz_shield
from routers import signal_actions as _signal_actions
from routers import signals_ask as _signals_ask
from routers import synisense as _synisense
from routers import synisense_engine as _synisense_engine
from routers import synisense_metrics as _synisense_metrics
from routers import synisense_observability as _synisense_observability
from routers import synisense_shield as _synisense_shield
from routers import trust_center as _trust_center


# Ordered list of routers this app owns. The master `server.py` includes
# every entry via `app.include_router(r)`. Standalone Phase 4.3 mode
# constructs `FastAPI` below and includes the same list.
ROUTERS = [
    _synisense.router,
    _synisense_engine.router,
    _synisense_metrics.router,
    _synisense_observability.router,
    _synisense_shield.router,
    _healthz_shield.router,
    _trust_center.router,
    _signal_actions.router,
    _signals_ask.router,
    _admin_shield_backfill.router,
    _admin_signal_kpi.router,
    _governance.router,
]


# Phase 4.3 / 4.4 will give this app its own lifespan + per-process
# scheduler + spaCy load. For Phase 4.1 we ship a slim FastAPI that
# exists primarily to declare the ownership contract.
app = FastAPI(
    title="SyniSense",
    description=(
        "Shield, trust, signal engine and observability — context "
        "boundary surface. Akki + Solva consume this app via the "
        "Phase 1 contracts package (`get_synisense()`)."
    ),
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)
for _r in ROUTERS:
    app.include_router(_r)


__all__ = ["app", "ROUTERS"]
