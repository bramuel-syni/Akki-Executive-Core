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
    Chat,
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
        context_ids: Optional[List[str]] = None,
        committee_label_regex: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Cycle]:
        """All cycles for the tenant (optionally scoped to a context or
        list of context-ids; optionally filtered by committee_label
        regex). Replaces nested cursor in tenant-entity harvester +
        Phase 4.2 SyniSense engine multi-context reads."""
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

    # ─────────── Phase 4.2 widening — typed counters ─────────────────────
    # Dissolves the 13 SyniSense engine count_documents() escape hatches
    # + the 3 router-internal count_documents/count_chats hatches.

    async def count_documents(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
        status: Optional[str] = None,
        since_iso: Optional[str] = None,
    ) -> int:
        """Tenant-scoped document count (used by SyniSense engine derivation + signals_ask polling)."""
        ...

    async def count_chats(
        self,
        *,
        account_id: str,
        admin_cross_tenant: bool = False,
        shield_audit_pending: bool = False,
    ) -> int:
        """Tenant-scoped chat count. `admin_cross_tenant=True` is super-admin only (cross-tenant pending Shield back-fill probe — `account_id` is the calling super-admin's id, captured for audit but not used in the filter). `shield_audit_pending=True` matches chats lacking `synisense_audit_ids` AND `backfill_metadata.partial != False`."""
        ...

    async def count_chat_messages(
        self,
        *,
        account_id: str,
        role: Optional[str] = None,
        since_iso: Optional[str] = None,
    ) -> int:
        """Tenant-scoped chat-message count (used by SyniSense engine activity health)."""
        ...

    async def count_cycles(
        self,
        *,
        account_id: str,
        context_ids: Optional[List[str]] = None,
        status: Optional[str] = None,
        status_in: Optional[List[str]] = None,
    ) -> int:
        """Tenant-scoped cycle count (used by SyniSense engine activity health)."""
        ...

    async def count_cycle_questions(
        self,
        *,
        account_id: str,
        context_ids: Optional[List[str]] = None,
        status: Optional[str] = None,
        status_in: Optional[List[str]] = None,
        overdue_iso: Optional[str] = None,
    ) -> int:
        """Tenant-scoped cycle-question count (used by SyniSense engine overdue probe)."""
        ...

    async def count_briefings(
        self,
        *,
        account_id: str,
        status: Optional[str] = None,
        updated_since_iso: Optional[str] = None,
    ) -> int:
        """Tenant-scoped briefing count (used by SyniSense engine activity health)."""
        ...

    async def count_objectives(
        self,
        *,
        account_id: str,
        context_ids: Optional[List[str]] = None,
        rag_status: Optional[str] = None,
    ) -> int:
        """Tenant-scoped objective count (used by SyniSense engine objective-velocity)."""
        ...

    # ─────────── Phase 4.2 widening — typed lookups ─────────────────────

    async def get_document(
        self,
        *,
        account_id: str,
        document_id: str,
        context_id: Optional[str] = None,
        untenanted: bool = False,
    ) -> Optional[Document]:
        """Single-document lookup. `untenanted=True` is a bare-id lookup (Solva v2 evidence-card resolver fetches by document id alone, then verifies via membership downstream). Replaces `db.documents.find_one(...)` in Solva v2 + Solva Phase D."""
        ...

    async def get_context(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> Optional[Context]:
        """Single-context lookup, tenant-scoped. Replaces Solva v2 artefact name-lookups + Trust Center context-name reads."""
        ...

    async def get_context_by_owner(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> Optional[Context]:
        """Owner-scoped context lookup. Replaces SyniSense `signal_seeder` ownership-gated read. `account_id` IS the owner account id."""
        ...

    async def get_chat(
        self,
        *,
        account_id: str,
        chat_id: str,
        untenanted: bool = False,
    ) -> Optional[Chat]:
        """Single-chat lookup. `untenanted=True` skips the account_id filter (Trust Center + synisense_metrics public mirror, both with caller-side membership/auth gating); `untenanted=False` (default) = tenant-scoped (Solva Phase-E polish)."""
        ...

    async def get_membership(
        self,
        *,
        account_id: str,
        context_id: str,
        status: str = "active",
    ) -> Optional[Membership]:
        """Single-membership lookup. Replaces 5 Solva v2 membership checks + Trust Center filter."""
        ...

    async def get_chat_message(
        self,
        *,
        account_id: str,
        chat_id: Optional[str] = None,
        message_id: str,
        role: Optional[str] = None,
    ) -> Optional[ChatMessage]:
        """Single chat-message lookup. `chat_id=None` allowed for bare-id lookups (Solva v2 use-in-Solva resolver fetches by message id alone, then verifies account_id downstream). `account_id` captured for audit (the chat itself is bounded by chat_id when supplied; the caller has membership-gated the chat upstream — Trust Center turn detail)."""
        ...

    async def list_chat_messages_in_chat(
        self,
        *,
        account_id: str,
        chat_id: str,
    ) -> List[ChatMessage]:
        """All messages in a chat. `account_id` captured for audit (chat_id-bound, caller has membership-gated the chat upstream — Trust Center turn list)."""
        ...

    async def find_assistant_reply_after(
        self,
        *,
        account_id: str,
        chat_id: str,
        after_iso: str,
        inclusive: bool = False,
        exclude_message_id: Optional[str] = None,
    ) -> Optional[ChatMessage]:
        """First assistant message after the user message timestamp (Trust Center turn pairing). `inclusive=True` uses `$gte`; default `$gt`. `account_id` captured for audit."""
        ...

    async def find_chats(
        self,
        *,
        account_id: str,
        context_ids: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        status_excludes: Optional[List[str]] = None,
        untenanted: bool = False,
        limit: int = 200,
    ) -> List[Chat]:
        """Versatile chat query helper for Trust Center filters. `untenanted=True` skips the account_id filter (Trust Center already-filtered re-fetch by ids); `account_id` is still required as the caller-of-record."""
        ...

    async def get_cycle(
        self,
        *,
        account_id: str,
        cycle_id: str,
        context_id: Optional[str] = None,
    ) -> Optional[Cycle]:
        """Single-cycle lookup. Replaces Solva Phase D cycle fetch by ref."""
        ...

    async def get_cycle_question(
        self,
        *,
        account_id: str,
        question_id: str,
    ) -> Optional[CycleQuestion]:
        """Single cycle-question lookup. `account_id` captured for audit (Solva v2 Use-in-Solva resolver; caller validates via membership downstream)."""
        ...

    async def list_cycles_by_statuses(
        self,
        *,
        account_id: str,
        statuses: List[str],
        limit: int = 2000,
    ) -> List[Cycle]:
        """Cross-tenant cycle list filtered by status (SyniSense signal_seeder; `account_id` is the calling super-admin's id, captured for audit but not used in the filter)."""
        ...

    async def insert_document_row(
        self,
        *,
        account_id: str,
        document_row: Dict[str, Any],
    ) -> str:
        """Insert a Solva-produced derived document row. Returns the document id. (Solva Phase D writes Akki documents.)"""
        ...


__all__ = ["AkkiContract"]
