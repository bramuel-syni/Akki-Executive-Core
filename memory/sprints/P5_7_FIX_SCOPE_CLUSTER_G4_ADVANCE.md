**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.4` (Cluster-G sub-sprint G.4 = Shield-adjacency M2 trio · single-vs-sequential dispatch shape ADVANCE-SCAN-DEFAULT-ON per Cluster-F retrospective §5.1 · F.6 TWO-DISPATCH precedent applies; user autonomous mandate "Resume from idle" dispatch grants single-vs-sequential recommendation authority to advance-scan agent subject to escalation triggers (a/b/c)) + cross-references `sprints/JC_POLLUTION_CLUSTER_G3_FIX.md` (immediately preceding G.3 close) + `sprints/CLUSTER_F_RETROSPECTIVE.md §5.1` (advance-scan-default-on rule) + `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (closure-schedule lock origin)

# Sprint P5_7_FIX_SCOPE_CLUSTER_G4_ADVANCE — Shield-adjacency M2 trio advance scan

**Status**: SHIPPED (memo only) · READ-ONLY · HARD STOP at memo surface · single-G.4 dispatch shape RECOMMENDED per evidence ladder · escalation triggers (a/b/c) NOT TRIPPED so fix dispatch can autonomously proceed per user autonomous mandate
**Date**: 2026-06-30
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_G3_FIX.md` (G.3 close; M2_CEILING 11→7) · `sprints/JC_STORAGE_PIVOT_AZURE_SAS_DECISIONS_LOCK` (storage arc PAUSED; Cluster-G arc RESUMED per user autonomous run-to-close mandate)

---

## §0 — Trio identification (canonical)

| # | File | Lineno | Func | Site shape |
|---|---|---:|---|---|
| 1 | `tests/test_phase12_2_surfaces.py` | 61 | `test_paragraph_anchors_stable_through_redaction` | M2b single-capture (`out = asyncio.run(dryrun(...))`) |
| 2 | `tests/test_phase_a_synisense_unification.py` | 58 | `test_synisense_adapter_returns_pipeline_shaped_tokens` | M2c tuple-unpack (`redacted, shield_map = asyncio.run(_run())`) |
| 3 | `tests/test_phase_a_synisense_unification.py` | 96 | `test_rehydrate_round_trips_via_synisense_helpers` | M2c tuple-unpack (`redacted, shield_map = asyncio.run(_run())`) |
| 4 | `tests/test_solva_v2_llm_adapter.py` | 81 | `test_synisense_runs_before_llm` | M2b single-capture (`result = asyncio.run(_runner())`) |
| 5 | `tests/test_solva_v2_llm_adapter.py` | 125 | `test_adapter_refuses_when_synisense_fails` | M2a bare under `with pytest.raises(...)` |

**Total**: 3 files · 5 sites · 5 distinct test functions

---

## §1 — Critical findings

### §1.1 — ALL 3 files UNQUARANTINED (no pytestmark.skip)

Verified via:
```bash
for f in /app/backend/tests/test_phase12_2_surfaces.py \
         /app/backend/tests/test_phase_a_synisense_unification.py \
         /app/backend/tests/test_solva_v2_llm_adapter.py; do
  grep -nE "pytestmark|@pytest.mark.skip" $f
done
```

Result: **0 hits in all 3 files**. Tests RUN at runtime in CI.

This is FUNDAMENTALLY DIFFERENT from G.2 (iter39 + iter53) and G.3 (iter54) which were all Patch-8 quarantined batches with module-level `pytestmark = pytest.mark.skip(...)`. RULE-A "preserve quarantine" from G.2/G.3 N/A here; instead UNQUARANTINED conversions require **pre-conversion runtime PASS baseline capture + post-conversion runtime PASS re-verification** (see §6 banked discipline lesson #5).

### §1.2 — Pre-conversion runtime baseline (locked)

```bash
python -m pytest tests/test_phase12_2_surfaces.py \
                 tests/test_phase_a_synisense_unification.py \
                 tests/test_solva_v2_llm_adapter.py --tb=no -q
```

Result: **10 passed in 5.50s** (21 warnings — all `on_event` deprecation, unrelated).

Test breakdown: 3 in phase12_2 (L34, L77, L100) + 5 in phase_a (L37, L50, L85, L116, L142) + 2 in solva_v2 (L29, L105) = 10 collected · 10 passed.

Invariant suite baseline:

```bash
python -m pytest tests/invariants/test_no_bespoke_run_helper.py --tb=no -q
```

Result: **3 passed in 5.75s** (catcher + drift + count-ceiling M1=0/M2=7).

Post-conversion target: 10/10 PASS preserved + 3/3 PASS preserved + M2_CEILING ratcheted 7 → 2.

### §1.3 — pytest-asyncio config confirmed

`/app/backend/pytest.ini` declares:
```
asyncio_mode = auto
asyncio_default_fixture_loop_scope = session
asyncio_default_test_loop_scope = session
```

Auto mode means `@pytest.mark.asyncio` decorator is REDUNDANT for `async def test_*` functions — they're auto-collected. **However**, phase_a uses the decorator on its pre-existing async example at L115 (`@pytest.mark.asyncio` + `async def test_call_llm_routes_through_synisense_no_key_branch`). For **in-file consistency** + **belt-and-braces robustness** + **pattern uniformity with G.2/G.3 conversion shape**, the fix dispatch will ADD the decorator on G.4 conversions (despite redundancy in auto mode).

`session`-scoped fixture + test loop is critical for Motor's module-singleton client (per pytest.ini comment); G.4 conversions inherit this scoping by default (no per-test fixture redefinition needed).

---

## §2 — Per-file analysis

### §2.1 — `test_phase12_2_surfaces.py`

| Property | Value |
|---|---|
| M2 sites | 1 (line 61) |
| Conversion target functions | 1 |
| Other test functions untouched | 2 (L77 + L100 — pure sync, no asyncio.run, NOT M2 sites) |
| Quarantine status | UNQUARANTINED |
| Shield surface contact | REAL `services.synisense.dryrun` call inside the test body |
| Mocking | NONE (real Shield call) |
| Risk | MEDIUM (real Shield surface contact; conversion must preserve identical call semantics) |
| pre-existing pytest-asyncio examples in file | NONE (this conversion will be the first async test in the file) |

**Conversion shape**:
```diff
-def test_paragraph_anchors_stable_through_redaction():
+@pytest.mark.asyncio
+async def test_paragraph_anchors_stable_through_redaction():
     ...
-        out = asyncio.run(dryrun(p["text"], context_id="t", surface="ingest"))
+        out = await dryrun(p["text"], context_id="t", surface="ingest")
```

Net diff: +1 decorator line · 1 `def` → `async def` · 1 `asyncio.run(...)` → `await ...`. **No other LOC touched per RULE-2 minimal scope.**

`import asyncio` becomes orphaned at module level after conversion (no other call sites). RULE-2 forbids cosmetic cleanup → keep `import asyncio` line 16.

### §2.2 — `test_phase_a_synisense_unification.py`

| Property | Value |
|---|---|
| M2 sites | 2 (lines 58 + 96) |
| Conversion target functions | 2 |
| Other test functions untouched | 3 (L37 sync, L116 already async, L142 sync — NOT M2 sites) |
| Quarantine status | UNQUARANTINED |
| Shield surface contact | REAL `services.synisense.shield_payload_async` + `rehydrate` calls inside test bodies |
| Mocking | NONE (real Shield calls) |
| Risk | MEDIUM (real Shield surface contact at 2 sites) |
| pre-existing pytest-asyncio examples in file | YES at L115 (`@pytest.mark.asyncio` + `async def test_call_llm_routes_through_synisense_no_key_branch`) |

**Conversion shape** (both sites identical mechanical pattern):
```diff
-def test_synisense_adapter_returns_pipeline_shaped_tokens():
+@pytest.mark.asyncio
+async def test_synisense_adapter_returns_pipeline_shaped_tokens():
     ...
-    async def _run():
-        return await shield_payload_async(
-            SAMPLE_PROMPT, surface="chat", context_id="phase-a-test",
-        )
-
-    redacted, shield_map = asyncio.run(_run())
+    redacted, shield_map = await shield_payload_async(
+        SAMPLE_PROMPT, surface="chat", context_id="phase-a-test",
+    )
     ...
```

**OPTIONAL inner-helper inlining at conversion time**: the inner `async def _run()` becomes a single-call wrapper that can be inlined. **Decision**: do NOT inline per RULE-2 minimal scope (inlining = cosmetic cleanup). Keep inner `_run` definitions verbatim; just change `asyncio.run(_run())` → `await _run()`:

```diff
-def test_synisense_adapter_returns_pipeline_shaped_tokens():
+@pytest.mark.asyncio
+async def test_synisense_adapter_returns_pipeline_shaped_tokens():
     ...
     async def _run():
         return await shield_payload_async(
             SAMPLE_PROMPT, surface="chat", context_id="phase-a-test",
         )

-    redacted, shield_map = asyncio.run(_run())
+    redacted, shield_map = await _run()
```

Same shape applies to L96 conversion.

Net diff: 2 decorator lines · 2 `def` → `async def` · 2 `asyncio.run(...)` → `await ...`. **Inner `_run` defs PRESERVED verbatim per RULE-2.**

### §2.3 — `test_solva_v2_llm_adapter.py`

| Property | Value |
|---|---|
| M2 sites | 2 (lines 81 + 125) |
| Conversion target functions | 2 |
| Other test functions untouched | 0 (file has exactly 2 tests, both convert) |
| Quarantine status | UNQUARANTINED |
| Shield surface contact | MOCKED via `monkeypatch.setattr("services.synisense.run", ...)` |
| Mocking | HERMETIC (no real Shield call) |
| Risk | LOW (fully mocked; conversion is purely structural) |
| pre-existing pytest-asyncio examples in file | NONE |

**Conversion shape** (site 1 — L81):
```diff
-def test_synisense_runs_before_llm(monkeypatch):
+@pytest.mark.asyncio
+async def test_synisense_runs_before_llm(monkeypatch):
     ...
     async def _runner():
         return await llm_adapter.shielded_call(
             engine="llm_primary", ...
         )

-    result = asyncio.run(_runner())
+    result = await _runner()
```

**Conversion shape** (site 2 — L125; M2a bare under `with pytest.raises(...)`):
```diff
-def test_adapter_refuses_when_synisense_fails(monkeypatch):
+@pytest.mark.asyncio
+async def test_adapter_refuses_when_synisense_fails(monkeypatch):
     ...
     async def _runner():
         await llm_adapter.shielded_call(...)

     with pytest.raises(RuntimeError, match="Synisense unavailable"):
-        asyncio.run(_runner())
+        await _runner()
```

Note: `with pytest.raises(...): await _runner()` works correctly under `@pytest.mark.asyncio` — the assertion context manager intercepts the exception from the awaited coroutine. Verified pattern matches G.2's iter53 site at L222 which used same construct.

Net diff: 2 decorator lines · 2 `def` → `async def` · 2 `asyncio.run(...)` → `await ...`. **Inner `_runner` defs PRESERVED verbatim per RULE-2.**

`import asyncio` at module-level becomes orphaned post-conversion. RULE-2 → keep.

---

## §3 — Sub-sprint shape decision

### §3.1 — Two candidate shapes

| Shape | Pros | Cons |
|---|---|---|
| **Single G.4 dispatch** | One proving slice covers all 3 files; faster overall; pattern uniformity carries across batch | If any site converts badly, all 5 affected |
| **Sequential G.4a/b/c** | Per-file isolation; smaller blast radius if regression surfaces; F.6 TWO-DISPATCH precedent | 3× more dispatch ceremony; 3× more proving slices; 3× more sprint memos; F.6 risk-shape doesn't fully apply (F.6 = INTERNAL Shield code mutation; G.4 = TEST-SIDE-ONLY) |

### §3.2 — Six evidence rows favouring SINGLE G.4

| # | Evidence | Implication |
|---:|---|---|
| 1 | F.6 precedent was INTERNAL Shield code mutation (`synisense_security.py` modified); G.4 is TEST-SIDE-ONLY mechanical conversion | Risk model differs significantly — test-side mechanical work has historically (8 sub-sprints worth) been single-dispatch-safe |
| 2 | ALL 3 files share IDENTICAL conversion shape: `def → async def` + `asyncio.run(coro) → await coro` + decorator add | No file-specific tailoring → no reason to split the dispatch |
| 3 | Pattern uniformity at 9 sub-sprints (F.2 + F.1 + F.4 + F.5 + F.3 + F.6 + G.1 + G.2 + G.3 = 22 files converted with same M1+M2 conversion family); 0 conversion failures across 22 files | Mechanical conversion has 0% historical failure rate; statistical confidence is HIGH |
| 4 | 5 sites across 3 files is a SMALL batch well within single-dispatch capacity (G.2 shipped 15 sites across 2 files in one dispatch + iter53 had 9 sites alone) | Cardinality argument does NOT push toward splitting |
| 5 | UNQUARANTINED status enables RUNTIME validation post-conversion (10/10 PASS preservation check); STRONGER validation than G.2/G.3 quarantined-files (which could only do collection-time validation) | More robust feedback loop → single dispatch is safer here than it was at G.2/G.3 |
| 6 | Proving slice can cover all 3 files in 12-15 rows (per-file isolation rows + cross-file Shield contract regression + invariant suite + AST source-check + G.2/G.3 sibling regression) | Slice cadence is the same as G.2/G.3 — fits the established ~60s runtime envelope |

### §3.3 — Escalation triggers evaluation (per user autonomous mandate)

| Trigger | Status | Reasoning |
|---|---|---|
| (a) Locked-area collision | **NOT TRIPPED** | Shield internals NOT mutated; OAuth NOT mutated; WS Doc NOT mutated; Track-2 NOT mutated; Monitor NOT mutated. Conversion is 100% test-side. |
| (b) Scope outside Cluster-G plan | **NOT TRIPPED** | The 3 files are EXACTLY the Shield-adjacency trio identified in Cluster-G §1.4 (per G.3 forward-look note + scope memo). |
| (c) Evidence ambiguous between dispatch shapes | **NOT TRIPPED** | 6 evidence rows uniformly favour single G.4; counterargument (F.6 precedent) addressed in evidence row 1. |

**All 3 triggers NOT TRIPPED** → per user autonomous mandate, fix dispatch can autonomously proceed with single G.4 shape.

### §3.4 — Single-G.4 dispatch LOCKED

The fix dispatch will be a SINGLE `JC-POLLUTION-CLUSTER-G4-FIX` dispatch executing all 5 site conversions across 3 files in one batched proving slice.

---

## §4 — Locked-area sweep

| Area | Touched in conversion? | Touched in advance scan? |
|---|:---:|:---:|
| Shield internals (`services.synisense.*`, `pipeline_run`, `shield_*` modules) | NO (only test-side `asyncio.run` → `await`) | NO (only reads test files) |
| Track-2 schema (`perspective_spread` slot, divergent deck builder) | NO | NO |
| Monitor pre-warmer (`services/monitor/*`) | NO | NO |
| OAuth provider live endpoints | NO | NO |
| WS Doc UI (doc-generation rendering) | NO | NO |
| Product code | NO mutation | NO mutation |
| Existing GridFS upload path | NO | NO |
| Backfilled 3068 rows | NO | NO |
| Storage arc (Azure SAS work) | NO (Cluster-G + storage arcs are independent) | NO |

Cleared.

---

## §5 — F.6 Shield-contract regression discipline-pay

F.6 banked a "Shield contract regression discipline-pay" rule for any sub-sprint that touches Shield-adjacency code paths. G.4 trio has 2 real-Shield-call files (phase12_2 + phase_a) so the discipline-pay applies. Pay = 3 mandatory proving-slice rows:

1. **Defensive row for synisense_security file** (Shield contract preservation): run `tests/test_synisense_security.py` post-conversion; require GREEN (3 tests minimum per F.6 baseline)
2. **Defensive row for chat surface** (real Shield call from phase_a is exercised): run phase_a as part of the conversion check; require 5/5 PASS (1 sync + 2 converted + 1 already-async + 1 sync mapping test)
3. **AST source-check** verifies catcher's `test_*` AST scope is the actual fix-set (no underscore-prefixed orphan trap as in G.3-VERIFICATION §3.1 — already confirmed in §2 above that NONE of the 3 G.4 files have `_disabled_test_*` orphans)

These 3 rows will be embedded in the G.4 fix dispatch proving slice. Plus the runtime PASS preservation row (per new banked lesson §6) covers an even stronger validation surface.

---

## §6 — NEW banked discipline lesson #5: UNQUARANTINED conversions require pre-conversion runtime PASS baseline

**Lesson statement**: When converting `asyncio.run(coro) → await coro` in a test file that is NOT module-level quarantined (no `pytestmark = pytest.mark.skip(...)`), the fix dispatch MUST capture pre-conversion runtime PASS baseline AND verify post-conversion runtime PASS preservation. Collection-time validation (which suffices for quarantined files) is INSUFFICIENT because real test bodies run.

**Origin**: G.4 trio (this advance scan, 2026-06-30). All 3 files UNQUARANTINED — first time in Cluster-G arc.

**Distinguishing feature**: G.2 + G.3 = quarantined batches → validation was AST + collection-time + invariant suite (no runtime body execution). G.4 (and future G.5) = UNQUARANTINED → validation MUST add a runtime PASS baseline + post-conversion PASS preservation row to the proving slice.

**Applied at**: G.4 fix dispatch (mandatory row 1 = baseline preserve). Re-applied at G.5 fix dispatch (G.5 file `test_synisense_surface_validation.py` quarantine status to be re-verified in G.5 advance scan).

**Pattern uniformity preserved**: the conversion shape itself (`def → async def`, `asyncio.run → await`) is UNCHANGED from G.2/G.3; only the validation ladder gains 1 row.

---

## §7 — Conversion shape locked (canonical for G.4 fix dispatch)

Per-site conversion shape (all 5 sites share IDENTICAL pattern):

```python
# BEFORE:
def test_X(monkeypatch=...):
    ...
    async def _runner():
        return await ...
    result = asyncio.run(_runner())
    assert ...

# AFTER:
@pytest.mark.asyncio
async def test_X(monkeypatch=...):
    ...
    async def _runner():
        return await ...
    result = await _runner()
    assert ...
```

For inline single-call sites (e.g., phase12_2:61) where there's no inner `_runner` def:

```python
# BEFORE:
def test_X():
    ...
    out = asyncio.run(dryrun(...))
    ...

# AFTER:
@pytest.mark.asyncio
async def test_X():
    ...
    out = await dryrun(...)
    ...
```

For `with pytest.raises(...)` sites (e.g., solva_v2:125):

```python
# BEFORE:
def test_X(monkeypatch):
    ...
    async def _runner():
        await ...
    with pytest.raises(RuntimeError, match="..."):
        asyncio.run(_runner())

# AFTER:
@pytest.mark.asyncio
async def test_X(monkeypatch):
    ...
    async def _runner():
        await ...
    with pytest.raises(RuntimeError, match="..."):
        await _runner()
```

All 3 variants are mechanically interchangeable; the diff is uniformly `+@pytest.mark.asyncio` + `def → async def` + `asyncio.run(coro) → await coro`. Total expected diff: ~5 decorator lines + 5 function signature changes + 5 call-site changes = ~15 LOC net delta across 3 files (additive only; no deletions outside the M2 site itself).

---

## §8 — Forward look (G.4 fix dispatch shape)

**Dispatch slug**: `JC-POLLUTION-CLUSTER-G4-FIX` (single dispatch per §3.4 lock).

**Proving slice target rows (12-15)**:

| Row | Check | Expected |
|---:|---|---|
| 1 | **G.4 trio runtime PASS preservation (per §6 banked lesson)** | **10/10 PASS preserved post-conversion** |
| 2 | phase12_2 isolation post-fix | 3/3 PASS |
| 3 | phase_a isolation post-fix | 5/5 PASS |
| 4 | solva_v2 isolation post-fix | 2/2 PASS |
| 5 | F.6 Shield contract via synisense_security defensive | 3/3 PASS minimum |
| 6 | chat surface real-Shield-call via phase_a (already covered by row 3) | confirmed by row 3 |
| 7 | autosave defensive (B.2 polluter pair pattern) | PASS |
| 8 | phase4_2 A+D defensive | 8/8 PASS (surface ratchets in lockstep) |
| 9 | p5_10 Cluster-E defensive | 5/5 PASS |
| 10 | G.2 + G.3 sibling regression (iter39 + iter53 + iter54) | 26 SKIPPED in <0.5s (quarantine intact) |
| 11 | G.4 trio + invariant suite | 13/13 PASS (10 G.4 + 3 invariant) |
| 12 | invariant cross-validation M2_CEILING ratcheted 7 → 2 | 3/3 PASS with new ceiling |
| 13 | inventory slice sibling re-run | 3/3 GREEN (M1=0/0, M2=2/2, zero drift) |
| 14 | AST source-assertion all 3 files clean of `asyncio.run`-in-test | 0 sites in catcher AST scope |
| 15 | log scan zero `Future attached to a different loop` | 0 occurrences |

**M2 trajectory**: 7 → 2 (-5 sites; -71% reduction in single sub-sprint). Combined Cluster-G arc close after G.4: M1 0→0 (FINAL) · M2 28→2 (-26 sites across G.1+G.2+G.3+G.4 = 4 sub-sprints).

**G.5 forward-look (NOT chained per autonomous mandate's HARD STOP-between-sub-sprints rule)**: only `synisense_surface_validation.py:78` remains as the single M2 outlier. Per G.4 banked-lesson #5 the G.5 advance scan must re-verify quarantine status + capture pre-conversion runtime baseline.

---

## §9 — Discipline notes

- **READ-ONLY scope honoured**: 0 LOC mutated outside this memo file
- **Canonical spec cited on line 1**: explicit cite of `P5_7_FIX_SCOPE_CLUSTER_G.md §1.4` + cross-references
- **F.3-ADVANCE memo-order slip lesson APPLIED**: DEV_PIPELINE.md §9 row authored BEFORE this memo file
- **F.5 YAML-edit slip lesson N/A**: no YAML edits this dispatch
- **G.1 slice-poll-cadence-mismatch lesson N/A**: no proving slice runs in scope; baseline pytest runs ~5.5s well under foreground timeout
- **G.3-VERIFICATION AST-over-grep lesson APPLIED**: used `grep -nE "pytestmark|@pytest.mark.skip"` to definitively confirm UNQUARANTINED status + direct pytest invocation for runtime baseline; no fragile greps
- **NEW G.4-ADVANCE banked lesson #5**: UNQUARANTINED conversions require pre-conversion runtime PASS baseline (this scan captured 10/10 baseline)
- **No testing subagent used** (per banned-list rule + user explicit ban)
- **No scope creep**: the 9 numbered sections + 1 discipline section is the exact deliverable; no extra audit, no extra files
- **No build steps executed**: advance scan is READ-ONLY by definition
- **HARD STOP** at memo surface; standing rules unchanged
- **Cluster-G arc continues** at G.4 fix dispatch boundary; storage arc remains PAUSED (no Azure creds delivered)

---

## §10 — User-direction surface (HARD STOP)

Per user autonomous mandate: **HARD STOP at memo surface; surface to user; G.4 fix dispatch can autonomously proceed at next dispatch boundary because escalation triggers (a/b/c) NOT TRIPPED.**

**G.4 advance scan milestone**:
- ✅ Trio identified (3 files · 5 sites)
- ✅ Pre-conversion runtime PASS baseline captured (10/10 PASS in 5.50s)
- ✅ Quarantine status verified UNQUARANTINED for all 3 files
- ✅ pytest-asyncio config confirmed (`asyncio_mode = auto`; decorator kept for in-file consistency)
- ✅ Per-file analysis complete (sites + sub-shape + Shield contact + risk)
- ✅ Conversion shape locked (mechanical; identical to G.2/G.3 family)
- ✅ Sub-sprint shape decision: SINGLE G.4 (6 evidence rows; escalation triggers not tripped)
- ✅ Locked-area sweep clean
- ✅ F.6 Shield-contract regression discipline-pay rows planned (3 mandatory)
- ✅ NEW banked discipline lesson #5 documented
- ✅ Forward look: 15-row proving slice + M2 trajectory 7 → 2
- ✅ 0 LOC mutated outside memo file

**Next dispatch** (autonomous per user run-to-close mandate): **`JC-POLLUTION-CLUSTER-G4-FIX`** — single-dispatch · 5 site conversions across 3 files · 15-row proving slice · 24 LOC est. diff (15 conversion + 4 YAML deletes + 2 ceiling ratchet + 3 audit).

Standing rules unchanged. Time-gate status: no active time-gate. Cluster-G arc continues; storage arc PAUSED awaiting Azure credentials.

End of memo.
