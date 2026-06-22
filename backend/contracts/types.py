"""Shared types for the Phase 1 contract surfaces.

These DTOs are the over-the-wire shape any contract method returns
or accepts. All are `dataclass(frozen=True)` — immutable, hashable,
stdlib-only. No pydantic dependency, no runtime validation.

Each DTO carries a `raw: Dict[str, Any]` field so a caller that
needs a field not surfaced in the typed shape can still reach it.
This is a Phase 1 escape hatch to preserve behaviour during the
adapter pass-through migration — Phase 2 / 3 will narrow the
surface as call sites migrate.

ShieldFailure is imported and re-exported from
services.synisense.shield.exceptions so contract consumers don't
have to reach into the SyniSense package for the exception type.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

# Re-export ShieldFailure under the contracts namespace so consumers
# import `from contracts.types import ShieldFailure` and never reach
# into services.synisense for the exception class.
from services.synisense.shield.exceptions import ShieldFailure  # noqa: F401


# ───────────────────────── Shield DTOs ─────────────────────────

@dataclass(frozen=True)
class ShieldRequest:
    """One Shield invocation payload (used by future batch APIs).

    Phase 1 doesn't surface a batch method — singleton calls only.
    The type exists in the contract namespace so Phase 1.B / Phase 2
    can add batching without a new dataclass migration."""
    content: str
    purpose: str
    consumer_id: str
    user_id: str
    model_preference: str = "balanced"
    internal_caller: bool = False
    system_msg: Optional[str] = None


@dataclass(frozen=True)
class ShieldResult:
    """Result of a single Shield round-trip."""
    response: str
    audit_id: Optional[str]
    trust_receipt: Optional[Dict[str, Any]]
    de_id_summary: Dict[str, Any]
    elapsed_ms: int
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditEvent:
    """A SyniSense audit row."""
    audit_id: str
    timestamp: str
    tenant_id: str
    purpose: str
    consumer_id: str
    outcome: str
    de_id_summary: Dict[str, Any]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrustReceipt:
    """An HMAC-signed trust receipt mirror row."""
    receipt_id: str
    audit_id: str
    tenant_id: str
    signature: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ShieldMetrics:
    """Aggregated Shield metrics for a tenant."""
    total_calls: int
    success_rate: float
    raw: Dict[str, Any] = field(default_factory=dict)


# ───────────────────────── Akki DTOs (cross-context reads) ─────

@dataclass(frozen=True)
class TenantProfile:
    """Identity profile for a tenant (the `accounts` row)."""
    account_id: str
    name: Optional[str]
    email: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Context:
    """A workspace context (the `contexts` row)."""
    context_id: str
    name: str
    account_id: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Cycle:
    """A cycle row."""
    cycle_id: str
    account_id: str
    context_id: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChatMessage:
    """A single chat message row."""
    message_id: str
    chat_id: str
    account_id: str
    role: str
    content: str
    created_at: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Document:
    """A document row (user-uploaded or Akki-generated)."""
    document_id: str
    account_id: str
    context_id: Optional[str]
    name: str
    kind: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Signal:
    """A signal row."""
    signal_id: str
    account_id: str
    context_id: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Objective:
    """A cycle objective row."""
    objective_id: str
    account_id: str
    context_id: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CycleQuestion:
    """A cycle question row (Q4Y entry)."""
    question_id: str
    cycle_id: str
    account_id: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Briefing:
    """A pre-meeting briefing row."""
    briefing_id: str
    account_id: str
    context_id: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TenantEntity:
    """A per-tenant proper-noun entry harvested for the de-id pipeline."""
    kind: str
    value: str
    source: str  # e.g. "accounts", "contexts", "cycles"


# ───────────────────────── Solva DTOs ─────────────────────────

@dataclass(frozen=True)
class SynthesisResult:
    """Result of a Solva v2 multi-workbook synthesize."""
    analysis_id: str
    headline: str
    observations: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    cache_key: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PhaseResult:
    """Result of a Solva phase run (A / B / C / D / E)."""
    session_id: str
    phase: str
    artefact: Dict[str, Any]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SolvaSessionState:
    """Snapshot of a Solva session for UI rendering."""
    session_id: str
    account_id: str
    phase: str
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SolvaInputs:
    """Inputs envelope for Solva refuse-to-decide checking."""
    workbook_present: bool
    objective: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RefusalReason:
    """A typed refusal returned by Solva when input is insufficient."""
    code: str
    detail: str


@dataclass(frozen=True)
class SolvaArtefact:
    """A Solva-produced artefact (export-ready)."""
    artefact_id: str
    session_id: str
    account_id: str
    raw: Dict[str, Any] = field(default_factory=dict)


__all__ = [
    "ShieldFailure",
    "ShieldRequest",
    "ShieldResult",
    "AuditEvent",
    "TrustReceipt",
    "ShieldMetrics",
    "TenantProfile",
    "Context",
    "Cycle",
    "ChatMessage",
    "Document",
    "Signal",
    "Objective",
    "CycleQuestion",
    "Briefing",
    "TenantEntity",
    "SynthesisResult",
    "PhaseResult",
    "SolvaSessionState",
    "SolvaInputs",
    "RefusalReason",
    "SolvaArtefact",
]
