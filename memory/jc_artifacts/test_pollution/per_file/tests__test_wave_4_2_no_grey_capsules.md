**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_wave_4_2_no_grey_capsules.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 5.55 s
- **Return code**: 1

## STDOUT tail
```

tests/test_wave_4_2_no_grey_capsules.py::test_w42_swept_sites_no_grey_capsules
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_wave_4_2_no_grey_capsules.py::test_w42_swept_sites_no_grey_capsules
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_wave_4_2_no_grey_capsules.py::test_w42_swept_sites_no_grey_capsules
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_wave_4_2_no_grey_capsules.py::test_w42_swept_sites_no_grey_capsules
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_wave_4_2_no_grey_capsules.py::test_w42_swept_sites_no_grey_capsules
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_wave_4_2_no_grey_capsules.py::test_w42_global_capsule_grep_clean
1 failed, 4 passed, 1 deselected, 21 warnings in 4.06s
```