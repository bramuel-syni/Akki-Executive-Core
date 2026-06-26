**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution · confirmed polluter→polluted pair · holdout-finisher)

# Confirmed pollution pair (holdout-finisher #9)

- **Polluter file**: `tests/test_phase_p3_2_cookie_hardening.py`
- **Polluted file**: `tests/test_track_b_phase_b5_g6_notes_autosave.py`
- **Cluster**: `autosave_debounce_timer_leak`
- **FTT IDs covered**: FTT-024, FTT-025, FTT-026
- **Locked area polluter?**: no
- **Pair duration**: 6.82 s
- **Exit code**: 1

## Reproduction command
```bash
cd /app/backend && python -m pytest tests/test_phase_p3_2_cookie_hardening.py tests/test_track_b_phase_b5_g6_notes_autosave.py -q --no-header --tb=no -m 'not integration and not deploy_smoke and not runtime_playwright' -p no:cacheprovider
```

## STDOUT tail (failure output)
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
3 failed, 2 passed, 21 warnings in 4.70s
```

Discovered via the holdout-finisher full predecessor sweep (vs. the cluster-narrowed bisect in P5.7-BISECT). The cluster's static signature did NOT include this polluter; only the full sweep surfaced it. Confirm-before-fix discipline preserved: paired pytest invocation validated the pair; sample-recheck consistent.