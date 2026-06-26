**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_wave_5_contextless_chat_e2e.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 5.96 s
- **Return code**: 1

## STDOUT tail
```
tests/test_wave_5_contextless_chat_e2e.py::test_wave5_create_get_patch_delete_no_header
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_wave_5_contextless_chat_e2e.py::test_wave5_create_get_patch_delete_no_header
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_wave_5_contextless_chat_e2e.py::test_wave5_create_get_patch_delete_no_header
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_wave_5_contextless_chat_e2e.py::test_wave5_create_get_patch_delete_no_header
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_wave_5_contextless_chat_e2e.py::test_wave5_create_get_patch_delete_no_header
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_wave_5_contextless_chat_e2e.py::test_wave5_create_get_patch_delete_no_header
FAILED tests/test_wave_5_contextless_chat_e2e.py::test_wave5_context_scoped_paths_remain_gated
2 failed, 1 passed, 21 warnings in 4.15s
```