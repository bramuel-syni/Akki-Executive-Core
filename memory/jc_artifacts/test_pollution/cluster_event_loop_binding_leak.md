**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · event_loop_binding_leak)

# Pollution cluster — `event_loop_binding_leak`

- **FTT IDs**: FTT-002, FTT-003
- **Polluted targets**: 2
  - `tests/characterisation/test_chat_roundtrip_golden.py::test_chat_roundtrip_golden_shape`
  - `tests/test_chat_fluency_no_shield_leak.py::test_chat_response_does_not_leak_shield_mechanics`

## Leaked state
Motor AsyncIOMotorClient (`db` module-singleton) is bound to the FIRST event loop that awaits it. The conftest session-loop fixture pins async tests to one loop, but `asyncio.run(...)` called from sync tests spins up a fresh loop, latches motor to it transiently, then CLOSES that loop. Any subsequent session-loop await on `db` then hits `RuntimeError: Event loop is closed`.

## Isolation passes
- ✅ PASS in isolation — `tests/characterisation/test_chat_roundtrip_golden.py::test_chat_roundtrip_golden_shape`
  > 1 passed, 21 warnings in 28.20s

--STDERR--

## Static polluter candidate hits
| pattern | file | line | snippet |
|---|---|---:|---|
| `asyncio_run_in_sync_test` | `backend/tests/test_solva_v2_llm_adapter.py` | 125 | `asyncio.run(_runner())` |
| `asyncio_run_in_sync_test` | `backend/tests/test_synisense_surface_validation.py` | 77 | `` |

## Dynamic confirmation
- Polluter file: `tests/test_solva_v2_llm_adapter.py`
- Polluted target: `tests/characterisation/test_chat_roundtrip_golden.py::test_chat_roundtrip_golden_shape`
- Reproduced: **NO**
- Summary:
```

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
3 passed, 21 warnings in 24.41s

--STDERR--
```

## Recommended cleanup
Two options. (A) Replace `asyncio.run(_inner())` with the session-loop helper pattern: `loop = asyncio.get_event_loop(); loop.run_until_complete(_inner())` — pulls the same loop conftest pinned. (B) Per-test motor-client reset: at module teardown of each polluter, re-bind `core.db` to a fresh client tied to the session loop (heavier; deferred). Prefer (A); it's mechanical and behaviour-preserving.
