**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_z2d_reseed_integrity.py`

- **Bucket**: `PASS`
- **Duration**: 4.85 s
- **Return code**: 0

## STDOUT tail
```

tests/test_phase_z2d_reseed_integrity.py::test_rebuilt_cohort_pass_rate_meets_target
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2d_reseed_integrity.py::test_rebuilt_cohort_pass_rate_meets_target
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2d_reseed_integrity.py::test_rebuilt_cohort_pass_rate_meets_target
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2d_reseed_integrity.py::test_rebuilt_cohort_pass_rate_meets_target
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2d_reseed_integrity.py::test_rebuilt_cohort_pass_rate_meets_target
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [3] tests/test_phase_z2d_reseed_integrity.py:46: No re-seed timestamp at /tmp/reseed_start.txt — re-seed was not run in this environment.
3 skipped, 21 warnings in 3.62s
```