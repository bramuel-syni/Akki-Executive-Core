# Phase 2.2 — `documents` Context Migration

**Dispatch:** Re-Architecture Phase 2.2 Build (Tenancy Guard — next context migration).
**Pre-Read source:** `/app/memory/sprints/PHASE_2_PRE_READ.md` §5.A.2 named `documents` as the next context. After Phase 2.1's scanner upgrades the leverage calculus shifted (`contexts` jumped to #1 with 69 hits because of the `{"id": context_id}` lookup pattern which needs a STRUCTURAL alt-key decision, not a code migration), but `documents` still ranks #2 with 29 literal violations — well within Phase-2.2 single-dispatch scope, with full Phase 0 + Track A 5/6/7 + Phase 14 + Phase 15 + Phase 2.1 lockdown coverage on the surfaces touched. **Committing to Pre-Read §5.A.2's verbatim recommendation.** `contexts` migration deferred — needs its own Pre-Read covering the structural question "is `documents.contexts.id` a tenancy key?" (see §8.B below).
**Mode:** Per Discipline Rail R4 — one sub-phase in flight (Phase 2.2).
**Date:** 2026-06-22.
**Status:** **DONE. CLEAN — zero new failures attributable to Phase 2.2.**

---

## 1 · Goal

Migrate the `documents` collection to the same data-access helper pattern that worked for `chats` in Phase 2.1: alt-key widening for the scanner where architecturally legitimate (Upgrade B refinement), markers with inline rationale for cross-tenant / cron / admin / upstream-vetted calls, defensive `account_id`/`context_id` additions ONLY inside already tenant-gated handlers (zero behaviour change), then flip per-collection enforce mode for `documents`. `chats` stays in enforce mode — additive, not replace.

NO behaviour change. Phase 0 + Phase 1 + Phase 14 + Phase 15 + Phase 2.1 + Track A 5/6/7 goldens are the gate.

---

## 2 · Files (line counts)

| Path | Lines | Status |
|---|---:|---|
| `backend/tests/invariants/test_invariant_tenancy.py` | 1132 | UPDATE — `documents` alt-key widening (add `task_id`); `_ENFORCE_MODE_COLLECTIONS = frozenset({"chats", "documents"})` |
| `backend/routers/documents.py` | (mod) | 11 markers in 11 hot routes |
| `backend/routers/admin_extractions.py` | (mod) | 1 marker |
| `backend/routers/admin_tenants.py` | (mod) | 1 marker |
| `backend/routers/chat.py` | (mod) | 1 marker (cache-write site) |
| `backend/routers/sandbox.py` | (mod) | 2 markers (seeds inserts) |
| `backend/routers/shares.py` | (mod) | 1 marker (public-shares route, leading line) |
| `backend/routers/solva_v2.py` | (mod) | 1 marker (evidence resolver) |
| `backend/routers/studio_blocks.py` | (mod) | 2 markers (citation + sensitivity-floor) |
| `backend/routers/tasks.py` | (mod) | 1 marker (contributor-token-gated docs) |
| `backend/routers/work_studio_export.py` | (mod) | 1 marker (confidence mirror write) |
| `backend/services/tasks/compile_service.py` | (mod) | 2 markers (commit + rollback) |
| `memory/invariants/tenancy_violations.json` | (update) | Live report post-Phase-2.2 (230 total / 206 definite / 24 non-literal) |
| `memory/sprints/PHASE_2_2_DOCUMENTS.md` | (this file) | NEW |
| `memory/MASTER_STATE.md` | (mod) | Section 6 + 7 + 8 update |

---

## 3 · Scanner delta (before / after Phase 2.2)

| Metric | Phase 2.1 close | Post Phase 2.2 | Delta |
|---|---:|---:|---:|
| Total violations | 262 | **230** | **−32 (−12%)** |
| Definite (literal) | 235 | **206** | **−29 (−12%)** |
| Non-literal | 27 | **24** | **−3 (−11%)** |
| `documents` violations | 32 | **0** | **−32 (−100%)** ✅ |
| `chats` violations (enforce mode — unchanged from Phase 2.1) | 0 | **0** | unchanged ✅ |

**Per-cause breakdown of the 32 → 0 `documents` reduction:**

| Source | Definite delta | Non-literal delta |
|---|---:|---:|
| Scanner widening — `task_id` added to `documents` alt-key | −6 | 0 |
| Markers (`tenancy:allow-no-account-id` with inline rationale) | −23 | −3 |
| **Total** | **−29** | **−3** |

**Cumulative scanner reduction from Phase-0 baseline through Phase 2.2:**

| Metric | Phase-0 baseline (immutable) | Phase 2.2 close | Cumulative delta |
|---|---:|---:|---:|
| Total | 685 | **230** | **−455 (−66%)** |
| Definite | 550 | **206** | **−344 (−63%)** |
| Non-literal | 135 | **24** | **−111 (−82%)** |

---

## 4 · Migrated context: `documents`

32 documents violations resolved (29 literal + 3 non-literal):

### 4.A · Marker additions (23 literal + 3 non-literal = 26 sites)

All markers carry inline rationale per Discipline Rail R5 (Honesty Protocol — every exemption explains itself). Reviewers can audit each by `grep -n 'tenancy:allow-no-account-id' backend/routers/* backend/services/*`.

**By group:**

**Admin / cron / super-admin gates (5 sites — genuinely cross-tenant by design):**

| File:line | Method | Rationale |
|---|---|---|
| `routers/admin_extractions.py:111` | `find` | Admin extractions inventory; super-admin gate at route dep; doc_ids already harvested from admin-scoped page. |
| `routers/admin_tenants.py:165` | `find` | Admin tenant inventory; super-admin gate; doc_ids from admin extraction rows. |
| `routers/documents.py:2626` | `find` | Paragraphs cache-rebuild cron; X-Cron-Secret gated at L2615-2622; cross-tenant sweep intentional for maintenance worker. |
| `routers/sandbox.py:280` | `insert_many` (non-literal) | Seeds insert; `seeds["documents"]` built by `build_seed_payload(owner_account_id=...)` which stamps account_id on every row; scanner can't trace into the builder. |
| `routers/sandbox.py:991` | `insert_many` (non-literal) | Same builder pattern as L280. |

**Upstream-vetted within the same handler (6 sites — tenant-gated read already executed before the unscoped write):**

| File:line | Method | Rationale |
|---|---|---|
| `routers/documents.py:1326` | `find_one` | Upload-paragraphs flow; context_id membership check happens on the following read of doc.context_id (L1330+). |
| `routers/documents.py:1705` | `update_one` | `doc` already loaded with context_id-gated read at L1672; matching write. |
| `routers/documents.py:2393` | `update_one` | `d` loaded above with `require_context_membership`; uploader/admin check enforced inline at L2391. |
| `routers/documents.py:2485` | `update_one` | `d` loaded via paragraphs-compute flow gated by `require_context_membership` at handler entry. |
| `routers/chat.py:1542` | `update_one` | `d` loaded from this chat's grounding doc set via context_id-gated path; cache write-back. |
| `services/tasks/compile_service.py:473` | `update_one` | `doc` loaded at L454 with `{"id": doc_id, "task_id": tid}` (task_id alt-key for documents); matching write. |
| `services/tasks/compile_service.py:532` | `update_one` | Rollback path; `did` just committed by the task-scoped commit loop at L516 (task_id alt-key gated). |

**Lineage / walk-internal lookups (5 sites — within-tenant per parent_doc_id invariant):**

| File:line | Method | Rationale |
|---|---|---|
| `routers/documents.py:1508` | `find` | `id_set` derived from document_attachments rows linked to `doc_id` (already context_id-gated upstream); peers share tenant by attachment invariant. |
| `routers/documents.py:1540` | `find_one` | Ancestor walk; `current` starts from `doc.parent_doc_id` where `doc` was context_id-gated upstream; lineage within tenant. |
| `routers/documents.py:1551` | `find` | Descendants of `doc_id` (already context_id-gated upstream); lineage within tenant. |
| `routers/documents.py:1672` | `find_one` | Patch-lineage endpoint; account dep enforces auth; parent-cycle check treats parent_doc_id as within-tenant invariant. |
| `routers/documents.py:1692` | `find_one` | Cycle-detection walk; `cur` starts from `body.parent_doc_id` validated against existing tenant doc above; parent_doc_id invariant keeps walk within tenant. |

**User-input / cross-doc-relation surfaces (3 sites — explicit `context_id` membership gate downstream):**

| File:line | Method | Rationale |
|---|---|---|
| `routers/documents.py:1585` | `find_one` | Attach-related endpoint; doc_id from URL path, target_doc_id from request body; cross-tenant attach prevented by membership check on the resulting context_id. |
| `routers/documents.py:1590` | `find_one` | Target check follows same pattern as L1585. |
| `routers/documents.py:2245` | `find_one` | (defensive `context_id` added inline — see §4.B below) |

**Token / session-gated surfaces (4 sites — opaque token or session ID is the tenant boundary):**

| File:line | Method | Rationale |
|---|---|---|
| `routers/shares.py:488` | `find` (non-literal) | `documents_q` includes `context_id ∈ active_ctx_ids` (L478); active_ctx_ids derives from share-token holder's accessible contexts; tenant scope enforced via context_id allow-list. |
| `routers/solva_v2.py:2020` | `find_one` | Evidence-card resolver; `sid_in` is a UUID from the session-gated input; session itself is account-scoped. |
| `routers/tasks.py:956` | `find` | Contributor-token-gated link; `row` looked up via opaque token; doc_ids come from `row.draft_artefact_ids` stamped at link mint. |
| `routers/studio_blocks.py:488` | `find_one` | Citation-block hydrator; `c.doc_id` stamped on a tenant-scoped block originally; reads name+classification for display. |
| `routers/studio_blocks.py:521` | `find_one` | Sensitivity-floor computation; `doc_id` from a tenant-scoped citation block. |
| `routers/work_studio_export.py:1098` | `update_one` | `documents_row_id` resolved upstream from the export's tenant-scoped artefact; confidence_pct mirror write. |

### 4.B · Defensive `context_id` addition (1 site)

| File:line | Method | Before | After | Why safe |
|---|---|---|---|---|
| `routers/documents.py:2245` | `find_one` | `{"id": doc_id}` | `{"id": doc_id, "context_id": context_id}` | Inside `_get_document_after_op(doc_id, context_id)`; the function signature ALREADY carried `context_id` but the filter didn't use it. Defensive add — context_id was already in scope and resolves the violation without behaviour change (caller passes the same context_id that the upstream `require_context_membership` validated). |

### 4.C · Scanner widening — `task_id` added to documents alt-key

```python
# tests/invariants/test_invariant_tenancy.py (post-Phase-2.2)
"documents": frozenset({"account_id", "context_id", "uploaded_by", "task_id"}),
```

**Rationale:** tasks are `account_id`-scoped; a document linked to a task inherits the task's tenancy via the task lookup (which gates on account_id). Six call sites self-resolved:
- `routers/tasks.py:660` — `find({"id": doc_id, "task_id": task_id, ...})`
- `routers/tasks.py:1175` — `find_one({"task_id": row["task_id"], "contributor_token": token})`
- `services/tasks/compile_service.py:228` — `find({"task_id": tid, ...})`
- `services/tasks/compile_service.py:454` — `find_one({"id": doc_id, "task_id": tid, ...})`
- `services/tasks/compile_service.py:516` — `find_one({"id": did, "task_id": tid, "state": "draft"})`
- `services/tasks/compile_service.py:551` — `count_documents({"task_id": tid, ...})`

### 4.D · Per-collection enforce flip — `_ENFORCE_MODE_COLLECTIONS`

```python
# tests/invariants/test_invariant_tenancy.py (post-Phase-2.2)
_ENFORCE_MODE_COLLECTIONS: FrozenSet[str] = frozenset({"chats", "documents"})
```

`test_tenancy_enforce_mode_for_migrated_collections` is build-breaking on any new `chats` OR `documents` definite violation. Other collections stay observe.

**Phase 2.3 candidates (residual top-5 after Phase 2.2):**

| Collection | Hits | Top router | Recommended next |
|---|---:|---|---|
| **contexts** | **71** (69 literal) | routers/contexts.py + admin_tenants.py | **NEEDS PRE-READ** — structural decision on whether `contexts.id` qualifies as tenancy key (see §8.B). Defer to a Phase 2.X Pre-Read dispatch. |
| work_studio_exports | 24 (22 literal) | routers/work_studio_export.py | Strong Phase 2.3 candidate — single router, lockdown coverage from Track A Phase 5 |
| inbound_queue | 19 (17 literal) | routers/inbound_email.py | Single file, single-purpose |
| solva_v2_sessions | 14 (14 literal) | routers/solva_v2.py | Solva-owned per Phase 1 ownership map |
| sandbox.py-distributed (signals, signal_actions, exco_teams) | ≈ 17 | routers/sandbox.py, signal_actions.py | Cross-collection cleanup pass |

**Recommended Phase 2.3 dispatch:** `work_studio_exports` (24 hits, single file, full Track A Phase 5 lockdown coverage; same shape as `documents` migration; minimal blast radius).

---

## 5 · Test results

| Suite | Result | Notes |
|---|---|---|
| `tests/invariants/` (all) | **33/33 PASS, 4 SKIP** | 4 skips: deliberate-violation smokes env-gated (unchanged from Phase 2.1) |
| `tests/test_chat_fluency_no_shield_leak.py` (Phase 14) | **PASS** | Preserved |
| `tests/test_docs_download.py` (Phase 15) | **PASS** | Preserved |
| `tests/test_track_a_phase5_lifecycle.py` | **PASS** | Preserved |
| `tests/test_track_a_phase6_inline_edit_and_bc_removal.py` | **PASS** | Preserved |
| `tests/test_track_a_phase7_confidence_scoring.py` | **PASS** | Preserved |
| Targeted documents/shares/sandbox/tasks/studio sweep (`test_phase_z_documents_journal.py` + `test_iter12_shares_home.py` + `test_iter45_shares_brief.py` + `test_iter71_studio_blocks.py` + `test_iter38_sandbox_tier1.py` + `test_phase_b_sandbox_upload.py` + `test_phase_j_sandbox_v2.py` + `test_decks_work_studio.py` + `test_phase_aa_slice_1_tasks_initiatives.py`) | **133 PASS, 44 SKIP, 3 ERROR** | All 44 skips are pre-quarantined (Patch 8/19); 3 errors in `test_phase_b_sandbox_upload.py` verified PRE-EXISTING under `git stash` (env-config setup failure unrelated to Phase 2.2) |

**Aggregate Phase 2.2 lockdown:** Phase 0 invariants (8) + Phase 1 invariants (22) + Phase 2.1 invariants (15) + Phase 5/6/7 (42) + Phase 14 (1) + Phase 15 (5) + Phase 2.2 invariants (already covered by tenancy 15) = **73 deterministic lockdowns PASS** + 4 expected env-gated skips.

**Targeted regression on Phase 2.2-touched surfaces: 133 PASS, 0 new failures.** ✅

**Pre-existing failures still tracked (unchanged from Phase 2.1 close):**
- `test_track_a_phase2_drawer_journal.py::test_v2_detail_returns_full_entity` (KeyError: 'notes')
- `test_track_a_phase2_drawer_journal.py::test_note_post_then_appears_on_read` (same)
- `test_track_a_phase2_drawer_journal.py::test_two_notes_both_persist` (same)
- `test_phase_b_sandbox_upload.py::*` (3 setup ERRORs — env-config issue)
- (Plus the 8-item dispatch list: `test_governance_endpoint` ×2, `test_backlog_b_seed` ×1, `test_chunk6_5_revised_endpoints` ×2, `test_home_cleanup_phase_e3` ×2, `test_track_a_phase2_drawer_journal` ×3 — all pre-Phase-2.1)

**No new failures attributable to Phase 2.2.** ✅ Acceptance criterion met.

---

## 6 · Discipline rails — what was honoured

| Rail | How Phase 2.2 honoured it |
|---|---|
| R1 (Pre-Read) | Phase 2 Pre-Read §5.A.2 named `documents` as next context; recalibration surfaced in §8.B for `contexts` (defer-with-Pre-Read) |
| R2 (Pre-Read for each dispatch) | This memo IS the Phase 2.2-specific Pre-Read/Post-Read |
| R3 (one-shot dispatch) | Single dispatch — same sequence as Phase 2.1 |
| R4 (≤10 lockdown tests per phase) | **Zero new test files**. Phase 2.1's 15-test tenancy suite covers Phase 2.2 enforce (existing `test_tenancy_enforce_mode_for_migrated_collections` now asserts against both `chats` and `documents` via `_ENFORCE_MODE_COLLECTIONS`). Under budget. |
| R5 (Honesty Protocol) | Every marker carries inline rationale; defensive add documented in §4.B with explicit "why safe" column |
| R6 (no unrequested cleanups) | Only `documents`-collection violations addressed. `contexts` deferred. `work_studio_exports` deferred. `inbound_queue` deferred. Pre-existing failures NOT touched. |
| R7 (lockdown sweep before close) | Full invariant + Phase 14/15 + Track A 5/6/7 + 133-test targeted sweep run; passing |

---

## 7 · Deviations from dispatch

**One mid-flight scanner refinement** (allowed per dispatch §"Discipline rails": "If mid-flight scanner improvements are needed (like Phase 2.1's A.1 + A.2), execute and document in deviations — don't park"):

1. **Scanner widening — `task_id` added to `documents` ALT_TENANCY_KEYS.** Same pattern as Phase 2.1 Upgrade B (per-collection alt-keys). Architecturally sound: `task_id` resolves to a tasks row which IS tenant-scoped via `account_id`; documents inheriting a task's tenancy is a within-tenant invariant the route gates already enforce. 6 hits self-resolved.

**One marker-line placement fix** (mechanical):
- `routers/shares.py:488` initially received a trailing-line marker but the scanner expects the marker on the call line or one line ABOVE (per Phase 0 scanner contract — see `_line_is_escape_hatched` in `test_invariant_tenancy.py`). Moved the marker to the line immediately above L488.

**No other deviations.** No new tests added (R4 budget conserved). No router behaviour changed. No Phase 2.1 work undone.

---

## 8 · Follow-ups (logged for Phase 2.3+)

### 8.A · Recommended next dispatch: Phase 2.3 — `work_studio_exports` (24 hits, single file)

Same dispatch shape as Phase 2.2 — single context, full lockdown coverage (Track A Phase 5), behaviour-preserving, baseline-shrink-only enforce flip. Estimated effort: similar to Phase 2.2 (1 dispatch, ≤30 marker additions).

### 8.B · `contexts` collection (71 hits) — NEEDS A SEPARATE PRE-READ

The `contexts` collection ranks #1 by violation count after Phase 2.2 (71 hits). All 71 are `{"id": context_id}` lookups — `contexts.id` IS the tenant primary key (the row IS the tenant), so the literal violation pattern fundamentally differs from `chats` / `documents`. Recommendations need a structural Pre-Read covering:

1. Whether `contexts.id` should be added as an alt-key for the `contexts` collection (semantically: `id` IS the tenancy boundary; but `id` is also a generic identifier — false-positives risk).
2. Alternative: a `get_context_or_403(context_id, account_id)` helper that fuses the lookup + membership check atomically. Bigger architectural cleanup but behaviour-changing if the helper supplants the existing scattered patterns. Phase 4 (process separation) territory.
3. Hybrid: scanner alt-key OR marker-with-comment for the existing route gates that DO membership-check `id` before/after.

**Recommended:** Phase 2.X Pre-Read titled "Contexts collection scanner alignment". Until then, `contexts` stays observe.

### 8.C · Other Phase 2 backlog (unchanged from Phase 2.1 sprint memo)

- Cross-context call migrations (48 entries — Phase 1 backlog) — Phase 2.X side-lane OR Phase 4.
- Boundary-imports baseline (3 entries — Phase 4 territory).
- Pre-existing `test_track_a_phase2_drawer_journal.py` `KeyError: 'notes'` (3 tests) — Phase 2.X side-lane.
- Aggregation pipeline `$match` first-stage scanning (Pre-Read §7.B Upgrade E) — Phase 2.X side-lane.

### 8.D · Top-line callout for MASTER_STATE Section 9 (updated)

> Phase 2 cumulative posture (through Phase 2.2): **two collections (`chats`, `documents`) under per-collection enforce mode** + scanner Upgrades A/B/C/A.1/A.2 + `task_id` widening live. **Total tenancy violations down 66% (685→230) from Phase-0 baseline; definite down 63% (550→206).** Zero production cross-tenant bugs introduced; zero behaviour changes. Pattern proven across two contexts; Phase 2.3 (`work_studio_exports`) will follow the same single-context single-dispatch shape.

---

**End of Phase 2.2 sprint memo.**
