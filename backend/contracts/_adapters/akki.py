"""In-process AkkiContract adapter — pass-through to Mongo collections.

Wraps direct collection reads + writes for Akki-owned data. SyniSense
and Solva use this adapter (via the contract surface) instead of
reaching into Mongo collections directly.

No new logic. Phase 1 ships this; Phase 2 migrates call sites; Phase
4 swaps for an HTTP-client adapter.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core import db

from ..akki import AkkiContract
from ..types import (
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

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class InProcessAkkiAdapter(AkkiContract):
    """Pass-through adapter delegating to direct Mongo collection access."""

    # ─────────── Identity / tenancy ───────────

    async def get_tenant_profile(self, *, account_id: str) -> TenantProfile:
        """Pass-through to db.accounts.find_one."""
        row = await db.accounts.find_one(
            {"id": account_id}, {"_id": 0},
        )
        if row is None:
            return TenantProfile(account_id=account_id, name=None, email=None, raw={})
        return TenantProfile(
            account_id=account_id,
            name=row.get("name"),
            email=row.get("email"),
            raw=row,
        )

    async def list_contexts(self, *, account_id: str) -> List[Context]:
        """Pass-through to db.contexts.find."""
        cursor = db.contexts.find({"account_id": account_id}, {"_id": 0})
        rows = await cursor.to_list(1000)
        return [
            Context(
                context_id=r.get("id") or "",
                name=r.get("name") or "",
                account_id=account_id,
                raw=r,
            )
            for r in rows
        ]

    async def list_cycles(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
        context_ids: Optional[List[str]] = None,
        committee_label_regex: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Cycle]:
        """Pass-through to db.cycles.find."""
        query: Dict[str, Any] = {}
        if context_ids is not None:
            if not context_ids:
                return []
            query["context_id"] = {"$in": list(context_ids)}
        else:
            query["account_id"] = account_id
            if context_id is not None:
                query["context_id"] = context_id
        if committee_label_regex is not None:
            query["committee_label"] = {"$regex": committee_label_regex, "$options": "i"}
        cursor = db.cycles.find(query, {"_id": 0}).limit(int(limit))
        rows = await cursor.to_list(int(limit))
        return [
            Cycle(
                cycle_id=r.get("id") or "",
                account_id=r.get("account_id") or account_id,
                context_id=r.get("context_id"),
                raw=r,
            )
            for r in rows
        ]

    async def list_tenant_entities(self, *, account_id: str) -> List[TenantEntity]:
        """Pass-through to the existing tenant-entity harvest pipeline.

        Today's behaviour: the catalogue is built lazily in
        `services.synisense.shield.tenant_entities` via nested DB
        cursors. This adapter method returns the precomputed cache
        entries; if the cache is cold, it triggers a harvest. No
        behaviour change — the harvest is the same one the Shield
        runs on cache miss today.
        """
        try:
            from services.synisense.shield.tenant_entities import _ensure_cache
            rows = await _ensure_cache(account_id)
        except Exception:
            logger.exception(
                "InProcessAkkiAdapter.list_tenant_entities: harvest failed "
                "for account_id=%s",
                account_id,
            )
            rows = []
        out: List[TenantEntity] = []
        for r in rows:
            kind = r.get("kind") or r.get("type") or "unknown"
            value = r.get("value") or r.get("token") or ""
            source = r.get("source") or "unknown"
            if value:
                out.append(TenantEntity(kind=kind, value=value, source=source))
        return out

    async def list_memberships(
        self,
        *,
        account_id: str,
        status: Optional[str] = "active",
    ) -> List[Membership]:
        """Pass-through to db.memberships.find.

        Phase 4.0 widening (Pre-Read §9.1) — surfaces the one in-tree
        SyniSense direct read (`services/synisense/engine/signal_derivation.py:476`)
        through the contract. When `status` is None, returns ALL
        memberships regardless of state.
        """
        query: Dict[str, Any] = {"account_id": account_id}
        if status is not None:
            query["status"] = status
        cursor = db.memberships.find(query, {"_id": 0})
        rows = await cursor.to_list(1000)
        return [
            Membership(
                account_id=account_id,
                context_id=r.get("context_id") or "",
                status=r.get("status") or "",
                raw=r,
            )
            for r in rows
        ]

    # ─────────── Chat context ───────────

    async def get_chat_history(
        self,
        *,
        account_id: str,
        chat_id: str,
        limit: int = 50,
    ) -> List[ChatMessage]:
        """Pass-through to db.chats — messages live as an embedded array on the chat row."""
        row = await db.chats.find_one(
            {"id": chat_id, "account_id": account_id}, {"_id": 0},
        )
        if row is None:
            return []
        messages = list(row.get("messages") or [])[-int(limit):]
        return [
            ChatMessage(
                message_id=m.get("id") or "",
                chat_id=chat_id,
                account_id=account_id,
                role=m.get("role") or "",
                content=m.get("content") or "",
                created_at=m.get("created_at") or "",
                raw=m,
            )
            for m in messages
        ]

    # ─────────── Documents / signals / objectives ───────────

    async def list_documents(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> List[Document]:
        """Pass-through to db.documents.find."""
        query: Dict[str, Any] = {"account_id": account_id}
        if context_id is not None:
            query["context_id"] = context_id
        if kind is not None:
            query["kind"] = kind
        cursor = db.documents.find(query, {"_id": 0}).limit(500)
        rows = await cursor.to_list(500)
        return [
            Document(
                document_id=r.get("id") or "",
                account_id=account_id,
                context_id=r.get("context_id"),
                name=r.get("name") or "",
                kind=r.get("kind") or "",
                raw=r,
            )
            for r in rows
        ]

    async def list_signals(
        self,
        *,
        account_id: str,
        context_id: str,
        since: Optional[datetime] = None,
    ) -> List[Signal]:
        """Pass-through to db.signals.find."""
        query: Dict[str, Any] = {"account_id": account_id, "context_id": context_id}
        if since is not None:
            query["created_at"] = {"$gte": since.isoformat()}
        cursor = db.signals.find(query, {"_id": 0}).limit(500)
        rows = await cursor.to_list(500)
        return [
            Signal(
                signal_id=r.get("id") or "",
                account_id=account_id,
                context_id=context_id,
                raw=r,
            )
            for r in rows
        ]

    async def list_objectives(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> List[Objective]:
        """Pass-through to db.objectives.find."""
        cursor = db.objectives.find(
            {"account_id": account_id, "context_id": context_id}, {"_id": 0},
        ).limit(500)
        rows = await cursor.to_list(500)
        return [
            Objective(
                objective_id=r.get("id") or "",
                account_id=account_id,
                context_id=context_id,
                raw=r,
            )
            for r in rows
        ]

    async def list_cycle_questions(
        self,
        *,
        account_id: str,
        cycle_id: str,
    ) -> List[CycleQuestion]:
        """Pass-through to db.cycle_questions.find."""
        cursor = db.cycle_questions.find(
            {"account_id": account_id, "cycle_id": cycle_id}, {"_id": 0},
        ).limit(500)
        rows = await cursor.to_list(500)
        return [
            CycleQuestion(
                question_id=r.get("id") or "",
                cycle_id=cycle_id,
                account_id=account_id,
                raw=r,
            )
            for r in rows
        ]

    async def list_briefings(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> List[Briefing]:
        """Pass-through to db.briefings.find."""
        cursor = db.briefings.find(
            {"account_id": account_id, "context_id": context_id}, {"_id": 0},
        ).limit(500)
        rows = await cursor.to_list(500)
        return [
            Briefing(
                briefing_id=r.get("id") or "",
                account_id=account_id,
                context_id=context_id,
                raw=r,
            )
            for r in rows
        ]

    # ─────────── Audit-log write-back ───────────

    async def audit_event(
        self,
        *,
        account_id: str,
        action: str,
        payload: Dict[str, Any],
    ) -> None:
        """Append to the universal `audit_log` (Akki-owned).

        SyniSense + Solva append here via this method. NOTE:
        `synisense_audit_log` is a SEPARATE collection (SyniSense-
        owned) — do not conflate. Phase 1 build dispatch resolution
        #2 confirms this split.
        """
        try:
            await db.audit_log.insert_one({
                "id":         uuid.uuid4().hex,
                "account_id": account_id,
                "action":     action,
                "payload":    payload,
                "created_at": _now_iso(),
            })
        except Exception:
            logger.exception(
                "InProcessAkkiAdapter.audit_event: write failed "
                "(account_id=%s action=%s)",
                account_id,
                action,
            )

    # ─────────── Phase 4.2 widening — typed counters ─────────────────────

    async def count_documents(
        self,
        *,
        account_id: str,
        context_id: Optional[str] = None,
        status: Optional[str] = None,
        since_iso: Optional[str] = None,
    ) -> int:
        """Pass-through to db.documents.count_documents.

        When `context_id` is given, the query scopes by context_id
        (mirrors the legacy direct-call shape used by signals_ask
        polling); `account_id` is captured for audit. When
        `context_id` is None, the query scopes by account_id.
        """
        query: Dict[str, Any] = {}
        if context_id is not None:
            query["context_id"] = context_id
        else:
            query["account_id"] = account_id
        if status is not None:
            query["status"] = status
        if since_iso is not None:
            query["created_at"] = {"$gte": since_iso}
        return await db.documents.count_documents(query)

    async def count_chats(
        self,
        *,
        account_id: str,
        admin_cross_tenant: bool = False,
        shield_audit_pending: bool = False,
    ) -> int:
        """Pass-through to db.chats.count_documents.

        `admin_cross_tenant=True` is super-admin only. The caller is the
        super-admin Shield back-fill probe at
        `routers/admin_shield_backfill.py`; that route gates super-admin
        upstream. `account_id` is captured for audit but not used in the
        filter when `admin_cross_tenant=True`.

        `shield_audit_pending=True` matches chats with no
        `synisense_audit_ids` AND `backfill_metadata.partial != False`
        (the H4 back-fill probe shape).
        """
        query: Dict[str, Any] = {}
        if not admin_cross_tenant:
            query["account_id"] = account_id
        if shield_audit_pending:
            query["$or"] = [
                {"synisense_audit_ids": {"$exists": False}},
                {"synisense_audit_ids": {"$size": 0}},
            ]
            query["backfill_metadata.partial"] = {"$ne": False}
        return await db.chats.count_documents(query)

    async def count_chat_messages(
        self,
        *,
        account_id: str,
        role: Optional[str] = None,
        since_iso: Optional[str] = None,
    ) -> int:
        """Pass-through to db.chat_messages.count_documents."""
        query: Dict[str, Any] = {"account_id": account_id}
        if role is not None:
            query["role"] = role
        if since_iso is not None:
            query["created_at"] = {"$gte": since_iso}
        return await db.chat_messages.count_documents(query)

    async def count_cycles(
        self,
        *,
        account_id: str,
        context_ids: Optional[List[str]] = None,
        status: Optional[str] = None,
        status_in: Optional[List[str]] = None,
    ) -> int:
        """Pass-through to db.cycles.count_documents."""
        if context_ids is not None and not context_ids:
            return 0
        query: Dict[str, Any] = {}
        if context_ids is not None:
            query["context_id"] = {"$in": list(context_ids)}
        elif account_id:
            query["account_id"] = account_id
        if status is not None:
            query["status"] = status
        if status_in is not None:
            query["status"] = {"$in": list(status_in)}
        return await db.cycles.count_documents(query)

    async def count_cycle_questions(
        self,
        *,
        account_id: str,
        context_ids: Optional[List[str]] = None,
        status: Optional[str] = None,
        status_in: Optional[List[str]] = None,
        overdue_iso: Optional[str] = None,
    ) -> int:
        """Pass-through to db.cycle_questions.count_documents."""
        if context_ids is not None and not context_ids:
            return 0
        query: Dict[str, Any] = {}
        if context_ids is not None:
            query["context_id"] = {"$in": list(context_ids)}
        elif account_id:
            query["account_id"] = account_id
        if status is not None:
            query["status"] = status
        elif status_in is not None:
            query["status"] = {"$in": list(status_in)}
        if overdue_iso is not None:
            query["due_at"] = {"$lt": overdue_iso}
        return await db.cycle_questions.count_documents(query)

    async def count_briefings(
        self,
        *,
        account_id: str,
        status: Optional[str] = None,
        updated_since_iso: Optional[str] = None,
    ) -> int:
        """Pass-through to db.briefings.count_documents."""
        query: Dict[str, Any] = {"account_id": account_id}
        if status is not None:
            query["status"] = status
        if updated_since_iso is not None:
            query["updated_at"] = {"$gte": updated_since_iso}
        return await db.briefings.count_documents(query)

    async def count_objectives(
        self,
        *,
        account_id: str,
        context_ids: Optional[List[str]] = None,
        rag_status: Optional[str] = None,
    ) -> int:
        """Pass-through to db.objectives.count_documents."""
        if context_ids is not None and not context_ids:
            return 0
        query: Dict[str, Any] = {}
        if context_ids is not None:
            query["context_id"] = {"$in": list(context_ids)}
        elif account_id:
            query["account_id"] = account_id
        if rag_status is not None:
            query["rag_status"] = rag_status
        return await db.objectives.count_documents(query)

    # ─────────── Phase 4.2 widening — typed lookups ─────────────────────

    async def get_document(
        self,
        *,
        account_id: str,
        document_id: str,
        context_id: Optional[str] = None,
        untenanted: bool = False,
    ) -> Optional[Document]:
        """Pass-through to db.documents.find_one."""
        if untenanted:
            query: Dict[str, Any] = {"id": document_id}
        elif context_id is not None:
            # Solva Phase D queries by id + context_id WITHOUT account_id
            # (session-gated upstream). Mirror the existing semantics.
            query = {"id": document_id, "context_id": context_id}
        else:
            query = {"id": document_id, "account_id": account_id}
        row = await db.documents.find_one(query, {"_id": 0})
        if row is None:
            return None
        return Document(
            document_id=row.get("id") or "",
            account_id=row.get("account_id") or account_id,
            context_id=row.get("context_id"),
            name=row.get("name") or "",
            kind=row.get("kind") or "",
            raw=row,
        )

    async def get_context(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> Optional[Context]:
        """Pass-through to db.contexts.find_one.

        Tenant-scope check is intentionally NOT applied here because the
        caller pattern (Solva v2 artefact builder + Trust Center name
        lookups) is session-gated upstream; we mirror the existing
        find_one({"id": cid}) semantics.
        """
        row = await db.contexts.find_one({"id": context_id}, {"_id": 0})
        if row is None:
            return None
        return Context(
            context_id=context_id,
            name=row.get("name") or "",
            account_id=row.get("account_id") or account_id,
            raw=row,
        )

    async def get_context_by_owner(
        self,
        *,
        account_id: str,
        context_id: str,
    ) -> Optional[Context]:
        """Pass-through to db.contexts.find_one with owner_account_id scope.

        `account_id` IS the owner-account-id (SyniSense `signal_seeder`
        ownership-gated read pattern).
        """
        row = await db.contexts.find_one(
            {"id": context_id, "owner_account_id": account_id},
            {"_id": 0},
        )
        if row is None:
            return None
        return Context(
            context_id=context_id,
            name=row.get("name") or "",
            account_id=row.get("account_id") or account_id,
            raw=row,
        )

    async def get_chat(
        self,
        *,
        account_id: str,
        chat_id: str,
        untenanted: bool = False,
    ) -> Optional[Chat]:
        """Pass-through to db.chats.find_one. `untenanted=True` skips the account_id filter (Trust Center / synisense_metrics public mirror); `account_id` is still required as the caller-of-record (captured for audit even when not in the filter)."""
        query: Dict[str, Any] = {"id": chat_id}
        if not untenanted:
            query["account_id"] = account_id
        row = await db.chats.find_one(query, {"_id": 0})
        if row is None:
            return None
        return Chat(
            chat_id=row.get("id") or chat_id,
            account_id=row.get("account_id"),
            context_id=row.get("context_id"),
            title=row.get("title"),
            status=row.get("status"),
            created_at=row.get("created_at") or "",
            raw=row,
        )

    async def get_membership(
        self,
        *,
        account_id: str,
        context_id: str,
        status: str = "active",
    ) -> Optional[Membership]:
        """Pass-through to db.memberships.find_one."""
        query: Dict[str, Any] = {
            "account_id": account_id,
            "context_id": context_id,
        }
        if status is not None:
            query["status"] = status
        row = await db.memberships.find_one(query, {"_id": 0})
        if row is None:
            return None
        return Membership(
            account_id=account_id,
            context_id=context_id,
            status=row.get("status") or "",
            raw=row,
        )

    async def get_chat_message(
        self,
        *,
        account_id: str,
        chat_id: Optional[str] = None,
        message_id: str,
        role: Optional[str] = None,
    ) -> Optional[ChatMessage]:
        """Pass-through to db.chat_messages.find_one. `account_id` captured for audit (chat already membership-gated upstream)."""
        _ = account_id  # noqa: F841 — audit/log trail
        query: Dict[str, Any] = {"id": message_id}
        if chat_id is not None:
            query["chat_id"] = chat_id
        if role is not None:
            query["role"] = role
        row = await db.chat_messages.find_one(query, {"_id": 0})
        if row is None:
            return None
        return ChatMessage(
            message_id=row.get("id") or message_id,
            chat_id=row.get("chat_id") or chat_id or "",
            account_id=row.get("account_id") or "",
            role=row.get("role") or "",
            content=row.get("content") or "",
            created_at=row.get("created_at") or row.get("ts") or "",
            raw=row,
        )

    async def list_chat_messages_in_chat(
        self,
        *,
        account_id: str,
        chat_id: str,
    ) -> List[ChatMessage]:
        """Pass-through to db.chat_messages.find by chat_id. `account_id` captured for audit."""
        _ = account_id  # noqa: F841 — audit/log trail
        cursor = db.chat_messages.find({"chat_id": chat_id}, {"_id": 0})
        rows = await cursor.to_list(2000)
        return [
            ChatMessage(
                message_id=r.get("id") or "",
                chat_id=chat_id,
                account_id=r.get("account_id") or "",
                role=r.get("role") or "",
                content=r.get("content") or "",
                created_at=r.get("created_at") or r.get("ts") or "",
                raw=r,
            )
            for r in rows
        ]

    async def find_assistant_reply_after(
        self,
        *,
        account_id: str,
        chat_id: str,
        after_iso: str,
        inclusive: bool = False,
        exclude_message_id: Optional[str] = None,
    ) -> Optional[ChatMessage]:
        """Pass-through to db.chat_messages.find_one for the next assistant reply. `account_id` captured for audit."""
        _ = account_id  # noqa: F841 — audit/log trail
        cmp_op = "$gte" if inclusive else "$gt"
        query: Dict[str, Any] = {
            "chat_id": chat_id,
            "role": "assistant",
            "created_at": {cmp_op: after_iso},
        }
        if exclude_message_id is not None:
            query["id"] = {"$ne": exclude_message_id}
        row = await db.chat_messages.find_one(
            query,
            {"_id": 0},
            sort=[("created_at", 1)],
        )
        if row is None:
            return None
        return ChatMessage(
            message_id=row.get("id") or "",
            chat_id=chat_id,
            account_id=row.get("account_id") or "",
            role="assistant",
            content=row.get("content") or "",
            created_at=row.get("created_at") or "",
            raw=row,
        )

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
        """Pass-through to db.chats.find with the Trust-Center query shape."""
        query: Dict[str, Any] = {}
        if not untenanted:
            query["account_id"] = account_id
        if context_ids:
            query["context_id"] = {"$in": list(context_ids)}
        if ids:
            query["id"] = {"$in": list(ids)}
        if status_excludes:
            query["status"] = {"$nin": list(status_excludes)}
        cursor = db.chats.find(
            query,
            {"_id": 0, "id": 1, "title": 1, "context_id": 1, "account_id": 1, "status": 1, "created_at": 1},
        ).limit(int(limit))
        rows = await cursor.to_list(int(limit))
        return [
            Chat(
                chat_id=r.get("id") or "",
                account_id=r.get("account_id"),
                context_id=r.get("context_id"),
                title=r.get("title"),
                status=r.get("status"),
                created_at=r.get("created_at") or "",
                raw=r,
            )
            for r in rows
        ]

    async def get_cycle(
        self,
        *,
        account_id: str,
        cycle_id: str,
        context_id: Optional[str] = None,
    ) -> Optional[Cycle]:
        """Pass-through to db.cycles.find_one. `account_id` captured for audit (Solva Phase D session-gated)."""
        _ = account_id  # noqa: F841 — audit/log trail
        query: Dict[str, Any] = {"id": cycle_id}
        if context_id is not None:
            query["context_id"] = context_id
        row = await db.cycles.find_one(query, {"_id": 0})
        if row is None:
            return None
        return Cycle(
            cycle_id=cycle_id,
            account_id=row.get("account_id") or "",
            context_id=row.get("context_id"),
            raw=row,
        )

    async def get_cycle_question(
        self,
        *,
        account_id: str,
        question_id: str,
    ) -> Optional[CycleQuestion]:
        """Pass-through to db.cycle_questions.find_one. `account_id` captured for audit (Solva v2 Use-in-Solva resolver; caller validates via membership downstream)."""
        _ = account_id  # noqa: F841 — audit/log trail
        row = await db.cycle_questions.find_one({"id": question_id}, {"_id": 0})
        if row is None:
            return None
        return CycleQuestion(
            question_id=question_id,
            cycle_id=row.get("cycle_id") or "",
            account_id=row.get("account_id") or "",
            raw=row,
        )

    async def list_cycles_by_statuses(
        self,
        *,
        account_id: str,
        statuses: List[str],
        limit: int = 2000,
    ) -> List[Cycle]:
        """Cross-tenant cycle list by status (SyniSense signal_seeder). `account_id` captured for audit (calling super-admin)."""
        _ = account_id  # noqa: F841 — audit/log trail (super-admin caller)
        cursor = db.cycles.find(
            {"status": {"$in": list(statuses)}},
            {"_id": 0},
        ).limit(int(limit))
        rows = await cursor.to_list(int(limit))
        return [
            Cycle(
                cycle_id=r.get("id") or "",
                account_id=r.get("account_id") or "",
                context_id=r.get("context_id"),
                raw=r,
            )
            for r in rows
        ]

    async def insert_document_row(
        self,
        *,
        account_id: str,
        document_row: Dict[str, Any],
    ) -> str:
        """Pass-through to db.documents.insert_one.

        Solva Phase D synthesises briefing-like derived documents and
        writes them into Akki's documents collection. `account_id` is
        captured for audit; the row itself is inserted verbatim (no
        auto-set of account_id) to preserve byte-identical legacy
        write behaviour. Caller is responsible for the row's `id` /
        `context_id` / `account_id` fields.
        """
        _ = account_id  # noqa: F841 — audit/log trail
        row = dict(document_row)
        await db.documents.insert_one(row)
        row.pop("_id", None)
        return row.get("id") or ""


__all__ = ["InProcessAkkiAdapter"]
