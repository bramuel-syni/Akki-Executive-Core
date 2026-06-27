**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (Cluster-F closes 14 existing polluters using this anti-pattern; this invariant prevents the anti-pattern from re-introducing itself in NEW test files going forward AND tracks closure of existing polluter files; shipped as Step 4.5 of the 2026-06-27 batch dispatch)

# Sprint INVARIANT_NO_BESPOKE_RUN_HELPER — structural enforcement of the Cluster-F mechanical pattern

**Status**: SHIPPED · proving slice **10/10 GREEN** · regression-check ladder GREEN · HARD STOP at slice close
**Date**: 2026-06-27
**Predecessor**: `sprints/INVARIANT_NO_THIN_ASSERTIONS.md` (mirrors the two-tier-exemption pattern · file-based grandfather YAML + in-source marker); `sprints/JC_POLLUTION_CLUSTER_F1_FIX.md` (immediate predecessor — F.1 sub-sprint closed 2 polluters mechanically)

---

## §0 — Outcome at a glance

| Anti-pattern | Detection | Baseline count | Ceiling |
|---|---|---:|---:|
| **M1** — module-level `def _run(coro): return asyncio.get_event_loop().run_until_complete(coro)` helper | AST: `FunctionDef name=='_run'` with `Call(attr='run_until_complete')` on `Call(attr='get_event_loop')` of `Name('asyncio')` | **13 files** | M1_CEILING = 13 |
| **M2** — `asyncio.run(...)` direct call inside `test_*` function body | AST: `Call(func=Attribute(attr='run', value=Name('asyncio')))` within `FunctionDef name.startswith('test_')` | **28 sites across 10 files** | M2_CEILING = 28 |

**Net**: structural enforcement of the Cluster-E + Cluster-F closure trajectory. New test files cannot introduce either anti-pattern without explicit allowlist (YAML grandfather entry OR in-source `@pytest.mark.acceptable_bespoke_run` + `# reason:` comment). Existing sites are tagged with their target sub-sprint so the closure schedule is machine-readable.

**Discovery finding** (load-bearing, surfaced in §3): the Cluster-F scope memo §0 surveyed 14 files. This invariant's baseline scan surfaced 23 distinct files — **9 MORE** than the scope memo identified. 5 newly-discovered M1 files + 4 newly-discovered M2 files (counting `test_phase4_2_http_transport_smoke.py` separately since it's already A+D-fixed in-place) need a "Cluster-G (post-F)" follow-up dispatch.

---

## §1 — What shipped

### §1.1 — `tests/invariants/test_no_bespoke_run_helper.py` (NEW, ~340 LOC)

Three invariant functions:

1. **`test_no_bespoke_run_helper_in_tests`** — the catcher. Walks every `test_*.py` file under `backend/tests/` (excluding the `invariants/` subdirectory). For each file, AST-classifies M1 and M2 sites. Skips entries that match the grandfather YAML OR have the in-source marker + `# reason:` comment. Any remaining hit FAILS the build with a clear pointer to the three resolution options (convert to async / add YAML entry / add marker).

2. **`test_grandfather_list_does_not_drift`** — the drift detector. Reads the YAML, scans the live tree, and FAILS if any YAML entry no longer matches a real anti-pattern site. Prevents stale entries from accumulating — when a Cluster-F sub-sprint closes a file, the YAML entry MUST be removed in the same commit, else this test fails.

3. **`test_grandfather_count_below_ceiling`** — the ceiling. `M1_CEILING = 13`, `M2_CEILING = 28`. FAILS if either count grows. The ceiling LOCKS the trajectory: as Cluster-F sub-sprints ship, both counts trend DOWN (each closed file = YAML entry removed = count drops by 1). Never up.

### §1.2 — `tests/invariants/bespoke_run_helper_grandfathered.yml` (NEW, ~240 LOC YAML)

- 13 M1 entries — 8 in current Cluster-F scope (F.3 × 3 + F.4 × 2 + F.5 × 3), 5 in "Cluster-G (post-F)" follow-up bucket
- 28 M2 entries — 2 in F.6 (synisense_security), 1 marked "A+D fix preserves this" (test_phase4_2_http_transport_smoke.py:254 — wrapped by env+loop-policy snapshot/restore), 25 in "Cluster-G (post-F)" follow-up bucket

Each entry carries: `file`, `lineno`, `cluster_f_sub_sprint` (closure target), `reason` (free-text or sub-sprint tag). M2 entries also carry `func`.

### §1.3 — Locked-area re-confirmation

| Area | Touched? |
|---|---|
| Shield surfaces | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| Product code (`server.py`, `core.py`, `contracts/`) | NO |
| Other test files | NO |
| Other invariant files | NO (the thin-assertion ceiling fix is in a separate memo) |

Cleared. The bespoke-run invariant is a NEW file + a NEW YAML; no other file mutated.

---

## §2 — Proving slice (`backend/scripts/jc_invariant_bespoke_run_helper_slice.py`)

```
============================================================================
INVARIANT-NO-BESPOKE-RUN-HELPER Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
============================================================================
  Row  1  GREEN  baseline YAML has 13 M1 + 28 M2 entries
            m1_count=13  m2_count=28
  Row  2  GREEN  bespoke-run guard PASSES at baseline (everything grandfathered)
            1 passed, 21 warnings in 5.70s
  Row  3  GREEN  drift detector PASSES at baseline (no stale entries)
            1 passed, 21 warnings in 4.92s
  Row  4  GREEN  count-ceiling PASSES at baseline (M1=13<=13, M2=28<=28)
            1 passed, 21 warnings in 3.77s
  Row  5  GREEN  NEGATIVE M1 probe: inject new _run helper → invariant FAILS
            1 failed, 21 warnings in 5.31s
  Row  6  GREEN  NEGATIVE M2 probe: inject new asyncio.run → invariant FAILS
            1 failed, 21 warnings in 5.04s
  Row  7  GREEN  MARKER probe: M2 site + `acceptable_bespoke_run` marker → PASS
            1 passed, 21 warnings in 4.92s
  Row  8  GREEN  DRIFT probe: stale YAML entry → drift detector FAILS
            1 failed, 21 warnings in 4.94s
  Row  9  GREEN  thin-assertion count-ceiling PASSES (9 ≤ 10)
            1 passed, 21 warnings in 3.78s
  Row 10  GREEN  thin-assertion ceiling probe: lower ceiling to 8 → FAILS
            1 failed, 21 warnings in 3.79s
============================================================================
RESULT  10/10 GREEN
============================================================================
```

**Key signals**:
- **Rows 5-6 (NEGATIVE probes)**: temp test files injected with each anti-pattern → invariant FAILS as designed. Cleanup deletes the probe file after assertion. End-to-end catch confirmed.
- **Row 7 (MARKER probe)**: same M2 inject + `@pytest.mark.acceptable_bespoke_run` + `# reason:` comment → invariant PASSES. Confirms the in-source marker exemption works end-to-end.
- **Row 8 (DRIFT probe)**: stale YAML entry pointing at a non-existent test file → drift detector FAILS. Confirms the audit trail can't accumulate dead weight.
- **Rows 9-10 (thin-assertion ceiling)**: cross-checks the Step 4 fix (separate memo) lands cleanly — the new `test_grandfather_count_below_ceiling` in `test_no_thin_assertions.py` works on its 10-entry ceiling.

---

## §3 — Discovery finding (load-bearing)

The Cluster-F scope memo §0 surveyed 14 files (13 M1 + 1 M2). This invariant's baseline scan surfaced **23 distinct files** carrying the anti-patterns. Gap:

| Pattern | Scope memo §0 | Live scan | Delta |
|---|---:|---:|---:|
| M1 (`_run` helper) | 13 files | 13 files (5 already converted by F.2 + F.1; **5 EXTRAS** not in scope memo) | +5 unsurfaced |
| M2 (`asyncio.run` in test body) | 1 file (synisense_security) | 10 files (28 sites) | +9 unsurfaced |
| Total distinct files | 14 | 23 | **+9** |

**Newly discovered M1 files** (need a "Cluster-G (post-F)" dispatch):
1. `test_phase_p2_b2_rate_limits.py`
2. `test_phase_p3_3_mfa.py`
3. `test_phase_p4_cohort_funnel.py`
4. `test_phase_p5_6_csrf_cookie_domain.py`
5. `test_phase_p5_corrections.py`

**Newly discovered M2 files** (need a "Cluster-G (post-F)" dispatch — but each needs per-file analysis to determine if conversion is viable or if the `asyncio.run` is genuinely justified):
1. `test_iter39_briefings_objective_check.py` (6 sites)
2. `test_iter53_deep_tier_minutes.py` (9 sites)
3. `test_iter54_llm_spend_quota_inbound.py` (4 sites)
4. `test_phase12_2_surfaces.py` (1 site)
5. `test_phase_a_synisense_unification.py` (2 sites)
6. `test_solva_v2_llm_adapter.py` (2 sites)
7. `test_synisense_surface_validation.py` (1 site)

**One M2 site is pre-acknowledged**: `test_phase4_2_http_transport_smoke.py:254` — the A+D fix sprint preserved this `asyncio.run` call and wrapped it with env + asyncio-loop-policy snapshot/restore. That site is structurally safe under current shape but still appears in the baseline because the AST is pattern-matching on the call itself, not its surrounding guards. Tagged in the YAML as "A+D fix preserves this asyncio.run with snapshot/restore" for honest accounting.

**Implication**: the Cluster-F scope was 14/23 ≈ 61% of the true polluter surface. Closing all 6 Cluster-F sub-sprints will resolve 9 M1 + 2 M2 = 11/23 files (47%). The remaining 12 files / 26 sites need a "Cluster-G" dispatch.

**Recommendation surfaced for user direction**: do NOT expand Cluster-F scope mid-flight (sub-sprints are designed and locked). After F.6 closes, dispatch a "Cluster-G" survey memo (READ-ONLY, similar shape to `P5_7_FIX_SCOPE_CLUSTER_F.md`) to characterize each Cluster-G file's structural shape and recommend a sub-sprint grouping.

---

## §4 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **92 pass / 7 pre-existing failures** | Was 88 PASS pre-Step 4; +4 new = 3 bespoke-run tests + 1 thin-assertion ceiling. SAME 7 pre-existing failures unchanged. Pattern: `enforce_mode_zero_violations` + `polymorphic_response_ratchet` × 2 + `sdk_slices` + `tenancy_enforce_mode_for_migrated_collections` + `tenancy_escape_hatch_allowlist` × 2. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via `test_phase4_4_dual_mount_smoke.py` 37/37 PASS — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` all in lockstep |
| JC-TM email path smoke | yes | **N/A** | No SendGrid/email-path code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Cluster's own proving slice | yes (10/10) | **10/10 GREEN** |

---

## §5 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/invariants/test_no_bespoke_run_helper.py` | NEW | 340 LOC — 3 invariant functions (catcher + drift + ceiling) + AST classifier helpers |
| `tests/invariants/bespoke_run_helper_grandfathered.yml` | NEW | ~240 LOC YAML — 13 M1 + 28 M2 grandfathered entries with sub-sprint tags |
| `backend/scripts/jc_invariant_bespoke_run_helper_slice.py` | NEW | 225 LOC — 10-row slice with NEGATIVE / MARKER / DRIFT probes (all auto-cleanup) |
| `memory/sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added (combined with INVARIANT_GRANDFATHER_CEILING) |

**Files NOT touched**: any product code, any non-invariant test file, any fixture file, any other invariant file. (The companion Step 4 thin-assertion ceiling fix is in a separate sprint memo `INVARIANT_GRANDFATHER_CEILING.md` for clean audit-trail separation; both ship together in this 2026-06-27 batch.)

---

## §6 — Discipline notes

- **Scope honoured**: Step 4.5 directive exactly — additive invariant, mirrors thin-assertion shape, prevents Cluster-F anti-pattern re-introduction.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 10/10 GREEN** — HARD STOP at slice close.
- **Locked-area check** done — clear.
- **No production code changes** — entirely invariant + YAML + slice + memo.
- **Discovery surfaced**: scope-memo-vs-reality gap reported as load-bearing finding (§3). 9 additional polluter files identified. "Cluster-G (post-F)" dispatch recommended after F.6 closes.
- **Drift detector is the closure-discipline lock**: when F.3-F.6 sub-sprints ship, they MUST remove their YAML entries simultaneously. Forgetting fails the drift detector. Closure schedule is now machine-enforced.

---

## §7 — User-direction surface (HARD STOP per Step 4 + 4.5 batch directive)

Both invariants ship together. Next dispatch (per locked sequence):
- **Step 5** Cluster-F F.4 dispatch (bounce_webhook + waitlist_reminder) — 2 M1 files, ~13 sync tests
- After F.4 → F.5 → F.3 → F.6 → Cluster C
- **Steps 2 + 3** auto-fire when `date -u` ≥ `Sat Jun 27 09:12:00 UTC 2026` (GridFS backfill + FTT-014 re-run)
- **Cluster-G dispatch** recommended after F.6 closes (9 additional files surfaced by this slice's baseline scan)

Standing rules unchanged.
