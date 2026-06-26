**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_j3_stage_4_5_frontend.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 4.95 s
- **Return code**: 1

## STDOUT tail
```

tests/test_j3_stage_4_5_frontend.py::test_j3_f1_g27_verbatim_trust_center_tooltip_copy
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_j3_stage_4_5_frontend.py::test_j3_f1_g27_verbatim_trust_center_tooltip_copy
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_j3_stage_4_5_frontend.py::test_j3_f1_g27_verbatim_trust_center_tooltip_copy
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_j3_stage_4_5_frontend.py::test_j3_f1_g27_verbatim_trust_center_tooltip_copy
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_j3_stage_4_5_frontend.py::test_j3_f1_g27_verbatim_trust_center_tooltip_copy
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_j3_stage_4_5_frontend.py::test_j3_f4_trust_center_page_mounts_tour_overlay_via_use_effect_chain
1 failed, 7 passed, 21 warnings in 3.69s
```