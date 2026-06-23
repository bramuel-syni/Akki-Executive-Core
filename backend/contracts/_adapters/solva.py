"""In-process SolvaContract adapter — pass-through to Solva v2.

Wraps existing services in `services.solva_v2.*`. No new logic.
Phase 1 ships this; Phase 2 migrates call sites; Phase 4 swaps for
an HTTP-client adapter.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Literal, Optional

from core import db

from ..solva import SolvaContract
from ..types import (
    PhaseResult,
    RefusalReason,
    SolvaArtefact,
    SolvaInputs,
    SolvaSessionState,
    SynthesisResult,
)

logger = logging.getLogger(__name__)


class InProcessSolvaAdapter(SolvaContract):
    """Pass-through adapter delegating to the in-process Solva v2 services."""

    async def synthesize_workbook(
        self,
        *,
        analysis_id: str,
        account_id: str,
        objective: Optional[str] = None,
    ) -> SynthesisResult:
        """Delegates to services.solva_v2.analyze_narration.narrate_analysis.

        The legacy entry point takes a `WorkbookAnalysis` model; the
        adapter fetches the analysis row + delegates. No behaviour
        change vs. the existing router-driven call path.
        """
        from services.solva_v2.analyze_narration import narrate_analysis
        # Fetch the analysis row exactly as the existing workbook router does.
        row = await db.analyses.find_one(
            {"id": analysis_id, "account_id": account_id}, {"_id": 0},
        )
        if row is None:
            # Mirror the existing 404 behaviour from the router by
            # returning an empty narration. The contract caller can
            # treat empty headline as "not found" without us inventing
            # a new exception class in Phase 1.
            return SynthesisResult(
                analysis_id=analysis_id,
                headline="",
                observations=[],
                citations=[],
                cache_key=None,
                raw={},
            )
        # narrate_analysis builds the WorkbookAnalysis envelope from
        # the row + the objective override. Same call shape as the
        # existing route at routers/workbook_analysis.py:748.
        envelope = await narrate_analysis(
            analysis=row,
            objective=(objective or row.get("objective") or ""),
        )
        return SynthesisResult(
            analysis_id=analysis_id,
            headline=envelope.get("headline") or "",
            observations=list(envelope.get("observations") or []),
            citations=list(envelope.get("citations") or []),
            cache_key=envelope.get("cache_key"),
            raw=envelope,
        )

    async def narrate_analysis(
        self,
        *,
        workbook_analysis: Any,
        account_id: str,
        objective: str = "",
        cached: Optional[Dict[str, Any]] = None,
        workbook_context: Optional[Dict[str, Any]] = None,
        forecast_meta: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Pass-through to services.solva_v2.analyze_narration.narrate_analysis.

        Phase 4.0 widening (Pre-Read §9.1) — gives one production call
        site in `routers/workbook_analysis.py:1089` a typed surface
        without re-shaping it through the higher-level
        `synthesize_workbook` path.
        """
        from services.solva_v2.analyze_narration import narrate_analysis as _narrate
        return await _narrate(
            workbook_analysis=workbook_analysis,
            account_id=account_id,
            objective=objective,
            cached=cached,
            workbook_context=workbook_context,
            forecast_meta=forecast_meta,
        )

    async def run_solva_session(
        self,
        *,
        session_id: str,
        account_id: str,
        phase: Literal["A", "B", "C", "D", "E"],
    ) -> PhaseResult:
        """Pass-through reader for an existing Solva session phase artefact.

        Phase 1 does NOT trigger phase execution — it returns the
        current snapshot of the requested phase from solva_v2_sessions.
        Phase execution remains owned by the existing Solva v2 router
        endpoints; this method is the read-side mirror for downstream
        consumers.
        """
        row = await db.solva_v2_sessions.find_one(
            {"id": session_id, "account_id": account_id}, {"_id": 0},
        )
        if row is None:
            return PhaseResult(session_id=session_id, phase=phase, artefact={}, raw={})
        # The session row holds per-phase artefacts under `phases.<X>` keys.
        phases = row.get("phases") or {}
        artefact = phases.get(phase) or {}
        return PhaseResult(
            session_id=session_id,
            phase=phase,
            artefact=artefact if isinstance(artefact, dict) else {},
            raw=row,
        )

    async def get_session_state(
        self,
        *,
        session_id: str,
        account_id: str,
    ) -> SolvaSessionState:
        """Pass-through to db.solva_v2_sessions."""
        row = await db.solva_v2_sessions.find_one(
            {"id": session_id, "account_id": account_id}, {"_id": 0},
        )
        if row is None:
            return SolvaSessionState(
                session_id=session_id,
                account_id=account_id,
                phase="A",
                raw={},
            )
        return SolvaSessionState(
            session_id=session_id,
            account_id=account_id,
            phase=row.get("current_phase") or row.get("phase") or "A",
            raw=row,
        )

    async def refuse_to_decide_check(
        self,
        *,
        inputs: SolvaInputs,
        account_id: str,  # noqa: ARG002  — kwarg required by contract; not used in v1 logic
    ) -> Optional[RefusalReason]:
        """Pass-through to the Solva v2 refuse-to-decide gate.

        Mirrors the gate logic from services.workbook_analyzer.refuse_to_decide:
        no workbook → refuse; no objective → refuse. Anything else returns None.
        No behaviour change from the existing in-flow check.
        """
        if not inputs.workbook_present:
            return RefusalReason(
                code="no_workbook",
                detail="A workbook is required for Solva v2 synthesis.",
            )
        if not (inputs.objective or "").strip():
            return RefusalReason(
                code="no_objective",
                detail="An objective is required for Solva v2 synthesis.",
            )
        return None

    async def list_solva_artefacts(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
    ) -> List[SolvaArtefact]:
        """Pass-through scan of solva_v2_sessions (and legacy solva_sessions)."""
        query: dict = {"account_id": account_id}
        if context_id is not None:
            query["context_id"] = context_id
        cursor = db.solva_v2_sessions.find(query, {"_id": 0}).sort("created_at", -1).limit(200)
        rows = await cursor.to_list(200)
        return [
            SolvaArtefact(
                artefact_id=r.get("id") or "",
                session_id=r.get("id") or "",
                account_id=r.get("account_id") or account_id,
                raw=r,
            )
            for r in rows
        ]


__all__ = ["InProcessSolvaAdapter"]
