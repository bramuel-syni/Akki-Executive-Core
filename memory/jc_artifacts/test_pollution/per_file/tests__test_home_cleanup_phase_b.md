**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_home_cleanup_phase_b.py`

- **Bucket**: `PASS`
- **Duration**: 0.37 s
- **Return code**: 0

## STDOUT tail
```
ssssssssssssss                                                           [100%]
=============================== warnings summary ===============================
tests/conftest.py:99
  /app/backend/tests/conftest.py:99: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as _StarletteTestClient  # noqa: E402

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [14] tests/test_home_cleanup_phase_b.py: Phase I.1 archived Home2.jsx; Phase B cleanup tests no longer apply.
14 skipped, 1 warning in 0.03s
```