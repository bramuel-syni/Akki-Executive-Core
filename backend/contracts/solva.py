"""SolvaContract — the Phase 1 reasoning surface.

Per Pre-Read §4.B. Five methods originally, **six after Phase 4.0**
(2026-06-23 — Pre-Read §9 widening: `narrate_analysis` added because
the one in-tree call site at `routers/workbook_analysis.py:1089` uses
a signature distinct from `synthesize_workbook`). Every method takes
`account_id: str` as a required keyword argument. Pass-through
adapter lives at `backend/contracts/_adapters/solva.py`.

Phase 1 ships the surface only. Phase 4.0 migrates call sites. Phase
4.2 swaps the in-process adapter for an HTTP client.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Protocol, runtime_checkable

from .types import (
    PhaseResult,
    RefusalReason,
    SolvaArtefact,
    SolvaInputs,
    SolvaSessionState,
    SynthesisResult,
)


@runtime_checkable
class SolvaContract(Protocol):
    """The single canonical surface for Solva v2 reasoning."""

    async def synthesize_workbook(
        self,
        *,
        analysis_id: str,
        account_id: str,
        objective: Optional[str] = None,
    ) -> SynthesisResult:
        """Solva v2 multi-workbook narration — idempotent on cache_key. Wraps Phase 4 multi-blob synthesize."""
        ...

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
        """Lower-level narration entry point: pass an already-built `WorkbookAnalysis` model directly. Mirror of `services.solva_v2.analyze_narration.narrate_analysis`. Phase 4.0 widening (Pre-Read §9.1)."""
        ...

    async def run_solva_session(
        self,
        *,
        session_id: str,
        account_id: str,
        phase: Literal["A", "B", "C", "D", "E"],
    ) -> PhaseResult:
        """Directed reasoning pipeline phase runner. Replaces the direct router-to-engine call."""
        ...

    async def get_session_state(
        self,
        *,
        session_id: str,
        account_id: str,
    ) -> SolvaSessionState:
        """Snapshot a Solva session for UI rendering."""
        ...

    async def refuse_to_decide_check(
        self,
        *,
        inputs: SolvaInputs,
        account_id: str,
    ) -> Optional[RefusalReason]:
        """Explicit insufficient-input gate. Returns None when safe to proceed."""
        ...

    async def list_solva_artefacts(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
    ) -> List[SolvaArtefact]:
        """Paginated artefact list (replaces direct solva_sessions reads by Akki routers)."""
        ...


__all__ = ["SolvaContract"]
