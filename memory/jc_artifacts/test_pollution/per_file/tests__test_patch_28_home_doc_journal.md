**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_patch_28_home_doc_journal.py`

- **Bucket**: `PASS`
- **Duration**: 5.91 s
- **Return code**: 0

## STDOUT tail
```
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

tests/test_patch_28_home_doc_journal.py::test_home2_hero_copy_variants_present_in_source
  tests/test_patch_28_home_doc_journal.py:31: PytestWarning: The test <Function test_home2_hero_copy_variants_present_in_source> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_home2_hero_copy_variants_present_in_source():

tests/test_patch_28_home_doc_journal.py::test_modal_sizing_rule_applied_in_dialog
  tests/test_patch_28_home_doc_journal.py:150: PytestWarning: The test <Function test_modal_sizing_rule_applied_in_dialog> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_modal_sizing_rule_applied_in_dialog():

tests/test_patch_28_home_doc_journal.py::test_monitor_goal_drawer_present_in_source
  tests/test_patch_28_home_doc_journal.py:166: PytestWarning: The test <Function test_monitor_goal_drawer_present_in_source> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_monitor_goal_drawer_present_in_source():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
4 passed, 24 warnings in 4.22s
```