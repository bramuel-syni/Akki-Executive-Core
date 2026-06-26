**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_m0c_cohort_applications.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 7.58 s
- **Return code**: 1

## STDOUT tail
```
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m0c_cohort_applications.py::test_m0c_router_registered
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m0c_cohort_applications.py::test_m0c_router_registered
tests/test_phase_m0c_cohort_applications.py::test_m0c_post_application_happy_path
tests/test_phase_m0c_cohort_applications.py::test_m0c_post_application_validation_errors
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m0c_cohort_applications.py::test_m0c_router_registered
tests/test_phase_m0c_cohort_applications.py::test_m0c_post_application_happy_path
tests/test_phase_m0c_cohort_applications.py::test_m0c_post_application_validation_errors
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m0c_cohort_applications.py::test_m0c_router_registered
tests/test_phase_m0c_cohort_applications.py::test_m0c_post_application_happy_path
tests/test_phase_m0c_cohort_applications.py::test_m0c_post_application_validation_errors
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_phase_m0c_cohort_applications.py::test_m0c_router_registered
1 failed, 4 passed, 33 warnings in 5.45s
```