**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution bisect · statically-narrowed predecessor search · HARD STOP at confirmed-pair surface)

# Sprint P5.7-BISECT — statically-narrowed polluter→polluted pair search

**Status**: SHIPPED · HARD STOP at confirmed-pair surface · AWAITING USER SCOPE APPROVAL on fix sprint
**Date**: 2026-06-26
**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` — every polluter→polluted pair MUST be confirmed dynamically by paired pytest execution; static cluster signatures are SEARCH HEURISTICS only, not fixes
**Slice**: `/app/backend/scripts/jc_pollution_bisect_slice.py` — READ-ONLY by contract; +600 LOC
**Consolidated index**: `/app/memory/jc_artifacts/test_pollution/bisect_20260626T192013Z.md`
**Confirmed-pair evidence**: 4 MDs at `/app/memory/jc_artifacts/test_pollution/confirmed_pairs/`
**Wall time**: 1636 s (27.3 min) — under budget
**Files mutated (production / test / fixture)**: 0 · 0 · 0

## Discipline pull-up (verbatim per user direction)

> "The static cluster hypotheses are NOT being used as the fix — they're being used as a SEARCH HEURISTIC for the bisect. Every polluter→polluted pair must still be confirmed dynamically by paired pytest invocation."

Honoured: every pair below was found via static-signature narrowing of the predecessor candidate set, then validated by a `pytest <candidate> <polluted>` subprocess invocation that observed `FAILED <polluted_file>` in stdout. Each confirmed pair was also sample-rechecked (re-run once) for subprocess consistency before the evidence MD was emitted.

## 4 confirmed polluter→polluted pairs

| # | Polluter | Polluted | Cluster | FTT IDs | Pair dur. | Locked? |
|--:|----------|----------|---------|---------|----------:|:-------:|
| 1 | `tests/test_phase4_2_http_transport_smoke.py` | `tests/test_phase_p3_2_cookie_hardening.py` | env_or_motor_loop_state__p3_2 | FTT-015, FTT-016 | 6.68 s | no |
| 2 | `tests/test_phase4_2_http_transport_smoke.py` | `tests/test_phase_p5_10_audit_panel_direct_linkage.py` | env_or_motor_loop_state__p5_10 | FTT-017, FTT-018 | 5.33 s | no |
| 3 | `tests/test_phase4_2_http_transport_smoke.py` | `tests/test_phase_p5_7_5_bounce_webhook.py` | sendgrid_env_stub_leak | FTT-019, FTT-020, FTT-021, FTT-022 | 5.27 s | no |
| 4 | `tests/test_phase_p5_10_audit_panel_direct_linkage.py` | `tests/test_track_b_phase2_task_lifecycle.py` | tenant_resolver_stub_leak | FTT-023 | 6.04 s | no |

## Key diagnostic insight

**ONE file — `tests/test_phase4_2_http_transport_smoke.py` — is the polluter in 3 of the 4 confirmed pairs.** That single file is responsible for **8 of the 10 confirmed-bisect FTT IDs** (FTT-015..022). The fourth pair is tiered: `test_phase_p5_10_audit_panel_direct_linkage.py` (itself polluted by `test_phase4_2_http_transport_smoke.py`) acts as a polluter for `test_track_b_phase2_task_lifecycle.py`.

Inspection of the per-file-capture evidence reveals an additional sub-finding: **`test_phase4_2_http_transport_smoke.py` is FAIL_DETERMINISTIC in isolation TOO** (its `test_internal_transport_openapi_hash_unchanged` fails alone, exit 1). The file has a DUAL IDENTITY:

1. **Deterministic regression** — its own test fails when run in isolation (recorded as such in the per-file capture)
2. **Polluter** — it mutates global state (likely env vars, given the env-cluster signature hits) that breaks downstream tests when the broad-suite runs

Fixing this one file therefore should deliver a double benefit: closes its own deterministic failure + stops the env leak that breaks 8 FTT IDs downstream.

**FTT-023's polluter being itself-polluted (tiered pollution)** is the strongest evidence that the env leak from `test_phase4_2_http_transport_smoke.py` cascades — the env state polluted into `phase_p5_10` then re-emerges as a different shape when `phase_p5_10` runs the tenant-resolver dependency override.

## 2 holdouts (for full-(a) binary search next sprint)

| Cluster | File | FTT IDs | Candidates tried | Why holdout |
|---|---|---|---:|---|
| `dependency_overrides_leak` | `tests/test_p_cleanup_c_help_tooltip_suppression.py` | FTT-010, FTT-011, FTT-012 | 8 | Polluter not in the static-signature set; needs widened predecessor scan |
| `autosave_debounce_timer_leak` | `tests/test_track_b_phase_b5_g6_notes_autosave.py` | FTT-024, FTT-025, FTT-026 | 30 | Polluter not in the static-signature set even at max cap; needs full binary search across remaining predecessors |

These two files PASS in isolation (per-file capture confirmed) AND fail in the broad-suite — so pollution is real — but the polluter does not match the cluster's static signature, OR the polluter requires 3+ ordered tests rather than a single pairwise polluter. Full-(a) binary search on the alphabetical predecessor set will identify them.

## 1 intra-file cluster (separate sprint shape)

| Cluster | File | FTT IDs | Shape |
|---|---|---|---|
| `shared_fixture_state_iter41` | `tests/test_iter41_signal_actions_in_process.py` | FTT-004..009 | Six tests in the SAME FILE pollute each other; predecessor-search across other files does not apply. Requires per-test-pair invocation WITHIN the file to identify which test in iter41 mutates state read by which other. Different sprint shape. |

## Halt-and-surface conditions (all clear)

| Condition (pre-authorised) | Status |
|---|---|
| confirmed polluter in a locked area (Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer) | ✅ clear (all 4 confirmed polluters live outside locked areas) |
| polluter chain requires 3+ tests in order (not pairwise) | partially detected as the 2 holdouts (where no pairwise polluter found); surfaced for next sprint, NOT halted at this stage because the holdout bucket is the correct disposition |
| pytest-subprocess inconsistency on a confirmed pair | ✅ clear (every confirmed pair passed sample-recheck) |
| shared_fixture_state_iter41 cluster surfaces separately | ✅ surfaced as intra-file (separate sprint shape) |

## What this surfaces for user direction (HARD STOP)

The 4 confirmed polluter→polluted pairs are concrete, reproducible, and locality-clean (no locked-area collisions). The next sprint is a FIX sprint, but per the HARD STOP contract:

> "No fix attempts on confirmed pairs without user (or my judgment on user's behalf) scope approval. The fix scope decision needs the confirmed pair list visible."

### Three concrete fix-scope options for user pick

a. **Single-file surgical fix on `test_phase4_2_http_transport_smoke.py`** (~30-90 min). Investigate the env mutations causing the downstream cluster failures. Add proper teardown (or replace with `monkeypatch.setenv`). Closes 8 FTT IDs in one sprint + closes the deterministic regression on its own test. Highest-leverage move.

b. **All-4-pairs cleanup sprint** (~2-4 h). Fix the (a) above, AND patch `test_phase_p5_10_audit_panel_direct_linkage.py` so it no longer leaks tenant resolver state into `test_track_b_phase2_task_lifecycle.py` (FTT-023). Closes all 10 currently-confirmed FTT IDs.

c. **Defer the fix sprint; investigate holdouts first**. Run (a) binary search on the 2 holdouts (`test_p_cleanup_c_help_tooltip_suppression.py` and `test_track_b_phase_b5_g6_notes_autosave.py`) to identify ALL polluters before committing to any cleanup. Resolves whether the holdouts have polluters in the same `test_phase4_2_http_transport_smoke.py` (which would consolidate all 16 external-pollution FTT IDs to a single fix) or distinct polluters.

Agent recommendation: **(c) first, then (b)**. The holdouts may consolidate to the same polluter; binary search is cheap (~30 min per holdout = 1 h total) and de-risks the fix scope.

## Discipline notes

- Static cluster signatures used ONLY as search heuristics — never as the fix decision. Every confirmed pair was validated by real paired pytest execution.
- Sample-recheck ran on every confirmed pair; 0 subprocess inconsistencies detected.
- Locked-area polluter check ran on every confirmed pair; 0 locked-area collisions.
- 0 LOC mutated; READ-ONLY contract honoured.
- HARD STOP at the confirmed-pair surface — fix sprint awaits user scope direction.

## Files produced

- `/app/backend/scripts/jc_pollution_bisect_slice.py` (+600 LOC · READ-ONLY by contract)
- `/app/memory/jc_artifacts/test_pollution/confirmed_pairs/` — 4 confirmed-pair MDs
- `/app/memory/jc_artifacts/test_pollution/bisect_20260626T192013Z.md` — consolidated index
- `/app/memory/sprints/P5_7_BISECT.md` — this memo

## Files NOT touched

- 0 production code mutated
- 0 test files mutated
- 0 fixture files mutated
- 0 invariant files mutated
- HARD STOP at confirmed-pair surface honoured
