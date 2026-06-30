**Canonical Spec**: `/app/memory/sprints/P5_7_HOLDOUT_FINISHER.md §1 Cluster C row` + `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md L22 + L34 + L71` (joint canonical authority for Cluster-C intra-file refactor: 1 file × 6 tests = FTT-004..009 closure via module-scoped state → function-scoped fixtures refactor) + advance scan `sprints/P5_7_FIX_SCOPE_CLUSTER_C_ADVANCE.md` (locked dispatch shape + all 5 escalation triggers cleared).

# Sprint JC-POLLUTION-CLUSTER-C-FIX — Cluster-C intra-file refactor (fixture-isolation family)

**Status**: SHIPPED · test-file-only patches · proving slice **13/13 GREEN** · minimal-scope dispatch honoured · NEW mechanical family documented · 0 production code touched · HARD STOP at slice close
**Date**: 2026-06-30
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_C_ADVANCE.md` (advance scan; all 5 triggers cleared)

---

## §1 — Conversion summary

**Touched files**:
- `backend/tests/test_iter41_signal_actions_in_process.py` MOD (~+30 LOC net)

**Conversion shape**: fixture-isolation refactor. 3 module-level free helper functions REMOVED + replaced with 3 `@pytest_asyncio.fixture` function-scoped fixtures + 1 `@pytest.fixture(autouse=True)` defensive fixture.

| Removed (module-level free fn) | LOC | Replaced by (fixture) | Scope | Teardown |
|---|---:|---|---|---|
| `_client()` L44 | 5 | `client` fixture (async-with-yield) | function | `async with` closes connection |
| `_register(c, prefix)` L51 | 16 | `registered_user` fixture (yields `(token, account, ctx_id)`) | function | deletes `accounts` + `contexts` rows |
| `_seed_signal(ctx_id, kind, headline)` L67 | 14 | `signal_factory` fixture (factory pattern; tracks created sids) | function | deletes `signals` + `signal_actions` rows |
| — (new defensive) | — | `_reset_app_dependency_overrides` autouse fixture | function | clears + restores snapshot |

**Net diff**: +63 LOC fixture defs/teardowns + -37 LOC removed module-level helpers + per-test signature changes balance out = **~+30 LOC net** (advance scan estimate ~+25 LOC; the +20% delta vs estimate is from the factory pattern in `signal_factory` which lets s41.C parameterize `kind="opportunity"` without indirect-parametrize ceremony).

**6 test functions updated** to inject fixtures + remove `async with _client()` context manager wrapper. Assertion logic UNCHANGED per anti-source-string-assertion discipline.

---

## §2 — Banked rules adherence

| Rule | Applied? | How |
|---|:---:|---|
| RULE-1 (minimal scope) | ✓ | Diff = fixture refactor ONLY; no behavioral test changes; same assertion chains; 0 product code touched |
| RULE-2 (no cosmetic cleanups) | ✓ | Module-level helpers removed because they're REPLACED by fixtures (direct mechanical consequence, not cosmetic); docstring + imports PRESERVED |
| F.5 YAML-edit single-batch | N/A | No YAML edits this dispatch (Cluster-C is NOT in M1+M2 family; ceilings UNCHANGED at 0/1 FINAL) |
| F.3-ADVANCE memo-order (lesson #1) | ✓ | `DEV_PIPELINE.md §9` row authored BEFORE this memo file (chronological evidence in the row sequence) |
| G.1 slice-poll-cadence (lesson #3) | ✓ | Slice ran in single foreground call (~100s including inventory slice re-use of 50.6s); well under foreground timeout |
| G.3-VERIFICATION AST-over-grep (lesson #4) | ✓ | AST scan used for Row 3 (autouse fixture decorator detection) + Row 12 (helper-removal + fixture-presence + decorator-count check) + Row 13 (test_count + async_test_count tally); no fragile greps for invariant validation |
| NEW lesson #5 UNQUARANTINED runtime PASS baseline (G.4-ADVANCE) | ✓ THIRD APPLICATION | Row 1 of slice verifies 6/6 PASS preservation against advance-scan baseline (advance scan: 6/6 in 5.49s; post-fix: 6/6 in 5.51s — runtime delta within expected variance) |
| NEW lesson #6 file-names-from-YAML (G.4-FIX) | ✓ | Target file `test_iter41_signal_actions_in_process.py` sourced via direct text reads of `FAILING_TEST_TRACKER.md L22` + `P5_7_HOLDOUT_FINISHER.md §1 Cluster C row`; G.4 trio + G.5 file + iter regression filenames sourced from disk lookups (matching G.5 fix lesson application) |

---

## §3 — Proving slice rows (13/13 GREEN)

| Row | Check | Result |
|---:|---|---|
| 1 | iter41 file runtime PASS preservation (lesson #5; baseline 6/6 preserved) | 6 passed in 5.51s |
| 2 | Per-test isolation: 6 FTT-004..009 tests run SOLO + pass | solo_pass=6/6 |
| 3 | `app.dependency_overrides` snapshot/restore autouse fixture validated (AST + behavioral) | has_autouse_decorator=True · clears_and_restores=True |
| 4 | Cross-test pollution scan: iter41 6/6 preserved after running with polluters in same invocation | polluter_combined_rc=0 · post-combined iter41 solo PASS=True · 'Future attached to a different loop' signatures=0 |
| 5 | autosave defensive (B.2 polluter pair pattern; Cluster-F closure regression-free) | 3 passed in 5.14s |
| 6 | phase4_2 A+D defensive (surface ratchets lockstep + A+D-preserved M2 entry intact) | 8 passed in 4.98s |
| 7 | G.4 trio post-fix runtime regression (phase12_2 + phase_a + solva_v2) | 10 passed in 5.91s |
| 8 | G.5 file + G.2/G.3 sibling regression (synisense_surface 34/34 + iter39/53/54 26 skipped) | 34 passed · 26 skipped in 3.96s |
| 9 | iter41 file + invariant suite (9/9 = 6 iter41 + 3 invariant) | 9 passed in 7.70s |
| 10 | Invariant cross-validation M1=0/M2=1 UNCHANGED FINAL (Cluster-C NOT in M1+M2 family) | 3 passed in 5.92s |
| 11 | Inventory slice steady state 9/10 + YAML M1=0/M2=1 unchanged | exit=1 (expected 9/10 RED-on-baseline-row) dur=50.6s · YAML M1=0/M2=1 · 9/10 GREEN steady state observed |
| 12 | AST source-check: 3 module-level helpers REMOVED + 4 fixtures present + decorated | helpers_removed=ALL · fixtures_present=4/4 · decorator_count=4/4 |
| 13 | FTT-004..009 closure trajectory marker (6 IDs ready for FTT registry update) | test_count=6/6 · async_test_count=6/6 |

**Aggregate**: 13/13 GREEN · slice runtime ~100s (incl. inventory slice 50.6s reuse) · 0 RED rows on first run · 0 mid-flight script-level slips · 0 conversion failures.

---

## §4 — Closure-schedule lock state

| Ceiling | Pre-Cluster-C | Post-Cluster-C | Change | Reason |
|---|:---:|:---:|:---:|---|
| `M1_CEILING` | 0 | 0 | UNCHANGED FINAL | Cluster-C is NOT in M1+M2 family; M1 has been FINAL since G.1 close |
| `M2_CEILING` | 1 | 1 | UNCHANGED FINAL | Cluster-C is NOT in M1+M2 family; the A+D-preserved entry at `phase4_2_http_transport_smoke:254` remains by design as Cluster-G arc end-state |

**Cluster-C is the FIRST sub-sprint of a DIFFERENT mechanical family (fixture-isolation refactor) — it intentionally does NOT participate in the M1+M2 ratchet.** Future fixture-isolation refactor sub-sprints (if any) would similarly not touch these ceilings.

---

## §X — NEW mechanical family: fixture-isolation refactor

(Per user explicit ask: document the conversion shape so future scans can recognize it.)

### §X.1 — Family characterisation

| Family | Mechanical shape | Pollution mechanism addressed | Identifier patterns |
|---|---|---|---|
| **F+G** (sync→async test body conversion) | `def → @pytest.mark.asyncio + async def` + `asyncio.run(coro) → await coro` + module-level `_run` helper conversion | wrong-loop-binding from sync `asyncio.get_event_loop().run_until_complete` polluting downstream `@pytest.mark.asyncio` tests | module-level `_run = asyncio.get_event_loop().run_until_complete(coro)` (M1) · `asyncio.run(...)` call inside test_* body (M2) |
| **Cluster-C** (fixture-isolation refactor) — NEW | module-level free helper functions → `@pytest_asyncio.fixture` function-scoped fixtures with `yield + teardown` cleanup + autouse `app.dependency_overrides` snapshot/restore | shared-mutable-singleton pollution from upstream tests mutating FastAPI `app.dependency_overrides` or holding Motor connection state without cleanup | module-level `def _helper(...)` or `async def _helper(...)` taking shared singletons as implicit deps · tests calling helpers inside `async with _client()` context managers |

**The two families are MUTUALLY EXCLUSIVE for any given file.** A test file is EITHER an `asyncio.run`-in-test polluter (F+G family) OR a shared-fixture-state polluter (Cluster-C family) OR neither, but never both. The decision tree at scope time:

```
1. Run `grep -nE "asyncio\.run|_run\s*=" tests/<file>.py`
   - If ANY hit → F+G family (sync→async conversion)
   - If NO hits → continue to step 2

2. Run AST scan for module-level `def _<helper>(...)` or `async def _<helper>(...)` taking implicit shared singletons
   - If ANY helpers found that operate on FastAPI app / Motor singleton / similar → Cluster-C family (fixture-isolation refactor)
   - If NO helpers → file may have a third (yet-unidentified) mechanical family; advance-scan required
```

### §X.2 — Cluster-C refactor template (canonical reference)

```python
# BEFORE — module-level free functions sharing singletons:
def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

async def _register(c, prefix: str):
    # ... uses shared app singleton implicitly via httpx ASGI transport ...
    return token, account, ctx_id

async def _seed_signal(ctx_id, *, kind="risk", headline="..."):
    # ... uses shared core_mod.db singleton ...
    return sid

@pytest.mark.asyncio
async def test_foo():
    async with _client() as c:
        token, _, ctx_id = await _register(c, "prefix")
        sid = await _seed_signal(ctx_id, kind="risk")
        # ... assertions ...

# AFTER — function-scoped fixtures with teardown:
import pytest_asyncio

@pytest.fixture(autouse=True)
def _reset_app_dependency_overrides():
    """Defensive snapshot/restore against upstream dep-override leaks."""
    snapshot = dict(app.dependency_overrides)
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(snapshot)

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test",
    ) as c:
        yield c

@pytest_asyncio.fixture
async def registered_user(client, request):
    # ... register fresh user; yield (token, account, ctx_id) ...
    yield token, account, ctx_id
    # Teardown: delete account + contexts
    try:
        await core_mod.db.accounts.delete_one({"id": account["id"]})
        await core_mod.db.contexts.delete_many({"account_id": account["id"]})
    except Exception:
        pass

@pytest_asyncio.fixture
async def signal_factory(registered_user):
    """Factory pattern: variable-kind seeding with cleanup tracking."""
    _, _, ctx_id = registered_user
    created: list[str] = []
    async def _create(*, kind="risk", headline="..."):
        sid = str(uuid.uuid4())
        await core_mod.db.signals.insert_one({...})
        created.append(sid)
        return sid
    yield _create
    # Teardown: delete all tracked signals + actions
    for sid in created:
        try:
            await core_mod.db.signals.delete_one({"id": sid})
            await core_mod.db.signal_actions.delete_many({"signal_id": sid})
        except Exception:
            pass

@pytest.mark.asyncio
async def test_foo(client, registered_user, signal_factory):
    token, _, ctx_id = registered_user
    sid = await signal_factory(kind="risk")
    # ... assertions UNCHANGED ...
```

### §X.3 — Defensive autouse fixture rationale

The `_reset_app_dependency_overrides` autouse fixture is the SINGLE MOST IMPORTANT addition vs the bare fixture-conversion. It addresses the DOMINANT pollution surface (advance scan §2.2 surface 1) — FastAPI `app.dependency_overrides` is a shared mutable dict; upstream tests that add overrides without cleanup leak state.

**Snapshot/restore semantics** (NOT clear-only): if a test ITSELF adds an override (some chat surface tests do), the snapshot/restore semantics correctly remove the test's override at teardown while preserving any pre-existing overrides set by conftest or earlier test setup. This is more conservative than `app.dependency_overrides.clear()` at teardown (which would wipe legitimate conftest setups).

**Function-scoped** (not session-scoped): every test gets a fresh snapshot/restore cycle, so the defense applies to each FTT independently. The pollution defense is per-test, not per-suite.

### §X.4 — Factory pattern vs single-shot fixture

The `signal_factory` uses a factory pattern (yields an async callable) rather than a single-shot `seeded_signal` fixture. This is because s41.C requires `kind="opportunity"` while s41.A/B/D use `kind="risk"`. The factory pattern:
- Avoids indirect-parametrize ceremony (`@pytest.mark.parametrize("seeded_signal", [{...}], indirect=True)`)
- Lets each test call `await signal_factory(kind=...)` inline with explicit kwargs
- Tracks ALL created sids so teardown can clean up multi-seed tests cleanly (e.g., if a test needs both risk + opportunity signals, the factory handles both)

Factory-pattern fixtures are a pytest idiom for variable-input fixture lifecycles; Cluster-C is a natural use case.

### §X.5 — Future application: file classifier heuristic

For future test-pollution sprints, files exhibiting both pollution-mechanism families have not yet been observed across 27 converted files. If a hybrid file IS encountered (Cluster-C-style helpers AND F+G-style `asyncio.run`-in-test), the dispatch shape would need to address both mechanics in sequence; the families are mutually exclusive per FILE but in principle a file could carry both anti-patterns. Surface this discovery via a dedicated advance scan.

---

## §5 — Locked-area sweep

| Area | Touched? |
|---|:---:|
| Shield internals (`services.synisense.*`) | NO |
| Track-2 schema (`perspective_spread` + divergent deck builder) | NO |
| Monitor pre-warmer (`services/monitor/*`) | NO |
| OAuth provider live endpoints | NO |
| WS Doc UI (doc-generation rendering) | NO |
| Product code (`backend/*.py` outside `tests/`) | NO |
| Storage arc (Azure SAS work; PAUSED awaiting creds) | NO |
| Existing GridFS upload path | NO |
| Backfilled 3068 rows | NO |
| Bespoke-run invariant (M1+M2 ceilings) | NO (Cluster-C NOT in M1+M2 family) |
| FAILING_TEST_TRACKER.md | YES (mark FTT-004..009 ✅ CLOSED; in-scope per dispatch) |

Cleared. Only registry edit is the FTT closure (in-scope per dispatch shape).

---

## §6 — FTT closure trajectory

**FTT-004..009 closed in single sub-sprint** (6 IDs):

| FTT | s41 label | Test | Closure mechanism |
|---|---|---|---|
| FTT-004 | s41.A | `test_s41_a_get_recommendations_returns_bucket_and_three` | fixture-isolation refactor |
| FTT-005 | s41.B | `test_s41_b_post_acted_persists_and_summarises` | fixture-isolation refactor |
| FTT-006 | s41.C | `test_s41_c_post_shared_aggregates_recipients` | fixture-isolation refactor (with `kind="opportunity"` via factory) |
| FTT-007 | s41.D | `test_s41_d_actions_list_orders_most_recent_first` | fixture-isolation refactor |
| FTT-008 | s41.E | `test_s41_e_post_action_unknown_signal_returns_404` | fixture-isolation refactor (no `signal_factory` injection needed) |
| FTT-009 | s41.F | `test_s41_f_invalid_action_type_returns_422` | fixture-isolation refactor |

`FAILING_TEST_TRACKER.md L22` row updated to ✅ **CLOSED by JC-POLLUTION-CLUSTER-C-FIX (2026-06-30)** — single-dispatch fixture-isolation refactor; module-level free helpers → function-scoped fixtures with yield+teardown + autouse `app.dependency_overrides` snapshot/restore. Proving slice 13/13 GREEN. Closes 6 FTT IDs in single sub-sprint.

**FTT registry post-Cluster-C**:
- Cross-test pollution FLAKES: 0 ACTIVE (all 18 IDs in 7 files closed across A+D, B.1, B.2, C, Cluster-E, Cluster-F)
- DETERMINISTIC REGRESSIONS: 0 ACTIVE (FTT-014 closed by Cluster-F arc + anti-false-GREEN audit)
- Remaining ACTIVE: FTT-027..035 (thin-assertion grandfathered debt with machine-enforced ceiling at YAML-count — separate dispatch shape)

---

## §7 — Pattern uniformity tracker

**12 sub-sprints across 2 mechanical families**:
- F+G family (sync→async; 11 sub-sprints): F.2 + F.1 + F.4 + F.5 + F.3 + F.6 + G.1 + G.2 + G.3 + G.4 + G.5 = 26 files converted
- Cluster-C family (fixture-isolation; 1 sub-sprint): C = 1 file converted

**Total: 27 files converted across 2 mechanical families with 0 conversion failures.**

Cumulative arc M2 ratchet (F+G family): 28 → 1 FINAL (-27 sites; A+D-preserved entry remains by design).
Cumulative FTT registry closures (cross-family): 18 distinct nodes in 7 files (all CROSS-TEST POLLUTION IDs from initial P5.7-PER-FILE-CAPTURE classification).

---

## §8 — Discipline notes

- **READ-ONLY scope honoured outside the target test file**: only `tests/test_iter41_signal_actions_in_process.py` MOD + `scripts/jc_pollution_cluster_c_proving_slice.py` NEW + `memory/sprints/JC_POLLUTION_CLUSTER_C_FIX.md` NEW + `memory/jc_artifacts/FAILING_TEST_TRACKER.md` MOD (FTT closure row); `DEV_PIPELINE.md §9` row MOD (added BEFORE memo per lesson #1)
- **Canonical spec cited on line 1**: explicit cite of `P5_7_HOLDOUT_FINISHER.md §1 Cluster C row` + `FAILING_TEST_TRACKER.md L22+L34+L71` + advance scan
- **No testing subagent used** (per user explicit ban)
- **No scope creep**: numbered sections match the advance scan's proving-slice plan + user explicit asks (Row 3 autouse fixture validation + Row 4 cross-test pollution scan)
- **HARD STOP** at slice close per dispatch shape; standing rules unchanged
- **Cluster-C arc CLOSED in 1 sub-sprint** (no retrospective dispatch needed per advance scan §4.3 cluster-C scope)
- **Storage arc remains PAUSED** awaiting Azure credentials per locked user call #2
- **Next dispatch** per user autonomous mandate: LLM_MODELS_REFRESH .2/.3 evaluation (queue item 7) with explicit user-dep stop check baked in

---

## §9 — User-direction surface (HARD STOP)

Cluster-C dispatch milestone:
- ✅ Fixture-isolation refactor landed (3 module-level helpers → 3 function-scoped fixtures + 1 autouse defensive fixture)
- ✅ Proving slice 13/13 GREEN (Row 1 lesson #5 baseline preserved · Row 3 autouse fixture validated · Row 4 cross-test pollution scan clean · Row 12 AST source-check)
- ✅ M1=0/M2=1 ceilings UNCHANGED FINAL (Cluster-C NOT in M1+M2 family)
- ✅ FTT-004..009 6 IDs ready for registry update (Row 13)
- ✅ NEW mechanical family documented at §X (fixture-isolation refactor; distinct from F+G sync→async family)
- ✅ All 6 banked discipline-slip lessons applied (lesson #5 third application; lesson #6 file-names-from-disk)
- ✅ 0 production code touched · 0 mid-flight slips · 0 conversion failures
- ✅ Locked areas swept clean (Shield + Track-2 + Monitor + OAuth + WS Doc UI + product code + storage arc all 0)

**Open questions**: NONE.

**HARD STOP at slice close per dispatch shape; surfacing to user.** Cluster-C arc CLOSED. Per user autonomous mandate, LLM_MODELS_REFRESH .2/.3 evaluation can autonomously proceed at next dispatch boundary — with the explicit user-dep stop check baked in (STOP if implementation requires user-supplied API keys/model access; proceed if self-contained).

Files:
- `backend/tests/test_iter41_signal_actions_in_process.py` MOD (~+30 LOC net)
- `backend/scripts/jc_pollution_cluster_c_proving_slice.py` NEW (~260 LOC; 13-row slice)
- `memory/sprints/JC_POLLUTION_CLUSTER_C_FIX.md` NEW (this file; canonical spec line 1)
- `memory/jc_artifacts/FAILING_TEST_TRACKER.md` MOD (L22 FTT-004..009 ✅ CLOSED)
- `memory/DEV_PIPELINE.md` §9 row added BEFORE memo (lesson #1 honoured)

Standing rules unchanged. Time-gate status: no active time-gate. Cluster-G arc CLOSED; Cluster-C arc CLOSED; storage arc PAUSED awaiting Azure credentials per locked user call #2.

End of memo.
