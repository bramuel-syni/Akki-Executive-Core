**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_m_workstudio_noise.py`

- **Bucket**: `PASS`
- **Duration**: 4.89 s
- **Return code**: 0

## STDOUT tail
```
tests/test_phase_m_workstudio_noise.py::test_m_M1c_context_actions_unconditionally_rendered
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m_workstudio_noise.py::test_m_M1c_context_actions_unconditionally_rendered
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m_workstudio_noise.py::test_m_M1c_context_actions_unconditionally_rendered
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m_workstudio_noise.py::test_m_M1c_context_actions_unconditionally_rendered
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_m_workstudio_noise.py::test_m_M1c_context_actions_unconditionally_rendered
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_phase_m_workstudio_noise.py:67: Superseded by Phase Z-slice-2 (2026-05-27) — DocumentCardsSection REMOVED + main-board tab listing un-gated. See `test_phase_z_documents_journal.py::test_Z2_k_main_board_tab_no_longer_gated_off_listing` for the post-Z lock.
SKIPPED [1] tests/test_phase_m_workstudio_noise.py:85: Superseded by Phase Z-slice-2 (2026-05-27) — main-board tab listing un-gated; the listing now surfaces unified docs by category. See `test_phase_z_documents_journal.py::test_Z2_k_main_board_tab_no_longer_gated_off_listing`.
11 passed, 2 skipped, 21 warnings in 3.67s
```