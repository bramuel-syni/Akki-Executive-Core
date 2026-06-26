**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_patch_21_news.py`

- **Bucket**: `PASS`
- **Duration**: 6.53 s
- **Return code**: 0

## STDOUT tail
```
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

tests/test_patch_21_news.py::test_aggregator_parses_known_feed_correctly
  tests/test_patch_21_news.py:49: PytestWarning: The test <Function test_aggregator_parses_known_feed_correctly> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_aggregator_parses_known_feed_correctly():

tests/test_patch_21_news.py::test_aggregator_handles_empty_feed_gracefully
  tests/test_patch_21_news.py:78: PytestWarning: The test <Function test_aggregator_handles_empty_feed_gracefully> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_aggregator_handles_empty_feed_gracefully():

tests/test_patch_21_news.py::test_aggregator_strips_summary_html_and_caps_length
  tests/test_patch_21_news.py:83: PytestWarning: The test <Function test_aggregator_strips_summary_html_and_caps_length> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_aggregator_strips_summary_html_and_caps_length():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_patch_21_news.py:150: Cross-test cookie persistence — auth gate covered by FastAPI Depends
4 passed, 1 skipped, 24 warnings in 4.45s
```