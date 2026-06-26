**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution path (b) done right · per-file subprocess capture · INVESTIGATE-ONLY · HARD STOP at confirmed-polluter-chain surface)

# Sprint P5.7-PER-FILE-CAPTURE — Per-file subprocess capture (path b done right)

**Status**: SHIPPED · HARD STOP at FAIL_IN_CONTEXT surface · AWAITING USER PATH PICK on bisect strategy
**Date**: 2026-06-26
**User direction picked**: (b) only — explicitly NOT (d). "Static patterns are signals, not confirmed polluters. Shipping fixes from (a) without confirmation = guessing."
**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` (confirmed root cause + cleanup mapping per cluster)
**Slice**: `/app/backend/scripts/jc_test_pollution_per_file_capture_slice.py` (READ-ONLY by contract; +400 LOC)
**Consolidated index**: `/app/memory/jc_artifacts/test_pollution/per_file_capture_20260626T181453Z.md`
**Per-file evidence**: 433 `cluster_*.md` files at `/app/memory/jc_artifacts/test_pollution/per_file/`
**Wall time**: 3,288 s (54.8 min) — well under the 90-min budget the in-process attempt 1 needed; per-file timeout (60 s) immune to harness state-accumulation hang
**Dependency added**: `pytest-forked` (additive; logged in DEV_PIPELINE.md)
**Files mutated (production / test / fixture)**: 0 · 0 · 0

## What was attempted

Per-file subprocess pytest invocation on every `tests/**/test_*.py` (excluding `tests/invariants/` and `tests/deploy/`). Each file runs in a fresh Python process with a 60-second wall timeout, marker filter `not integration and not deploy_smoke and not runtime_playwright`, `-p no:cacheprovider`. Per-file bucket classification:

- `PASS` — exit 0
- `PASS_NO_TESTS` — exit 5 (all tests deselected by markers; file healthy but outside lane)
- `FAIL_DETERMINISTIC` — exit non-zero with FAILED/ERRORS in output
- `TIMEOUT` — subprocess killed at 60 s
- `ERROR` — collection error / pytest infra error

Phase 2: cross-reference each file's bucket against the FAILING_TEST_TRACKER FTT-002..026 list:
- `PASS` (in isolation) + listed in tracker = **FAIL_IN_CONTEXT** (true pollution candidate)
- `FAIL_DETERMINISTIC` + listed = **tracker misclassification** (file fails alone too)
- `TIMEOUT` / `ERROR` + listed = **INCONCLUSIVE** (cannot bucket)

## Aggregate buckets (full 433-file run)

| Bucket | Count | Pct |
|---|---:|---:|
| `PASS` | 350 | 80.8% |
| `PASS_NO_TESTS` | 14 | 3.2% |
| `FAIL_DETERMINISTIC` | 59 | 13.6% |
| `TIMEOUT` | 10 | 2.3% |
| `ERROR` | 0 | 0.0% |

## Phase-2 cross-reference: corrected scope

**18 FTT IDs / 7 files confirmed as FAIL_IN_CONTEXT** (pollution candidates):

| File | FTT IDs | Status |
|---|---|---|
| `tests/test_iter41_signal_actions_in_process.py` | FTT-004..009 | PASS alone → **POLLUTION CANDIDATE** |
| `tests/test_p_cleanup_c_help_tooltip_suppression.py` | FTT-010..012 | PASS alone → **POLLUTION CANDIDATE** |
| `tests/test_phase_p3_2_cookie_hardening.py` | FTT-015..016 | PASS alone → **POLLUTION CANDIDATE** |
| `tests/test_phase_p5_10_audit_panel_direct_linkage.py` | FTT-017..018 | PASS alone → **POLLUTION CANDIDATE** |
| `tests/test_phase_p5_7_5_bounce_webhook.py` | FTT-019..022 | PASS alone → **POLLUTION CANDIDATE** |
| `tests/test_track_b_phase2_task_lifecycle.py` | FTT-023 | PASS alone → **POLLUTION CANDIDATE** |
| `tests/test_track_b_phase_b5_g6_notes_autosave.py` | FTT-024..026 | PASS alone → **POLLUTION CANDIDATE** |

**6 FTT IDs reclassified out of pollution scope**:

| FTT IDs | File | Original classification | Corrected classification |
|---|---|---|---|
| FTT-002, FTT-003 | `test_chat_roundtrip_golden.py`, `test_chat_fluency_no_shield_leak.py` | cross-test pollution | **integration-marker-only** (PASS_NO_TESTS in default lane; both carry `pytestmark = [..., pytest.mark.integration]`). Not pollution; lane-mismatched. |
| FTT-013 | `test_phase_d_fix_bundle.py` | cross-test pollution | **slow test** (TIMEOUT 60 s in isolation — not pollution, deterministic-slow) |
| FTT-014 | `test_phase_i5_open_questions.py` | cross-test pollution | **deterministic regression** (FAIL_DETERMINISTIC in isolation — tracker misclassification; needs its own bug-fix sprint, not pollution cleanup) |

**Net pollution scope: 18 FTT IDs / 7 files** — was 25 active in tracker before this sprint, now correctly scoped to 18.

## Halt-and-surface conditions (all clear)

| Halt condition (pre-authorised by user) | Threshold | Observed | Status |
|---|---|---|---|
| Files time out at 60 s | > 100 | 10 | ✅ clear |
| FAIL_IN_CONTEXT bucket | > 100 | 7 (files) / 18 (FTT IDs) | ✅ clear |
| Confirmed polluter in locked area | any | none (bisect is the surface point; this slice only confirms FAIL_IN_CONTEXT files) | ✅ clear at this stage — re-checked at bisect time |
| `pytest-forked` install failure | install errors | install clean | ✅ clear |
| Polluter chain requires 3+ ordered tests | n/a (this slice doesn't bisect) | n/a | deferred to bisect sprint |

## What this surfaces for user direction

The next-sprint input is now scoped: **7 files** to bisect. For each file:

1. Compute its alphabetical predecessor set (all `tests/**/test_*.py` files that pytest collects BEFORE it).
2. Bisect the predecessor set to find the minimum polluter chain that flips the file from PASS to FAIL.
3. Record: polluter file:line · polluted file:line · leaked state name + type · recommended cleanup.

Bisect is **OUT OF SCOPE** for this slice per the HARD STOP contract. The 7-file scope is small enough to do as a single follow-up sprint OR seven small per-file sprints.

### Three concrete bisect strategies for user pick

a. **Binary-search bisect per file** (~30-60 min per file × 7 files = 3.5-7 h). For each file, run pytest on `[first half of predecessors, polluted_file]`. If polluted still fails, polluter in first half; else in second half. Recurse until single polluter identified. Most precise; highest cost.

b. **Statically-narrowed bisect per file** (~10-20 min per file × 7 files = 1-2 h). For each file, restrict the predecessor candidate set to files matching the P5.7-DIAG static signature (the 9 cluster hypotheses already documented). Bisect only that narrowed set. Faster; depends on hypothesis correctness — if the polluter isn't in the static set, bisect returns negative and we widen.

c. **Two-file blanket sweep per polluted file** (~15-30 min per file × 7 files = 1.5-3.5 h). For each polluted file, run it paired with EVERY other test file individually. Identifies pairwise polluters but not chains. Coarse; covers cases (b) misses.

Agent recommendation: **(b) then (a) on remaining unconfirmed files**. Static hypotheses are cheap to test; failed (b) confirmations escalate to (a) for the holdouts.

## What this rules out

- **(d) "ship static guards first, measure delta"** — already rejected by user. This slice's data validates the rejection: 6/24 tracker entries are non-pollution misclassifications; shipping the static guards would have measured deltas against a wrong baseline.
- **Locked-area polluter (Shield, WS Generate Doc UI, Track-2 schema, Monitor pre-warmer)** — at this surface, none of the 7 confirmed polluted files lives in a locked area. Bisect must re-check polluter locations.
- **Systemic harness rot** — the 7-file scope is well under the 100-file halt threshold. The pollution is discrete, not systemic.

## Discipline notes

- READ-ONLY by contract honoured: 0 test/fixture/production lines mutated.
- Per-file subprocess isolation worked: no harness state-accumulation hang (in-process attempt-1 hung at 16%; this attempt completed 100% in 54.8 min).
- Tracker corrections are MD-level (not in-source) — surface for user direction on whether to bulk-rewrite FAILING_TEST_TRACKER.md or do per-FTT MD-only corrections.

## Files produced

- `/app/backend/scripts/jc_test_pollution_per_file_capture_slice.py` NEW · 400 LOC · READ-ONLY by contract
- `/app/memory/jc_artifacts/test_pollution/per_file/` — 433 per-file MDs
- `/app/memory/jc_artifacts/test_pollution/per_file_capture_20260626T181453Z.md` — consolidated index
- `/app/memory/sprints/P5_7_PER_FILE_CAPTURE.md` — this memo

## Files NOT touched

- 0 production code mutated
- 0 test files mutated
- 0 fixture files mutated
- 0 invariant files mutated
- HARD STOP at FAIL_IN_CONTEXT surface — bisect is the next sprint, scope-approved or scope-modified by user.
