"""Phase 1 contract package — single canonical surface for cross-context calls.

Exports the three contract Protocols + shared DTOs.

Adapters live under `backend/contracts/_adapters/` and are the
PASS-THROUGH implementations used in Phase 1. Phase 2 migrates call
sites to use the contracts; Phase 4.2 swaps the in-process adapters
for HTTP clients via the `BOUNDED_CONTEXT_TRANSPORT` env var
(default `inproc`; set to `http` to flip every accessor below to
its `httpx`-backed variant).

Usage example (Phase 2+):

    from contracts import SyniSenseContract, get_synisense
    contract: SyniSenseContract = get_synisense()
    result = await contract.shield_invoke(
        content=prompt, purpose="chat", account_id=current["id"],
        consumer_id="chat", user_id=current["id"],
    )
"""
from __future__ import annotations

import os

# Re-export the Protocol classes.
from .akki import AkkiContract
from .solva import SolvaContract
from .synisense import SyniSenseContract

# Re-export the shared DTOs at the package level so callers don't have
# to dig into contracts.types.
from .types import (  # noqa: F401
    AuditEvent,
    Briefing,
    Chat,
    ChatMessage,
    Context,
    Cycle,
    CycleQuestion,
    Document,
    Membership,
    Objective,
    PhaseResult,
    RefusalReason,
    ShieldFailure,
    ShieldMetrics,
    ShieldRequest,
    ShieldResult,
    Signal,
    SolvaArtefact,
    SolvaInputs,
    SolvaSessionState,
    SynthesisResult,
    TenantEntity,
    TenantProfile,
    TrustReceipt,
)


# Dependency-injection accessors. Phase 1 returns the in-process
# adapter; Phase 4.2 swaps these for HTTP-client adapters via env
# config (set `BOUNDED_CONTEXT_TRANSPORT=http` — no caller change
# required).

def _transport_mode() -> str:
    """Lookup at call time so tests / Phase 4.3 boot can flip it."""
    return os.environ.get("BOUNDED_CONTEXT_TRANSPORT", "inproc").strip().lower()


def get_synisense() -> SyniSenseContract:
    """Return the active SyniSenseContract implementation."""
    if _transport_mode() == "http":
        from ._adapters._http_client import get_http_synisense
        return get_http_synisense()  # type: ignore[return-value]
    from ._adapters.synisense import InProcessSyniSenseAdapter
    return InProcessSyniSenseAdapter()


def get_solva() -> SolvaContract:
    """Return the active SolvaContract implementation."""
    if _transport_mode() == "http":
        from ._adapters._http_client import get_http_solva
        return get_http_solva()  # type: ignore[return-value]
    from ._adapters.solva import InProcessSolvaAdapter
    return InProcessSolvaAdapter()


def get_akki() -> AkkiContract:
    """Return the active AkkiContract implementation."""
    if _transport_mode() == "http":
        from ._adapters._http_client import get_http_akki
        return get_http_akki()  # type: ignore[return-value]
    from ._adapters.akki import InProcessAkkiAdapter
    return InProcessAkkiAdapter()


__all__ = [
    "SyniSenseContract",
    "SolvaContract",
    "AkkiContract",
    "get_synisense",
    "get_solva",
    "get_akki",
    # DTOs
    "AuditEvent",
    "Briefing",
    "Chat",
    "ChatMessage",
    "Context",
    "Cycle",
    "CycleQuestion",
    "Document",
    "Membership",
    "Objective",
    "PhaseResult",
    "RefusalReason",
    "ShieldFailure",
    "ShieldMetrics",
    "ShieldRequest",
    "ShieldResult",
    "Signal",
    "SolvaArtefact",
    "SolvaInputs",
    "SolvaSessionState",
    "SynthesisResult",
    "TenantEntity",
    "TenantProfile",
    "TrustReceipt",
]
