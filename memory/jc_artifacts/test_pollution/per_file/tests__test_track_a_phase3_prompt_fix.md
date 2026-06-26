**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_track_a_phase3_prompt_fix.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 12.52 s
- **Return code**: 1

## STDOUT tail
```
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
FAILED tests/test_track_a_phase3_prompt_fix.py::test_banned_jargon_in_headline_blanked[Revenue ran 2.11\u03c3 above the mean across the trade book.]
FAILED tests/test_track_a_phase3_prompt_fix.py::test_banned_jargon_in_headline_blanked[Q1 actual sales standard deviation widened 14% YoY.]
FAILED tests/test_track_a_phase3_prompt_fix.py::test_banned_jargon_in_headline_blanked[Pricing-power variance lifted three regions above plan.]
FAILED tests/test_track_a_phase3_prompt_fix.py::test_banned_jargon_in_headline_blanked[January readings sit in the 95th percentile of the prior twelve months.]
FAILED tests/test_track_a_phase3_prompt_fix.py::test_forecast_meta_surfaces_in_response
FAILED tests/test_track_a_phase3_prompt_fix.py::test_bounded_retry_when_whats_likely_next_omitted
FAILED tests/test_track_a_phase3_prompt_fix.py::test_post_shield_validator_sets_per_tab_missing_flags
FAILED tests/test_track_a_phase3_prompt_fix.py::test_forecast_meta_passes_to_prompt_even_when_run_forecast_raises
FAILED tests/test_track_a_phase3_prompt_fix.py::test_logger_warning_on_swallowed_forecast_exception
9 failed, 4 passed, 21 warnings in 10.67s
```