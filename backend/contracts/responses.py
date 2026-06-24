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
    """`/me/first-session/*` (6 routes) and intake-style state-envelope
    responses. The wire shape is `{"state": <dict>, ...optional extras}`
    where `state` is the first-session state envelope (a dict with
    keys `status / started_at / completed_at / current_step /
    door_taken / artefact / intake / grandfathered`), and the optional
    extras include `questions` (GET /), `landing_cycle_id` (POST
    /choose-door under the demo door).

    Phase 5.5.2 (2026-06-24) — `state` was originally typed as
    `Optional[str]` under the Phase 3.0 narrowing batch. The first-
    session handlers genuinely return a dict, so FastAPI's response-
    model validator was raising `ResponseValidationError` and the 6
    routes were 500ing in production. Widened to `Optional[Dict[str,
    Any]]` to match the handler contract. `extra='allow'` preserves
    the optional sibling keys (`questions`, `landing_cycle_id`)
    documented above.
    """
    model_config = ConfigDict(extra="allow")
    state: Optional[Dict[str, Any]] = None


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



# ────────────────────────────────────────────────────────────────────────
# Phase 3.2 — additional shared response models authored to narrow the
# remaining 37 singleton routes from the Phase 3.1 marker pool. All carry
# `extra='allow'` so existing extra fields keep flowing through unchanged.
# ────────────────────────────────────────────────────────────────────────


class ChatModelsResponse(BaseModel):
    """`GET /api/chat/models` shape: `{default_model_id, models}`."""
    model_config = ConfigDict(extra="allow")
    default_model_id: Optional[str] = None
    models: Optional[List[Any]] = None


class ChatAttachmentResponse(BaseModel):
    """`POST /api/chats/{chat_id}/attach` shape: full attachment row
    (chat-context-document linkage + storage metadata).
    """
    model_config = ConfigDict(extra="allow")
    chat_id: Optional[str] = None
    context_id: Optional[str] = None
    document_id: Optional[str] = None
    name: Optional[str] = None
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    char_len: Optional[int] = None
    sensitivity: Optional[Any] = None
    storage_key: Optional[str] = None
    created_at: Optional[str] = None


class ChatAuditResponse(BaseModel):
    """`GET /api/chats/{chat_id}/audit` shape:
    `{chat_id, rows, verification_note}`.
    """
    model_config = ConfigDict(extra="allow")
    chat_id: Optional[str] = None
    rows: Optional[List[Any]] = None
    verification_note: Optional[str] = None


class ChatAuditPanelResponse(BaseModel):
    """`GET /api/chats/{chat_id}/audit-panel` per-message panel shape."""
    model_config = ConfigDict(extra="allow")
    audit_id: Optional[str] = None
    message_id: Optional[str] = None
    protective_event: Optional[Any] = None
    protective_layer_prose: Optional[str] = None
    provider_prose: Optional[str] = None
    references: Optional[Any] = None
    scores: Optional[Any] = None
    shielding_prose: Optional[str] = None


class ChatAuditAggregateResponse(BaseModel):
    """`GET /api/chats/{chat_id}/audit-panel/aggregate` aggregate shape."""
    model_config = ConfigDict(extra="allow")
    average_dilution: Optional[float] = None
    average_exposure_reduction: Optional[float] = None
    headline_prose: Optional[str] = None
    identifiers_shielded: Optional[int] = None
    llm_calls: Optional[int] = None
    message_count: Optional[int] = None


class GovernancePanelResponse(BaseModel):
    """`GET /api/me/governance` TrustPanel surface shape."""
    model_config = ConfigDict(extra="allow")
    audit_log: Optional[Any] = None
    connected_models: Optional[Any] = None
    inbound: Optional[Any] = None
    sensitivity: Optional[Any] = None
    shielding: Optional[Any] = None
    synisense: Optional[Any] = None


class IntelligenceRegenerateResponse(BaseModel):
    """`POST /api/contexts/{cid}/documents/{doc_id}/intelligence/regenerate`
    shape: `{doc_id, mode, status}`.
    """
    model_config = ConfigDict(extra="allow")
    doc_id: Optional[str] = None
    mode: Optional[str] = None
    status: Optional[str] = None


class JournalCommentaryResponse(BaseModel):
    """`POST /api/contexts/{cid}/documents/{doc_id}/journal-commentary`
    shape (sync result; the async sibling already returns AsyncJobResponse).
    """
    model_config = ConfigDict(extra="allow")
    cached: Optional[bool] = None
    commentary: Optional[Any] = None
    commentary_redacted: Optional[Any] = None
    doc_id: Optional[str] = None
    generated_at: Optional[str] = None
    synisense_version: Optional[str] = None


class ParagraphsResponse(BaseModel):
    """`GET /api/contexts/{cid}/documents/{doc_id}/paragraphs` shape."""
    model_config = ConfigDict(extra="allow")
    computed_at: Optional[str] = None
    doc_id: Optional[str] = None
    page_count: Optional[int] = None
    paragraphs: Optional[List[Any]] = None
    version: Optional[Any] = None


class CycleTeamResponse(BaseModel):
    """`GET /api/contexts/{cid}/cycle/team` shape."""
    model_config = ConfigDict(extra="allow")
    agenda_id: Optional[str] = None
    cycle_id: Optional[str] = None
    members: Optional[List[Any]] = None


class CycleContributionsListResponse(BaseModel):
    """`GET /api/contexts/{cid}/cycle/contributions` shape."""
    model_config = ConfigDict(extra="allow")
    agenda_id: Optional[str] = None
    contributions: Optional[List[Any]] = None
    cycle_id: Optional[str] = None


class CycleContributionResponse(BaseModel):
    """`POST /api/contexts/{cid}/cycle/contributions` (+ score) shape:
    full contribution row.
    """
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    agenda_id: Optional[str] = None
    agenda_item_id: Optional[str] = None
    body_text: Optional[str] = None
    context_id: Optional[str] = None
    created_at: Optional[str] = None
    cycle_id: Optional[str] = None
    kind: Optional[str] = None
    scored_at: Optional[str] = None
    scored_by: Optional[str] = None
    scores: Optional[Any] = None
    source_doc_id: Optional[str] = None
    status: Optional[str] = None
    team_member_id: Optional[str] = None
    title: Optional[str] = None


class FollowUpDraftsResponse(BaseModel):
    """`POST /api/contexts/{cid}/cycle/follow-ups/draft` shape:
    `{count, drafts}`.
    """
    model_config = ConfigDict(extra="allow")
    count: Optional[int] = None
    drafts: Optional[List[Any]] = None


class CycleFollowUpsResponse(BaseModel):
    """`GET /api/contexts/{cid}/cycle/follow-ups` shape."""
    model_config = ConfigDict(extra="allow")
    agenda_id: Optional[str] = None
    cycle_id: Optional[str] = None
    followups: Optional[List[Any]] = None


class CycleActionsResponse(BaseModel):
    """`GET /api/contexts/{cid}/cycle/actions` summary shape."""
    model_config = ConfigDict(extra="allow")
    as_of: Optional[str] = None
    context_id: Optional[str] = None
    counts: Optional[Any] = None
    sections: Optional[Any] = None


class MfaEnrollStartResponse(BaseModel):
    """`POST /api/auth/mfa/enroll/start` shape:
    `{otpauth_url, qr_data_url, secret}`.
    """
    model_config = ConfigDict(extra="allow")
    otpauth_url: Optional[str] = None
    qr_data_url: Optional[str] = None
    secret: Optional[str] = None


class MfaStatusResponse(BaseModel):
    """`GET /api/auth/mfa/status` shape."""
    model_config = ConfigDict(extra="allow")
    enrolled_at: Optional[str] = None
    locked: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    recovery_codes_remaining: Optional[int] = None


class OnboardingBriefsResponse(BaseModel):
    """`GET /api/onboarding-briefs` shape: `{slides}`."""
    model_config = ConfigDict(extra="allow")
    slides: Optional[List[Any]] = None


class AdminAuthEventsResponse(BaseModel):
    """`GET /api/admin/auth-events/events` summary shape."""
    model_config = ConfigDict(extra="allow")
    by_credential: Optional[Any] = None
    by_failure_reason: Optional[Any] = None
    dual_credentials_mismatched: Optional[int] = None
    dual_credentials_seen: Optional[int] = None
    failure: Optional[int] = None
    failure_rate_pct: Optional[float] = None
    recent: Optional[List[Any]] = None
    sampled_events: Optional[int] = None
    success: Optional[int] = None
    top_paths: Optional[Any] = None
    window_hours: Optional[int] = None


class DocumentEngagementResponse(BaseModel):
    """`GET /api/contexts/{cid}/documents/{doc_id}/engagement` shape."""
    model_config = ConfigDict(extra="allow")
    linked_count: Optional[int] = None
    linked_documents: Optional[List[Any]] = None
    readers: Optional[List[Any]] = None
    share_count: Optional[int] = None
    shares: Optional[List[Any]] = None
    unique_readers: Optional[int] = None
    view_count: Optional[int] = None


class PasswordResetTokenResponse(BaseModel):
    """`GET /api/auth/reset-password/{token}` shape:
    `{email_masked, valid}`.
    """
    model_config = ConfigDict(extra="allow")
    email_masked: Optional[str] = None
    valid: Optional[bool] = None


class TokenIssueResponse(BaseModel):
    """`POST /api/cohort/magic-link/issue` shape:
    `{expires_at, token}`.
    """
    model_config = ConfigDict(extra="allow")
    expires_at: Optional[str] = None
    token: Optional[str] = None


class CohortPreviewResponse(BaseModel):
    """`GET /api/cohort/magic-link/preview/{token}` shape."""
    model_config = ConfigDict(extra="allow")
    expires_at: Optional[str] = None
    first_name: Optional[str] = None
    organisation: Optional[str] = None


class SignalsResponse(BaseModel):
    """Signals extraction shape: `{signals}`."""
    model_config = ConfigDict(extra="allow")
    signals: Optional[List[Any]] = None


class AnomaliesResponse(BaseModel):
    """Anomalies extraction shape: `{anomalies}`."""
    model_config = ConfigDict(extra="allow")
    anomalies: Optional[List[Any]] = None


class DocumentExtractResponse(BaseModel):
    """`POST /api/contexts/{cid}/documents/{doc_id}/extract` shape."""
    model_config = ConfigDict(extra="allow")
    document_id: Optional[str] = None
    extract_goals: Optional[Any] = None
    extract_tasks: Optional[Any] = None
    extraction_queued: Optional[bool] = None
    has_extracted_text: Optional[bool] = None


class TaskCirculationResponse(BaseModel):
    """`GET /api/tasks/circulation/{token}` reviewer surface shape."""
    model_config = ConfigDict(extra="allow")
    docs: Optional[List[Any]] = None
    expires_at: Optional[str] = None
    own_comments: Optional[Any] = None
    reviewer_email: Optional[str] = None
    task: Optional[Any] = None


class TaskContributeResponse(BaseModel):
    """`GET /api/tasks/contribute/{token}` contributor surface shape."""
    model_config = ConfigDict(extra="allow")
    contribution: Optional[Any] = None
    contributor_email: Optional[str] = None
    docs: Optional[List[Any]] = None
    expires_at: Optional[str] = None
    peers: Optional[List[Any]] = None
    task: Optional[Any] = None
    your_due_date: Optional[str] = None
    your_status: Optional[str] = None



# ─── Phase 5.4 Narrowing Batch 1 ─────────────────────────────────────


class TaskCountsResponse(BaseModel):
    """`GET /api/tasks/counts` — per-state count plus a total.

    Wire shape is `{<state_name>: int, ..., "all": int}` where the keys
    are dynamic (driven by `TASK_STATES`). The model declares the
    invariant `all` field; sibling state-named keys flow through
    `extra='allow'` unchanged.
    """
    model_config = ConfigDict(extra="allow")
    all: Optional[int] = None


class TaskResponse(BaseModel):
    """Task-row shape returned by:
      - `GET /api/tasks/{task_id}`
      - `PATCH /api/tasks/{task_id}`
      - `POST /api/tasks/{tid}/commission`
      - `POST /api/tasks/{tid}/close`

    The handler returns `_sanitize_task(row)` from the `tasks`
    collection. Documented keys below are the stable contract; extras
    (e.g. `status_history`, `team`, `output_spec`, ad-hoc audit
    metadata) pass through via `extra='allow'`.
    """
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    account_id: Optional[str] = None
    context_id: Optional[str] = None
    name: Optional[str] = None
    objective: Optional[str] = None
    state: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat-row shape returned by:
      - `GET /api/chats/{chat_id}` (with `messages: [...]` appended)
      - `PATCH /api/chats/{chat_id}` (without `messages`)

    The handler returns the chat document (Akki-owned `chats`
    collection). On GET, a `messages` list is appended after the
    Mongo read. Documented keys below are the stable contract;
    sibling fields (`linked_context`, `shielding_policy`,
    `archived_at`, etc.) pass through via `extra='allow'`.
    """
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    account_id: Optional[str] = None
    context_id: Optional[str] = None
    title: Optional[str] = None
    model_id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    messages: Optional[List[Any]] = None
