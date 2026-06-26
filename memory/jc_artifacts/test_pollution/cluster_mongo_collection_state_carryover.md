**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · mongo_collection_state_carryover)

# Pollution cluster — `mongo_collection_state_carryover`

- **FTT IDs**: FTT-014
- **Polluted targets**: 1
  - `tests/test_phase_i5_open_questions.py::test_i5_B1_backfill_idempotent`

## Leaked state
The backfill-idempotent test asserts a precise row count in a Mongo collection (likely `open_questions` or similar). Earlier broad-suite tests insert rows into the same collection without cleanup, so the count assertion drifts. Conftest provides NO per-test Mongo cleanup; cleanup is each test file's responsibility.

## Isolation passes
- ✅ PASS in isolation — `tests/test_phase_i5_open_questions.py::test_i5_B1_backfill_idempotent`
  > 1 passed, 21 warnings in 4.57s

--STDERR--

## Static polluter candidate hits
| pattern | file | line | snippet |
|---|---|---:|---|
| `in_body_dependency_override` | `backend/tests/test_aa_followup_4_extractions_activity.py` | 64 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_aa_followup_4_extractions_activity.py` | 123 | `app.dependency_overrides[get_current_account] = _fake_admin` |
| `in_body_dependency_override` | `backend/tests/test_backlog_b_blocker_2_cycle_compilation.py` | 89 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_cycle_assignment_handoff.py` | 187 | `app.dependency_overrides[core_mod.get_current_account] = _override` |
| `in_body_dependency_override` | `backend/tests/test_cycle_assignment_privacy_wall.py` | 162 | `app.dependency_overrides[core_mod.get_current_account] = _override` |
| `in_body_dependency_override` | `backend/tests/test_cycle_feel_pass.py` | 82 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_cycles_v2.py` | 67 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_exco_teams.py` | 86 | `app.dependency_overrides[core_mod.get_current_account] = _override` |
| `in_body_dependency_override` | `backend/tests/test_monitor_drawer_progress_timeline.py` | 96 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_monitor_drawer_progress_timeline.py` | 163 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_monitor_drawer_progress_timeline.py` | 222 | `app.dependency_overrides[get_current_account] = _fake_attacker` |
| `in_body_dependency_override` | `backend/tests/test_patch_10_home_insights.py` | 70 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_12_streaming_v3.py` | 66 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_14_questions.py` | 68 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_2b1_kinds.py` | 75 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_2b2_compilations.py` | 79 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_3_home_v2.py` | 62 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_5_monitor_v2.py` | 61 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_9_streaming_phases.py` | 68 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_phase_p5_10_audit_panel_direct_linkage.py` | 113 | `app.dependency_overrides[get_current_account] = lambda: {` |
| `in_body_dependency_override` | `backend/tests/test_phase_r_invite_founder_cta.py` | 89 | `app.dependency_overrides[get_current_account] = _fake_admin` |
| `in_body_dependency_override` | `backend/tests/test_phase_w_admin_tenants.py` | 88 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_phase_w_admin_tenants.py` | 125 | `app.dependency_overrides[get_current_account] = _fake_admin` |
| `in_body_dependency_override` | `backend/tests/test_phase_w_followup_1_tenant_extraction_panel.py` | 70 | `app.dependency_overrides[get_current_account] = _fake_admin` |
| `in_body_dependency_override` | `backend/tests/test_phase_w_followup_1_tenant_extraction_panel.py` | 110 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_phase_w_followup_1_tenant_extraction_panel.py` | 128 | `app.dependency_overrides[get_current_account] = _fake_admin` |
| `in_body_dependency_override` | `backend/tests/test_phase_x_account_deletion.py` | 76 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_phase_x_account_deletion.py` | 129 | `app.dependency_overrides[get_current_account] = _fake_super` |
| `in_body_dependency_override` | `backend/tests/test_phase_x_account_deletion.py` | 189 | `app.dependency_overrides[get_current_account] = _fake_super` |
| `in_body_dependency_override` | `backend/tests/test_phase_x_account_deletion.py` | 249 | `app.dependency_overrides[get_current_account] = _fake_super` |
| `in_body_dependency_override` | `backend/tests/test_phase_x_account_deletion.py` | 269 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_phase_x_deployed_env_delete_account_e2e.py` | 63 | `app.dependency_overrides[get_current_account] = _fake_resolve` |
| `in_body_dependency_override` | `backend/tests/test_phase_zz2_x.py` | 116 | `app.dependency_overrides[get_current_account] = _override` |
| `in_body_dependency_override` | `backend/tests/test_phase_zz4.py` | 111 | `app.dependency_overrides[get_current_account] = _fake_current` |
| `in_body_dependency_override` | `backend/tests/test_phase_zz4.py` | 146 | `app.dependency_overrides[get_current_account] = _fake_current` |
| `in_body_dependency_override` | `backend/tests/test_phase_zz4.py` | 167 | `app.dependency_overrides[get_current_account] = _fake_current` |
| `in_body_dependency_override` | `backend/tests/test_qa_chunk_19.py` | 54 | `app.dependency_overrides[_require_superadmin] = _allow_superadmin` |
| `in_body_dependency_override` | `backend/tests/test_qa_chunk_19.py` | 127 | `app.dependency_overrides[_require_superadmin] = _allow_superadmin` |
| `in_body_dependency_override` | `backend/tests/test_qa_chunk_19.py` | 153 | `app.dependency_overrides[_require_superadmin] = _deny` |
| `in_body_dependency_override` | `backend/tests/test_t1_add_to_cycle_g1.py` | 101 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_t2_backend.py` | 82 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_t3_backend.py` | 78 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_t4_backend.py` | 87 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_t5_backend.py` | 78 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_team_catalogue.py` | 54 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_wave_5_contextless_chat_e2e.py` | 53 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_wave_5_contextless_chat_e2e.py` | 124 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_work_studio_listing.py` | 106 | `app.dependency_overrides[core_mod.get_current_account] = _o` |

## Dynamic confirmation
_(skipped — see slice header for the rationale.)_

## Recommended cleanup
Per-test fixture in `test_phase_i5_open_questions.py` that purges the asserted-on collection in `setup` AND `teardown`. Don't rely on session-wide DB isolation.
