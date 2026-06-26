**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_track_b_phase1_signin_begin.py`

- **Bucket**: `PASS`
- **Duration**: 5.1 s
- **Return code**: 0

## STDOUT tail
```
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_track_b_phase1_signin_begin.py::test_fig7_first_session_begin_button_no_low_contrast_disabled
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_track_b_phase1_signin_begin.py::test_fig7_first_session_begin_button_no_low_contrast_disabled
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_track_b_phase1_signin_begin.py::test_fig7_first_session_begin_button_no_low_contrast_disabled
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_track_b_phase1_signin_begin.py::test_fig7_first_session_begin_button_no_low_contrast_disabled
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_track_b_phase1_signin_begin.py:153: Fig 7 live-DOM trace script missing at /tmp/. Run the v2 scaffold step or set PREVIEW_URL to skip the trace.
SKIPPED [1] tests/test_track_b_phase1_signin_begin.py:195: Fig 20 BLOCKED_NEED_SCREENSHOT — literal interpretation (redirect / to /signin for unauth) would break marketing funnel. Real fix scope unknown without the Fig 20 screenshot.
SKIPPED [1] tests/test_track_b_phase1_signin_begin.py:206: Fig 22 BLOCKED_NEED_SCREENSHOT — multiple candidate root causes (OAuth callback, idle-timeout, set-password gate, sign-in toast). Cannot pinpoint without the Fig 22 screenshot.
6 passed, 3 skipped, 21 warnings in 3.79s
```