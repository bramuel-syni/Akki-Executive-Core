**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution flakes FTT-002..026 — INVESTIGATE-ONLY · HALT-and-surface)

# Sprint P5.7-DIAG — Cross-test pollution diagnosis (FTT-002..026)

**Status**: DIAGNOSIS SHIPPED · AWAITING USER DIRECTION (halt-and-surface contract)
**Date**: 2026-06-26
**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` (CSRF-grade discipline — root cause + cleanup mapping per cluster; halt on locked-area polluter or scope > 25 tests)
**Diagnostic slice**: `/app/backend/scripts/jc_test_pollution_diagnose_slice.py` (READ-ONLY by contract; no test/fixture mutation)
**Consolidated diagnosis**: `/app/memory/jc_artifacts/test_pollution/diagnosis_20260626T173637Z.md`
**Per-cluster evidence**: 9 `cluster_*.md` files at `/app/memory/jc_artifacts/test_pollution/`
**Files touched**: 0 production · 0 test/fixture (diagnosis is read-only) · 1 NEW slice script (+520) · 9 NEW evidence MDs + 1 index MD

## Scope contract

Per user direction (Q1=1a, Q2=2c, Q3=3b on the plan ask):

- Investigate 24 active FTT entries (FTT-002..026 — FTT-001 resolved in Phase 5.6.2 today)
- Use **existing artifact + targeted re-runs per cluster** (not a fresh broad-suite capture)
- Per cluster: identify, isolate, polluter-bisect, record polluter file:line + polluted file:line + leaked state + cleanup
- Save per-cluster evidence to `cluster_<name>.md`; consolidated index to `diagnosis_<UTC ts>.md`
- **DIAGNOSTIC SLICE IS READ-ONLY** by contract
- **HALT and surface** after Item 2 — no auto-fix without user approval

### HALT conditions checked
- Scope > 25 tests → **24 ≤ 25, no halt**
- Polluter in locked area (Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer) → **none, no halt**
- Cluster requires full broad-suite to confirm → **see Critical Surface below**

## Diagnosis outputs

- **9 clusters processed** mapping to 24 FTT IDs
- **337 static polluter-pattern hits** across the test directory (asyncio.run callers, module-level `app.dependency_overrides[...]`, bare `os.environ[...]` mutations, module-scope fixtures)
- **0 dynamic reproductions** in 2-file minimum-reproduction pytest invocations (cluster 1 attempted)
- **No locked-area polluter** found in any cluster
- **No halt condition tripped**

### Cluster summary (see consolidated index for full table)

| Cluster | FTT IDs | Static hits | Effort |
|---|---|---:|---|
| `event_loop_binding_leak` | FTT-002, FTT-003 | 2 | MED — sweep `asyncio.run` callers to session-loop helper |
| `shared_fixture_state_iter41` | FTT-004..009 | 87 | LOW — single-file module→function fixture refactor |
| `dependency_overrides_leak` | FTT-010..012 | 0 | LOW — audit module-level overrides; move into fixture (no static hits, cluster relies on narrative diagnosis) |
| `skipped_slow_phase_d_fix_bundle` | FTT-013 | 0 | n/a — enable slow lane to re-bisect |
| `mongo_collection_state_carryover` | FTT-014 | 48 | LOW — per-test collection purge fixture |
| `env_or_motor_loop_state` | FTT-015..018 | 109 | MED — replace bare env mutations with monkeypatch |
| `sendgrid_env_stub_leak` | FTT-019..022 | 52 | LOW — pin env vars at fixture scope |
| `tenant_resolver_stub_leak` | FTT-023 | 0 | subsumed by `dependency_overrides_leak` fix |
| `autosave_debounce_timer_leak` | FTT-024..026 | 39 | MED — explicit timer cancel + state reset |

## Critical surface for user direction

**Cluster 1 minimum-reproduction did NOT reproduce the pollution.**

- 2-file pytest invocation (`tests/test_solva_v2_llm_adapter.py` + `tests/characterisation/test_chat_roundtrip_golden.py::test_chat_roundtrip_golden_shape`) → 3 passed, 0 failed.
- Manual extension to 4-file invocation (both asyncio.run candidates + both polluted targets) → 38 passed, 0 failed.

**What this means**: the candidate `asyncio.run` polluters can run in the same Python process as the polluted tests without breaking them. The broad-suite pollution is **ordering-dependent in a way that requires more than the candidate polluter alone** — likely a specific multi-file sequence that re-binds motor's loop state in a particular order.

The static recommendations (asyncio.run hygiene, dependency_overrides guards, env-mutation guards) remain SOUND structurally. But the FAILING_TEST_TRACKER's per-cluster cause attribution is a HYPOTHESIS based on broad-suite delta; this slice could NOT collapse it to a single-file polluter under targeted re-runs.

## Three honest paths forward (user pick)

a. **Ship static guards proactively, then re-measure flake reduction.** Land 2 AST invariants (no module-level `dependency_overrides`; no bare `os.environ` mutation in tests) + sweep `asyncio.run` callers to session-loop helper. Each guard ships as its own small sprint with proving slice. After the sweeps, re-run the broad-suite and measure the FTT delta.

b. **Full broad-suite capture with deterministic ordering** (`pytest --no-randomly` or pinned shuffle seed; 45-90 min) to find the actual polluter chain before any fix. Per the ground-rules upgrade clause: "If any cluster requires running the full broad-suite to confirm → upgrade to a single fresh broad-suite capture, document why, then resume."

c. **Defer the pollution sprint entirely** until a different trigger (e.g., CI lane expansion in Phase 5.7) forces the issue. No proactive cleanup; per-test-file isolation is sufficient for current dispatches.

## Discipline notes

- This sprint changed **zero test files, zero fixture files, zero production code**. Diagnostic slice is read-only by contract; pytest invocations are subprocess reads of test state.
- Pollution scope (24 active FTT IDs) is at or just under the 25-test halt threshold; no scope-halt fires.
- The pollution is NOT a regression from this session's work; it is pre-existing flakiness mapped during the 5.6.1 audit's broad-suite run.
- Sibling sprint **P5.6.2** (FTT-001 real-assertion repair) shipped earlier today in this dispatch; tracker now sits at 24 active entries instead of 25.

## Files added

- `/app/backend/scripts/jc_test_pollution_diagnose_slice.py` (NEW · +520 LOC)
- `/app/memory/jc_artifacts/test_pollution/cluster_*.md` (NEW · 9 files)
- `/app/memory/jc_artifacts/test_pollution/diagnosis_20260626T173637Z.md` (NEW · consolidated index)
- `/app/memory/sprints/P5_7_DIAG_test_pollution.md` (NEW · this memo)
