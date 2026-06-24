# Module Product Specs — Akki Platform (7 modules)

> **Phase 5.2 — Module-lens companion to `PRODUCT_FEATURE_REVIEW.md`.**
> Generated 2026-06-24. Source-of-truth basis: live router decorators in `/app/backend/routers/`, FE route table in `/app/frontend/src/App.js`, Phase 4.1 ownership map (134 routers), 68 typed contract methods, Phase 4.4 dual-mount slices (`/api/*` sha `cdcb23322bb82895`, `/v1/{context}/*` sha `acc51822aa8818ae`).
> Where `PRODUCT_FEATURE_REVIEW.md` reads bounded-context-first (SyniSense / Solva / Akki), this doc reads module-first (the surfaces the operator touches). It is engineering-authoritative: every endpoint cited resolves in the live OpenAPI, every UI route resolves in the FE router config, no features are invented.
> Honesty rule applies: **Live · Partial · Parked · Gated** — exactly one per module.

---

## 1. Chat

### Value statement
One conversational surface per context (multi-tenant scope) — every turn passes through the SyniSense Shield (deidentify → mint → reidentify → audit), so even a casual "what's our top governance risk?" question is auditable, redaction-aware, and quota-gated.

### Primary persona / role
Operator + Executive — the user-facing daily entry-point on the platform. Every authenticated member of a context can use Chat; superadmins additionally see the audit-panel surfaces.

### Core capabilities
- Multi-chat thread management per context (create, list, rename, archive, restore, delete).
- Streaming token-by-token replies (`POST /api/chats/{id}/messages/stream`).
- File-attached chat turns (image / document) — drives Shield's input-side classification.
- Per-turn Shield audit drill-down (input SHA, redactions, tokenized prompt, full audit chain) via the linked Trust Center.
- "Escalate to Solva" inline action — promotes a chat thread to a Solva v2 session for reasoning-grade output.
- Chat retention sweep (admin cron) + archived-chat retrieval.
- Audit ZIP export for compliance review.
- Search across the user's chats.

### UI entry points
- `/app/chat` → `Chat.jsx`
- `/app/chats/archived` → `ArchivedChats.jsx`
- Inline in `AppHome.jsx` (recent chats card)

### Backend endpoints
| Legacy `/api/*` | Versioned `/v1/akki/*` | Method | Auth |
|---|---|---|---|
| `/api/chats` | `/v1/akki/chats` | GET, POST | required |
| `/api/chats/search` | `/v1/akki/chats/search` | GET | required |
| `/api/chats/{chat_id}` | `/v1/akki/chats/{chat_id}` | GET, PATCH, DELETE | required + context-membership |
| `/api/chats/{chat_id}/restore` | `/v1/akki/chats/{chat_id}/restore` | POST | required + context-membership |
| `/api/chats/{chat_id}/messages` | `/v1/akki/chats/{chat_id}/messages` | POST | required + context-membership |
| `/api/chats/{chat_id}/messages/stream` | `/v1/akki/chats/{chat_id}/messages/stream` | POST | required + context-membership |
| `/api/chats/{chat_id}/attach` | `/v1/akki/chats/{chat_id}/attach` | POST | required + context-membership |
| `/api/chats/{chat_id}/audit` | `/v1/akki/chats/{chat_id}/audit` | GET | required + audit-role |
| `/api/chats/{chat_id}/audit/export.zip` | `/v1/akki/chats/{chat_id}/audit/export.zip` | GET | required + audit-role |
| `/api/chats/{chat_id}/governance/solva-escalation-clicked` | `/v1/akki/chats/{chat_id}/governance/solva-escalation-clicked` | POST | required + context-membership |
| `/api/chat/models` | `/v1/akki/chat/models` | GET | required |
| `/api/admin/chat-retention/sweep` | `/v1/akki/admin/chat-retention/sweep` | POST | superadmin |
| `/api/streaming/v9/...` | `/v1/akki/streaming/v9/...` | POST | required |

### Owning bounded context(s)
**Akki** (orchestration, persistence, UI surface). Every turn calls **SyniSense** via `get_synisense().shield_invoke(...)` — one of the 30 SyniSense typed contract methods.

### Data model touched
- `chats` (Akki-owned) — one row per thread.
- `chat_messages` (Akki-owned) — turn-level rows; references shield audit ids.
- `chat_message_audits` (Akki-owned) — local mirror of the shield-audit pointer (Phase G).
- `synisense_audit_log` (SyniSense-owned, **read only via contract method**) — Shield's per-call record.
- `synisense_trust_receipts` (SyniSense-owned, read-only via contract) — tamper-evident receipt per turn.

### Integration surfaces
- `get_synisense().shield_invoke(...)` per turn — the only path outbound to LLMs (Anthropic Claude Sonnet 4.5 via Emergent LLM Key).
- `get_synisense().issue_trust_receipt(...)` after every successful turn.
- `get_synisense().get_shield_audit_by_chat(...)` from the Trust Center surface.
- `get_akki().mark_solva_escalation_clicked(...)` from the inline "escalate" action.
- Quota gating via `services/llm_quota.py` (Akki-internal).

### Status
**Live.**

### Known limitations & debt
- Streaming Shield exists at the token level (`services/synisense/shield/streaming.py`) but the streaming Shield UI in the Trust Center is parked (per `PRODUCT_FEATURE_REVIEW.md §2.1`).
- Chat retention sweep is cron-driven; a per-user "delete now" path exists but the long-tail archive-and-purge policy is per-tenant config (no central admin UI yet).
- 6 `/api/chats/*` endpoints currently return `Optional[Dict[str, Any]]` with a `# phase-3.0:narrow-in-3.1` marker — Phase 5.2 Part B partially narrows these. See `responses.py` for the new models.

### Future / planned enhancements
None on roadmap. The Phase 4 / Phase 5 work pinned Chat as a "settled" surface; future enhancements (streaming Shield UI, multi-LLM-per-context, in-thread Solva embed) are tracked under Phase 6 +.

---

## 2. Solva

### Value statement
A multi-workbook reasoning surface that takes a question and a dossier of documents/signals and produces a multi-step, citation-pinned reasoning brief. Where Chat is "ask one question, get one answer", Solva is "ask one question, get a 6-section brief with every claim tied to a citation, a frame audit, and a downloadable PDF."

### Primary persona / role
Analyst + Chief-of-Staff. The user who'd rather wait 90 seconds for a board-quality brief than 5 seconds for a conversational reply.

### Core capabilities
- Solva v2 session lifecycle: create session, attach documents, frame-audit (LLM clarifies the question before answering), turn-by-turn reasoning, abandonment, fork.
- Multi-workbook document attach per session (analyst-grade dossier).
- Streaming reasoning-log surface (`GET /sessions/{sid}/reasoning-log`, `.../summary`, `.../synisense-breakdown`).
- Per-session PDF + DOCX export.
- Hand-off to Cycle Manager — pin a Solva brief as a decision-cycle item.
- Solva v2 artefact chunks (long runs stream their progress as fragments so the UI can render before the full brief is done).
- Solva Telemetry (admin) — per-key latency, token spend, citation-stability metric.
- Solva v1 / Phase-D / Phase-E legacy artefacts retained for back-compat (admin reports, chat-attached PDF rendering).
- Intent classifier (`POST /intent/classify`) — routes a free-text question to Solva v2 vs Chat vs Walk-in.

### UI entry points
- `/app/solva` → `SolvaApp.jsx`
- `/app/solva/sessions` → `SolvaSessions.jsx`
- `/app/solva/session/new`, `/app/solva/session/:sessionId` → `SolvaSession.jsx`
- `/app/solva/phase-d/session/new`, `/app/solva/phase-d/session/:sessionId` → `SolvaPhaseDSession.jsx`

### Backend endpoints
| Legacy `/api/*` | Versioned `/v1/solva/*` | Method | Auth |
|---|---|---|---|
| `/api/solva/v2/sessions` | `/v1/solva/v2/sessions` | GET, POST | required |
| `/api/solva/v2/sessions/{sid}` | `/v1/solva/v2/sessions/{sid}` | GET | required + context-membership |
| `/api/solva/v2/sessions/{sid}/frame-audit` | `/v1/solva/v2/sessions/{sid}/frame-audit` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/frame-audit-decision` | `/v1/solva/v2/sessions/{sid}/frame-audit-decision` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/turn` | `/v1/solva/v2/sessions/{sid}/turn` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/continue-chat` | `/v1/solva/v2/sessions/{sid}/continue-chat` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/attach-document` | `/v1/solva/v2/sessions/{sid}/attach-document` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/attached-documents/{doc_id}` | `/v1/solva/v2/sessions/{sid}/attached-documents/{doc_id}` | DELETE | required + context-membership |
| `/api/solva/v2/sessions/{sid}/reasoning-log` | `/v1/solva/v2/sessions/{sid}/reasoning-log` | GET | required + context-membership |
| `/api/solva/v2/sessions/{sid}/reasoning-log/summary` | `/v1/solva/v2/sessions/{sid}/reasoning-log/summary` | GET | required + context-membership |
| `/api/solva/v2/sessions/{sid}/synisense-breakdown` | `/v1/solva/v2/sessions/{sid}/synisense-breakdown` | GET | required + context-membership |
| `/api/solva/v2/sessions/{sid}/artefact-reasoning` | `/v1/solva/v2/sessions/{sid}/artefact-reasoning` | GET | required + context-membership |
| `/api/solva/v2/sessions/{sid}/abandon` | `/v1/solva/v2/sessions/{sid}/abandon` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/fork` | `/v1/solva/v2/sessions/{sid}/fork` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/handoff/cycle` | `/v1/solva/v2/sessions/{sid}/handoff/cycle` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/take-to-cycle` | `/v1/solva/v2/sessions/{sid}/take-to-cycle` | POST | required + context-membership |
| `/api/solva/v2/sessions/{sid}/export.pdf` | `/v1/solva/v2/sessions/{sid}/export.pdf` | GET | required + context-membership |
| `/api/solva/v2/sessions/{sid}/export.docx` | `/v1/solva/v2/sessions/{sid}/export.docx` | GET | required + context-membership |
| `/api/solva/v2/intent/classify` | `/v1/solva/v2/intent/classify` | POST | required |
| `/api/solva/v2/seed` | `/v1/solva/v2/seed` | GET | required |
| `/api/solva/v2/cron/stale-session-sweep` | `/v1/solva/v2/cron/stale-session-sweep` | POST | superadmin / cron |
| `/api/solva/v2/artefacts` | `/v1/solva/v2/artefacts` | POST | required |
| `/api/solva/v2/artefacts/{id}/stream` | `/v1/solva/v2/artefacts/{id}/stream` | GET | required |
| `/api/solva/briefing/*` | `/v1/solva/briefing/*` | (mixed) | required |
| `/api/admin/solva/key-usage` | `/v1/solva/admin/solva/key-usage` | GET | superadmin |
| `/api/admin/solva/diag-snapshot` | `/v1/solva/admin/solva/diag-snapshot` | GET | superadmin |
| `/api/solva/phase-d/*`, `/api/solva/phase-e/*` | `/v1/solva/phase-d/*`, `/v1/solva/phase-e/*` | (mixed) | required (legacy) |

### Owning bounded context(s)
**Solva** (the bounded context owns the routers in `solva_app.py`). Calls **SyniSense** via `get_synisense().shield_invoke(...)` for every LLM turn. Calls **Akki** via `get_akki().materialise_cycle_handoff(...)` on the cycle hand-off action. Solva's contract surface exposes 38 typed methods at `get_solva().*` consumed by Akki (e.g. `take_to_solva` from Pulse / Chat).

### Data model touched
- `solva_v2_sessions` (Solva-owned) — session lifecycle, frame-audit decisions.
- `solva_v2_turns` (Solva-owned) — turn-level reasoning rows.
- `solva_v2_reasoning_log` (Solva-owned) — per-turn reasoning fragment stream.
- `solva_v2_attached_documents` (Solva-owned).
- `solva_v2_artefacts` (Solva-owned) — chunked-render artefact rows.
- `solva_briefing_v2_*` (Solva-owned) — briefing artefacts.
- `solva_v1_artefacts`, `solva_chat_pdfs` (Solva-owned, legacy).
- `solva_telemetry_runs`, `solva_key_usage` (Solva-owned, admin telemetry).

### Integration surfaces
- `get_synisense().shield_invoke(...)` — every LLM call.
- `get_synisense().issue_trust_receipt(...)` — per turn.
- `get_akki().materialise_cycle_handoff(...)` — on `take-to-cycle`.
- `get_akki().resolve_documents_for_session(...)` — on `attach-document`.
- Consumed BY: `Chat` (escalate-to-Solva button), `Pulse` (take-to-Solva on a signal), `DocumentsPage` (analyse-via-Solva inline action).

### Status
**Live.**

### Known limitations & debt
- Solva v1 (`phase-d`, `phase-e`) is **Partial** — back-compat surface for partners integrated pre-v2; not on the active feature roadmap.
- Stale-session sweep is cron-only; no operator surface to bulk-discard parked sessions.
- Frame-audit LLM call uses the same Shield path as turns — adds ~3s P50 even for a 3-line clarifier.

### Future / planned enhancements
None on roadmap. Solva v2 is the production target; v1 retains until partner integrations cut over.

---

## 3. Work Studio

### Value statement
The "stitch it together" surface — combine documents + signals + decks + simulation outputs + Solva briefs into a multi-block artefact (a board paper, a one-pager, a strategic-goal write-up), then export as PDF or DOCX with full citation traceability.

### Primary persona / role
Chief-of-Staff + Analyst. The user who needs the output to land in a board pack with consistent formatting.

### Core capabilities
- Phase-C composer: pick a source (document / signal cluster / Solva brief / deck), render into a brief, save as draft, revise, version.
- Phase-C2 review surface: side-by-side revision diff, set-active version, enhance with a follow-up LLM pass.
- Overlay (Phase-3 overlay layer): document-grade workspace for live editing of work-studio artefacts (save / move-to-review / commit / revise / version / restore).
- From-source: instantiate a work-studio artefact directly from a document or a Solva session.
- Render: per-kind streaming render (board paper, one-pager, etc.).
- Export: PDF + DOCX export with status streaming (`exports/{id}/stream`) and signed download.
- Enhance: a second-pass LLM-driven polish on a finished artefact.
- Save-as-draft: persist mid-composition state.
- SyniSense breakdown per artefact (every block's Shield-audit trail).
- Activity feed: per-artefact change log.

### UI entry points
- `/app/work-studio` → `WorkStudio.jsx`
- `/app/work-studio/activity` → `WorkStudioActivity.jsx`
- `/app/work-studio/document/:artefactId` → `WorkStudioDocumentPage.jsx`
- `/app/studio/composer/:kind/:artefactId` → `StudioComposerPage.jsx`
- `/app/analyze` → `AnalyzeJournal.jsx` (the legacy `/app/work-studio/analyze` redirects here)
- `/app/decks/:deckId` → `Decks.jsx` (deck export surface)

### Backend endpoints
| Legacy `/api/*` | Versioned `/v1/akki/*` | Method | Auth |
|---|---|---|---|
| `/api/contexts/{ctx}/work-studio/from-source` | `/v1/akki/contexts/{ctx}/work-studio/from-source` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/artefacts` | `/v1/akki/contexts/{ctx}/work-studio/artefacts` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents` | `/v1/akki/contexts/{ctx}/work-studio/documents` | GET | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}` | `/v1/akki/contexts/{ctx}/work-studio/documents/{aid}` | GET, PATCH, DELETE | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}/save` | `/v1/akki/contexts/{ctx}/work-studio/documents/{aid}/save` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}/move-to-review` | `/v1/akki/contexts/{ctx}/work-studio/documents/{aid}/move-to-review` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}/commit` | `/v1/akki/contexts/{ctx}/work-studio/documents/{aid}/commit` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}/create-new-version` | `/v1/akki/.../create-new-version` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}/versions` | `/v1/akki/.../versions` | GET | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}/versions/{vid}` | `/v1/akki/.../versions/{vid}` | GET | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}/versions/{vid}/restore` | `/v1/akki/.../versions/{vid}/restore` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/{aid}/revise` | `/v1/akki/.../revise` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/export/{kind}` | `/v1/akki/contexts/{ctx}/work-studio/export/{kind}` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/exports/{eid}` | `/v1/akki/.../exports/{eid}` | GET | required + context-membership |
| `/api/contexts/{ctx}/work-studio/exports/{eid}/stream` | `/v1/akki/.../exports/{eid}/stream` | GET | required + context-membership |
| `/api/contexts/{ctx}/work-studio/exports/{eid}/download` | `/v1/akki/.../exports/{eid}/download` | GET | required (signed) |
| `/api/contexts/{ctx}/work-studio/enhance/{kind}` | `/v1/akki/contexts/{ctx}/work-studio/enhance/{kind}` | POST | required + context-membership |
| `/api/contexts/{ctx}/work-studio/documents/save-draft` | `/v1/akki/.../documents/save-draft` | POST | required + context-membership |
| `/api/work_studio/artefacts/{kind}/{aid}/synisense-breakdown` | `/v1/akki/work_studio/artefacts/{kind}/{aid}/synisense-breakdown` | GET | required + context-membership |
| Phase-C surface: `/api/work-studio/picker`, `/api/work-studio/exports`, `/api/work-studio/exports/{eid}/download`, `/api/work-studio/exports/{eid}` | `/v1/akki/work-studio/*` | (mixed) | required |
| Phase-C2 surface: `/api/work-studio-briefs/{bid}`, `/api/work-studio-briefs/{bid}/revisions`, `/api/work-studio-briefs/{bid}/revisions/{rid}/diff`, `/api/work-studio-briefs/{bid}/enhance`, `/api/work-studio-briefs/{bid}/set_active` | `/v1/akki/work-studio-briefs/*` | (mixed) | required + context-membership |

### Owning bounded context(s)
**Akki** (all 6 work-studio routers — `work_studio_export.py`, `work_studio_overlay.py`, `work_studio_phase_c.py`, `work_studio_phase_c2.py`, `work_studio_from_source.py`, `work_studio_render.py`). Calls **SyniSense** via Shield for every LLM-rendered block. Calls **Solva** via `get_solva().fetch_brief_for_studio(...)` when the source is a Solva session.

### Data model touched
- `work_studio_artefacts` (Akki-owned) — top-level brief / one-pager / board-paper rows.
- `work_studio_artefact_versions` (Akki-owned) — per-version snapshots.
- `work_studio_drafts` (Akki-owned) — mid-composition state.
- `work_studio_exports` (Akki-owned) — export-job lifecycle rows.
- `work_studio_briefs` (Akki-owned, Phase-C2) — review-flow brief rows.
- `decks`, `deck_slides` (Akki-owned) — deck artefacts (rendered via Work Studio's deck-kind path).

### Integration surfaces
- `get_synisense().shield_invoke(...)` — every LLM-rendered block.
- `get_solva().fetch_brief_for_studio(...)` — when source is a Solva session.
- `get_synisense().get_artefact_audit_breakdown(...)` — for the SyniSense-breakdown side-panel.
- Consumed BY: `Decks` (Decks.jsx uses the work-studio export pipeline for PDF), `Cycle` (work-studio artefacts can be pinned to cycle items).

### Status
**Live.**

### Known limitations & debt
- 10 `work_studio_overlay.py` endpoints currently return `Optional[Dict[str, Any]]` — Phase 5.2 Part B partially narrows.
- Export streaming uses SSE; clients must reconnect-and-resume manually on transient drops (no built-in resume protocol).
- Phase-C and Phase-C2 share the brief domain but the routers live in two files; consolidation tracked under Phase 6 +.

### Future / planned enhancements
None on roadmap. The Phase 4 / Phase 5 work pinned Work Studio as a settled surface.

---

## 4. Task Manager

### Value statement
Decision-cycle execution layer: turn a Solva brief / chat governance moment / signal into a tracked task with assignment, contributor invites, draft / review / circulation / final-production state machine, and a tamper-evident commit signature.

### Primary persona / role
Chief-of-Staff + Operator. The user who owns the "what happens next" after a brief lands.

### Core capabilities
- Task CRUD per context.
- Commission / close transitions.
- Counts surface (per-status badge feeds the AppHome card).
- Contributor invites with magic-link tokens (`/api/tasks/contribute/{token}`).
- Draft lifecycle: create draft, list drafts, patch contributor metadata.
- Intelligence layer per task: `GET .../intelligence` returns the LLM-generated brief; `POST .../intelligence/regenerate` triggers a refresh.
- Compile workflow (multi-stage state machine):
  - draft → review → circulation → final-production → commit
  - per-stage endpoints (`compile/draft`, `compile/review/complete`, `compile/circulation/send`, `compile/circulation/close`, `compile/final-production/apply-comment`, `compile/final-production/complete`, `compile/commit`).
- Circulation token surface (external reviewer flow): comment, upload, submit.
- Contributor reinvite.
- Per-account task-activity feed.
- Tasks & Initiatives (org-level view): `tasks_initiatives.router` exposes higher-level grouping.
- Agent-prefill: LLM proposes a draft based on a signal or document.

### UI entry points
- `/app/task-manager` → `TaskManager.jsx`
- `/app/task-manager/:taskId` → `TaskManager.jsx` (deep-link to a task)
- `/app/task-manager/activity` → `TaskManagerActivity.jsx`
- Contributor-portal (public, token-gated): `/contribute/:token` → `ContributorPortal.jsx`

### Backend endpoints
| Legacy `/api/*` | Versioned `/v1/akki/*` | Method | Auth |
|---|---|---|---|
| `/api/tasks` | `/v1/akki/tasks` | GET, POST | required |
| `/api/tasks/counts` | `/v1/akki/tasks/counts` | GET | required |
| `/api/tasks/{task_id}` | `/v1/akki/tasks/{task_id}` | GET, PATCH | required + context-membership |
| `/api/tasks/{tid}/commission` | `/v1/akki/tasks/{tid}/commission` | POST | required + context-membership |
| `/api/tasks/{tid}/close` | `/v1/akki/tasks/{tid}/close` | POST | required + context-membership |
| `/api/tasks/agent-prefill` | `/v1/akki/tasks/agent-prefill` | POST | required |
| `/api/tasks/{task_id}/drafts` | `/v1/akki/tasks/{task_id}/drafts` | GET | required + context-membership |
| `/api/tasks/{task_id}/contributions/{cid}` | `/v1/akki/tasks/{task_id}/contributions/{cid}` | PATCH | required + context-membership |
| `/api/tasks/{task_id}/intelligence` | `/v1/akki/tasks/{task_id}/intelligence` | GET | required + context-membership |
| `/api/tasks/{task_id}/intelligence/regenerate` | `/v1/akki/.../intelligence/regenerate` | POST | required + context-membership |
| `/api/tasks/{task_id}/compile` | `/v1/akki/tasks/{task_id}/compile` | GET | required + context-membership |
| `/api/tasks/{task_id}/compile/draft` | `/v1/akki/.../compile/draft` | POST | required + context-membership |
| `/api/tasks/{task_id}/compile/review/complete` | `/v1/akki/.../compile/review/complete` | POST | required + context-membership |
| `/api/tasks/{task_id}/compile/circulation/send` | `/v1/akki/.../compile/circulation/send` | POST | required + context-membership |
| `/api/tasks/{task_id}/compile/circulation/close` | `/v1/akki/.../compile/circulation/close` | POST | required + context-membership |
| `/api/tasks/{task_id}/compile/final-production/apply-comment` | `/v1/akki/.../apply-comment` | POST | required + context-membership |
| `/api/tasks/{task_id}/compile/final-production/complete` | `/v1/akki/.../complete` | POST | required + context-membership |
| `/api/tasks/{task_id}/compile/commit` | `/v1/akki/.../compile/commit` | POST | required + context-membership |
| `/api/tasks/circulation/{token}` | `/v1/akki/tasks/circulation/{token}` | GET | token-only (public) |
| `/api/tasks/circulation/{token}/comment` | `/v1/akki/.../comment` | POST | token-only |
| `/api/tasks/contribute/{token}` | `/v1/akki/tasks/contribute/{token}` | GET | token-only |
| `/api/tasks/contribute/{token}/upload` | `/v1/akki/.../upload` | POST | token-only |
| `/api/tasks/contribute/{token}/comment` | `/v1/akki/.../comment` | POST | token-only |
| `/api/tasks/contribute/{token}/submit` | `/v1/akki/.../submit` | POST | token-only |
| `/api/tasks/{task_id}/contributors/{cid}/reinvite` | `/v1/akki/.../reinvite` | POST | required + context-membership |
| `/api/accounts/{aid}/task-activity/recent` | `/v1/akki/accounts/{aid}/task-activity/recent` | GET | required (self) |
| `/api/contexts/{ctx}/tasks-initiatives` | `/v1/akki/contexts/{ctx}/tasks-initiatives` | GET, POST | required + context-membership |
| `/api/contexts/{ctx}/tasks-initiatives/{ti_id}` | `/v1/akki/contexts/{ctx}/tasks-initiatives/{ti_id}` | GET, PATCH, DELETE | required + context-membership |

### Owning bounded context(s)
**Akki** (`tasks.py`, `tasks_initiatives.py`). Calls **SyniSense** via Shield for every LLM-rendered intelligence brief. Calls **Solva** via `get_solva().attach_brief_to_task(...)` when an agent-prefill consumes a Solva session output.

### Data model touched
- `tasks` (Akki-owned) — task lifecycle rows.
- `task_contributions` (Akki-owned) — contributor invites, comments, uploads.
- `task_compile_state` (Akki-owned) — compile-state-machine snapshot.
- `task_intelligence` (Akki-owned) — cached LLM-generated brief per task.
- `task_drafts` (Akki-owned) — per-revision drafts.
- `task_activity_log` (Akki-owned) — feed.
- `tasks_initiatives` (Akki-owned) — org-level grouping.

### Integration surfaces
- `get_synisense().shield_invoke(...)` — every intelligence-generation + regenerate call.
- `get_solva().fetch_brief_for_task(...)` — when source is a Solva session.
- `get_akki().send_circulation_invite_email(...)` — uses SendGrid (user-supplied key).
- Consumed BY: `Cycle` / `Cycle Manager` (cycles pin tasks), `AppHome` / `Monitor` (counts card).

### Status
**Live.**

### Known limitations & debt
- 15 `routers/tasks.py` endpoints currently return `Optional[Dict[str, Any]]` with `# phase-3.0:narrow-in-3.1` markers — the highest concentration of polymorphic surfaces in any single module. Phase 5.2 Part B narrows the top traffic ones; remainder is carry-forward.
- Circulation token expiry is a hard 14-day window (no per-task override).
- Contributor reinvite cooldown is 24h (no admin override).
- Agent-prefill quality varies with task category (governance vs operational) — no per-category prompt template yet.

### Future / planned enhancements
None on roadmap. Task Manager is on the Phase 6 "consolidate compile-state-machine" candidate list but not yet scheduled.

---

## 5. Monitor

### Value statement
The "what changed?" surface per context — observability for the operator: which signals went red, which goals slipped, which decisions are overdue, which initiatives have stalled.

### Primary persona / role
Operator + Chief-of-Staff. The user who opens the platform daily to scan the state of their context.

### Core capabilities
- Single-shot context monitor (legacy): aggregates signals, goals-at-risk, unread counts, recent activity into a single dashboard payload.
- Per-kind drill (v2): one of `objectives`, `projects`, `roles`, `assessments` — each with full CRUD.
- Auto-suggest objectives (LLM-proposed objective list for a context).
- Auto-suggest projects (LLM-proposed project list).
- Owner-roles surface — who owns what.
- Status-assessment subsurface (`monitor_status_assessment.py`) — per-objective health-status with rationale.
- Daily-Review surface (separate page; consumes the same data) — "what's new since you last visited".

### UI entry points
- `/app/monitor` → `Monitor.jsx`
- `/app/review` → `DailyReview.jsx`
- AppHome `Monitor` card (inline summary)

### Backend endpoints
| Legacy `/api/*` | Versioned `/v1/akki/*` | Method | Auth |
|---|---|---|---|
| `/api/contexts/{ctx}/monitor` | `/v1/akki/contexts/{ctx}/monitor` | GET | required + context-membership |
| `/api/contexts/{ctx}/monitor/{kind}` | `/v1/akki/contexts/{ctx}/monitor/{kind}` | GET, POST | required + context-membership |
| `/api/contexts/{ctx}/monitor/{kind}/{rid}` | `/v1/akki/contexts/{ctx}/monitor/{kind}/{rid}` | GET, PATCH, DELETE | required + context-membership |
| `/api/contexts/{ctx}/monitor/auto-suggest-objectives` | `/v1/akki/contexts/{ctx}/monitor/auto-suggest-objectives` | GET | required + context-membership |
| `/api/contexts/{ctx}/monitor/auto-suggest-projects` | `/v1/akki/contexts/{ctx}/monitor/auto-suggest-projects` | GET | required + context-membership |
| `/api/contexts/{ctx}/monitor/owner-roles` | `/v1/akki/contexts/{ctx}/monitor/owner-roles` | GET | required + context-membership |
| `/api/contexts/{ctx}/monitor/{kind}/{rid}/status-assessment` | `/v1/akki/.../status-assessment` | GET, POST | required + context-membership |
| `/api/monitor` | `/v1/akki/monitor` | GET | required |
| `/api/daily-review` | `/v1/akki/daily-review` | GET | required |

### Owning bounded context(s)
**Akki** (`monitor.py`, `monitor_v2.py`, `monitor_status_assessment.py`). Reads SyniSense signals via `get_synisense().list_signals(...)` (and `count_goals_at_risk`, `count_unread_signals`) — 3 of the 24 SyniSense signal contract methods.

### Data model touched
- `monitor_objectives` (Akki-owned).
- `monitor_projects` (Akki-owned).
- `monitor_owner_roles` (Akki-owned).
- `monitor_status_assessments` (Akki-owned).
- `signals` (SyniSense-owned, **read-only via contract**) — for goals-at-risk + unread counts.

### Integration surfaces
- `get_synisense().count_goals_at_risk(...)`, `count_unread_signals(...)`, `list_signals(...)`.
- `get_synisense().shield_invoke(...)` — for auto-suggest LLM calls.
- Consumed BY: `AppHome` (Monitor card), `DailyReview` (composes Monitor + recent activity).

### Status
**Live.**

### Known limitations & debt
- Auto-suggest-objectives + auto-suggest-projects are LLM-grounded but the prompt-quality varies with context-domain density (rich-context Boards get good suggestions; thin-context Boards get generic ones).
- The status-assessment surface persists per-objective state but lacks a per-objective history graph (only latest assessment is queryable).
- Monitor v2's per-kind generic CRUD is `Optional[Dict[str, Any]]` typed — narrowing tracked.

### Future / planned enhancements
None on roadmap.

---

## 6. Pulse

### Value statement
The signals-consumption surface — a per-context feed of SyniSense-discovered intelligence events (risks, gaps, opportunities, dismissed items, bookmarked items) with comment + resolve + bookmark + share + take-to-Solva + take-to-task actions inline.

### Primary persona / role
Analyst + Operator. The user who wants the highest-signal-to-noise daily scan of "what does the platform think I should look at?"

### Core capabilities
- Per-context Pulse feed (`GET .../pulse/feed`).
- Across-boards aggregation (`GET .../pulse/across-boards`).
- Signal lifecycle actions: comment / delete-comment / share / resolve / unresolve / bookmark / unbookmark / save / take-to-Solva.
- Pulse Ideas (separate page) — surfaces LLM-proposed actions / next-steps grounded in the feed.
- Lens filtering (signal-type, severity, owner, date-range).

### UI entry points
- `/app/pulse` → `Pulse.jsx`
- `/app/pulse/ideas` → `PulseIdeas.jsx`

### Backend endpoints
| Legacy `/api/*` | Versioned `/v1/akki/*` | Method | Auth |
|---|---|---|---|
| `/api/contexts/{ctx}/pulse/feed` | `/v1/akki/contexts/{ctx}/pulse/feed` | GET | required + context-membership |
| `/api/contexts/{ctx}/pulse/across-boards` | `/v1/akki/contexts/{ctx}/pulse/across-boards` | GET | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/comment` | `/v1/akki/.../comment` | POST | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/comments/{cid}` | `/v1/akki/.../comments/{cid}` | DELETE | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/share` | `/v1/akki/.../share` | POST | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/resolve` | `/v1/akki/.../resolve` | POST | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/unresolve` | `/v1/akki/.../unresolve` | POST | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/bookmark` | `/v1/akki/.../bookmark` | POST | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/unbookmark` | `/v1/akki/.../unbookmark` | POST | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/save` | `/v1/akki/.../save` | POST | required + context-membership |
| `/api/contexts/{ctx}/pulse/signals/{sid}/take-to-solva` | `/v1/akki/.../take-to-solva` | POST | required + context-membership |
| `/api/pulse/ideas/*` | `/v1/akki/pulse/ideas/*` | (mixed) | required + context-membership |

### Owning bounded context(s)
**Akki** (`pulse.py`). All Pulse data lives in **SyniSense**'s `signals` collection — Akki only orchestrates the consumption. Calls `get_synisense().list_pulse_feed_signals(...)`, `add_signal_comment(...)`, `delete_signal_comment(...)`, `mark_signal_resolved(...)`, `mark_signal_unresolved(...)`, `bookmark_signal(...)`, `unbookmark_signal(...)`, `dismiss_signal(...)` — 8 of the 24 SyniSense signal contract methods.

### Data model touched
- `signals` (SyniSense-owned, all access via contract method).
- `signal_comments` (SyniSense-owned, via contract).
- `pulse_shares` (Akki-owned) — share-token rows for the inline share action.
- `pulse_ideas` (Akki-owned) — LLM-proposed-next-step cache.

### Integration surfaces
- `get_synisense().list_pulse_feed_signals(...)` — primary feed query.
- `get_synisense().add_signal_comment(...)`, `delete_signal_comment(...)`, `mark_signal_resolved(...)`, etc. — every Pulse action.
- `get_solva().create_session_from_signal(...)` — on `take-to-solva`.
- `get_synisense().shield_invoke(...)` — on Pulse Ideas LLM call.
- Consumed BY: `AppHome` (recent pulse card), `Monitor` (signal-derived metrics).

### Status
**Live.**

### Known limitations & debt
- Pulse Ideas LLM grounding is per-context but uses a fixed prompt template — no per-tenant tuning yet.
- Across-boards aggregation is N+1 query shape; OK at SMB scale (≤10 boards/user) but is on the Phase 6 query-consolidation list.
- Comment soft-delete behaviour is opaque — `DELETE /comments/{cid}` flips a flag but the comment row stays in the audit trail.

### Future / planned enhancements
None on roadmap.

---

## 7. Learn

### Value statement
On-demand governance / sector / regulatory research — an LLM-grounded "explain this concept" surface that personalises its output to the user's active context (sector + jurisdiction + board-type weighting).

### Primary persona / role
Operator (governance-curious) + Analyst (background-research). The user who'd otherwise open a browser tab to Google a regulator name.

### Core capabilities
- Single research call: topic + optional context-id → LLM-grounded research article personalised to the user's sector/jurisdiction/board-type.
- Personalisation layer: when a `context_id` is supplied, the prompt weights the output to the sector (e.g. Kenyan banking → CBK/CMA references) and jurisdiction (Kenya / UK / US / South Africa / Nigeria / Singapore / EU).
- LLM call goes through SyniSense Shield like every other LLM-producing handler.

### UI entry points
- `/app/learn` → `Learn.jsx`
- `/app/learn/:id` → `Learn.jsx` (deep-link to a saved research article)

### Backend endpoints
| Legacy `/api/*` | Versioned `/v1/akki/*` | Method | Auth |
|---|---|---|---|
| `/api/learn/research` | `/v1/akki/learn/research` | POST | required |

### Owning bounded context(s)
**Akki** (`learn.py`). Calls **SyniSense** via `get_synisense().shield_invoke(...)` for the research LLM call.

### Data model touched
- No persistent collection of its own. Each call is a per-session LLM hit; the FE caches the result client-side. The deep-link `/app/learn/:id` is intended for future server-side persistence (see "Future / planned enhancements").

### Integration surfaces
- `get_synisense().shield_invoke(...)` — every research call.
- Reads the user's active context via `get_current_account` + the active-context resolver to seed the personalisation paragraph.

### Status
**Partial.** The research endpoint is **Live**, but the surface is the smallest of the seven modules (single endpoint, no persistence, no library / save / share). The `/app/learn/:id` route exists in the FE router config but currently re-runs the research call rather than fetching a persisted article — the persistence layer is on backlog.

### Known limitations & debt
- No persistence: every visit re-runs the LLM call. The `/app/learn/:id` route is forward-declared, not backed.
- No save / share / library surface — the result lives only in the current browser session.
- Personalisation hard-codes a regulator-name lookup table inline in the prompt; new jurisdictions need a code change rather than admin config.
- The router prefix is `/api` (not `/api/learn`) — every other module uses a sub-prefix; minor inconsistency, harmless.

### Future / planned enhancements
- **Persistence layer**: store research articles per-user with a Library tab. (Tracked, no committed sprint.)
- **Curated library**: editorial / partner-supplied research articles seeded per-jurisdiction. (Discussed in `PRODUCT.md`, no sprint.)

---

## Cross-module map (informational)

The 7 modules above are the operator-facing surfaces. The platform also exposes (NOT covered by this module-lens doc — see `PRODUCT_FEATURE_REVIEW.md` for the bounded-context view):

- **Shield / Trust Center** — SyniSense's PII-guardrail + per-turn forensic surface (every LLM call in every module above passes through it).
- **Signals API** — the SyniSense surface Pulse + Monitor consume; 24 of the 30 SyniSense typed contract methods.
- **Auth / Identity / Context membership** — Akki orchestrator surface; covers 27 routers.
- **Sandbox / Inbox / Sharing / Cohort console / Cycle Manager / Briefings / Decks / Documents / Strategic goals / Simulate / Walk-in / Lens** — Akki product surfaces sibling to the 7 modules above.

Cross-cutting integration map (every LLM call in every module above) is **SyniSense** via `get_synisense().shield_invoke(...)`. Every cross-context call goes through one of the 68 typed contract methods enforced by the Phase 4.1 boundary-import invariant.

---

## Honesty footer

This doc was generated against the live codebase on 2026-06-24. Where a module's documented endpoint disagrees with the live OpenAPI, the codebase wins — file a delta and update this doc. Where a module's documented UI route disagrees with `/app/frontend/src/App.js`, the FE router wins.

Status decisions:
- **Chat** — Live.
- **Solva** — Live.
- **Work Studio** — Live.
- **Task Manager** — Live.
- **Monitor** — Live.
- **Pulse** — Live.
- **Learn** — Partial (live endpoint, no persistence layer, forward-declared deep-link route).
