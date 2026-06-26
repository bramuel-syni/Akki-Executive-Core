**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_f1_capability_gaps.py`

- **Bucket**: `PASS`
- **Duration**: 9.56 s
- **Return code**: 0

## STDOUT tail
```
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

tests/test_phase_f1_capability_gaps.py::test_p2_extract_text_png_ocr
  tests/test_phase_f1_capability_gaps.py:388: PytestWarning: The test <Function test_p2_extract_text_png_ocr> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_p2_extract_text_png_ocr():

tests/test_phase_f1_capability_gaps.py::test_p2_extract_text_xlsx
  tests/test_phase_f1_capability_gaps.py:404: PytestWarning: The test <Function test_p2_extract_text_xlsx> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_p2_extract_text_xlsx():

tests/test_phase_f1_capability_gaps.py::test_p2_extract_text_csv
  tests/test_phase_f1_capability_gaps.py:420: PytestWarning: The test <Function test_p2_extract_text_csv> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_p2_extract_text_csv():

tests/test_phase_f1_capability_gaps.py::test_p2_extract_text_corrupted_image_graceful
  tests/test_phase_f1_capability_gaps.py:429: PytestWarning: The test <Function test_p2_extract_text_corrupted_image_graceful> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_p2_extract_text_corrupted_image_graceful():

tests/test_phase_f1_capability_gaps.py::test_p2_image_routing_does_not_crash_on_empty_image
  tests/test_phase_f1_capability_gaps.py:438: PytestWarning: The test <Function test_p2_image_routing_does_not_crash_on_empty_image> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_p2_image_routing_does_not_crash_on_empty_image():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_phase_f1_capability_gaps.py:391: tesseract binary not on PATH; install tesseract-ocr to run.
13 passed, 1 skipped, 26 warnings in 7.58s
```