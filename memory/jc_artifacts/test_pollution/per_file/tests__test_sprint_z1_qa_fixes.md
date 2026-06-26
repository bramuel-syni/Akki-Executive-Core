**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_sprint_z1_qa_fixes.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 5.37 s
- **Return code**: 1

## STDOUT tail
```
tests/test_sprint_z1_qa_fixes.py::test_supported_models_opus_id_is_valid
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_sprint_z1_qa_fixes.py::test_supported_models_opus_id_is_valid
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_sprint_z1_qa_fixes.py::test_supported_models_opus_id_is_valid
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_sprint_z1_qa_fixes.py::test_supported_models_opus_id_is_valid
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_sprint_z1_qa_fixes.py::test_supported_models_opus_id_is_valid
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_sprint_z1_qa_fixes.py::test_model_fallback_cascade_is_ordered
FAILED tests/test_sprint_z1_qa_fixes.py::test_cascade_starting_from_strips_the_failing_id
2 failed, 13 passed, 21 warnings in 3.92s
```