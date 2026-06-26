**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_aa_slice_7_orthogonality_wire.py`

- **Bucket**: `PASS_NO_TESTS`
- **Duration**: 0.4 s
- **Return code**: 5

## STDOUT tail
```

=============================== warnings summary ===============================
tests/conftest.py:99
  /app/backend/tests/conftest.py:99: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as _StarletteTestClient  # noqa: E402

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1 deselected, 1 warning in 0.05s
```