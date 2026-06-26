**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · shared_fixture_state_iter41)

# Pollution cluster — `shared_fixture_state_iter41`

- **FTT IDs**: FTT-004, FTT-005, FTT-006, FTT-007, FTT-008, FTT-009
- **Polluted targets**: 1
  - `tests/test_iter41_signal_actions_in_process.py::test_s41_a_get_recommendations_returns_bucket_and_three`

## Leaked state
All 6 tests in `test_iter41_signal_actions_in_process.py` share a module-scope FastAPI dep override and/or a module-global dict that one test mutates (e.g. signal-action history list). The autouse conftest `_isolate_dependency_overrides` snapshots overrides at TEST start — but the module-level override is set at module IMPORT, so snapshot==override (no isolation gained). Mutations to a non-override module-global (lists/dicts) are entirely outside conftest's scope.

## Isolation passes
- ✅ PASS in isolation — `tests/test_iter41_signal_actions_in_process.py::test_s41_a_get_recommendations_returns_bucket_and_three`
  > 1 passed, 21 warnings in 4.04s

--STDERR--

## Static polluter candidate hits
| pattern | file | line | snippet |
|---|---|---:|---|
| `in_body_dependency_override` | `backend/tests/test_aa_followup_4_extractions_activity.py` | 64 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_aa_followup_4_extractions_activity.py` | 123 | `app.dependency_overrides[get_current_account] = _fake_admin` |
| `in_body_dependency_override` | `backend/tests/test_backlog_b_blocker_2_cycle_compilation.py` | 89 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `module_scope_fixture` | `backend/tests/test_cycle_assignment_handoff.py` | 37 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_cycle_assignment_handoff.py` | 187 | `app.dependency_overrides[core_mod.get_current_account] = _override` |
| `module_scope_fixture` | `backend/tests/test_cycle_assignment_privacy_wall.py` | 73 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_cycle_assignment_privacy_wall.py` | 162 | `app.dependency_overrides[core_mod.get_current_account] = _override` |
| `module_scope_fixture` | `backend/tests/test_cycle_feel_pass.py` | 33 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_cycle_feel_pass.py` | 82 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `module_scope_fixture` | `backend/tests/test_cycle_manager_actions_tab.py` | 32 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_cycles_v2.py` | 27 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_cycles_v2.py` | 67 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `module_scope_fixture` | `backend/tests/test_docs_download.py` | 28 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_exco_teams.py` | 42 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_exco_teams.py` | 86 | `app.dependency_overrides[core_mod.get_current_account] = _override` |
| `module_scope_fixture` | `backend/tests/test_governance_endpoint.py` | 25 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_inbound_uuid_fallback.py` | 41 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_monitor_drawer_progress_timeline.py` | 96 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_monitor_drawer_progress_timeline.py` | 163 | `app.dependency_overrides[get_current_account] = _fake_user` |
| `in_body_dependency_override` | `backend/tests/test_monitor_drawer_progress_timeline.py` | 222 | `app.dependency_overrides[get_current_account] = _fake_attacker` |
| `in_body_dependency_override` | `backend/tests/test_patch_10_home_insights.py` | 70 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_12_streaming_v3.py` | 66 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_14_questions.py` | 68 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `module_scope_fixture` | `backend/tests/test_patch_2b1_kinds.py` | 39 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_patch_2b1_kinds.py` | 75 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `module_scope_fixture` | `backend/tests/test_patch_2b2_compilations.py` | 38 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_patch_2b2_compilations.py` | 79 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `module_scope_fixture` | `backend/tests/test_patch_3_home_v2.py` | 32 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_patch_3_home_v2.py` | 62 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `module_scope_fixture` | `backend/tests/test_patch_5_monitor_v2.py` | 32 | `@pytest.fixture(scope="module")` |
| `in_body_dependency_override` | `backend/tests/test_patch_5_monitor_v2.py` | 61 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `in_body_dependency_override` | `backend/tests/test_patch_9_streaming_phases.py` | 68 | `app.dependency_overrides[core_mod.get_current_account] = _o` |
| `module_scope_fixture` | `backend/tests/test_phase4_2_http_transport_smoke.py` | 61 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase4_4_dual_mount_smoke.py` | 57 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase_b_sandbox_upload.py` | 69 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase_g_privacy_wall_sentinel.py` | 69 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase_g_privacy_wall_sentinel.py` | 74 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase_g_privacy_wall_sentinel.py` | 85 | `@pytest.fixture(scope="module")` |
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

_…and 37 more hits (truncated)._

## Dynamic confirmation
_(skipped — see slice header for the rationale.)_

## Recommended cleanup
Move the override from module scope into a function-scope autouse fixture inside the test file (so the snapshot/restore catches it). Convert any module-global lists/dicts into fixture-yielded objects so each test gets a fresh instance. Mechanical.
