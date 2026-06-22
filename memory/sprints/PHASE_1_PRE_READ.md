# Phase 1 Pre-Read — Contracts, Ownership, Tenant Propagation

**Mode:** READ-ONLY investigation (per Discipline Rail R1).
**Date:** 2026-06-05.
**Scope:** Establish ground-truth for the 5 dispatch questions before any Phase 1 code dispatch.

**Headline:** **CLEAN_WITH_NOTES.** No code-level blockers found. Three confirmed discrepancies with the approved plan's assumptions are surfaced in §5 / §6 — all three are PLANNABLE (no behaviour change required to address); Phase 1 build can dispatch contingent on user acknowledgement of the discrepancies and the recommended scope in §7.

---

## 1 · Collection ownership split (Q1)

**Harvest method:** AST-scanned every `.py` under `backend/services/` + `backend/routers/` for `db.<collection>.<method>(...)` shapes (165 distinct collection symbols). Categorised by reader/writer module location. Excluded noise tokens (`db.list_collection_names`, `db.command`, `db._migrations`, `db.update`, `db.chunk`, `db.solva_v` truncations).

**Symbol counts (live code):**
- Total real Mongo collections touched: **156** (after noise removal).
- Touched by `services/synisense/*`: 17.
- Touched by `services/solva_v2/*`: 4 (most Solva DB access lives in `routers/solva_v2.py`, not the service package).
- Touched by `services/ideas_engine/*`: 0 (also router-bound).

### 1.A · Inverted-dependency hotspots (touched by NOT-owning package)

The Phase 0 dispatch tentative split assumed clean package boundaries. The live code shows these inverted dependencies — they are the load-bearing problem Phase 1 must solve:

| Collection (Akki-owned) | Read by SyniSense package | File:line |
|---|---|---|
| `accounts` | tenant_entities harvester | `services/synisense/shield/tenant_entities.py:92` |
| `contexts` | tenant_entities harvester | `services/synisense/shield/tenant_entities.py:107` |
| `cycles` | tenant_entities harvester | `services/synisense/shield/tenant_entities.py:127` |
| `chat_messages` | engine / scheduler | `services/synisense/engine/` |
| `chats` | engine / scheduler | `services/synisense/engine/` |
| `briefings` | engine | `services/synisense/engine/` |
| `documents` | engine | `services/synisense/engine/` |
| `objectives` | engine | `services/synisense/engine/` |
| `cycle_questions` | engine | `services/synisense/engine/` |
| `memberships` | engine | `services/synisense/engine/` |

| Collection (Akki-owned) | Read by Solva v2 package | File:line |
|---|---|---|
| `accounts` | Solva v2 service | `services/solva_v2/*` |
| `chats` | Solva v2 service | `services/solva_v2/*` |
| `chat_messages` | Solva v2 service | `services/solva_v2/*` |
| `contexts` | Solva v2 service | `services/solva_v2/*` |
| `cycles`, `cycle_configs`, `cycle_contributions`, `cycle_questions` | Solva v2 service | `services/solva_v2/*` |
| `documents`, `signals` | Solva v2 service | `services/solva_v2/*` |
| `memberships`, `questions` | Solva v2 service | `services/solva_v2/*` |
| `ned_meetings`, `work_studio_artefacts`, `work_studio_briefs` | Solva v2 service | `services/solva_v2/*` |
| `synisense_audit_log`, `synisense_runs`, `synisense_trust_receipts` | Solva v2 reads SyniSense audit | `services/solva_v2/*` |

**Implication:** the SyniSense and Solva packages today are NOT cleanly bounded — both reach directly into Akki's collections (and into each other). Phase 1's contract layer must mediate every one of these access points.

### 1.B · Full collection ownership table

| Collection | Owner | Read by | Written by | Tenant-scoped? | Justification |
|---|---|---|---|---|---|
| `_migrations` | Cross-context | server.py | server.py | no | Schema migration tracking; system-wide. |
| `accounts` | Akki (identity) | Akki, SyniSense (harvester), Solva v2 (cross-read) | Akki | self (row IS tenant) | The row IS the tenant. Phase 1 must hide direct reads behind `AkkiContract.get_tenant_profile()`. |
| `admin_cleanup_audit` | Cross-context (admin) | Akki admin | Akki admin | no | Superadmin observability. |
| `admin_inbox_messages` | Akki | Akki | Akki | yes | Inbox routing. |
| `agendas` | Akki | Akki | Akki | yes | Cycle agenda surface. |
| `analyses` | Solva | Akki (workbook router), Solva v2 | Akki (workbook router), Solva v2 | yes | Workbook analysis entity (Phase 4 multi-blob). Reader/writer are routers/workbook_analysis.py + Solva narration. |
| `analysis_blobs` | Solva | workbook router, Solva v2 | workbook router | yes | Workbook source blob storage (deleted on session close per D4). |
| `ask_messages` | Akki | Akki | Akki | yes | Ad-hoc question surface. |
| `async_jobs` | Akki | Akki | Akki | yes | Async job orchestration (Generate Brief, etc.). |
| `audit_invariant_violations` | SyniSense | Akki (chat sync handler), SyniSense | Akki, SyniSense | yes (tenant tagged) | Shield invariant violations recorded for forensics. |
| `audit_log` | Akki | Akki, Solva | Akki | yes | Generic audit log; both packages append. Should be `AkkiContract.audit_event(...)`. |
| `auth_events` | Akki (identity) | Akki | Akki | yes | Auth event tracking. |
| `backfill_jobs` / `backfill_log` | Akki (admin) | Akki | Akki | no | Admin migration tooling. |
| `billing_launch_interest` | Akki (marketing) | Akki | Akki | no | Pre-billing lead capture; not tenant-scoped. |
| `blog_posts` / `blog_subscribers` | Akki (marketing) | Akki | Akki | no | Public-side marketing. |
| `boardpacks` | Akki | Akki | Akki | yes | Board pack rows. |
| `briefing_reads` | Akki | Akki | Akki | yes | Briefing engagement. |
| `briefings` | Akki | Akki, SyniSense (engine), Solva v2 (read) | Akki | yes | Pre-meeting briefings; read by both SyniSense (entity harvest signal) and Solva (citation source). Cross-context reader → contract method. |
| `briefs` | Akki | Akki | Akki | yes | Cycle-bound brief artefacts. |
| `chat_audit_log` | Akki | Akki, SyniSense | Akki | yes | Per-message chat audit (separate from synisense_audit_log). |
| `chat_messages` | Akki | Akki, SyniSense (engine), Solva v2 | Akki | yes | Chat message rows. SyniSense + Solva read for grounding/signals. |
| `chats` | Akki | Akki, SyniSense (engine), Solva v2 | Akki | yes | Chat sessions. Crossed by both. |
| `checklists` | Akki | Akki | Akki | yes | UI checklist state. |
| `cohort_*` (8 collections) | Akki (cohort) | Akki | Akki | yes (per-applicant) | Cohort apply / waitlist / invites / magic links / audit / copy overrides / email events / special asks. |
| `cohorts` | Akki (admin) | Akki | Akki | no | Cohort definitions (system-wide). |
| `collab_comments` | Akki | Akki | Akki | yes | Collaborative comments. |
| `comments` | Akki | Akki | Akki | yes | Generic comments. |
| `committees` | Akki | Akki | Akki | yes | Committees CRUD. |
| `compilations` | Akki | Akki, Solva (read) | Akki | yes | Work Studio compile job rows. |
| `consent_decisions` | Akki | Akki | Akki | yes | GDPR-ish consent log. |
| `context_members` | Akki | Akki | Akki | yes | Per-context membership rows. |
| `context_memberships` | Akki | Akki | Akki | yes | Alternate membership table (legacy). |
| `context_metadata_signatures` | Akki | Akki | Akki | yes | E.0.2 cross-board metadata sig. |
| `context_objects` | Akki | Akki | Akki | yes | Generic context-bound objects. |
| `contexts` | Akki | Akki, SyniSense (harvester), Solva v2 (read) | Akki | yes (id IS context scope) | Workspace scope. Reads by both other packages need `AkkiContract.list_contexts(account_id)`. |
| `cycle_*` (10 collections) | Akki | Akki, SyniSense (engine), Solva v2 | Akki | yes | Cycle Manager. SyniSense reads cycle_questions for entity harvest; Solva reads many for synthesis. |
| `cycles` | Akki | Akki, SyniSense (harvester), Solva v2 | Akki | yes | Cycle root rows. |
| `decks`, `deck_outlines`, `deck_telemetry` | Akki | Akki | Akki | yes | Slide-deck composer. |
| `default_inbox_contexts` | Akki | Akki | Akki | yes | Default inbox per user. |
| `document_*` (5 collections) | Akki | Akki, SyniSense (engine), Solva v2 | Akki | yes | Documents library + engagement + shares + views + attachments + intelligence. |
| `documents` | Akki | Akki, SyniSense (engine), Solva v2 (citations) | Akki | yes | Universal document rows. |
| `early_access_*` (3 collections) | Akki (marketing) | Akki | Akki | no | Pre-signup capture. |
| `enterprise_interest` | Akki (marketing) | Akki | Akki | no | Pre-signup capture. |
| `events`, `event_invitations` | Akki | Akki | Akki | yes | Calendar. |
| `exco_teams` | Akki | Akki | Akki | yes | Exco team CRUD. |
| `extraction_failures`, `extractions_log` | Akki | Akki | Akki | yes | Doc extraction observability. |
| `feature_events` | Akki | Akki | Akki | no | Telemetry. |
| `feedback` | Akki | Akki | Akki | yes | Feedback widget. |
| `highlights` | Akki | Akki | Akki | yes | Doc highlights. |
| `ideas_audit_log`, `ideas_digests` | Akki | Akki, ideas_engine | Akki, ideas_engine | yes | Pulse Ideas. |
| `inbound_queue`, `inbound_queue_raw` | Akki | Akki | Akki | yes | TM3 SendGrid inbound parse. |
| `inbox_routing_*` (4 collections) | Akki | Akki | Akki | yes | Routing tables. |
| `influence_maps` | Akki | Akki | Akki | yes | Influence map. |
| `invitations` | Akki | Akki | Akki | yes | User invites. |
| `lens_*` (2 collections) | Akki | Akki | Akki | yes | Lens Room coaching. |
| `llm_*` (3 collections — deep_usage, retry_log, validator_usage) | SyniSense | SyniSense, Solva | SyniSense, Solva | yes | LLM usage telemetry; routes through Shield. |
| `login_attempts` | Akki (identity) | Akki | Akki | yes (per email) | Brute-force protection. |
| `mentions` | Akki | Akki | Akki | yes | @-mention notifications. |
| `members` | Akki | Akki | Akki | yes | Per-account team members. |
| `memberships` | Akki | Akki, SyniSense (engine), Solva v2 | Akki | yes (link table) | (account_id, context_id) link table; both filter directions legitimate. |
| `model_fallback_log` | SyniSense | SyniSense | SyniSense | yes | LLM provider fallback observability. |
| `ned_*` (5 collections) | Akki | Akki, Solva (ned_meetings read) | Akki | yes | NED Cycle Manager. |
| `news_items` | Akki (news aggregator) | Akki | Akki cron | no | Public news feed; system-wide. |
| `oauth_pkce_verifiers` | Akki (identity) | Akki | Akki | no (short-lived) | OAuth PKCE state. |
| `objectives` | Akki | Akki, SyniSense (engine), Solva v2 | Akki | yes | Cycle objectives. |
| `organisations` | Akki (admin) | Akki | Akki | yes | Tenant org metadata. |
| `payment_transactions` | Akki (billing) | Akki | Akki | yes | Stripe-gated. |
| `plays` | Akki | Akki | Akki | yes | Strategic plays. |
| `projects` | Akki | Akki | Akki | yes | Project rows. |
| `questions` | Akki | Akki, Solva v2 | Akki | yes | Q4Y questions. |
| `quick_action_usage` | Akki | Akki | Akki | yes | Quick action telemetry. |
| `reportees`, `reports` | Akki | Akki | Akki | yes | Generic reports. |
| `revoked_jtis` | Akki (identity) | Akki | Akki | yes | Revoked JWT IDs. |
| `sandbox_*` (3 collections) | Akki | Akki | Akki | yes | Sandbox sessions + pickups. |
| `scheduler_runs` | Cross-context (cron) | SyniSense, Akki | SyniSense | no | Mongo-locked scheduler audit; system-wide. |
| `shares` | Akki | Akki | Akki | yes | Generic shares. |
| `signal_actions`, `signal_events`, `signals` | Akki | Akki, Solva v2 | Akki | yes | Signal pipeline. Solva reads for synthesis. |
| `simulations` | Akki | Akki | Akki | yes | Simulations. |
| `solva_*` (12 collections) | Solva | Solva, Akki (router glue) | Solva | yes | Solva entity tables (sessions, clusters, handoffs, key_emissions, briefing_state, phase_d_sessions, variant_seen, comparables, etc.). |
| `solve_*` (3 collections) | Solva (legacy alias) | Solva legacy | Solva legacy | yes | Legacy Solva v1; archived per M.4 2026-05-26 but rows linger. |
| `source_view_log` | Akki | Akki | Akki | yes | View tracking. |
| `strategic_goals` | Akki | Akki, Solva v2 | Akki | yes | Strategic goal CRUD. |
| `stripe_*` (2 collections) | Akki (billing) | Akki | Akki | no | Stripe webhook state. |
| `studio_*` (4 collections — blocks, images, shares, views) | Akki | Akki | Akki | yes | Studio Composer. |
| `submissions` | Akki | Akki | Akki | yes | Submitted artefacts. |
| `synisense_audit_log` | SyniSense | SyniSense, Solva (cross-read) | SyniSense | yes | Shield audit (append-only). |
| `synisense_runs` | SyniSense | SyniSense, Solva (cross-read) | SyniSense | yes | Per-message Shield run details. |
| `synisense_shield_maps` | SyniSense | SyniSense | SyniSense | yes | At-rest token-map encryption. |
| `synisense_trust_receipts` | SyniSense | SyniSense, Solva (cross-read) | SyniSense | yes | HMAC trust receipt mirror. |
| `task_*` (4 collections — circulation_tokens, contributor_tokens, inbound_emails, intelligence) | Akki | Akki | Akki | yes | Task subordinate tables. |
| `tasks`, `tasks_initiatives` | Akki | Akki | Akki | yes | Task Manager + initiatives. |
| `team_catalogue` | Akki | Akki | Akki | yes | Team catalogue. |
| `telemetry_events` | Cross-context (telemetry) | Akki | Akki | no | System-wide telemetry. |
| `user_calendar_credentials` | Akki | Akki | Akki | yes | Per-user calendar creds. |
| `user_context_visits` | Akki | Akki | Akki | yes | Last-visit tracking. |
| `user_ideas_preferences` | Akki | Akki, ideas_engine | Akki | yes | Ideas personalisation. |
| `user_recent_views` | Akki | Akki | Akki | yes | Recent-view rows. |
| `work_studio_*` (6 collections) | Akki | Akki, Solva (read for artefact composition) | Akki | yes | Work Studio entity tables. |
| `workbook_analyses`, `workbook_blobs` | Solva (legacy) | Akki (workbook router) | Akki | yes | Legacy workbook entity (pre-Phase-4 Analyze entity). |

### 1.C · Counts by owner

| Owner | Count | Notes |
|---|---|---|
| **Akki** (orchestration + UX) | **115** | The bulk. Includes identity, marketing, UX surfaces. |
| **SyniSense** (governance) | **9** | synisense_audit_log, synisense_runs, synisense_trust_receipts, synisense_shield_maps, audit_invariant_violations, model_fallback_log, llm_deep_usage, llm_retry_log, llm_validator_usage. |
| **Solva** (reasoning) | **19** | analyses, analysis_blobs, solva_* (12), solve_* (3 legacy), workbook_analyses, workbook_blobs. |
| **Cross-context (shared)** | **13** | _migrations, accounts (special — row IS tenant), audit_log, admin_cleanup_audit, scheduler_runs, telemetry_events, login_attempts, oauth_pkce_verifiers, revoked_jtis, news_items, blog_*, billing_launch_interest, enterprise_interest, early_access_*, cohorts (def). |

**Total real collections enumerated: 156.**

### 1.D · "Shared" collections that need contract mediation

Tier 1 — touched by ≥2 owning packages (Phase 1 MUST mediate):

- **accounts** ← read by SyniSense (harvester) + Solva v2 + Akki. → `AkkiContract.get_tenant_profile(account_id)`.
- **contexts** ← read by SyniSense (harvester) + Solva v2 + Akki. → `AkkiContract.list_contexts(account_id)`.
- **cycles** ← read by SyniSense (harvester) + Solva v2 + Akki. → `AkkiContract.list_cycles(account_id, context_id?)`.
- **chats / chat_messages** ← read by Solva v2 + SyniSense (engine) + Akki. → `AkkiContract.get_chat_history(account_id, chat_id)`.
- **briefings, documents, signals, objectives, cycle_questions, memberships** ← read by Solva v2 + Akki. → `AkkiContract.*` per kind.
- **synisense_audit_log, synisense_runs, synisense_trust_receipts** ← read by Solva v2 (cross-read for narration) + SyniSense. → `SyniSenseContract.get_audit_events(account_id, since, until)`.

Tier 2 — system-wide unowned (these get the Phase 2 `@cross_tenant` marker, no contract):

- _migrations, scheduler_runs, news_items, blog_*, early_access_*, billing_launch_interest, enterprise_interest, cohorts (def), audit_log (kept open for both), telemetry_events.

---

## 2 · Tenant propagation design (Q2)

### 2.A · `account_id` availability at every cross-context call site

All identified cross-context call sites trace back to a router handler whose `Depends(get_current_account)` already injects an `account_id` (via `current["id"]`). Spot checks:

| Call site | Has `account_id` today? | Source |
|---|---|---|
| `services/synisense/shield/tenant_entities.py:_load_tenant` | ✅ yes | function arg `tenant_id` (== account_id) |
| `services/solva_v2/analyze_narration.py:695` (`shield_invoke`) | ✅ yes | `tenant_id` arg explicit |
| `services/synisense/engine/scheduler_lock.py` | ✅ yes | per-tenant iteration in scheduler |
| `routers/chat.py` 8 shield_invoke sites | ✅ yes | `current["id"]` from `Depends(get_current_account)` |
| `routers/work_studio_overlay.py` 2 shield_invoke sites | ✅ yes | `current["id"]` |
| `routers/work_studio_export.py:1370` (`_syn_shield`) | ✅ yes | `current["id"]` |
| `routers/documents.py` (intelligence + signals) | ✅ yes | `current["id"]` |
| `routers/tasks.py:580` (compile) | ✅ yes | `current["id"]` |

**Verdict:** `account_id` is ALREADY available at every identified cross-context call site. No new plumbing is needed to make it a first-class contract parameter — the variable just needs to flow into the contract method signature.

### 2.B · Recommended propagation pattern

**Recommendation: explicit kwarg.**

```python
result = await synisense.shield_invoke(
    content=...,
    purpose=...,
    account_id=current["id"],       # required keyword
    consumer_id="chat",
    ...
)
```

**Justification:**

1. **Matches the existing dominant pattern.** Every `shield_invoke()` site already passes `tenant_id=...` as an explicit kwarg. We're not introducing a new pattern; we're consolidating the existing one.
2. **Zero behaviour change.** A `TenantContext` dataclass OR a FastAPI dependency would add new abstractions; the existing pattern already works.
3. **Lints cleanly.** Phase 0's tenancy invariant scans Dict literals for `account_id`. A required kwarg lands cleanly in the same pattern; no AST scanner rework needed.
4. **Easy enforcement in Phase 2.** A `mypy --strict` pass on the contract modules + a runtime fail-fast assertion (`raise ValueError("account_id required")`) gives layered defence.
5. **Trivially extends.** Phase 1+ can add `tenant_context: TenantContext` as a SUPERSET of `account_id` later if scope expands; the kwarg pattern is forward-compatible.

**Decisively NOT recommended: a context-var or thread-local.** Async code paths break this pattern silently and the resulting bugs are nightmarish to trace.

### 2.C · Intentionally cross-tenant collections

These collections are GENUINELY unscoped and Phase 2's guard must learn to exempt them. Listed with one-line justification:

| Collection | Why unscoped |
|---|---|
| `_migrations` | Mongo schema version registry. System-wide. |
| `scheduler_runs` | Cron run audit; one row per Mongo-locked tick. |
| `news_items` | Public news feed; same rows visible to every tenant. |
| `blog_posts`, `blog_subscribers` | Public marketing content. |
| `early_access_*`, `enterprise_interest`, `billing_launch_interest` | Pre-signup lead capture; visitor has no account_id. |
| `cohorts` | Cohort definitions (system-wide). Individual `cohort_invites` rows ARE per-account. |
| `oauth_pkce_verifiers` | Short-lived PKCE state during OAuth handshake; visitor not yet authenticated. |
| `telemetry_events` | System-wide telemetry. |
| `health_check` | Health probe smoke. |
| `revoked_jtis` | Revoked JWT IDs — looked up by JTI, not account. (Could become tenant-scoped in Phase 2 for defence-in-depth; recommend leaving as-is.) |
| `login_attempts` | Brute-force tracking; keyed on email (not account_id which may not exist yet). |
| `admin_*` (cleanup audit, qa hooks data) | Superadmin observability. |

Phase 2's `@cross_tenant` decorator (or comment marker — TBD) gets these.

### 2.D · Non-literal violations from Phase 0 (sample 10 → 8 categorised)

I sampled 10 of the 135 non-literal violations. Findings:

| Sample | File:line | Category |
|---|---|---|
| 1 | `routers/admin_qa_hooks.py:194` (`contexts.insert_one(dict(ctx))`) | (ii) dict variable that DOES include account_id, constructed lines above. **False positive.** |
| 2 | `routers/admin_qa_hooks.py:223` (`documents.insert_one(dict(doc))`) | (ii) Same shape. **False positive.** |
| 3 | `routers/admin_qa_hooks.py:318` (`cycle_questions.insert_one(dict(row))`) | (ii) Same shape. **False positive.** |
| 4 | `routers/admin_tenants.py:106` (`contexts.count_documents(match)`) | (i) **Genuinely cross-tenant** — admin tenant inventory; `match` filters by `type`, not account_id. Needs `@cross_tenant` marker. |
| 5 | `routers/admin_tenants.py:108` (`contexts.find(match, ...)`) | (i) Same. **Genuinely cross-tenant.** |
| 6 | `routers/briefings.py:76` (`signals.count_documents(q)`) | (ii) `q` includes `account_id` and `context_id`, constructed above. **False positive.** |
| 7 | `routers/briefings.py:130` (`signals.find(q, ...)`) | (ii) Same shape. **False positive.** |
| 8 | `routers/chat.py:720` (`chats.insert_one(rec)`) | (ii) `rec` has `account_id` set above. **False positive.** |
| 9 | `routers/chat.py:946` (`documents.insert_one(doc)`) | (ii) `doc` has `account_id`. **False positive.** |
| 10 | `routers/chat.py:1168` (`chats.find_one(chat_filter, ...)`) | (ii) `chat_filter` was built with `account_id` two lines above. **False positive.** |

**Categorisation of the sample:**
- (i) **Genuinely cross-tenant:** 2 / 10 (20%). The `admin_tenants.py` pair. Phase 2 marks these.
- (ii) **Dynamic filter that DOES include `account_id`:** 8 / 10 (80%). These are FALSE POSITIVES of the AST scanner — the variable filter does contain `account_id` but Phase 0's scanner is intentionally conservative on non-literal first-args.
- (iii) **Actual bugs:** 0 / 10 (0%).

**Implication for Phase 2:** the enforce-mode counter should be against `definite_violation_count` (682), NOT `violation_count` (827). The Phase 0 scanner already separates these. Phase 2 fix scope ≈ 682 (most resolvable by adding an `account_id` key) + ~10-20 admin paths that need explicit `@cross_tenant` markers.

---

## 3 · Chatty flow identification (Q3)

### 3.A · Per-request shield_invoke fan-out (top 5 user-facing routes)

| Route | shield_invoke calls per request | Trace |
|---|---|---|
| **Chat send** (`POST /api/chats/{cid}/messages`) | **2 (typical) / up to 4 (deep mode)** | (1) `mint_chat_outcome()` runs deidentify on the user turn for the envelope at `routers/chat.py:1738-1743`. (2) Main `shield_invoke()` at `routers/chat.py:1933` with the full prompt. Deep-mode Phase D path adds 2 more at `routers/chat.py:3055 + 3079`. |
| **Solva analyze synthesize** (`POST /api/workbook/v2/analyses/{aid}/synthesize`) | **1** | Single `shield_invoke()` at `services/solva_v2/analyze_narration.py:695` for the headline-first narration. |
| **Work Studio compile** (`POST /api/contexts/{cid}/work-studio/export/{kind}`) | **1 per stage × 2-3 stages = 2-3** | The Phase 5 lifecycle runs a two-pass shape: `_run_two_pass_for_export()` at `routers/work_studio_export.py:388` calls Shield once for the draft + once for the polish + (optional) once for confidence scoring at `services/work_studio/confidence_scorer.py:200`. |
| **Generate Brief** (`POST /api/contexts/{cid}/documents/{doc_id}/briefings/generate`) | **2-3** | (1) Intelligence extract (signals + intelligence_report) at `services/documents/intelligence_service.py` — 1-2 Shield calls. (2) Brief composition at the compile path — 1 call. |
| **Pulse Ideas refresh** (`POST /api/ideas/refresh-now` or scheduler) | **1** | Single synthesizer call inside `services/ideas_engine/synthesizer.py` (routed through the scheduler at `services/ideas_engine/scheduler.py:133` — `shield_invoke_id` referenced post-call). |

### 3.B · Sequential-N-call patterns

I traced for any "for each X in [list], call SyniSense" loops in the production hot paths. Findings:

| Location | Loop shape | Count today | Phase 1 batching candidate? |
|---|---|---|---|
| `routers/chat.py:2473-2498` (streaming follow-ups) | Two consecutive shield_invoke calls (P1 + P2) inside a single function — not a loop, just two stages | 2 | **No — sequential by design** (stage 1 output feeds stage 2 input). |
| `services/synisense/shield/tenant_entities.py:107-127` | `db.contexts.find(...)` cursor, then for each ctx → `db.cycles.find(...)`. Nested LOOP over Mongo cursors but **no Shield calls inside** — pure DB reads. | N×M DB reads, 0 Shield | **No — DB reads only.** Phase 1 should still expose this as `AkkiContract.list_tenant_entities(account_id)` to hide the nested-loop from SyniSense. |
| `routers/cycle_assignments.py` | Per-cycle iteration for assignment list | N | No — DB reads only. |
| `services/synisense/engine/signal_derivation.py` | Per-tenant tick (hourly cron) | Tenant-count many | Already batched via per-tenant tick; no Phase 1 work needed. |
| `services/ideas_engine/synthesizer.py` | Per-tenant synthesis | Tenant-count many | Same — scheduler-driven, not request-driven. |

**Conclusion:** **NO chatty-N-shield patterns exist in the codebase today.** The architecture is already 1-2 Shield calls per user request. Phase 1 does NOT need a `shield_batch()` contract method. Singleton calls are sufficient.

The ONLY batched contract method worth proposing in Phase 1 is `AkkiContract.list_tenant_entities(account_id)` — replaces the nested DB-cursor loop in `services/synisense/shield/tenant_entities.py:107-127` with a single contract call returning a precomputed list. This is a hygiene improvement that reduces SyniSense's Akki-DB reads from N+M+1 to 1.

### 3.C · Recommended batched contract methods

| Method | Replaces | Rationale |
|---|---|---|
| `AkkiContract.list_tenant_entities(account_id) -> list[TenantEntity]` | `tenant_entities.py:_load_tenant` nested cursor loop | One contract call vs. 1 + N + (N × M) DB reads. Caches in tenant_entities.py per `SYNISENSE_SHIELD_MAP_TTL_HOURS`. |

That's the only batched method I recommend. Singleton `shield_invoke()`, `solva.synthesize()`, etc. stay singleton — the fan-out today is already ≤3 per request.

---

## 4 · Proposed contract surface (Q4)

> **No code — signatures + one-line purpose only. Phase 1 build dispatch writes the actual files.**

### 4.A · `backend/contracts/synisense.py` — proposed surface

```python
class SyniSenseContract(Protocol):
    async def shield_invoke(
        self, *,
        content: str,
        purpose: str,                      # e.g. "chat", "work_studio.export.compile"
        account_id: str,                   # tenant scope (required)
        consumer_id: str,                  # surface label
        user_id: str,                      # caller user (often == account_id for internal)
        model_preference: str = "balanced",
        internal_caller: bool = False,
        system_msg: Optional[str] = None,
    ) -> ShieldResult: ...
    # purpose: the single canonical Shield entrypoint. Wraps de-id +
    # LLM + re-id + audit + trust-receipt mint. Fail-closed.

    async def get_audit_events(
        self, *,
        account_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[AuditEvent]: ...
    # purpose: paginated audit reads for the Trust Center / observability.
    # Replaces direct reads of synisense_audit_log by Solva narration.

    async def get_trust_receipt(self, *, audit_id: str, account_id: str) -> Optional[TrustReceipt]: ...
    # purpose: single-receipt lookup with tenant-scope check.

    async def get_shield_metrics(self, *, account_id: str) -> ShieldMetrics: ...
    # purpose: aggregated metrics for the per-chat audit panel + admin
    # dashboard. Replaces direct count_documents() calls by chat router.

    async def refresh_tenant_entities_cache(self, *, account_id: str) -> None: ...
    # purpose: cache-invalidation hook (Phase 0 noted the TTL-only
    # invalidation; this method gives Akki a push-invalidate path
    # when it registers new entities).
```

### 4.B · `backend/contracts/solva.py` — proposed surface

```python
class SolvaContract(Protocol):
    async def synthesize_workbook(
        self, *,
        analysis_id: str,
        account_id: str,
        objective: Optional[str] = None,
    ) -> SynthesisResult: ...
    # purpose: Solva v2 multi-workbook narration. Wraps Phase 4's
    # multi-blob synthesize path. Idempotent on cache_key.

    async def run_solva_session(
        self, *,
        session_id: str,
        account_id: str,
        phase: Literal["A","B","C","D","E"],
    ) -> PhaseResult: ...
    # purpose: directed reasoning pipeline phase runner. Replaces the
    # direct router-to-engine call.

    async def get_session_state(self, *, session_id: str, account_id: str) -> SolvaSessionState: ...
    # purpose: snapshot the session for UI rendering.

    async def refuse_to_decide_check(
        self, *,
        inputs: SolvaInputs,
        account_id: str,
    ) -> Optional[RefusalReason]: ...
    # purpose: explicit "insufficient input" gate. Returns None when
    # safe to proceed.

    async def list_solva_artefacts(
        self, *,
        account_id: str,
        context_id: Optional[str] = None,
    ) -> list[SolvaArtefact]: ...
    # purpose: paginated artefact list (replaces direct solva_sessions
    # reads by Akki routers).
```

### 4.C · `backend/contracts/akki.py` — proposed surface

> **The critical surface.** This is what SyniSense and Solva CALL BACK INTO to get the Akki data they currently read directly. It inverts the dependency.

```python
class AkkiContract(Protocol):
    # ─────────── Identity / tenancy ───────────
    async def get_tenant_profile(self, *, account_id: str) -> TenantProfile: ...
    # purpose: replace `db.accounts.find_one({"id": tenant_id})` in
    # services/synisense/shield/tenant_entities.py:92.

    async def list_contexts(self, *, account_id: str) -> list[Context]: ...
    # purpose: replace `db.contexts.find({"account_id": ...})` in
    # services/synisense/shield/tenant_entities.py:107.

    async def list_cycles(self, *, account_id: str, context_id: Optional[str] = None) -> list[Cycle]: ...
    # purpose: replace nested `db.cycles.find(...)` in
    # services/synisense/shield/tenant_entities.py:127.

    async def list_tenant_entities(self, *, account_id: str) -> list[TenantEntity]: ...
    # purpose: BATCHED — replaces the nested-cursor loop with a single
    # call returning precomputed (kind, value, source) tuples for the
    # Shield's tenant dictionary harvester. The only batched contract
    # method in Phase 1.

    # ─────────── Chat context ───────────
    async def get_chat_history(
        self, *,
        account_id: str,
        chat_id: str,
        limit: int = 50,
    ) -> list[ChatMessage]: ...
    # purpose: replace direct chat_messages reads by Solva v2 grounding.

    # ─────────── Documents / signals ───────────
    async def list_documents(
        self, *,
        account_id: str,
        context_id: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> list[Document]: ...
    # purpose: replace direct documents.find by Solva v2.

    async def list_signals(
        self, *,
        account_id: str,
        context_id: str,
        since: Optional[datetime] = None,
    ) -> list[Signal]: ...
    # purpose: replace direct signals.find by Solva v2 narration.

    async def list_objectives(self, *, account_id: str, context_id: str) -> list[Objective]: ...
    # purpose: replace direct objectives.find by Solva v2 + SyniSense engine.

    async def list_cycle_questions(
        self, *,
        account_id: str,
        cycle_id: str,
    ) -> list[CycleQuestion]: ...
    # purpose: replace direct cycle_questions.find by Solva v2 + SyniSense engine.

    async def list_briefings(self, *, account_id: str, context_id: str) -> list[Briefing]: ...
    # purpose: replace direct briefings reads by Solva v2 narration.

    # ─────────── Audit-log writers (write-back) ───────────
    async def audit_event(
        self, *,
        account_id: str,
        action: str,
        payload: dict,
    ) -> None: ...
    # purpose: SyniSense + Solva append to the universal Akki audit_log
    # without direct insert_one.
```

**Total proposed methods:**
- SyniSenseContract: 5 methods.
- SolvaContract: 5 methods.
- AkkiContract: 11 methods (inverts every Akki-DB read currently performed by SyniSense or Solva).

### 4.D · Implementation strategy (one paragraph each)

The contract files at `backend/contracts/{synisense, solva, akki}.py` ship as **Protocols + thin pass-through adapters**. The adapters in Phase 1 wrap the existing in-process imports (e.g. `AkkiContract.list_contexts(account_id)` initially calls `db.contexts.find({"account_id": account_id})`). No behaviour change. The contracts are an indirection layer that lets us run the Phase 0 invariants against the contract surface (Phase 2 enforce mode) AND that Phase 4 swaps to an HTTP client transparently.

---

## 5 · Discrepancies with the approved plan (Q5)

### 5.A · Plan assumption: clean SyniSense package boundary

**Status: PARTIALLY LEAKY.** The Plan §10 Honest Caveat assumed SyniSense is "cleanly bounded except for the tenant-entity harvester reading Akki." The live code shows:

- `services/synisense/shield/tenant_entities.py` reads `accounts`, `contexts`, `cycles` directly (confirmed assumption).
- `services/synisense/engine/*` reads `chats`, `chat_messages`, `briefings`, `cycle_questions`, `documents`, `memberships`, `objectives`, `cycles` directly (BROADER than the Plan assumed).

**Impact:** the inverted-dependency surface is bigger than the Plan estimated (3 Akki collections → 10 Akki collections). Phase 1's `AkkiContract` must cover the engine's reads as well, not just the harvester's. **NOT a behaviour change** — just a wider Phase-1 scope.

### 5.B · Plan assumption: clean Solva package boundary

**Status: SIGNIFICANTLY LEAKY.** Solva v2 reads ~25 Akki collections directly and ALSO reads SyniSense's audit-log + receipts + runs collections. The Plan assumed "Solva = reasoning over inputs."

**Impact:** `SolvaContract` is fine as proposed (5 methods), but the Phase 1 build will need to **wrap a lot more direct reads in `AkkiContract` calls** than the Plan suggested. **NOT a behaviour change** — same reads, routed through contracts.

### 5.C · Plan assumption: Akki = orchestrator over the other two

**Status: PARTIALLY TRUE.** Akki routers DO call SyniSense (via `shield_invoke`) and Solva (via direct service imports). But the call graph is NOT a clean DAG:

- Akki → SyniSense: ✅ via `shield_invoke()` (clean).
- Akki → Solva: ✅ direct service imports (clean but tight coupling).
- **SyniSense → Akki: ❌ direct DB reads (the inverted dependency).**
- **Solva → SyniSense: ❌ direct reads of synisense_audit_log + receipts + runs (cross-package leak).**
- **Solva → Akki: ❌ direct reads of ~25 Akki collections (the bigger leak).**

So Akki is the orchestrator at the HTTP-handler level, but BELOW that level the three packages all read each other's data. Phase 1 ships the contracts; Phase 2 makes them enforced.

### 5.D · Collections that genuinely belong to >1 owner

**Found: 1 ambiguous collection.**

- **`audit_log`** — appended by both Akki (route audit) and Solva (engine telemetry). The Plan implicitly treated audit_log as Akki-owned. The cleanest fix is: Akki owns the collection; both packages append via `AkkiContract.audit_event(...)`. Behaviour-preserving.

The original Phase 0 dispatch tentative split had:
- SyniSense: synisense_audit_log, synisense_trust_receipts, tenant_entities (if persisted).
  → Confirmed; `tenant_entities` is NOT persisted (in-memory cache only). The DB-backed SyniSense set is the 9 collections in §1.C.
- Solva: analyses, analysis_runs (if separate), notes_history (if separate).
  → `analysis_runs` is NOT separate (it's `analyses.runs[]` array); `notes_history` is NOT separate either (`documents.notes_history[]` and `analyses.notes_history[]` arrays). Confirmed Solva owns 19 collections including analyses + analysis_blobs + solva_* + solve_* + workbook_*.

**Plan assumed Akki = "everything else."** Confirmed; Akki owns 115 collections.

### 5.E · Tenant-propagation patterns requiring behaviour change to standardise

**None found.** Every cross-context call site already has `account_id` available (see §2.A). Standardising on explicit-kwarg is a code-shape change, not a behaviour change.

---

## 6 · ESCALATE TO USER

Three notes that need user acknowledgement before Phase 1 build dispatches, but **none are blockers**:

### 6.1 · Plan-§5B leak is bigger than assumed

The Plan estimated SyniSense reads 3 Akki collections; live code shows 10. The Plan estimated Solva reads "inputs"; live code shows ~25 Akki collections + 3 SyniSense audit collections.

**Question for you:** is Phase 1 scope still "ship the contracts at all 11 AkkiContract methods proposed in §4.C" — or do you want to defer the engine-side reads to a later sub-phase (Phase 1.B)?

**Recommendation:** ship all 11 in Phase 1. The cost difference is small (each contract method is ~10 LOC of pass-through wrapping) and shipping less now means a Phase 1.B follow-up dispatch.

### 6.2 · `audit_log` ambiguous ownership

Akki appends + Solva appends. Recommended: Akki owns; both packages write via `AkkiContract.audit_event(...)`.

**Question for you:** acknowledge?

### 6.3 · Phase 0 tenancy scanner false-positive rate (80% of non-literal sample)

The Phase 0 observe-mode report shows 145 non-literal violations. My §2.D sample categorised 80% as false positives (dynamic dicts that DO include account_id). The number to track in Phase 2's enforce flip is `definite_violation_count = 682`, NOT `violation_count = 827`.

**Question for you:** acknowledge that Phase 2's enforce-mode flip will assert against `definite_violation_count == 0` (subject to baseline allowance) and NOT against the broader counter?

---

## 7 · Recommended Phase 1 dispatch scope

Contingent on §6 acknowledgement.

### 7.A · Phase 1 build dispatch — proposed brief (concrete, ready to send)

```
RE-ARCHITECTURE — Phase 1: Contracts, Logical Data Ownership, Tenant Propagation

Per the Phase 1 Pre-Read (sprints/PHASE_1_PRE_READ.md), this dispatch
ships the contract layer with all 11 AkkiContract methods, 5
SyniSenseContract methods, and 5 SolvaContract methods. Tenant scope
(account_id) is a required kwarg on every contract method.

NO behaviour change. The contracts are PASS-THROUGH ADAPTERS in
Phase 1 — they wrap the existing in-process db.X.find / direct
service imports. Phase 2 enforces the boundary; Phase 4 swaps the
adapters to HTTP clients.

Deliverables:
  1. backend/contracts/__init__.py
  2. backend/contracts/synisense.py — SyniSenseContract Protocol + 
     InProcessSyniSenseAdapter implementation.
  3. backend/contracts/solva.py — SolvaContract Protocol + 
     InProcessSolvaAdapter implementation.
  4. backend/contracts/akki.py — AkkiContract Protocol + 
     InProcessAkkiAdapter implementation.
  5. backend/contracts/types.py — TenantProfile, Context, Cycle, 
     ChatMessage, Document, Signal, Objective, CycleQuestion,
     Briefing, TenantEntity, AuditEvent, TrustReceipt, ShieldResult,
     ShieldMetrics, SynthesisResult, PhaseResult, SolvaSessionState,
     SolvaArtefact, SolvaInputs, RefusalReason dataclasses.
  6. backend/tests/contracts/test_contract_signatures.py — verify
     every method signature in §4 exists and accepts account_id 
     keyword.
  7. backend/tests/contracts/test_contract_behaviour_preserved.py —
     for each contract method, call it AND call the underlying
     direct-DB equivalent, assert deep-equal results.
  8. backend/tests/invariants/test_invariant_contract_account_id.py —
     enforce-mode AST check that every contract method signature
     has `account_id: str` (or `*, account_id: str`) as a required 
     parameter. Build-breaking.
  9. /app/memory/sprints/PHASE_1_CONTRACTS.md — sprint memo.
  10. MASTER_STATE.md Section 6 + 8 update.

DO NOT in this phase:
  - Migrate any existing call site to use the contracts.
    (Phase 1 ships the surface; Phase 2 / Phase 3 migrates call
    sites; Phase 4 swaps adapters.)
  - Add HTTP transport.
  - Touch the Phase 0 invariants.
  - Refactor any service code outside backend/contracts/.

Acceptance criteria:
  - All 21 contract methods (5 + 5 + 11) defined as Protocol + 
    InProcess adapter pair.
  - account_id required keyword on every method (enforced by the
    new AST invariant).
  - Behaviour-preservation test green for every method.
  - Phase 0 invariants 8/8 deterministic + delib smoke 4/4 still
    PASS. Phase 14 + 15 lockdowns still PASS.

Out of scope:
  - Call-site migration.
  - HTTP transport.
  - Behaviour changes.
```

### 7.B · Phase 1 risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Type drift between Protocol + adapter | Medium | The behaviour-preservation tests cover this. |
| InProcessAkkiAdapter imports too much of Akki | Low | The adapter lives in `backend/contracts/akki.py` and imports only `core.db`; everything else is pass-through. |
| Tests get too slow | Low | Phase 1's behaviour-preservation tests are deterministic (no LLM). |
| Real LLM call leaks through Protocol | None | The Protocol surfaces accept `account_id` as kwarg; no LLM call lands in this phase. |

### 7.C · Phase 1 → Phase 2 handoff

Phase 1 ships the surface. Phase 2 (Tenancy Guard) will:
1. Flip the Phase 0 tenancy scanner to enforce mode (`definite_violation_count == 0` against a Phase-1 baseline).
2. Migrate every call site identified in §1.A from direct-DB reads to contract calls.
3. Add `@cross_tenant` markers (or comment exemptions) for the §2.C list of intentionally-cross-tenant collections.
4. Add a runtime guard on `db.<tenant_scoped>.<method>()` that fails-fast if the call originates from outside `backend/contracts/akki.py`.

Phase 3 (Frontend API-boundary contract) will pin the routes' response shapes against goldens — independent of Phase 2 progress.

---

**End of Phase 1 Pre-Read. Status: CLEAN_WITH_NOTES — Phase 1 build dispatch is ready contingent on §6 acknowledgement.**
