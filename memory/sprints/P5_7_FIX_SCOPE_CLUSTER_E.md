**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution · Cluster-E fix-scope memo for FTT-023 · post-A+D · READ-ONLY · no test/product code mutations · HARD STOP at memo close)

# Sprint P5.7-FIX-SCOPE-CLUSTER-E — fix-scope memo for FTT-023's independent polluter

**Status**: SHIPPED (memo only) · HARD STOP at memo surface · AWAITING USER FIX-SPRINT DISPATCH
**Date**: 2026-06-26
**Predecessor**: `sprints/JC_POLLUTION_A_D_FIX.md` §5 (HARD STOP finding: empirical evidence proved `test_phase_p5_10_audit_panel_direct_linkage.py` is an INDEPENDENT polluter of `test_track_b_phase2_task_lifecycle.py`, NOT a tiered downstream of phase4_2's env leak as the bisect originally hypothesised)
**Discipline**: READ-ONLY contract honoured. 0 test/product/fixture files mutated. Pure source-read + scope-design output.

---

## §0 — Headline finding (load-bearing root cause)

`tests/test_phase_p5_10_audit_panel_direct_linkage.py` pollutes `tests/test_track_b_phase2_task_lifecycle.py` via the **wrong-loop-binding** mechanism — captured live during A+D's proving slice:

```
RuntimeError: Task <Task pending ... BaseHTTPMiddleware.__call__.<locals>.call_next.<locals>.coro ...>
              got Future <Future pending cb=[_chain_future.<locals>._call_check_cancel...]>
              attached to a different loop
```

**Source-read evidence** for the mechanism:

### Polluter (`test_phase_p5_10_audit_panel_direct_linkage.py`)

- **Line 45-46**: `def _run(coro): return asyncio.get_event_loop().run_until_complete(coro)` — synchronous helper.
- **All 5 test functions are SYNCHRONOUS** (no `@pytest.mark.asyncio` decorator) — they invoke `_run(coro)` to execute async HTTP calls.
- **Line 116-126** (`_http_get_audit_panel`):
  ```python
  async def _do():
      async with AsyncClient(
          transport=ASGITransport(app=app),
          base_url="http://testserver",
      ) as ac:
          return await ac.get(...)
  try:
      return _run(_do())
  finally:
      app.dependency_overrides.pop(get_current_account, None)
  ```
  - `_run(_do())` → `asyncio.get_event_loop().run_until_complete(...)`
  - Inside `_do()`, FastAPI's middleware chain awaits its way down to `core.db.X.find_one(...)` which uses Motor's `AsyncIOMotorClient` instance.
  - **Motor's singleton client binds to whichever event loop first issues an I/O on it.** For sync tests, that loop is `asyncio.get_event_loop()`'s return value — call it `LOOP_P5_10`.

### Polluted (`test_track_b_phase2_task_lifecycle.py`)

- **Line 32-34**:
  ```python
  @pytest.fixture
  def transport():
      return ASGITransport(app=app)
  ```
  Function-scoped transport — clean per test.
- **All 7 failing tests** carry `@pytest.mark.asyncio` (lines 83, 113, 138, 162, 189, 216, 237).
- They use `AsyncClient(transport=transport, base_url="http://test")` inside an `async def test_*(transport)`.
- pytest-asyncio runs each async test on the session-scoped event loop (`tests/conftest.py:210-221` defines `@pytest.fixture(scope="session") def event_loop()`) — call it `LOOP_SESSION`.

### Mechanism chain

1. Suite collects + runs `test_phase_p5_10_*` first (alphabetical predecessor).
2. p5_10's first sync test calls `_run(_do())` → `asyncio.get_event_loop()` returns a fresh loop OR the policy's default loop. In Python 3.11 with `asyncio_default_fixture_loop_scope=session` set in `pytest.ini`, the default is the SESSION loop. BUT `_run` is called from a SYNC test body — pytest-asyncio's session-loop fixture is NOT active for sync tests, so the policy's "current loop" may be DIFFERENT from `LOOP_SESSION`.
3. Either (a) `_run` uses a fresh loop and Motor binds there, OR (b) `_run` happens to use `LOOP_SESSION` but the AsyncClient/ASGITransport state mutates session-shared state.
4. The empirical observation `Future attached to a different loop` tells us: Motor (or some other async resource) ended up bound to a DIFFERENT loop than the one pytest-asyncio uses for the next file's tests. The `AsyncClient` task's child future is on `LOOP_P5_10`; the awaiting code in `LOOP_SESSION` rejects it.

**This is the same loop-policy shape as A+D — but originating from a DIFFERENT polluter file and triggered by a DIFFERENT primitive (`get_event_loop().run_until_complete()` instead of `asyncio.run()`)**.

### Conftest infrastructure

- `tests/conftest.py:210-221` — session-scoped `event_loop` fixture (Motor's stable loop for the suite).
- `tests/conftest.py:224-253` — autouse function-scoped `_isolate_dependency_overrides` fixture (snapshots + restores `app.dependency_overrides` per test).

The dep-override leak is ALREADY handled by conftest. So even though `_http_get_audit_panel` mutates `app.dependency_overrides[get_current_account]`, conftest's autouse fixture cleans it up. **Dep-overrides are NOT the polluter shape.** The polluter shape is **event-loop binding** — outside conftest's reach.

---

## §1 — Proposed fix (minimum patch)

**Touch ONE file** (test-side hardening): `tests/test_phase_p5_10_audit_panel_direct_linkage.py`

**Patch shape: convert the 5 sync test functions to async + `@pytest.mark.asyncio`**

This binds them to the session-scoped event loop (`tests/conftest.py:210-221`), the same loop pytest-asyncio uses for the rest of the suite. Motor's singleton remains stable across the whole session.

Source-read sketch (for memo only, NOT applied per READ-ONLY contract):

```python
# Sketch — convert each of the 5 tests to async.
@pytest.mark.asyncio
async def test_p5_10_audit_panel_uses_direct_shield_audit_id():
    account_id = f"acc-p5-10-direct-{uuid.uuid4().hex[:6]}"
    chat_id, msg_ids = _seed_chat_with_messages(account_id=account_id, turns=[...])
    r = await _http_get_audit_panel_async(chat_id=chat_id, message_id=msg_ids[1], account_id=account_id)
    ...

# And `_http_get_audit_panel` becomes async (drop the `_run(_do())` wrapper):
async def _http_get_audit_panel_async(*, chat_id, message_id, account_id):
    from core import get_current_account
    app.dependency_overrides[get_current_account] = lambda: {...}
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as ac:
            return await ac.get(
                f"/api/chats/{chat_id}/audit-panel",
                params={"message_id": message_id},
            )
    finally:
        app.dependency_overrides.pop(get_current_account, None)
```

**Why this is the minimum patch**:
- Zero new files. Zero new imports beyond what's already there.
- 5 function signatures change (`def → async def`) + 5 decorator additions (`@pytest.mark.asyncio`).
- 1 helper changes (`_http_get_audit_panel` → `_http_get_audit_panel_async`).
- 1 helper removed (`_run`).
- No assertions change, no test bodies fundamentally restructure.

### §1.1 — Alternative considered and rejected

**Alternative A**: change `_run` to explicitly use `LOOP_SESSION`:
```python
def _run(coro):
    loop = asyncio.get_event_loop_policy().get_event_loop()
    return loop.run_until_complete(coro)
```
**Why rejected**: relies on `get_event_loop_policy().get_event_loop()` returning the session loop for sync tests, which is implementation-dependent across pytest-asyncio versions and Python 3.11 vs 3.12. The async-conversion is unambiguously stable.

**Alternative B**: keep the sync tests but explicitly close Motor's singleton in p5_10's `finally`:
**Why rejected**: requires production-code introspection (touching the contracts module's singleton accessor), which crosses the locked-area boundary. Test-side conversion is the smaller blast radius.

---

## §2 — Proving slice design (target 9/9 GREEN)

Slice path: `backend/scripts/jc_pollution_e_proving_slice.py` (NEW, to be authored by the Cluster-E fix sprint).

| Row | Check | Acceptance |
|---|---|---|
| 1 | Polluter file (`test_phase_p5_10_audit_panel_direct_linkage.py`) in isolation post-fix | 5/5 PASS (regression-free) |
| 2 | Polluter + task_lifecycle paired pytest post-fix | 9/9 PASS in task_lifecycle (all 7 previously-failing + 2 sync-only) |
| 3 | Polluter + autosave (B.2 polluted file) paired post-fix | 11/11 PASS — defensive (confirms p5_10's async-conversion doesn't regress B.2) |
| 4 | Polluter + bounce_webhook (FTT-019..022 was already CLOSED by A+D) | 13/13 PASS — defensive (no regression of A+D's closure) |
| 5 | Polluter + audit_panel itself in 2× repeat order | 10/10 PASS (sanity: no intra-file regression from async conversion) |
| 6 | task_lifecycle in isolation post-fix | 9/9 PASS (no regression of the polluted file alone) |
| 7 | Single async test runs through full middleware chain — no `Future attached to a different loop` error anywhere | log scan: 0 occurrences |
| 8 | Loop-binding sanity: post-polluter, `asyncio.get_event_loop_policy().get_event_loop()` returns a non-closed loop | clean state |
| 9 | All 7 originally-failing task_lifecycle tests pass when run with p5_10 in front | 7/7 PASS |

**Acceptance**: 9/9 GREEN. HARD STOP at slice close.

---

## §3 — Locked-area re-confirmation (per scope memo §6 discipline)

| Area | Touched? | Evidence |
|---|---|---|
| Shield surfaces | NO | only `tests/test_phase_p5_10_audit_panel_direct_linkage.py` modified; no `services/synisense/*` source touched |
| WS Generate Doc UI | NO | same |
| Track-2 schema | NO | same |
| Monitor pre-warmer | NO | same |
| Product code (`server.py`, `core.py`, `contracts/`) | NO | conversion is purely test-side; production async code untouched |

**Cleared.** The patch touches one test file's 5 function signatures + 1 helper rename. No production code, no fixture code, no invariant code.

---

## §4 — HALT conditions for the fix sprint

Pre-authorised HALT triggers (per user's standing rules):

1. **If source-read of `_http_get_audit_panel_async` reveals a production-code dependency** (e.g., the helper needs to introspect the contracts module's Motor singleton for cleanup) → HALT, surface (different sprint shape).
2. **If async conversion introduces a NEW failure in p5_10 itself** (one of the 5 tests fails in isolation post-conversion) → HALT, surface (the test's underlying assertion may depend on sync-call ordering).
3. **If 7/9 task_lifecycle tests don't all close** after the fix → HALT, surface (residual pollution from a different mechanism not captured in this scope).
4. **If the proving slice's Row 8 (loop-binding sanity) doesn't clear** → HALT, surface (loop-policy still leaking; deeper investigation needed).
5. **If `tenant_resolver_stub_leak` cluster name in tracker turns out to be wrong** (the actual leak is loop-binding, not tenant-resolver) → surface a tracker correction in the fix sprint memo. This is a documentation-truth fix, NOT a HALT.

---

## §5 — Files produced by this scope memo

| Path | Status |
|---|---|
| `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_E.md` | NEW — this memo (~250 lines · READ-ONLY) |
| `/app/memory/DEV_PIPELINE.md` | TO UPDATE — §9 row addition (per standing rule "DEV_PIPELINE.md updated before sprint memo") |
| `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` | TO UPDATE — refine FTT-023 entry's cluster name from `tenant_resolver_stub_leak` to `event_loop_binding_leak_from_sync_run` to reflect the actual mechanism captured here |

## §6 — Files NOT touched by this memo

- 0 product code mutated
- 0 test files mutated
- 0 fixture files mutated
- 0 proving-slice scripts authored (deferred to fix sprint)

---

## §7 — User-direction surface (next dispatch)

Per your standing sequence post-A+D:

> "1. Cluster-E fix sprint (closes FTT-023)
>  2. B.2 fix sprint (closes whatever the remeasure says is genuinely B.2 — likely fewer than 3 if some autosave polluters were downstream of A+D)
>  3. B.1 fix sprint (single-line scope demotion, closes FTT-010..012)
>  4. Cluster C dispatch (intra-file fixture refactor, FTT-004..009)"

The B.2 remeasure (`sprints/P5_7_B2_REMEASURE.md`) showed: **0 polluters disappeared, 15 remain**. B.2's scope is unchanged at 15 polluters. So the sequence is now:

1. **Cluster-E fix sprint** (this memo's scope) — async-conversion of 5 sync tests in p5_10 — closes FTT-023's 7 task_lifecycle failures
2. **B.2 fix sprint** — original §2.2 plan refined by remeasure §3.1 (Mongo-collection reset, NOT dep-overrides which conftest already handles) — closes FTT-024..026
3. **B.1 fix sprint** — single-line scope demotion on test_p_cleanup_c_help_tooltip_suppression.py
4. **Cluster C dispatch** — intra-file in test_iter41_signal_actions_in_process.py

Standing rules unchanged across all four sprints (canonical spec line 1, READ-ONLY scope memos, DEV_PIPELINE updated before sprint memo, confirm before fix, no testing subagent, HALT-on-locked-area, proving slice GREEN before any sprint close).
