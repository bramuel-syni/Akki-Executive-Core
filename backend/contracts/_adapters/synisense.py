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


__all__ = ["InProcessSyniSenseAdapter"]
