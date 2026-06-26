**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_home_cleanup_phase_f6_debt.py`

- **Bucket**: `PASS`
- **Duration**: 7.74 s
- **Return code**: 0

## STDOUT tail
```
          
    return self.router.on_event(event_type)  # ty: ignore[deprecated]

tests/test_home_cleanup_phase_f6_debt.py::test_w1_inbound_router_defines_sendgrid_endpoint
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_f6_debt.py::test_w1_inbound_router_defines_sendgrid_endpoint
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_f6_debt.py::test_w1_inbound_router_defines_sendgrid_endpoint
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_f6_debt.py::test_w1_inbound_router_defines_sendgrid_endpoint
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_f6_debt.py::test_w1_inbound_router_defines_sendgrid_endpoint
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
26 passed, 21 warnings in 6.14s
```