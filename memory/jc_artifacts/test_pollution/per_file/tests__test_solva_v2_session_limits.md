**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_solva_v2_session_limits.py`

- **Bucket**: `PASS`
- **Duration**: 5.47 s
- **Return code**: 0

## STDOUT tail
```
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_solva_v2_session_limits.py::test_stale_session_cron_requires_secret
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_solva_v2_session_limits.py::test_stale_session_cron_requires_secret
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_solva_v2_session_limits.py::test_stale_session_cron_requires_secret
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_solva_v2_session_limits.py::test_stale_session_cron_requires_secret
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_solva_v2_session_limits.py:71: Patch 19 — concurrent-session limit changed across Solva v2 versions. Needs rewrite.
SKIPPED [1] tests/test_solva_v2_session_limits.py:117: Patch 19 — max-turns-per-session limit changed; needs rewrite.
SKIPPED [1] tests/test_solva_v2_session_limits.py:179: Patch 19 — stale-session cron path moved; needs rewrite to hit the new admin route.
2 passed, 3 skipped, 24 warnings in 4.17s
```