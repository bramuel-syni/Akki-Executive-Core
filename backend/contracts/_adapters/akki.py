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
    ChatMessage,
    Context,
    Cycle,
    CycleQuestion,
    Document,
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
    ) -> List[Cycle]:
        """Pass-through to db.cycles.find."""
        query: Dict[str, Any] = {"account_id": account_id}
        if context_id is not None:
            query["context_id"] = context_id
        cursor = db.cycles.find(query, {"_id": 0})
        rows = await cursor.to_list(1000)
        return [
            Cycle(
                cycle_id=r.get("id") or "",
                account_id=account_id,
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


__all__ = ["InProcessAkkiAdapter"]
