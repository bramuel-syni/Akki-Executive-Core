**Canonical Spec**: `/app/memory/sprints/P5_7_B2_REMEASURE.md §3` (B.2 fix-sprint dispatched by user 2026-06-26 with scope "autouse fixture for Mongo-collection state reset on `admin@akki.ai`" · empirical evidence at dispatch entry contradicted the scope hypothesis · HALT-and-surface fired immediately · NO test/product code mutated)

# Sprint JC_POLLUTION_B2_HALT — B.2 fix scope re-discovery (NOT a fix sprint)

**Status**: HALTED at dispatch-entry · NO LOC mutated in any test/product/fixture/invariant code · scope-hypothesis-vs-empirical-mechanism mismatch surfaced · AWAITING USER FIX-SCOPE RE-DIRECTION

**Date**: 2026-06-26
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_E_FIX.md` (Cluster-E shipped 2026-06-26; FTT-023 closed by sync→async conversion of 5 test functions in `test_phase_p5_10_audit_panel_direct_linkage.py`)

---

## §0 — Why halted (one-paragraph summary)

The dispatched B.2 patch shape was "autouse function-scoped fixture in `tests/test_track_b_phase_b5_g6_notes_autosave.py` that resets Mongo-collection state on `admin@akki.ai` per remeasure §3.1 refinement (`login_failed_attempts` counter, `session_revocations` rows, `accounts.{is_locked, mfa_required, force_reset_at}` flags)". The first diagnostic step before patching was to capture the actual failure trace from a paired-pytest run of one polluter + autosave. The captured error is **identical to Cluster-E's**: `RuntimeError: Task ... got Future ... attached to a different loop`. This contradicts the remeasure §3.1 hypothesis. Static scan of all 14 of the 15 B.2 polluters that haven't already been Cluster-E-fixed confirms: every one uses the same sync-test + `asyncio.get_event_loop().run_until_complete(coro)` or `asyncio.run(...)` pattern that drives the wrong-loop-binding cascade. **B.2's actual pollution mechanism is the same as Cluster-E's**, not Mongo-collection state.

---

## §1 — Empirical evidence (file:line precise)

### §1.1 — The actual failure trace

```bash
$ cd /app/backend && pytest tests/test_phase_p2_b4_password_change.py \
                           tests/test_track_b_phase_b5_g6_notes_autosave.py
...
FAILED tests/test_track_b_phase_b5_g6_notes_autosave.py::test_patch_notes_sets_notes_updated_at
FAILED tests/test_track_b_phase_b5_g6_notes_autosave.py::test_patch_empty_notes_clears_field_and_bumps_timestamp
FAILED tests/test_track_b_phase_b5_g6_notes_autosave.py::test_patch_notes_idempotency_safe_for_autosave_debounce

E  RuntimeError: Task <Task pending name='Task-169'
   coro=<test_patch_notes_sets_notes_updated_at() running at
   /app/backend/tests/test_track_b_phase_b5_g6_notes_autosave.py:107>
   cb=[_run_until_complete_cb() at /usr/local/lib/python3.11/asyncio/base_events.py:181]>
   got Future <Future pending cb=[_chain_future.<locals>._call_check_cancel() at
   /usr/local/lib/python3.11/asyncio/futures.py:387]> attached to a different loop
E  RuntimeError: Task <Task pending name='Task-170' ...> attached to a different loop
E  RuntimeError: Task <Task pending name='Task-171' ...> attached to a different loop
```

The "Future attached to a different loop" string is verbatim the same RuntimeError that Cluster-E's proving slice Row 8 confirmed had been silenced. The autosave file's 3 async tests are bound to the session loop (conftest.py:210-221); the polluter (`test_phase_p2_b4_password_change.py`) bound Motor to its sync-test-local loop; same shape as p5_10 was doing pre-Cluster-E.

### §1.2 — Static scan of all 14 candidate polluters

```
test_phase_p2_a2_microsoft_pkce    → 1 asyncio hit, 7 sync tests, 0 async tests
test_phase_p2_b1_security_headers  → 1 asyncio hit, 5 sync tests, 0 async tests
test_phase_p2_b4_password_change   → 1 asyncio hit, 4 sync tests, 0 async tests
test_phase_p2_b6_admin_force_reset → 1 asyncio hit, 4 sync tests, 0 async tests
test_phase_p2_d2_health_composite  → 1 asyncio hit, 4 sync tests, 0 async tests
test_phase_p3_1_csrf               → 1 asyncio hit, 7 sync tests, 0 async tests
test_phase_p3_2_cookie_hardening   → 1 asyncio hit, 2 sync tests, 0 async tests
test_phase_p3_4_session_timeout    → 1 asyncio hit, 5 sync tests, 0 async tests
test_phase_p5_5_session_reauth     → 1 asyncio hit, 4 sync tests, 0 async tests
test_phase_p5_7_5_bounce_webhook   → 1 asyncio hit, 5 sync tests, 0 async tests
test_phase_p5_7_waitlist_reminder  → 1 asyncio hit, 8 sync tests, 0 async tests
test_phase_p5_8_inbox_migration    → 1 asyncio hit, 7 sync tests, 0 async tests
test_phase_p5_9_admin_button_and_badge → 1 asyncio hit, 4 sync tests, 0 async tests
test_synisense_security            → 2 asyncio hits, 3 sync tests, 0 async tests
```

**Uniformly**: each polluter has 0 async tests + some sync tests + 1-2 hits on `asyncio.get_event_loop`/`asyncio.run`/`run_until_complete`/`asyncio.new_event_loop`. Spot-check of two polluters confirms the exact `_run` helper shape:

```python
# tests/test_phase_p2_b4_password_change.py:34-35
def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

# tests/test_phase_p3_1_csrf.py:21-22
def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)
```

And `test_synisense_security.py` uses `asyncio.run(...)` directly at lines 35 and 52 — same A+D-style mechanism (which A+D already fixed at `test_phase4_2_http_transport_smoke.py` via env+loop-policy snapshot/restore).

**Total**: ~70 sync tests across 14 files, all instances of the same wrong-loop-binding bug Cluster-E captured.

### §1.3 — Why remeasure §3.1 reached the wrong conclusion

Remeasure §3.1 reasoned: "conftest.py:224-253 already handles dep-override cleanup, so the dominant mechanism must be Mongo-collection state on admin@akki.ai." But the actual mechanism — wrong-loop-binding from sync-test `_run` helpers — is invisible to a paired-pytest-bucket measurement. The bucket measurement only records PASS/FAIL counts, not error shapes. The 15-polluter file-name pattern (all auth/session/CSRF) looked like Mongo-state pollution, but it was actually loop-binding pollution — those files happen to be the auth/session/CSRF files BECAUSE those are the files that mint admin credentials and so need to drive async-HTTP traffic through `_run` helpers in their sync test bodies. **Same files, different mechanism — the same systemic anti-pattern Cluster-E identified.**

---

## §2 — Why the dispatched scope (Mongo-collection reset) wouldn't have worked

Even if I had landed the dispatched autouse-fixture-on-autosave with Mongo-collection reset, the wrong-loop-binding RuntimeError would still fire BEFORE the autosave test's HTTP calls reach the Mongo collections in question. The error is raised in the httpx → ASGITransport → FastAPI-middleware → Motor stack as soon as `await ac.get("/api/csrf")` runs (the first line of `_csrf_login` in autosave). The Mongo `login_failed_attempts` / `session_revocations` / `accounts` reads/writes that the dispatched fixture would reset never get a chance to be touched by the failing call. **Mongo state is downstream of the error; resetting it doesn't help.**

Verified by reasoning, not by writing the fixture (READ-ONLY contract preserved). The failure trace explicitly shows the error fires at the httpx middleware layer, not at the Mongo query layer.

---

## §3 — Three options for fix-scope re-direction (NOT executed; awaiting user choice)

### Option (a) — Cluster-F: broad sync→async conversion across all 14 polluters

**Mechanically identical to Cluster-E**, applied 14× instead of 1×:

- Each polluter file: drop `_run` helper, convert sync tests to `@pytest.mark.asyncio + async def`, replace `_run(coro)` with `await coro`, import `pytest` if missing, drop `import asyncio` if no longer used.
- Estimated LOC delta per file: ~20-30 LOC. Total: ~280-420 LOC across 14 files.
- `test_synisense_security.py` is slightly different (uses `asyncio.run(...)` directly, like phase4_2 did pre-A+D) — fix shape there is either (i) async-convert OR (ii) snapshot/restore env+loop-policy around `asyncio.run` like A+D did.
- **Closes**: FTT-024..026 (the 3 autosave IDs) AND removes the wrong-loop-binding leak at source for all 14 files. Likely closes other latent issues we don't even know about yet — sync-test files are landmines anywhere they sit alphabetically before any `@pytest.mark.asyncio` file.
- **Trade-off**: bigger blast radius than the dispatched 1-file scope. Each file's conversion is small + mechanical, but quality-of-life requires reviewing each file's specific test semantics (the 5 spot-checked all look mechanical, but ~70 tests is a lot to mass-convert without per-file inspection).
- **Recommended sub-sequencing**: 2-3 files per sub-sprint, each its own proving slice + HARD STOP. Probably 5-7 sub-sprints to clear the 14 files. Like Wave 3 axios migration shape.

### Option (b) — Test-side Motor rebind on the autosave file

**Brittle hack** — add an autouse fixture on autosave that calls `db._client.close()` or sets `db._client._topology = None` before each test to force Motor to re-instantiate against the current loop. Couples to Motor internals.

- **Closes**: FTT-024..026 only. Polluters remain landmines for other future async test files.
- **Trade-off**: smaller scope but depends on Motor internals; vulnerable to upstream Motor library updates; harder to reason about. The user's dispatch directive said: "If you discover the reset mechanism requires a new helper in production code → HALT, surface." Touching `db._client._topology` (private attribute) arguably violates this, even though no production source file is edited.
- **NOT recommended** unless time-to-close is critical and the broader cleanup can wait.

### Option (c) — Defer B.2; proceed with B.1 + Cluster C

- B.1 is a genuine 1-line scope demotion (`@pytest_asyncio.fixture(scope="module")` → `function`) — known-safe, easy win.
- Cluster C is intra-file fixture refactor — also self-contained.
- B.2 sits parked until Cluster-F is dispatched or until the broader sync→async sweep happens organically.
- **Trade-off**: defers the autosave file's flake closure. But the autosave file's 3 tests aren't blocking production; they're just flaky in broad-suite runs. Acceptable parking shape.

---

## §4 — Locked-area re-confirmation (HALT did not touch any code)

| Area | Touched by this HALT memo? |
|---|---|
| Shield surfaces | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| `tests/test_track_b_phase_b5_g6_notes_autosave.py` (dispatched target) | **NO — no autouse fixture added, no LOC mutated** |
| Any of the 14 polluter files | NO |
| `conftest.py` | NO |
| Any product code (`server.py`, `core.py`, `contracts/`, etc.) | NO |

**Pure HALT-and-surface output. 0 LOC mutated across the entire repo.**

---

## §5 — Files produced by this HALT

| Path | Status |
|---|---|
| `/app/memory/sprints/JC_POLLUTION_B2_HALT.md` | NEW — this HALT memo |
| `/app/memory/DEV_PIPELINE.md` | UPDATED — §9 row for HALT (no FTT IDs closed, but evidence captured) |
| `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` | UPDATED — FTT-024..026 cluster name refined from `autosave_debounce_timer_leak` to `event_loop_binding_leak_from_sync_run_in_polluter_files` (same Cluster-E mechanism, broader file scope) |

## §6 — Files NOT touched

- 0 product code mutated
- 0 test files mutated
- 0 fixture files mutated
- 0 proving-slice scripts authored
- 0 invariant files mutated

---

## §7 — Discipline notes

- **HALT-and-surface fired at dispatch entry**, BEFORE any patch code was written. The first diagnostic step (capture failure trace) revealed the scope-hypothesis-vs-empirical-mechanism mismatch.
- **READ-ONLY contract preserved**.
- **No testing subagent used** (per banned-list rule).
- **The HALT triggered against the dispatched scope's stated mechanism**, not against a regression. This is the system working as designed: scope hypotheses are confirmed empirically before patches land.
- **Cluster-E's evidence informed this HALT** — without the verbatim error string from Cluster-E's Row 8 log scan, the trace from `test_phase_p2_b4_password_change + autosave` might have been ambiguous. Cluster-E surfaced the canonical wrong-loop-binding signature; B.2's HALT pattern-matched against that signature.

---

## §8 — User-direction surface

Three options in §3 above. **Recommended: (a) Cluster-F** — broad sync→async conversion, sub-sequenced into 5-7 small sprints. Same mechanical pattern as Cluster-E; just applied at scale. The leverage is high: closes B.2's 3 IDs AND removes a systemic test-infrastructure anti-pattern that's been latent across the suite for who-knows-how-long.

If you'd prefer to keep moving fast on the immediate sequence: **(c) Defer B.2** and proceed with B.1 + Cluster C, then circle back to Cluster-F as its own dedicated multi-sub-sprint dispatch.

(b) is the "patch over symptoms" choice — workable but not honoring the discipline that's been carrying this sequence so far.

Whichever you pick, the FTT-024..026 cluster name has been refined in the tracker to reflect the empirical mechanism, so future agents starting from the tracker won't repeat the §1.3 misreading.
