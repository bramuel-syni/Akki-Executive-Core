# Phase 2.5a — Top-7 Density Collections Migration + Cross-Tenant Whitelist

**Dispatch:** Re-Architecture Phase 2.5 Build (split internally into 2.5a + 2.5b per user-authorised latitude).
**Predecessor:** Phase 2.4 ✅ DONE (`contexts` hybrid migration).
**Mode:** Per Discipline Rail R4 — one sub-phase in flight (Phase 2.5a).
**Date:** 2026-06-23.
**Status:** **DONE. CLEAN — zero new failures attributable to Phase 2.5a.**

---

## 1 · Goal

Migrate the **top-7 highest-density collections** to zero static violations and flip per-collection enforce mode, plus formalise the `_CROSS_TENANT_COLLECTIONS` whitelist (paper trail for collections legitimately out-of-scope for the scanner).

The 7 collections migrated:

| Collection | Phase 2.4 close | Phase 2.5a pre-marker | Phase 2.5a post-marker |
|---|---:|---:|---:|
| `inbound_queue` | 19 | 9 (post `context_id` alt-key) | **0** ✅ |
| `tasks` | 15 | 14 (post `task_id` alt-key) | **0** ✅ |
| `chat_messages` | 12 | 1 (post `chat_id` alt-key) | **0** ✅ |
| `user_calendar_credentials` | 11 | 5 (post `user_id` alt-key) | **0** ✅ |
| `signals` | 10 | 10 | **0** ✅ |
| `cycles` | 10 | 10 | **0** ✅ |
| `solva_v2_sessions` | 10 | 10 | **0** ✅ |
| **Total** | **87** | **59** | **0** ✅ |

Plus `studio_blocks`: 9 → 0 (resolved via `artefact_id` alt-key + `_resolve_artefact` helper-fusion) — held for Phase 2.5b enforce flip.

NO behaviour change. Phase 0 + Phase 1 + Phase 14 + Phase 15 + Phase 2.1 + Phase 2.2 + Phase 2.3 + Phase 2.4 + Track A 5/6/7 invariants are the gate.

---

## 2 · Pre-flight check (per user directive)

- **Phase 0 goldens** — unchanged from Phase 2.4 close.
- **Phase 1 invariants** — `33/33` PASS at start of Phase 2.5a; `34/34` PASS at close (1 new test added: `test_cross_tenant_whitelist_disjoint_from_scoped`).
- **Partial alt-key landing from pre-compaction** — verified by re-running scanner at session start. Delta `135 → 101` was within the expected band for the in-place alt-key widening (chat_messages +chat_id, user_calendar_credentials +user_id, cycle_assignments +ned_id +brief_id, studio_blocks +artefact_id, team_catalogue +member_id, exco_teams +team_id, tasks +task_id). No broken foundation; no Phase 0 golden or Phase 1 invariant break attributable to the partial landing.

---

## 3 · Scanner extensions (this phase)

### 3.A · Alt-key map widening (2 entries)

```python
# Phase 2.5a additions to ALT_TENANCY_KEYS:
"inbound_queue":     frozenset({"account_id", "context_id"}),
"chat_attachments":  frozenset({"account_id", "chat_id"}),
```

`inbound_queue` widening resolves 10 of the 19 Phase-2.4-close hits (every inbound-queue row carries `context_id` per the mailbox-router contract).

### 3.B · TENANT_GATE_HELPERS extension (1 collection)

```python
# Phase 2.5a addition to TENANT_GATE_HELPERS:
"studio_blocks": frozenset({"_resolve_artefact"}),
```

Honours the comment-promise in the `studio_blocks` alt-key block (Phase 2.4 close had this as a "to-finish" contract). `_resolve_artefact` (`routers/studio_blocks.py:444`) verifies parent artefact + membership upstream → every subsequent `db.studio_blocks.*` call inside its handlers is already context-validated.

### 3.C · _CONTEXT_HELPER_FUNCTIONS exemption widening (1 entry)

```python
_CONTEXT_HELPER_FUNCTIONS = frozenset({
    "_dep",                  # Phase 2.4
    "_verify_ned_context",   # Phase 2.4
    "_resolve_artefact",     # Phase 2.5a — studio_blocks artefact resolver
})
```

The `_resolve_artefact` body's own `find_one({"id": aid})` lookup IS the tenancy contract (it then verifies membership in the next line) — not a consumer of it. Exempt from scanner.

### 3.D · `_CROSS_TENANT_COLLECTIONS` formal whitelist (NEW — Phase 2.5a)

New constant in `test_invariant_tenancy.py` documenting 40 collections that are **legitimately out-of-scope** for the tenancy scanner by design (pre-account, system audit, telemetry, cron-state, webhook log, public content). Each entry carries inline rationale. The list does NOT change scanner behaviour today (anything outside `TENANT_SCOPED_COLLECTIONS` is already unchecked) — it exists as a formal paper trail so future agents see an immediate dated answer to "why is collection X unchecked?" rather than relying on absence.

Categories with counts:
- **Identity / pre-account (7):** accounts, memberships, context_members, invitations, revoked_jtis, oauth_pkce_verifiers, login_attempts.
- **Cohort onboarding pre-account (9):** cohorts, cohort_applications, cohort_application_audit, cohort_copy_overrides, cohort_email_events, cohort_invites, cohort_magic_links, cohort_special_asks, cohort_waitlist.
- **Early-access / interest forms pre-account (5):** early_access_applications, early_access_optins, early_access_registrations, enterprise_interest, billing_launch_interest.
- **System audit / telemetry / cron-state (14):** audit_log, audit_invariant_violations, auth_events, chat_audit_log, feature_events, telemetry_events, scheduler_runs, model_fallback_log, llm_deep_usage, llm_retry_log, extraction_failures, extractions_log, backfill_jobs, backfill_log, async_jobs.
- **Synisense Shield audit (4):** synisense_audit_log, synisense_runs, synisense_shield_maps, synisense_trust_receipts.
- **External webhook logs (4):** stripe_events, stripe_dead_letter, inbound_queue_raw, inbox_routing_log.
- **Public content (3):** blog_posts, blog_subscribers, news_items.

**New invariant** — `test_cross_tenant_whitelist_disjoint_from_scoped` enforces `_CROSS_TENANT_COLLECTIONS & TENANT_SCOPED_COLLECTIONS == ∅`. Build-breaking on overlap.

### 3.E · `_ENFORCE_MODE_COLLECTIONS` widening

```python
# Phase 2.4 close (4 collections):
#   {chats, documents, work_studio_exports, contexts}
#
# Phase 2.5a close (11 collections):
_ENFORCE_MODE_COLLECTIONS = frozenset({
    "chats",
    "documents",
    "work_studio_exports",
    "contexts",
    # Phase 2.5a additions (all 7 reached 0):
    "inbound_queue",
    "tasks",
    "chat_messages",
    "user_calendar_credentials",
    "signals",
    "cycles",
    "solva_v2_sessions",
})
```

`test_tenancy_enforce_mode_for_migrated_collections` is now build-breaking on any new definite violation against any of the 11 collections.

---

## 4 · Markers placed (59 across 19 files)

Per-file bottom-up application (Phase 2.4 lesson — line-shift safety). Every marker carries inline rationale per Discipline Rail R5.

| File | # markers | Pattern summary |
|---|---:|---|
| `routers/oauth_google.py` | 5 | `cred` resolved upstream by `user_id`+`context_id`; row-id-targeted writes |
| `routers/tasks.py` | 8 | Task pre-validated by upstream `find_one` with `account_id`; row-id-targeted reads/writes |
| `routers/inbound_email.py` | 3 | Contributor email reply: token validated upstream, then task fetched/updated by row id |
| `services/tasks/compile_service.py` | 3 | Service invoked by tenant-gated router entry; row-id-targeted update |
| `routers/inbound_queue.py` | 3 | Queue item pre-validated by upstream `find_one` with `context_id`; row-id-targeted update |
| `routers/daily_review.py` | 6 | Handler is context-membership-gated; queue item fetched/updated by row id |
| `routers/solva_v2.py` | 9 | Session pre-validated by upstream `find_one` with `account_id`; row-id-targeted updates; +1 cron-secret-gated stale-session sweeper |
| `routers/cycles.py` | 7 | Handler is context-membership-gated; filt is `$or` over (context_id + seed_marker_visible_for) — both tenant-scoped |
| `routers/cycle_manager.py` | 1 | Handler is context-membership-gated upstream; cycle fetched by row id |
| `services/inbox_routing/backfill.py` | 1 | Admin/cron backfill worker: cross-tenant by design |
| `services/synisense/engine/signal_seeder.py` | 1 | Internal seeder invoked from context-gated entry point |
| `routers/admin_signal_kpi.py` | 1 | Admin-only route (super-admin gate at file entry); cross-tenant KPI |
| `routers/sandbox.py` | 3 | Sandbox seed insert: ctx loaded with `owner_account_id` upstream |
| `routers/shares.py` | 1 | Share token validated upstream; signals filtered by token-resolved context_id list |
| `routers/studio_blocks.py` | 1 | Block hydrator: parent block validated via `_resolve_artefact` upstream |
| `services/documents/intelligence_service.py` | 1 | Intelligence promoter: doc validated with `account_id` upstream |
| `services/signal_dedup.py` | 2 | Dedup helper called with account-gated signal payload |
| `routers/governance.py` | 2 | Admin governance KPI route (super-admin gate); cross-tenant aggregation |
| `routers/observability.py` | 1 | Admin/observability cron route: cross-tenant by design |
| **Total** | **59** | |

---

## 5 · Scanner delta (before / after Phase 2.5a)

| Metric | Phase 2.4 close | Phase 2.5a post-alt-key | Phase 2.5a post-markers | Δ this phase |
|---|---:|---:|---:|---:|
| Total violations | 135 | 91 | **32** | **−103 (−76%)** |
| Definite (literal) | 115 | 75 | **26** | **−89 (−77%)** |
| Non-literal | 20 | 16 | **6** | **−14 (−70%)** |
| 7 target collections | 87 | 59 | **0** | **−87 (−100%)** ✅ |

**Cumulative scanner reduction from Phase-0 baseline through Phase 2.5a:**

| Metric | Phase-0 baseline (immutable) | Phase 2.5a close | Cumulative delta |
|---|---:|---:|---:|
| Total | 685 | **32** | **−653 (−95%)** |
| Definite | 550 | **26** | **−524 (−95%)** |
| Non-literal | 135 | **6** | **−129 (−96%)** |

---

## 6 · Test results

| Suite | Result | Notes |
|---|---|---|
| `tests/invariants/` (all) | **34 PASS, 5 SKIP** | +1 new test vs Phase 2.4 (`test_cross_tenant_whitelist_disjoint_from_scoped`); 5 SKIP = 4 deliberate-violation env-gated + 1 pre-existing upload-multi schema drift (unchanged from Phase 2.4 close) |
| `test_chat_fluency_no_shield_leak.py` (Phase 14) | **PASS** | Preserved |
| `test_chat_system_msg_prepended.py` (Phase 14) | **PASS** | Preserved |
| `test_chat_token_shape_consistency.py` (Phase 14) | **PASS** | Preserved |
| `test_tenant_entities_length_floor.py` (Phase 14) | **PASS** | Preserved |
| `test_spacy_org_common_noun_protector.py` (Phase 14) | **PASS** | Preserved |
| `test_docs_download.py` (Phase 15) | **PASS** | Preserved |
| `test_track_a_phase4_versioning_multi.py` | **PASS** | Preserved |
| `test_track_a_phase4_forecaster_tuning.py` | **PASS** | Preserved |
| `test_track_a_phase4_iter2_corrective.py` | **PASS** | Preserved |
| `test_track_a_phase5_lifecycle.py` | 1 PRE-EXISTING fail | `test_phase5_w2_compile_full_cycle` — `lifecycle_state is None`. Verified pre-existing via `git stash` clean-tree retest. Logged in maintenance backlog. |
| `test_track_a_phase6_inline_edit_and_bc_removal.py` | **PASS** | Preserved |
| `test_track_a_phase7_confidence_scoring.py` | **PASS** | Preserved |
| Targeted 7-collection sweep (cycle/task/sandbox/oauth/share/inbound) | **86 PASS, 10 SKIP, 6 PRE-EXISTING errors** | All 6 errors pre-existing (env-config / postmark fixture / session.actions tab). Verified pre-existing via `git stash` clean-tree retest. |
| `tests/characterisation/` | 1 PRE-EXISTING fail | `test_work_studio_compile_start_golden_shape`. Verified pre-existing via `git stash` clean-tree retest. |

**Aggregate Phase 2.5a deterministic lockdown:** 50 PASS (invariants 34 + Phase 14 8 + Phase 15 1 + Track A 4 lockdowns 7). Targeted regression: 86 PASS. No new failures attributable to Phase 2.5a.

**Backend smoke:** Hot reload picked up changes; service healthy throughout dispatch.

---

## 7 · Discipline rails — what was honoured

| Rail | How Phase 2.5a honoured it |
|---|---|
| R1 (Pre-Read) | This is a sub-phase of Phase 2.5; Phase 2.4 Pre-Read §8.A recommended `inbound_queue` next + the user's Phase 2.5 dispatch authorised the broader 23-collection scope with explicit split latitude |
| R2 (Pre-Read for each dispatch) | User confirmed Option (a) Phase 2.5a split with explicit "Top Half + Whitelist" scope and discipline; no new scope expansion |
| R3 (one-shot dispatch) | Single dispatch — pre-flight scanner → alt-key widening → helper-fusion add → whitelist creation → markers (bottom-up per file) → enforce flip → regression sweep → memo |
| R4 (≤10 lockdown tests per phase) | 1 new test added (`test_cross_tenant_whitelist_disjoint_from_scoped`). The 7 collection migrations are exercised by the existing tenancy invariant + the per-collection enforce test (already in place since Phase 2.1). Well under budget. |
| R5 (Honesty Protocol) | Every marker carries inline rationale; helper-fusion auto-resolves are visible in the live `tenancy_violations.json` (no silent suppression). Pre-existing failures explicitly flagged. One shares.py line-continuation `\` collision was caught + fixed inline (marker moved to line above). |
| R6 (no unrequested cleanups) | Only the 7 target collections + `studio_blocks` helper-fusion comment-promise completion. No adjacent collections migrated; no "while I'm in there" refactors. |
| R7 (lockdown sweep before close) | Full invariant + Phase 14 (5 files) + Phase 15 + Track A 4/5/6/7 + 13-suite targeted contexts/cycles/tasks/sandbox/oauth/share sweep — passing modulo pre-existing failures verified via clean-tree retest. |

---

## 8 · Deviations from dispatch

### 8.1 · `shares.py:485` line-continuation collision

The marker script appended `  # tenancy:...` to a line ending in `\` (Python line continuation). This created a `SyntaxError: unexpected character after line continuation character`. Caught by invariant suite collection failure within seconds. Fix: moved the marker to the line ABOVE the call (the scanner accepts marker on line OR line-above per `_line_is_escape_hatched()`). No other line-continuation collisions across the other 58 marker placements (verified via `ast.parse` smoke across all 19 files).

### 8.2 · Internal split executed (per pre-authorised latitude)

User's original Phase 2.5 dispatch granted explicit permission to split if shipping all 23 collections at once exceeded safe behaviour-preservation budget. Agent exercised this latitude. Phase 2.5b (remaining 12 collections at long-tail density) deferred to the next dispatch.

### 8.3 · `inbound_queue` `context_id` widening is broader than the migrated collection alone

Adding `context_id` to `inbound_queue` alt-keys also auto-resolved 1 hit in `routers/shares.py:531` (a `db.inbound_queue.find(...)` on the active-context list). Resolution carries over cleanly because the underlying contract IS that `inbound_queue` rows carry `context_id`. No behavioural ripple.

### 8.4 · `studio_blocks` not in this dispatch's enforce flip

`studio_blocks` reached 0 violations through Phase 2.5a's alt-key widening + helper-fusion contract completion but is NOT in this dispatch's `_ENFORCE_MODE_COLLECTIONS` flip — held for Phase 2.5b alongside the rest of the long-tail. Rationale: keep this dispatch's enforce flip cleanly scoped to the 7 explicitly-named collections from the dispatch brief; avoid scope creep mid-flight. Phase 2.5b will flip `studio_blocks` + the remaining long-tail in one coordinated close.

---

## 9 · Pre-existing failures pool (verified via clean-tree retest)

The following failures appear in the targeted regression but are **NOT attributable to Phase 2.5a** — each reproduces on a `git stash` clean tree:

| Test | Symptom | Pre-existing? |
|---|---|:---:|
| `test_track_a_phase5_lifecycle.py::test_phase5_w2_compile_full_cycle` | `lifecycle_state is None` after compile | ✅ Verified |
| `test_work_studio_compile_golden.py::test_work_studio_compile_start_golden_shape` | Golden shape mismatch | ✅ Verified |
| `test_cycle_manager_actions_tab.py` (3 tests) | Setup error | ✅ Verified |
| `test_phase_b_sandbox_upload.py` (3 tests) | Setup error | ✅ Verified |
| `test_iter70_inbound_edge.py`, `test_iter70_inbound_triage.py` | `KeyError: 'POSTMARK_SERVER_TOKEN'` | ✅ Verified (env-config) |
| `test_iter42_signal_kpi.py` (8 skipped) | Patch 19 quarantine | ✅ Verified |

All logged for maintenance backlog. Phase 2.5a footprint: **zero net-new failures.**

---

## 10 · Follow-ups (logged for Phase 2.5b)

### 10.1 · Recommended next dispatch: **Phase 2.5b — Long-tail close-out (15 collections, 32 violations)**

Residual 32 violations across 15 collections (density-ordered):

| Collection | Hits | Notes |
|---|---:|---|
| exco_teams | 8 | exco_teams.py — already has `team_id` alt-key from Phase 2.5a pre-work; mostly markers |
| team_catalogue | 6 | team_catalogue.py — already has `member_id` alt-key |
| cycle_questions | 4 | cycle_questions.py |
| cycle_assignments | 2 | cycle_assignments.py |
| ideas_digests | 2 | ideas_digests.py |
| signal_actions | 1 | Single-hit |
| compilations | 1 | Single-hit |
| decks | 1 | Single-hit |
| document_shares | 1 | Single-hit |
| questions | 1 | Single-hit |
| strategic_goals | 1 | Single-hit |
| workbook_blobs | 1 | Single-hit |
| workbook_analyses | 1 | Single-hit |
| analyses | 1 | Single-hit |
| analysis_blobs | 1 | Single-hit |

Plus `studio_blocks` (0 violations, held from Phase 2.5a for the coordinated enforce flip).

**Phase 2.5b acceptance criteria:**
- All 15 long-tail collections reach 0 definite violations.
- `_ENFORCE_MODE_COLLECTIONS` widened to ALL tenant-scoped collections (~45 total).
- Final close-out memo `PHASE_2_5_CLOSE_OUT.md` declares Phase 2 → DONE.
- Resolution of any 6 non-literal residuals via inline markers with rationale OR Upgrade A spread-tracker extension.

### 10.2 · Pre-existing failures pool

Carried forward unchanged from Phase 2.3/2.4 close-out memos — items pre-existing before Phase 2 work; logged for Phase 2.X maintenance backlog.

### 10.3 · Top-line callout for MASTER_STATE Section 9

> Phase 2 cumulative posture (through Phase 2.5a): **eleven collections under per-collection enforce mode** (`chats`, `documents`, `work_studio_exports`, `contexts`, `inbound_queue`, `tasks`, `chat_messages`, `user_calendar_credentials`, `signals`, `cycles`, `solva_v2_sessions`). Scanner Upgrades A/B/C/D + helper-fusion (3 helpers now: `require_context_membership`, `_verify_ned_context`, `_resolve_artefact`) + 11 alt-key widenings + formal `_CROSS_TENANT_COLLECTIONS` whitelist (40 entries, 7 categories). **Total tenancy violations down 95% (685→32); definite down 95% (550→26).** Zero production cross-tenant bugs introduced; zero behaviour changes. Phase 2.5b (long-tail close-out + final enforce flip = full Phase 2 close) follows.

---

**End of Phase 2.5a sprint memo.**
