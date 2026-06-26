**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_t2_frontend_wire.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 4.95 s
- **Return code**: 1

## STDOUT tail
```

tests/test_t2_frontend_wire.py::test_t2_1_workspace_renders_four_filter_tabs_in_spec_order
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_t2_frontend_wire.py::test_t2_1_workspace_renders_four_filter_tabs_in_spec_order
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_t2_frontend_wire.py::test_t2_1_workspace_renders_four_filter_tabs_in_spec_order
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_t2_frontend_wire.py::test_t2_1_workspace_renders_four_filter_tabs_in_spec_order
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_t2_frontend_wire.py::test_t2_1_workspace_renders_four_filter_tabs_in_spec_order
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_t2_frontend_wire.py::test_t2_4_x6_dual_rag_bars_independent_colours
1 failed, 19 passed, 21 warnings in 3.69s
```