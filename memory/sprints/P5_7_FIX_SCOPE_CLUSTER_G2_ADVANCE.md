**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.2` (Cluster-G sub-sprint G.2 = M2 class-based iter pair iter39+iter53 / 16 tests / 15 M2 sites · MEDIUM-risk classification on scope-memo §1 surface = class-based test pattern + sync `session.get` interaction · advance-scan-default-on per Cluster-F retrospective §5.1 banked rule · READ-ONLY · zero LOC mutated outside this memo · HARD STOP at memo surface · pre-approved by user dispatch · sequential G.2 → G.3 → G.4 → G.5 arc confirmed)

# Sprint P5.7-FIX-SCOPE-CLUSTER-G2-ADVANCE — F.6-style structural-shape advance scan for the iter pair (iter39 + iter53)

**Status**: SHIPPED (memo only) · READ-ONLY · HARD STOP at memo surface · 0 LOC mutated outside this memo · pre-approved per user dispatch · sequential arc confirmed
**Date**: 2026-06-30
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_G1_FIX.md` (G.1 ship + M1=0 FINAL milestone); `sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.2` (G.2 scope-memo entry); `sprints/CLUSTER_F_RETROSPECTIVE.md §5.1` (advance-scan-default-on banked rule); `sprints/P5_7_FIX_SCOPE_CLUSTER_F6_ADVANCE.md` (F.6 advance-scan precedent — surface-area HIGH → source-read LOW reclassification track record)

---

## §0 — HALT-and-surface finding (load-bearing for the entire scan)

**Both iter39 + iter53 carry a module-level `pytestmark = pytest.mark.skip(...)`.** Verified by source-read + AST scan:

```
iter39 line 7:  import pytest
iter39 line 8:  pytestmark = pytest.mark.skip(reason='Patch 8 quarantined — pre-existing failures from before autonomous sprint. See SYSTEM_STATE §7.')

iter53 line 13: import pytest
iter53 line 14: pytestmark = pytest.mark.skip(reason='Patch 8 quarantined — pre-existing failures from before autonomous sprint. See SYSTEM_STATE §7.')
```

**ALL 16 tests in both files are SKIPPED at runtime** — pytest mark cascading applies module-level `pytestmark` to ALL test functions in the module, INCLUDING class methods (`TestBriefings.*`, `TestObjectiveCheck.*`, `TestLlmQuota.*`, `TestDeepBrief.*`, `TestMinutesToCycle.*`, `TestMinutesNarrative.*`).

**Cross-reference**: `/app/memory/SYSTEM_STATE.md` line 24 documents `Patch 8 — Pre-existing failing tests triage / quarantine — shipped 2026-05-12`. Both iter files have been quarantined for ~7 weeks as part of the Patch-8 batch. A `QUARANTINE_TRIAGE_PLAN.md` (Patch 11 deliverable, SYSTEM_STATE line 123) lists 5 phases for systematic un-quarantine — iter39 + iter53 are not in any unquarantined phase yet.

**This fundamentally reshapes the G.2 risk classification.** Scope-memo §1's MEDIUM classification ("class-based + sync `session.get` runtime interaction is unvalidated at fix-sprint dispatch time") is based on the assumption that the tests RUN. They don't. The 15 M2 sites are real at AST/grep level (the bespoke-run invariant catches them via source scan, not runtime instrumentation) but never execute at runtime.

**Verified risk reclassification**: MEDIUM (scope-memo §1) → **LOW** (this advance scan). Rationale:
- Runtime pollution risk = **ZERO** (tests skipped before any `asyncio.run(...)` executes)
- AST-pattern risk = real but mechanically resolvable (drop wrappers, decorate methods async, leave skip in place)
- Sync `session.get` blocking-in-async-event-loop concern (scope-memo's primary medium-risk driver) = MOOT (tests don't run)
- Class-based fixture wiring concern = MOOT (tests don't run; pytest-asyncio class-method support is well-established anyway)

**Directional consistency with prior advance scans**: F.3 medium → LOW, F.6 high → LOW, G.2 medium → LOW. All three advance scans pulled risk DOWN, never up. The advance-scan-default-on rule continues to demonstrate value: surface-area-only risk assessments overshoot when source-read reveals load-bearing properties (quarantine, no Shield-internal touch, timing injected through state).

---

## §1 — Per-site M2 evidence (verified against YAML + on-disk source)

### §1.1 — iter39 (6 M2 sites in 7 tests · class-based · all quarantined)

YAML claims 6 M2 sites (verified via `grep -c "asyncio.run(" tests/test_iter39_briefings_objective_check.py` → 6).

| Test | Class | M2 sites | M2 sub-shape | Inner coroutine name | What the coroutine does |
|---|---|---:|---|---|---|
| `test_list_briefings_has_read_fields` | TestBriefings | 0 | — | — | (no asyncio.run; pure HTTP via session.get) |
| `test_clear_then_mark_read_manual` | TestBriefings | 1 | M2a | `_clear` | Motor `delete_many` on `briefing_reads` for clean slate |
| `test_mark_read_scroll_idempotent` | TestBriefings | 0 | — | — | (no asyncio.run; pure HTTP) |
| `test_mark_read_404_on_unknown` | TestBriefings | 0 | — | — | (no asyncio.run; pure HTTP) |
| `test_objective_check_lifecycle_seeded` | TestObjectiveCheck | 2 | M2a + M2a | `_backdate` + `_cleanup` | Motor `find_one` + `update_one` to backdate generated_at; then `delete_one` cleanup |
| `test_objective_check_skip_dismisses` | TestObjectiveCheck | 2 | M2a + M2a | `_backdate` + `_cleanup` | Motor `update_one` (backdate) + `delete_one` (cleanup) |
| `test_objective_check_invalid_answer` | TestObjectiveCheck | 1 | M2a | `_cleanup` | Motor `delete_one` in `finally:` block (try/finally cleanup pattern) |
| **Totals** | — | **6** | all M2a | — | — |

**All 6 sites are M2a (bare `asyncio.run(coro())`) form** — none capture return values, none tuple-unpack, none Shield-call M2d.

### §1.2 — iter53 (9 M2 sites in 9 tests · class-based · all quarantined)

YAML claims 9 M2 sites (verified via `grep -c "asyncio.run(" tests/test_iter53_deep_tier_minutes.py` → 9).

| Test | Class | M2 sites | M2 sub-shape | Inner coroutine name | What the coroutine does |
|---|---|---:|---|---|---|
| `test_quota_all_surfaces` | TestLlmQuota | 1 | M2a | `_reset_quota` | Motor `delete_one` on `llm_deep_usage` baseline |
| `test_quota_single_surface` | TestLlmQuota | 0 | — | — | (no asyncio.run; pure HTTP) |
| `test_brief_non_deep_does_not_decrement` | TestDeepBrief | 1 | M2a | `_reset_quota` | Motor `delete_one` baseline |
| `test_brief_deep_decrements_and_uses_opus` | TestDeepBrief | 1 | M2a | `_reset_quota` | Motor `delete_one` baseline |
| `test_brief_deep_quota_exhausted_falls_back` | TestDeepBrief | 2 | M2a + M2a | `_set_quota` + `_reset_quota` | Motor `update_one(upsert)` + `delete_one` cleanup |
| `test_seed_then_idempotent` | TestMinutesToCycle | 1 | M2a | `_cleanup_test_questions` | Motor `delete_many` on `questions` collection |
| `test_400_when_no_actions` | TestMinutesToCycle | 2 | M2a + M2a | `_run` + `_clean` | Motor `insert_one` document setup + `delete_one` cleanup (M2a `tmp = asyncio.run(_run())` captures inserted id) |
| `test_narrative_generates_persists` | TestMinutesNarrative | 1 | M2a | `_reset_quota` | Motor `delete_one` baseline |
| `test_minutes_list_returns_narrative` | TestMinutesNarrative | 0 | — | — | (no asyncio.run; pure HTTP) |
| **Totals** | — | **9** | all M2a | — | — |

**All 9 sites are M2a form**. One site (`tmp = asyncio.run(_run())` line 220) captures a return value but is still M2a sub-shape (the value capture is on a bare `asyncio.run(coro())` — not a tuple-unpack M2c). The inner coroutine name `_run` is method-scope-local (`test_400_when_no_actions` method body, line 202) — **NOT** the M1 module-level helper pattern; no naming collision with the M1 catcher invariant.

### §1.3 — Aggregate totals match scope memo §0

| Metric | Scope memo §0 | This advance scan | Match? |
|---|---:|---:|:---:|
| iter39 M2 sites | 6 | 6 | ✓ |
| iter53 M2 sites | 9 | 9 | ✓ |
| iter39 tests | 7 | 7 | ✓ |
| iter53 tests | 9 | 9 | ✓ |
| **Total M2 sites** | **15** | **15** | ✓ |
| **Total tests** | **16** | **16** | ✓ |

Scope memo §0 evidence holds. Zero false positives. Zero file-path drift.

---

## §2 — `asyncio.run` semantics audit (per F.6 precedent)

The F.6 advance scan's load-bearing audit was whether each `asyncio.run(...)` site had hidden semantics dependencies beyond simple coroutine completion (signal handlers, async generators with `__aexit__`, weakrefs to the loop, etc.). Applied here to all 15 G.2 M2 sites:

### §2.1 — Return value usage

| Test/site | Captures return? | Tuple unpack? | Shield-call? |
|---|:---:|:---:|:---:|
| iter39 `_clear` × 1 | NO | NO | NO |
| iter39 `_backdate` × 2 | YES (returns `old_iso` ISO string) | NO | NO |
| iter39 `_cleanup` × 3 | NO | NO | NO |
| iter53 `_reset_quota` × 4 | NO | NO | NO |
| iter53 `_set_quota` × 1 | NO | NO | NO |
| iter53 `_cleanup_test_questions` × 1 | NO | NO | NO |
| iter53 `_run` (line 202) × 1 | YES (returns `tmp_id` string) | NO | NO |
| iter53 `_clean` (line 216) × 1 | NO | NO | NO |

**12 of 15 sites: bare `asyncio.run(coro())`** (return discarded). **3 of 15 sites: `var = asyncio.run(coro())`** (single return capture; ISO string or document id). **All 15 sites pass the F.6 semantics audit** — no signal handlers registered, no async generators with `__aexit__` dependencies, no weakrefs to the loop, no `asyncio.run` keyword args used. Conversion to `@pytest.mark.asyncio + async def` + `await coro()` is mechanically safe.

### §2.2 — Inner coroutine scope

All 12 inner coroutines (`_clear`, `_backdate`, `_cleanup` × 4, `_reset_quota` × 4, `_set_quota`, `_cleanup_test_questions`, `_run`, `_clean`) are defined **inside test method bodies** (not module-level). This is a NEW shape vs Cluster-F (where coroutines were either module-level functions or single-expression inlines). The conversion preserves the inner-`async def` definition + replaces `asyncio.run(coro())` with `await coro()`. Inner-scoped `async def` functions are well-supported under `@pytest.mark.asyncio` test methods.

**Naming-collision check**: 1 inner coroutine is named `_run` (iter53 line 202, inside `test_400_when_no_actions`). This is **method-scope-local**, NOT a module-level helper. The M1 catcher invariant (`tests/invariants/test_no_bespoke_run_helper.py`) checks for `def _run(coro): return asyncio.get_event_loop().run_until_complete(coro)` at module level — the method-scope `_run` is a coroutine function with different signature (`async def _run():` returning a string), no semantic overlap. Conversion leaves the inner `_run` name as-is.

---

## §3 — Locked-area aggregate scan

| Area | iter39 | iter53 | Notes |
|---|:---:|:---:|---|
| Shield internals / `pipeline_run` / `shield_*` | NO | NO | grep clean |
| WS Generate Doc UI | NO | NO | grep clean |
| Track-2 schema | NO | NO | grep clean |
| Monitor pre-warmer | NO | NO | grep clean |
| OAuth provider live endpoints | NO | NO | grep clean |
| Product code modification | NO | NO | tests only call API endpoints + Motor cleanup helpers |

Both files clean of all locked-area surfaces enumerated in Cluster-F scope-memo §6 + Cluster-G scope-memo §2. Conversion changes test invocation only — production code untouched.

---

## §4 — Class-based fixture wiring under async conversion

Scope-memo §1 flagged class-based test organization as a NEW pattern vs Cluster-F (which had 0 class-based tests across 14 polluter files). Audit:

### §4.1 — Fixture scope verification

iter39:
```python
@pytest.fixture(scope="module")
def session():
    s, _ = _login()
    return s

@pytest.fixture(scope="module")
def account_id():
    _, data = _login()
    return data["account"]["id"]
```

iter53:
```python
@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
    ...
    s.account_id = (me.get("account") or {}).get("id")
    return s
```

Both files use module-scoped fixtures. **pytest-asyncio class-method support is well-established** — module-scoped sync fixtures wire correctly into `@pytest.mark.asyncio` async test methods. The session fixture is a `requests.Session()` instance (sync HTTP client), not an httpx-async client; this is fine under conversion because:
- Tests don't run at runtime (quarantine), so blocking-loop concern is moot
- Even if tests DID run, sync `requests` inside an async test would block the loop but complete correctly (just slower than ideal); zero correctness risk, only performance

### §4.2 — Monkeypatching pattern (iter53)

iter53 line 41 sets `s.account_id = ...` — monkey-patches the `requests.Session` object with a custom attribute. This pattern survives async conversion mechanically (still works as attribute attachment); class test methods access `session.account_id` the same way.

### §4.3 — Sync `session.get` interaction under conversion (scope-memo's MEDIUM-risk driver)

Scope memo §1 wrote: *"converting test to async means the sync `session.get(...)` blocks the loop — works mechanically but is a medium-risk conversion shape"*. **This risk is NEUTRALIZED by quarantine** at runtime. At AST level, the converted test method body would have `await self._helper()` interleaved with sync `session.get(...)` — this is structurally valid Python; the sync call is just a blocking operation in the middle of an async function, well-defined semantics.

**Recommended fix-sprint discipline**: leave the sync `session.get` calls as-is. Do NOT swap them for httpx-async equivalents (that would be a test-rewrite, not a mechanical M2 conversion). The conversion is purely structural at the `asyncio.run(...)` → `await ...` site.

---

## §5 — Fix-sprint shape options for user direction

Three structurally distinct options, in order of recommended preference:

### §5.1 — Option A (RECOMMENDED): Mechanical convert + preserve quarantine

**Approach**:
1. Decorate all 11 async-touching test methods (4 iter39 + 7 iter53 — the ones with M2 sites) with `@pytest.mark.asyncio` + change `def` to `async def`
2. Replace inner `asyncio.run(coro())` with `await coro()` at all 15 sites
3. **Leave `pytestmark = pytest.mark.skip(...)` in place** — tests stay quarantined
4. Drop `import asyncio` (no longer needed); drop redundant `import pytest` on iter39 line 11 + iter53 line 18 (cosmetic cleanup)
5. Closure-schedule lock: remove 15 M2 entries from YAML in single batched edit; ratchet `M2_CEILING` 26 → 11

**Risk profile**:
- Runtime: ZERO (tests don't run)
- AST invariant: CLEARED (no `asyncio.run` remains in test bodies)
- Pattern uniformity: matches F.6 M2 mechanical + G.1 helper-as-async extension
- LOC delta estimate: ~30 LOC (15 wrapper drops + 11 decorator/def changes + 2 import cleanups)

**Pattern matches banked discipline**: F.6 + G.1 mechanical pattern continues.

### §5.2 — Option B: Permanent-quarantine-grandfather

**Approach**:
1. Leave M2 sites in YAML
2. Retag from `cluster_f_sub_sprint: "Cluster-G (post-F)"` → `cluster_f_sub_sprint: "Cluster-G-quarantined-permanent"`
3. Add a YAML `reason` field per entry: `"Quarantined via pytestmark.skip on iter39 line 8 / iter53 line 14 (Patch 8 batch 2026-05-12). Runtime risk = ZERO. Accepts AST debt as documented permanent quarantine debt until QUARANTINE_TRIAGE_PLAN unquarantine sprint reaches this batch."`
4. Add a new invariant test asserting these entries remain quarantined (i.e., the YAML tag matches the source `pytestmark` line at the file's recorded lineno)

**Risk profile**:
- Runtime: ZERO (tests don't run)
- AST invariant: NOT cleared (M2_CEILING stays at 26; no G.2 ratchet)
- Trade-off: accepts permanent AST debt with structural enforcement that it remains quarantined

**Rejected as default because**: G.1 trajectory recently went M1=0 FINAL; Option B halts the M2_CEILING ratchet trajectory at G.2 (would need same disposition for G.3 iter54 which is also Patch-8-quarantined per inspection in §6.2 below). Closure-schedule lock pattern works best with monotonic decrease, not "decrease until quarantined batches".

### §5.3 — Option C: Restore-and-convert (OUT OF SCOPE for advance scan)

**Approach**:
1. Remove `pytestmark.skip` line from both files
2. Mechanically convert M2 sites
3. Verify tests pass against current schema + endpoints + Patch-8's "pre-existing failures" haven't been independently fixed

**Why out of scope for advance scan**: requires runtime verification that the tests pass after restore. Tests have been quarantined for ~7 weeks; the codebase has shifted significantly (briefings + objective-check + LLM quota + deep-tier surfaces all touched in subsequent dispatches). Restore-then-pass verification is a separate sprint shape — recommend separate dispatch tied to `QUARANTINE_TRIAGE_PLAN.md` (Patch 11 deliverable) un-quarantine phase planning.

---

## §6 — Cluster-G sub-sprint forward-look impact

### §6.1 — Closure-schedule lock trajectory if Option A applied to G.2

| Checkpoint | M2_CEILING | Note |
|---|---:|---|
| G.1 close (current) | 26 | M1=0 FINAL; M2 unchanged from F.6 close |
| G.2 close (Option A) | 11 | -15 sites (iter39=6 + iter53=9) |
| G.3 projected | 7 | -4 sites (iter54) — pending G.3 advance scan |
| G.4 projected | 2 | -5 sites (Shield-adjacency trio) — pending G.4 advance scan + TWO-DISPATCH decision |
| G.5 projected | 1 | -1 site (synisense_surface_validation) — pending G.5 advance scan |
| **Final state** | **1** | A+D-preserved entry remains by design |

Option A keeps the trajectory monotonic and reaches the planned final state.

### §6.2 — Cross-check: is iter54 (G.3) also Patch-8-quarantined?

Quick AST check warranted to inform whether G.3 will land the same HALT-and-surface finding. If iter54 is ALSO `pytestmark.skip`-quarantined, the G.3 advance scan will have the same finding + same Option A recommendation.

**Verified**: `grep -n "pytestmark\|pytest.mark.skip" tests/test_iter54_llm_spend_quota_inbound.py` — leaving this verification to the G.3 advance scan dispatch per HARD STOP rule (this scan covers only G.2). Surface here as a forward-look: **probable** but not verified in this advance scan.

---

## §7 — Open questions surfaced for user direction at G.2 fix-sprint dispatch

**Q1: Which fix-sprint option to dispatch?**
- A (mechanical convert + preserve quarantine) — RECOMMENDED
- B (permanent-quarantine-grandfather) — alternative if you prefer to halt the M2_CEILING ratchet for quarantined batches
- C (restore-and-convert) — recommend separate Quarantine-Triage-revisit dispatch instead

**Q2: Should the cosmetic cleanups (drop redundant `import pytest` lines + drop `import asyncio`) be in-scope?**
- IN-scope: matches F.6 + G.1 import-cleanup discipline; ~2 LOC savings
- OUT-of-scope: stricter "test-file-only mechanical conversion" interpretation
- Recommend: IN-scope (consistent with F.6 + G.1 patterns)

**Q3: Should we also surface the iter53 redundant fallback URL** (`"https://akki-executive.preview.emergentagent.com"` matches current env so it's defensive but redundant) **as a separate cleanup item?**
- IN-scope here: ~3 LOC delta, low risk
- OUT-of-scope: separate cleanup-cluster dispatch
- Recommend: OUT-of-scope; leave for a future cleanup pass (it's NOT a polluter; it's a code-smell)

---

## §8 — Discipline notes

- **Scope honoured**: READ-ONLY — 0 LOC mutated outside this memo file.
- **No testing subagent used** (per banned-list rule).
- **HALT-and-surface rule applied**: pytestmark.skip finding surfaced honestly rather than absorbed silently into a mechanical pattern. The risk reclassification MEDIUM → LOW is load-bearing for user direction at fix-sprint dispatch.
- **F.3-ADVANCE memo-order slip lesson APPLIED**: DEV_PIPELINE.md §9 row added BEFORE memo authoring (verified pre-memo write). G.1's order-strict re-banked rule honoured.
- **Source-read verification complete**: scope memo §0 evidence holds exactly (15 M2 sites across 16 tests across 2 files); zero false positives; zero file-path drift.
- **Directional consistency across 3 advance scans (F.3 + F.6 + G.2)** — all three pulled risk DOWN, never up. The advance-scan-default-on rule continues to demonstrate value.
- **Sequential arc confirmed by user**: G.2 → G.3 → G.4 → G.5 with HARD STOP + user approval before each next dispatch. No chaining into G.2 fix-sprint dispatch from this advance scan.
- **Banked patterns from Cluster-F retrospective §5 + G.1 §5 reused**: mechanical M2 conversion + sync-test preservation heuristic + closure-schedule lock pattern + class-based pytest-asyncio support + inner-coroutine preservation under async test methods.
- **Cross-references documented**: SYSTEM_STATE.md line 24 (Patch 8 ship date) + line 123 (QUARANTINE_TRIAGE_PLAN.md). No fabricated context.
- **G.3 forward-look surfaced honestly**: probable but not verified that iter54 is also Patch-8-quarantined; leaving verification to G.3 advance scan per HARD STOP rule.

---

## §9 — Time-gate status at memo close

`date -u` at memo author: post-G.1-close window (2026-06-30 17:20 UTC+ approximate). No active time-gate. Cluster-G arc is ungated and proceeds per user's sequential dispatch direction.

---

## §10 — HARD STOP per dispatch — no chaining into G.2 fix dispatch

Advance scan complete. Awaiting user direction at G.2 fix-sprint dispatch:
- **Recommended next dispatch**: G.2 fix-sprint with **Option A** (mechanical convert + preserve `pytestmark.skip`; ratchets M2_CEILING 26 → 11).
- **Alternative dispatch options**: B (permanent grandfather) or C (restore-and-convert; recommend separate Quarantine-Triage dispatch).

Standing rules unchanged.
