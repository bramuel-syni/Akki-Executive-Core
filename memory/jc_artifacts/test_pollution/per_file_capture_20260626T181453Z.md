**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution path (b) · per-file subprocess capture · INVESTIGATE-ONLY · HALT-and-surface)

# Per-file subprocess capture · 20260626T181453Z

**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` (confirmed root cause + cleanup mapping per cluster).

**Slice**: `/app/backend/scripts/jc_test_pollution_per_file_capture_slice.py` (READ-ONLY by contract).

## Aggregate buckets

- **Total files run**: 433
- **Total wall time**: 3288s (54.8 min)

| Bucket | Count | Pct |
|---|---:|---:|
| `PASS` | 350 | 80.8% |
| `PASS_NO_TESTS` | 14 | 3.2% |
| `FAIL_DETERMINISTIC` | 59 | 13.6% |
| `TIMEOUT` | 10 | 2.3% |
| `ERROR` | 0 | 0.0% |

## Diagnostic interpretation (post-capture review)

Phase-2 cross-reference initially counted **FTT-002** and **FTT-003** as FAIL_IN_CONTEXT, but a manual review of their files showed `pytestmark = [pytest.mark.asyncio, pytest.mark.integration]` — i.e. they are marker-deselected from this lane (`not integration`) and never executed. The capture's PASS_NO_TESTS bucket is the honest signal.

**This means**: FTT-002 and FTT-003 are NOT cross-test pollution candidates in the default test lane. They appeared as failures in the broader baseline (`phase_5_5_3_failing_files_20260626.txt`) only because that run included `-m integration`. Tracker reclassification needed:
- Either keep them but tag with the lane-context that surfaces them, OR
- Move them out of the pollution cluster entirely (they are integration-lane failures, not pollution flakes)

### Corrected scope

- **18 FTT IDs / 7 files = confirmed pollution candidates** (file PASSes in isolation in the default lane, tracker says it fails in-suite):
  - FTT-004..009 → `test_iter41_signal_actions_in_process.py`
  - FTT-010..012 → `test_p_cleanup_c_help_tooltip_suppression.py`
  - FTT-015..016 → `test_phase_p3_2_cookie_hardening.py`
  - FTT-017..018 → `test_phase_p5_10_audit_panel_direct_linkage.py`
  - FTT-019..022 → `test_phase_p5_7_5_bounce_webhook.py`
  - FTT-023 → `test_track_b_phase2_task_lifecycle.py`
  - FTT-024..026 → `test_track_b_phase_b5_g6_notes_autosave.py`
- **2 FTT IDs (FTT-002, FTT-003) = lane-mismatched** (integration-only; not pollution in default lane)
- **1 FTT ID (FTT-013) = slow test** (TIMEOUT in isolation; not pollution)
- **1 FTT ID (FTT-014) = tracker misclassification** (fails in isolation too; deterministic regression, not pollution)

**Net pollution scope: 7 files / 18 FTT IDs** — well under the 100-file systemic-rot halt threshold. Each is now eligible for the next-sprint bisect (predecessor-chain search to find the specific polluter).

## Phase-2 cross-reference vs FAILING_TEST_TRACKER (FTT-002..026)

### FAIL_IN_CONTEXT — confirmed pollution candidates
Files that PASS alone but appear in the tracker as failing in-suite.
This is the diagnostic gold: each represents a real polluter chain.

| File | FTT IDs | Locked area? |
|---|---|:---:|
| `tests/characterisation/test_chat_roundtrip_golden.py` | FTT-002 | no |
| `tests/test_chat_fluency_no_shield_leak.py` | FTT-003 | no |
| `tests/test_iter41_signal_actions_in_process.py` | FTT-004, FTT-005, FTT-006, FTT-007, FTT-008, FTT-009 | no |
| `tests/test_p_cleanup_c_help_tooltip_suppression.py` | FTT-010, FTT-011, FTT-012 | no |
| `tests/test_phase_p3_2_cookie_hardening.py` | FTT-015, FTT-016 | no |
| `tests/test_phase_p5_10_audit_panel_direct_linkage.py` | FTT-017, FTT-018 | no |
| `tests/test_phase_p5_7_5_bounce_webhook.py` | FTT-019, FTT-020, FTT-021, FTT-022 | no |
| `tests/test_track_b_phase2_task_lifecycle.py` | FTT-023 | no |
| `tests/test_track_b_phase_b5_g6_notes_autosave.py` | FTT-024, FTT-025, FTT-026 | no |

### FAIL_DETERMINISTIC_IN_TRACKER — tracker entry needs correction
Files that FAIL alone too — the tracker classified them as pollution flakes but they're deterministic regressions.

| File | FTT IDs |
|---|---|
| `tests/test_phase_i5_open_questions.py` | FTT-014 |

### INCONCLUSIVE — TIMEOUT or ERROR in isolation
Files that didn't complete in isolation; cannot bucket.

| File | Bucket | FTT IDs |
|---|---|---|
| `tests/test_phase_d_fix_bundle.py` | `TIMEOUT` | FTT-013 |

## Halt-and-surface conditions

_(none — all clear)_

## Discipline & out-of-scope notes

- This slice is READ-ONLY by contract. NO test/fixture/production code mutated.
- Per-file subprocess isolation replaces the in-process broad-suite that hung at 16% in `P5_7_CAPTURE_B_ATTEMPT_1`.
- The FAIL_IN_CONTEXT bucket is the next sprint's input: bisect each file's predecessor chain to identify the polluter(s).
- Bisect itself is OUT OF SCOPE for this slice — HARD STOP at surface per user direction.
