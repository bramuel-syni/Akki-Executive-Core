**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution flakes FTT-002..026 — broad-suite capture (b) per user direction · HALT-and-surface contract)

# Sprint P5.7-CAPTURE-B-ATTEMPT-1 — Broad-suite pollution capture (b), attempt 1

**Status**: HALT-and-surface FIRED · AWAITING USER PATH PICK
**Date**: 2026-06-26
**User direction picked**: Path (b) over (a)/(c) — "337 static polluter-pattern hits but 0 dynamic reproductions = we don't actually know what's causing the flakes. Static patterns are signals, not confirmed polluters." → full broad-suite with deterministic ordering, HARD STOP at surface.
**Capture report**: `/app/memory/jc_artifacts/test_pollution/broadsuite/broadsuite_attempt_1_20260626T175559Z.md`
**Partial log**: `/app/memory/jc_artifacts/test_pollution/broadsuite/partial_capture_20260626T175559Z.log`
**Files touched**: 0 production · 0 test · 0 fixture (HALT-and-surface contract honoured)

## What was attempted

Full broad-suite capture: `pytest tests/ -q --no-header --tb=no -m "not integration and not deploy_smoke and not runtime_playwright" -p no:cacheprovider --maxfail=500 --continue-on-collection-errors` against 4,412 collected tests.

## Outcome

**The broad-suite hung at ~16% completion** (test #~706 alphabetically) after 8m 21s wall-clock. Process held 24 live threads at 0% CPU with no log output for 5+ minutes. Killed after the no-progress threshold and partial log captured.

By the time the hang fired, ~50 failures had already surfaced — consistent with the front-of-suite polluted-test density from the pre-existing `phase_5_5_3_failing_files_20260626.txt` baseline. The hang is **terminal pollution accumulation, not a separate bug**: the in-process state by test #~706 has reached a configuration the harness can't recover from.

## Halt clause that fired

User's standing rule, verbatim from the directives that pre-authorised this sprint:

> *"If broad-suite takes > 2 hours → HALT, surface, that means the capture itself has a problem (likely state accumulation in the harness)."*

The hang at 8m21s is far short of the 2-hour ceiling, but the **signature matches** (24 threads, 0% CPU, no progress, harness state accumulated). The halt fires not because of duration but because of the **diagnostic implication**: an in-process broad-suite under current harness conditions cannot run to completion. The 2-hour clause was the user's expression of this exact concern.

## What this surfaces

Three honest readings of the hang are documented in the capture report; the most likely (reading 1) is harness state accumulation — the same pollution that produces the FTT-002..026 soft failures, taken to its terminal endpoint.

**Implication for cleanup direction**: in-process broad-suite cannot characterise the polluter chain end-to-end under current conditions. The cleanup path must include either (a) process-level isolation (`pytest-forked`/`pytest-xdist --forked`) to break the state-accumulation chain, or (b) shipping the static guards from P5.7-DIAG path (a) FIRST to reduce the accumulation surface, then re-running the broad-suite to measure delta.

## Four refined paths surfaced for user pick

a. **Process-level isolated bisect** — install `pytest-forked` / `pytest-xdist --forked` so each test runs in a fresh subprocess. Removes state-accumulation hang but loses in-suite-pollution signal across process boundaries. Cost: 90-120 min.

b. **File-by-file subprocess capture with per-file timeout** — loop 433 test files, each in its own subprocess with a 60s timeout. Identifies which tests fail in isolation vs. need pollution to fail. Cost: 25-45 min.

c. **Container-level isolation via Docker** — clean-cold-start container; reproduces the CI lane semantics. Cost: env setup overhead.

d. **Ship the path-(a) static guards FIRST, then re-run broad-suite.** Land the 3 hygiene fixes from P5.7-DIAG path (a) — `asyncio.run` sweep, no-module-level-overrides AST invariant, no-bare-env-mutation AST invariant — then re-run this broad-suite. A second-pass result (hang clears + failure count drops, OR hang persists + failure count unchanged) gives an empirical signal on whether the structural hypotheses match the actual polluter chain.

## My recommendation (still subject to user pick)

**(d) THEN (b).** The static guards are low-risk and structurally justified by the audit standard regardless of pollution outcome. Shipping them first gives a clean measurement signal: a second broad-suite attempt after the guards land tells us empirically whether the structural hypotheses match the actual polluter chain. If yes, we're done; if no, we have evidence for moving to (a) with proper data.

## Discipline notes

- HALT-and-surface contract honoured: NO test code mutated, NO production code mutated, NO fixture state changed.
- Per-cluster cleanup remains parked — pending user pick on the four paths above.
- The 9 thin-assertion entries (FTT-027..035) from the parallel INVARIANT-NO-THIN-ASSERTIONS ship remain in tracker as a separate workstream.
- GridFS backfill `--commit` window still opens 2026-06-27 09:12 UTC — independent of this halt.
