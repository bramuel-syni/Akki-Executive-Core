**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution · confirmed polluter→polluted pair)

# Confirmed pollution pair

- **Polluter file**: `tests/test_phase4_2_http_transport_smoke.py`
- **Polluted file**: `tests/test_phase_p5_10_audit_panel_direct_linkage.py`
- **Cluster**: `env_or_motor_loop_state__p5_10`
- **FTT IDs covered**: FTT-017, FTT-018
- **Locked area polluter?**: no
- **Pair duration**: 5.35 s
- **Exit code**: 1

## Reproduction command
```bash
cd /app/backend && python -m pytest tests/test_phase4_2_http_transport_smoke.py tests/test_phase_p5_10_audit_panel_direct_linkage.py -q --no-header --tb=no -m 'not integration and not deploy_smoke and not runtime_playwright' -p no:cacheprovider
```

## STDOUT tail (failure output)
```
          
    @app.on_event("shutdown")

tests/test_phase_p5_10_audit_panel_direct_linkage.py::test_p5_10_cancelled_turn_does_not_break_next_turn_audit
  /usr/local/lib/python3.11/threading.py:254: RuntimeWarning: coroutine '_http_get_audit_panel.<locals>._do' was never awaited
    self._release_save = lock._release_save
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/test_phase_p5_10_audit_panel_direct_linkage.py::test_p5_10_legacy_positional_fallback_when_direct_link_missing
  /root/.venv/lib/python3.11/site-packages/bson/son.py:99: RuntimeWarning: coroutine '_http_get_audit_panel.<locals>._do' was never awaited
    yield from self.__keys
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/test_phase_p5_10_audit_panel_direct_linkage.py::test_p5_10_user_role_message_returns_404
  /usr/local/lib/python3.11/threading.py:910: RuntimeWarning: coroutine '_http_get_audit_panel.<locals>._do' was never awaited
    self._invoke_excepthook = _make_invoke_excepthook()
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_phase4_2_http_transport_smoke.py::test_internal_transport_openapi_hash_unchanged
FAILED tests/test_phase_p5_10_audit_panel_direct_linkage.py::test_p5_10_audit_panel_uses_direct_shield_audit_id
FAILED tests/test_phase_p5_10_audit_panel_direct_linkage.py::test_p5_10_cancelled_turn_does_not_break_next_turn_audit
FAILED tests/test_phase_p5_10_audit_panel_direct_linkage.py::test_p5_10_legacy_positional_fallback_when_direct_link_missing
FAILED tests/test_phase_p5_10_audit_panel_direct_linkage.py::test_p5_10_404_when_message_id_missing
FAILED tests/test_phase_p5_10_audit_panel_direct_linkage.py::test_p5_10_user_role_message_returns_404
6 failed, 7 passed, 24 warnings in 3.95s
```

## Suspected leaked state (static-signature hypothesis)
Per the cluster signature (search heuristic):

- `env_mutation_without_cleanup`
- `env_del_no_restore`
- `monkeypatch_setenv_module_scope`

Actual root cause requires source inspection of the polluter file and the polluted assertion. This MD records the *confirmed* pair by paired pytest execution; the fix-scope decision and leaked-state characterisation are deferred to the next sprint per the HARD STOP contract.