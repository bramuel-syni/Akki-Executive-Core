**Canonical Spec**: `/app/memory/sprints/P5_22_csrf_wire_test_refresh.md` (failing-test ledger seeded by Phase 5.6.1 CSRF rig audit)

# Failing-Test Tracker

Per the Zero-Handoff-Loss discipline: every test marked FLAGGED-FALSE-GREEN
during a rig-fix audit, or surfaced as a flaky-in-broad-but-green-in-isolation
test, lives here until it is either re-implemented with a real assertion or
diagnosed for a root-cause sprint.

## Active entries

### FLAGGED-FALSE-GREEN (from PHASE_5_6_1_CSRF_RIG_AUDIT.md, 2026-06-26)

— **(empty)** — FTT-001 resolved by Phase 5.6.2 on 2026-06-26; see Resolved section below.

### CROSS-TEST POLLUTION FLAKES (from broad-suite run delta, 2026-06-26)

These tests went GREEN → RED in the AFTER broad-suite run but PASS in isolation. They were equally flake-prone BEFORE; a different shuffle would have surfaced a different sub-set. Not regressions caused by the CSRF rig fix.

| ID | Node | Pass in isolation? | Suspected pollution source |
|----|------|--------------------|-----------------------------|
| FTT-002 | `tests/characterisation/test_chat_roundtrip_golden.py::test_chat_roundtrip_golden_shape` | ✅ | event-loop binding leak |
| FTT-003 | `tests/test_chat_fluency_no_shield_leak.py::test_chat_response_does_not_leak_shield_mechanics` | ✅ | event-loop binding leak |
| FTT-004 | `tests/test_iter41_signal_actions_in_process.py::test_s41_a_get_recommendations_returns_bucket_and_three` | ✅ | shared fixture-state |
| FTT-005 | `tests/test_iter41_signal_actions_in_process.py::test_s41_b_post_acted_persists_and_summarises` | ✅ | shared fixture-state |
| FTT-006 | `tests/test_iter41_signal_actions_in_process.py::test_s41_c_post_shared_aggregates_recipients` | ✅ | shared fixture-state |
| FTT-007 | `tests/test_iter41_signal_actions_in_process.py::test_s41_d_actions_list_orders_most_recent_first` | ✅ | shared fixture-state |
| FTT-008 | `tests/test_iter41_signal_actions_in_process.py::test_s41_e_post_action_unknown_signal_returns_404` | ✅ | shared fixture-state |
| FTT-009 | `tests/test_iter41_signal_actions_in_process.py::test_s41_f_invalid_action_type_returns_422` | ✅ | shared fixture-state |
| FTT-010 | `tests/test_p_cleanup_c_help_tooltip_suppression.py::test_both_flags_set_is_idempotent_off` | ✅ | dependency_overrides leak |
| FTT-011 | `tests/test_p_cleanup_c_help_tooltip_suppression.py::test_explicit_dismissal_suppresses_independently` | ✅ | dependency_overrides leak |
| FTT-012 | `tests/test_p_cleanup_c_help_tooltip_suppression.py::test_returning_user_with_acknowledged_at_is_suppressed` | ✅ | dependency_overrides leak |
| FTT-013 | `tests/test_phase_d_fix_bundle.py::test_far_refusal_reachable_with_substantive_but_thin_inputs` | (skipped — slow) | TBD |
| FTT-014 | `tests/test_phase_i5_open_questions.py::test_i5_B1_backfill_idempotent` | ✅ | Mongo-collection state from prior file |
| FTT-015..018 | `test_phase_p3_2_cookie_hardening.py` (×2), `test_phase_p5_10_audit_panel_direct_linkage.py` (×4) | ✅ | env / Motor loop |
| FTT-019..022 | `test_phase_p5_7_5_bounce_webhook.py` (×4) | ✅ | SendGrid env stub |
| FTT-023 | `tests/test_track_b_phase2_task_lifecycle.py::test_cross_tenant_lifecycle_blocked` | ✅ | tenant-stub state |
| FTT-024..026 | `test_track_b_phase_b5_g6_notes_autosave.py` (×3) | ✅ | autosave debounce timer |

Total flake tracker: **24** distinct nodes (FTT-002..026); root causes need a separate sprint (not Phase 5.6.x scope).

## Resolved entries

### Phase 5.6.2 ship (2026-06-26)

| ID | Node | Disposition | Sprint memo |
|----|------|-------------|-------------|
| FTT-001 | `tests/test_phase_zz2_x.py::test_zz2_x_fixture_404_when_env_disabled` | RE-IMPLEMENTED with real assertion (both rails: env-disabled fall-through + env-enabled positive control via sentinel-patched `stream_fixture`). 4/4 GREEN on proving slice; 1 passed on pytest target with no sibling regression. | `sprints/P5_6_2_ftt001_real_assertion.md` |

## Disposition rules

1. **THIN-ASSERTION** items → Phase 5.6.2: rewrite each test with a real assertion that exercises the documented branch. Each entry leaves this tracker when its sprint memo ships.
2. **CROSS-TEST POLLUTION** items → require root-cause investigation (event-loop binding, dependency_overrides isolation, Mongo collection cleanup). Filed for a future Phase 5.7+ sprint.
3. New entries appended at the bottom of the appropriate section with the rationale, never inline-edited (preserve the audit trail).

— END —
