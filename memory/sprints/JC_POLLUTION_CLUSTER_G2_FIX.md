**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.2` (Cluster-G sub-sprint G.2 = M2 class-based iter pair iter39+iter53 / 16 tests / 15 M2 sites · Option A per `P5_7_FIX_SCOPE_CLUSTER_G2_ADVANCE.md §5.1` user direction · minimal-scope dispatch · quarantine preserved · F.6 + G.1 banked mechanical patterns applied · sequential arc G.2 → G.3 → G.4 → G.5 with HARD STOP between sub-sprints)

# Sprint JC_POLLUTION_CLUSTER_G2_FIX — Option A mechanical M2 conversion on the iter pair (iter39 + iter53)

**Status**: SHIPPED (test-file-only patches landed) · proving slice **15/15 GREEN** in ~52s total · minimal-scope dispatch honoured · NO discipline slips this sprint · HARD STOP at slice close per dispatch · no chaining to G.3
**Date**: 2026-06-30
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_G2_ADVANCE.md` (immediate predecessor — READ-ONLY advance scan that reclassified G.2 MEDIUM → LOW under quarantine + surfaced Option A as recommended path); `sprints/JC_POLLUTION_CLUSTER_G1_FIX.md` (G.1 M1=0 FINAL state); `sprints/CLUSTER_F_RETROSPECTIVE.md §5` (banked patterns); `sprints/JC_POLLUTION_CLUSTER_F6_FIX.md` (F.6 M2 mechanical pattern); `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (closure-schedule lock origin)

---

## §0 — Outcome at a glance

| File | Class-method tests | Sync (unchanged) | Async-converted | M2 sites cleared | Post-fix runtime |
|---|---:|---:|---:|---:|---|
| `tests/test_iter39_briefings_objective_check.py` | 7 | 3 (no M2 sites: `test_list_briefings_has_read_fields`, `test_mark_read_scroll_idempotent`, `test_mark_read_404_on_unknown`) | 4 (with `@pytest.mark.asyncio` + `async def`) | 6 | 7 SKIPPED in 0.12s (quarantine preserved) |
| `tests/test_iter53_deep_tier_minutes.py` | 9 | 2 (no M2 sites: `test_quota_single_surface`, `test_minutes_list_returns_narrative`) | 7 (with `@pytest.mark.asyncio` + `async def`) | 9 | 9 SKIPPED in 0.06s (quarantine preserved) |
| **Totals** | **16** | **5 stay sync** | **11 async-converted** | **15 sites cleared** | **16 SKIPPED — quarantine intact** |

**Net**: G.2 closes 15 of 26 remaining M2 polluter sites (-57% reduction). `M2_CEILING` ratchets 26 → 11 (FINAL state for G.2 contribution; G.3-G.5 will continue the trajectory toward 1 final A+D-preserved entry). Tests STAY SKIPPED at runtime per Patch-8 quarantine — the conversion is purely structural for the AST invariant; runtime risk = ZERO.

**Pattern uniformity validated at 8 sub-sprints**: F.2 + F.1 + F.4 + F.5 + F.3 + F.6 + G.1 + G.2 = 8 sub-sprints all using the same mechanical M1+M2 conversion family. G.2 extends with two NEW shapes (class-based test methods + inner coroutines defined inside method bodies) — both mechanically safe per advance-scan §4 analysis.

---

## §1 — Patches applied (test-file-only, minimal scope)

### §1.1 — `tests/test_iter39_briefings_objective_check.py`

4 test methods decorated `@pytest.mark.asyncio` + `def` → `async def`:
- `TestBriefings.test_clear_then_mark_read_manual` (1 M2 site)
- `TestObjectiveCheck.test_objective_check_lifecycle_seeded` (2 M2 sites)
- `TestObjectiveCheck.test_objective_check_skip_dismisses` (2 M2 sites)
- `TestObjectiveCheck.test_objective_check_invalid_answer` (1 M2 site)

6 `asyncio.run(coro())` → `await coro()` conversions:
- Line 75 (in `test_clear_then_mark_read_manual`): `asyncio.run(_clear())` → `await _clear()`
- Line 174 (in `test_objective_check_lifecycle_seeded`): `old_iso = asyncio.run(_backdate())` → `old_iso = await _backdate()`
- Line 210 (in `test_objective_check_lifecycle_seeded`): `asyncio.run(_cleanup())` → `await _cleanup()`
- Line 227 (in `test_objective_check_skip_dismisses`): `asyncio.run(_backdate())` → `await _backdate()`
- Line 249 (in `test_objective_check_skip_dismisses`): `asyncio.run(_cleanup())` → `await _cleanup()`
- Line 266 (in `test_objective_check_invalid_answer`, inside `finally:` block): `asyncio.run(_cleanup())` → `await _cleanup()`

**PRESERVED** (per minimal-scope discipline + dispatch RULE-A quarantine):
- `pytestmark = pytest.mark.skip(reason='Patch 8 quarantined...')` line 8 (Row 15 byte-level verifies)
- All inner coroutine definitions (`_clear`, `_backdate`, `_cleanup`) — defined inside test method bodies, unchanged
- 3 sync test methods unchanged (`test_list_briefings_has_read_fields`, `test_mark_read_scroll_idempotent`, `test_mark_read_404_on_unknown`)
- `import asyncio` line 10 (now orphaned — RULE-2 forbids the cosmetic cleanup)
- Redundant `import pytest` lines 7+11 (RULE-2 forbids cosmetic cleanup)
- All fixtures (`session`, `account_id`), helper functions, module constants

### §1.2 — `tests/test_iter53_deep_tier_minutes.py`

7 test methods decorated `@pytest.mark.asyncio` + `def` → `async def`:
- `TestLlmQuota.test_quota_all_surfaces` (1 M2 site)
- `TestDeepBrief.test_brief_non_deep_does_not_decrement` (1 M2 site)
- `TestDeepBrief.test_brief_deep_decrements_and_uses_opus` (1 M2 site)
- `TestDeepBrief.test_brief_deep_quota_exhausted_falls_back` (2 M2 sites)
- `TestMinutesToCycle.test_seed_then_idempotent` (1 M2 site)
- `TestMinutesToCycle.test_400_when_no_actions` (2 M2 sites)
- `TestMinutesNarrative.test_narrative_generates_persists` (1 M2 site)

9 `asyncio.run(coro())` → `await coro()` conversions:
- Line 86 (in `test_quota_all_surfaces`): `asyncio.run(_reset_quota(...))` → `await _reset_quota(...)`
- Line 113 (in `test_brief_non_deep_does_not_decrement`): `asyncio.run(_reset_quota(...))` → `await _reset_quota(...)`
- Line 128 (in `test_brief_deep_decrements_and_uses_opus`): `asyncio.run(_reset_quota(...))` → `await _reset_quota(...)`
- Line 149 (in `test_brief_deep_quota_exhausted_falls_back`): `asyncio.run(_set_quota(..., 10))` → `await _set_quota(..., 10)`
- Line 166 (in `test_brief_deep_quota_exhausted_falls_back`): `asyncio.run(_reset_quota(...))` → `await _reset_quota(...)`
- Line 175 (in `test_seed_then_idempotent`): `asyncio.run(_cleanup_test_questions(...))` → `await _cleanup_test_questions(...)`
- Line 220 (in `test_400_when_no_actions`): `tmp = asyncio.run(_run())` → `tmp = await _run()` (single return capture; inner `_run` is method-scope-local coroutine, NOT the M1 module-level helper — no naming collision)
- Line 227 (in `test_400_when_no_actions`, inside `finally:` block): `asyncio.run(_clean(tmp))` → `await _clean(tmp)`
- Line 235 (in `test_narrative_generates_persists`): `asyncio.run(_reset_quota(...))` → `await _reset_quota(...)`

**PRESERVED** (per minimal-scope discipline + dispatch RULE-A quarantine + dispatch RULE-3 fallback URL):
- `pytestmark = pytest.mark.skip(reason='Patch 8 quarantined...')` line 14 (Row 15 byte-level verifies)
- Inner coroutine definitions (`_run`, `_clean`) inside `test_400_when_no_actions` — unchanged
- 2 sync test methods unchanged (`test_quota_single_surface`, `test_minutes_list_returns_narrative`)
- `import asyncio` line 16 (now orphaned — RULE-2 forbids the cosmetic cleanup)
- Redundant `import pytest` lines 13+18 (RULE-2 forbids cosmetic cleanup)
- iter53 fallback URL `BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://akki-executive.preview.emergentagent.com").rstrip("/")` line 21 (RULE-3 forbids the change)
- `session.account_id = ...` monkeypatch line 41
- All module-level helpers (`_db`, `_today_utc`, `_set_quota`, `_reset_quota`, `_cleanup_test_questions`) — already `async def`, unchanged
- All fixtures, constants, classes

### §1.3 — Closure-schedule lock edits (F.5-slip lesson applied)

Per F.5 mid-flight YAML-edit slip lesson, applied a SINGLE BATCHED `mcp_search_replace` removing all 15 G.2 M2 entries at once. Post-edit `yaml.safe_load` verify confirmed exact state BEFORE running the slice:
- M1 count: 0 (UNCHANGED from G.1 close — FINAL state)
- M2 count: **11** (down from 26; matches new `M2_CEILING`)
- Zero iter39 entries remaining (all 6 deleted)
- Zero iter53 entries remaining (all 9 deleted)
- 11 remaining M2 entries: iter54 (4) + phase12_2_surfaces (1) + phase_a_synisense (2) + solva_v2_llm_adapter (2) + synisense_surface_validation (1) + A+D-preserved (1)
- 0 stale entries · 0 new ungrandfathered sites

`M2_CEILING` ratcheted from `26` → `11` in `test_no_bespoke_run_helper.py` to reflect new baseline post-G.2. **`M1_CEILING` UNCHANGED at 0** (G.1 closed all M1; G.2 had no M1 sites; FINAL state stays).

**Closure-schedule lock state post-G.2**:
- M1_CEILING = 0 (FINAL — unchanged from G.1)
- M2_CEILING = 11 (down from 26)
- Trajectory: M1 13 → 11 (F.4) → 8 (F.5) → 5 (F.3) → 0 (G.1) ✓ FINAL · M2 28 → 26 (F.6) → **11 (G.2)** ↓ continues (G.3-G.5 remaining)

### §1.4 — F.3-ADVANCE-slip lesson applied (memo-before-DEV_PIPELINE order)

Per F.3-ADVANCE-scan discipline + G.1's re-banked order-strict rule, the DEV_PIPELINE.md §9 row was added BEFORE authoring this memo. Verified row addition pre-memo. Discipline standing rule honoured (no recovery needed this sprint).

### §1.5 — G.1 slice-poll-cadence-mismatch lesson applied

Per G.1's re-banked rule "poll cadence MUST match observed latency", the G.2 proving slice ran in foreground in a single tool call (~52s total wall clock). Quarantine-skipped tests complete in ~0.1s per row; defensive pairings ~5-7s per row; total ~52s — well under the 280s foreground timeout, no polling needed. **No slip this sprint**.

### §1.6 — Locked-area re-confirmation (advance scan §3 already verified clean)

| Area | Touched? |
|---|---|
| Shield internals | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| OAuth provider live endpoints | NO |
| Product code | NO |

Cleared. All edits are test-side or invariant-side (the invariant edit is the closure-schedule lock).

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_g2_proving_slice.py`)

```
============================================================================
P5.7-Cluster-G.2 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_G.md §1.2
============================================================================
  Row  1  GREEN  tests/test_iter39_briefings_objective_check.py in isolation post-fix (expect skipped per quarantine)
            7 skipped, 1 warning in 0.12s  [dur=0.5s]
  Row  2  GREEN  tests/test_iter53_deep_tier_minutes.py in isolation post-fix (expect skipped per quarantine)
            9 skipped, 1 warning in 0.06s  [dur=0.4s]
  Row  3  GREEN  ALL G.2 files combined post-fix (expect 16 skipped)
            16 skipped, 1 warning in 0.13s  [dur=0.5s]
  Row  4  GREEN  G.2 + autosave (B.2 polluter pair, post-fix)
            3 passed, 16 skipped, 21 warnings in 5.03s  [dur=6.9s]
  Row  5  GREEN  G.2 + phase4_2 (A+D defensive)
            8 passed, 16 skipped, 21 warnings in 4.89s  [dur=6.3s]
  Row  6  GREEN  G.2 + p5_10 (Cluster-E defensive)
            5 passed, 16 skipped, 21 warnings in 4.21s  [dur=6.2s]
  Row  7  GREEN  G.2 + synisense_security (F.6 defensive)
            3 passed, 16 skipped, 21 warnings in 5.10s  [dur=7.0s]
  Row  8  GREEN  G.2 + invariant suite (M1=0 FINAL + M2=11 cross-validation)
            3 passed, 16 skipped, 21 warnings in 5.90s  [dur=7.2s]
  Row  9  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 4's full stdout
  Row 10  GREEN  AST source-assertion: zero asyncio.run(...) in test_* method bodies
            iter39 + iter53 clean of asyncio.run-in-test patterns (M2 closure validated)
  Rows 11-13  GREEN  bespoke-run invariant (catcher + drift + count-ceiling M1=0/M2=11)
            3 passed, 21 warnings in 5.96s  [dur=7.2s]
  Row 14  GREEN  inventory slice sibling re-run (M1=0/0, M2=11/11, zero drift)
            RESULT  3/3 GREEN  [dur=2.0s]
  Row 15  GREEN  quarantine preservation: pytestmark.skip line still at iter39:8 + iter53:14
            iter39:8 + iter53:14 carry pytestmark.skip — Patch 8 quarantine intact
============================================================================
RESULT  15/15 GREEN
============================================================================
```

**Key signals**:
- **Rows 1-2**: per-file isolation produces SKIPPED outcomes (7 + 9 = 16 tests) — collection succeeds with async methods + class fixtures + quarantine intact
- **Row 3**: combined G.2 = 16 SKIPPED — both files coexist cleanly
- **Rows 4-7**: defensive pairings show G.2's 16 skipped + companion file's real tests passing (autosave 3 + phase4_2 8 + p5_10 5 + synisense 3) — no cross-file pollution
- **Row 8**: G.2 + bespoke-run invariant suite — 3 invariant tests PASS + 16 G.2 skipped, cross-validates M1=0 FINAL + M2=11 ceiling in single invocation
- **Row 9**: zero `Future attached to a different loop` occurrences across all defensive runs (Row 4 stdout scanned)
- **Row 10**: AST source-assertion verifies both files have zero `asyncio.run(...)` calls inside test method bodies — the structural M2 closure is real
- **Rows 11-13**: bespoke-run invariant catcher + drift + count-ceiling all PASS in 5.96s with M1_CEILING=0 + M2_CEILING=11
- **Row 14**: inventory slice sibling 3/3 GREEN confirms M1=0/0 ceiling, M2=11/11 ceiling, zero drift across full per-sub-sprint roll-up
- **Row 15 (G.2-specific)**: byte-level verification that `pytestmark = pytest.mark.skip` line still exists at iter39 line 8 + iter53 line 14 — quarantine preservation invariant for Option A

**Runtime**: ~52s total slice runtime (vs G.1's ~80 min). The dramatic speed difference is the quarantine: G.2 tests never execute their bodies; G.1 tests ran 37 HTTP+DB-intensive tests across ~10 minutes of cumulative test time. Confirms Option A's runtime risk = ZERO.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Cluster's own proving slice | yes (15/15) | **15/15 GREEN** |
| Invariant suite `tests/invariants/*` (bespoke-run subset) | yes | **3 passed** (catcher + drift + count-ceiling with M1_CEILING=0, M2_CEILING=11) |
| Quarantine preservation | yes | **GREEN** | Row 15 byte-level check; iter39:8 + iter53:14 carry pytestmark.skip |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via Row 5 G.2 + phase4_2 8/8 PASS (phase4_2 includes dual_mount_smoke) — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` in lockstep |
| JC-TM email path smoke | yes | **N/A** | No SendGrid send code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Shield contract preservation (F.6 defensive) | yes | **GREEN** via Row 7 (G.2 + synisense_security 3/3 PASS — Shield contract intact) |
| Inventory slice sibling re-run | yes | **3/3 GREEN** · M1=0/0 ceiling, M2=11/11 ceiling, zero drift |
| Cross-cluster regression (G.1 M1=0 FINAL + autosave + A+D + Cluster-E defensive) | yes | **GREEN** across Rows 4-8 (all defensive pairings pass companion files) |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_iter39_briefings_objective_check.py` | MOD | 4 test methods decorated `@pytest.mark.asyncio + async def` + 6 `asyncio.run(coro())` → `await coro()` conversions (~+4 LOC for decorators + 0 LOC delta on conversions) |
| `tests/test_iter53_deep_tier_minutes.py` | MOD | 7 test methods decorated `@pytest.mark.asyncio + async def` + 9 `asyncio.run(coro())` → `await coro()` conversions (~+7 LOC for decorators + 0 LOC delta on conversions) |
| `tests/invariants/bespoke_run_helper_grandfathered.yml` | MOD | 15 G.2 `m2_entries:` rows DELETED in SINGLE BATCHED edit (F.5-slip lesson applied); M2 list shrinks from 26 to 11 entries |
| `tests/invariants/test_no_bespoke_run_helper.py` | MOD | `M2_CEILING` 26 → 11 (`M1_CEILING` UNCHANGED at 0 — FINAL state preserved) |
| `backend/scripts/jc_pollution_cluster_g2_proving_slice.py` | NEW | 15-row proving slice with quarantine-aware skipped-as-GREEN logic + Row 15 quarantine-preservation byte-level check (~245 LOC) |
| `memory/sprints/JC_POLLUTION_CLUSTER_G2_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added BEFORE memo authored (F.3-ADVANCE-slip lesson applied) |
| `memory/PRD.md` | UPDATED | Head-entry blockquote summarising G.2 close + M2 trajectory advance |

**Files NOT touched** (per minimal-scope discipline):
- iter53 fallback URL (RULE-3 preservation)
- `pytestmark.skip` lines (RULE-A quarantine preservation)
- `import asyncio` (RULE-2 no cosmetic cleanup)
- Redundant `import pytest` (RULE-2)
- Any product code, any other test file, any other invariant file, any fixture file, Shield internals, Shield API

---

## §5 — Discipline notes

- **Minimal-scope dispatch (RULE-1) honoured**: diff = M2 conversions equal to dispatch title. Net LOC delta ~+11 (decorators) with zero LOC adjacent-tidying.
- **Minimal-scope dispatch (RULE-2) honoured**: NO cosmetic cleanups. PRESERVED 2× `import asyncio` (orphaned but RULE-2 forbids the cleanup) + 4× redundant `import pytest`.
- **Minimal-scope dispatch (RULE-3) honoured**: iter53 fallback URL PRESERVED as-is. If addressed later, separate dispatch.
- **G.3 forward-look (RULE-4) honoured**: this sprint did NOT chain into G.3 advance scan. Awaiting separate G.3 dispatch with hard-guardrail (if iter54 NOT same Patch-8 quarantine class, escalate to full advance scan).
- **Quarantine preservation (RULE-A) honoured**: `pytestmark.skip` UNTOUCHED on iter39:8 + iter53:14. Row 15 byte-level verifies.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 15/15 GREEN** in ~52s — HARD STOP at slice close.
- **No production code changes** — entirely test-side + invariant lock + docs.
- **Pattern uniformity confirmed at 8 sub-sprints**: F.2 + F.1 + F.4 + F.5 + F.3 + F.6 + G.1 + G.2 = 8 sub-sprints; same mechanical conversion family applied to 21 files (14 Cluster-F + 5 Cluster-G.1 + 2 Cluster-G.2). G.2 extends with class-based async test methods + inner-coroutine-in-method-body patterns — both mechanically validated via Row 1-3 isolation/combined + Row 10 AST + Rows 11-13 invariant.
- **All 3 banked discipline-slip lessons applied successfully (zero slips this sprint)**:
  - F.5 YAML-edit slip → SINGLE batched edit + `yaml.safe_load` verify-before-slice ✓
  - F.3-ADVANCE memo-order slip → §9 row BEFORE memo authoring (no recovery needed) ✓
  - G.1 slice-poll-cadence-mismatch → slice ran in single foreground call (~52s, well under foreground timeout) ✓

---

## §6 — Trajectory advance summary

| Checkpoint | M1_CEILING | M2_CEILING | Reason |
|---|---:|---:|---|
| G.1 close (predecessor) | 0 | 26 | M1=0 FINAL milestone; M2 unchanged from F.6 close |
| **G.2 close (this sprint)** | **0** | **11** | **G.2 closes 15 sites (iter39=6 + iter53=9) — quarantined files, structural M2 conversion only** |
| G.3 projected | 0 | 7 | -4 sites (iter54; probable Patch-8 quarantine same shape — verification dispatch pending) |
| G.4 projected | 0 | 2 | -5 sites (Shield-adjacency trio; ADVANCE-SCAN + TWO-DISPATCH per F.6 precedent) |
| G.5 projected | 0 | 1 | -1 site (synisense_surface_validation; HYBRID 4-sync-preserved + 1-async-converted) |
| **Final state** | **0** | **1** | A+D-preserved entry remains by design |

**Sub-sprint trajectory contribution**: G.2 makes the largest single-sprint M2 reduction in the entire Cluster (15 sites in one sprint vs F.6's 2 sites in single sprint). The combination of quarantined-batch + Option A mechanical pattern delivers maximum closure-schedule-lock velocity with zero runtime risk.

---

## §7 — User-direction surface (HARD STOP)

Per dispatch directive: **HARD STOP at slice close — no chaining to G.3**.

**G.2 milestone**:
- ✅ 2 of 2 G.2 files converted (16 tests · 11 async-converted + 5 unchanged sync · 15 M2 sites cleared)
- ✅ M2_CEILING ratcheted 26 → 11
- ✅ Proving slice 15/15 GREEN in ~52s
- ✅ Regression-check ladder GREEN (surface ratchets + Shield contract + cross-cluster defensive)
- ✅ Quarantine preservation byte-level verified (Row 15)
- ✅ All 4 dispatch RULEs honoured (minimal scope + no cosmetic cleanup + URL preserved + no G.3 chaining)
- ✅ All 3 banked discipline-slip lessons applied (zero slips)

**Remaining Cluster-G sub-sprints**:
- **G.3** — Compressed verification-only advance scan if iter54 is same Patch-8 quarantine class; else escalate to full advance scan per dispatch RULE-4 (iter54 / 7 tests / 4 M2 sites)
- **G.4** — Shield-adjacency M2 trio (HIGH risk · ADVANCE-SCAN + TWO-DISPATCH decision)
- **G.5** — Shield-adjacency M2 outlier (LOW-MEDIUM · HYBRID conversion)

Recommended next dispatch: **G.3 compressed verification memo** per dispatch RULE-4. Single grep to check iter54 for `pytestmark.skip` resolves the branch.

Awaiting next dispatch from user. Standing rules unchanged.

---

## §8 — Time-gate status at slice close

`Tue Jun 30 17:46:36 UTC 2026` at slice close. No active time-gate. Cluster-G arc ungated; proceeds per user's sequential dispatch direction.
