**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_qa_chunk_15.py`

- **Bucket**: `PASS`
- **Duration**: 8.06 s
- **Return code**: 0

## STDOUT tail
```
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

tests/test_qa_chunk_15.py::test_chunk15_qa016_cycle_step_nav_label_locked
  tests/test_qa_chunk_15.py:215: PytestWarning: The test <Function test_chunk15_qa016_cycle_step_nav_label_locked> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk15_qa016_cycle_step_nav_label_locked():

tests/test_qa_chunk_15.py::test_chunk15_no_new_direct_llm_calls
  tests/test_qa_chunk_15.py:235: PytestWarning: The test <Function test_chunk15_no_new_direct_llm_calls> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk15_no_new_direct_llm_calls():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
6 passed, 23 warnings in 6.25s
```