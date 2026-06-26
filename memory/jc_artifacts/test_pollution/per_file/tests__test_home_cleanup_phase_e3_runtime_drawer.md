**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_home_cleanup_phase_e3_runtime_drawer.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 4.88 s
- **Return code**: 1

## STDOUT tail
```

tests/test_home_cleanup_phase_e3_runtime_drawer.py::test_no_inline_legacy_drawer_definitions_on_doc_listing_surfaces
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3_runtime_drawer.py::test_no_inline_legacy_drawer_definitions_on_doc_listing_surfaces
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3_runtime_drawer.py::test_no_inline_legacy_drawer_definitions_on_doc_listing_surfaces
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3_runtime_drawer.py::test_no_inline_legacy_drawer_definitions_on_doc_listing_surfaces
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3_runtime_drawer.py::test_no_inline_legacy_drawer_definitions_on_doc_listing_surfaces
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_home_cleanup_phase_e3_runtime_drawer.py::test_document_drawer_has_5_spec_ctas_with_canonical_urls
1 failed, 29 passed, 21 warnings in 3.67s
```