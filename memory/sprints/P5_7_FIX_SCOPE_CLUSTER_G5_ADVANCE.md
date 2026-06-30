**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.5` (Cluster-G sub-sprint G.5 = Shield-adjacency M2 outlier `test_synisense_surface_validation.py:78` · HYBRID 4-sync-preserved + 1-async-converted shape · advance-scan-default-on per Cluster-F retrospective §5.1 · user autonomous mandate granting single-vs-sequential authority subject to escalation triggers (a/b/c/d) per `JC-POLLUTION-CLUSTER-G5-ADVANCE-SCAN` dispatch) + cross-references `sprints/JC_POLLUTION_CLUSTER_G4_FIX.md` (G.4 close immediately precedes) + `sprints/CLUSTER_F_RETROSPECTIVE.md §5.1` (advance-scan-default-on rule) + `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (closure-schedule lock origin)

# Sprint P5_7_FIX_SCOPE_CLUSTER_G5_ADVANCE — Shield-adjacency M2 outlier advance scan

**Status**: SHIPPED (memo only) · READ-ONLY · HARD STOP at memo surface · single-G.5 dispatch shape AUTO-LOCKED (only 1 site; single-vs-sequential question is N/A) · escalation triggers (a/b/c/d) NOT TRIPPED so fix dispatch can autonomously proceed per user autonomous mandate
**Date**: 2026-06-30
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_G4_FIX.md` (G.4 close immediately precedes; M2_CEILING ratcheted 7 → 2; Cluster-G arc continues at G.5 for the final M2 closure)

---

## §0 — Target identification (canonical, via YAML lookup per lesson #6)

Source: `tests/invariants/bespoke_run_helper_grandfathered.yml` (post-G.4 state; M2 list = 2 entries).

| Field | Value |
|---|---|
| File | `backend/tests/test_synisense_surface_validation.py` |
| Func | `test_real_pipeline_run_rejects_bad_subsurface` |
| Lineno | 78 |
| Site shape | M2a bare (`asyncio.run(_runner())` with `_runner` already async + `with pytest.raises(...)` INSIDE `_runner` body) |
| Notes | "M2 site discovered by 2026-06-27 invariant baseline scan; needs per-file investigation (not in Cluster-F scope)" |

Per lesson #6: identification sourced PROGRAMMATICALLY via `yaml.safe_load` of the grandfather YAML, NOT from memo prose. AST scan + grep cross-validates exactly 1 M2 site at L78.

---

## §1 — Critical findings

### §1.1 — UNQUARANTINED (lesson #5 verify)

Verified via:
```bash
grep -nE "pytestmark|@pytest.mark.skip" /app/backend/tests/test_synisense_surface_validation.py
```

Result: **0 hits**. Tests RUN at runtime in CI.

This MATCHES G.4 trio pattern (UNQUARANTINED) — same NEW banked lesson #5 applies: **pre-conversion runtime PASS baseline capture + post-conversion runtime PASS preservation** required. RULE-A "preserve quarantine" from G.2/G.3 N/A here.

### §1.2 — Pre-conversion runtime baseline (locked)

```bash
python -m pytest tests/test_synisense_surface_validation.py --tb=no -q
```

Result: **34 passed in 3.71s** (21 warnings — `on_event` deprecation, unrelated).

Test breakdown:
- 14 instances of `test_explicit_allow_list_remains_valid` (parametrize over `sorted(_VALID_SURFACES)`)
- 1 instance of `test_solve_v2_bare_remains_valid`
- 7 instances of `test_solve_v2_subsurfaces_are_valid` (parametrize)
- 11 instances of `test_invalid_surfaces_are_rejected` (parametrize)
- 1 instance of `test_real_pipeline_run_rejects_bad_subsurface` (the G.5 target)

**Total: 14 + 1 + 7 + 11 + 1 = 34 collected/passed.**

Cross-check: `_VALID_SURFACES` cardinality verified via direct import = **14** (briefing, chat, chat_classifier, chat_evidence_list, chat_four_check, deck, ingest, journal_commentary, public_read, pulse, report, sandbox_generation, solve, solve_v2). Matches parametrize count exactly.

Invariant suite baseline:
```bash
python -m pytest tests/invariants/test_no_bespoke_run_helper.py --tb=no -q
```

Result: **3 passed in 5.79s** (catcher + drift + count-ceiling with M1_CEILING=0, M2_CEILING=2).

Post-conversion target: 34/34 PASS preserved + 3/3 PASS preserved + M2_CEILING ratcheted 2 → 1 (final state).

### §1.3 — HYBRID 4-sync-preserved + 1-async-converted shape justified by PRODUCT API SURFACE

AST scan of the file confirms 5 test functions, exactly 1 M2 site:

| L | Test function | Calls | Async machinery? | Decision |
|---:|---|---|---|---|
| 25 | `test_explicit_allow_list_remains_valid` (parametrize × 14) | sync `_is_valid_surface(surface) → bool` | NONE | **STAY SYNC** |
| 29 | `test_solve_v2_bare_remains_valid` | sync `_is_valid_surface("solve_v2") → bool` | NONE | **STAY SYNC** |
| 42 | `test_solve_v2_subsurfaces_are_valid` (parametrize × 7) | sync `_is_valid_surface(surface) → bool` | NONE | **STAY SYNC** |
| 59 | `test_invalid_surfaces_are_rejected` (parametrize × 11) | sync `_is_valid_surface(bad) → bool` | NONE | **STAY SYNC** |
| 63 | `test_real_pipeline_run_rejects_bad_subsurface` (G.5 target) | async `await run(text=..., context_id=..., surface=..., mode=..., account_id=...)` | YES (the only async call in the file) | **CONVERT ASYNC** |

**Justification**: the async/sync split is dictated by the PRODUCT API SURFACE — `_is_valid_surface` is a pure-Python predicate function (sync); `pipeline.run` is an async coroutine (Motor I/O, real Shield pipeline). The 4 sync tests legitimately use NO async machinery; converting them to async would be cosmetic + scope creep (no `await` calls would be added). The 1 G.5 target is the ONLY test calling the async surface, and it's the ONLY M2 site. **The split is product-driven, not stylistic.**

### §1.4 — Site shape M2a bare (matches G.4 solva_v2:125 pattern)

```python
# L63-78 (current source):
def test_real_pipeline_run_rejects_bad_subsurface(monkeypatch):
    """End-to-end: pipeline.run raises ValueError on a malformed sub-surface."""
    import asyncio
    from services.synisense.pipeline import run

    async def _runner():
        with pytest.raises(ValueError, match="invalid surface"):
            await run(
                text="hello world",
                context_id="ctx-test",
                surface="solve_v2.Bad-Thing",
                mode="redact",
                account_id="acct-test",
            )

    asyncio.run(_runner())  # ← M2 site at L78
```

**Sub-shape classification**: M2a bare under exception-raise context manager — the `with pytest.raises(...)` context manager is INSIDE `_runner` (NOT outside the `asyncio.run(...)` wrapper). This matches G.4's solva_v2:125 conversion shape exactly. The conversion is:

```python
# AFTER:
@pytest.mark.asyncio
async def test_real_pipeline_run_rejects_bad_subsurface(monkeypatch):
    """End-to-end: pipeline.run raises ValueError on a malformed sub-surface."""
    import asyncio  # PRESERVED orphaned per RULE-2 (function-local, post-conversion unused)
    from services.synisense.pipeline import run

    async def _runner():
        with pytest.raises(ValueError, match="invalid surface"):
            await run(
                text="hello world",
                context_id="ctx-test",
                surface="solve_v2.Bad-Thing",
                mode="redact",
                account_id="acct-test",
            )

    await _runner()  # ← was `asyncio.run(_runner())`
```

Net diff: **+1 decorator line · 1 `def` → `async def` · 1 `asyncio.run(_runner())` → `await _runner()` = ~3 LOC additive.** Inner `async def _runner()` + `with pytest.raises(...)` + `await run(...)` body PRESERVED verbatim per RULE-2.

**Function-local `import asyncio` at L65**: stays orphaned post-conversion. RULE-2 forbids the cleanup. Note that this is a function-local import (inside the test body), not module-level — but RULE-2 applies uniformly.

---

## §2 — Sub-sprint shape decision

### §2.1 — Single-vs-sequential question N/A

The G.5 dispatch targets **1 file with 1 M2 site**. There is no single-vs-sequential ambiguity — the dispatch is inherently single-shape because there is no sub-divisible scope. Per user autonomous mandate, this is an auto-locked single-G.5 dispatch.

### §2.2 — Escalation triggers evaluation (per user autonomous mandate)

| Trigger | Status | Reasoning |
|---|---|---|
| (a) Locked-area collision | **NOT TRIPPED** | Only test-side conversion at L78; `services.synisense.pipeline.run` is IMPORTED but NOT mutated; Shield internals NOT touched. |
| (b) Scope outside §1.5 | **NOT TRIPPED** | File has EXACTLY 1 M2 site at L78 as expected per scope memo + YAML cross-validation. HYBRID 4-sync + 1-async confirmed by AST + product-API surface analysis (§1.3). |
| (c) Evidence ambiguous on 4-sync rationale | **NOT TRIPPED** | 4 sync tests call SYNC `_is_valid_surface(surface) → bool` predicate; 1 async test calls ASYNC `pipeline.run(...)` coroutine. Async/sync boundary is on PRODUCT API surface (`_is_valid_surface` is sync; `pipeline.run` is async) — NOT a stylistic choice. Six per-test rows in §1.3 table provide explicit evidence. |
| (d) Quarantine status surprise | **NOT TRIPPED** | UNQUARANTINED confirmed via grep (0 `pytestmark.skip` hits); matches G.4 trio pattern; NEW lesson #5 applies (runtime PASS baseline + preservation row). |

**All 4 triggers NOT TRIPPED** → per user autonomous mandate, fix dispatch can autonomously proceed with single G.5 shape on next turn.

---

## §3 — Locked-area sweep

| Area | Touched in conversion? | Touched in advance scan? |
|---|:---:|:---:|
| Shield internals (`services.synisense.*` body modules, `pipeline_run`, `shield_*` modules) | NO (only test-side `asyncio.run` → `await`; `services.synisense.pipeline.run` is IMPORTED + CALLED but NOT mutated) | NO (only reads test file + imports `_VALID_SURFACES`) |
| Track-2 schema (`perspective_spread` slot, divergent deck builder) | NO | NO |
| Monitor pre-warmer (`services/monitor/*`) | NO | NO |
| OAuth provider live endpoints | NO | NO |
| WS Doc UI (doc-generation rendering) | NO | NO |
| Product code | NO mutation | NO mutation |
| Storage arc (Azure SAS work) | NO (Cluster-G + storage arcs are independent) | NO |
| Existing GridFS upload path | NO | NO |
| Backfilled 3068 rows | NO | NO |

Cleared.

---

## §4 — F.6 Shield-contract regression discipline-pay

F.6 banked "Shield contract regression discipline-pay" for any sub-sprint touching Shield-adjacency code paths. G.5 target (L63 `test_real_pipeline_run_rejects_bad_subsurface`) calls REAL `services.synisense.pipeline.run` via the inner `_runner` coroutine. Discipline-pay APPLIES.

**Pay = 3 mandatory proving-slice rows planned for G.5 fix dispatch**:

1. **Defensive row for `synisense_security`** (Shield contract preservation): run `tests/test_synisense_security.py` post-conversion; require GREEN (3 tests minimum per F.6 baseline + G.4 fix Row 5 evidence).
2. **Chat-surface real-Shield-call exercise**: COVERED INTERNALLY in G.5 — Row 2 (G.5 file isolation post-fix) runs the converted L63 test which itself calls real `pipeline.run` with malformed `solve_v2.Bad-Thing` and asserts `ValueError, match="invalid surface"`. This IS the live-Shield-contract exercise; no additional row needed. (Distinguishes from G.4 where chat surface was a separate Row 6 cover.)
3. **AST source-check confirms 0 hits in catcher's `test_*` AST scope** post-fix: dedicated row in the proving slice with the same scope as G.4 fix Row 14.

Plus the runtime PASS preservation row (per lesson #5) provides the strongest validation surface — 34/34 PASS must hold byte-perfect.

---

## §5 — Per-banked-lesson application

All 6 banked discipline-slip lessons apply to the G.5 fix dispatch. Applicability matrix:

| Lesson | Applies? | Why |
|---|:---:|---|
| F.5 YAML-edit slip | YES | YAML edit must be SINGLE batched (1 entry removal); `yaml.safe_load` verify-after pattern applies |
| F.3-ADVANCE memo-order slip | YES | DEV_PIPELINE §9 row must precede memo authoring for the fix dispatch (already applied in this advance scan) |
| G.1 slice-poll-cadence-mismatch | YES | G.5 fix dispatch will run proving slice in single foreground call (~30-60s expected; well under foreground timeout) |
| G.3-VERIFICATION AST-over-grep | YES | Use AST as primary verification (Row for source-check) + invariant suite; no fragile greps in slice |
| NEW G.4-ADVANCE UNQUARANTINED-runtime-PASS-baseline | YES | UNQUARANTINED file → runtime PASS baseline (34/34 in 3.71s) captured here + preservation row required in G.5 fix proving slice |
| NEW G.4-FIX file-name-from-YAML (lesson #6) | YES | All non-target file references in the G.5 fix proving slice (iter39/53/54, autosave, phase4_2, p5_10, etc.) must be sourced from YAML or `ls + grep`, NOT from memo prose. Applied here: target file/func/lineno sourced via `yaml.safe_load` of grandfather YAML. |

---

## §6 — Conversion shape locked (canonical for G.5 fix dispatch)

```python
# BEFORE (L63-78):
def test_real_pipeline_run_rejects_bad_subsurface(monkeypatch):
    """End-to-end: pipeline.run raises ValueError on a malformed sub-surface."""
    import asyncio
    from services.synisense.pipeline import run

    async def _runner():
        with pytest.raises(ValueError, match="invalid surface"):
            await run(
                text="hello world",
                context_id="ctx-test",
                surface="solve_v2.Bad-Thing",
                mode="redact",
                account_id="acct-test",
            )

    asyncio.run(_runner())

# AFTER:
@pytest.mark.asyncio
async def test_real_pipeline_run_rejects_bad_subsurface(monkeypatch):
    """End-to-end: pipeline.run raises ValueError on a malformed sub-surface."""
    import asyncio  # PRESERVED orphaned per RULE-2 (function-local; post-conversion unused but RULE-2 forbids cosmetic cleanup)
    from services.synisense.pipeline import run

    async def _runner():
        with pytest.raises(ValueError, match="invalid surface"):
            await run(
                text="hello world",
                context_id="ctx-test",
                surface="solve_v2.Bad-Thing",
                mode="redact",
                account_id="acct-test",
            )

    await _runner()
```

Total diff: **+1 decorator · 1 `def → async def` · 1 `asyncio.run(_runner()) → await _runner()` = ~3 LOC additive in the test file.** Plus YAML 1-entry removal + M2_CEILING 2→1 ratchet = 2 single-line edits in invariant files.

---

## §7 — Forward look (G.5 fix dispatch shape)

**Dispatch slug**: `JC-POLLUTION-CLUSTER-G5-FIX` (single dispatch).

**Proving slice target rows (12-15)**:

| Row | Check | Expected |
|---:|---|---|
| 1 | **G.5 file runtime PASS preservation (per lesson #5)** | **34/34 PASS preserved post-conversion** |
| 2 | G.5 file isolation post-fix (also covers chat-surface real-Shield-call) | 34/34 PASS in ~4s |
| 3 | F.6 Shield contract via `synisense_security` defensive | 3/3 PASS minimum |
| 4 | AST source-check 0 hits in catcher's `test_*` scope (F.6 + G.3-VERIFICATION discipline-pay) | 0 sites |
| 5 | autosave defensive (B.2 polluter pair pattern) | PASS |
| 6 | phase4_2 A+D defensive | 8/8 PASS (surface ratchets in lockstep) |
| 7 | G.4 trio post-fix runtime regression (phase12_2 + phase_a + solva_v2) | 10/10 PASS (G.4 conversions still passing) |
| 8 | G.2 + G.3 sibling regression (iter39 + iter53 + iter54 → 26 skipped) | 26 skipped in <0.5s |
| 9 | G.5 file + invariant suite (37/37 PASS expected = 34 G.5 + 3 invariant) | PASS |
| 10 | Invariant cross-validation M2_CEILING ratcheted 2 → 1 (final state) | 3/3 PASS |
| 11 | Inventory slice sibling re-run (post-G.5 steady state 9/10 GREEN + YAML M1=0/M2=1) | GREEN |
| 12 | Log scan 0 'Future attached to a different loop' | 0 occurrences |
| 13 | Cluster-G arc closure marker — M2 trajectory 28→26→11→7→2→**1 FINAL** | Trajectory locked at final state |

13 rows is sufficient for the single-site G.5 dispatch (vs G.4's 15 rows for 3 files); the smaller scope justifies a tighter slice. Lesson #6 will be re-applied: all file references sourced from YAML + ls + grep, NOT memo prose.

**M2 trajectory after G.5**: 2 → 1 (FINAL state; `phase4_2:254` A+D-preserved entry remains by design).

**Combined Cluster-G arc post-G.5 (projected FINAL)**: M1 5→0 (FINAL since G.1) · M2 28→1 across 5 sub-sprints (32 site closures; 1 A+D-preserved entry remains by design).

**Next dispatch after G.5 fix (per user autonomous queue item 5)**: **Cluster-G arc retrospective** (mirrors `CLUSTER_F_RETROSPECTIVE.md` shape; documents trajectory + banked lessons #5+#6 + pattern uniformity 25 files + 10 sub-sprints + invariant ladder evolution + future-arc applicability for Cluster-C + LLM_MODELS_REFRESH).

---

## §8 — Discipline notes

- **READ-ONLY scope honoured**: 0 LOC mutated outside this memo file
- **Canonical spec cited on line 1**: explicit cite of `P5_7_FIX_SCOPE_CLUSTER_G.md §1.5` + cross-references to G.4 fix + Cluster-F retrospective + invariant origin
- **F.3-ADVANCE memo-order slip lesson APPLIED**: DEV_PIPELINE.md §9 row authored BEFORE this memo file
- **F.5 YAML-edit slip lesson N/A**: no YAML edits this dispatch (advance scan is READ-ONLY)
- **G.1 slice-poll-cadence-mismatch lesson N/A**: no proving slice runs in scope; baseline pytest runs ~3.7s well under foreground timeout
- **G.3-VERIFICATION AST-over-grep lesson APPLIED**: AST scan used for site identification + product API surface check; grep used only for explicit string presence (`pytestmark` / `@pytest.mark.skip`) where AST is overkill; no fragile greps for invariant validation
- **NEW G.4-ADVANCE UNQUARANTINED-runtime-PASS-baseline lesson APPLIED**: 34/34 PASS in 3.71s captured at advance scan; will be required as proving-slice Row 1 in G.5 fix dispatch
- **NEW G.4-FIX file-name-from-YAML (lesson #6) APPLIED**: target file `test_synisense_surface_validation.py` + func `test_real_pipeline_run_rejects_bad_subsurface` + lineno 78 sourced via `yaml.safe_load` of grandfather YAML, NOT from memo prose (cross-validated by AST scan)
- **No testing subagent used** (per banned-list rule + user explicit ban)
- **No scope creep**: the 7 numbered sections + 1 discipline section is the exact deliverable; no extra audit, no extra files
- **No build steps executed**: advance scan is READ-ONLY by definition
- **HARD STOP** at memo surface; standing rules unchanged
- **Cluster-G arc continues** at G.5 fix dispatch boundary; storage arc remains PAUSED (no Azure creds delivered)
- **Single-vs-sequential dispatch shape**: N/A (single file, single site; inherently single-shape)

---

## §9 — User-direction surface (HARD STOP)

Per user autonomous mandate: **HARD STOP at memo surface; surface to user; G.5 fix dispatch can autonomously proceed at next dispatch boundary because all 4 escalation triggers (a/b/c/d) NOT TRIPPED.**

**G.5 advance scan milestone**:
- ✅ Target identified via YAML lookup (lesson #6 applied)
- ✅ UNQUARANTINED status verified (matches G.4 trio pattern; lesson #5 applies)
- ✅ Pre-conversion runtime PASS baseline captured (34/34 PASS in 3.71s)
- ✅ HYBRID 4-sync-preserved + 1-async-converted shape justified by PRODUCT API SURFACE (NOT a stylistic choice)
- ✅ Site shape locked: M2a bare under exception-raise context manager (matches G.4 solva_v2:125 pattern)
- ✅ Conversion shape locked (3 LOC additive: +1 decorator, 1 def→async def, 1 asyncio.run→await; inner `_runner` body PRESERVED verbatim)
- ✅ Sub-sprint shape decision: single G.5 (N/A — only 1 site; auto-locked single-shape)
- ✅ Locked-area sweep clean (Shield internals untouched; only test-side mutation planned)
- ✅ F.6 Shield-contract regression discipline-pay rows planned (3 mandatory; chat-surface real-Shield exercise covered INTERNALLY at G.5 Row 2 since L63 IS the real-Shield call)
- ✅ All 6 banked discipline-slip lessons applicability matrix documented
- ✅ Forward look: 13-row proving slice + M2 trajectory 2 → 1 FINAL
- ✅ 0 LOC mutated outside memo file

**Next dispatch** (autonomous per user run-to-close mandate): **`JC-POLLUTION-CLUSTER-G5-FIX`** — single-dispatch · 1 site conversion at L78 · 13-row proving slice · ~5 LOC est. diff (3 test conversion + 1 YAML delete + 1 ceiling ratchet).

After G.5 fix closes, **Cluster-G arc retrospective** (queue item 5) is the natural next step per user autonomous mandate.

Standing rules unchanged. Time-gate status: no active time-gate. Cluster-G arc continues; storage arc PAUSED awaiting Azure credentials.

End of memo.
