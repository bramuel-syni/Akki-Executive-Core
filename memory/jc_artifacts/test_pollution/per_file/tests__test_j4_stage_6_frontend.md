**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_j4_stage_6_frontend.py`

- **Bucket**: `FAIL_DETERMINISTIC`
- **Duration**: 4.8 s
- **Return code**: 1

## STDOUT tail
```

tests/test_j4_stage_6_frontend.py::test_j4_f1_first_session_solve_door_uses_starter_param_chain
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_j4_stage_6_frontend.py::test_j4_f1_first_session_solve_door_uses_starter_param_chain
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_j4_stage_6_frontend.py::test_j4_f1_first_session_solve_door_uses_starter_param_chain
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_j4_stage_6_frontend.py::test_j4_f1_first_session_solve_door_uses_starter_param_chain
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_j4_stage_6_frontend.py::test_j4_f1_first_session_solve_door_uses_starter_param_chain
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_j4_stage_6_frontend.py::test_j4_f4_phase_d_session_reads_starter_and_sets_draft
1 failed, 8 passed, 21 warnings in 3.62s
```