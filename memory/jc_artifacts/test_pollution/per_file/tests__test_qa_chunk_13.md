**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_qa_chunk_13.py`

- **Bucket**: `PASS`
- **Duration**: 8.06 s
- **Return code**: 0

## STDOUT tail
```
tests/test_qa_chunk_13.py::test_chunk13_classify_paused_when_status_active_and_stale_24h
  tests/test_qa_chunk_13.py:61: PytestWarning: The test <Function test_chunk13_classify_paused_when_status_active_and_stale_24h> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_paused_when_status_active_and_stale_24h():

tests/test_qa_chunk_13.py::test_chunk13_classify_paused_when_status_active_and_far_stale
  tests/test_qa_chunk_13.py:66: PytestWarning: The test <Function test_chunk13_classify_paused_when_status_active_and_far_stale> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_paused_when_status_active_and_far_stale():

tests/test_qa_chunk_13.py::test_chunk13_classify_complete_when_status_completed
  tests/test_qa_chunk_13.py:70: PytestWarning: The test <Function test_chunk13_classify_complete_when_status_completed> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_complete_when_status_completed():

tests/test_qa_chunk_13.py::test_chunk13_classify_complete_when_layer_state_done
  tests/test_qa_chunk_13.py:74: PytestWarning: The test <Function test_chunk13_classify_complete_when_layer_state_done> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_complete_when_layer_state_done():

tests/test_qa_chunk_13.py::test_chunk13_classify_refused_when_status_refused
  tests/test_qa_chunk_13.py:80: PytestWarning: The test <Function test_chunk13_classify_refused_when_status_refused> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_refused_when_status_refused():

tests/test_qa_chunk_13.py::test_chunk13_classify_refused_when_status_abandoned
  tests/test_qa_chunk_13.py:84: PytestWarning: The test <Function test_chunk13_classify_refused_when_status_abandoned> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_refused_when_status_abandoned():

tests/test_qa_chunk_13.py::test_chunk13_classify_refused_when_layer_state_refused
  tests/test_qa_chunk_13.py:90: PytestWarning: The test <Function test_chunk13_classify_refused_when_layer_state_refused> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_refused_when_layer_state_refused():

tests/test_qa_chunk_13.py::test_chunk13_classify_active_when_no_timestamps
  tests/test_qa_chunk_13.py:96: PytestWarning: The test <Function test_chunk13_classify_active_when_no_timestamps> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_active_when_no_timestamps():

tests/test_qa_chunk_13.py::test_chunk13_classify_handles_datetime_object
  tests/test_qa_chunk_13.py:103: PytestWarning: The test <Function test_chunk13_classify_handles_datetime_object> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_handles_datetime_object():

tests/test_qa_chunk_13.py::test_chunk13_classify_terminal_state_wins_over_recency
  tests/test_qa_chunk_13.py:112: PytestWarning: The test <Function test_chunk13_classify_terminal_state_wins_over_recency> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_classify_terminal_state_wins_over_recency():

tests/test_qa_chunk_13.py::test_chunk13_tally_groups_all_four_buckets_plus_all
  tests/test_qa_chunk_13.py:117: PytestWarning: The test <Function test_chunk13_tally_groups_all_four_buckets_plus_all> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_tally_groups_all_four_buckets_plus_all():

tests/test_qa_chunk_13.py::test_chunk13_no_new_direct_llm_calls
  tests/test_qa_chunk_13.py:342: PytestWarning: The test <Function test_chunk13_no_new_direct_llm_calls> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_chunk13_no_new_direct_llm_calls():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
18 passed, 34 warnings in 6.33s
```