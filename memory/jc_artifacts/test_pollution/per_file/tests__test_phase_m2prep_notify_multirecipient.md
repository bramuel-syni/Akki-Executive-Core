**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_m2prep_notify_multirecipient.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 4.88 s
- **Return code**: 1

## STDOUT tail
```
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m2prep_notify_multirecipient.py::test_m2prep_parse_two_recipients
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m2prep_notify_multirecipient.py::test_m2prep_parse_two_recipients
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m2prep_notify_multirecipient.py::test_m2prep_parse_two_recipients
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m2prep_notify_multirecipient.py::test_m2prep_parse_two_recipients
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_phase_m2prep_notify_multirecipient.py::test_m2prep_sendgrid_called_with_both_addresses
FAILED tests/test_phase_m2prep_notify_multirecipient.py::test_m2prep_sendgrid_handles_whitespace_separated
FAILED tests/test_phase_m2prep_notify_multirecipient.py::test_m2prep_empty_env_no_sendgrid_no_500
FAILED tests/test_phase_m2prep_notify_multirecipient.py::test_m2prep_audit_log_has_recipient_count
4 failed, 7 passed, 21 warnings in 3.65s
```