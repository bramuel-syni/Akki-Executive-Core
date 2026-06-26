**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_iter15_board_pack.py`

- **Bucket**: `PASS`
- **Duration**: 0.39 s
- **Return code**: 0

## STDOUT tail
```
ssss                                                                     [100%]
=============================== warnings summary ===============================
tests/conftest.py:99
  /app/backend/tests/conftest.py:99: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as _StarletteTestClient  # noqa: E402

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [4] tests/test_iter15_board_pack.py: Patch 13 Phase 2 attempt — depends on live sandbox endpoint + LLM key; reclassified to Phase 4 (REWRITE).
4 skipped, 1 warning in 0.05s
```