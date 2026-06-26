**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution · confirmed polluter→polluted pair)

# Confirmed pollution pair

- **Polluter file**: `tests/test_phase_p5_10_audit_panel_direct_linkage.py`
- **Polluted file**: `tests/test_track_b_phase2_task_lifecycle.py`
- **Cluster**: `tenant_resolver_stub_leak`
- **FTT IDs covered**: FTT-023
- **Locked area polluter?**: no
- **Pair duration**: 6.04 s
- **Exit code**: 1

## Reproduction command
```bash
cd /app/backend && python -m pytest tests/test_phase_p5_10_audit_panel_direct_linkage.py tests/test_track_b_phase2_task_lifecycle.py -q --no-header --tb=no -m 'not integration and not deploy_smoke and not runtime_playwright' -p no:cacheprovider
```

## STDOUT tail (failure output)
```
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
FAILED tests/test_track_b_phase2_task_lifecycle.py::test_commission_draft_to_active_and_audit
FAILED tests/test_track_b_phase2_task_lifecycle.py::test_close_active_to_closed_and_audit
FAILED tests/test_track_b_phase2_task_lifecycle.py::test_commission_idempotent_on_active
FAILED tests/test_track_b_phase2_task_lifecycle.py::test_close_idempotent_on_closed
FAILED tests/test_track_b_phase2_task_lifecycle.py::test_state_machine_guards
FAILED tests/test_track_b_phase2_task_lifecycle.py::test_cross_tenant_lifecycle_blocked
FAILED tests/test_track_b_phase2_task_lifecycle.py::test_filter_tab_counts_match_db
7 failed, 7 passed, 21 warnings in 4.34s
```

## Suspected leaked state (static-signature hypothesis)
Per the cluster signature (search heuristic):

- `module_level_dependency_override`
- `tenant_override_marker`
- `in_body_dependency_override`

Actual root cause requires source inspection of the polluter file and the polluted assertion. This MD records the *confirmed* pair by paired pytest execution; the fix-scope decision and leaked-state characterisation are deferred to the next sprint per the HARD STOP contract.