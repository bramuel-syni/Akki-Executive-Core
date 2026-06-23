"""Phase 3.1 shared response models.

Open-shape Pydantic models with `extra='allow'` — they DOCUMENT the
expected response fields without stripping anything the route emits
beyond those fields. This is the safest narrowing path: drift on the
declared field set is catchable by the FE zod codegen; unrelated extra
fields pass through unchanged.

Used by Phase 3.1 narrowing to replace `Optional[Dict[str, Any]]`
baselines from Phase 3.0 with shape-bearing models on hot-path routes
where the response pattern is well-known.

NO behaviour change vs Phase 3.0 baseline (verified via FastAPI
TestClient pre-flight in Phase 3.1 §6).
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class StateOnlyResponse(BaseModel):
    """Common shape across `/me/first-session/*` and intake-style routes:
    `{"state": "<phase>", ...optional extras...}`.
    """
    model_config = ConfigDict(extra="allow")
    state: Optional[str] = None


class OkResponse(BaseModel):
    """Acknowledgment shape: `{"ok": True}` (sometimes with `message`).
    Used by delete/refresh/governance-click endpoints.
    """
    model_config = ConfigDict(extra="allow")
    ok: Optional[bool] = None
    message: Optional[str] = None


class ItemsListResponse(BaseModel):
    """Paged-list shape: `{"items": [...], "next_cursor": ..., "total": ...}`.
    Used by portfolio / recent-views / work-studio document lists / etc.
    """
    model_config = ConfigDict(extra="allow")
    items: Optional[List[Any]] = None
    next_cursor: Optional[str] = None
    total: Optional[int] = None
    total_pending: Optional[int] = None


class AsyncJobResponse(BaseModel):
    """Async-job-kicked shape: `{"job_id": "...", "kind": "...", "status": "queued"}`.
    Used by document async-generate-meta / summary-async / journal-commentary-async.
    """
    model_config = ConfigDict(extra="allow")
    job_id: Optional[str] = None
    kind: Optional[str] = None
    status: Optional[str] = None


class IdResponse(BaseModel):
    """Row-id-returning shape: `{"id": "...", optional_extras}` or
    `{"deleted": True, "id": "..."}` for tombstone returns.
    """
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    deleted: Optional[bool] = None


class AuthSessionResponse(BaseModel):
    """Login / refresh / OAuth-finish shape:
    `{"access_token": "...", "account": {...}, "contexts": [...]}`.
    """
    model_config = ConfigDict(extra="allow")
    access_token: Optional[str] = None
    account: Optional[Dict[str, Any]] = None
    contexts: Optional[List[Any]] = None


class DiffResponse(BaseModel):
    """Evolution-diff shape: `{"diff": [...], "previous_doc": {...}}`."""
    model_config = ConfigDict(extra="allow")
    diff: Optional[List[Any]] = None
    previous_doc: Optional[Dict[str, Any]] = None


class ExportPolicyResponse(BaseModel):
    """Export-permission probe shape:
    `{"can_export": bool, "watermark_label": "...", "watermark_required": bool}`.
    """
    model_config = ConfigDict(extra="allow")
    can_export: Optional[bool] = None
    watermark_label: Optional[str] = None
    watermark_required: Optional[bool] = None


class BriefsCountResponse(BaseModel):
    """Briefs-summary shape: `{"briefs": [...], "count": int}`."""
    model_config = ConfigDict(extra="allow")
    briefs: Optional[List[Any]] = None
    count: Optional[int] = None


class ByContextSummaryResponse(BaseModel):
    """Cross-context aggregate shape: `{"by_context": [...], "total_pending": int}`
    or `{"by_context": [...], "by_kind": [...], "total": int}`.
    """
    model_config = ConfigDict(extra="allow")
    by_context: Optional[List[Any]] = None
    by_kind: Optional[List[Any]] = None
    total: Optional[int] = None
    total_pending: Optional[int] = None


class CompilationStartResponse(BaseModel):
    """Work Studio compile / draft-compilation start shape:
    `{"compilation_id": "...", "export_id": "...", "idempotent": bool, "status": "..."}`.
    """
    model_config = ConfigDict(extra="allow")
    compilation_id: Optional[str] = None
    export_id: Optional[str] = None
    idempotent: Optional[bool] = None
    status: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Chat-message shape: `{"id": "...", "role": "...", "content": "...", "created_at": "..."}`.
    Used by chat list / chat single message endpoints.
    """
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    role: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[str] = None


class TaskSummaryResponse(BaseModel):
    """Task shape: stable `id / title / status / context_id / account_id` core fields."""
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    context_id: Optional[str] = None
    account_id: Optional[str] = None


class DocumentSummaryResponse(BaseModel):
    """Document shape: stable `id / title / context_id / created_at` core fields."""
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    title: Optional[str] = None
    context_id: Optional[str] = None
    created_at: Optional[str] = None


class CycleSummaryResponse(BaseModel):
    """Cycle shape: stable `id / context_id / status / created_at` core fields."""
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    context_id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class AccountWrapResponse(BaseModel):
    """Auth/session-update shape: `{"account": {...}, optional contexts}`.
    Used by declare-role / default-context / settings update endpoints.
    """
    model_config = ConfigDict(extra="allow")
    account: Optional[Dict[str, Any]] = None
    contexts: Optional[List[Any]] = None


class StatusKindResponse(BaseModel):
    """Generic status/kind shape: `{"status": "...", "kind": "...", ...}`.
    Used by document upload / task hash / draft / mode response endpoints.
    """
    model_config = ConfigDict(extra="allow")
    status: Optional[str] = None
    kind: Optional[str] = None


class ArtefactRedirectResponse(BaseModel):
    """Work-studio artefact creation shape:
    `{"artefact_id": "...", "kind": "...", "redirect_url": "...", "brief_id": "..."}`.
    """
    model_config = ConfigDict(extra="allow")
    artefact_id: Optional[str] = None
    kind: Optional[str] = None
    redirect_url: Optional[str] = None
    brief_id: Optional[str] = None
    title: Optional[str] = None
    document_id: Optional[str] = None
    active_revision_id: Optional[str] = None


class SnapshotResponse(BaseModel):
    """Snapshot-saved shape: `{"snapshot_id": "...", "saved_at": "..."}`."""
    model_config = ConfigDict(extra="allow")
    snapshot_id: Optional[str] = None
    saved_at: Optional[str] = None


class DocumentMetaResponse(BaseModel):
    """Document metadata shape (generate-meta):
    `{"display_name": "...", "description": "...", "shielding": ..., "mode": "..."}`.
    """
    model_config = ConfigDict(extra="allow")
    display_name: Optional[str] = None
    description: Optional[str] = None
    shielding: Optional[Any] = None
    shielding_masked: Optional[Any] = None
    mode: Optional[str] = None


class ThreadAncestryResponse(BaseModel):
    """Document thread / cycle ancestry shape:
    `{"ancestors": [...], "descendants": [...]}`.
    """
    model_config = ConfigDict(extra="allow")
    ancestors: Optional[List[Any]] = None
    descendants: Optional[List[Any]] = None


class DraftLifecycleResponse(BaseModel):
    """Draft-session lifecycle shape:
    `{"draft_session_id": "...", "export_id": "...", "idempotent_update": bool,
      "lifecycle_state": "...", "updated_at": "..."}`.
    """
    model_config = ConfigDict(extra="allow")
    draft_session_id: Optional[str] = None
    export_id: Optional[str] = None
    idempotent_update: Optional[bool] = None
    lifecycle_state: Optional[str] = None
    updated_at: Optional[str] = None


class ObjectiveSourceResponse(BaseModel):
    """Objective / source / success-criteria shape (strategic goals):
    `{"objective": ..., "source": ..., "success_criteria": [...]}`.
    """
    model_config = ConfigDict(extra="allow")
    objective: Optional[Any] = None
    source: Optional[Any] = None
    success_criteria: Optional[List[Any]] = None


class ScheduleResponse(BaseModel):
    """Schedule shape: `{"schedule": {...}}`. Used by cycle schedule endpoints."""
    model_config = ConfigDict(extra="allow")
    schedule: Optional[Dict[str, Any]] = None


class CommitteesResponse(BaseModel):
    """Committee/team listing shape: `{"committees": [...]}`."""
    model_config = ConfigDict(extra="allow")
    committees: Optional[List[Any]] = None


class TaskHashResponse(BaseModel):
    """Task-hash / contributor-readiness shape:
    `{"task_id": "...", "task_hash": "...", "status": "...",
      optional contributor_id / readiness_score / team}`.
    """
    model_config = ConfigDict(extra="allow")
    task_id: Optional[str] = None
    task_hash: Optional[str] = None
    status: Optional[str] = None
    contributor_id: Optional[str] = None
    readiness_score: Optional[float] = None
    team: Optional[Any] = None


class ExportStartResponse(BaseModel):
    """Export-job start shape: `{"export_id": "...", "kind": "...",
      "output_format": "...", "status": "...", "created_at": "..."}`.
    """
    model_config = ConfigDict(extra="allow")
    export_id: Optional[str] = None
    kind: Optional[str] = None
    output_format: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None


class WorkbookAnalysisResponse(BaseModel):
    """Workbook analysis shape: stable `id / context_id / account_id / status` core fields."""
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    context_id: Optional[str] = None
    account_id: Optional[str] = None
    status: Optional[str] = None
