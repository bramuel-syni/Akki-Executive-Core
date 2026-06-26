**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_patch_25_news_geo.py`

- **Bucket**: `PASS`
- **Duration**: 6.46 s
- **Return code**: 0

## STDOUT tail
```

server.py:1362
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_patch_25_news_geo.py::test_diversify_5_items_across_3_sources
  tests/test_patch_25_news_geo.py:41: PytestWarning: The test <Function test_diversify_5_items_across_3_sources> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_diversify_5_items_across_3_sources():

tests/test_patch_25_news_geo.py::test_diversify_no_dominance_at_limit_5_with_5_sources
  tests/test_patch_25_news_geo.py:62: PytestWarning: The test <Function test_diversify_no_dominance_at_limit_5_with_5_sources> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_diversify_no_dominance_at_limit_5_with_5_sources():

tests/test_patch_25_news_geo.py::test_diversify_handles_empty
  tests/test_patch_25_news_geo.py:74: PytestWarning: The test <Function test_diversify_handles_empty> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_diversify_handles_empty():

tests/test_patch_25_news_geo.py::test_diversify_under_limit
  tests/test_patch_25_news_geo.py:78: PytestWarning: The test <Function test_diversify_under_limit> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_diversify_under_limit():

tests/test_patch_25_news_geo.py::test_resolve_region_profile_country_wins
  tests/test_patch_25_news_geo.py:87: PytestWarning: The test <Function test_resolve_region_profile_country_wins> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_resolve_region_profile_country_wins():

tests/test_patch_25_news_geo.py::test_resolve_region_top_level_country_when_no_profile
  tests/test_patch_25_news_geo.py:92: PytestWarning: The test <Function test_resolve_region_top_level_country_when_no_profile> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_resolve_region_top_level_country_when_no_profile():

tests/test_patch_25_news_geo.py::test_resolve_region_workspace_country_when_no_account_country
  tests/test_patch_25_news_geo.py:97: PytestWarning: The test <Function test_resolve_region_workspace_country_when_no_account_country> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_resolve_region_workspace_country_when_no_account_country():

tests/test_patch_25_news_geo.py::test_resolve_region_accept_language_when_nothing_else
  tests/test_patch_25_news_geo.py:103: PytestWarning: The test <Function test_resolve_region_accept_language_when_nothing_else> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_resolve_region_accept_language_when_nothing_else():

tests/test_patch_25_news_geo.py::test_resolve_region_global_fallback
  tests/test_patch_25_news_geo.py:110: PytestWarning: The test <Function test_resolve_region_global_fallback> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_resolve_region_global_fallback():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_patch_25_news_geo.py:217: Cross-test request-scope account caching — see docstring
11 passed, 1 skipped, 30 warnings in 4.66s
```