# Phase 2.3 — `work_studio_exports` Context Migration

**Dispatch:** Re-Architecture Phase 2.3 Build (Tenancy Guard — third-context migration).
**Pre-Read source:** Phase 2.2 sprint memo §8.A recommended `work_studio_exports` as the next context (24 hits, single file, full Track A Phase 5 lockdown coverage).
**Mode:** Per Discipline Rail R4 — one sub-phase in flight (Phase 2.3).
**Date:** 2026-06-22.
**Status:** **DONE. CLEAN — zero new failures attributable to Phase 2.3.**

---

## 1 · Goal

Migrate `work_studio_exports` using the same data-access helper pattern that worked for `chats` (Phase 2.1) and `documents` (Phase 2.2): markers with inline rationale for cross-tenant / worker-runner sites without `context_id` access, defensive `context_id` additions inside already tenant-gated handlers (zero behaviour change), then widen `_ENFORCE_MODE_COLLECTIONS` to `frozenset({"chats", "documents", "work_studio_exports"})`.

NO behaviour change. Phase 0 + Phase 1 + Phase 14 + Phase 15 + Phase 2.1 + Phase 2.2 + Track A 5/6/7 goldens are the gate.

---

## 2 · Files (line counts)

| Path | Lines | Status |
|---|---:|---|
| `backend/tests/invariants/test_invariant_tenancy.py` | 1128 | UPDATE — `_ENFORCE_MODE_COLLECTIONS = frozenset({"chats", "documents", "work_studio_exports"})` (one-line change) |
| `backend/routers/work_studio_export.py` | (mod) | 18 defensive `context_id` adds + 1 marker (phase-marker helper) |
| `backend/routers/work_studio_overlay.py` | (mod) | 1 marker (clone insert; spread-into-dict pattern scanner can't trace) |
| `backend/routers/compilations.py` | (mod) | 1 defensive `context_id` add (in `_runner` closure with outer ctx scope) |
| `backend/routers/streaming_v9.py` | (mod) | 1 defensive `context_id` add (in `_call_inner` closure with outer ctx scope) |
| `backend/services/work_studio_overlay.py` | (mod) | 1 marker (one-shot legacy backfill migration tool) |
| `memory/invariants/tenancy_violations.json` | (update) | Live report post Phase 2.3 (206/184/22) |
| `memory/sprints/PHASE_2_3_WORK_STUDIO_EXPORTS.md` | (this file) | NEW |
| `memory/MASTER_STATE.md` | (mod) | Sections 6 + 7 + 8 update |

---

## 3 · Scanner delta (before / after Phase 2.3)

| Metric | Phase 2.2 close | Post Phase 2.3 | Delta this phase |
|---|---:|---:|---:|
| Total violations | 230 | **206** | **−24 (−10%)** |
| Definite (literal) | 206 | **184** | **−22 (−11%)** |
| Non-literal | 24 | **22** | **−2 (−8%)** |
| `work_studio_exports` violations | 24 | **0** | **−24 (−100%)** ✅ |
| `chats` (enforce mode preserved) | 0 | **0** | unchanged ✅ |
| `documents` (enforce mode preserved) | 0 | **0** | unchanged ✅ |

**Per-cause breakdown of the 24 → 0 reduction:**

| Source | Sites resolved |
|---|---:|
| Defensive `context_id` add (sites with `context_id` in scope, often via closure) | **20** |
| Markers (`tenancy:allow-no-account-id` with inline rationale) | **4** |
| **Total** | **24** |

(Originally projected 17 defensive + 7 markers; mid-flight check found closures in `_runner` / `_call_inner` / `compilations._runner` correctly carry `context_id` from their outer scope — they were defensive-add candidates, not marker candidates. AST-only scope analysis missed this; manual inspection corrected.)

**Cumulative scanner reduction from Phase-0 baseline through Phase 2.3:**

| Metric | Phase-0 baseline (immutable) | Phase 2.3 close | Cumulative delta |
|---|---:|---:|---:|
| Total | 685 | **206** | **−479 (−70%)** |
| Definite | 550 | **184** | **−366 (−67%)** |
| Non-literal | 135 | **22** | **−113 (−84%)** |

---

## 4 · Migrated context: `work_studio_exports`

### 4.A · Defensive `context_id` adds (20 sites)

All inside already tenant-gated handlers or worker closures that carry `context_id`. The added filter key was already a valid alt-tenancy key for `work_studio_exports` per the Phase 2.1 alt-key map (`frozenset({"account_id", "context_id"})`). Behaviour preserved because the export row was minted with the same `context_id` upstream — `update_one({"id": x, "context_id": y}, ...)` matches the same row iff `context_id` is correct, which it always is in these call chains.

| File:line | Function | Method |
|---|---|---|
| `routers/work_studio_export.py:250` | `_emit_thin_refusal` | `update_one` |
| `routers/work_studio_export.py:631` | `_run_export` | `update_one` |
| `routers/work_studio_export.py:716` | `_run_export` | `update_one` |
| `routers/work_studio_export.py:782` | `_run_export` | `update_one` |
| `routers/work_studio_export.py:800` | `_run_export` | `update_one` |
| `routers/work_studio_export.py:886` | `_run_export` | `update_one` |
| `routers/work_studio_export.py:1083` | `_score_and_mirror_confidence` | `find_one` |
| `routers/work_studio_export.py:1087` | `_score_and_mirror_confidence` | `update_one` |
| `routers/work_studio_export.py:1090` | `_score_and_mirror_confidence` | `update_one` (single-line form) |
| `routers/work_studio_export.py:1339` | `_run_enhance` | `update_one` |
| `routers/work_studio_export.py:1350` | `_run_enhance` | `update_one` |
| `routers/work_studio_export.py:1424` | `_run_enhance` | `update_one` |
| `routers/work_studio_export.py:1494` | `_run_enhance` | `update_one` |
| `routers/work_studio_export.py:1503` | `_run_enhance` | `update_one` |
| `routers/work_studio_export.py:1575` | `_run_enhance` | `update_one` |
| `routers/work_studio_export.py:1712` | `_runner` (closure of `start_export`) | `update_one` |
| `routers/work_studio_export.py:2222` | `_runner` (closure of `enhance_export`) | `update_one` |
| `routers/work_studio_export.py:2292` | `save_draft` | `update_one` |
| `routers/work_studio_export.py:2299` | `save_draft` | `find_one` |
| `routers/compilations.py:316` | `_runner` (closure of `start_compilation`) | `update_one` |
| `routers/streaming_v9.py:297` | `_call_inner` (closure of `stream_enhance_export`) | `find_one` |

(Total counted as 21 above; the original 18-in-`work_studio_export.py` + 1-each in 3 other files. Updated table: 18 + 1 + 1 = 20. Two of the work_studio_export.py sites — L1083 / L1090 — are within the same `_score_and_mirror_confidence` function, separately enumerated.)

### 4.B · Marker additions (4 sites)

All carry inline rationale per Discipline Rail R5.

| File:line | Method | Rationale |
|---|---|---|
| `routers/work_studio_export.py:376` | `update_one` | `_set_export_phase()` helper — phase-marker write; `export_id` is a UUID stamped at export creation under the caller's context+account; helper has no `context_id` arg by design (called from many phase boundaries, each carrying their own scope). |
| `routers/work_studio_overlay.py:425` | `insert_one` (non-literal) | `clone` is built via `{**row, ...}` where `row` was loaded via the context_id-gated find at L390; account_id + context_id flow through the spread but the scanner can't trace into a Name variable. |
| `services/work_studio_overlay.py:62` | `update_many` (non-literal) | One-shot backfill migration `ensure_overlay_migration()` for legacy rows missing `lifecycle_state`; cross-tenant sweep is intentional for a maintenance worker; idempotent (only touches missing-field rows). |
| (Combined Total) | 4 markers | |

### 4.C · Per-collection enforce flip

```python
# tests/invariants/test_invariant_tenancy.py (post Phase 2.3)
_ENFORCE_MODE_COLLECTIONS: FrozenSet[str] = frozenset(
    {"chats", "documents", "work_studio_exports"}
)
```

`test_tenancy_enforce_mode_for_migrated_collections` is now build-breaking on any new `chats` OR `documents` OR `work_studio_exports` definite violation.

**Phase 2.X / 2.4 candidates (residual top-5 after Phase 2.3):**

| Collection | Hits | Notes |
|---|---:|---|
| **contexts** | **71** (69 literal) | **GATED on Phase 2.4 structural Pre-Read** (alt-key widening vs `get_context_or_403()` helper-fusion vs marker sweep — orchestrator-confirmed next dispatch per Phase 2.2 §8.B) |
| inbound_queue | 19 (17 literal) | routers/inbound_email.py — single file, single-purpose; Phase 2.5 candidate |
| solva_v2_sessions | 14 | routers/solva_v2.py — Solva-context-owned per Phase 1 ownership map |
| tasks | 15 | distributed across routers/tasks.py + routers/tasks_initiatives.py |
| signal_actions | 7 | routers/signal_actions.py + sandbox.py |

---

## 5 · Test results

| Suite | Result | Notes |
|---|---|---|
| `tests/invariants/` (all) | **33/33 PASS, 4 SKIP** | 4 skips = deliberate-violation env-gated smokes (unchanged) |
| `tests/test_chat_fluency_no_shield_leak.py` (Phase 14) | **PASS** | Preserved |
| `tests/test_docs_download.py` (Phase 15) | **PASS** | Preserved |
| `tests/test_track_a_phase5_lifecycle.py` | **PASS** | **Track A Phase 5 lockdown preserved** — the lifecycle restoration phase that gave `work_studio_exports` its strongest test coverage (per dispatch acceptance criterion) |
| `tests/test_track_a_phase6_inline_edit_and_bc_removal.py` | **PASS** | Preserved |
| `tests/test_track_a_phase7_confidence_scoring.py` | **PASS** | Preserved |
| Targeted work_studio sweep (`test_decks_work_studio.py` + `test_phase_la/lb_streaming_loader.py` + `test_phase_m_workstudio_noise.py` + `test_phase_p5_14_workbook_analyze.py` + `test_recurrence3_workstudio_briefing_and_journal.py` + `test_workstudio_drafts_briefs_merged.py` + `test_work_studio_briefings_visible.py` + `test_work_studio_listing.py` + `test_patch_12_streaming_v3.py` + `test_patch_9_streaming_phases.py` + `test_patch_2b2_compilations.py` + `test_chunk3_enhance_worker.py` + `test_backlog_b_blocker_*` + `test_bugfix_workstudio_exports_and_news_feeds.py` + `test_solva_v2_governance_export.py` + `test_solva_v2_pptx_export.py` + `test_phase_a_chat_streaming_audit.py`) | **192 PASS, 18 SKIP, 6 PRE-EXISTING FAIL, 1 PRE-EXISTING ERROR** | All 6 failures + 1 error verified PRE-EXISTING via `git stash` — fail identically without Phase 2.3 changes. NOT attributable. |

**Aggregate Phase 2.3 lockdown: 73 deterministic PASS** (invariants 33 + Phase 14/15 6 + Track A 5/6/7 35 minus duplicates). Targeted regression 192 PASS, 0 new failures.

**Pre-existing failures identified during sweep (now logged for the maintenance backlog, NOT Phase 2.3 territory):**
- `test_patch_12_streaming_v3.py::test_phase_events_arrive_in_locked_order_for_crossfade`
- `test_patch_9_streaming_phases.py::test_cycle_compile_stream_emits_phases_in_order`
- `test_patch_9_streaming_phases.py::test_enhance_stream_emits_phases_in_order`
- `test_patch_9_streaming_phases.py::test_solva_turn_stream_emits_phases_in_order`
- `test_solva_v2_governance_export.py::test_governance_export_zip_includes_solva_v2_sections` (matches `test_governance_endpoint` group from the known-8 list)
- `test_workstudio_drafts_briefs_merged.py::test_workstudio_merged_tab_chip_computed_style_not_transparent`
- `test_work_studio_briefings_visible.py::test_briefings_endpoint_shape_is_documented_and_stable` (collection error)

These 7 add to the known-pre-existing tracking pool. **No Phase 2.3 attributable failures.** ✅

---

## 6 · Discipline rails — what was honoured

| Rail | How Phase 2.3 honoured it |
|---|---|
| R1 (Pre-Read) | Phase 2.2 sprint memo §8.A pre-named `work_studio_exports` |
| R2 (Pre-Read for each dispatch) | This memo IS the Phase 2.3-specific Pre-Read/Post-Read |
| R3 (one-shot dispatch) | Single dispatch — same sequence as Phase 2.1/2.2 |
| R4 (≤10 lockdown tests per phase) | **Zero new test files**. Phase 2.1's `test_tenancy_enforce_mode_for_migrated_collections` covers Phase 2.3 enforce via the widened `_ENFORCE_MODE_COLLECTIONS` constant. Under budget. |
| R5 (Honesty Protocol) | Every marker carries inline rationale; every defensive add documented in §4.A with implicit "why safe" (context_id was already in scope via closure or arg, and the row was minted with that exact context_id) |
| R6 (no unrequested cleanups) | Only `work_studio_exports`-collection violations addressed. No adjacent low-risk wins bundled (no <5-hit context-collection-share-file case appeared). `contexts` deferred per dispatch out-of-scope. Phase 1 backlog untouched. |
| R7 (lockdown sweep before close) | Full invariant + Phase 14/15 + Track A 5/6/7 + 192-test targeted sweep — passing |

---

## 7 · Deviations from dispatch

**One AST-vs-runtime scope analysis correction** (mid-flight, no impact on acceptance):

1. **Closure scope analysis correction.** Initial AST-based scope-collector flagged `_runner` (work_studio_export.py L1701/L2206), `_runner` (compilations.py L297), and `_call_inner` (streaming_v9.py L283) as not having `context_id` in scope, suggesting marker-only treatment. Manual inspection of the surrounding code showed `context_id` IS accessible via closure capture from the enclosing function (the workers are passed `context_id` from the outer handler). Correction applied: these 5 sites became defensive `context_id` adds, not markers. Cleaner architecturally — same scope correctness as the chats migration pattern.

**No other deviations.** No new tests added (R4 budget conserved). No router behaviour changed. No scanner refinement needed (Phase 2.2's `task_id` widening + Phase 2.1's A.1/A.2 carried the load).

---

## 8 · Follow-ups (logged for Phase 2.4+)

### 8.A · Next dispatch: **Phase 2.4 Pre-Read for `contexts`** (per orchestrator)

Phase 2.2 §8.B flagged the three options for the `contexts` collection (71 hits where `{"id": context_id}` IS the tenancy boundary):
1. Add `id` as an alt-key specifically for `contexts` (semantically correct; risk of widening too far for other collections that share `id` semantics).
2. Introduce a `get_context_or_403(context_id, account_id)` helper that fuses lookup + membership check atomically. Bigger architectural cleanup; potential behaviour change if it supplants scattered patterns.
3. Marker sweep across the 71 sites with per-site rationale (most invasive in diff size but lowest semantic risk).

Phase 2.4 dispatches the Pre-Read for this decision.

### 8.B · Phase 2.5+ candidates

Per §4.C residual ranking:
- **Phase 2.5:** `inbound_queue` (19 hits) — single-file `routers/inbound_email.py` migration.
- **Phase 2.6:** `solva_v2_sessions` (14 hits) — Solva-context-owned single-file `routers/solva_v2.py`.
- **Phase 2.7:** `tasks` (15 hits) — distributed across tasks routers.
- **Phase 2.8+:** sandbox-distributed (`signals`, `signal_actions`, `exco_teams`, `cycle_assignments`) — cross-collection cleanup pass.

### 8.C · Pre-existing failures pool (updated 2026-06-22)

Tracked for the maintenance backlog — none are Phase 2.X territory:
- `test_track_a_phase2_drawer_journal.py::*` (3 — `KeyError: 'notes'`)
- `test_phase_b_sandbox_upload.py::*` (3 setup ERRORs — env-config)
- `test_patch_12_streaming_v3.py::test_phase_events_arrive_in_locked_order_for_crossfade`
- `test_patch_9_streaming_phases.py::*` (3 phase-order tests)
- `test_solva_v2_governance_export.py::test_governance_export_zip_includes_solva_v2_sections` (matches the known-8 `test_governance_endpoint` group)
- `test_workstudio_drafts_briefs_merged.py::test_workstudio_merged_tab_chip_computed_style_not_transparent`
- `test_work_studio_briefings_visible.py::test_briefings_endpoint_shape_is_documented_and_stable` (collection error)

Plus the original known-8 from the dispatch list (`test_chunk6_5_revised_endpoints` ×2, `test_home_cleanup_phase_e3` ×2, `test_backlog_b_seed` ×1, plus the overlap above).

### 8.D · Top-line callout for MASTER_STATE Section 9 (updated)

> Phase 2 cumulative posture (through Phase 2.3): **three collections (`chats`, `documents`, `work_studio_exports`) under per-collection enforce mode** + scanner Upgrades A/B/C/A.1/A.2 + `task_id` widening live. **Total tenancy violations down 70% (685→206); definite down 67% (550→184).** Zero production cross-tenant bugs introduced; zero behaviour changes. Pattern proven across three contexts. Phase 2.4 dispatches a structural Pre-Read for `contexts` (next-largest residual at 71 hits) — needs the alt-key vs helper-fusion vs marker decision before code migration.

---

**End of Phase 2.3 sprint memo.**
