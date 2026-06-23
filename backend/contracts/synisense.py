"""SyniSenseContract — the Phase 1 governance surface.

Per Pre-Read §4.A. Five methods. Every method takes `account_id: str`
as a required keyword argument. Pass-through adapter lives at
`backend/contracts/_adapters/synisense.py`.

Phase 1 ships the surface only. Phase 2 migrates call sites. Phase 4
swaps the in-process adapter for an HTTP client.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from .types import (
    AuditEvent,
    ShieldMetrics,
    ShieldResult,
    Signal,
    TrustReceipt,
)


@runtime_checkable
class SyniSenseContract(Protocol):
    """The single canonical surface for governance / Shield concerns."""

    async def shield_invoke(
        self,
        *,
        content: str,
        purpose: str,
        account_id: str,
        consumer_id: str,
        user_id: str,
        model_preference: str = "balanced",
        internal_caller: bool = False,
        system_msg: Optional[str] = None,
    ) -> ShieldResult:
        """Run the full Shield pipeline (de-id → LLM → re-id → audit → receipt). Fail-closed."""
        ...

    async def get_audit_events(
        self,
        *,
        account_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Paginated audit reads for Trust Center / observability surfaces."""
        ...

    async def get_trust_receipt(
        self,
        *,
        audit_id: str,
        account_id: str,
    ) -> Optional[TrustReceipt]:
        """Single trust-receipt lookup with tenant-scope verification."""
        ...

    async def get_shield_metrics(
        self,
        *,
        account_id: str,
    ) -> ShieldMetrics:
        """Aggregated Shield metrics for the per-chat audit panel + admin dashboard."""
        ...

    async def refresh_tenant_entities_cache(
        self,
        *,
        account_id: str,
    ) -> None:
        """Push-invalidate / reload the tenant-entity catalogue cache (vs. TTL-only)."""
        ...

    # ─────────── Phase 4.2 widening — signals are SyniSense-owned ─────

    async def get_signal(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: Optional[str] = None,
        untenanted: bool = False,
    ) -> Optional[Signal]:
        """Single-signal lookup. `untenanted=True` allowed for session-gated reads (Solva v2 Use-in-Solva resolver — caller validates via membership upstream). `context_id` constrains the lookup when supplied."""
        ...

    # ─────────── Phase 4.3 widening — full signals API ────────────────

    async def count_signals(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
        context_ids: Optional[List[str]] = None,
        type_in: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        since_iso: Optional[str] = None,
        until_iso: Optional[str] = None,
        status: Optional[str] = None,
        status_in: Optional[List[str]] = None,
        severity: Optional[str] = None,
        state_in: Optional[List[str]] = None,
        committee_id: Optional[str] = None,
    ) -> int:
        """Tenant-scoped signal count with composable filters. Replaces all `db.signals.count_documents(...)` direct calls in Akki routers."""
        ...

    async def list_signals(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
        context_ids: Optional[List[str]] = None,
        type_in: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        status: Optional[str] = None,
        status_in: Optional[List[str]] = None,
        status_excludes: Optional[List[str]] = None,
        severity: Optional[str] = None,
        state_in: Optional[List[str]] = None,
        committee_id: Optional[str] = None,
        sources_doc_id: Optional[str] = None,
        category_in: Optional[List[str]] = None,
        sandbox_artefact: Optional[bool] = None,
        since_iso: Optional[str] = None,
        created_after_iso: Optional[str] = None,
        before_created_iso: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        limit: int = 50,
    ) -> List[Signal]:
        """Tenant-scoped signal list with composable filters + sort. Replaces all `db.signals.find(...).sort(...).to_list(...)` direct calls. Caller reads fields via `signal.raw[...]` since projections are an adapter optimisation, not a contract concern."""
        ...

    async def list_signals_by_ids(
        self,
        *,
        account_id: str,
        signal_ids: List[str],
        admin_cross_tenant: bool = False,
    ) -> List[Signal]:
        """Bulk fetch signals by id list. `admin_cross_tenant=True` is super-admin only (admin_signal_kpi cross-tenant aggregation)."""
        ...

    async def aggregate_signals_by_type(
        self,
        *,
        account_id: str,
        context_id: str,
        since_iso: Optional[str] = None,
    ) -> Dict[str, int]:
        """Aggregate signal count per `type` for a single context. Replaces `db.signals.aggregate([$match, $group])` in `routers/company_home.py`."""
        ...

    async def find_signal_by_content_hash(
        self,
        *,
        account_id: str,
        context_id: str,
        content_hash: str,
    ) -> Optional[Signal]:
        """Dedup helper — `services/signal_dedup.py` finds by (context_id, content_hash) before merging or inserting a new signal row."""
        ...

    async def find_signal_by_external_ref(
        self,
        *,
        account_id: str,
        context_id: str,
        source: str,
        source_ref: str,
    ) -> Optional[Signal]:
        """Inbox-routing helper — finds an existing row by (context_id, origin.source, origin.message_id) before inserting a new one. (`services/inbox_routing/{upstream_adapter,backfill}.py`)"""
        ...

    # Mutations — semantic-named per business action

    async def insert_signal(
        self,
        *,
        account_id: str,
        signal_row: Dict[str, Any],
    ) -> str:
        """Insert a single signal row. Returns the inserted id. Replaces direct `db.signals.insert_one(...)` calls in `services/inbox_routing/`, `services/signal_dedup.py`. The row is inserted verbatim — caller is responsible for the `id` / `context_id` / `account_id` fields."""
        ...

    async def insert_signals_for_context(
        self,
        *,
        account_id: str,
        context_id: str,
        signal_rows: List[Dict[str, Any]],
    ) -> int:
        """Bulk-insert a list of signals (sandbox seed). Returns inserted count."""
        ...

    async def delete_signals_in_context(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> int:
        """Bulk-delete every signal in a context (sandbox reset). Returns deleted count."""
        ...

    async def add_signal_comment(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        comment: Dict[str, Any],
    ) -> bool:
        """`$push` a comment doc onto `signals.comments[]`. (Pulse comment add.)"""
        ...

    async def delete_signal_comment(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        comment_id: str,
        commenter_account_id: str,
    ) -> bool:
        """`$pull` a comment by (id, account_id) — owner-only delete (Pulse)."""
        ...

    async def mark_signal_resolved(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        resolution_note: Optional[str],
        resolved_by: str,
    ) -> bool:
        """Set state=resolved + resolved_at / resolved_by / resolution_note (Pulse resolve)."""
        ...

    async def mark_signal_unresolved(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
    ) -> bool:
        """Set state=active + clear resolved_* fields (Pulse unresolve)."""
        ...

    async def bookmark_signal(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        bookmarked_by: str,
    ) -> bool:
        """Set state=bookmarked + bookmarked_at / bookmarked_by (Pulse save)."""
        ...

    async def unbookmark_signal(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
    ) -> bool:
        """Set state=active + clear bookmarked_* (Pulse unsave)."""
        ...

    async def dismiss_signal(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
    ) -> bool:
        """Set status=dismissed + dismissed_at (signals_ask dismiss)."""
        ...

    async def unset_signals_committee(
        self,
        *,
        account_id: str,
        context_id: str,
        committee_id: str,
    ) -> int:
        """Bulk `$unset committee_id` on every signal in a (context, committee) pair (committee deletion). Returns affected count."""
        ...

    async def upsert_signal_intelligence(
        self,
        *,
        account_id: str,
        signal_id: str,
        signal_doc: Dict[str, Any],
    ) -> bool:
        """Intelligence-promoter upsert by signal_id with `$setOnInsert`{created_at}. (services/documents/intelligence_service.py)"""
        ...

    async def merge_signal_dedup(
        self,
        *,
        account_id: str,
        signal_id: str,
        content_hash: str,
        last_seen_at: str,
    ) -> bool:
        """Atomic `$inc` of merge_count + `$set` updated_at / last_merged_at on a deduped signal row (services/signal_dedup.py)."""
        ...

    # Semantic-named composite queries — preserve legacy filter shapes verbatim

    async def list_pulse_feed_signals(
        self,
        *,
        account_id: str,
        context_id: str,
        state_filter: str = "active",
        origin: Optional[str] = None,
        limit: int = 500,
    ) -> List[Signal]:
        """Pulse feed — verbatim `state` + `origin` filter (routers/pulse.py).
        `state_filter` is one of `"active"` / `"resolved"` / any other
        string mapped to `{state: <value>}`. `origin` is one of
        `"email_akki"` (→ `origin.source == email_akki`) / `"manual"`
        (→ `origin` absent or null) / None (no origin filter)."""
        ...

    async def get_signal_with_origin(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        origin_required: bool = False,
    ) -> Optional[Signal]:
        """Pulse action handler — fetch by (id, context_id). When
        `origin_required=True`, the row is only returned if `origin`
        exists and is non-null (used by the `email_akki` action filter)."""
        ...

    async def search_signals_by_text(
        self,
        *,
        account_id: str,
        context_id: str,
        query: str,
        limit: int = 50,
    ) -> List[Signal]:
        """Universal Search — case-insensitive regex on `headline` OR
        `summary`. Excludes archived signals. (services/universal_search.py)"""
        ...

    # Semantic-named count helpers — preserve legacy filter shapes verbatim

    async def count_goals_at_risk(
        self,
        *,
        account_id: str,
        context_id: str,
        confidence_gt: float = 0.6,
    ) -> int:
        """Count `goal_risk`-category signals with confidence above the threshold and state ≠ archived (Portfolio Goals-at-Risk tile)."""
        ...

    async def count_unread_signals(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> int:
        """Count Pulse "unread" signals — `state == active` OR (no `state` AND `status ∈ {active, None}`). (Portfolio unread tile.)"""
        ...


__all__ = ["SyniSenseContract"]
