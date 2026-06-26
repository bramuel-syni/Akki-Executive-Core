**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution · confirmed polluter→polluted pair)

# Confirmed pollution pair

- **Polluter file**: `tests/test_phase4_2_http_transport_smoke.py`
- **Polluted file**: `tests/test_phase_p5_7_5_bounce_webhook.py`
- **Cluster**: `sendgrid_env_stub_leak`
- **FTT IDs covered**: FTT-019, FTT-020, FTT-021, FTT-022
- **Locked area polluter?**: no
- **Pair duration**: 5.35 s
- **Exit code**: 1

## Reproduction command
```bash
cd /app/backend && python -m pytest tests/test_phase4_2_http_transport_smoke.py tests/test_phase_p5_7_5_bounce_webhook.py -q --no-header --tb=no -m 'not integration and not deploy_smoke and not runtime_playwright' -p no:cacheprovider
```

## STDOUT tail (failure output)
```
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_phase_p5_7_5_bounce_webhook.py::test_p5_7_5_delivered_event_writes_delivered_bucket
  /usr/local/lib/python3.11/traceback.py:425: RuntimeWarning: coroutine 'test_p5_7_5_bounce_event_writes_failed_bucket_on_application_row.<locals>._do' was never awaited
    result.append(FrameSummary(
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/test_phase_p5_7_5_bounce_webhook.py::test_p5_7_5_invalid_body_returns_400
  /root/.venv/lib/python3.11/site-packages/_pytest/_code/code.py:368: RuntimeWarning: coroutine 'test_p5_7_5_delivered_event_writes_delivered_bucket.<locals>._do' was never awaited
    yield TracebackEntry(cur_)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

tests/test_phase_p5_7_5_bounce_webhook.py::test_p5_7_5_invalid_body_returns_400
  /root/.venv/lib/python3.11/site-packages/_pytest/_code/code.py:368: RuntimeWarning: coroutine 'test_p5_7_5_unknown_recipient_does_not_create_row.<locals>._do' was never awaited
    yield TracebackEntry(cur_)
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_phase4_2_http_transport_smoke.py::test_internal_transport_openapi_hash_unchanged
FAILED tests/test_phase_p5_7_5_bounce_webhook.py::test_p5_7_5_bounce_event_writes_failed_bucket_on_application_row
FAILED tests/test_phase_p5_7_5_bounce_webhook.py::test_p5_7_5_delivered_event_writes_delivered_bucket
FAILED tests/test_phase_p5_7_5_bounce_webhook.py::test_p5_7_5_unknown_recipient_does_not_create_row
FAILED tests/test_phase_p5_7_5_bounce_webhook.py::test_p5_7_5_invalid_body_returns_400
5 failed, 8 passed, 24 warnings in 3.93s
```

## Suspected leaked state (static-signature hypothesis)
Per the cluster signature (search heuristic):

- `sendgrid_env_marker`
- `env_mutation_without_cleanup`
- `env_del_no_restore`

Actual root cause requires source inspection of the polluter file and the polluted assertion. This MD records the *confirmed* pair by paired pytest execution; the fix-scope decision and leaked-state characterisation are deferred to the next sprint per the HARD STOP contract.