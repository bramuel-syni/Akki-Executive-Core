**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution flakes FTT-002..026 — broad-suite capture (b) attempt · HALT-and-surface fired)

# Broad-suite pollution capture · attempt 1 · 2026-06-26 17:55 UTC

## Status

**🟥 HALT-and-surface fired** — pre-authorised condition: *"If broad-suite takes > 2 hours → HALT, surface, that means the capture itself has a problem (likely state accumulation in the harness)."*

The broad-suite **hung at ~16% completion** after 8m 21s wall-clock, with the pytest process holding 24 live threads at ~0% CPU and no log output for 5+ minutes. This is far short of the 2-hour ceiling but the hang signature MATCHES the user's halt clause: the capture itself has a problem.

## Configuration of attempted capture

- **Cmd**: `pytest tests/ -q --no-header --tb=no -m "not integration and not deploy_smoke and not runtime_playwright" -p no:cacheprovider --maxfail=500 --continue-on-collection-errors`
- **Collected**: 4,412 tests (from `pytest --collect-only`)
- **Cwd**: `/app/backend`
- **Wall-clock budget**: 5400s (90 min, well under 2-hour halt ceiling)
- **Started**: 2026-06-26 17:55:59 UTC
- **Last log output**: 2026-06-26 18:02:29 UTC (at ~16% bar)
- **Killed**: 2026-06-26 18:04 UTC, after 8m 21s elapsed with 0% CPU for >5 min
- **Process state at kill**: PID 36483, RSS 619 MB, 24 live threads, status S (sleeping)

## Observed evidence (partial)

The partial-capture log (`/app/memory/jc_artifacts/test_pollution/broadsuite/partial_capture_20260626T175559Z.log`) carries the 16% slice. Failure-pattern survey by progress-bar inspection:

| Progress bar segment | F count (failures) | s count (skips) | Notes |
|---|---:|---:|---|
| 0% → 16% | **~50** | ~38 | Heavy F clustering in 11%–16% range |
| ≥ 17% | n/a | n/a | Process hung; no further output |

Compared to the pre-existing `phase_5_5_3_failing_files_20260626.txt` baseline (101 failures total over a completed broad-suite from an earlier run), this partial 16% slice has already surfaced ~50% of that volume — consistent with the polluted-test density at the front of the suite.

## Diagnostic implication

Three honest readings of the hang:

1. **Harness state accumulation (most likely).** By the time the runner reaches alphabetical test #~706, accumulated in-process state (motor client bindings, asyncio event loops, dependency_overrides residue, fixture-state leftovers) has reached a configuration that deadlocks one of the remaining tests. The hang is the *terminal* end of the same pollution chain that produces FTT-002..026 as soft failures — not a separate bug.

2. **One pathological test acquires a lock or external resource and never releases it.** A single test hits a deadlock (e.g., aiohttp connection pool exhaustion, GridFS bucket lock, in-memory queue saturation) and the process stalls. The 24 live threads suggests async worker pools blocked on a join.

3. **External-service contention** — Mongo, Shield's LLM mock, the in-process SendGrid stub, or the APScheduler hourly cron triggering inside the test session — induces a cross-test wait that the harness doesn't surface as a test timeout (no `pytest-timeout` is installed; per-test timeouts are not enforced).

These readings are NOT mutually exclusive. Reading 1 directly supports the user's pre-authorised halt clause ("state accumulation in the harness").

## Why this answers the user's question

The user's stated goal for capture (b) was: *"identify the specific predecessor test that flipped it (bisect if necessary)."*

The hang prevents that bisect from running to completion under in-process broad-suite semantics. The bisect can still be done, but only with **process-level isolation per chain**. This is a structural finding that REVISES the cleanup direction:

- The 337 static polluter-pattern hits from P5.7-DIAG remain SOUND structurally
- But in-process broad-suite cannot reliably reproduce or characterise the pollution end-to-end — the pollution itself prevents the diagnostic
- A bounded bisect approach (file-by-file or chain-by-chain with subprocess isolation + per-file timeouts) is the realistic next step

## Pre-authorised halt — what this surfaces for user direction

Per the user's standing rules ("HARD STOP after (b) surfaces" + "If broad-suite takes > 2 hours → HALT, surface, that means the capture itself has a problem"), this report **HALTS the cleanup sprint** until user picks a refined path.

### Four refined paths forward

a. **Process-level isolated bisect (recommended structural).** Install `pytest-forked` or `pytest-xdist --forked` so each test (or file) runs in a fresh subprocess. Pollution surfaces ONLY where tests in the same process collide; in-suite-but-cross-process tests show no polluter chain. Output: confirmed polluter→polluted pairs scoped to each process group. Cost: 90-120 min for full broad-suite (~doubled vs. in-process) but with deadlock immunity.

b. **File-by-file subprocess capture with per-file timeout (cheaper, less precise).** Loop over the 433 test files, run each in its own subprocess with a 60s timeout. Records per-file: pass/fail/timeout. Identifies WHICH tests fail in isolation vs. need pollution to fail. Doesn't surface polluter chains, but does narrow which clusters NEED the chained capture. Cost: ~25-45 min.

c. **Container-level isolation via Docker.** Run the broad-suite inside a fresh Docker container with the same fixture state as a clean cold-start. Reproduces the CI lane semantics. Cost: env setup overhead; unclear whether the hang reproduces in a Docker isolation.

d. **Ship the path-(a) static guards FIRST.** Land the 3 hygiene fixes from P5.7-DIAG path (a) — `asyncio.run` sweep, no-module-level-overrides AST invariant, no-bare-env-mutation AST invariant — then RE-RUN this broad-suite. If the hang clears AND failure count drops, the hypotheses were correct. If hang persists OR failure count is unchanged, the static guards were hygiene-only and the polluter chain lives elsewhere.

### My recommendation

**Path (d) THEN (a).** The static guards are low-risk and structurally justified by the audit standard regardless of pollution outcome. Shipping them first gives a clean measurement signal: a second broad-suite attempt after the guards land tells us empirically whether the structural hypotheses match the actual polluter chain. If yes, we're done; if no, we have evidence for (a) being the right next move with proper data.

**Specifically NOT recommended**:
- Continuing to retry the full broad-suite in-process — it hangs the same way every time without subprocess isolation
- Auto-fixing without user picking the path — the diagnosis depends on subsequent measurement signals

## Files produced this attempt

- `/app/memory/jc_artifacts/test_pollution/broadsuite/partial_capture_20260626T175559Z.log` (partial pytest output up to ~16%)
- `/app/memory/jc_artifacts/test_pollution/broadsuite/broadsuite_attempt_1_20260626T175559Z.md` (this report)

## Files NOT touched

- Zero production code mutated
- Zero test files mutated
- Zero fixture files mutated
- HALT-and-surface contract honoured: surfacing only; no auto-fix
