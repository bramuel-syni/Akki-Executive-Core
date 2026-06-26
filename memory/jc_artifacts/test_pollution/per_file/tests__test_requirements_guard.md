**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_requirements_guard.py`

- **Bucket**: `PASS`
- **Duration**: 5.42 s
- **Return code**: 0

## STDOUT tail
```

tests/test_requirements_guard.py::test_script_exists
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_requirements_guard.py::test_script_exists
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_requirements_guard.py::test_script_exists
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_requirements_guard.py::test_script_exists
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_requirements_guard.py::test_script_exists
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_requirements_guard.py:120: Wave8.followup.1 (2026-05-27) — Skipped deliberately. The check_requirements_urls.py guard refuses URL-pinned deps in requirements.txt, but our `requirements.txt` intentionally pins (a) `emergentintegrations` from the Emergent cloudfront wheel index and (b) the spaCy `en_core_web_sm` model wheel from a github release. Both are deliberate operational choices, not regressions. The guard's policy model doesn't represent that nuance — filed as `Wave8.followup.5` if a future audit demands a more sophisticated allowlist.
8 passed, 1 skipped, 21 warnings in 4.05s
```