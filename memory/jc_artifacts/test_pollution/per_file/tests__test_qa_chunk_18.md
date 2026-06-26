**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_qa_chunk_18.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 6.57 s
- **Return code**: 1

## STDOUT tail
```

tests/test_qa_chunk_18.py::test_chunk18_scheduler_lock_runs_once_per_bucket
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_qa_chunk_18.py::test_chunk18_scheduler_lock_runs_once_per_bucket
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_qa_chunk_18.py::test_chunk18_scheduler_lock_runs_once_per_bucket
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_qa_chunk_18.py::test_chunk18_scheduler_lock_runs_once_per_bucket
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_qa_chunk_18.py::test_chunk18_engine_hourly_cron_registered_in_server
  tests/test_qa_chunk_18.py:109: PytestWarning: The test <Function test_chunk18_engine_hourly_cron_registered_in_server> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk18_engine_hourly_cron_registered_in_server():

tests/test_qa_chunk_18.py::test_chunk18_no_new_direct_llm_calls
  tests/test_qa_chunk_18.py:280: PytestWarning: The test <Function test_chunk18_no_new_direct_llm_calls> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk18_no_new_direct_llm_calls():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_qa_chunk_18.py::test_chunk18_shield_invoke_records_exact_metering_when_sdk_returns_usage
FAILED tests/test_qa_chunk_18.py::test_chunk18_shield_invoke_falls_back_to_estimated_when_usage_missing
2 failed, 7 passed, 23 warnings in 4.62s
```