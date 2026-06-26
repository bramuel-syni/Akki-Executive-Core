**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · autosave_debounce_timer_leak)

# Pollution cluster — `autosave_debounce_timer_leak`

- **FTT IDs**: FTT-024, FTT-025, FTT-026
- **Polluted targets**: 1
  - `tests/test_track_b_phase_b5_g6_notes_autosave.py`

## Leaked state
Notes-autosave tests rely on a debounce timer (most likely an `asyncio.TimerHandle` or a `threading.Timer`) set/torn-down within the autosave service. An upstream test (probably in track_b/) leaves the timer alive — either by installing a module-scope fixture that triggers an autosave without teardown, or by mocking `asyncio.sleep` without restore. The debounce timer then fires inside the polluted tests and breaks expected payload counts.

## Isolation passes
- ✅ PASS in isolation — `tests/test_track_b_phase_b5_g6_notes_autosave.py`
  > 3 passed, 21 warnings in 4.91s

--STDERR--

## Static polluter candidate hits
| pattern | file | line | snippet |
|---|---|---:|---|
| `module_scope_fixture` | `backend/tests/test_cycle_assignment_handoff.py` | 37 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_cycle_assignment_privacy_wall.py` | 73 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_cycle_feel_pass.py` | 33 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_cycle_manager_actions_tab.py` | 32 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_cycles_v2.py` | 27 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_docs_download.py` | 28 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_exco_teams.py` | 42 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_governance_endpoint.py` | 25 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_inbound_uuid_fallback.py` | 41 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_patch_2b1_kinds.py` | 39 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_patch_2b2_compilations.py` | 38 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_patch_3_home_v2.py` | 32 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_patch_5_monitor_v2.py` | 32 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase4_2_http_transport_smoke.py` | 61 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase4_4_dual_mount_smoke.py` | 57 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase_b_sandbox_upload.py` | 69 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase_g_privacy_wall_sentinel.py` | 69 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase_g_privacy_wall_sentinel.py` | 74 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_phase_g_privacy_wall_sentinel.py` | 85 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_prepare_redirect_alias.py` | 34 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_privacy_wall.py` | 72 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_privacy_wall.py` | 77 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_privacy_wall.py` | 91 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_privacy_wall_phase_2c.py` | 32 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_privacy_wall_phase_2c.py` | 39 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_route_existence_smoke.py` | 56 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_solva_v2_pptx_chair_notes.py` | 55 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_t1_add_to_cycle_g1.py` | 57 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_t2_backend.py` | 41 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_t3_backend.py` | 40 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_t4_backend.py` | 49 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_t5_backend.py` | 40 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_team_catalogue.py` | 26 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_universal_search.py` | 41 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_universal_search.py` | 48 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_universal_search.py` | 56 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_universal_search.py` | 317 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_work_studio_briefings_visible.py` | 39 | `@pytest.fixture(scope="module")` |
| `module_scope_fixture` | `backend/tests/test_work_studio_listing.py` | 32 | `@pytest.fixture(scope="module")` |

## Dynamic confirmation
_(skipped — see slice header for the rationale.)_

## Recommended cleanup
Audit `test_track_b_*` files for module-scope fixtures that trigger autosave. Add an explicit timer cancel + service-level state reset to each test's fixture teardown.
