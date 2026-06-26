**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_z2_batch1.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 5.05 s
- **Return code**: 1

## STDOUT tail
```
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2_batch1.py::test_z2_1_native_datetime_local_input_removed
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2_batch1.py::test_z2_1_native_datetime_local_input_removed
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2_batch1.py::test_z2_1_native_datetime_local_input_removed
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2_batch1.py::test_z2_1_native_datetime_local_input_removed
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_phase_z2_batch1.py::test_z2_4_empty_state_has_run_solva_cta
FAILED tests/test_phase_z2_batch1.py::test_z2_4_cta_navigates_to_solva_landing
FAILED tests/test_phase_z2_batch1.py::test_z2_4_empty_state_subtext_verbatim
3 failed, 6 passed, 21 warnings in 3.65s
```