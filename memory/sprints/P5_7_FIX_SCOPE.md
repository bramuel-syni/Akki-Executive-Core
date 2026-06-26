**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution fix-scope memo · post-P5.7-HOLDOUT-FINISHER · READ-ONLY · no test/product mutations · HARD STOP at memo close)

# Sprint P5.7-FIX-SCOPE — fix-scope memo for the four cross-test-pollution clusters

**Status**: SHIPPED (memo only) · HARD STOP at memo surface · AWAITING USER FIX-SPRINT DISPATCH
**Date**: 2026-06-26
**Predecessor**: `sprints/P5_7_HOLDOUT_FINISHER.md` (full predecessor sweep · 19 active FTT IDs all mapped to concrete fix-shapes with confirmed evidence)
**Discipline**: READ-ONLY contract honoured. 0 test files mutated. 0 product code mutated. 0 fixture files mutated. Pure source-read + scope-design output.
**User-direction picked**: (a) — proceed exactly as planned. Sequence A+D → B.2 → B.1; park C for separate dispatch.

---

## §0 — Bundle-vs-sequence rationale (recorded verbatim, per user message)

> "A+D is polluter-side (stops the env/loop bleed at source). B.2 is test-side hardening. Bundling mixes fix shapes in one diff, forfeits the re-measurement signal between them. Sequencing lets the broad-suite re-run after A+D measure whether B.2's polluter list shrinks first — possibly some of B.2's 15 polluters depend on the env state A+D was leaking, in which case B.2 needs less work than initially thought. Same 'confirm before fix' discipline that picked path (b) over (d) at pollution capture and (c) over (b) at bisect: measure the actual delta before committing to scope."

This rationale is load-bearing for the §3 inter-cluster measurement procedure between A+D ship and B.2 dispatch.

---

## §1 — Smoking-gun finding (load-bearing root cause for Cluster A+D)

`tests/test_phase4_2_http_transport_smoke.py::test_http_mode_adapter_class_reconstructs_dto` (lines 205-237) contains three concrete mutations of process-global state. Two are restored; the **third (the env-load) is NEVER restored**:

| # | Line | Mutation | Restoration | Pollution impact |
|---|----:|----------|-------------|------------------|
| 1 | 210 | `os.environ["BOUNDED_CONTEXT_TRANSPORT"] = "http"` | line 237 `os.environ.pop("BOUNDED_CONTEXT_TRANSPORT", None)` — clean | none — restored |
| 2 | 216-217 | `from dotenv import load_dotenv; load_dotenv(Path("/app/backend/.env"))` | **NONE** — every key in `/app/backend/.env` (≈ 90 keys per repo state) is now permanently injected into `os.environ` for the remainder of the pytest process | **THIS IS THE LEAK** — explains `sendgrid_env_stub_leak` (FTT-019..022), `env_or_motor_loop_state` shape (FTT-015..018), and likely a non-trivial subset of B.2's 15-polluter list |
| 3 | 230 | `asyncio.run(_run())` → inside which `get_akki()` instantiates the contracts adapter, which (via `contracts/_adapters/_http_client.py`) instantiates the Motor `AsyncIOMotorClient` module-singleton bound to the loop created by `asyncio.run()` | the loop closes when `asyncio.run` returns — but the singleton's `client._io_loop` reference is now to a CLOSED loop | **Motor closed-loop leak** — any subsequent test that calls `db.X.find_one(...)` from a different loop hangs/raises because the client is bound to the dead loop |

**Sibling failure within the polluter file (Cluster D / FTT-014)**: `test_internal_transport_openapi_hash_unchanged` (line 91-110) hardcodes `EXPECTED = "cdcb23322bb82895"` as the `/api/*` slice sha. The current ratchet (per `DEV_PIPELINE.md §5`, refreshed at the JC-TL GP-ship close on 2026-06-26) is `9aa905f6d951f2a8`. The sha is stale because legitimate additive routes have shipped since the original Phase 4.1 pin. The test fails deterministically in isolation — this is the FAIL_DETERMINISTIC bucket per P5.7-PER-FILE-CAPTURE.

Single-file surgical fix in the polluter probably closes 10 FTT IDs at source (FTT-014 own-failure + FTT-015..023 downstream pollution), plus an unknown subset of B.2's polluter dependency.

---

## §2 — Surface 1 (PRIMARY · Cluster A+D + Cluster B.2, SEQUENCED)

### §2.1 — Cluster A+D — polluter-side fix on `tests/test_phase4_2_http_transport_smoke.py`

**Closes**: FTT-014 (deterministic regression, sibling test in same file) + FTT-015..023 (9 downstream IDs, 3 confirmed polluted files + 1 tiered polluted file). **Total: 10 FTT IDs.**

**Locked-area check**: `tests/test_phase4_2_http_transport_smoke.py` — TEST FILE only. The proposed fix touches a single test function body and a single hardcoded constant. **Zero touches** to Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer. Cleared.

**Proposed minimal patches** (described, NOT applied per READ-ONLY contract):

1. **Fix the env-leak (load-bearing)** — wrap the `load_dotenv` call in a snapshot/restore context manager scoped to the test body:
   ```python
   # Sketch — for memo only, not committed.
   _env_snapshot = dict(os.environ)
   try:
       load_dotenv(Path("/app/backend/.env"))
       from contracts import get_akki, Document
       ...
       result = asyncio.run(_run())
       assert result is None
   finally:
       # Restore env to pre-test state exactly.
       for k in list(os.environ.keys()):
           if k not in _env_snapshot:
               del os.environ[k]
       for k, v in _env_snapshot.items():
           os.environ[k] = v
       os.environ.pop("BOUNDED_CONTEXT_TRANSPORT", None)
   ```
   Net effect: every env key loaded by `load_dotenv` is removed (or restored to its pre-test value) before the next test runs. Closes Cluster A's env-pollution mechanism.

2. **Fix the Motor closed-loop leak** — either (a) move the `asyncio.run` block into a `pytest_asyncio` async test that uses the suite's session-level event loop instead of creating its own, OR (b) explicitly close the contracts module-singletons in the `finally`:
   ```python
   # Sketch — option (b).
   finally:
       try:
           import contracts as _contracts_mod
           if hasattr(_contracts_mod, "_singleton_akki"):
               _contracts_mod._singleton_akki = None  # force re-instantiation on next loop
       except Exception:
           pass
       ...env restore...
   ```
   The exact symbol depends on `contracts/_adapters/_http_client.py` source (NOT re-read here per contract; the fix sprint must source-inspect it). Closes the Motor cascade.

3. **Fix Cluster D (FTT-014) — refresh the sha** — update line 101:
   ```python
   EXPECTED = "9aa905f6d951f2a8"  # rolled forward to JC-TL GP-ship close (2026-06-26)
   ```
   This IS the surface-ratchet refresh; it does NOT widen surface — only the test assertion catches up. Document the roll-forward in the sprint memo and mirror the §5 row in DEV_PIPELINE.md if appropriate.

**Proving slice design** (`backend/scripts/jc_pollution_a_d_proving_slice.py` — to be authored by the fix sprint, not now):
- **Row 1**: env-restoration assertion — record `dict(os.environ)` pre-call to `test_http_mode_adapter_class_reconstructs_dto`, run the test, assert `dict(os.environ)` is EXACTLY identical post-call. (Diff-print on mismatch.)
- **Row 2**: Motor-loop-consistency assertion — run the polluter test, then run a probe that calls `db.accounts.find_one(...)` from a fresh `asyncio.run`. PASS = no `RuntimeError: Event loop is closed` / no hang.
- **Row 3-10**: paired-pytest invocations of polluter + each previously-polluted FTT ID in turn:
  - `polluter + test_phase_p3_2_cookie_hardening` (FTT-015/016) → all PASS
  - `polluter + test_phase_p5_10_audit_panel_direct_linkage` (FTT-017/018) → all PASS
  - `polluter + test_phase_p5_7_5_bounce_webhook` (FTT-019..022) → all PASS
  - `polluter + test_phase_p5_10_audit_panel_direct_linkage + test_track_b_phase2_task_lifecycle` (FTT-023 tiered) → all PASS
- **Row 11**: standalone polluter file → all 7 tests PASS in isolation (closes FTT-014 deterministic regression in the same run).

Acceptance: 11/11 GREEN. Surface ratchet asserts at the new pin (`9aa905f6d951f2a8`).

---

### §2.2 — Cluster B.2 — test-side hardening on `tests/test_track_b_phase_b5_g6_notes_autosave.py`

**Closes**: FTT-024..026 (3 IDs). 15 confirmed polluters from P5.7-HOLDOUT-FINISHER, all in the auth/session/CSRF surface area.

**Locked-area check**: `tests/test_track_b_phase_b5_g6_notes_autosave.py` — TEST FILE only. The proposed fix touches per-test fixtures in the file. **Zero touches** to Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer. Cleared.

**Pollution surface analysis** (from source-read of the file, lines 31-50):
- Module-level imports: `import server`, `from server import app`, `from core import db`. These are stable across the broad-suite (no per-test re-import).
- The `transport` fixture is **function-scoped** (line 31-33 `@pytest.fixture` with no `scope=`). ✅ Already clean — not the leak vector.
- Each test calls `_csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")` — depends on:
  - `admin@akki.ai` row in `db.accounts` (must exist, password must hash-match, must not be `is_locked=True`)
  - `/api/csrf` returning a valid token (depends on CSRF dep registration)
  - `/api/auth/login` not being rate-limited (depends on `login_failed_attempts` counter)
  - `/api/auth/login` not returning 401 due to a stale dependency override (`app.dependency_overrides` accumulating from prior tests)

**Probable pollution mechanisms** (each maps to one or more of the 15 polluters):
- `app.dependency_overrides` not cleared after `test_phase_p3_1_csrf.py` / `test_phase_p3_2_cookie_hardening.py` / `test_phase_p3_4_session_timeout.py` — CSRF or session dep replaced with a stub that returns 401 to the autosave test's login
- `login_failed_attempts` counter for `admin@akki.ai` left at threshold by `test_phase_p2_b4_password_change.py` / `test_phase_p2_b6_admin_force_reset.py` — autosave's `_csrf_login` returns 429
- `db.session_revocations` populated by `test_phase_p5_5_session_reauth.py` / `test_phase_p5_10_audit_panel_direct_linkage.py` — admin's session revoked before autosave's PATCH lands
- `accounts.admin@akki.ai` mutation (MFA enrolment, password change, lockout flag) by `test_phase_p2_a2_microsoft_pkce.py` / `test_phase_p2_b4` / `test_synisense_security.py`

**Proposed minimal patches** (test-side hardening — described, NOT applied):

1. **Add an autouse function-scoped fixture** at the top of the autosave test file that resets the relevant per-test state before each test:
   ```python
   # Sketch — for memo only, not committed.
   @pytest.fixture(autouse=True)
   async def _reset_admin_auth_state():
       """B.2 hardening — per-test reset of admin auth state polluted
       by other auth/session/CSRF tests in the broad suite."""
       # 1. Clear login-failed-attempts counter.
       try:
           await db.login_failed_attempts.delete_many({"email": "admin@akki.ai"})
       except Exception:
           pass
       # 2. Clear session revocations for admin.
       try:
           admin = await db.accounts.find_one({"email": "admin@akki.ai"}, {"_id": 0, "id": 1})
           if admin:
               await db.session_revocations.delete_many({"account_id": admin["id"]})
       except Exception:
           pass
       # 3. Reset admin lockout / MFA flags to their canonical state.
       await db.accounts.update_one(
           {"email": "admin@akki.ai"},
           {"$unset": {"is_locked": "", "mfa_required": "", "force_reset_at": ""}},
       )
       # 4. Restore app.dependency_overrides to whatever conftest.py sets at session-start.
       #    (Exact symbols depend on conftest source; fix sprint must source-inspect.)
       _expected_overrides = getattr(app, "_conftest_baseline_overrides", None)
       if _expected_overrides is not None:
           app.dependency_overrides.clear()
           app.dependency_overrides.update(_expected_overrides)
       yield
   ```
   The exact symbol list above (`login_failed_attempts`, `session_revocations`, `is_locked` / `mfa_required` / `force_reset_at`) is derived from naming conventions in the polluter files; the fix sprint must source-inspect each polluter file to confirm the actual collection/field names it mutates. **This memo does NOT prescribe the exact symbol list** — only the fixture shape.

2. **Document the rationale** with a comment block above the fixture citing the 15-polluter holdout-finisher evidence at `/app/memory/jc_artifacts/test_pollution/confirmed_pairs/*BREAKS*notes_autosave*.md`.

**Proving slice design** (`backend/scripts/jc_pollution_b2_proving_slice.py`):
- **Row 1-15**: paired pytest invocations — each of the 15 confirmed polluters paired with the autosave file post-fix → all PASS:
  - `test_synisense_security` + autosave
  - `test_phase_p5_{5,7,7_5,8,9,10}_*` (6 files) + autosave
  - `test_phase_p3_{1,2,4}_*` (3 files) + autosave
  - `test_phase_p2_{a2,b1,b4,b6,d2}_*` (5 files) + autosave
- **Row 16**: autosave file in isolation → all 3 tests PASS (no regression from the new fixture).
- **Row 17**: full-suite measurement — re-run holdout-finisher's full predecessor sweep on autosave; assert ZERO confirmed polluters post-fix.

Acceptance: 17/17 GREEN.

---

### §2.3 — Inter-cluster measurement procedure (between A+D ship and B.2 dispatch)

This is the load-bearing reason for sequencing over bundling. Between the A+D fix sprint closing and the B.2 fix sprint dispatching, the next agent MUST:

1. **Re-run the holdout-finisher's full predecessor sweep on `tests/test_track_b_phase_b5_g6_notes_autosave.py`** using `backend/scripts/jc_pollution_holdout_finisher_slice.py` with the predecessor candidate set narrowed to just that one polluted file (a ~30 min run rather than the full 53-min original).
2. **Compare** the 15-polluter list pre-A+D vs post-A+D:
   - **Polluters that disappear from the list** = they were depending on A+D's env / Motor-loop leak. Their pollution was a downstream symptom of A+D. B.2's scope shrinks by that count.
   - **Polluters that remain in the list** = genuine session/cookie/auth state issues. B.2's actual scope is this residual set.
3. **Surface the delta** in the post-A+D sprint-close handoff, so B.2's dispatch is sized on real evidence. The handoff note should explicitly state:
   - Pre-A+D polluter count: 15
   - Post-A+D polluter count: N (where N is measured, not predicted)
   - Net-new polluters surfaced (if any): list
   - Recommended B.2 scope: bare-minimum hardening to close the residual N polluters

**Why this matters**: if N = 0, B.2 is closed for free by A+D and there is no B.2 sprint to dispatch. If N = 15, B.2's scope is fully separate from A+D. The real number is almost certainly between — and the measurement IS the dispatch shape.

---

## §3 — Surface 2 (SECONDARY · Cluster B.1)

### §3.1 — Cluster B.1 — module-scoped async-fixture demotion on `tests/test_p_cleanup_c_help_tooltip_suppression.py`

**Closes**: FTT-010..012 (3 IDs). **0 confirmed pairwise polluters** in 69 candidates from P5.7-HOLDOUT-FINISHER (the smoking-gun finding for this cluster's shape — pollution is shared-global-state, NOT pairwise).

**Locked-area check**: `tests/test_p_cleanup_c_help_tooltip_suppression.py` — TEST FILE only. The proposed fix touches one fixture decorator. **Zero touches** to Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer. Cleared.

**Shared global state identified** (from source-read, lines 43-45):

```python
@pytest_asyncio.fixture(scope="module")
async def transport():
    yield ASGITransport(app=app)
```

The `transport` fixture is **`scope="module"`** and **`pytest_asyncio.fixture` (async)**. `pytest-asyncio` binds module-scoped async fixtures to the event loop active at first-resolution. Across the broad suite, hundreds of preceding tests create-and-close their own event loops (`asyncio.run`, fresh `@pytest_asyncio` function-scoped fixtures, etc.). By the time the module-scoped `transport` resolves, the `ASGITransport(app=app)` object holds an `app` whose Motor singletons / dependency overrides / middleware state may be bound to a closed loop or stale dependency map.

**The 0-pairwise finding is exactly consistent with this shape**: any single-pair invocation creates only ONE event-loop transition before the module fixture resolves, which is rarely enough to corrupt it. Only an accumulation of MANY loop transitions across the broad-suite reliably breaks it.

**Proposed minimal patches** (described, NOT applied):

1. **Demote the fixture to function-scope** (single-line change):
   ```python
   # Sketch — for memo only, not committed.
   @pytest_asyncio.fixture
   async def transport():
       yield ASGITransport(app=app)
   ```
   No other change required; each test gets a freshly-resolved transport bound to the per-test event loop.

2. **Secondary (only if (1) is insufficient)**: add an autouse function-scoped fixture that explicitly clears any test-leftover `app.dependency_overrides` state before each test runs.

**Proving slice design** (`backend/scripts/jc_pollution_b1_proving_slice.py`):
- **Row 1**: paired pytest — pick any 3 files from the P5.7-HOLDOUT-FINISHER 69-candidate sweep (e.g., 3 random PASS-bucket predecessors), pair each with the polluted file → all PASS (regression-free).
- **Row 2**: broad-suite simulation — run a randomly-ordered subset of 50 PASS-bucket predecessor files + the polluted file → all PASS.
- **Row 3**: full-suite re-run — run the broad suite via P5.7-HOLDOUT-FINISHER's harness against the post-fix polluted file → FTT-010..012 no longer surface as FAIL_IN_CONTEXT.
- **Row 4**: isolation re-run — polluted file alone → all 5 tests PASS (no regression).

Acceptance: 4/4 GREEN.

---

## §4 — Surface 3 (TERTIARY · Cluster C — PARKED)

### §4.1 — Cluster C — intra-file fixture refactor on `tests/test_iter41_signal_actions_in_process.py` (PARKED)

**Closes**: FTT-004..009 (6 IDs). **Intra-file pollution** — per P5.7-BISECT, pollution does NOT come from external files; it comes from within `test_iter41_signal_actions_in_process.py` itself (six tests in the same file mutating module-scoped state that subsequent tests in the same file then read).

**Status in this scope memo: PARKED**. Per user direction (a):

> "Cluster C was parked at the prior dispatch because the source-reads on A+D/B.1/B.2 are already substantive. Pulling C in would dilute the memo. C gets its own dispatch with its own source-read pass after the first three clusters close."

**Disposition**: Cluster C is logged in `BACKLOG_SCHEDULE.md` (P1 row 11, sub-bullet "C — intra-file"); it gets its own scope memo + own source-read pass + own fix sprint when the user dispatches it, AFTER the A+D / B.2 / B.1 sequence closes. No source-read of `test_iter41_signal_actions_in_process.py` was performed in this memo.

---

## §5 — Per-cluster regression-check ladder (what proves we didn't break anything)

Applied AT EACH cluster's fix-sprint close, BEFORE the next cluster's dispatch:

| Check | Cluster A+D | Cluster B.2 | Cluster B.1 |
|-------|:------------|:------------|:------------|
| Invariant suite (`tests/invariants/*`) GREEN | required | required | required |
| Stage 1 deck byte-identical (76555 bytes) | required | required | required |
| 450/450 Solva v2 schema+validator tests PASS | required | required | required |
| Surface ratchet at `9aa905f6d951f2a8` (or rolled forward by additive only) | **THIS IS THE RATCHET REFRESH** — A+D rolls the test's hardcoded sha forward to current pin; the pin itself is unchanged | required (unchanged) | required (unchanged) |
| JC-TM email path smoke | required | required (the autosave / email surfaces are adjacent) | required |
| Convergent pptx render (76555 bytes) | required | required | required |
| Divergent pptx render (69105 bytes / 14 slides) | required | required | required |
| Cluster's own paired-pytest proving slice GREEN | A+D: 11/11 | B.2: 17/17 | B.1: 4/4 |

Any check failing on any sprint = HALT and surface; do NOT dispatch the next cluster until the failure is investigated.

---

## §6 — Locked-area re-confirmation (per cluster)

| Cluster | Files touched (test files only) | Touches Shield? | Touches WS Generate Doc UI? | Touches Track-2 schema? | Touches Monitor pre-warmer? | Cleared? |
|---------|---------------------------------|:---:|:---:|:---:|:---:|:---:|
| A+D | `tests/test_phase4_2_http_transport_smoke.py` (one function body + one constant) | no | no | no | no | ✅ |
| B.2 | `tests/test_track_b_phase_b5_g6_notes_autosave.py` (one new autouse fixture) | no | no | no | no | ✅ |
| B.1 | `tests/test_p_cleanup_c_help_tooltip_suppression.py` (one fixture decorator change) | no | no | no | no | ✅ |

If during the fix sprint any patch requires touching ANY of the four locked-area surfaces — even adjacent — **HALT and surface separately**. The locked-area discipline supersedes the fix-sprint dispatch.

---

## §7 — Discipline notes (this memo)

- **READ-ONLY contract honoured**: 0 product code mutated. 0 test files mutated. 0 fixture files mutated. 0 invariant files mutated.
- **Pure source-read output**: every finding cited file:line precise from the three target test files. No speculation marked as fact.
- **No fix code committed**: all `Sketch — for memo only, not committed.` snippets are illustrative, not patches.
- **No proving slice script written yet**: the three proving slices (`jc_pollution_a_d_proving_slice.py`, `jc_pollution_b2_proving_slice.py`, `jc_pollution_b1_proving_slice.py`) are designed in §2/§3 above; their authoring belongs to each cluster's fix sprint.
- **No testing subagent used** (per banned-list rule).
- **HARD STOP at memo surface**: this memo closes the diagnostic chain. Next dispatch = Cluster A+D fix sprint, dispatched separately by user.

---

## §8 — Files produced by this sprint

- `/app/memory/sprints/P5_7_FIX_SCOPE.md` NEW (this memo · ~330 lines · READ-ONLY)
- `/app/memory/DEV_PIPELINE.md` UPDATED (§9 row added for P5.7-FIX-SCOPE per standing rule "DEV_PIPELINE.md updated before sprint memo")

## §9 — Files NOT touched by this sprint

- 0 product code mutated (`backend/`, `frontend/`)
- 0 test files mutated (`backend/tests/`)
- 0 fixture files mutated
- 0 invariant files mutated
- 0 proving-slice scripts authored (deferred to each cluster's fix sprint)

---

## §10 — User-direction surface (what to dispatch next)

The next agent (post user direction) should dispatch **Cluster A+D fix sprint** as its own task with its own canonical-spec-cited sprint memo, its own proving slice (`backend/scripts/jc_pollution_a_d_proving_slice.py`), and its own HARD STOP at slice close.

After A+D ships GREEN, the inter-cluster measurement procedure in §2.3 runs, then **Cluster B.2 fix sprint** dispatches with its scope sized on the post-A+D residual polluter list.

After B.2 ships GREEN, **Cluster B.1 fix sprint** dispatches.

After B.1 ships GREEN, **Cluster C** (parked) is dispatched as its own scope-memo + fix-sprint sequence, mirroring the discipline of this memo.

Standing rules unchanged across all four sprints:
- Canonical spec on line 1 of every memo
- READ-ONLY scope memos before fix sprints
- DEV_PIPELINE.md updated before sprint memo
- Confirm before fix
- No testing subagent
- HALT-on-locked-area
