**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution · confirmed polluter→polluted pair)

# Confirmed pollution pair

- **Polluter file**: `tests/test_phase4_2_http_transport_smoke.py`
- **Polluted file**: `tests/test_phase_p3_2_cookie_hardening.py`
- **Cluster**: `env_or_motor_loop_state__p3_2`
- **FTT IDs covered**: FTT-015, FTT-016
- **Locked area polluter?**: no
- **Pair duration**: 6.68 s
- **Exit code**: 1

## Reproduction command
```bash
cd /app/backend && python -m pytest tests/test_phase4_2_http_transport_smoke.py tests/test_phase_p3_2_cookie_hardening.py -q --no-header --tb=no -m 'not integration and not deploy_smoke and not runtime_playwright' -p no:cacheprovider
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
FAILED tests/test_phase4_2_http_transport_smoke.py::test_internal_transport_openapi_hash_unchanged
FAILED tests/test_phase_p3_2_cookie_hardening.py::test_p3_2_login_cookie_attributes
FAILED tests/test_phase_p3_2_cookie_hardening.py::test_p3_2_csrf_cookie_samesite_lax
3 failed, 7 passed, 21 warnings in 5.10s
```

## Suspected leaked state (static-signature hypothesis)
Per the cluster signature (search heuristic):

- `env_mutation_without_cleanup`
- `env_del_no_restore`
- `monkeypatch_setenv_module_scope`

Actual root cause requires source inspection of the polluter file and the polluted assertion. This MD records the *confirmed* pair by paired pytest execution; the fix-scope decision and leaked-state characterisation are deferred to the next sprint per the HARD STOP contract.