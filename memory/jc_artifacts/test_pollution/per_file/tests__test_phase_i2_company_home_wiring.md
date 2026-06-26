**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_i2_company_home_wiring.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 7.27 s
- **Return code**: 1

## STDOUT tail
```
tests/test_phase_i2_company_home_wiring.py::test_i2_endpoints_require_auth[/api/me/company-home/readiness?context_id=any]
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_i2_company_home_wiring.py::test_i2_endpoints_require_auth[/api/me/company-home/readiness?context_id=any]
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_i2_company_home_wiring.py::test_i2_endpoints_require_auth[/api/me/company-home/readiness?context_id=any]
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_i2_company_home_wiring.py::test_i2_endpoints_require_auth[/api/me/company-home/readiness?context_id=any]
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_i2_company_home_wiring.py::test_i2_endpoints_require_auth[/api/me/company-home/readiness?context_id=any]
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_phase_i2_company_home_wiring.py::test_i2_frontend_fetches_both_endpoints
FAILED tests/test_phase_i2_company_home_wiring.py::test_i2_click_routing_uses_context_filtered_routes_per_card
2 failed, 10 passed, 21 warnings in 5.79s
```