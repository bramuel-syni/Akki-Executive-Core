**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE.md §2.3` (post-A+D B.2 remeasure)

# B.2 remeasure · `tests/test_phase_p2_b6_admin_force_reset.py`

- **Polluted file**: `tests/test_track_b_phase_b5_g6_notes_autosave.py`
- **Pre-A+D bucket**: `CONFIRMED_POLLUTER` (from P5.7-HOLDOUT-FINISHER)
- **Post-A+D bucket**: `CONFIRMED_POLLUTER` (7.71 s · exit 1)
- **Sample-recheck bucket**: `CONFIRMED_POLLUTER` · consistent: **True**
- **Disposition**: **REMAINING**
- **Locked area polluter?**: no

## Reproduction command
```bash
cd /app/backend && python -m pytest tests/test_phase_p2_b6_admin_force_reset.py tests/test_track_b_phase_b5_g6_notes_autosave.py -q --no-header --tb=short -m 'not integration and not deploy_smoke and not runtime_playwright' -p no:cacheprovider
```

## STDOUT tail (post-A+D run)
```
  
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
FAILED tests/test_track_b_phase_b5_g6_notes_autosave.py::test_patch_notes_sets_notes_updated_at
FAILED tests/test_track_b_phase_b5_g6_notes_autosave.py::test_patch_empty_notes_clears_field_and_bumps_timestamp
FAILED tests/test_track_b_phase_b5_g6_notes_autosave.py::test_patch_notes_idempotency_safe_for_autosave_debounce
3 failed, 4 passed, 21 warnings in 5.78s
```