**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_home_cleanup_phase_e3.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 15.65 s
- **Return code**: 1

## STDOUT tail
```
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3.py::test_e3_document_drawer_mounted_on_every_primary_surface[surface0]
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3.py::test_e3_document_drawer_mounted_on_every_primary_surface[surface0]
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3.py::test_e3_document_drawer_mounted_on_every_primary_surface[surface0]
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3.py::test_e3_document_drawer_mounted_on_every_primary_surface[surface0]
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_home_cleanup_phase_e3.py::test_e3_drawer_five_ctas_all_canonical_urls
FAILED tests/test_home_cleanup_phase_e3.py::test_e3_backend_patch_document_endpoint_wired
FAILED tests/test_home_cleanup_phase_e3.py::test_e3_backend_intelligence_endpoints_wired
FAILED tests/test_home_cleanup_phase_e3.py::test_e3_backend_export_guard_allows_drafts_with_watermark_required
FAILED tests/test_home_cleanup_phase_e3.py::test_e3_intelligence_service_routes_through_shield
5 failed, 18 passed, 21 warnings in 14.28s
```