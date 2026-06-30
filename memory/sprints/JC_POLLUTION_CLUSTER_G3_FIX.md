**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.3` (Cluster-G sub-sprint G.3 = M2 class-based iter54 / 7 tests / 4 M2 sites · Option A per `P5_7_FIX_SCOPE_CLUSTER_G3_VERIFICATION.md §5` user direction · minimal-scope dispatch · quarantine preserved · F.6 + G.1 + G.2 banked mechanical patterns applied · sequential arc G.3 → G.4 → G.5 with HARD STOP between sub-sprints)

# Sprint JC_POLLUTION_CLUSTER_G3_FIX — Option A mechanical M2 conversion on iter54

**Status**: SHIPPED (test-file-only patches landed) · proving slice **15/15 GREEN** in ~58s total · minimal-scope dispatch honoured · NO discipline slips this sprint · HARD STOP at slice close per dispatch · no chaining to G.4
**Date**: 2026-06-30
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_G3_VERIFICATION.md` (immediate predecessor — compressed verification memo confirming iter54 is same Patch-8 quarantine class as iter39/iter53 + recommending Option A); `sprints/JC_POLLUTION_CLUSTER_G2_FIX.md` (G.2 ship; iter pair Option A mechanical pattern banked); `sprints/JC_POLLUTION_CLUSTER_G1_FIX.md` (G.1 M1=0 FINAL state); `sprints/CLUSTER_F_RETROSPECTIVE.md §5` (banked patterns); `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (closure-schedule lock origin)

---

## §0 — Outcome at a glance

| File | Class-method tests | Sync (unchanged) | Async-converted | M2 sites cleared | Post-fix runtime |
|---|---:|---:|---:|---:|---|
| `tests/test_iter54_llm_spend_quota_inbound.py` | 7 (10 with parametrize × 4 on `test_superadmin_window`) | 4 (no M2 sites: `test_non_superadmin_forbidden`, `test_unauthenticated_unauthorised`, `test_superadmin_window` × 4 params, `test_seeded_data_visible_30d`) | 3 (with `@pytest.mark.asyncio` + `async def`) | 4 | 10 SKIPPED in 0.10s (quarantine preserved) |
| **Totals** | **7 base / 10 collected** | **4 stay sync** | **3 async-converted** | **4 sites cleared** | **10 SKIPPED — quarantine intact** |

**Net**: G.3 closes 4 of 11 remaining M2 polluter sites (-36% reduction in single sub-sprint). `M2_CEILING` ratchets 11 → 7 (FINAL state for G.3 contribution; G.4 + G.5 will continue trajectory toward 1 final A+D-preserved entry). Tests STAY SKIPPED at runtime per Patch-8 quarantine — the conversion is purely structural for the AST invariant; runtime risk = ZERO.

**Pattern uniformity validated at 9 sub-sprints**: F.2 + F.1 + F.4 + F.5 + F.3 + F.6 + G.1 + G.2 + G.3 = 9 sub-sprints all using the same mechanical M1+M2 conversion family. G.3 follows G.2's exact shape (class-based async test methods + inner coroutines defined inside method bodies) with the additional sub-shape M2c (tuple-unpack) at L257 mechanically validated.

---

## §1 — Patches applied (test-file-only, minimal scope)

### §1.1 — `tests/test_iter54_llm_spend_quota_inbound.py`

3 test methods decorated `@pytest.mark.asyncio` + `def` → `async def`:
- `TestRaceSafeDeepQuota.test_unique_index_exists` (1 M2 site)
- `TestRaceSafeDeepQuota.test_at_cap_and_under_cap_combined` (1 M2 site)
- `TestInboundVirusRejected.test_eicar_attachment_rejected_and_audited` (2 M2 sites)

4 `asyncio.run(coro())` → `await coro()` conversions:
- Line 127 (in `test_unique_index_exists`): `asyncio.run(_check())` → `await _check()` (M2a bare)
- Line 172 (in `test_at_cap_and_under_cap_combined`): `asyncio.run(_run())` → `await _run()` (M2a bare; inner `_run` is method-scope-local coroutine — NOT the M1 module-level helper; no naming collision)
- Line 260 (in `test_eicar_attachment_rejected_and_audited`): `account, ctx = asyncio.run(_setup())` → `account, ctx = await _setup()` (M2c tuple-unpack)
- Line 301 (in `test_eicar_attachment_rejected_and_audited`): `audit = asyncio.run(_check_audit())` → `audit = await _check_audit()` (M2b single-capture)

**PRESERVED** (per minimal-scope discipline + dispatch RULE-A quarantine):
- `pytestmark = pytest.mark.skip(reason='Patch 8 quarantined...')` line 4 (Row 15 byte-level verifies)
- All inner coroutine definitions (`_check`, `_run`, `_setup`, `_check_audit`) — defined inside test method bodies, unchanged
- 4 sync test methods unchanged (`test_non_superadmin_forbidden`, `test_unauthenticated_unauthorised`, `test_superadmin_window` parametrized × 4 cases, `test_seeded_data_visible_30d`)
- 2 `_disabled_test_*` orphan methods (`_disabled_test_at_cap_no_overage` at L174 + `_disabled_test_under_cap_parallel_no_overcount` at L203) — preserved verbatim per RULE-2 no cosmetic cleanup; underscore-prefix means they are NOT collected as tests by pytest; their `asyncio.run` calls at L201 + L233 are inside underscore-prefixed methods so NOT M2 sites (catcher only flags `test_*` bodies)
- `import asyncio` line 5 (still required by `_disabled_test_*` orphans — RULE-2 forbids the cleanup)
- Redundant `import pytest` at lines 3 + 11 (RULE-2 forbids cosmetic cleanup)
- All fixtures (`admin_token`, `user_token`, `admin_client`, `user_client`), module constants, classes

### §1.2 — Open verification from G.3-VERIFICATION §3.1 RESOLVED

The G.3-VERIFICATION memo §3.1 flagged L199 + L231 raw-grep hits for `asyncio.run(...)` as an open question: are they inside nested helper functions or do they need a conversion cascade?

**Source-read resolution**: L199 + L231 raw-grep hits are inside the `_disabled_test_*` orphan methods (`_disabled_test_at_cap_no_overage` body L174-L201 + `_disabled_test_under_cap_parallel_no_overcount` body L203-L233). Both are underscore-prefixed → NOT collected as tests by pytest → NOT in the catcher's AST scope (catcher only walks `def test_*` FunctionDef nodes). Their `asyncio.run` calls are part of orphan/legacy code paths NEVER executed. AST scan post-fix stays clean at 0 sites — Row 10 confirms.

**Action taken**: NO cascade conversion needed; the 4 AST-scoped sites at L126/L170/L257/L298 (per G.3-VERIFICATION §1) were the complete fix set.

**Lesson re-banked (companion to G.3-VERIFICATION's "AST authoritative > grep")**: underscore-prefixed test method orphans are valid scope-narrowing — the invariant catcher and the fix dispatcher both correctly limit AST walk to `test_*` named functions. Discoveries surfaced from raw grep need to be cross-checked against the catcher's scope rules before triggering cascade work.

### §1.3 — Closure-schedule lock edits (F.5-slip lesson applied)

Per F.5 mid-flight YAML-edit slip lesson, applied a SINGLE BATCHED `mcp_search_replace` removing all 4 G.3 M2 entries at once. Post-edit `yaml.safe_load` verify confirmed exact state BEFORE running the slice:
- M1 count: 0 (UNCHANGED from G.1 close — FINAL state)
- M2 count: **7** (down from 11; matches new `M2_CEILING`)
- Zero iter54 entries remaining (all 4 deleted)
- 7 remaining M2 entries: phase12_2_surfaces (1) + phase4_2_http_transport_smoke A+D-preserved (1) + phase_a_synisense_unification (2) + solva_v2_llm_adapter (2) + synisense_surface_validation (1)
- 0 stale entries · 0 new ungrandfathered sites

`M2_CEILING` ratcheted from `11` → `7` in `test_no_bespoke_run_helper.py` to reflect new baseline post-G.3. **`M1_CEILING` UNCHANGED at 0** (G.1 closed all M1; G.3 had no M1 sites; FINAL state stays).

**Closure-schedule lock state post-G.3**:
- M1_CEILING = 0 (FINAL — unchanged from G.1)
- M2_CEILING = 7 (down from 11)
- Trajectory: M1 13 → 11 (F.4) → 8 (F.5) → 5 (F.3) → 0 (G.1) ✓ FINAL · M2 28 → 26 (F.6) → 11 (G.2) → **7 (G.3)** ↓ continues (G.4 + G.5 remaining)

### §1.4 — F.3-ADVANCE-slip lesson applied (memo-before-DEV_PIPELINE order)

Per F.3-ADVANCE-scan discipline + G.1's re-banked order-strict rule + G.2's re-application, the DEV_PIPELINE.md §9 row was added BEFORE authoring this memo. Verified row addition pre-memo. Discipline standing rule honoured (no recovery needed this sprint).

### §1.5 — G.1 slice-poll-cadence-mismatch lesson applied

Per G.1's re-banked rule "poll cadence MUST match observed latency", the G.3 proving slice ran in foreground in a single tool call (~58s total wall clock). Quarantine-skipped tests complete in ~0.1s per isolation row; defensive pairings ~5-7s per row; total ~58s — well under the 300s foreground timeout, no polling needed. **No slip this sprint**.

### §1.6 — G.3-VERIFICATION AST-authoritative-over-grep lesson applied

Per G.3-VERIFICATION's newly-banked lesson "AST authoritative > raw grep for invariant verification", the G.3 fix dispatch used AST as primary verification (Row 10 AST source-assertion + Rows 11-13 bespoke-run invariant). No grep-based assertions used in the proving slice. The §1.2 resolution of the L199 + L231 question above used source-read of method names (matched the AST catcher's scope rule of `test_*` FunctionDef only) rather than further grep.

### §1.7 — Locked-area re-confirmation (verification scan §2 already verified clean)

| Area | Touched? |
|---|---|
| Shield internals / `pipeline_run` / `shield_*` / synisense | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| OAuth provider live endpoints | NO |
| Product code | NO |

Cleared. All edits are test-side or invariant-side (the invariant edit is the closure-schedule lock).

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_g3_proving_slice.py`)

```
============================================================================
P5.7-Cluster-G.3 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_G.md §1.3
============================================================================
  Row  1  GREEN  tests/test_iter54_llm_spend_quota_inbound.py in isolation post-fix (expect 7 skipped)
            10 skipped, 1 warning in 0.10s  [dur=0.5s]
  Row  2  GREEN  iter54 + autosave (B.2 polluter pair, post-fix)
            3 passed, 10 skipped, 21 warnings in 5.02s  [dur=6.9s]
  Row  3  GREEN  iter54 + phase4_2 (A+D defensive)
            8 passed, 10 skipped, 21 warnings in 4.88s  [dur=6.2s]
  Row  4  GREEN  iter54 + p5_10 (Cluster-E defensive)
            5 passed, 10 skipped, 21 warnings in 4.23s  [dur=6.4s]
  Row  5  GREEN  iter54 + synisense_security (F.6 defensive)
            3 passed, 10 skipped, 21 warnings in 5.08s  [dur=7.1s]
  Row  6  GREEN  iter54 + iter39 + iter53 (G.2 sibling regression — 23 skipped expected)
            26 skipped, 1 warning in 0.16s  [dur=0.5s]
  Row  7  GREEN  iter54 + invariant suite (M2=7 cross-validation)
            3 passed, 10 skipped, 21 warnings in 5.86s  [dur=7.2s]
  Row  8  GREEN  iter54 + autosave + phase4_2 broad sweep
            11 passed, 10 skipped, 21 warnings in 5.37s  [dur=7.5s]
  Row  9  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 2's full stdout
  Row 10  GREEN  AST source-assertion: zero asyncio.run(...) in iter54 test_* method bodies
            iter54 clean of asyncio.run-in-test patterns (M2 closure validated)
  Rows 11-13  GREEN  bespoke-run invariant (catcher + drift + count-ceiling M1=0/M2=7)
            3 passed, 21 warnings in 5.97s  [dur=7.3s]
  Row 14  GREEN  inventory slice sibling re-run (M1=0/0, M2=7/7, zero drift)
            RESULT  3/3 GREEN  [dur=2.0s]
  Row 15  GREEN  quarantine preservation: pytestmark.skip line still at iter54:4
            iter54:4 carries pytestmark.skip — Patch 8 quarantine intact
============================================================================
RESULT  15/15 GREEN
============================================================================
```

**Key signals**:
- **Row 1**: iter54 isolation produces 10 SKIPPED (7 base tests; `test_superadmin_window` parametrized × 4 cases bumps collected total to 10) — collection succeeds with async methods + class fixtures + quarantine intact
- **Rows 2-5**: defensive pairings show iter54's 10 skipped + companion file's real tests passing (autosave 3 + phase4_2 8 + p5_10 5 + synisense 3) — no cross-file pollution
- **Row 6 (NEW G.3-specific)**: iter54 + iter39 + iter53 = 26 SKIPPED (G.2 sibling regression — confirms all 3 quarantined Cluster-G files coexist cleanly post-conversion; if any had import or fixture collision, this row would fail)
- **Row 7**: iter54 + bespoke-run invariant suite — 3 invariant tests PASS + 10 iter54 skipped, cross-validates M1=0 FINAL + M2=7 ceiling in single invocation
- **Row 8**: broad sweep iter54 + autosave + phase4_2 — 11 PASS + 10 skipped — confirms G.3 conversion + B.2 polluter pair + A+D defensive coexist
- **Row 9**: zero `Future attached to a different loop` occurrences across all defensive runs (Row 2 stdout scanned)
- **Row 10**: AST source-assertion verifies iter54 has zero `asyncio.run(...)` calls inside `test_*` method bodies — the structural M2 closure is real (orphan `_disabled_test_*` methods are out of scope by design)
- **Rows 11-13**: bespoke-run invariant catcher + drift + count-ceiling all PASS in 5.97s with M1_CEILING=0 + M2_CEILING=7
- **Row 14**: inventory slice sibling 3/3 GREEN confirms M1=0/0 ceiling, M2=7/7 ceiling, zero drift across full per-sub-sprint roll-up
- **Row 15**: byte-level verification that `pytestmark = pytest.mark.skip` line still exists at iter54 line 4 — quarantine preservation invariant for Option A

**Runtime**: ~58s total slice runtime (similar to G.2's ~52s; both quarantine-batches complete fast because tests never execute their bodies). Confirms Option A's runtime risk = ZERO at the 3rd quarantined-file application.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Cluster's own proving slice | yes (15/15) | **15/15 GREEN** |
| Invariant suite `tests/invariants/*` (bespoke-run subset) | yes | **3 passed** (catcher + drift + count-ceiling with M1_CEILING=0, M2_CEILING=7) |
| Quarantine preservation | yes | **GREEN** | Row 15 byte-level check; iter54:4 carries pytestmark.skip |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via Row 3 iter54 + phase4_2 8/8 PASS (phase4_2 includes dual_mount_smoke) — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` in lockstep |
| JC-TM email path smoke | yes | **N/A** | No SendGrid send code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Shield contract preservation (F.6 defensive) | yes | **GREEN** via Row 5 (iter54 + synisense_security 3/3 PASS — Shield contract intact) |
| G.2 sibling regression (iter39 + iter53 still quarantine-clean) | yes | **GREEN** via Row 6 (26 skipped in 0.16s — 7 iter39 + 9 iter53 + 10 iter54) |
| Inventory slice sibling re-run | yes | **3/3 GREEN** · M1=0/0 ceiling, M2=7/7 ceiling, zero drift |
| Cross-cluster regression (G.1 M1=0 FINAL + G.2 + autosave + A+D + Cluster-E defensive) | yes | **GREEN** across Rows 2-8 (all defensive pairings pass companion files) |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_iter54_llm_spend_quota_inbound.py` | MOD | 3 test methods decorated `@pytest.mark.asyncio + async def` + 4 `asyncio.run(coro())` → `await coro()` conversions (~+3 LOC for decorators + 0 LOC delta on conversions) |
| `tests/invariants/bespoke_run_helper_grandfathered.yml` | MOD | 4 G.3 `m2_entries:` rows DELETED in SINGLE BATCHED edit (F.5-slip lesson applied); M2 list shrinks from 11 to 7 entries |
| `tests/invariants/test_no_bespoke_run_helper.py` | MOD | `M2_CEILING` 11 → 7 (`M1_CEILING` UNCHANGED at 0 — FINAL state preserved) |
| `backend/scripts/jc_pollution_cluster_g3_proving_slice.py` | NEW | 15-row proving slice with quarantine-aware skipped-as-GREEN logic + Row 6 G.2-sibling-regression check + Row 15 quarantine-preservation byte-level check (~223 LOC) |
| `memory/sprints/JC_POLLUTION_CLUSTER_G3_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added BEFORE memo authored (F.3-ADVANCE-slip lesson applied) |
| `memory/PRD.md` | UPDATED | Head-entry blockquote summarising G.3 close + M2 trajectory advance |

**Files NOT touched** (per minimal-scope discipline):
- `pytestmark.skip` line at iter54:4 (RULE-A quarantine preservation)
- `import asyncio` (RULE-2 no cosmetic cleanup; still used by `_disabled_test_*` orphans)
- Redundant `import pytest` (RULE-2)
- `_disabled_test_*` orphan methods (RULE-2; out of catcher scope)
- Any product code, any other test file, any other invariant file, any fixture file, Shield internals, Shield API

---

## §5 — Discipline notes

- **Minimal-scope dispatch (RULE-1) honoured**: diff = M2 conversions equal to dispatch title. Net LOC delta ~+3 (decorators) with zero LOC adjacent-tidying.
- **Minimal-scope dispatch (RULE-2) honoured**: NO cosmetic cleanups. PRESERVED `import asyncio` (still used by `_disabled_test_*` orphans) + redundant `import pytest`.
- **Minimal-scope dispatch (RULE-3) honoured**: no fallback URL change applicable — iter54 uses `os.environ["REACT_APP_BACKEND_URL"]` without fallback string.
- **No-chain (RULE-4) honoured**: this sprint did NOT chain into G.4 advance scan. Awaiting separate G.4 dispatch with hard-guardrail (Shield-adjacency trio is HIGH-risk; advance-scan-default-on per Cluster-F retrospective §5.1; F.6 TWO-DISPATCH precedent applies; single-vs-sequential G.4a/b/c decision is an ESCALATION TRIGGER to user per orchestrator standing note).
- **Quarantine preservation (RULE-A) honoured**: `pytestmark.skip` UNTOUCHED on iter54:4. Row 15 byte-level verifies.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 15/15 GREEN** in ~58s — HARD STOP at slice close.
- **No production code changes** — entirely test-side + invariant lock + docs.
- **Pattern uniformity confirmed at 9 sub-sprints**: F.2 + F.1 + F.4 + F.5 + F.3 + F.6 + G.1 + G.2 + G.3 = 22 files converted across the same mechanical conversion family. G.3 reinforces G.2's class-based async-test-method pattern with the additional M2c (tuple-unpack) sub-shape mechanically validated at L257.
- **All 4 banked discipline-slip lessons applied successfully (zero slips this sprint)**:
  - F.5 YAML-edit slip → SINGLE batched edit + `yaml.safe_load` verify-before-slice ✓
  - F.3-ADVANCE memo-order slip → §9 row BEFORE memo authoring (no recovery needed) ✓
  - G.1 slice-poll-cadence-mismatch → slice ran in single foreground call (~58s, well under foreground timeout) ✓
  - G.3-VERIFICATION AST-authoritative-over-grep → fix-sprint used AST as primary verification (Row 10 + Rows 11-13); §1.2 open-question resolved via source-read of method-name scope rule rather than further grep ✓

---

## §6 — Trajectory advance summary

| Checkpoint | M1_CEILING | M2_CEILING | Reason |
|---|---:|---:|---|
| G.2 close (predecessor) | 0 | 11 | G.2 -15 sites (iter39=6 + iter53=9); M2 trajectory continuation |
| **G.3 close (this sprint)** | **0** | **7** | **G.3 closes 4 sites (iter54); quarantined file, structural M2 conversion only** |
| G.4 projected | 0 | 2 | -5 sites (Shield-adjacency trio: phase12_2 + phase_a × 2 + solva_v2 × 2; ADVANCE-SCAN + TWO-DISPATCH per F.6 precedent; single-vs-sequential G.4a/b/c decision = ESCALATION TRIGGER) |
| G.5 projected | 0 | 1 | -1 site (synisense_surface_validation; HYBRID 4-sync-preserved + 1-async-converted) |
| **Final state** | **0** | **1** | A+D-preserved entry (phase4_2:254) remains by design |

**Sub-sprint trajectory contribution**: G.3 makes a smaller M2 reduction than G.2 (4 sites vs G.2's 15 sites) because iter54 is a single-file batch vs G.2's iter-pair batch — but per-site cost is identical due to Option A's mechanical pattern. Combined G.1 + G.2 + G.3 close: M1 5→0 + M2 26→7 = 24 sites cleared across 3 sub-sprints.

---

## §7 — User-direction surface (HARD STOP)

Per dispatch directive: **HARD STOP at slice close — no chaining to G.4**.

**G.3 milestone**:
- ✅ 1 of 1 G.3 file converted (7 tests / 10 collected with parametrize · 3 async-converted + 4 unchanged sync · 4 M2 sites cleared)
- ✅ M2_CEILING ratcheted 11 → 7
- ✅ Proving slice 15/15 GREEN in ~58s
- ✅ Regression-check ladder GREEN (surface ratchets + Shield contract + G.2 siblings + cross-cluster defensive)
- ✅ Quarantine preservation byte-level verified (Row 15)
- ✅ All 4 dispatch RULEs honoured (minimal scope + no cosmetic cleanup + no fallback URL change applicable + no G.4 chaining)
- ✅ All 4 banked discipline-slip lessons applied (zero slips, including the new G.3-VERIFICATION AST-over-grep lesson)
- ✅ §1.2 open question from G.3-VERIFICATION resolved (L199 + L231 inside `_disabled_test_*` orphans; no cascade needed)

**Remaining Cluster-G sub-sprints**:
- **G.4** — Shield-adjacency M2 trio (phase12_2 + phase_a × 2 + solva_v2 × 2 = 5 sites across 3 files; HIGH risk; advance-scan-default-on; F.6 TWO-DISPATCH precedent; **single-vs-sequential G.4a/b/c decision = ESCALATION TRIGGER to user** per orchestrator standing note)
- **G.5** — Shield-adjacency M2 outlier (synisense_surface_validation; LOW-MEDIUM risk; advance-scan-on; HYBRID 4-sync-preserved + 1-async-converted)

Recommended next dispatch: **G.4 advance scan (READ-ONLY)** per Cluster-F retrospective §5.1 default-on rule. Source-read the 3 Shield-adjacency files for: (a) Shield contract surface area; (b) `asyncio.run` semantics audit (signal handlers / async generators / loop weakrefs / loop-scoped state); (c) sub-sprint shape decision (single G.4 vs sequential G.4a/b/c — ESCALATION TRIGGER); (d) F.6 Shield-contract regression discipline-pay applied.

Awaiting next dispatch from user. Standing rules unchanged.

---

## §8 — Time-gate status at slice close

`Tue Jun 30 18:31:30 UTC 2026` at slice close. No active time-gate. Cluster-G arc ungated; proceeds per user's sequential dispatch direction.
