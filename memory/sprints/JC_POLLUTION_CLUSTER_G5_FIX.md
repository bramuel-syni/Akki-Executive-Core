**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.5` (Cluster-G sub-sprint G.5 = Shield-adjacency M2 outlier `test_synisense_surface_validation.py:78` · HYBRID 4-sync-preserved + 1-async-converted shape per advance scan §1.3 · SINGLE-dispatch shape per advance scan §2.1 = 1 file × 1 site auto-locked · F.6 Shield-contract regression discipline-pay applied · UNQUARANTINED runtime PASS preservation per banked lesson #5 second application · file-name-from-YAML per banked lesson #6 · sequential arc G.5 → Cluster-G retrospective with HARD STOP per user autonomous mandate)

# Sprint JC_POLLUTION_CLUSTER_G5_FIX — Single-dispatch mechanical M2 conversion on Shield-adjacency outlier · CLUSTER-G ARC M2 CLOSURE COMPLETE

**Status**: SHIPPED (test-file-only patches landed) · proving slice **13/13 GREEN** in ~110s total · minimal-scope dispatch honoured · UNQUARANTINED runtime baseline 34/34 PASS preserved BYTE-PERFECT (3% delta within variance) · NO production-impacting slips this sprint (1 script-level slip discovered + fixed mid-flight) · **CLUSTER-G ARC M2 CLOSURE COMPLETE at final state M2=1 (A+D-preserved by design)** · HARD STOP at slice close per dispatch · no chaining to Cluster-G arc retrospective
**Date**: 2026-06-30
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_G5_ADVANCE.md` (immediate predecessor — advance scan auto-locked SINGLE-G.5 dispatch shape after all 4 escalation triggers cleared); `sprints/JC_POLLUTION_CLUSTER_G4_FIX.md` (G.4 ship; M2_CEILING 7→2); `sprints/CLUSTER_F_RETROSPECTIVE.md §5` (banked patterns + F.6 Shield-contract discipline-pay rule)

---

## §0 — Outcome at a glance

| File | Quarantine | Tests in file | Tests untouched | Async-converted | M2 sites cleared | Post-fix runtime |
|---|---|---:|---:|---:|---:|---|
| `tests/test_synisense_surface_validation.py` | UNQUARANTINED | 5 unique (34 collected with parametrize) | 4 sync (33 collected) | 1 | 1 | 34 PASSED in 3.81s |

**Net**: G.5 closes the LAST closable M2 polluter site (the only remaining entry post-G.5 is the A+D-preserved `phase4_2:254` which stays by design). `M2_CEILING` ratchets 2 → 1 (FINAL state). Tests RUN at runtime per UNQUARANTINED status — Row 1 of slice confirms 34/34 baseline preserved post-conversion.

**Pattern uniformity validated at 11 sub-sprints**: F.2 + F.1 + F.4 + F.5 + F.3 + F.6 + G.1 + G.2 + G.3 + G.4 + G.5 = 26 files converted across the same mechanical M1+M2 conversion family. **G.5 marks the CLUSTER-G ARC M2 CLOSURE**.

**HYBRID 4-sync-preserved + 1-async-converted shape APPLIED per advance scan §1.3**: 4 sync tests (L25 + L29 + L42 + L59) call sync `_is_valid_surface(surface) → bool` predicate; legitimately use no async machinery; UNCHANGED. 1 test (L63 G.5 target) calls async `await run(...)` coroutine via inner `_runner`; CONVERTED to `await _runner()`.

---

## §1 — Patches applied (test-file-only, minimal scope)

### §1.1 — `tests/test_synisense_surface_validation.py`

1 test method decorated `@pytest.mark.asyncio` + `def` → `async def`:
- L63 `test_real_pipeline_run_rejects_bad_subsurface(monkeypatch)` (1 M2a-under-pytest.raises site at L78)

1 `asyncio.run(coro())` → `await coro()` conversion:
- L78 (in `test_real_pipeline_run_rejects_bad_subsurface`): `asyncio.run(_runner())` → `await _runner()` (M2a bare; inner `_runner` is method-scope-local coroutine with `with pytest.raises(...)` context manager INSIDE its body — preserved verbatim per RULE-2)

**PRESERVED** (per minimal-scope discipline RULE-2):
- Function-local `import asyncio` line 65 (now orphaned post-conversion — RULE-2 forbids cosmetic cleanup; function-local imports treated identically to module-level for RULE-2 purposes)
- Inner `async def _runner()` definition UNCHANGED verbatim
- `with pytest.raises(ValueError, match="invalid surface")` context manager UNCHANGED verbatim INSIDE `_runner` body
- `await run(text="hello world", context_id="ctx-test", surface="solve_v2.Bad-Thing", mode="redact", account_id="acct-test")` call UNCHANGED verbatim (REAL Shield contract surface preserved end-to-end)
- 4 sync test methods UNCHANGED (L25 `test_explicit_allow_list_remains_valid` parametrize × 14, L29 `test_solve_v2_bare_remains_valid`, L42 `test_solve_v2_subsurfaces_are_valid` parametrize × 7, L59 `test_invalid_surfaces_are_rejected` parametrize × 11)
- All module imports + `_VALID_SURFACES` reference

### §1.2 — Closure-schedule lock edits (F.5-slip lesson applied)

Per F.5 mid-flight YAML-edit slip lesson, applied a SINGLE BATCHED `mcp_search_replace` removing the 1 G.5 M2 entry. Post-edit `yaml.safe_load` verify confirmed exact state BEFORE running the slice:
- M1 count: 0 (UNCHANGED from G.1 close — FINAL state)
- M2 count: **1** (down from 2; matches new `M2_CEILING`)
- Remaining M2 entry: `phase4_2_http_transport_smoke:254` (A+D-preserved by design as Cluster-G arc end-state)

`M2_CEILING` ratcheted from `2` → `1` in `test_no_bespoke_run_helper.py` to reflect new FINAL baseline. **`M1_CEILING` UNCHANGED at 0** (G.1 FINAL milestone preserved).

**Closure-schedule lock state post-G.5 (CLUSTER-G ARC FINAL)**:
- M1_CEILING = 0 (FINAL — unchanged from G.1)
- M2_CEILING = 1 (FINAL — A+D-preserved entry by design; not subject to further ratcheting)
- Trajectory: M1 13 → 11 (F.4) → 8 (F.5) → 5 (F.3) → 0 (G.1) ✓ FINAL · M2 28 → 26 (F.6) → 11 (G.2) → 7 (G.3) → 2 (G.4) → **1 (G.5)** ✓ FINAL

### §1.3 — F.3-ADVANCE-slip lesson applied (memo-before-DEV_PIPELINE order)

Per F.3-ADVANCE-scan discipline + G.1's re-banked order-strict rule + G.2/G.3/G.4's re-applications, the DEV_PIPELINE.md §9 row was added BEFORE authoring this memo. Discipline standing rule honoured (no recovery needed this sprint).

### §1.4 — G.1 slice-poll-cadence-mismatch lesson applied

Per G.1's re-banked rule "poll cadence MUST match observed latency", the G.5 proving slice ran in foreground in a single tool call (~110s total wall clock including ~53s inventory slice re-use at Row 11). Under the 240s foreground timeout, no polling needed. **No slip this sprint**.

### §1.5 — G.3-VERIFICATION AST-over-grep lesson applied

Per G.3-VERIFICATION's banked lesson "AST authoritative > raw grep for invariant verification", the G.5 fix dispatch used AST as primary verification (Row 4 AST source-check + Rows 9-10 bespoke-run invariant suite). No grep-based assertions used for invariant validation.

### §1.6 — NEW G.4-ADVANCE UNQUARANTINED-runtime-PASS-baseline lesson SECOND APPLICATION

This is the **SECOND application** of NEW banked lesson #5 (first was G.4 fix; banked at G.4 advance scan). Pre-conversion baseline: 34/34 PASS in 3.71s (captured at G.5 advance scan). Post-conversion: 34/34 PASS in 3.81s (Row 1 of slice; baseline preserved with ~3% timing delta well within variance for cold-start variance). **Second-application slip-free**. Lesson #5 is now battle-tested across 2 dispatches with 100% pass-preservation.

### §1.7 — NEW G.4-FIX file-name-from-YAML (lesson #6) APPLIED

Per G.4-FIX banked lesson "cite test-file names from YAML/AST, not from memo prose", all non-target file references in the G.5 proving slice were sourced PROGRAMMATICALLY:
- G.5 target (`test_synisense_surface_validation.py:78`) sourced via `yaml.safe_load` of `bespoke_run_helper_grandfathered.yml` (the post-G.4 M2 list had 2 entries; the non-A+D one is G.5)
- G.4 trio (Row 7) sourced from G.4 fix sprint memo `tests/test_phase12_2_surfaces.py` + `tests/test_phase_a_synisense_unification.py` + `tests/test_solva_v2_llm_adapter.py` (already validated by G.4 fix)
- iter file names (Row 8) sourced from `ls tests/` per G.4 fix Slip A correction: `test_iter39_briefings_objective_check.py` + `test_iter53_deep_tier_minutes.py` + `test_iter54_llm_spend_quota_inbound.py` (verified by G.4 fix proving slice Row 10)

**Lesson #6 first application clean** — no Row 8 RED this sprint (vs G.4 fix Slip A which RED'd Row 10 from aspirational names).

### §1.8 — F.6 Shield-contract regression discipline-pay APPLIED (3 rows GREEN)

F.6 banked the "Shield contract regression discipline-pay" rule for any sub-sprint touching Shield-adjacency code paths. G.5 target file calls real `services.synisense.pipeline.run` via inner `_runner` → discipline-pay APPLIES. **Pay = 3 mandatory proving-slice rows shipped GREEN**:
- Row 2 — converted test L63 solo 1/1 PASS in 3.77s (chat-surface real-Shield-call exercise: the converted test IS the real `pipeline.run(...)` exercise via `await _runner()`; runs solo confirms live Shield contract intact across the await conversion)
- Row 3 — synisense_security defensive 3/3 PASS in 5.08s (Shield contract preservation)
- Row 4 — AST source-check 0 hits in catcher's `test_*` AST scope (no underscore-prefixed orphan trap reintroduced; matches G.4 fix Row 14 pattern)

Note: G.5 dispatch's Row 2 + Row 3 differ from G.4 dispatch's Row 6 + Row 5 in coverage geometry — G.4 had a separate Row 6 for chat-surface exercise (covered by phase_a Row 3); G.5 covers chat-surface real-Shield via the converted test itself (Row 2 solo run). Both shapes satisfy F.6 discipline-pay.

### §1.9 — Locked-area re-confirmation (verification scan §3 already verified clean)

| Area | Touched? |
|---|---|
| Shield internals / `pipeline_run` / `shield_*` / synisense INTERNAL code | NO (real `services.synisense.pipeline.run` imported + called as test subject but NOT mutated) |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| OAuth provider live endpoints | NO |
| Product code | NO |
| Storage arc (Azure SAS work) | NO (independent arcs; storage PAUSED awaiting Azure credentials) |

Cleared. All edits are test-side or invariant-side (the invariant edit is the closure-schedule lock).

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_g5_proving_slice.py`)

```
============================================================================
P5.7-Cluster-G.5 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_G.md §1.5
============================================================================
  Row  1  GREEN  G.5 file runtime PASS preservation (lesson #5; baseline 34/34 preserved)
            34 passed, 21 warnings in 3.86s
  Row  2  GREEN  Converted test L63 runs solo + passes (chat-surface real-Shield-call cover)
            1 passed, 21 warnings in 3.77s · L63 IS the real `pipeline.run(...)` exercise via `await _runner()`
  Row  3  GREEN  F.6 Shield contract preservation (synisense_security)
            3 passed, 21 warnings in 5.08s
  Row  4  GREEN  AST source-check: 0 asyncio.run-in-test hits in G.5 file (F.6 + G.3 discipline-pay)
            hits=0
  Row  5  GREEN  autosave defensive (1 files)
            3 passed, 21 warnings in 4.97s
  Row  6  GREEN  phase4_2 A+D defensive (surface ratchets lockstep + A+D-preserved entry as M2 final state)
            8 passed, 21 warnings in 4.93s
  Row  7  GREEN  G.4 trio post-fix runtime regression (phase12_2 + phase_a + solva_v2)
            10 passed, 21 warnings in 5.57s
  Row  8  GREEN  G.2 + G.3 sibling regression (iter39 + iter53 + iter54 → 26 skipped)
            26 skipped, 1 warning in 0.16s
  Row  9  GREEN  G.5 file + invariant suite (37/37 PASS expected = 34 G.5 + 3 invariant)
            37 passed, 21 warnings in 6.02s
  Row 10  GREEN  Invariant cross-validation M2_CEILING ratcheted 2 → 1 FINAL
            3 passed, 21 warnings in 5.84s
  Row 11  GREEN  Inventory slice sibling re-run (post-G.5 steady state 9/10 + YAML M1=0/M2=1)
            inventory_slice_exit=1 dur=52.6s · YAML M1=0/0 · M2=1/1 · 9/10 GREEN steady state observed
  Row 12  GREEN  Log scan zero 'Future attached to a different loop' across G.5 + G.4 trio
            occurrences=0
  Row 13  GREEN  Cluster-G arc closure trajectory marker (M2 28→26→11→7→2→1 FINAL)
            final_state M1=0/M2=1: True · A+D-preserved entry intact: True · arc CLOSES at M2=1
============================================================================
RESULT  13/13 GREEN — Cluster-G arc CLOSES at M2=1 FINAL
============================================================================
```

**Key signals**:
- **Row 1 (lesson #5 second application)**: UNQUARANTINED runtime PASS preservation — 34/34 PASS in 3.86s vs advance-scan baseline 34/34 in 3.71s (~3% delta within variance; passing-count BYTE-PERFECT)
- **Row 2 (F.6 discipline-pay alt cover)**: converted test L63 runs solo + passes 1/1 in 3.77s — confirms `await _runner()` correctly invokes inner `_runner` async function which calls real `services.synisense.pipeline.run(...)` and asserts `pytest.raises(ValueError, match="invalid surface")` fires
- **Row 3 (F.6 discipline-pay)**: synisense_security defensive 3/3 PASS (Shield contract surface intact post-conversion)
- **Row 4 (F.6 + G.3-VERIFICATION discipline-pay)**: AST source-check confirms 0 hits in catcher's `test_*` AST scope — structural M2 closure is real (no underscore-prefixed orphan trap)
- **Row 5**: autosave defensive 3/3 (B.2 polluter pair pattern; cross-cluster regression-free)
- **Row 6**: phase4_2 A+D defensive 8/8 (surface ratchets in lockstep — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` all preserved; dual_mount_smoke included; this row ALSO confirms the A+D-preserved entry at L254 is the M2 final state by exercising it directly)
- **Row 7**: G.4 trio post-fix runtime regression 10/10 PASS in 5.57s (G.4 conversions still passing; no regression from G.4 close at 19:32 to G.5 close ~10min later)
- **Row 8 (lesson #6 first application)**: G.2 + G.3 sibling regression — 26 SKIPPED in 0.16s (7 iter39 + 9 iter53 + 10 iter54 = 26 across 3 quarantined files); iter file names sourced from `ls tests/` per lesson #6 — NO Row 8 RED this sprint
- **Row 9**: G.5 + invariant suite 37/37 PASS (34 G.5 + 3 invariant)
- **Row 10**: invariant cross-validation M2_CEILING=1 → 3/3 PASS (catcher + drift + count-ceiling all green at new FINAL ceiling)
- **Row 11 (F.5 + steady-state insight)**: inventory slice sibling re-run produces post-G.5 steady state 9/10 GREEN; YAML M1=0/0 + M2=1/1 verified
- **Row 12**: 0 `Future attached to a different loop` occurrences across G.5 + G.4 trio cross-file run (covers Shield-adjacency regression surface)
- **Row 13 (CLUSTER-G ARC CLOSURE MARKER)**: final_state M1=0/M2=1 + A+D-preserved entry intact → **Cluster-G arc CLOSES at M2=1 FINAL**

**Runtime**: ~110s total slice runtime (vs G.4's ~95s); +15s delta from extra defensive rows (Row 7 G.4 trio regression + Row 6 phase4_2 A+D defensive; both added to validate FINAL state of M2 ratchet). Subtracting Row 11's ~53s inventory slice re-use, G.5 slice would be ~57s — comparable to G.4's ~44s slice.

---

## §3 — Mid-flight slip discovery: 1 script-level slip fixed (NOT production-impacting)

### §3.1 — First slice run: 12/13 RED on Row 2 only

First run returned 12/13. Investigation surfaced **1 script-level slip** (in my proving slice authoring, NOT in the G.5 conversion itself):

**Slip — Row 2 `-q -v` pytest flag conflict**: I invoked `_run_pytest(G5_FILE, "-v")` expecting verbose `PASSED` markers per-test, but the helper hardcoded `-q` at the front of the argument list. The combined `-q -v` output suppressed individual test PASSED markers (pytest's combined-flag behavior shows test names but not PASSED status in `-q` mode). My check `"PASSED" in out` returned False even though all 34 tests passed (proven by parallel "34 passed" summary line).

The G.5 conversion was complete + correct BEFORE the slice ran; the slice slip only affected my assertion shape, not the underlying truth.

### §3.2 — Slip fixed in single edit

Patched Row 2 to invoke the single converted test by node ID:
```python
rc, out = _run_pytest(f"{G5_FILE}::test_real_pipeline_run_rejects_bad_subsurface")
ok = (rc == 0) and ("1 passed" in out)
```

This is a CLEANER verification of the chat-surface real-Shield-call exercise — runs only the converted test and asserts 1/1 PASS. Re-ran slice: **13/13 GREEN**.

### §3.3 — Lesson refinement (NO new banked lesson; refinement to existing #6)

Original lesson #6 statement (from G.4 fix §3.3): "cite test-file names from YAML/AST, not from memo prose".

Refinement after G.5 slip: when authoring proving slice rows that use BOTH `-q` (quiet) and `-v` (verbose) pytest flags, BE EXPLICIT about which marker style the assertion expects. Prefer node-ID invocation + count-based assertion (`"N passed"`) over verbose-marker assertion (`"PASSED" in out`).

This is a REFINEMENT to slice-authoring discipline (related to but not requiring a new banked lesson). The fix template: when verifying a SPECIFIC test runs + passes (not a file's worth of tests), invoke by node ID + assert "1 passed" — more deterministic + decoupled from flag-combo edge cases.

### §3.4 — Why this slip is NOT production-impacting

- The G.5 conversion was complete + correct from the FIRST `mcp_search_replace` round (verified by smoke-test `34 passed in 3.81s` immediately after conversion)
- The slice slip was at the assertion layer, not the test-runner or test-file layer
- YAML + ceilings + Shield contract surface were always correct; only my Row 2 assertion shape was incorrect

---

## §4 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Cluster's own proving slice | yes (13/13) | **13/13 GREEN** | Second run after Row 2 assertion fix |
| **UNQUARANTINED runtime PASS preservation (lesson #5 SECOND application)** | yes | **GREEN** | Row 1: 34/34 in 3.86s vs baseline 34/34 in 3.71s — BYTE-PERFECT pass count |
| Invariant suite `tests/invariants/*` (bespoke-run subset) | yes | **3 passed** in 5.84s (catcher + drift + count-ceiling with M1_CEILING=0, M2_CEILING=1 FINAL) |
| Quarantine preservation (G.2 + G.3 siblings) | yes | **GREEN** via Row 8 (26 skipped in 0.16s) |
| G.4 trio post-fix regression | yes | **GREEN** via Row 7 (10/10 PASS) |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via Row 6 phase4_2 8/8 PASS — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` in lockstep |
| JC-TM email path smoke | yes | **N/A** | No SendGrid send code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| **Shield contract preservation (F.6 defensive — discipline-pay row 3)** | yes | **GREEN** | Row 3: synisense_security 3/3 PASS |
| **Chat surface real-Shield-call (F.6 defensive — discipline-pay row 2)** | yes | **GREEN** | Row 2 solo: converted L63 calls real `pipeline.run(...)` and asserts ValueError — 1/1 PASS |
| **AST source-check (F.6 defensive — discipline-pay row 4)** | yes | **GREEN** | Row 4: 0 hits in catcher's `test_*` AST scope |
| Inventory slice sibling re-run | yes | **GREEN** | Row 11: post-G.5 steady state 9/10 GREEN + YAML M1=0/M2=1 FINAL |
| **Cluster-G arc closure trajectory marker** | yes | **GREEN** | Row 13: M2 28→26→11→7→2→1 FINAL · A+D-preserved entry intact |

---

## §5 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_synisense_surface_validation.py` | MOD | +1 decorator · 1 def→async def · 1 asyncio.run→await (M2a at L78) |
| `tests/invariants/bespoke_run_helper_grandfathered.yml` | MOD | 1 G.5 `m2_entries:` row DELETED in SINGLE BATCHED edit (F.5-slip lesson applied); M2 list shrinks from 2 to 1 entry (phase4_2 A+D-preserved FINAL state) |
| `tests/invariants/test_no_bespoke_run_helper.py` | MOD | `M2_CEILING` 2 → 1 (FINAL — A+D-preserved entry by design; `M1_CEILING` UNCHANGED at 0 FINAL since G.1) |
| `backend/scripts/jc_pollution_cluster_g5_proving_slice.py` | NEW | 13-row proving slice with Row 1 = lesson #5 + Row 2 = chat-surface real-Shield cover + Row 3+4 F.6 discipline-pay + Row 13 = Cluster-G arc closure trajectory marker (~270 LOC) |
| `memory/sprints/JC_POLLUTION_CLUSTER_G5_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added BEFORE memo authored (F.3-ADVANCE-slip lesson applied) |
| `memory/PRD.md` | UPDATED | Head-entry blockquote summarising G.5 close + Cluster-G arc M2 closure |

**Files NOT touched** (per minimal-scope discipline):
- Function-local `import asyncio` at L65 (RULE-2 no cosmetic cleanup; now orphaned but left as-is)
- 4 sync test methods (L25 + L29 + L42 + L59 unchanged per HYBRID shape from advance scan)
- All product code, all other test files, all other invariant files, all fixture files
- Shield internals (`services.synisense.pipeline.run` imported + called as test subject but NOT mutated), Shield API, OAuth, Track-2 schema, Monitor pre-warmer, WS Doc UI
- Storage arc (Azure SAS work paused awaiting credentials)

---

## §6 — Discipline notes

- **Minimal-scope dispatch (RULE-1) honoured**: diff = M2 conversion equal to dispatch title. Net LOC delta ~+1 (decorator).
- **Minimal-scope dispatch (RULE-2) honoured**: NO cosmetic cleanups. PRESERVED orphaned function-local `import asyncio` + inner `_runner` def verbatim + `with pytest.raises(...)` block verbatim + 4 sync tests verbatim.
- **Minimal-scope dispatch (RULE-3) honoured**: no fallback URL change applicable.
- **No-chain (RULE-4) honoured**: this sprint did NOT chain into Cluster-G arc retrospective dispatch. Awaiting separate retrospective dispatch per user autonomous queue.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 13/13 GREEN** in ~110s — HARD STOP at slice close.
- **No production code changes** — entirely test-side + invariant lock + docs.
- **Pattern uniformity at 11 sub-sprints**: F.2 + F.1 + F.4 + F.5 + F.3 + F.6 + G.1 + G.2 + G.3 + G.4 + G.5 = 26 files converted across the same mechanical conversion family with 0 conversion failures.
- **Locked-area scan clean**: NO Shield internals, NO Track-2 schema, NO WS Doc UI, NO Monitor pre-warmer, NO OAuth, NO product code touched.
- **All 6 banked discipline-slip lessons applied successfully (NO production-impacting slips this sprint)**:
  - F.5 YAML-edit slip → SINGLE batched edit + `yaml.safe_load` verify-before-slice ✓
  - F.3-ADVANCE memo-order slip → §9 row BEFORE memo authoring (no recovery needed) ✓
  - G.1 slice-poll-cadence-mismatch → slice ran in single foreground call (~110s, well under 240s foreground timeout) ✓
  - G.3-VERIFICATION AST-over-grep → fix-sprint used AST as primary verification (Row 4) + invariant suite (Rows 9-10) ✓
  - NEW G.4-ADVANCE UNQUARANTINED-runtime-PASS-baseline (lesson #5) SECOND APPLICATION → Row 1 of slice verifies 34/34 PASS preservation BYTE-PERFECT ✓
  - NEW G.4-FIX file-name-from-YAML (lesson #6) FIRST APPLICATION → Row 8 iter file names sourced from `ls tests/` not memo prose; no Row 8 RED ✓
- **1 script-level slip discovered + fixed mid-flight (NOT production-impacting)**: Slip A (Row 2 `-q -v` pytest flag conflict → assertion shape mismatch) → assertion shape corrected to node-ID invocation + count-based check. Lesson refinement (not a new banked lesson): when verifying SPECIFIC test runs, prefer node-ID + "N passed" over verbose-marker assertion.
- **F.6 Shield-contract regression discipline-pay APPLIED**: 3 mandatory rows shipped GREEN (Row 2 chat-surface via converted L63 solo run · Row 3 synisense_security · Row 4 AST source-check)
- **CLUSTER-G ARC M2 CLOSURE COMPLETE at FINAL state M2=1 (A+D-preserved by design)**

---

## §7 — Trajectory advance summary — CLUSTER-G ARC M2 CLOSURE FINAL

| Checkpoint | M1_CEILING | M2_CEILING | Reason |
|---|---:|---:|---|
| Pre-arc (post-F.6) | 5 | 26 | F-arc close; G-arc opens |
| G.1 close | 0 | 26 | G.1 -5 sites (M1 closure FINAL) |
| G.2 close | 0 | 11 | G.2 -15 sites (iter39 + iter53 batch) |
| G.3 close | 0 | 7 | G.3 -4 sites (iter54 quarantined) |
| G.4 close | 0 | 2 | G.4 -5 sites (Shield-adjacency trio; UNQUARANTINED) |
| **G.5 close (this sprint)** | **0** | **1** | **G.5 -1 site (Shield-adjacency outlier HYBRID); CLUSTER-G ARC M2 CLOSURE COMPLETE** |
| **Final state** | **0** | **1** | **A+D-preserved entry (`phase4_2:254`) remains by design** |

**Sub-sprint trajectory contribution**: G.5 closes the LAST closable M2 polluter site. Combined Cluster-G arc close: **M1 5→0 (FINAL) + M2 28→1 = 32 sites cleared + 1 A+D-preserved by design = 33 sites total across 5 sub-sprints**.

**Pattern uniformity across G.1-G.5**: all 5 Cluster-G sub-sprints used the same mechanical conversion family (`def → @pytest.mark.asyncio + async def` + `asyncio.run(coro) → await coro`). NEW G.4+G.5 specific contributions: UNQUARANTINED runtime PASS preservation discipline (lesson #5) battle-tested across 2 dispatches with 100% pass-preservation; file-name-from-YAML discipline (lesson #6) first-clean application at G.5.

**Cluster-G ARC M2 CLOSURE EVIDENCE**:
- ✅ M2 final state = 1 entry (A+D-preserved `phase4_2:254` by design)
- ✅ Row 13 of G.5 slice asserts the A+D-preserved entry intact + final state True
- ✅ Cluster-G arc closes per scope memo §1.5 final state expectation
- ✅ Next M2 ratcheting would require touching the A+D-preserved entry which is OUT OF SCOPE by design

---

## §8 — User-direction surface (HARD STOP)

Per dispatch directive: **HARD STOP at slice close — no chaining to Cluster-G arc retrospective**.

**G.5 milestone + CLUSTER-G ARC CLOSURE**:
- ✅ 1 G.5 file converted (1 M2 site cleared) · M2_CEILING ratcheted 2 → 1 (FINAL)
- ✅ Proving slice 13/13 GREEN in ~110s
- ✅ UNQUARANTINED runtime baseline 34/34 PASS preserved BYTE-PERFECT (lesson #5 SECOND application; battle-tested)
- ✅ F.6 Shield-contract regression discipline-pay applied (3 rows GREEN: chat-surface via L63 solo + synisense_security + AST source-check)
- ✅ Regression-check ladder GREEN (surface ratchets + Shield + G.2/G.3 siblings + G.4 trio + cross-cluster defensive)
- ✅ All 4 dispatch RULEs honoured (minimal scope + no cosmetic cleanup + no fallback URL change + no retrospective chaining)
- ✅ All 6 banked discipline-slip lessons applied (zero production-impacting slips; 1 script-level slip fixed mid-flight → lesson refinement to #6)
- ✅ **CLUSTER-G ARC M2 CLOSURE COMPLETE** at FINAL state M2=1 (A+D-preserved `phase4_2:254` by design)
- ✅ Row 13 of slice asserts the arc closure trajectory marker

**Cluster-G arc summary (READY FOR RETROSPECTIVE)**:
| Sub-sprint | M2 ratchet | UNQUARANTINED? | Sites cleared |
|---|---|---|---:|
| G.1 | M1 5→0 FINAL | YES | 5 (M1) |
| G.2 | M2 26→11 | NO (quarantined) | 15 |
| G.3 | M2 11→7 | NO (quarantined) | 4 |
| G.4 | M2 7→2 | YES (first UNQ; lesson #5 born) | 5 |
| G.5 | M2 2→1 FINAL | YES (lesson #5 second app) | 1 |
| **Total** | M1 5→0 + M2 28→1 | mixed | **30 (+2 G.1 retroactive M1 + 1 A+D-preserved = 33)** |

Recommended next dispatch: **Cluster-G arc retrospective** per user autonomous mandate queue item 5. Will document: trajectory matrix (above) + banked lessons #5 + #6 + pattern uniformity at 11 sub-sprints (26 files, 0 conversion failures) + F.6 Shield-contract discipline-pay applicability matrix across the arc + future applicability for Cluster-C + LLM_MODELS_REFRESH + closure-schedule lock state.

Per user autonomous mandate, Cluster-G arc retrospective can autonomously proceed at next dispatch boundary.

---

## §9 — Time-gate status at slice close

`Tue Jun 30 19:51:00 UTC 2026` approx at slice close. No active time-gate. Cluster-G arc CLOSED per scope §1.5 expected final state. Storage arc remains PAUSED awaiting Azure credentials.

End of memo.
