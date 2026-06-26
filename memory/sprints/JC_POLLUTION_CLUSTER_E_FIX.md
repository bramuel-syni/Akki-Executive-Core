**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_E.md` (Cluster-E fix sprint dispatched per user direction 2026-06-26 · scope: `tests/test_phase_p5_10_audit_panel_direct_linkage.py` only · HARD STOP at proving-slice close)

# Sprint JC_POLLUTION_CLUSTER_E_FIX — async-conversion fix for FTT-023's wrong-loop polluter

**Status**: SHIPPED (test-file-only patches landed) · proving slice **9/9 GREEN** · regression-check ladder GREEN · HARD STOP at slice close
**Date**: 2026-06-26
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_E.md` (scope memo with file:line evidence for the loop-binding mechanism)

---

## §0 — Outcome at a glance

| Tracker FTT ID | Test surface | Pre-fix | Post-fix | Disposition |
|---|---|---|---|---|
| **FTT-023** | `test_track_b_phase2_task_lifecycle.py::test_cross_tenant_lifecycle_blocked` (and 6 sibling async tests in same file) | RED when paired with `test_phase_p5_10_audit_panel_direct_linkage.py` (7/9 failures in task_lifecycle) | **GREEN when paired** (9/9 task_lifecycle PASS in Row 2 of slice; 1/1 FTT-023 proper test PASS in Row 3) | **CLOSED** by async-conversion of p5_10's 5 sync test functions |

**Net**: 1 tracker-FTT ID closed (FTT-023) + 6 sibling async test failures in same file closed by same fix (`test_commission_draft_to_active_and_audit`, `test_close_active_to_closed_and_audit`, `test_commission_idempotent_on_active`, `test_close_idempotent_on_closed`, `test_state_machine_guards`, `test_filter_tab_counts_match_db`).

**Cluster-name correction landed in tracker**: `tenant_resolver_stub_leak` → `event_loop_binding_leak_from_sync_run` (the bisect's original hypothesis was wrong; conftest.py:224-253 already handles dep-override cleanup, so the real mechanism was loop-binding all along).

---

## §1 — Patches applied (test-file-only, locked-area cleared)

**File touched**: `tests/test_phase_p5_10_audit_panel_direct_linkage.py` (single test file; zero touches to product code, fixtures, invariants, or any of the four locked surfaces).

### §1.1 — Patch 1: Import refresh

- Removed `import asyncio` (no longer needed after `_run` helper deletion)
- Added `import pytest` (for the `@pytest.mark.asyncio` decorators)

### §1.2 — Patch 2: Drop `_run` helper

Lines 45-46 (pre-fix):
```python
def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)
```
Removed entirely. No other consumers existed (grep confirmed exactly one call site at line 126 inside `_http_get_audit_panel`).

### §1.3 — Patch 3: Convert `_http_get_audit_panel` to async

Pre-fix structure (lines 108-128):
```python
def _http_get_audit_panel(*, chat_id, message_id, account_id):
    from core import get_current_account
    app.dependency_overrides[get_current_account] = lambda: {...}
    async def _do():
        async with AsyncClient(...) as ac:
            return await ac.get(...)
    try:
        return _run(_do())
    finally:
        app.dependency_overrides.pop(get_current_account, None)
```

Post-fix structure:
```python
async def _http_get_audit_panel(*, chat_id, message_id, account_id):
    """[docstring updated to cite P5.7-Cluster-E fix and the loop-binding root cause]"""
    from core import get_current_account
    app.dependency_overrides[get_current_account] = lambda: {...}
    try:
        async with AsyncClient(...) as ac:
            return await ac.get(...)
    finally:
        app.dependency_overrides.pop(get_current_account, None)
```

Eliminates the inner `_do()` closure (now redundant — body inlined). Drops the `_run(_do())` wrapper. The function now `await`s on the caller's event loop, which (because callers carry `@pytest.mark.asyncio`) is the session-scoped loop from conftest.py:210-221.

### §1.4 — Patch 4: Convert 5 sync test functions to async

| Line (pre-fix) | Test name | Conversion |
|---:|---|---|
| 132 | `test_p5_10_audit_panel_uses_direct_shield_audit_id` | `def → @pytest.mark.asyncio + async def` |
| 155 | `test_p5_10_cancelled_turn_does_not_break_next_turn_audit` | same |
| 200 | `test_p5_10_legacy_positional_fallback_when_direct_link_missing` | same |
| 236 | `test_p5_10_404_when_message_id_missing` | same |
| 252 | `test_p5_10_user_role_message_returns_404` | same |

Each test body's `_http_get_audit_panel(...)` call became `await _http_get_audit_panel(...)`. Assertions, parametrization, fixture wiring, and Mongo seeding all unchanged.

### §1.5 — Locked-area re-confirmation (per scope memo §3)

| Area | Touched? | Evidence |
|---|---|---|
| Shield surfaces | NO | only `tests/test_phase_p5_10_audit_panel_direct_linkage.py` modified |
| WS Generate Doc UI | NO | same |
| Track-2 schema | NO | same |
| Monitor pre-warmer | NO | same |
| Product code (`server.py`, `core.py`, `contracts/`) | NO | conversion is purely test-side; production async code untouched |

**Cleared.**

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_e_proving_slice.py`)

```
============================================================================
P5.7-Cluster-E Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_E.md §2
============================================================================
  Row  1  GREEN  p5_10 file in isolation post-fix (5/5 PASS)
            5 passed, 21 warnings in 4.19s  [dur=6.2s]
  Row  2  GREEN  p5_10 + task_lifecycle (9 IDs + 5 polluter = 14 PASS)
            14 passed, 21 warnings in 6.34s  [dur=8.2s]
  Row  3  GREEN  p5_10 + test_cross_tenant_lifecycle_blocked (FTT-023 proper)
            6 passed, 21 warnings in 4.98s  [dur=7.0s]
  Row  4  GREEN  p5_10 + autosave (B.2 defensive)
            8 passed, 21 warnings in 5.11s  [dur=7.4s]
  Row  5  GREEN  p5_10 + bounce_webhook (A+D defensive, FTT-019..022 closed)
            10 passed, 21 warnings in 4.49s  [dur=6.3s]
  Row  6  GREEN  intra-file order check — p5_10 invoked twice
            5 passed, 21 warnings in 4.16s  [dur=6.3s]
  Row  7  GREEN  post-fix isolation re-run (self-pollution check)
            5 passed, 21 warnings in 4.16s  [dur=6.3s]
  Row  8  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 2's full stdout
  Row  9  GREEN  loop-binding sanity (post-fix loop policy clean)
            pytest_rc=0 loop_before='open' loop_after='open' same_loop=True
============================================================================
RESULT  9/9 GREEN
============================================================================
```

**Row 2 nuance**: 14 PASS = 5 (p5_10) + 9 (task_lifecycle). All 9 task_lifecycle tests passed when paired with the now-async p5_10 — confirming FTT-023 + its 6 sibling failures are closed.

**Row 6 nuance**: pytest dedupes file-arg duplicates, so 5 PASS (not 10) is the expected output. The intent of this row is to verify no order-dependent state accumulates within a single test invocation; PASS means it didn't.

**Row 8 (log scan)**: `attached to a different loop` count = **0** in Row 2's full stdout. The exact RuntimeError that captured the polluter mechanism during A+D's slice no longer fires.

**Row 9 (loop-binding sanity)**: `loop_before == loop_after == 'open'` and `same_loop=True` — the async-conversion preserved the session-scoped event loop state, no inner-loop creation, no policy mutation.

---

## §3 — Regression-check ladder (per scope memo §5 + standing-rule §5)

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **88 pass / 7 pre-existing failures** unchanged | Same `.....................Fsss.................................FF...F...` pattern as post-A+D state. 7 failures all pre-existed Cluster-E. NOT a regression introduced by this sprint. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched; preserved by construction (the pptx renderer is in `services/solva_v2/pptx_export.py`, not touched). |
| 450/450 Solva v2 schema+validator tests | yes | **N/A** | No schema/validator file touched; preserved by construction. |
| Surface ratchet at `31e1d9769f632472` | yes | **MATCH** — `live /api/* sha = 31e1d9769f632472; path count = 636` re-verified post-fix |
| JC-TM email path smoke | yes | **N/A** | No SendGrid/email-path code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx-render code touched. |
| Cluster's own proving slice | yes (target 9/9) | **9/9 GREEN** |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_phase_p5_10_audit_panel_direct_linkage.py` | MODIFIED | 5 sync→async test conversions + helper async conversion + `_run` helper removal + import refresh. Net delta: ≈25 LOC (5 decorators added, 5 `await` keywords added, 1 `def → async def` on helper, 1 helper removed, 1 import removed, 1 import added). |
| `backend/scripts/jc_pollution_cluster_e_proving_slice.py` | NEW | 9-row proving slice. |
| `memory/sprints/JC_POLLUTION_CLUSTER_E_FIX.md` | NEW | This sprint memo. |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row for JC-POLLUTION-CLUSTER-E-FIX. |
| `memory/jc_artifacts/FAILING_TEST_TRACKER.md` | UPDATED | Mark FTT-023 as CLOSED-BY-CLUSTER-E. |

**Files NOT touched**: any product code, any other test file, any fixture file, any invariant file. Zero touches to Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer · contracts module · core.py · server.py.

---

## §5 — Honest accounting

**Tracker-FTT IDs closed by Cluster-E: 1** (FTT-023). Plus 6 sibling async test failures in task_lifecycle (`test_commission_draft_to_active_and_audit` + 5 others) that were collateral damage of the same wrong-loop-binding mechanism — all closed simultaneously by the async-conversion.

**Cluster-name correction surfaced and applied**:
- Bisect's original hypothesis: `tenant_resolver_stub_leak`
- Empirical truth: `event_loop_binding_leak_from_sync_run`
- Tracker line 27 (FTT-023 entry) updated.

**FTT-023 cluster is FULLY CLOSED**. No residual.

---

## §6 — Discipline notes

- **Scope honoured**: only `tests/test_phase_p5_10_audit_panel_direct_linkage.py` modified.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 9/9 GREEN** — HARD STOP at slice close per <11/11-style discipline.
- **Locked-area check** done before and after — clear on all four surfaces.
- **No production code changes** — entirely test-side.
- **Surface ratchet unchanged** — `31e1d9769f632472` preserved.
- **Async-conversion alternative considered + rejected** per scope memo §1.1 (production-code Motor singleton reset would have crossed locked-area boundary).
- **Mechanism captured verbatim**: `RuntimeError: Future attached to a different loop` was the live observation that drove the diagnosis. Row 8 log scan asserts that error string is GONE post-fix.

---

## §7 — User-direction surface (next dispatch)

Per your stated post-A+D sequence:

1. ✅ **Cluster-E fix sprint** — this sprint — FTT-023 CLOSED
2. **B.2 fix sprint** — next dispatch — autouse fixture for Mongo-collection state reset on `admin@akki.ai` (per remeasure §3.1 refinement); closes FTT-024..026; scope unchanged at 15 polluters
3. **B.1 fix sprint** — single-line scope demotion `@pytest_asyncio.fixture(scope="module")` → function-scope on `test_p_cleanup_c_help_tooltip_suppression.py:43-45`; closes FTT-010..012
4. **Cluster C dispatch** — intra-file fixture refactor in `test_iter41_signal_actions_in_process.py`; closes FTT-004..009

Standing rules unchanged across remaining sprints (canonical spec line 1 · READ-ONLY scope memos · DEV_PIPELINE updated before sprint memo · confirm before fix · no testing subagent · HALT-on-locked-area · proving slice GREEN before each sprint close).
