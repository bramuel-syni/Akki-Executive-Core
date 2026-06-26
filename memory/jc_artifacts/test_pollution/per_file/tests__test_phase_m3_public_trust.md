**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_m3_public_trust.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 8.07 s
- **Return code**: 1

## STDOUT tail
```
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m3_public_trust.py::test_m3_public_router_registered_in_server
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_no_auth_required
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_rejects_non_30d_window
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_cache_hit
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m3_public_trust.py::test_m3_public_router_registered_in_server
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_no_auth_required
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_rejects_non_30d_window
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_cache_hit
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m3_public_trust.py::test_m3_public_router_registered_in_server
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_no_auth_required
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_rejects_non_30d_window
tests/test_phase_m3_public_trust.py::test_m3_public_endpoint_cache_hit
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_phase_m3_public_trust.py::test_m3_public_router_registered_in_server
FAILED tests/test_phase_m3_public_trust.py::test_m3_velocity_tile_numeric_state_template
FAILED tests/test_phase_m3_public_trust.py::test_m3_velocity_tile_uses_akki_in_public_copy
3 failed, 13 passed, 39 warnings in 6.38s
```