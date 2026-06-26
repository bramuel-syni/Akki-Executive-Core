**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_admin_email_provider_health.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 8.87 s
- **Return code**: 1

## STDOUT tail
```
tests/test_admin_email_provider_health.py::test_health_router_file_exists_and_defines_endpoint
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_admin_email_provider_health.py::test_health_router_file_exists_and_defines_endpoint
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_admin_email_provider_health.py::test_health_router_file_exists_and_defines_endpoint
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_admin_email_provider_health.py::test_health_router_file_exists_and_defines_endpoint
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_admin_email_provider_health.py::test_health_router_file_exists_and_defines_endpoint
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_admin_email_provider_health.py::test_health_router_is_registered_in_server
FAILED tests/test_admin_email_provider_health.py::test_health_admin_returns_200_with_expected_shape
2 failed, 9 passed, 21 warnings in 7.36s
```