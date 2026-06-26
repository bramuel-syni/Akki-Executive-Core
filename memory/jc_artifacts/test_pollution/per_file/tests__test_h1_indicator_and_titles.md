**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_h1_indicator_and_titles.py`

- **Bucket**: `PASS`
- **Duration**: 6.47 s
- **Return code**: 0

## STDOUT tail
```
  
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

tests/test_h1_indicator_and_titles.py::test_zero_activity_storyline_no_longer_says_on_standby
  tests/test_h1_indicator_and_titles.py:152: PytestWarning: The test <Function test_zero_activity_storyline_no_longer_says_on_standby> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_zero_activity_storyline_no_longer_says_on_standby():

tests/test_h1_indicator_and_titles.py::test_pre_v1_storyline_says_predates_shield
  tests/test_h1_indicator_and_titles.py:162: PytestWarning: The test <Function test_pre_v1_storyline_says_predates_shield> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_pre_v1_storyline_says_predates_shield():

tests/test_h1_indicator_and_titles.py::test_browser_tab_title_is_akki_for_executives
  tests/test_h1_indicator_and_titles.py:173: PytestWarning: The test <Function test_browser_tab_title_is_akki_for_executives> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_browser_tab_title_is_akki_for_executives():

tests/test_h1_indicator_and_titles.py::test_open_graph_and_twitter_cards_present
  tests/test_h1_indicator_and_titles.py:189: PytestWarning: The test <Function test_open_graph_and_twitter_cards_present> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_open_graph_and_twitter_cards_present():

tests/test_h1_indicator_and_titles.py::test_trust_center_us_spelling_in_appshell_footer
  tests/test_h1_indicator_and_titles.py:204: PytestWarning: The test <Function test_trust_center_us_spelling_in_appshell_footer> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_trust_center_us_spelling_in_appshell_footer():

tests/test_h1_indicator_and_titles.py::test_trust_center_us_spelling_in_tenant_settings
  tests/test_h1_indicator_and_titles.py:212: PytestWarning: The test <Function test_trust_center_us_spelling_in_tenant_settings> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_trust_center_us_spelling_in_tenant_settings():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
8 passed, 27 warnings in 4.63s
```