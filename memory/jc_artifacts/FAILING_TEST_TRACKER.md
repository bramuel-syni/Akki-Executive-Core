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

### Reclassification proposals (from P5.7-PER-FILE-CAPTURE, 2026-06-26)

The per-file subprocess capture (`sprints/P5_7_PER_FILE_CAPTURE.md`) confirmed which of the 24 active tracker entries are TRUE cross-test pollution (file PASSes in isolation but FAILs in-suite) vs. originally-misclassified entries. These are **proposed** reclassifications surfaced for user direction — original entries above remain unchanged per the audit-trail discipline ("Old entries are kept here even when resolved, never inline-edited").

| FTT IDs | File | Original | Per-file evidence | Proposed reclassification |
|---|---|---|---|---|
| FTT-002, FTT-003 | `test_chat_roundtrip_golden.py`, `test_chat_fluency_no_shield_leak.py` | cross-test pollution | PASS_NO_TESTS in default lane (`pytestmark = [..., pytest.mark.integration]`) | **integration-lane-only** — not pollution; failures only surface with `-m integration` enabled |
| FTT-013 | `test_phase_d_fix_bundle.py` | cross-test pollution (slow-marker skip suspected) | TIMEOUT at 60 s in isolation | **deterministic-slow** — not pollution; test simply exceeds 60 s in isolation |
| FTT-014 | `test_phase_i5_open_questions.py::test_i5_B1_backfill_idempotent` | cross-test pollution | FAIL_DETERMINISTIC in isolation | **deterministic regression** — not pollution; needs its own bug-fix sprint |

**Net cross-test pollution scope** (post-reclassification): 18 FTT IDs across 7 files — FTT-004..012, 015..026 (minus FTT-014). All seven files PASS in isolation under default lane markers and are confirmed as polluted-in-suite. **Halt thresholds clear** (under 100 files; no locked-area polluter at this surface).

| FTT IDs | File (confirmed pollution candidate) | Cluster (P5.7-DIAG hypothesis) |
|---|---|---|
| FTT-004..009 | `test_iter41_signal_actions_in_process.py` | shared_fixture_state_iter41 (in-file) |
| FTT-010..012 | `test_p_cleanup_c_help_tooltip_suppression.py` | dependency_overrides_leak |
| FTT-015..016 | `test_phase_p3_2_cookie_hardening.py` | env_or_motor_loop_state |
| FTT-017..018 | `test_phase_p5_10_audit_panel_direct_linkage.py` | env_or_motor_loop_state |
| FTT-019..022 | `test_phase_p5_7_5_bounce_webhook.py` | sendgrid_env_stub_leak |
| FTT-023 | `test_track_b_phase2_task_lifecycle.py` | tenant_resolver_stub_leak |
| FTT-024..026 | `test_track_b_phase_b5_g6_notes_autosave.py` | autosave_debounce_timer_leak |

Bisect (next-sprint scope) per user pick among (a) binary-search per file, (b) statically-narrowed per file, or (c) two-file blanket sweep per polluted file.

### THIN-ASSERTION grandfather entries (from INVARIANT_NO_THIN_ASSERTIONS baseline scan, 2026-06-26)

These 9 entries are the pre-existing thin-assertion test bodies that the new build-breaking invariant `tests/invariants/test_no_thin_assertions.py` surfaced at ship time. They are exempted by the file-based grandfather list at `backend/tests/invariants/thin_assertions_grandfathered.yml`. Each is queued for individual rewrite (real assertion that exercises the documented branch) OR deletion (if the test is truly redundant). Removing an entry from this section MUST coincide with removing it from the grandfather YAML.

| ID | Node | Pattern | Disposition target |
|----|------|---------|---------------------|
| FTT-027 | `tests/test_iter12_shares_home.py::test_comment_on_share_via_comments_router` | T2 (`pass`-only) | Legacy share-home test stub; rewrite with real comments-router assertion or delete |
| FTT-028 | `tests/test_j2_stage_3.py::test_no_guardrail_files_modified_in_j2` | T3 (`assert True`) | Guardrail-files marker assertion — replace with real file-set diff assertion |
| FTT-029 | `tests/test_j3_stage_4_5_frontend.py::test_j3_f6_retired_at_j4_ship` | T3 (`assert True`) | Retired-at-ship marker — confirm phase retirement via real surface check |
| FTT-030 | `tests/test_j3_stage_4_5_frontend.py::test_j3_f8_no_guardrail_files_modified` | T3 (`assert True`) | Same shape as FTT-028 |
| FTT-031 | `tests/test_patch_21_news.py::test_news_endpoint_requires_auth` | T4 (only `pytest.skip`) | Either remove (dead test) or restore real auth-gate assertion |
| FTT-032 | `tests/test_patch_23_upload_p0.py::test_upload_endpoint_rejects_without_auth_header` | T4 (only `pytest.skip`) | Same shape as FTT-031 |
| FTT-033 | `tests/test_patch_25_news_geo.py::test_profile_country_get_patch_round_trip` | T4 (only `pytest.skip`) | Same shape as FTT-031 |
| FTT-034 | `tests/test_track_b_phase1_signin_begin.py::test_fig20_unauth_root_lands_on_signin` | T2 (`pass`-only) | Track-B Phase 1 sign-in unauth-root — pair with FIG-20 acceptance row |
| FTT-035 | `tests/test_track_b_phase1_signin_begin.py::test_fig22_post_redirect_no_error_state` | T2 (`pass`-only) | Track-B Phase 1 post-redirect no-error — pair with FIG-22 acceptance row |

Total thin-assertion tracker: **9** distinct nodes (FTT-027..035); each requires individual rewrite or deletion. Combined active tracker total: **33** entries (24 pollution + 9 thin-assertion).

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
