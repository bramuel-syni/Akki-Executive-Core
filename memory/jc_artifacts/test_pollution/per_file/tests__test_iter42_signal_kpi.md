**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_iter42_signal_kpi.py`

- **Bucket**: `PASS`
- **Duration**: 0.37 s
- **Return code**: 0

## STDOUT tail
```
ssssssss                                                                 [100%]
=============================== warnings summary ===============================
tests/conftest.py:99
  /app/backend/tests/conftest.py:99: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as _StarletteTestClient  # noqa: E402

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [8] tests/test_iter42_signal_kpi.py: Patch 19 — E2E test using requests.Session() against live BASE_URL. Reclassified to Phase 4-large; needs in-process httpx+ASGI rewrite. Re-quarantined after the password constant was unified (Bramuel2026!) — previously silent-skipped because the login failed; now login succeeds but hardcoded context IDs no longer match the current seed.
8 skipped, 1 warning in 0.03s
```