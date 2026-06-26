**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_iter71_studio_blocks.py`

- **Bucket**: `PASS`
- **Duration**: 0.39 s
- **Return code**: 0

## STDOUT tail
```
sssssssssssss                                                            [100%]
=============================== warnings summary ===============================
tests/conftest.py:99
  /app/backend/tests/conftest.py:99: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as _StarletteTestClient  # noqa: E402

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [13] tests/test_iter71_studio_blocks.py: Patch 8 quarantined — pre-existing failures from before autonomous sprint. See SYSTEM_STATE §7.
13 skipped, 1 warning in 0.04s
```