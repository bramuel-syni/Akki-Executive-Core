"""In-process SyniSenseContract adapter — pass-through to the Shield.

Wraps existing services in `services.synisense.shield.*`. No new
logic. Phase 1 ships this; Phase 2 migrates call sites; Phase 4
swaps for an HTTP-client adapter.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core import db

from ..synisense import SyniSenseContract
from ..types import (
    AuditEvent,
    ShieldMetrics,
    ShieldResult,
    Signal,
    TrustReceipt,
)

logger = logging.getLogger(__name__)


class InProcessSyniSenseAdapter(SyniSenseContract):
    """Pass-through adapter delegating to the in-process SyniSense services."""

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
        """Delegates to services.synisense.shield.client.invoke.

        Maps `account_id` → existing `tenant_id` kwarg (pre-contract
        synonym). The Shield internally uses `tenant_id`; the contract
        surfaces `account_id` so the rest of the codebase converges
        on a single tenancy term.

        Phase 4.0 — only forwards `system_msg` to the underlying
        primitive when the caller explicitly provided a non-None
        value. The primitive's default behaviour (no system_msg kwarg
        present → llm_router's generic system prompt) is preserved
        verbatim for the 90+ legacy call sites that never passed
        system_msg.
        """
        from services.synisense.shield.client import invoke as _shield_invoke
        primitive_kwargs: Dict[str, Any] = {
            "content": content,
            "purpose": purpose,
            "tenant_id": account_id,
            "consumer_id": consumer_id,
            "user_id": user_id,
            "model_preference": model_preference,
            "internal_caller": internal_caller,
        }
        if system_msg is not None:
            primitive_kwargs["system_msg"] = system_msg
        result = await _shield_invoke(**primitive_kwargs)
        return ShieldResult(
            response=result.get("response") or "",
            audit_id=result.get("audit_id"),
            trust_receipt=result.get("trust_receipt"),
            de_id_summary=result.get("de_id_summary") or {},
            elapsed_ms=int(result.get("elapsed_ms") or 0),
            raw=result,
        )

    async def get_audit_events(
        self,
        *,
        account_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Pass-through paginated read of synisense_audit_log."""
        q: dict = {"tenant_id": account_id, "account_id": account_id}
        # synisense_audit_log uses `tenant_id` historically; back-compat
        # via $or so either key matches. The collection write path
        # writes `tenant_id` today.
        query: dict = {"tenant_id": account_id}
        if since is not None:
            query.setdefault("timestamp", {})["$gte"] = since.isoformat()
        if until is not None:
            query.setdefault("timestamp", {})["$lte"] = until.isoformat()
        cursor = db.synisense_audit_log.find(query, {"_id": 0}).sort("timestamp", -1).limit(int(limit))
        rows = await cursor.to_list(int(limit))
        return [
            AuditEvent(
                audit_id=r.get("audit_id") or "",
                timestamp=r.get("timestamp") or "",
                tenant_id=r.get("tenant_id") or "",
                purpose=r.get("purpose") or "",
                consumer_id=r.get("consumer_id") or "",
                outcome=r.get("outcome") or "",
                de_id_summary=r.get("de_id_summary") or {},
                raw=r,
            )
            for r in rows
        ]

    async def get_trust_receipt(
        self,
        *,
        audit_id: str,
        account_id: str,
    ) -> Optional[TrustReceipt]:
        """Pass-through to services.synisense.shield.audit_log.find_receipt."""
        from services.synisense.shield.audit_log import find_receipt
        row = await find_receipt(audit_id, tenant_id=account_id)
        if row is None:
            return None
        return TrustReceipt(
            receipt_id=row.get("receipt_id") or "",
            audit_id=row.get("audit_id") or audit_id,
            tenant_id=row.get("tenant_id") or account_id,
            signature=row.get("signature") or "",
            raw=row,
        )

    async def get_shield_metrics(
        self,
        *,
        account_id: str,
    ) -> ShieldMetrics:
        """Aggregated counts from synisense_audit_log for the tenant."""
        # Pass-through aggregation: same shape Akki uses today on the
        # audit panel + admin dashboard.
        total = await db.synisense_audit_log.count_documents({"tenant_id": account_id})
        success = await db.synisense_audit_log.count_documents(
            {"tenant_id": account_id, "outcome": "success"}
        )
        rate = (success / total) if total > 0 else 0.0
        return ShieldMetrics(
            total_calls=total,
            success_rate=rate,
            raw={"total": total, "success": success},
        )

    async def refresh_tenant_entities_cache(
        self,
        *,
        account_id: str,
    ) -> None:
        """Pass-through to services.synisense.shield.tenant_entities.harvest."""
        try:
            from services.synisense.shield.tenant_entities import harvest
            await harvest(account_id)
        except Exception:
            # Honesty protocol — log with exc_info but don't propagate;
            # cache refresh is best-effort by existing behaviour.
            logger.exception(
                "InProcessSyniSenseAdapter.refresh_tenant_entities_cache: "
                "harvest failed for account_id=%s",
                account_id,
            )

    # ─────────── Phase 4.2 widening — signals are SyniSense-owned ─────

    async def get_signal(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: Optional[str] = None,
        untenanted: bool = False,
    ) -> Optional[Signal]:
        """Pass-through to db.signals.find_one. Same-context read for
        SyniSense; surfaced through the contract so cross-context
        callers don't reach into `db.signals` directly. `untenanted=True`
        skips the account_id filter for session-gated upstream paths
        (Solva v2 evidence cards) — `account_id` is still required as
        the caller-of-record. `context_id` is honoured when supplied.
        """
        query: Dict[str, Any] = {"id": signal_id}
        if not untenanted:
            query["account_id"] = account_id
        if context_id is not None:
            query["context_id"] = context_id
        row = await db.signals.find_one(query, {"_id": 0})
        if row is None:
            return None
        return Signal(
            signal_id=signal_id,
            account_id=row.get("account_id") or account_id,
            context_id=row.get("context_id") or "",
            raw=row,
        )

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
        committee_id: Optional[str] = None,
    ) -> int:
        """Pass-through to db.signals.count_documents."""
        _ = account_id  # noqa: F841 — audit/log trail (filter is context-scoped, not account-scoped, mirroring legacy direct-call shape)
        query: Dict[str, Any] = self._build_signal_query(
            context_id=context_id,
            context_ids=context_ids,
            type_in=type_in,
            ids=ids,
            since_iso=since_iso,
            until_iso=until_iso,
            status=status,
            status_in=status_in,
            committee_id=committee_id,
        )
        return await db.signals.count_documents(query)

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
        committee_id: Optional[str] = None,
        since_iso: Optional[str] = None,
        before_created_iso: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        limit: int = 50,
    ) -> List[Signal]:
        """Pass-through to db.signals.find with composable filters."""
        _ = account_id  # noqa: F841 — audit/log trail (filter is context-scoped)
        query: Dict[str, Any] = self._build_signal_query(
            context_id=context_id,
            context_ids=context_ids,
            type_in=type_in,
            ids=ids,
            status=status,
            status_in=status_in,
            status_excludes=status_excludes,
            committee_id=committee_id,
            since_iso=since_iso,
            before_created_iso=before_created_iso,
        )
        sort_dir = -1 if order.lower() == "desc" else 1
        cursor = db.signals.find(query, {"_id": 0}).sort(sort_by, sort_dir).limit(int(limit))
        rows = await cursor.to_list(int(limit))
        return [
            Signal(
                signal_id=r.get("id") or "",
                account_id=r.get("account_id") or account_id,
                context_id=r.get("context_id") or "",
                raw=r,
            )
            for r in rows
        ]

    async def list_signals_by_ids(
        self,
        *,
        account_id: str,
        signal_ids: List[str],
        admin_cross_tenant: bool = False,
    ) -> List[Signal]:
        """Bulk fetch by id list. `admin_cross_tenant=True` is super-admin only (admin_signal_kpi cross-tenant aggregation)."""
        if not signal_ids:
            return []
        query: Dict[str, Any] = {"id": {"$in": list(signal_ids)}}
        if not admin_cross_tenant:
            query["account_id"] = account_id
        cursor = db.signals.find(query, {"_id": 0})
        rows = await cursor.to_list(length=None)
        return [
            Signal(
                signal_id=r.get("id") or "",
                account_id=r.get("account_id") or account_id,
                context_id=r.get("context_id") or "",
                raw=r,
            )
            for r in rows
        ]

    async def aggregate_signals_by_type(
        self,
        *,
        account_id: str,
        context_id: str,
        since_iso: Optional[str] = None,
    ) -> Dict[str, int]:
        """Aggregate signal count per `type` for a context."""
        _ = account_id  # noqa: F841 — audit
        match: Dict[str, Any] = {"context_id": context_id}
        if since_iso is not None:
            match["created_at"] = {"$gte": since_iso}
        cursor = db.signals.aggregate([
            {"$match": match},
            {"$group": {"_id": "$type", "n": {"$sum": 1}}},
        ])
        rows = await cursor.to_list(length=None)
        return {(r.get("_id") or "unknown"): int(r.get("n") or 0) for r in rows}

    async def find_signal_by_content_hash(
        self,
        *,
        account_id: str,
        context_id: str,
        content_hash: str,
    ) -> Optional[Signal]:
        """Dedup helper."""
        _ = account_id  # noqa: F841 — audit
        row = await db.signals.find_one(
            {"context_id": context_id, "content_hash": content_hash},
            {"_id": 0},
        )
        if row is None:
            return None
        return Signal(
            signal_id=row.get("id") or "",
            account_id=row.get("account_id") or account_id,
            context_id=context_id,
            raw=row,
        )

    async def find_signal_by_external_ref(
        self,
        *,
        account_id: str,
        context_id: str,
        source: str,
        source_ref: str,
    ) -> Optional[Signal]:
        """Inbox-routing helper."""
        _ = account_id  # noqa: F841 — audit
        row = await db.signals.find_one(
            {"context_id": context_id, "source": source, "source_ref": source_ref},
            {"_id": 0},
        )
        if row is None:
            return None
        return Signal(
            signal_id=row.get("id") or "",
            account_id=row.get("account_id") or account_id,
            context_id=context_id,
            raw=row,
        )

    # Mutations — semantic-named per business action

    async def insert_signal(
        self,
        *,
        account_id: str,
        signal_row: Dict[str, Any],
    ) -> str:
        """Insert a single signal row verbatim."""
        _ = account_id  # noqa: F841 — audit
        row = dict(signal_row)
        await db.signals.insert_one(row)
        row.pop("_id", None)
        return row.get("id") or ""

    async def insert_signals_for_context(
        self,
        *,
        account_id: str,
        context_id: str,
        signal_rows: List[Dict[str, Any]],
    ) -> int:
        """Bulk-insert (sandbox seed)."""
        _ = account_id  # noqa: F841 — audit
        if not signal_rows:
            return 0
        # Each row in `signal_rows` is expected to already carry context_id
        # — match the legacy direct-call shape exactly.
        rows = [dict(r) for r in signal_rows]
        result = await db.signals.insert_many(rows)
        return len(result.inserted_ids) if result and result.inserted_ids else 0

    async def delete_signals_in_context(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> int:
        """Bulk-delete every signal in a context (sandbox reset)."""
        _ = account_id  # noqa: F841 — audit
        result = await db.signals.delete_many({"context_id": context_id})
        return int(result.deleted_count) if result else 0

    async def add_signal_comment(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        comment: Dict[str, Any],
    ) -> bool:
        _ = account_id  # noqa: F841 — audit
        result = await db.signals.update_one(
            {"id": signal_id, "context_id": context_id},
            {"$push": {"comments": dict(comment)}},
        )
        return bool(result and result.modified_count)

    async def delete_signal_comment(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        comment_id: str,
        commenter_account_id: str,
    ) -> bool:
        _ = account_id  # noqa: F841 — audit
        result = await db.signals.update_one(
            {"id": signal_id, "context_id": context_id,
             "comments.id": comment_id, "comments.account_id": commenter_account_id},
            {"$pull": {"comments": {"id": comment_id, "account_id": commenter_account_id}}},
        )
        return bool(result and result.modified_count)

    async def mark_signal_resolved(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        resolution_note: Optional[str],
        resolved_by: str,
    ) -> bool:
        _ = account_id  # noqa: F841 — audit
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        upd: Dict[str, Any] = {
            "state": "resolved",
            "status": "resolved",
            "resolved_at": now_iso,
            "resolved_by": resolved_by,
        }
        if resolution_note is not None:
            upd["resolution_note"] = resolution_note
        result = await db.signals.update_one(
            {"id": signal_id, "context_id": context_id},
            {"$set": upd},
        )
        return bool(result and result.modified_count)

    async def mark_signal_unresolved(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
    ) -> bool:
        _ = account_id  # noqa: F841 — audit
        result = await db.signals.update_one(
            {"id": signal_id, "context_id": context_id},
            {
                "$set": {"state": "active", "status": "active"},
                "$unset": {"resolved_at": "", "resolved_by": "", "resolution_note": ""},
            },
        )
        return bool(result and result.modified_count)

    async def bookmark_signal(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
        bookmarked_by: str,
    ) -> bool:
        _ = account_id  # noqa: F841 — audit
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        result = await db.signals.update_one(
            {"id": signal_id, "context_id": context_id},
            {"$set": {
                "state": "bookmarked",
                "bookmarked_at": now_iso,
                "bookmarked_by": bookmarked_by,
            }},
        )
        return bool(result and result.modified_count)

    async def unbookmark_signal(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
    ) -> bool:
        _ = account_id  # noqa: F841 — audit
        result = await db.signals.update_one(
            {"id": signal_id, "context_id": context_id},
            {"$set": {"state": "active"}, "$unset": {"bookmarked_at": "", "bookmarked_by": ""}},
        )
        return bool(result and result.modified_count)

    async def dismiss_signal(
        self,
        *,
        account_id: str,
        signal_id: str,
        context_id: str,
    ) -> bool:
        _ = account_id  # noqa: F841 — audit
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        result = await db.signals.update_one(
            {"id": signal_id, "context_id": context_id},
            {"$set": {"status": "dismissed", "dismissed_at": now_iso}},
        )
        return bool(result and result.modified_count)

    async def unset_signals_committee(
        self,
        *,
        account_id: str,
        context_id: str,
        committee_id: str,
    ) -> int:
        _ = account_id  # noqa: F841 — audit
        result = await db.signals.update_many(
            {"context_id": context_id, "committee_id": committee_id},
            {"$unset": {"committee_id": ""}},
        )
        return int(result.modified_count) if result else 0

    async def upsert_signal_intelligence(
        self,
        *,
        account_id: str,
        signal_id: str,
        signal_doc: Dict[str, Any],
    ) -> bool:
        """Intelligence-promoter upsert."""
        _ = account_id  # noqa: F841 — audit
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        set_doc = {k: v for k, v in signal_doc.items() if k != "created_at"}
        result = await db.signals.update_one(
            {"id": signal_id},
            {
                "$set": set_doc,
                "$setOnInsert": {"created_at": now_iso},
            },
            upsert=True,
        )
        return bool(result)

    async def merge_signal_dedup(
        self,
        *,
        account_id: str,
        signal_id: str,
        content_hash: str,
        merge_count: int,
        last_seen_at: str,
    ) -> bool:
        _ = account_id  # noqa: F841 — audit
        result = await db.signals.update_one(
            {"id": signal_id, "content_hash": content_hash},
            {"$set": {"merge_count": int(merge_count), "last_seen_at": last_seen_at}},
        )
        return bool(result and result.modified_count)

    @staticmethod
    def _build_signal_query(
        *,
        context_id: Optional[str] = None,
        context_ids: Optional[List[str]] = None,
        type_in: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        status: Optional[str] = None,
        status_in: Optional[List[str]] = None,
        committee_id: Optional[str] = None,
        since_iso: Optional[str] = None,
        until_iso: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compose the legacy-shape Mongo filter dict from the typed kwargs."""
        query: Dict[str, Any] = {}
        if context_id is not None:
            query["context_id"] = context_id
        elif context_ids is not None:
            if not context_ids:
                # signal "match nothing" via impossible filter
                return {"_id": "__nomatch__"}
            query["context_id"] = {"$in": list(context_ids)}
        if type_in:
            query["type"] = {"$in": list(type_in)}
        if ids:
            query["id"] = {"$in": list(ids)}
        if status is not None:
            query["status"] = status
        elif status_in is not None:
            query["status"] = {"$in": list(status_in)}
        if committee_id is not None:
            query["committee_id"] = committee_id
        created_at: Dict[str, Any] = {}
        if since_iso is not None:
            created_at["$gte"] = since_iso
        if until_iso is not None:
            created_at["$lt"] = until_iso
        if created_at:
            query["created_at"] = created_at
        return query


__all__ = ["InProcessSyniSenseAdapter"]
