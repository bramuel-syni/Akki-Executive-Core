"""SyniSenseContract — the Phase 1 governance surface.

Per Pre-Read §4.A. Five methods. Every method takes `account_id: str`
as a required keyword argument. Pass-through adapter lives at
`backend/contracts/_adapters/synisense.py`.

Phase 1 ships the surface only. Phase 2 migrates call sites. Phase 4
swaps the in-process adapter for an HTTP client.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Protocol, runtime_checkable

from .types import (
    AuditEvent,
    ShieldMetrics,
    ShieldResult,
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


__all__ = ["SyniSenseContract"]
