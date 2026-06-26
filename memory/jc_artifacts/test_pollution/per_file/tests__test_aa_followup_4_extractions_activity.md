**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_aa_followup_4_extractions_activity.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 6.05 s
- **Return code**: 1

## STDOUT tail
```

tests/test_aa_followup_4_extractions_activity.py::test_aa_f4_router_module_exists_and_exposes_router
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_aa_followup_4_extractions_activity.py::test_aa_f4_router_module_exists_and_exposes_router
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_aa_followup_4_extractions_activity.py::test_aa_f4_router_module_exists_and_exposes_router
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_aa_followup_4_extractions_activity.py::test_aa_f4_router_module_exists_and_exposes_router
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_aa_followup_4_extractions_activity.py::test_aa_f4_router_module_exists_and_exposes_router
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_aa_followup_4_extractions_activity.py::test_aa_f4_router_registered_in_server
1 failed, 7 passed, 21 warnings in 4.16s
```