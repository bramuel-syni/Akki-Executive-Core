**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_zz4.py`

- **Bucket**: `PASS`
- **Duration**: 8.8 s
- **Return code**: 0

## STDOUT tail
```
          
    @app.on_event("startup")

tests/test_phase_zz4.py::test_zz4_endpoint_source_present
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_zz4.py::test_zz4_endpoint_source_present
tests/test_phase_zz4.py::test_zz4_math_p50_p95_slowest_fastest
tests/test_phase_zz4.py::test_zz4_empty_window_returns_zeros
tests/test_phase_zz4.py::test_zz4_window_param_strict
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_zz4.py::test_zz4_endpoint_source_present
tests/test_phase_zz4.py::test_zz4_math_p50_p95_slowest_fastest
tests/test_phase_zz4.py::test_zz4_empty_window_returns_zeros
tests/test_phase_zz4.py::test_zz4_window_param_strict
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_zz4.py::test_zz4_endpoint_source_present
tests/test_phase_zz4.py::test_zz4_math_p50_p95_slowest_fastest
tests/test_phase_zz4.py::test_zz4_empty_window_returns_zeros
tests/test_phase_zz4.py::test_zz4_window_param_strict
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
8 passed, 39 warnings in 6.94s
```