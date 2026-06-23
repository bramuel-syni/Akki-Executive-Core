# Product Features Review — SyniSense · Solva · Akki

> **Phase 5 — Sell-Ready snapshot. Generated 2026-06-23.**
> Source-of-truth basis: 134-router Phase 4.1 ownership map + 68 typed contract methods + live OpenAPI surface (`/api/*` slice sha `cdcb23322bb82895`, `/v1/{context}/*` slice sha `acc51822aa8818ae`). This doc is written for hybrid engineering + sales/diligence reading and follows an honesty rule: every feature is labelled with one of **Live · Partial · Parked · Gated**. Nothing is invented. Nothing is oversold.

---

## 1. Executive Summary

**SyniSense** is a data-governance / PII pipeline product. Every outbound LLM call in the platform routes through a deidentify → mint → reidentify → audit pipeline ("Shield"). On top of that pipeline sits a Trust Center surface (per-turn forensic drill-down with input SHA, tokenized prompt, redactions, audit chain) plus a Signals API that materialises Shield-discovered or document-ingested intelligence as typed events. Primary persona: governance lead at a regulated SMB. Maturity: **live** for Shield + Trust Center + Signals; **partial** for streaming Shield (token-level streaming exists; real-time UI Shield panel parked).

**Solva** is a reasoning-governance / multi-workbook analyzer. Users assemble dossiers ("analyses") that combine multiple documents, ask the platform to render a multi-step reasoning brief, and pin every produced section to the underlying citations. Solva v2 introduced session-scoped artefacts (briefings, decks, PDFs) and an admin telemetry panel surfacing run latency, token spend, and citation-stability metrics per key. Primary persona: analyst or chief-of-staff at a regulated SMB. Maturity: **live** for v2 briefing + workbook analysis + Solva PDF + admin telemetry; **partial** for v1 phase-d/phase-e legacy artefacts retained for back-compat.

**Akki** is the orchestrator, auth, billing, and user-facing product surface. It owns 113 of the 134 routers — context membership / multi-tenancy / chat / documents / decks / Pulse feed / studio blocks / sandbox / inbox routing / share links / admin & cohort surfaces / cron schedules / onboarding flows. Primary persona: operator + executive + analyst in a regulated SMB. Maturity: **live** for the operator + analyst surfaces; **partial** for the executive trial flow (C2 Google OAuth gated on user-supplied GCP creds — see §7 external blockers).

**Architectural posture.** All three are bounded contexts behind the same FastAPI process today (single-uvicorn deployment with read-only platform supervisor — see Phase 4.3 sprint memo §1 deviation). Cross-context calls go through 68 typed contract methods (`get_synisense() / get_solva() / get_akki()`) with an HTTP transport substrate already live (`BOUNDED_CONTEXT_TRANSPORT=http` in production). The Phase 4.4 dual-mount publishes every public route a second time under `/v1/{context}/*` so each product can be wrapped in its own SDK and sold standalone the day the platform supervisor unlocks (mechanical config change; no code work).

---

## 2. SyniSense — Data Governance / PII Pipeline

**Bounded context** owned by `synisense_app.py` (12 routers). **Contract surface** — 30 typed methods exposed at `get_synisense().*` (full signal lifecycle + Shield invocation + observability + trust-receipt issuance).

### 2.1 Shield — deidentify / mint / reidentify pipeline
- **Value:** Every outbound LLM call passes through a guardrail that strips PII before egress and re-identifies on return. Auditable, tamper-evident, regex + Presidio + spaCy NER triple-pass.
- **What the user does:** Nothing visible by default — the Shield is server-side. Power users / governance leads view the Shield's work in the Trust Center surface.
- **UI entry point:** Trust Center → "Activity" tab (per-turn drilldown).
- **Backend endpoints:** Shield is invoked transitively by every LLM-producing handler (chat, briefing, deck render, simulate). Exposed contract method: `get_synisense().shield_invoke(...)`. Health/warmup: `GET /api/healthz/shield`.
- **Versioned mirror:** Indirect — Trust Center surfaces under `/v1/synisense/trust-center/*`.
- **Owning collections:** `synisense_audit_log`, `synisense_trust_receipts`, `synisense_shield_warmup_log`.
- **Status:** **Live.** Settled guardrail per Phase 3 spec — leveraged, not redesigned in Phase 4.
- **Known limitations:** Streaming Shield exists at the token level (`backend/services/synisense/shield/streaming.py`) but the Trust Center streaming UI is parked. PII recogniser coverage is configurable per-tenant — a tenant onboarding a new PII class needs an admin to add a recogniser pack.

### 2.2 Trust Center — forensic surface
- **Value:** Sales/legal/compliance-grade audit trail. Per-turn drill-down with input SHA, tokenized prompt, tokenized LLM response, re-identified visible text, redactions list, full audit chain, and a gated plaintext endpoint that writes a `trust_center.plaintext_viewed` row on every read.
- **What the user does:** Open Trust Center → search by chat / session / actor → view per-turn evidence.
- **UI entry point:** `/app/frontend/src/pages/TrustCenter.jsx` (route: `/app/trust-center`).
- **Backend endpoints:** `GET /api/trust-center/activity`, `GET /api/trust-center/reasoning`, `GET /api/trust-center/metrics`, plaintext read endpoints (audited).
- **Versioned mirror:** `/v1/synisense/trust-center/*` (Phase 4.4 dual-mount).
- **Owning collections:** `synisense_audit_log`, `synisense_trust_receipts`.
- **Status:** **Live.**
- **Known limitations:** Historical back-fill of pre-Shield-v1.x chats is one-shot (admin tool, not user-self-serve); see `routers/admin_shield_backfill.py`.

### 2.3 Signals API — typed intelligence events
- **Value:** A unified read/write surface for "things the analyst should look at" — risk, gap, opportunity, dismissed, bookmarked, resolved, deduped — sourced from Shield audit promotions, document ingestion intelligence (`services/documents/intelligence_service.py`), inbox routing (`services/inbox_routing/upstream_adapter.py`), and explicit user actions.
- **What the user does:** Indirect — Akki's Pulse / Monitor / Portfolio / Studio / Sandbox / Walk-in surfaces read this API. Comments, bookmarks, resolutions all write back through it.
- **UI entry points:** Pulse (`/app/pulse`), Monitor (`/app/monitor`), Portfolio (`/app/portfolio`), Studio blocks, Walk-in.
- **Backend endpoints (contract methods, all reachable via `/api/internal/v1/synisense/method/*` when `BOUNDED_CONTEXT_TRANSPORT=http`):** `list_signals`, `list_signals_by_ids`, `list_pulse_feed_signals`, `get_signal`, `get_signal_with_origin`, `count_signals`, `count_goals_at_risk`, `count_unread_signals`, `aggregate_signals_by_type`, `search_signals_by_text`, `insert_signal`, `insert_signals_for_context`, `delete_signals_in_context`, `add_signal_comment`, `delete_signal_comment`, `mark_signal_resolved`, `mark_signal_unresolved`, `bookmark_signal`, `unbookmark_signal`, `dismiss_signal`, `update_signal_dismiss`, `upsert_signal_intelligence`, `unset_signals_committee`, `merge_signal_dedup`, `find_signal_by_external_ref`, `find_signal_by_content_hash` — **24 of the 30 SyniSense contract methods**.
- **Owning collections:** `signals` (registered SyniSense-owned in Phase 4.3 invariant scanner).
- **Status:** **Live.** All 47 Akki call sites migrated to typed methods in Phase 4.3 Part D (0 violations in `4_3_enforce_mode`).
- **Known limitations:** Severity-field coverage is sparse on legacy rows (Phase G migration partially incomplete) — query helpers tolerate both `severity` + `state`/`status` legacy shapes.

### 2.4 SyniSense Observability — reasoning velocity, KPI, dryrun
- **Value:** Internal + public telemetry surfaces showing how Shield is performing under load (reasoning velocity, blocked turn counts, redaction frequencies). A `dryrun` endpoint exposes a no-LLM Shield invocation for partner integration testing.
- **UI entry point:** Admin → SyniSense → Observability tab.
- **Backend endpoints:** `GET /api/synisense/observability/*`, `GET /api/observability/reasoning_velocity`, `GET /api/public/observability/reasoning_velocity`, `POST /api/synisense/dryrun`.
- **Versioned mirror:** `/v1/synisense/observability/*`.
- **Owning collections:** `synisense_audit_log` (derived metrics), `synisense_shield_metrics_snapshots`.
- **Status:** **Live.**

### 2.5 Governance — me/governance
- **Value:** Personal-scope governance surface for the signed-in account: what tenant policies apply, what's currently audited, what reasoning chains are mine.
- **UI entry point:** Profile → Governance.
- **Backend endpoints:** `GET /api/me/governance`, `GET /api/me/governance/audit`.
- **Versioned mirror:** `/v1/synisense/me/governance*`.
- **Status:** **Live.**

### 2.6 Inbox Routing → Signals adapter
- **Value:** Inbound email lands in Akki's inbox queue → routing service deidentifies + creates Signals at the right tenant scope → Pulse surfaces them.
- **Backend services:** `services/inbox_routing/upstream_adapter.py`, `services/inbox_routing/backfill.py` (operational backfill CLI).
- **Status:** **Live** — Phase 4.3 migrated to typed contract methods (`find_signal_by_external_ref`, `insert_signal`).
- **Known limitations:** Cross-account Akki-side dedup is keyed on `(context_id, origin.source, origin.message_id)` — robust for individual mailboxes; a shared mailbox emitting the same Message-Id twice would dedup correctly.

---

## 3. Solva — Reasoning Governance / Multi-Workbook Analyzer

**Bounded context** owned by `solva_app.py` (9 routers, 62 cloned routes in `/v1/solva/*`). **Contract surface** — 6 typed methods exposed at `get_solva().*`.

### 3.1 Solva v2 — briefing run
- **Value:** A user uploads a set of documents + a strategic question; Solva v2 produces a multi-section reasoning brief with citations pinned to source spans.
- **What the user does:** Solva Workbook → "New analysis" → upload docs → ask question → review brief → export.
- **UI entry point:** `/app/solva` (Solva Workbench).
- **Backend endpoints:** `POST /api/solva/v2/seed`, `POST /api/solva/v2/render`, `GET /api/solva/v2/sessions`, `GET /api/solva/v2/sessions/{id}`, `GET /api/solva/v2-poc/status`.
- **Versioned mirror:** `/v1/solva/v2/*`.
- **Owning collections:** `solva_v2_sessions`, `solva_v2_artefacts`.
- **Status:** **Live.**
- **Known limitations:** Concurrency cap is per-tenant (rate-limited in code, not OOM-protected — see Phase 2 hardening backlog).

### 3.2 Solva Workbook Analysis (v2)
- **Value:** Multi-document analyses persisted as workbook entries — synthesize, status-close, recall.
- **Backend endpoints:** `GET /api/workbook/analyses`, `GET /api/workbook/v2/analyses`, `POST /api/workbook/v2/analyses`, `POST /api/workbook/v2/analyses/{aid}/synthesize`, `POST /api/workbook/v2/analyses/{aid}/session-close`.
- **Versioned mirror:** `/v1/solva/workbook/*`.
- **Owning collections:** `solva_workbook_analyses`, `solva_workbook_sessions`.
- **Status:** **Live.**

### 3.3 Solva Briefing State
- **Value:** Stateful briefing rehydration so analysts can resume an interrupted run.
- **Backend endpoints:** `GET /api/solva/briefing/state`, `POST /api/solva/briefing/snapshot`.
- **Versioned mirror:** `/v1/solva/briefing/*`.
- **Status:** **Live.**

### 3.4 Solva Phase-D / Phase-E artefacts (v1 legacy)
- **Value:** Legacy Solva v1 artefacts (admin reports, PDF exports, chat-attached PDF rendering) retained for back-compat.
- **Backend endpoints:** `solva_phase_d.router`, `solva_phase_e_polish.{admin_router, solva_export_router, chat_pdf_router}`.
- **Owning collections:** `solva_v1_artefacts`, `solva_chat_pdfs`.
- **Status:** **Partial.** v1 surfaces remain available because partner integrations from the pre-v2 era depend on them; they are not on the active feature roadmap.

### 3.5 Solva Telemetry Admin
- **Value:** Per-key Solva run telemetry — latency, token spend, citation-stability metric.
- **Backend endpoints:** `GET /api/admin/solva/key-usage`, `GET /api/admin/solva/diag-snapshot`, etc.
- **Versioned mirror:** `/v1/solva/admin/solva/*`.
- **Status:** **Live.**

### 3.6 Solva v2 Artefact (chunked render)
- **Value:** Long Solva runs stream their progress as artefact fragments so the UI can render before the full brief is done.
- **Backend endpoints:** `POST /api/solva/v2/artefacts`, `GET /api/solva/v2/artefacts/{id}/stream`.
- **Versioned mirror:** `/v1/solva/v2/artefacts*`.
- **Status:** **Live.**

---

## 4. Akki — Orchestrator, Auth, Product Logic

**Bounded context** owned by `akki_app.py` (113 routers, 595 cloned routes in `/v1/akki/*`). **Contract surface** — 32 typed methods at `get_akki().*` plus 12 polymorphic surfaces still on the Phase-3 baseline (see §6).

Akki has the broadest functional footprint. Grouped by user surface:

### 4.1 Auth + Identity
- **Features:** Email/password auth (`/api/auth/*`), magic-link login (`auth_magic.router`), password reset (`password_reset.router`), Google OAuth (`oauth_google.router` — **gated on user-supplied GCP creds**), MFA enrolment + verification (`mfa.router`), password change.
- **Status:** **Live** for email/password + magic-link + MFA + password reset.
- **Gated:** Google OAuth — see §7 external blockers.

### 4.2 Contexts + Memberships (multi-tenancy primitive)
- **Features:** A "context" is the multi-tenant scope (an SMB or a department within one). Every Akki resource is context-scoped; membership grants role-bounded access. Endpoints: create context (`POST /api/contexts`), list mine (`GET /api/contexts`), active-context switch (`POST /api/me/active-context`), member invites, role updates, suspend/unsuspend, deletion.
- **Owning collections:** `contexts`, `context_memberships`, `accounts`.
- **Status:** **Live.**

### 4.3 Chat (multi-context conversational surface)
- **Features:** Per-context chat threads (`chat.router`), archived threads (`chat_audit_panel.router`), search (`chat/search`), streaming (`streaming_v9.router`). Every chat turn invokes SyniSense Shield.
- **Backend endpoints:** `GET/POST /api/chats`, `GET /api/chats/archived`, `GET /api/chats/search`, `POST /api/chats/{id}/messages`, `POST /api/streaming/v9/*`.
- **Owning collections:** `chats`, `chat_messages`, `chat_message_audits`.
- **Status:** **Live.**

### 4.4 Pulse (signal feed)
- **Features:** Per-context signal feed read from SyniSense. State transitions (active / resolved / bookmarked / archived), comments, dismiss/email-akki action telemetry, lens filters.
- **Backend endpoints:** `GET /api/pulse/feed`, `POST /api/pulse/{sid}/comment`, `DELETE /api/pulse/{sid}/comment/{cid}`, `POST /api/pulse/{sid}/{resolve,unresolve,bookmark,unbookmark,dismiss}`.
- **Status:** **Live.**

### 4.5 Documents
- **Features:** Upload (ClamAV-gated), extraction queue, intelligence promotion (extracted facts → SyniSense signals via `services/documents/intelligence_service.py`), preview, deletion, lens-filtered listing, briefing trigger.
- **Backend endpoints:** `POST /api/documents/upload`, `GET /api/documents`, `GET /api/documents/{did}/preview`, `POST /api/documents/{did}/briefing`, async mirror at `/api/documents/async/*`.
- **Owning collections:** `documents`, `document_extractions`, `document_engagements`.
- **Status:** **Live.**

### 4.6 Briefings (board-style PDF render)
- **Features:** Render a one-pager briefing from a document or signal cluster. Includes per-tenant LLM cost gating (`llm_quota`).
- **Backend endpoints:** `POST /api/briefings`, `GET /api/briefings/{bid}`, `GET /api/briefings/{bid}/pdf`.
- **Status:** **Live.**

### 4.7 Decks (slide-paginated artefacts)
- **Features:** Generate slide-style decks from context evidence. Stream-render + finished-deck retrieval.
- **Backend endpoints:** `POST /api/contexts/{cid}/decks/generate`, `POST /api/contexts/{cid}/decks/generate/stream`, `GET /api/contexts/{cid}/decks`, `GET /api/contexts/{cid}/decks/{deck_id}/context`.
- **Status:** **Live.**

### 4.8 Studio (Work Studio)
- **Features:** Visual editor for stitching documents + signals + decks + simulations into a multi-block artefact. Phases C / C2 / Overlay / From-Source / Render / Export.
- **Backend endpoints:** `work_studio_*.router` — 6 routers covering compose, overlay, render, export.
- **Status:** **Live.**

### 4.9 Sandbox (intake + seed dataset)
- **Features:** Cohort-onboarding sandbox where a new tenant is seeded with example documents + signals + briefings to explore the product before real data ingest. Lifecycle: generate seed → explore → convert to real context (or discard).
- **Backend endpoints:** `POST /api/sandbox/generate`, `POST /api/sandbox/{sid}/convert`, `POST /api/sandbox/{sid}/discard`, scheduled cleanup cron.
- **Status:** **Live.**

### 4.10 Inbox Routing (inbound email → signals)
- **Features:** Postmark inbound webhook → Akki inbox queue → routing service → SyniSense signal insert. Admin inbox preview + manual reroute.
- **Backend endpoints:** `POST /api/inbound/email`, `GET /api/admin/inbox/messages`, `POST /api/inbox/{mid}/{retry,route,reject}`.
- **Owning collections:** `inbox_messages`, `inbox_routing_log`.
- **Status:** **Live.**

### 4.11 Shares (public link surface)
- **Features:** Per-resource public/auth-walled share links with expiry + revoke. Public preview hides PII via Shield.
- **Backend endpoints:** `POST /api/shares`, `GET /api/shares/{token}`, `DELETE /api/shares/{token}`.
- **Status:** **Live.**

### 4.12 Portfolio / Company Home / Monitor / Daily Review
- **Features:** Per-context dashboards aggregating signals, briefings, decks, documents, goals-at-risk, unread counts. Daily review surfaces "what's new" since last visit.
- **Backend endpoints:** `GET /api/portfolio`, `GET /api/contexts/{cid}/home/*`, `GET /api/monitor`, `GET /api/daily-review`.
- **Status:** **Live.**

### 4.13 Simulate / Walk-in / Lens / Influence Map / Strategic Goals
- **Features:** Analytical surfaces over context evidence — simulate a what-if scenario grounded in signals; walk-in solve a quick decision; lens filtering; influence-map of strategic objectives; strategic-goal lifecycle (assess / evolve / close).
- **Backend endpoints:** `simulate.router`, `walkin.router`, `lens.router`, `influence_map.router`, `strategic_goal_*.router`.
- **Status:** **Live.**

### 4.14 Cycles + Followups + Cycle Manager
- **Features:** Recurring decision-cycle scheduling — assignments, follow-ups, status tracking, NED (non-executive director) cycle subset.
- **Backend endpoints:** `cycle.router`, `cycle_assignments.router`, `cycle_manager.router`, `cycles.router`, `ned_cycle.router`.
- **Status:** **Live.**

### 4.15 Committees + Exco Teams + Team Catalogue
- **Features:** Per-context committee management (boards, exec teams, sub-committees) + team catalogue per role.
- **Backend endpoints:** `committees.router`, `exco_teams.router`, `team_catalogue.router`.
- **Status:** **Live.**

### 4.16 Billing + Trial + Enterprise
- **Features:** Subscription billing (`billing.router` — Stripe TBD), trial status (`trial_status.router`), enterprise tier flag (`enterprise.router`).
- **Status:** **Partial.** Stripe integration is wired but not yet productionised (live Stripe key not deployed; test key available). Trial + enterprise flags live.
- **Known limitations:** No self-serve upgrade flow yet — pricing posture is **placeholder-only** (see §7).

### 4.17 Admin + Cohort + Onboarding
- **Features:** Admin surfaces (audit invariant violations, auth events, cohort applications, email provider config, tenant management, user management, journal, LLM spend, sandbox KPI, QA hooks). Cohort onboarding (waitlist, applications, email events, magic-link consume).
- **Backend endpoints:** `admin_*.router` (15 routers), `cohort_*.router` (4 routers), `onboarding_*.router` (2 routers).
- **Status:** **Live** for admin + cohort. Onboarding flow is the entry path for new SMB tenants.

### 4.18 Content surfaces (Blog + Help + News + Website + Feedback + Early Access)
- **Features:** Marketing content via the same backend (`blog.router`, `help.router`, `news.router`, `website.router`), feedback capture, early-access waitlist.
- **Status:** **Live.**

### 4.19 Observability + Audit + Quota + Health
- **Features:** Reasoning-velocity telemetry (`observability.router`), per-tenant LLM quota (`llm_quota.router`), audit trail (`audit.router`), health-composite probe (`health_composite.router`), ClamAV liveness (`healthz_clamav.router`).
- **Status:** **Live.**

### 4.20 Streaming v9 + Async Jobs + Document Async Mirror + Compilations
- **Features:** SSE/streaming responses for long-running chat + brief renders; an async job queue for backfills + heavy compute; a mirror collection for document jobs.
- **Status:** **Live.**

---

## 5. Cross-Context Integration Surfaces

The three contexts communicate **only** through the typed contract methods. No bounded context reaches into another's collections directly. Phase 4.3 dissolved the last 39 violations of this rule — current violation count is **0** in `4_3_enforce_mode`.

### 5.1 Akki → SyniSense (Pulse / Monitor / Portfolio reading signals)
- **Path:** Akki's `routers/pulse.py`, `monitor.py`, `portfolio.py`, `company_home.py`, etc. call `get_synisense().list_signals(...)` / `count_signals(...)` / `list_pulse_feed_signals(...)`.
- **Transport:** `BOUNDED_CONTEXT_TRANSPORT=http` (Phase 4.3 default). Each call serialises through `/api/internal/v1/synisense/method/<name>` with an HMAC-signed header. Falls back cleanly to in-process when `=inproc`.
- **DTO contract:** `Signal` dataclass — `signal_id`, `account_id`, `context_id`, `raw: dict` for the full payload.

### 5.2 Akki → SyniSense (Shield invocation)
- **Path:** Every chat / briefing / deck / simulate handler invokes `get_synisense().shield_invoke(...)` before producing LLM-bound text.
- **DTO contract:** `ShieldResult` — `audit_id`, `tokenized_input`, `tokenized_output`, `reidentified_output`, `redactions[]`.

### 5.3 Akki → Solva (briefing rehydration, render)
- **Path:** Akki's briefings router orchestrates Solva v2 runs via `get_solva().run_brief(...)`. The Solva session id is persisted in Akki's `briefings` collection.
- **DTO contract:** `SolvaSession` — `session_id`, `status`, `artefact_ids[]`.

### 5.4 Solva → SyniSense (governance + Shield receipts)
- **Path:** Every Solva render's component LLM calls go through Shield. Trust Center surfaces the resulting audit trail.

### 5.5 SyniSense → Akki (document materialization)
- **Path:** `services/documents/intelligence_service.py` promotes extracted facts into SyniSense signals via `get_synisense().upsert_signal_intelligence(...)`.

### 5.6 Contract method totals (Phase 4.3 close)
- **Akki:** 32 typed methods. Most frequently used: `get_tenant_profile`, `list_documents`, `record_audit`, `get_briefing_quota`.
- **SyniSense:** 30 typed methods (24 added in Phase 4.3 for full Signals API + Shield read/write).
- **Solva:** 6 typed methods.
- **Total surface:** **68 typed contract methods**.

### 5.7 HTTP transport
The `/api/internal/v1/{context}/method/<name>` endpoints are **excluded from public OpenAPI**. They are not part of the commercial `/v1/{context}/*` surface — they're internal-only and authenticated with `INTERNAL_TRANSPORT_SECRET`. Partner SDKs consume the public `/v1/{context}/*` surface only.

---

## 6. Maturity & Debt Snapshot

### Live / Partial / Parked / Gated counts

| Product | Live | Partial | Parked | Gated |
|---|---:|---:|---:|---:|
| SyniSense | 6 | 1 (streaming Shield UI) | 0 | 0 |
| Solva | 5 | 1 (v1 phase-d/e legacy) | 0 | 0 |
| Akki | 19 | 1 (Stripe productionisation) | 0 | 1 (Google OAuth) |

### Pre-existing debt (carry-forward, all user-acknowledged)

1. **15 Track-A E2E test flake** — sandbox-upload CSRF flow + integration suites. Failing on baseline (not net-new since Phase 4). Impact: CI noise, no product impact.
2. **314 FE raw-axios call sites** — Phase 3 carry-forward. FE calls `axios.X()` directly rather than the typed `api.X()` wrapper. Functional today; refactor candidate for Phase 6 polish. Impact: no behaviour change, but bypasses the typed FE contract surface.
3. **55 polymorphic BE routes** still on `Dict[str, Any]` baseline. Phase 3 carry-forward. These are genuinely polymorphic by product design (e.g. studio block payloads, simulation parameters); not all 55 will ever be typed. Impact: OpenAPI shows `additionalProperties: true` on these — acceptable for an internal SDK consumer, less ideal for an external one.

### Surface-level invariants (asserted on every test run)
- `/api/*` slice `paths_sha256[:16] = cdcb23322bb82895` — held since Phase 4.1.
- `/v1/*` slice `paths_sha256[:16] = acc51822aa8818ae` — Phase 4.4 baseline.
- Combined `paths_sha256[:16] = ca9429c64e44570c` — Phase 4.4 baseline.
- Cross-context invariant: **0** violations / **0** annotations in `4_3_enforce_mode`.

---

## 7. Commercial Posture

### Standalone product readiness

| Product | Sellable standalone today? | Conditions |
|---|---|---|
| **SyniSense** | ⚠️ **Conditional** — see below | Needs a productionised standalone SDK (in flight at Phase 5 Part E) + supervisor unlock so SyniSense can run on its own pod (Phase 5 external blocker). Until then, sellable as a bundled component of Akki. |
| **Solva** | ⚠️ **Conditional** — same conditions as SyniSense. | Solva v2 is feature-complete for standalone use; the surface is exposed at `/v1/solva/*` and ready for an SDK consumer. Multi-tenancy + auth currently piggy-backs Akki's identity layer. A truly standalone Solva would need its own auth surface or an integration where Akki acts as identity broker only. |
| **Akki** | ✅ **Yes** — Akki is the complete product as it stands today. | The orchestrator + user surfaces ARE the sold product. SyniSense + Solva ride along as guardrails / capabilities of Akki. |

### Bundle paths

| Bundle | Composition | Posture |
|---|---|---|
| Akki Solo | Akki only, with SyniSense Shield as transparent guardrail (no Trust Center surface, no Signals API to partner) | Smallest, simplest — operator + analyst SMB. |
| Akki + SyniSense | Akki + full Trust Center + Signals API + observability surfaces | Adds the governance product as a sellable line item. Target persona: regulated SMB with a compliance officer. |
| Akki + Solva | Akki + Solva Workbench + multi-document analyses | Adds the reasoning product as a sellable line item. Target persona: SMB with a chief-of-staff or analyst function. |
| **Full Triad** | Akki + SyniSense (Trust Center exposed) + Solva (Workbench exposed) | Current full-product offering. |

### Per-product SLA dimensions worth pricing on (PLACEHOLDERS — no dollar figures committed)
| Product | SLA dimension | Notes |
|---|---|---|
| SyniSense | Shield round-trip latency (p50 / p95), trust-receipt availability, audit-log retention window | Receipt availability is durability-critical |
| Solva | Briefing render turnaround (p50 / p95), citation-stability score over reruns, max concurrent analyses per tenant | Render turnaround is the most-asked-about |
| Akki | Pulse signal freshness lag, document extraction p95, chat turn latency p50, uptime | Standard SaaS SLA dimensions |

### Sale separability checklist
Before a single context can be sold to a customer without dragging the other two:

| Check | Status |
|---|---|
| Context is an independently runnable FastAPI app | ✅ Verified (Phase 4.1) — `python -c "from synisense_app import app"` etc. |
| Cross-context calls go through typed contracts only | ✅ Verified (Phase 4.3) — 0 violations in `4_3_enforce_mode` |
| HTTP transport substrate works between processes | ✅ Verified (Phase 4.2) — 8/8 smoke tests pass under `BOUNDED_CONTEXT_TRANSPORT=http` |
| Healthcheck triad live + composite proxy | ✅ Verified (Phase 4.3) |
| Versioned `/v1/{context}/*` SDK surface published | ✅ Verified (Phase 4.4) — 619 paths, sha `acc51822aa8818ae` |
| Per-context Dockerfile + compose + K8s manifests | ✅ Delivered (Phase 5 Part C) at `/app/backend/deploy/` |
| Per-context OpenAPI SDK slice | ✅ Delivered (Phase 5 Part B) at `/app/backend/openapi-sdk/` |
| TypeScript SDK build pipeline | ✅ Delivered (Phase 5 Part E) at `/app/sdk/` |
| Cron supervisor split | ✅ Delivered (Phase 5 Part D) — each `<ctx>_app.py` owns its own lifespan crons |
| Partner onboarding doc | ✅ Delivered (Phase 5 Part E) — `/app/memory/PARTNER_ONBOARDING.md` |
| Commercial posture doc | ✅ Delivered (Phase 5 Part F) — `/app/memory/COMMERCIAL_POSTURE.md` |
| Platform supervisor unlock (multi-process activation) | ❌ **External blocker** — `/etc/supervisor/conf.d/supervisord.conf` is READONLY in the bundled environment. Unlock activates standalone deployment. |
| Live Stripe productionisation | ❌ **Gated** — test key in pod env; live key + paying customer trigger the productionisation |
| Per-product brand / signed terms / DPA | ❌ **Out of scope** for engineering — sales/legal pre-requisite |

### External blockers (not engineering-resolvable)
1. **Supervisor unlock.** `/etc/supervisor/conf.d/supervisord.conf` is platform-`READONLY`. All multi-process artefacts (Dockerfiles, compose, K8s manifests) are buildable + lintable; activation requires a deploy lane where supervisor is writable.
2. **Google GCP OAuth creds.** C2 Google sign-in is awaiting user-supplied client ID + secret. Recurring blocker tracked in MASTER_STATE.
3. **Live Stripe key.** Productionisation gated on first paying customer.

### SDK surface
- **Public consumer surface:** `/v1/{context}/*` only (Phase 4.4).
- **Versioning policy:** see `/app/memory/API_VERSIONING.md` — `/api/*` is legacy-stable forever; `/v1/*` is the stable versioned SDK surface; major version bumps are per-context.
- **SDK slice files:** `/app/backend/openapi-sdk/{synisense,solva,akki}.openapi.json` (regeneratable via `scripts/generate_sdk_slices.py`).
- **TypeScript SDK:** `/app/sdk/{synisense,solva,akki}/` (built via `scripts/build_sdk.py`).

---

**End of Product Features Review.**

*Maintenance note: this document is regenerated at the end of every Phase that touches the public feature surface. Source-of-truth basis is the live OpenAPI document + the Phase 4.1 router-to-app classification + the contract method count in `tests/invariants/test_invariant_contract_snapshots.py`.*
