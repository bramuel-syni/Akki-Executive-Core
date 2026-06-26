**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_qa_chunk_8.py`

- **Bucket**: `PASS`
- **Duration**: 15.09 s
- **Return code**: 0

## STDOUT tail
```

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

tests/test_qa_chunk_8.py::test_chunk8_rag_band_thresholds
  tests/test_qa_chunk_8.py:124: PytestWarning: The test <Function test_chunk8_rag_band_thresholds> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk8_rag_band_thresholds():

tests/test_qa_chunk_8.py::test_chunk8_can_transition_state_machine
  tests/test_qa_chunk_8.py:146: PytestWarning: The test <Function test_chunk8_can_transition_state_machine> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk8_can_transition_state_machine():

tests/test_qa_chunk_8.py::test_chunk8_referenced_doc_id_scan
  tests/test_qa_chunk_8.py:157: PytestWarning: The test <Function test_chunk8_referenced_doc_id_scan> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk8_referenced_doc_id_scan():

tests/test_qa_chunk_8.py::test_chunk8_normalise_structured_content_strips_junk
  tests/test_qa_chunk_8.py:169: PytestWarning: The test <Function test_chunk8_normalise_structured_content_strips_junk> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk8_normalise_structured_content_strips_junk():

tests/test_qa_chunk_8.py::test_chunk8_allowed_lifecycle_constant
  tests/test_qa_chunk_8.py:638: PytestWarning: The test <Function test_chunk8_allowed_lifecycle_constant> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk8_allowed_lifecycle_constant():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
25 passed, 26 warnings in 12.97s
```