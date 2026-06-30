**Canonical Spec**: `/app/memory/sprints/P5_7_HOLDOUT_FINISHER.md §1 Cluster C row` + `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md L22 + L34 + L71` (joint canonical authority for Cluster-C intra-file refactor: 1 file × 6 tests = FTT-004..009 closure via module-scoped state → function-scoped fixtures refactor) + cross-references `sprints/CLUSTER_G_RETROSPECTIVE.md §6.1` (Cluster-C applicability matrix prediction: lessons #1-#6 apply; F.6 CONDITIONAL — likely NOT but verify) + `sprints/JC_POLLUTION_CLUSTER_G5_FIX.md` (G.5 ship immediately preceding) + `sprints/CLUSTER_G_RETROSPECTIVE.md §3` (pattern uniformity at 11 sub-sprints).

# Sprint P5_7_FIX_SCOPE_CLUSTER_C_ADVANCE — Cluster-C intra-file refactor advance scan

**Status**: SHIPPED (memo only) · READ-ONLY · HARD STOP at memo surface · single Cluster-C dispatch shape RECOMMENDED · all 5 escalation triggers NOT TRIPPED so fix dispatch can autonomously proceed per user autonomous mandate
**Date**: 2026-06-30
**Predecessor**: `sprints/CLUSTER_G_RETROSPECTIVE.md` (Cluster-G arc FULLY CLOSED; autonomous queue continues to item 6 Cluster-C)

---

## §0 — FTT inventory (canonical, via FAILING_TEST_TRACKER + AST cross-validation)

Source authority (joint):
- `P5_7_HOLDOUT_FINISHER.md §1 Cluster C row` (L54): "intra-file (in-file isolation fix) | FTT-004..009 (6 IDs) | within `test_iter41_signal_actions_in_process.py` | Per-test-pair invocation within the file; refactor module-scoped state to function-scoped fixtures"
- `P5_7_HOLDOUT_FINISHER.md §3 closure path` (L69): "Cluster C intra-file refactor (separate sprint shape). Per-test-pair invocation within `test_iter41_signal_actions_in_process.py`; convert module-scoped state to function-scoped fixtures. Closes FTT-004..009 (6 IDs)."
- `FAILING_TEST_TRACKER.md L22`: "FTT-004..009 | `tests/test_iter41_signal_actions_in_process.py` | shared_fixture_state_iter41 (in-file) | 🟧 INTRA-FILE — separate sprint shape (per-test-pair within file)"
- `FAILING_TEST_TRACKER.md L34`: "Cluster C — `test_iter41_signal_actions_in_process.py` in-file pollution. Fixture refactor (module-scoped → function-scoped) closes 6 FTT IDs."
- `FAILING_TEST_TRACKER.md L71`: "FTT-004..009 | shared fixture-state | PASS in isolation | CROSS-TEST POLLUTION (kept)"

### §0.1 — FTT-to-test mapping (1:1 confirmed via AST scan)

| FTT | s41 label | Test function | Lineno | Async? | Risk |
|---|---|---|---:|:---:|---|
| FTT-004 | s41.A | `test_s41_a_get_recommendations_returns_bucket_and_three` | 85 | YES (`@pytest.mark.asyncio + async def`) | LOW (GET read-only) |
| FTT-005 | s41.B | `test_s41_b_post_acted_persists_and_summarises` | 109 | YES | MEDIUM (POST + read + summary recompute) |
| FTT-006 | s41.C | `test_s41_c_post_shared_aggregates_recipients` | 142 | YES | MEDIUM (POST × 2 with dedup + sort) |
| FTT-007 | s41.D | `test_s41_d_actions_list_orders_most_recent_first` | 181 | YES | MEDIUM (POST × 2 + temporal ordering) |
| FTT-008 | s41.E | `test_s41_e_post_action_unknown_signal_returns_404` | 210 | YES | LOW (404 negative test) |
| FTT-009 | s41.F | `test_s41_f_invalid_action_type_returns_422` | 227 | YES | LOW (422 validation negative test) |

**Total**: 1 file (240 LOC) · 6 tests · 6 FTT IDs · all UNQUARANTINED · all already `async def + @pytest.mark.asyncio` (NOT a sync→async target).

### §0.2 — Module-level state surfaces (the pollution-mechanism candidates)

AST scan identifies 3 module-level helper functions + 2 module-level singleton imports:

| Object | Kind | Lineno | Role |
|---|---|---:|---|
| `_client()` | sync helper function | 44 | Returns a fresh `httpx.AsyncClient(ASGITransport)` per call |
| `_register(c, prefix)` | async helper function | 51 | Registers a test user; returns `(token, account, ctx_id)` triple |
| `_seed_signal(ctx_id, *, kind, headline)` | async helper function | 67 | Inserts a `signals` row into `core_mod.db.signals` |
| `core as core_mod` | module-level import | 40 | Surfaces `core_mod.db` Motor singleton (SHARED MUTABLE) |
| `from server import app` | module-level import | 41 | Surfaces FastAPI app singleton (SHARED MUTABLE) |

The 3 helper functions are STATELESS in themselves but operate against the 2 SHARED MUTABLE singletons.

---

## §1 — Critical findings

### §1.1 — UNQUARANTINED (lesson #5 verify)

Verified via:
```bash
grep -nE "pytestmark|@pytest.mark.skip" /app/backend/tests/test_iter41_signal_actions_in_process.py
```

Result: **0 hits**. Tests RUN at runtime in CI.

This MATCHES the FTT tracker note "PASS in isolation" — confirming the file is UNQUARANTINED and lesson #5 applies (pre-conversion runtime PASS baseline + post-conversion preservation row required).

### §1.2 — Pre-conversion runtime baseline (locked)

```bash
python -m pytest tests/test_iter41_signal_actions_in_process.py --tb=short -q
```

Result: **6 passed in 5.49s** (21 warnings — `on_event` deprecation, unrelated).

Test breakdown: 6 collected, 6 passed (1 per FTT). This is the IN-ISOLATION baseline; the FTT tracker notes these tests FAIL "in context" (when upstream polluters mutate shared singletons).

Invariant suite baseline:
```bash
python -m pytest tests/invariants/test_no_bespoke_run_helper.py --tb=no -q
```

Result: **3 passed in 5.86s** (catcher + drift + count-ceiling with M1_CEILING=0 FINAL, M2_CEILING=1 FINAL).

Post-refactor target: 6/6 PASS preserved + 3/3 PASS preserved + M1_CEILING + M2_CEILING UNCHANGED (Cluster-C is NOT in the M1+M2 conversion family — ceilings are not subject to ratcheting in this dispatch).

### §1.3 — NOT Shield-adjacent (F.6 verify per retro §6.1)

Verified via:
```bash
grep -nE "synisense|shield_payload|pipeline_run|shield_" /app/backend/tests/test_iter41_signal_actions_in_process.py
```

Result: **0 hits**. File does NOT import `services.synisense.*` modules.

F.6 Shield-contract regression discipline-pay **N/A** this dispatch — matches retro §6.1 prediction "APPLIES ONLY IF FTT-004..009 touch Shield surface; LIKELY NOT but verify".

### §1.4 — Intra-file refactor scope CONFIRMED

Single file: `tests/test_iter41_signal_actions_in_process.py` (240 LOC). 0 cross-file dependency churn. Refactor is 100% in-file fixture restructuring per canonical authority mandate.

No FTT spills outside its primary file. 6 FTTs are 1:1 mapped to the 6 tests in the single file.

---

## §2 — Pollution mechanism root cause analysis

### §2.1 — Why tests PASS in isolation

In isolation, the pytest process loads:
- `core as core_mod` → fresh Motor client connection to MongoDB
- `from server import app` → fresh FastAPI app instance with all routes registered
- `app.dependency_overrides` empty
- No prior cache state, no prior session state, no prior middleware mutation

Each test creates fresh data with unique UUIDs (email = `s41-{prefix}-{uuid.uuid4().hex[:8]}@example.com`; signal id = `str(uuid.uuid4())`). Test data is isolated by UUID; no collision possible.

### §2.2 — Why tests FAIL in context

When an upstream test in a different file runs BEFORE these tests, that upstream test can:
1. **Mutate `app.dependency_overrides`** — e.g., override an auth dependency to bypass JWT validation; if not cleaned up, iter41 tests receive overridden auth that doesn't match their unique token
2. **Mutate `core_mod.db` connection state** — e.g., close the Motor client, replace it with a mock, or hold an open transaction
3. **Hold references that mutate `app.state`** — middleware state, cached responses, rate limiter state
4. **Leave async tasks pending** — orphan tasks from prior tests that still hold connections or modify state asynchronously
5. **Mutate `core_mod.<other_attrs>`** — anything in `core_mod` module namespace (auth helpers, config, fixtures, cached lookups)

Tests FAIL in context because the helper functions `_register` + `_seed_signal` assume CLEAN module state at call time. Module state is NOT clean when upstream pollution has occurred.

### §2.3 — Why function-scoped fixtures fix it

Pytest's function-scoped fixtures execute their setup + teardown for EACH test. By converting `_client` + `_register` + `_seed_signal` into fixtures with `yield + teardown`, we get:
1. **Fresh httpx AsyncClient per test** — no shared connection state across tests
2. **Fresh user registration per test** — token + account + ctx_id are PER-TEST scoped
3. **Fresh signal seed per test** — signal row is PER-TEST scoped
4. **Teardown cleanup** — created `signals` + `signal_actions` + `accounts` + `contexts` rows are deleted at test end; no carry-over to next test
5. **Optional autouse fixture for app.dependency_overrides reset** — snapshot at setup, restore at teardown — addresses surface (1)

The refactor doesn't change WHAT the tests verify (s41.A still tests GET recommendations, etc.); it changes HOW state is acquired + released. Same control-flow assertions per anti-source-string-assertion discipline noted in file docstring §7.

---

## §3 — Mechanical family classification

### §3.1 — DIFFERENT from F+G mechanical family

| Family | Cluster | Mechanical shape |
|---|---|---|
| **F+G family** | F.1-F.6 + G.1-G.5 | `def → @pytest.mark.asyncio + async def` + `asyncio.run(coro) → await coro` + module-level `_run` helper conversion |
| **Cluster-C family** (NEW) | C | Module-level free functions (`_client` / `_register` / `_seed_signal`) → `@pytest.fixture` function-scoped fixtures with `yield + teardown` cleanup |

Cluster-C is the **fixture-isolation refactor family** — DIFFERENT from the F+G `sync→async test body conversion family`. The two families are MUTUALLY EXCLUSIVE for any given file (a file is either F+G's `asyncio.run`-in-test polluter OR Cluster-C's shared-fixture-state polluter, not both).

### §3.2 — Family characterisation

Per retro §6.1 prediction: "Cluster-C is intra-file refactor (different mechanical family vs F + G's sync→async). Use Cluster-G's READ-ONLY scope memo + advance-scan default-on discipline; conversion family will differ."

Confirmed at this advance scan. The discipline scaffolding (advance scan → fix dispatch with §9 row before memo + canonical spec line 1 + proving slice with runtime PASS preservation + locked-area sweep) TRANSFERS from Cluster-G. The mechanical conversion shape is NEW.

### §3.3 — Refactor shape LOCKED (CANONICAL authority mandate)

```python
# BEFORE (module-level free functions):
def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

async def _register(c, prefix: str):
    # ... register user, return (token, account, ctx_id) ...

async def _seed_signal(ctx_id: str, *, kind: str = "risk", headline: str = "..."):
    # ... insert signal row, return sid ...

@pytest.mark.asyncio
async def test_s41_a_get_recommendations_returns_bucket_and_three():
    async with _client() as c:
        token, _, ctx_id = await _register(c, "s41-a")
        sid = await _seed_signal(ctx_id, kind="risk")
        # ... assertions ...

# AFTER (function-scoped fixtures with cleanup):
import pytest_asyncio

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    # No explicit teardown — async with closes connection

@pytest_asyncio.fixture
async def registered_user(client, request):
    """Register a fresh user; teardown deletes account + contexts."""
    prefix = f"s41-{request.node.name[-3:]}"
    email = f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"
    r = await client.post(
        "/api/auth/register",
        json={"email": email, "password": "Password123!@#",
              "name": f"{prefix.title()} Tester", "role": "executive"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    yield body["access_token"], body["account"], body["contexts"][0]["id"]
    # Teardown: delete account + contexts to avoid pollution
    await core_mod.db.accounts.delete_one({"id": body["account"]["id"]})
    await core_mod.db.contexts.delete_many({"account_id": body["account"]["id"]})

@pytest_asyncio.fixture
async def seeded_signal(registered_user, request):
    """Seed a signal; teardown deletes signal + any actions on it."""
    _, _, ctx_id = registered_user
    kind = getattr(request, "param", "risk")
    sid = str(uuid.uuid4())
    await core_mod.db.signals.insert_one({
        "id": sid, "context_id": ctx_id, "kind": kind, "tone": kind,
        "headline": "Test risk surface",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    yield sid
    # Teardown: delete signal + actions
    await core_mod.db.signals.delete_one({"id": sid})
    await core_mod.db.signal_actions.delete_many({"signal_id": sid})

@pytest.fixture(autouse=True)
def reset_app_dependency_overrides():
    """Snapshot + restore app.dependency_overrides for upstream pollution defense."""
    snapshot = dict(app.dependency_overrides)
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(snapshot)

@pytest.mark.asyncio
async def test_s41_a_get_recommendations_returns_bucket_and_three(client, registered_user, seeded_signal):
    token, _, ctx_id = registered_user
    sid = seeded_signal
    h = {"Authorization": f"Bearer {token}"}
    r = await client.get(
        f"/api/contexts/{ctx_id}/signals/{sid}/recommendations", headers=h,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("bucket") == "risk", body
    # ... rest of assertions unchanged ...
```

Same control-flow assertions per anti-source-string-assertion discipline. Helper-call invocations replaced with fixture injection.

### §3.4 — Estimated diff

| Component | LOC change |
|---|---|
| Module-level `_client` / `_register` / `_seed_signal` removed | ~-37 LOC |
| 4 new fixtures (`client`, `registered_user`, `seeded_signal`, `reset_app_dependency_overrides`) | ~+60 LOC |
| Per-test signatures updated to inject fixtures + remove `async with _client()` | ~+0 / -6 (net mild) |
| Test bodies: `token, _, ctx_id = await _register(c, "...")` → `token, _, ctx_id = registered_user` | ~-6 / +6 (zero net) |
| `from server import app` + `import core as core_mod` UNCHANGED | 0 |
| `pytest_asyncio` import added | +1 |

**Net estimated diff**: ~+25 LOC additive. Mechanical refactor; no behavioral change.

---

## §4 — Dispatch shape recommendation

### §4.1 — Single Cluster-C dispatch RECOMMENDED

| Evidence row | Implication |
|---|---|
| 1 file × 6 tests is same geometry as G.4's 3-file/5-site batch | Proven single-dispatch capacity |
| All 6 tests share IDENTICAL refactor shape (httpx ASGI + register + seed + assert) | No file-specific tailoring → no reason to split |
| Pattern uniformity at 11 sub-sprints (26 files, 0 conversion failures) | Mechanical confidence transfers to fixture refactor |
| Single proving slice can cover all 6 FTTs in 10-13 rows | Slice cadence fits established envelope |
| Risk classification varies LOW/MEDIUM per test but refactor mechanic UNIFORM | Cardinality argument doesn't push toward splitting |

### §4.2 — Sub-sprint shape alternatives REJECTED

- **Per-FTT sub-sprints (C.1-C.6)**: REJECTED — would require 6 separate dispatches for IDENTICAL mechanical refactor; 6× ceremony overhead; per-test risk variation doesn't justify subdivision
- **Grouped sub-sprints (e.g., LOW risk in C.1, MEDIUM in C.2)**: REJECTED — fixture refactor applies UNIFORMLY across all 6 tests in the same file; splitting by risk doesn't change the mechanic

### §4.3 — Escalation triggers evaluation (per user autonomous mandate)

| Trigger | Status | Reasoning |
|---|---|---|
| (a) Locked-area collision | **NOT TRIPPED** | 0 Shield/Track-2/WS Doc/Monitor/OAuth imports; conversion is 100% test-side fixture restructure |
| (b) Scope outside FTT-004..009 | **NOT TRIPPED** | EXACTLY 6 tests = FTT-004..009 1:1 mapping confirmed via AST scan; no spillover to adjacent files; 240 LOC single-file scope |
| (c) Genuine ambiguity in dispatch shape | **NOT TRIPPED** | 5 evidence rows uniformly favour single Cluster-C dispatch; refactor shape locked by canonical authority "module-scoped → function-scoped fixtures" |
| (d) FTT inventory mismatch | **NOT TRIPPED** | FAILING_TEST_TRACKER L22 + P5_7_HOLDOUT_FINISHER §1 Cluster C row + AST scan all 3 agree on the 6 tests in 1 file |
| (e) User-side input required | **NOT TRIPPED** | No env vars beyond `MONGO_URL` / `JWT_SECRET` / `DB_NAME` already in `.env`; no credentials; no schema decisions |

**All 5 triggers NOT TRIPPED** → per user autonomous mandate, fix dispatch can autonomously proceed with single Cluster-C shape on next turn.

---

## §5 — Locked-area sweep

| Area | Touched in conversion? | Touched in advance scan? |
|---|:---:|:---:|
| Shield internals (`services.synisense.*` modules) | NO | NO |
| Track-2 schema (`perspective_spread` slot, divergent deck builder) | NO | NO |
| Monitor pre-warmer (`services/monitor/*`) | NO | NO |
| OAuth provider live endpoints | NO | NO |
| WS Doc UI (doc-generation rendering) | NO | NO |
| Product code | NO mutation | NO mutation |
| Storage arc (Azure SAS work) | NO (independent arcs; storage PAUSED awaiting Azure creds) | NO |
| Existing GridFS upload path | NO | NO |
| Backfilled 3068 rows | NO | NO |
| Bespoke-run invariant (M1+M2 ceilings) | NO — Cluster-C is NOT in M1+M2 family; ceilings UNCHANGED at 0/1 FINAL | NO |
| FTT registry (`FAILING_TEST_TRACKER.md`) | YES — fix dispatch will mark FTT-004..009 CLOSED | NO (no edit this advance scan) |

Cleared. The only registry edit is the FTT closure update at fix-dispatch time — within scope of the dispatch.

---

## §6 — Per-banked-lesson application

All 6 banked discipline-slip lessons apply to the Cluster-C fix dispatch per retro §6.1. Applicability matrix:

| Lesson | Applies at fix? | Reasoning |
|---|:---:|---|
| #1 F.3-ADVANCE memo-order | YES | DEV_PIPELINE §9 row must precede memo authoring for the fix dispatch (already applied in this advance scan) |
| #2 F.5 YAML-edit single-batch | N/A | No YAML edits in this advance scan; fix dispatch may update FTT registry (markdown, not YAML); F.5 single-batch principle applies to markdown edits if multiple updates needed |
| #3 G.1 slice-poll-cadence-mismatch | YES | Fix dispatch will run proving slice in single foreground call (~60-90s expected; well under foreground timeout) |
| #4 G.3-VERIFICATION AST-over-grep | YES | AST scan used here for FTT-test mapping + helper-function identification; fix dispatch will use AST for source-check (Row 11 of slice) |
| #5 NEW UNQUARANTINED runtime PASS baseline (G.4 ADVANCE) | YES | UNQUARANTINED file → runtime PASS baseline (6/6 in 5.49s) captured here + preservation row required in fix proving slice (Row 1 mandatory) — THIRD APPLICATION of lesson #5 across arcs |
| #6 NEW file-name-from-YAML-not-memo (G.4 FIX) | YES | All non-target file references in fix proving slice (G.4 trio, iter39/53/54, autosave, phase4_2, p5_10) must be sourced from disk lookups not memo prose. Applied here: target file `test_iter41_signal_actions_in_process.py` sourced via direct text reads of `FAILING_TEST_TRACKER.md L22` + `P5_7_HOLDOUT_FINISHER.md §1 Cluster C row`, cross-validated by AST scan |

**Lesson #5 third application context**: G.4 fix (first; G.4 trio 10/10 PASS preserved BYTE-PERFECT) → G.5 fix (second; G.5 file 34/34 PASS preserved BYTE-PERFECT) → Cluster-C fix (third; iter41 6/6 PASS preserved post-refactor REQUIRED). Lesson #5 now extends from sync→async conversion family (F+G) to fixture-isolation family (C).

---

## §7 — F.6 Shield-contract discipline-pay applicability

Per retro §4.3 trigger criteria + §1.3 finding (NOT Shield-adjacent):

| F.6 trigger condition | iter41 status |
|---|---|
| Target file imports `services.synisense.*` modules directly | NO |
| Target file UNQUARANTINED | YES |
| At least one test calls async `pipeline.run` / `shield_payload_async` / `rehydrate` / `dryrun` / similar Shield-surface coroutine | NO |

**F.6 discipline-pay N/A** — 2-of-3 trigger conditions fail (no Shield imports + no Shield-surface calls). Confirms retro §6.1 prediction "LIKELY NOT but verify".

---

## §8 — Forward look (Cluster-C fix dispatch shape)

**Dispatch slug**: `JC-POLLUTION-CLUSTER-C-FIX` (single dispatch).

**Proving slice target rows (10-13)**:

| Row | Check | Expected |
|---:|---|---|
| 1 | **iter41 file runtime PASS preservation (lesson #5)** | **6/6 PASS preserved post-fixture-refactor** |
| 2 | iter41 file isolation post-fix (each test runs ISOLATED) | 6/6 PASS in ~5-6s |
| 3 | Each FTT-004..009 test runs solo + passes (per-test isolation verification) | 6 × 1/1 PASS |
| 4 | autosave defensive (B.2 polluter pair pattern) | PASS |
| 5 | phase4_2 A+D defensive (surface ratchets in lockstep) | 8/8 PASS |
| 6 | G.4 trio post-fix runtime regression | 10/10 PASS |
| 7 | G.5 file + G.2 + G.3 sibling regression (synisense_surface 34/34 + iter39/53/54 26 skipped) | 60+ PASS / skipped |
| 8 | iter41 file + invariant suite (9/9 PASS expected) | PASS |
| 9 | Invariant cross-validation M1/M2 ceilings UNCHANGED (0/1 FINAL) | 3/3 PASS |
| 10 | Inventory slice sibling re-run (steady state 9/10 + YAML unchanged) | GREEN |
| 11 | AST source-check helper functions REMOVED from module-level (fixtures present instead) | GREEN |
| 12 | Log scan zero `Future attached to a different loop` | 0 occurrences |
| 13 | FTT-004..009 closure trajectory marker (6 IDs closed; FTT registry updated) | All 6 marked CLOSED |

13 rows fits the established Cluster-G slice cadence. Lesson #6 applied: all file references sourced from disk lookups + YAML.

**FTT trajectory**: 6 IDs closed in single sub-sprint (FTT-004 + FTT-005 + FTT-006 + FTT-007 + FTT-008 + FTT-009). Total FTT closures across Cluster-C arc = 6 (single sub-sprint).

**Cluster-C arc retrospective forward-look (queue item AFTER fix)**: NOT enumerated in user dispatch queue (single sub-sprint arc; no retrospective needed). Cluster-C closes in 1 fix dispatch.

---

## §9 — Discipline notes

- **READ-ONLY scope honoured**: 0 LOC mutated outside this memo file
- **Canonical spec cited on line 1**: explicit cite of `P5_7_HOLDOUT_FINISHER.md §1 Cluster C row` + `FAILING_TEST_TRACKER.md L22+L34+L71` as joint canonical authority + cross-references to Cluster-G retro
- **F.3-ADVANCE memo-order slip lesson APPLIED**: DEV_PIPELINE.md §9 row authored BEFORE this memo file
- **F.5 YAML-edit slip lesson N/A**: no YAML edits this dispatch
- **G.1 slice-poll-cadence-mismatch lesson N/A**: no proving slice runs in scope; baseline pytest runs ~5.5s well under foreground timeout
- **G.3-VERIFICATION AST-over-grep lesson APPLIED**: AST scan used for FTT-test mapping (§0.1 table) + helper-function identification (§0.2 table) + module-level state surface enumeration; no fragile greps for invariant validation
- **NEW G.4-ADVANCE UNQUARANTINED-runtime-PASS-baseline (lesson #5) APPLIED**: 6/6 PASS in 5.49s captured at advance scan; will be required as proving-slice Row 1 in fix dispatch — THIRD APPLICATION across arcs
- **NEW G.4-FIX file-name-from-YAML (lesson #6) APPLIED**: target file `test_iter41_signal_actions_in_process.py` + canonical authority `P5_7_HOLDOUT_FINISHER.md` + `FAILING_TEST_TRACKER.md` sourced via direct text reads (not memo prose), cross-validated by AST scan
- **No testing subagent used** (per banned-list rule + user explicit ban)
- **No scope creep**: the 9 numbered sections + 1 discipline section is the exact deliverable per user dispatch
- **No build steps executed**: advance scan is READ-ONLY by definition
- **HARD STOP** at memo surface; standing rules unchanged
- **Cluster-C is a NEW mechanical family** (fixture-isolation refactor) — distinct from F+G (sync→async conversion); discipline scaffolding transfers, conversion shape is new
- **F.6 Shield-contract discipline-pay N/A** (NOT Shield-adjacent)
- **Storage arc remains PAUSED** awaiting Azure credentials

---

## §10 — User-direction surface (HARD STOP)

Per user autonomous mandate: **HARD STOP at memo surface; surface to user; Cluster-C fix dispatch can autonomously proceed at next dispatch boundary because all 5 escalation triggers (a/b/c/d/e) NOT TRIPPED.**

**Cluster-C advance scan milestone**:
- ✅ FTT inventory (§0): 1 file × 6 tests = FTT-004..009 with 1:1 mapping (AST cross-validated)
- ✅ Intra-file refactor scope CONFIRMED (§1.4): single file 240 LOC, 0 cross-file dependency
- ✅ UNQUARANTINED status verified (§1.1): lesson #5 applies, runtime baseline 6/6 PASS in 5.49s captured
- ✅ F.6 Shield-adjacency check (§1.3 + §7): NOT Shield-adjacent; F.6 discipline-pay N/A per retro §6.1 prediction
- ✅ Mechanical family classification (§3): NEW Cluster-C fixture-isolation refactor family; distinct from F+G sync→async family
- ✅ Dispatch shape recommendation (§4): SINGLE Cluster-C dispatch per 5 evidence rows; sub-sprint alternatives REJECTED
- ✅ Locked-area sweep (§5): Shield/Track-2/Monitor/OAuth/WS Doc untouched
- ✅ Risk classification per FTT (§0.1 + §3.4): LOW/MEDIUM split; UNIFORM refactor mechanic across all 6
- ✅ Open questions surfaced (§10 below): NONE
- ✅ 0 LOC mutated outside memo file

**Open questions**: NONE — all 5 escalation triggers cleared with high-confidence evidence; user dispatch enumerates expected deliverables completely; no user-side input required (no env vars, no credentials, no schema decisions).

**Next dispatch** (autonomous per user run-to-close mandate): **`JC-POLLUTION-CLUSTER-C-FIX`** — single-dispatch · 6 site refactor in 1 file (module-level helper functions → function-scoped fixtures + autouse `app.dependency_overrides` snapshot/restore) · 13-row proving slice · ~+25 LOC est. net diff (4 fixtures replace 3 helpers; per-test sig updates).

After Cluster-C fix closes: 6 FTT IDs marked CLOSED in `FAILING_TEST_TRACKER.md`; queue continues with item 7 LLM_MODELS_REFRESH .2/.3 evaluation.

Standing rules unchanged. Time-gate status: no active time-gate. Cluster-G arc CLOSED; Cluster-C arc opens; storage arc PAUSED awaiting Azure credentials per locked user call #2.

End of memo.
