"""AkkiContract — the Phase 1 orchestration / data-ownership surface.

Per Pre-Read §4.C. Eleven methods. Every method takes `account_id: str`
as a required keyword argument. Pass-through adapter lives at
`backend/contracts/_adapters/akki.py`.

This is the CRITICAL contract: it inverts the dependency that
SyniSense + Solva currently have on Akki's data. Before Phase 1,
those packages reach directly into Mongo collections owned by Akki
(`accounts`, `contexts`, `cycles`, `chats`, `chat_messages`,
`briefings`, `documents`, `signals`, `objectives`, `cycle_questions`,
`memberships`). After Phase 1, they call through `AkkiContract`
methods instead.

Phase 1 ships the surface only. Phase 2 migrates call sites. Phase 4
swaps the in-process adapter for an HTTP client.

Per Resolution 2 of the Phase 1 build dispatch: SyniSense and Solva
WRITE to the universal `audit_log` collection via
`AkkiContract.audit_event(...)`. `synisense_audit_log` remains
SyniSense-owned (separate collection, not conflated).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from .types import (
    Briefing,
    ChatMessage,
    Context,
    Cycle,
    CycleQuestion,
    Document,
    Membership,
    Objective,
    Signal,
    TenantEntity,
    TenantProfile,
)


@runtime_checkable
class AkkiContract(Protocol):
    """Akki-owned data + write-back hooks for cross-context callers."""

    # ─────────── Identity / tenancy ───────────

    async def get_tenant_profile(
        self,
        *,
        account_id: str,
    ) -> TenantProfile:
        """Tenant identity row (`accounts` lookup). Replaces SyniSense harvester direct read."""
        ...

    async def list_contexts(
        self,
        *,
        account_id: str,
    ) -> List[Context]:
        """All contexts owned by the tenant. Replaces SyniSense + Solva direct reads."""
        ...

    async def list_cycles(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
    ) -> List[Cycle]:
        """All cycles for the tenant (optionally scoped to a context). Replaces nested cursor in tenant-entity harvester."""
        ...

    async def list_tenant_entities(
        self,
        *,
        account_id: str,
    ) -> List[TenantEntity]:
        """BATCHED: precomputed tenant proper-noun catalogue for the Shield's de-id dictionary."""
        ...

    async def list_memberships(
        self,
        *,
        account_id: str,
        status: Optional[str] = "active",
    ) -> List[Membership]:
        """Active memberships for the tenant (replaces `db.memberships.find` in SyniSense engine signal derivation). Phase 4.0 widening (Pre-Read §9.1)."""
        ...

    # ─────────── Chat context ───────────

    async def get_chat_history(
        self,
        *,
        account_id: str,
        chat_id: str,
        limit: int = 50,
    ) -> List[ChatMessage]:
        """Recent chat messages for the given session. Replaces direct chat_messages reads by Solva grounding."""
        ...

    # ─────────── Documents / signals / objectives ───────────

    async def list_documents(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> List[Document]:
        """Documents in the tenant's library (optionally filtered). Replaces direct documents.find by Solva."""
        ...

    async def list_signals(
        self,
        *,
        account_id: str,
        context_id: str,
        since: Optional[datetime] = None,
    ) -> List[Signal]:
        """Signals in a context (optionally newer than `since`). Replaces direct signals.find by Solva narration."""
        ...

    async def list_objectives(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> List[Objective]:
        """Objectives in a context. Replaces direct objectives.find by Solva + SyniSense engine."""
        ...

    async def list_cycle_questions(
        self,
        *,
        account_id: str,
        cycle_id: str,
    ) -> List[CycleQuestion]:
        """Cycle Q4Y questions. Replaces direct cycle_questions.find by Solva + SyniSense engine."""
        ...

    async def list_briefings(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> List[Briefing]:
        """Briefings in a context. Replaces direct briefings reads by Solva narration."""
        ...

    # ─────────── Audit-log write-back ───────────

    async def audit_event(
        self,
        *,
        account_id: str,
        action: str,
        payload: Dict[str, Any],
    ) -> None:
        """Append to the universal Akki `audit_log`. SyniSense + Solva write here via this method (not direct insert_one). `synisense_audit_log` remains SyniSense-owned."""
        ...


__all__ = ["AkkiContract"]
