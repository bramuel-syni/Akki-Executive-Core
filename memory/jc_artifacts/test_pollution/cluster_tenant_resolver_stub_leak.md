**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · tenant_resolver_stub_leak)

# Pollution cluster — `tenant_resolver_stub_leak`

- **FTT IDs**: FTT-023
- **Polluted targets**: 1
  - `tests/test_track_b_phase2_task_lifecycle.py::test_cross_tenant_lifecycle_blocked`

## Leaked state
Cross-tenant lifecycle test verifies a tenant-isolation boundary that depends on `get_current_account.tenant_id` resolution. An upstream test installs a tenant-stub resolver via dependency_overrides at module scope, which (as in cluster 3) bypasses the autouse snapshot. The cross-tenant test then sees the polluter's tenant_id as the canonical one and fails its boundary check.

## Isolation passes
- ✅ PASS in isolation — `tests/test_track_b_phase2_task_lifecycle.py::test_cross_tenant_lifecycle_blocked`
  > 1 passed, 21 warnings in 4.61s

--STDERR--

## Static polluter candidate hits
_(none — see leaked-state narrative for diagnosis basis.)_

## Dynamic confirmation
_(skipped — see slice header for the rationale.)_

## Recommended cleanup
Subsumed by cluster-3 fix: moving module-level dependency_overrides into function-scope fixtures.
