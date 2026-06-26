**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_track_a_phase3_narration.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 11.61 s
- **Return code**: 1

## STDOUT tail
```
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

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

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_track_a_phase3_narration.py::test_synthesize_returns_narration_payload
FAILED tests/test_track_a_phase3_narration.py::test_synthesize_handles_fenced_json_from_claude
FAILED tests/test_track_a_phase3_narration.py::test_synthesize_idempotent_cache_key
FAILED tests/test_track_a_phase3_narration.py::test_citation_resolver_drops_out_of_range
FAILED tests/test_track_a_phase3_narration.py::test_phase_1_and_2_regressions_still_pass
FAILED tests/test_track_a_phase3_narration.py::test_voice_lint_drops_banned_voice_observations
6 failed, 4 passed, 21 warnings in 9.35s
```