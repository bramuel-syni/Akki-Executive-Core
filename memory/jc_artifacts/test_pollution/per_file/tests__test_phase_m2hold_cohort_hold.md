**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_m2hold_cohort_hold.py`

- **Bucket**: `PASS`
- **Duration**: 6.42 s
- **Return code**: 0

## STDOUT tail
```
tests/test_phase_m2hold_cohort_hold.py::test_m2hold_holding_line_in_copy_module_verbatim
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m2hold_cohort_hold.py::test_m2hold_holding_line_in_copy_module_verbatim
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m2hold_cohort_hold.py::test_m2hold_holding_line_in_copy_module_verbatim
tests/test_phase_m2hold_cohort_hold.py::test_m2hold_form_submission_still_works
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m2hold_cohort_hold.py::test_m2hold_holding_line_in_copy_module_verbatim
tests/test_phase_m2hold_cohort_hold.py::test_m2hold_form_submission_still_works
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m2hold_cohort_hold.py::test_m2hold_holding_line_in_copy_module_verbatim
tests/test_phase_m2hold_cohort_hold.py::test_m2hold_form_submission_still_works
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
10 passed, 27 warnings in 4.45s
```