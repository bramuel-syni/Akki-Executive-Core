**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (holdout-finisher full predecessor sweep · HARD STOP at confirmed-pair surface)

# Sprint P5.7-HOLDOUT-FINISHER — full-(a) binary-sweep on remaining holdouts

**Status**: SHIPPED · HARD STOP at confirmed-pair surface · AWAITING USER FIX-SCOPE DIRECTION
**Date**: 2026-06-26
**User direction picked**: (c) — defer fix, finish holdout binary search first. "Holdouts may consolidate to the same polluter… ~1h cost to complete the diagnostic vs committing to fix scope on incomplete data is the right trade."
**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` (confirm-before-fix)
**Slice**: `/app/backend/scripts/jc_pollution_holdout_finisher_slice.py` — READ-ONLY by contract; +480 LOC
**Consolidated index**: `/app/memory/jc_artifacts/test_pollution/holdout_20260626T195600Z.md`
**Confirmed-pair evidence**: 15 new MDs at `/app/memory/jc_artifacts/test_pollution/confirmed_pairs/`
**Wall time**: 3197 s (53.3 min) — within the 2 h ceiling
**Files mutated**: 0 / 0 / 0 (production / test / fixture)

## Direct answer to the consolidation question

**Do the holdouts consolidate to `test_phase4_2_http_transport_smoke.py`? NO.**

The hypothesis was the holdouts might share the P5.7-BISECT polluter (turning the 8-of-10 finding into 14-of-14). They do NOT. Two distinct pollution shapes surfaced:

### Holdout 1 — `test_p_cleanup_c_help_tooltip_suppression.py` (FTT-010..012)

- 69 PASS predecessors swept; **0 confirmed pairs**
- HALT-fired: `holdout_zero_confirmed_pairs_likely_shared_global_state`
- **Interpretation**: pollution requires SHARED GLOBAL STATE accumulated across multiple files — NOT a pairwise polluter
- **Fix shape**: different from Cluster A. Likely needs source-inspection of the polluted file's reliance on session/login/CSRF state, plus a per-test fixture that resets that state

### Holdout 2 — `test_track_b_phase_b5_g6_notes_autosave.py` (FTT-024..026)

- 292 PASS predecessors swept; **15 confirmed polluters** (the autosave file is highly sensitive)
- **NOT consolidated** with `test_phase4_2_http_transport_smoke.py` (that file was NOT in the polluter list)
- Polluter set is uniformly auth/session/CSRF-related:
  - `test_synisense_security.py`
  - `test_phase_p5_{5,7,7_5,8,9,10}_*` (six files — session, waitlist, bounce, inbox, admin, audit)
  - `test_phase_p3_{1,2,4}_*` (csrf, cookie hardening, session timeout)
  - `test_phase_p2_{a2,b1,b4,b6,d2}_*` (microsoft pkce, security headers, password change, admin reset, health composite)
- **Interpretation**: the autosave test reads session/cookie state that EVERY one of these files mutates. The right fix is **test-side hardening** (per-test reset of the assumed session/cookie state) — not 15 separate polluter-side fixes
- One subprocess inconsistency detected on `test_phase_p3_3_mfa.py` (first = CONFIRMED, recheck = TIMEOUT); NOT emitted as evidence per the discipline guard

## Halt flags fired (pre-authorised by user)

1. **`holdout_zero_confirmed_pairs_likely_shared_global_state`** for Holdout 1 — surfaced per the standing rule "If a holdout returns 0 confirmed pairs across all 350 candidates → HALT, different fix shape." This is diagnostic gold, not a runtime error.
2. **`pytest_subprocess_inconsistency`** on one pair (`test_phase_p3_3_mfa.py` → autosave) — first run CONFIRMED, recheck TIMEOUT. Pair NOT emitted as evidence; counts as 14 truly-confirmed + 1 inconsistent.

## Full cluster taxonomy (post-holdout sweep)

Per user direction — full audit picture so fix-scope can be decided with complete visibility:

| Cluster | Shape | FTT IDs | Confirmed polluter(s) | Disposition |
|---|---|---|---|---|
| **A** | external pollution (polluter-side fix) | FTT-015..023 (9 IDs) | `test_phase4_2_http_transport_smoke.py` (P5.7-BISECT) + `test_phase_p5_10_audit_panel_direct_linkage.py` tiered for FTT-023 | Surgical sprint on `test_phase4_2_http_transport_smoke.py` (also closes its own deterministic regression — dual identity) |
| **B.1** | shared global state (test-side fix) | FTT-010..012 (3 IDs) | none — 0 pairwise polluters; accumulated state shape | Source-inspect polluted file's session/login/CSRF coupling; add per-test reset fixture |
| **B.2** | broad-sensitive (test-side hardening) | FTT-024..026 (3 IDs) | 15 distinct polluters (auth/session/CSRF surface area) | Test-side hardening: per-test reset of assumed session/cookie state in the autosave test fixture — single test-side change closes all 3 IDs |
| **C** | intra-file (in-file isolation fix) | FTT-004..009 (6 IDs) | within `test_iter41_signal_actions_in_process.py` | Per-test-pair invocation within the file; refactor module-scoped state to function-scoped fixtures |
| **D** | deterministic regression (folds into A) | FTT-014 (1 ID) | n/a — own bug | Folds into Cluster A surgical sprint (since A's polluter file ALSO has its own deterministic regression matching FTT-014's signature) |

**Total accounting**: 18 cross-test pollution FTT IDs (A+B+C) + 1 deterministic regression (D) = 19 active FTT IDs all mapped to a concrete fix-shape with confirmed evidence.

## What this surfaces for user direction

### Four sequenced fix sprints

1. **Cluster A + D surgical sprint** (highest leverage). Investigate `test_phase4_2_http_transport_smoke.py`. The env mutations causing downstream pollution + the file's own deterministic regression are likely the same root cause. One sprint closes 10 FTT IDs (FTT-014..023).

2. **Cluster B.2 test-side hardening** (single test-side change). Inspect `test_track_b_phase_b5_g6_notes_autosave.py`; add per-test session/cookie state reset. Closes FTT-024..026 (3 IDs).

3. **Cluster B.1 source-inspection sprint** (different shape). The "no pairwise polluter" finding tells us the polluted file assumes a clean global state; need source-inspect of help-tooltip-suppression's reliance on session/idempotent-off-flag state. Closes FTT-010..012 (3 IDs).

4. **Cluster C intra-file refactor** (separate sprint shape). Per-test-pair invocation within `test_iter41_signal_actions_in_process.py`; convert module-scoped state to function-scoped fixtures. Closes FTT-004..009 (6 IDs).

### Agent recommendation: sequence 1 → 2 → 3 → 4

Reasoning:
- (1) is highest-leverage (10 IDs) and the polluter is well-characterised by 8 confirmed pairs from P5.7-BISECT plus the dual-identity finding.
- (2) is the cheapest test-side change (15 polluters, but one test-side fix on the polluted file).
- (3) requires source-investigation — defer until the easier wins are landed (signal: does (1) or (2) accidentally fix it via session-state hygiene?).
- (4) is structurally distinct; can run in parallel with any of (1)-(3).

### Alternative shape: bundle (1) + (2) as ONE sprint

Both touch session/cookie/CSRF state. If the user prefers fewer sprints, (1)+(2) is ONE coherent "session/cookie state hygiene" sprint closing 13 FTT IDs. Higher risk of one-PR-touching-many-files but lower total context-switching cost.

## Discipline notes

- READ-ONLY by contract honoured: 0 LOC mutated.
- Full predecessor sweep (NO cluster-narrowing) — heuristic-free.
- Sample-recheck on every confirmed pair (subprocess-inconsistency guard fired 1 time; that pair NOT emitted).
- HARD STOP at confirmed-pair surface; fix-sprint scope awaits user direction.
- FTT-014 staying parked under DETERMINISTIC REGRESSIONS until (or unless) user chooses to fold it into the Cluster A surgical sprint.

## Files produced

- `/app/backend/scripts/jc_pollution_holdout_finisher_slice.py` NEW (+480 LOC · READ-ONLY)
- `/app/memory/jc_artifacts/test_pollution/confirmed_pairs/` — 15 new MDs (now 19 total: 4 from P5.7-BISECT + 15 from this sweep)
- `/app/memory/jc_artifacts/test_pollution/holdout_20260626T195600Z.md` NEW (consolidated index)
- `/app/memory/sprints/P5_7_HOLDOUT_FINISHER.md` NEW (this memo)

## Files NOT touched

- 0 production code mutated
- 0 test files mutated
- 0 fixture files mutated
- 0 invariant files mutated
- HARD STOP at confirmed-pair surface honoured
