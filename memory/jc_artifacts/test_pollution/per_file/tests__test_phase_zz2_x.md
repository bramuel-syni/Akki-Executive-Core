**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_zz2_x.py`

- **Bucket**: `PASS`
- **Duration**: 8.9 s
- **Return code**: 0

## STDOUT tail
```

tests/test_phase_zz2_x.py::test_zz2_x_fixture_module_carries_five_fixtures
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_zz2_x.py::test_zz2_x_fixture_module_carries_five_fixtures
tests/test_phase_zz2_x.py::test_zz2_x_fixture_404_when_env_disabled
tests/test_phase_zz2_x.py::test_zz2_x_fixture_stream_shape
tests/test_phase_zz2_x.py::test_zz2_x_fixture_stream_shape
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_zz2_x.py::test_zz2_x_fixture_module_carries_five_fixtures
tests/test_phase_zz2_x.py::test_zz2_x_fixture_404_when_env_disabled
tests/test_phase_zz2_x.py::test_zz2_x_fixture_stream_shape
tests/test_phase_zz2_x.py::test_zz2_x_fixture_stream_shape
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_zz2_x.py::test_zz2_x_fixture_module_carries_five_fixtures
tests/test_phase_zz2_x.py::test_zz2_x_fixture_404_when_env_disabled
tests/test_phase_zz2_x.py::test_zz2_x_fixture_stream_shape
tests/test_phase_zz2_x.py::test_zz2_x_fixture_stream_shape
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_phase_zz2_x.py:195: chat create skipped: 400
3 passed, 1 skipped, 39 warnings in 6.77s
```