**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_work_studio_briefings_visible.py`

- **Bucket**: `PASS`
- **Duration**: 5.88 s
- **Return code**: 0

## STDOUT tail
```

tests/test_work_studio_briefings_visible.py::test_briefings_endpoint_shape_is_documented_and_stable
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_work_studio_briefings_visible.py::test_briefings_endpoint_shape_is_documented_and_stable
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_work_studio_briefings_visible.py::test_briefings_endpoint_shape_is_documented_and_stable
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_work_studio_briefings_visible.py::test_briefings_endpoint_shape_is_documented_and_stable
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_work_studio_briefings_visible.py::test_briefings_endpoint_shape_is_documented_and_stable
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_work_studio_briefings_visible.py:105: Patch 19 — freshly-created briefing visibility depends on briefings list filter contract that diverged from this test. Other test in this file remains green.
1 passed, 1 skipped, 21 warnings in 4.55s
```