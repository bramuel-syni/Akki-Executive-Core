**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_q4y_p1_c1_use_in_solva.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 8.28 s
- **Return code**: 1

## STDOUT tail
```

solva_app.py:108
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

akki_app.py:318
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

server.py:362
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

server.py:1303
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

server.py:1362
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_q4y_p1_c1_use_in_solva.py::test_q4y_c1_solva_router_has_question_branch
1 failed, 5 passed, 21 warnings in 6.43s
```