"""Phase 4.1 — Solva FastAPI app.

Standalone FastAPI instance that owns the Solva HTTP surface
(Solva v2 production reasoning, Solva v2 artefact slide payload,
Solva Phase D 5-layer pipeline, Solva briefing-deck state, Solva
telemetry admin, Solva Phase-E polish admin/export/chat-PDF,
workbook analysis). Mounted into the master `server.py` app via
its `ROUTERS` list so the existing single-process composition
continues serving every `/api/*` path unchanged. Phase 4.3 will
run this app as its own uvicorn process; Phase 4.4 adds
dual-mount `/v1/solva/*` versioned paths.

Router ownership (9 modules):
  Solva v2 production:
    solva_v2, solva_v2_artefact
  Solva pipeline + briefing:
    solva_phase_d, solva_briefing, solva_telemetry_admin
  Solva Phase-E polish (3 sub-routers off the same module):
    solva_phase_e_polish.admin_router,
    solva_phase_e_polish.solva_export_router,
    solva_phase_e_polish.chat_pdf_router
  Workbook analysis (Solva narrate / synthesize surface):
    workbook_analysis

Mount ordering within Solva preserves the original `server.py`
sequence:
  1. solva_phase_d         (legacy /api/contexts/{cid}/solva/v2/*)
  2. solva_briefing
  3. solva_telemetry_admin
  4. solva_phase_e_polish (admin + export + chat_pdf)
  5. solva_v2_artefact
  6. solva_v2              (registered AFTER v1 routers per server.py
                            comment "so nothing is shadowed")
  7. workbook_analysis
"""
from __future__ import annotations

from fastapi import FastAPI

from routers import solva_briefing as _solva_briefing
from routers import solva_phase_d as _solva_phase_d
from routers import solva_phase_e_polish as _solva_pe
from routers import solva_telemetry_admin as _solva_telemetry_admin
from routers import solva_v2 as _solva_v2
from routers import solva_v2_artefact as _solva_v2_artefact
from routers import workbook_analysis as _workbook_analysis
from routers._internal_transport import make_internal_router  # Phase 4.2 internal HTTP transport.


# Ordered list of routers this app owns. The master `server.py`
# includes every entry via `app.include_router(r)`. Standalone
# Phase 4.3 mode constructs `FastAPI` below and includes the same
# list. Order preserved to match the original `server.py`
# sequence (v1 routers before v2 production registration).
ROUTERS = [
    _solva_phase_d.router,
    _solva_briefing.router,
    _solva_telemetry_admin.router,
    _solva_pe.admin_router,
    _solva_pe.solva_export_router,
    _solva_pe.chat_pdf_router,
    _solva_v2_artefact.router,
    _solva_v2.router,
    _workbook_analysis.router,
]


# Phase 4.2 internal HTTP transport — every Solva contract method is
# reachable at `POST /api/internal/v1/solva/method/<name>` when
# `BOUNDED_CONTEXT_TRANSPORT=http`. Excluded from public OpenAPI.
def _solva_internal_adapter():
    from contracts._adapters.solva import InProcessSolvaAdapter
    return InProcessSolvaAdapter()


INTERNAL_ROUTER = make_internal_router(
    context_name="solva",
    adapter_factory=_solva_internal_adapter,
)


# Phase 4.3 / 4.4 will give this app its own lifespan + per-process
# scheduler. For Phase 4.1 we ship a slim FastAPI that exists
# primarily to declare the ownership contract.
app = FastAPI(
    title="Solva",
    description=(
        "Solva reasoning (v2 production + Phase D pipeline + "
        "briefing + telemetry + Phase-E polish), Solva artefact "
        "slide payload, and workbook narration / synthesis. "
        "Akki consumes this app via the Phase 1 contracts package "
        "(`get_solva()`); SyniSense does not consume Solva."
    ),
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)
for _r in ROUTERS:
    app.include_router(_r)
app.include_router(INTERNAL_ROUTER)


__all__ = ["app", "ROUTERS", "INTERNAL_ROUTER"]
