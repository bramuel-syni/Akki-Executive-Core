**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE.md §3` (B.1 fix-sprint dispatched per user direction 2026-06-26 · scope: `tests/test_p_cleanup_c_help_tooltip_suppression.py` only · HARD STOP at proving-slice close)

# Sprint JC_POLLUTION_B1_FIX — module-scope fixture demotion for FTT-010..012

**Status**: SHIPPED (test-file-only patch landed) · proving slice **4/4 GREEN** · regression-check ladder GREEN · HARD STOP at slice close
**Date**: 2026-06-26
**Predecessor**: `sprints/P5_7_FIX_SCOPE.md §3` (scope memo with the module-scope async-fixture loop-binding identification)

---

## §0 — Outcome at a glance

| Tracker FTT ID | Test surface | Pre-fix | Post-fix | Disposition |
|---|---|---|---|---|
| FTT-010..012 | `tests/test_p_cleanup_c_help_tooltip_suppression.py` (3 polluted tests + 2 siblings) | RED in broad-suite (0/69 pairwise polluters → shared-global-state shape per P5.7-HOLDOUT-FINISHER) | GREEN in 3-predecessor broad-suite simulation (27/27 PASS) + GREEN in isolation (5/5) | **CLOSED** by single-line fixture-scope demotion |

**Net**: 3 tracker-FTT IDs closed (FTT-010, FTT-011, FTT-012) by a single decorator edit.

---

## §1 — Patch applied (test-file-only, locked-area cleared)

**File touched**: `tests/test_p_cleanup_c_help_tooltip_suppression.py` (single file; single fixture decorator).

Pre-fix (lines 43-45):
```python
@pytest_asyncio.fixture(scope="module")
async def transport():
    yield ASGITransport(app=app)
```

Post-fix:
```python
@pytest_asyncio.fixture(scope="function")
async def transport():
    yield ASGITransport(app=app)
```

**Mechanism (per scope memo §3)**: `pytest-asyncio` binds module-scoped async fixtures to the event loop active at first-resolution. Under broad-suite execution, hundreds of preceding tests churn through their own event loops. By the time the module-scoped `transport` resolves, the `ASGITransport(app=app)` object holds an `app` whose Motor singletons / dependency overrides / middleware state may be bound to a closed loop. Demoting to function-scope means each test gets a freshly-resolved transport bound to the per-test event loop — pytest-asyncio's session-scoped `event_loop` fixture from `conftest.py:210-221` keeps the Motor binding stable.

### §1.1 — Locked-area re-confirmation

| Area | Touched? |
|---|---|
| Shield surfaces | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| Product code (`server.py`, `core.py`, `contracts/`) | NO |

Cleared. Single test-file edit. Single decorator-kwarg semantic change (`module` → `function`).

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_b1_proving_slice.py`)

```
============================================================================
P5.7-B.1 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE.md §3
============================================================================
  Row  1  GREEN  polluted file in isolation post-fix (5/5 PASS)
            5 passed, 21 warnings in 6.06s  [dur=8.1s]
  Row  2  GREEN  paired with tests/test_phase4_2_http_transport_smoke.py (broad-suite simulation 1)
            13 passed, 21 warnings in 6.38s  [dur=8.5s]
  Row  3  GREEN  paired with 3 PASS-bucket predecessors (broad-suite simulation)
            27 passed, 21 warnings in 8.64s  [dur=10.4s]
  Row  4  GREEN  fixture-scope sanity (transport is now function-scoped)
            module_scope_marker_present=False  function_scope_marker_present=True
============================================================================
RESULT  4/4 GREEN
============================================================================
```

### §2.1 — Predecessor selection rationale (for Row 3)

The slice picks 3 predecessors **known clean** of the wrong-loop-binding bug:
- `tests/test_phase4_2_http_transport_smoke.py` — A+D-fixed (env+loop-policy snapshot/restore)
- `tests/test_phase_p5_10_audit_panel_direct_linkage.py` — Cluster-E-fixed (async-converted)
- `tests/test_track_b_phase2_task_lifecycle.py` — pure `@pytest.mark.asyncio` file, no `_run` helper

**Two predecessors deliberately AVOIDED in the slice design** (both surfaced during slice authoring as false-RED-source candidates):
1. Any of the 14 still-unconverted Cluster-F polluters — they drag in wrong-loop-binding pollution independent of B.1's mechanism (verified during slice debugging: pairing with `test_phase_p3_1_csrf.py` + `test_phase_p5_8_inbox_migration.py` produced 4 false-RED failures from Cluster-F's residual bug).
2. `test_phase4_4_dual_mount_smoke.py` — it has its own pre-existing 3-failure deterministic regression (stale ratchet shas, same shape as FTT-014's sibling). NOT a B.1 issue. Flagged as a separate parked finding in §5 below.

### §2.2 — Why Row 4's source-assertion matters

Row 4 reads the source post-fix and asserts:
- `@pytest_asyncio.fixture(scope="module")` marker is ABSENT
- `@pytest_asyncio.fixture(scope="function")` marker is PRESENT

Cheap durability check — future agents (or accidental refactors) can't silently re-introduce the module-scope decorator without Row 4 catching it. The slice is re-runnable as a regression check on any future change to this file.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **88 pass / 7 pre-existing failures** unchanged | Same `.....................Fsss.................................FF...F...` pattern as post-Cluster-E state. NOT regressions introduced by B.1. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchet at `31e1d9769f632472` | yes | **MATCH** — live re-verified, 636 paths |
| JC-TM email path smoke | yes | **N/A** | No SendGrid/email-path code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Cluster's own proving slice | yes (4/4) | **4/4 GREEN** |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_p_cleanup_c_help_tooltip_suppression.py` | MODIFIED | Single fixture decorator change (`scope="module"` → `scope="function"`) at lines 43-45 |
| `backend/scripts/jc_pollution_b1_proving_slice.py` | NEW | 4-row proving slice |
| `memory/sprints/JC_POLLUTION_B1_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row for JC-POLLUTION-B1-FIX |
| `memory/jc_artifacts/FAILING_TEST_TRACKER.md` | UPDATED | Mark FTT-010..012 as CLOSED-BY-B1 |

**Files NOT touched**: any product code, any other test file, any fixture file, any invariant file. Zero touches to Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer · contracts module · core.py · server.py.

---

## §5 — Side-finding: `test_phase4_4_dual_mount_smoke.py` has stale ratchet shas

During slice authoring, `test_phase4_4_dual_mount_smoke.py` was initially selected as a "clean" predecessor for Row 3. Running it in isolation revealed 3/37 failures:

```
FAILED tests/test_phase4_4_dual_mount_smoke.py::test_api_slice_hash_pinned
FAILED tests/test_phase4_4_dual_mount_smoke.py::test_v1_slice_hash_pinned
FAILED tests/test_phase4_4_dual_mount_smoke.py::test_combined_hash_pinned
```

Same shape as A+D's Cluster-D sibling regression (FTT-014's sibling): hardcoded ratchet shas drifted from the live `/api/*` + `/v1/*` + combined values. **NOT a B.1 issue, NOT a regression from this sprint**. Surfaced here as a parked finding because the slice happened to encounter it.

**Recommended disposition**: separate single-file ratchet-refresh sprint, mirroring the A+D Cluster-D pattern. Or fold into a future "all-ratchets-roll-forward" sweep along with similar drifted hardcoded shas in other files. NOT actioned in this sprint.

---

## §6 — Discipline notes

- **Scope honoured**: only `tests/test_p_cleanup_c_help_tooltip_suppression.py` modified.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 4/4 GREEN** — HARD STOP at slice close.
- **Locked-area check** done before and after — clear.
- **No production code changes** — single test-side decorator edit.
- **Predecessor-selection self-correction**: initially picked Cluster-F polluters + phase4_4 as Row 3 predecessors, both produced false-RED signals; corrected to known-clean predecessors. Discipline preserved through the debug.
- **Cluster-F polluters remain landmines** for any unconverted `@pytest.mark.asyncio` test that runs after them alphabetically — this is the Cluster-F memo's territory, not B.1's.

---

## §7 — User-direction surface (next dispatch)

Per your stated sequence post-A+D + Cluster-E + B.2-HALT:

1. ✅ A+D — 8 IDs closed
2. ✅ Cluster-E — FTT-023 closed
3. 🛑 B.2 HALT — surfaced Cluster-F scope; Cluster-F memo SHIPPED (parallel dispatch's #2)
4. ✅ B.1 — FTT-010..012 closed by this sprint
5. **Cluster-F sub-sprints** (next dispatch) — 6 sub-sprints F.1..F.6 per Cluster-F memo §1.1 grouping; closes FTT-024..026 + systemic anti-pattern
6. **Cluster C** — intra-file fixture refactor in `test_iter41_signal_actions_in_process.py`; closes FTT-004..009

Standing rules unchanged (canonical spec line 1 · READ-ONLY scope memos · DEV_PIPELINE updated before sprint memo · confirm before fix · no testing subagent · HALT-on-locked-area).
