**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · skipped_slow_phase_d_fix_bundle)

# Pollution cluster — `skipped_slow_phase_d_fix_bundle`

- **FTT IDs**: FTT-013
- **Polluted targets**: 1
  - `tests/test_phase_d_fix_bundle.py::test_far_refusal_reachable_with_substantive_but_thin_inputs`

## Leaked state
Test is skipped under `-m 'not slow'`; cannot bisect without enabling.

## Isolation passes

## Static polluter candidate hits
_(none — see leaked-state narrative for diagnosis basis.)_

## Dynamic confirmation
_(skipped — see slice header for the rationale.)_

## Recommended cleanup
Enable the slow marker for one dispatch (`pytest -m slow`) and re-bisect; defer until the slow lane is run.
