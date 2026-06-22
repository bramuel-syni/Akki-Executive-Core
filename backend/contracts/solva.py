"""SolvaContract — the Phase 1 reasoning surface.

Per Pre-Read §4.B. Five methods. Every method takes `account_id: str`
as a required keyword argument. Pass-through adapter lives at
`backend/contracts/_adapters/solva.py`.

Phase 1 ships the surface only. Phase 2 migrates call sites. Phase 4
swaps the in-process adapter for an HTTP client.
"""
from __future__ import annotations

from typing import List, Literal, Optional, Protocol, runtime_checkable

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
