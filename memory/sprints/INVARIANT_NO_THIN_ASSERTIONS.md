**Canonical Spec**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` (structural enforcement of the audit standard — tests that assert nothing hide gaps; same anti-pattern the CSRF rig fix surfaced)

# Sprint INVARIANT-NO-THIN-ASSERTIONS — build-breaking guard

**Status**: SHIPPED
**Date**: 2026-06-26
**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` — "A rig fix that greens a test which asserts nothing is worse than the red — it hides the gap."
**Proving slice**: `/app/backend/scripts/jc_invariant_thin_assertions_slice.py` — classifier 10/10 GREEN (7 positive + 3 negative); live-tree scan 9/9 ≤ 10 halt-threshold
**Invariant file**: `/app/backend/tests/invariants/test_no_thin_assertions.py` — 2 passed (positive + drift detector); negative-rail probe confirmed FAIL when a synthetic `try: pass` test injected
**Grandfather list**: `/app/backend/tests/invariants/thin_assertions_grandfathered.yml` — 9 pre-existing entries (FTT-027..035)
**Files touched**: 0 production code · 1 NEW invariant (+360 LOC) · 1 NEW grandfather YAML (+75 LOC) · 1 NEW slice script (+340 LOC)

## Problem (what the audit standard demands)

The 5.6.1 CSRF rig audit catalogued FTT-001 as a `try: pass` test body that "asserts nothing about the documented branch." The fix (Phase 5.6.2, shipped earlier this dispatch) rewrote that single test with a CSRF-grade dual-rail assertion.

But FTT-001 was likely not unique — the audit pattern ("rig fix greens a test that asserts nothing") could fire again whenever someone writes a placeholder test body. A code-search baseline was needed to know how widespread the issue was; a build-breaking guard was needed to stop NEW thin assertions from entering the suite.

## Fix

A build-breaking invariant `tests/invariants/test_no_thin_assertions.py` that AST-walks every `tests/test_*.py` (excluding `tests/invariants/` to avoid self-reference) and classifies test function bodies against 5 thin-assertion patterns:

  - **T1** — `try: pass` (no assertion inside the try body)
  - **T2** — body == `pass` (with optional docstring)
  - **T3** — `assert <constant>` (e.g. `assert True`)
  - **T4** — body contains only `pytest.skip(...)`
  - **T5** — docstring-only body

Two-tier exemption:
  (a) File-based **grandfather list** at `thin_assertions_grandfathered.yml` — seeded with the 9 legacy entries (FTT-027..035). Each is queued for individual rewrite or deletion in `FAILING_TEST_TRACKER.md`.
  (b) In-source `@pytest.mark.acceptable_thin_assertion` + `# reason: …` comment — for genuinely intentional thin assertions (import-side-effect checks, etc.). Adding the marker requires a sprint memo justification at code review.

A **drift detector** companion test (`test_grandfather_list_does_not_drift`) fires if an entry in the grandfather YAML no longer triggers the classifier (test was rewritten or removed) — so the YAML can't carry stale entries silently.

## Baseline scan output

Live-tree scan at 2026-06-26 17:48 UTC: **9 active findings** across 7 files — well under the 10-finding HALT threshold the user pre-authorised.

| Pattern | Count | Distribution |
|---|---:|---|
| T2 (`pass`-only) | 3 | `test_iter12_shares_home.py`, `test_track_b_phase1_signin_begin.py` ×2 |
| T3 (`assert True`) | 3 | `test_j2_stage_3.py`, `test_j3_stage_4_5_frontend.py` ×2 |
| T4 (`pytest.skip`-only) | 3 | `test_patch_21_news.py`, `test_patch_23_upload_p0.py`, `test_patch_25_news_geo.py` |

Per the user direction ("Surface those as a separate FAILING_TEST_TRACKER bulk-update — do NOT auto-fix"), each of the 9 was added to `FAILING_TEST_TRACKER.md` as FTT-027..035 (THIN-ASSERTION class) with individual disposition targets. Combined tracker total: **33** active entries (24 pollution + 9 thin-assertion).

## Why this is CSRF-grade

The classifier matches the AST signature of the EXACT pattern FTT-001 carried — `try: pass` with no real test action — and three sibling shapes that ASLO assert nothing (T2..T5). The proving slice exercises both rails:

- **Positive rail (10/10 GREEN)**: 7 fixtures known to BE thin assertions are classified correctly; 3 fixtures with real assertions are classified None (no false positives).
- **Negative-rail end-to-end probe**: a temporary `test_zzz_thin_assertion_negative_probe.py` was injected with `try: pass` + `assert True` → the invariant FAILED the build (1 failed). The probe file was deleted; invariant returned to GREEN (2 passed).
- **Drift guard**: the second invariant (`test_grandfather_list_does_not_drift`) ensures the YAML stays honest — if any of the 9 grandfathered tests is rewritten with a real assertion, the drift detector fires, prompting removal from the YAML.

## Forward-going policy

- **New thin assertions are build-breaking.** PR authors get a clear error message with pattern ID, file, line, function, and three resolution paths (rewrite, grandfather, in-source marker).
- **Legacy entries (FTT-027..035) are not auto-fixed.** Each goes into its own follow-up dispatch when the user prioritises individual rewrites.
- **In-source marker requires justification.** The marker MUST be paired with a `# reason: …` comment within 3 lines of the `def`; missing the comment means the marker doesn't exempt the test.

## Evidence

```
$ python /app/backend/scripts/jc_invariant_thin_assertions_slice.py --proving
  [GREEN] test_try_pass_only (expected=T1, actual=T1)
  [GREEN] test_only_pass (expected=T2, actual=T2)
  [GREEN] test_only_pass_with_docstring (expected=T2, actual=T2)
  [GREEN] test_assert_true (expected=T3, actual=T3)
  [GREEN] test_assert_constant_str (expected=T3, actual=T3)
  [GREEN] test_only_skip (expected=T4, actual=T4)
  [GREEN] test_docstring_only (expected=T5, actual=T5)
  [GREEN] test_real_assertion (expected=None, actual=None)
  [GREEN] test_real_with_try (expected=None, actual=None)
  [GREEN] test_legitimate_skip_with_marker (expected=None, actual=None)
OK: 10/10 classifier fixtures GREEN

$ python /app/backend/scripts/jc_invariant_thin_assertions_slice.py
   Total files scanned: 434
   Raw findings:        9
   Allowlisted:         0
   ACTIVE findings:     9
✅ Active count 9 ≤ threshold 10 — safe to ship invariant.

$ pytest tests/invariants/test_no_thin_assertions.py -xvs
2 passed, 21 warnings in 5.53s
```

Negative-rail end-to-end probe (temporary file injection):
```
$ mv _thin_assertions_negative_rail_probe.py test_zzz_thin_assertion_negative_probe.py
$ pytest tests/invariants/test_no_thin_assertions.py::test_no_thin_assertions_in_tests
1 failed, 21 warnings in 4.79s  ← invariant caught the synthetic violation
$ rm test_zzz_thin_assertion_negative_probe.py
$ pytest tests/invariants/test_no_thin_assertions.py
2 passed, 21 warnings in 5.53s  ← back to GREEN
```

## FAILING_TEST_TRACKER counter movement

Pre-ship: 24 active (FTT-002..026 pollution).
Post-ship: **33** active (24 pollution + 9 NEW THIN-ASSERTION entries FTT-027..035).

This is a deliberate surfacing — the 9 entries were hiding in the tree before the invariant; they are now visible audit liabilities awaiting user direction on individual rewrite cadence.

## Out of scope

- Individual rewrite of FTT-027..035 — separate dispatches per user prioritisation.
- Path (a) static guards from P5.7-DIAG (asyncio.run sweep, no-bare-env-mutation, no-module-level-overrides) — REMAIN PARKED pending P5.7-DIAG (b) broad-suite capture results, per user direction.
