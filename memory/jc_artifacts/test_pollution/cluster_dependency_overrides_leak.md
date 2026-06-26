**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · dependency_overrides_leak)

# Pollution cluster — `dependency_overrides_leak`

- **FTT IDs**: FTT-010, FTT-011, FTT-012
- **Polluted targets**: 1
  - `tests/test_p_cleanup_c_help_tooltip_suppression.py::test_both_flags_set_is_idempotent_off`

## Leaked state
A prior test file sets `app.dependency_overrides[get_current_account] = ...` (or similar) at MODULE BODY load time, BEFORE conftest's autouse `_isolate_dependency_overrides` snapshot runs. The snapshot then captures the polluted state as the baseline; restoration after each test puts the polluted state back. Help-tooltip tests rely on the real `get_current_account` resolution for the suppression flag, so the stale override breaks them.

## Isolation passes
- ✅ PASS in isolation — `tests/test_p_cleanup_c_help_tooltip_suppression.py::test_both_flags_set_is_idempotent_off`
  > 1 passed, 21 warnings in 4.59s

--STDERR--

## Static polluter candidate hits
_(none — see leaked-state narrative for diagnosis basis.)_

## Dynamic confirmation
_(skipped — see slice header for the rationale.)_

## Recommended cleanup
Audit any `app.dependency_overrides[...]` at module body and move into a fixture (function or module scope) with explicit teardown. Add a static guard: `tests/invariants/test_no_module_level_dependency_overrides.py` AST-checks for the pattern.
