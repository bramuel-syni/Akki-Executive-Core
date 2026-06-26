**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_qa_chunk_17.py`

- **Bucket**: `PASS`
- **Duration**: 4.96 s
- **Return code**: 0

## STDOUT tail
```

tests/test_qa_chunk_17.py::test_chunk17_c17_002_admin_no_data_fixture_seeded
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_qa_chunk_17.py::test_chunk17_c17_002_admin_no_data_fixture_seeded
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_qa_chunk_17.py::test_chunk17_c17_002_admin_no_data_fixture_seeded
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_qa_chunk_17.py::test_chunk17_c17_001_edit_goal_row_removed
  tests/test_qa_chunk_17.py:137: PytestWarning: The test <Function test_chunk17_c17_001_edit_goal_row_removed> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk17_c17_001_edit_goal_row_removed():

tests/test_qa_chunk_17.py::test_chunk17_c17_004_solva_prose_outer_overflow_class
  tests/test_qa_chunk_17.py:170: PytestWarning: The test <Function test_chunk17_c17_004_solva_prose_outer_overflow_class> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk17_c17_004_solva_prose_outer_overflow_class():

tests/test_qa_chunk_17.py::test_chunk17_qa014_cycle_quickactions_spacer_present
  tests/test_qa_chunk_17.py:212: PytestWarning: The test <Function test_chunk17_qa014_cycle_quickactions_spacer_present> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk17_qa014_cycle_quickactions_spacer_present():

tests/test_qa_chunk_17.py::test_chunk17_item7_smoke_probe_defensive_fallback
  tests/test_qa_chunk_17.py:227: PytestWarning: The test <Function test_chunk17_item7_smoke_probe_defensive_fallback> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk17_item7_smoke_probe_defensive_fallback():

tests/test_qa_chunk_17.py::test_chunk17_no_new_direct_llm_calls
  tests/test_qa_chunk_17.py:245: PytestWarning: The test <Function test_chunk17_no_new_direct_llm_calls> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk17_no_new_direct_llm_calls():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
8 passed, 26 warnings in 3.67s
```