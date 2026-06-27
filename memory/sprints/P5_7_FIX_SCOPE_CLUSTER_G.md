**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (Cluster-G follow-up scope — Cluster-F arc closed at F.6; Cluster-G is the 12-file polluter surface discovered by `INVARIANT_NO_BESPOKE_RUN_HELPER`'s baseline AST scan that the Cluster-F scope memo §0 did not survey; this READ-ONLY scope memo enumerates per-file evidence and proposes sub-sprint grouping with advance-scan-default-on per Cluster-F retrospective §5.1 banked pattern · 0 LOC mutated outside this memo · HARD STOP at memo surface · AWAITING FIRST CLUSTER-G SUB-SPRINT DISPATCH)

# Sprint P5.7-FIX-SCOPE-CLUSTER-G — READ-ONLY scope memo for the 12-file polluter surface tagged `Cluster-G (post-F)` in YAML

**Status**: SHIPPED (memo only) · READ-ONLY · HARD STOP at memo surface · 0 LOC mutated outside this memo
**Date**: 2026-06-27
**Predecessor**: `sprints/CLUSTER_F_RETROSPECTIVE.md` (immediate predecessor — banked patterns including advance-scan-default-on rule + mechanical M1+M2 conversion pattern + sync-test preservation heuristic + closure-schedule lock pattern); `tests/invariants/bespoke_run_helper_grandfathered.yml` (per-site evidence canonical source)

---

## §0 — Per-file evidence table

All 12 file paths verified ON DISK. All M1/M2 sites verified at YAML-claimed line numbers (0 drift, 0 false positives). M1 helper shape uniformly canonical (`def _run(coro): return asyncio.get_event_loop().run_until_complete(coro)`) across all 5 M1 files. M2 sites span 4 sub-shapes catalogued in §0.1.

### §0.1 — M1 files (5 files / 5 helpers / module-level scope)

| # | File | LOC | Tests | M1 line | Motor I/O? | HTTP/FastAPI? | Shield? | Locked-area? |
|---:|---|---:|---:|---:|:---:|:---:|:---:|:---:|
| 1 | `tests/test_phase_p2_b2_rate_limits.py` | 149 | 6 | 24 | NO | NO | NO | clean |
| 2 | `tests/test_phase_p3_3_mfa.py` | 198 | 6 | 25 | YES | YES (12) | NO | clean |
| 3 | `tests/test_phase_p4_cohort_funnel.py` | 367 | 14 | 31 | YES | YES (2) | NO | clean |
| 4 | `tests/test_phase_p5_6_csrf_cookie_domain.py` | 136 | 4 | 42 | NO | YES (5) | NO | clean |
| 5 | `tests/test_phase_p5_corrections.py` | 223 | 7 | 24 | YES | YES (2) | NO | clean |
| | **Totals** | **1073** | **37** | | | | | |

**M1 pattern uniformity**: all 5 helpers verified by source-read to be the canonical Cluster-E/Cluster-F shape (`def _run(coro): return asyncio.get_event_loop().run_until_complete(coro)`). Mechanical conversion proven at 13 prior M1 sites in Cluster-F (F.1 + F.2 + F.4 + F.5 + F.3).

### §0.2 — M2 files (7 files / 25 sites / 23 class-method tests + 12 module-level tests)

| # | File | LOC | Tests | M2 site count | Test organization | Motor I/O? | Shield? | Locked-area? |
|---:|---|---:|---:|---:|---|:---:|:---:|:---:|
| 6 | `tests/test_iter39_briefings_objective_check.py` | 266 | 7 | 6 | class-based | YES | NO | clean |
| 7 | `tests/test_iter53_deep_tier_minutes.py` | 261 | 9 | 9 | class-based | YES | NO | clean |
| 8 | `tests/test_iter54_llm_spend_quota_inbound.py` | 306 | 7 | 4 | class-based | YES | NO | clean (LLM quota / virus scan endpoints) |
| 9 | `tests/test_phase12_2_surfaces.py` | 113 | 3 | 1 | module-level | NO | **YES** (`dryrun`) | Shield-adjacency |
| 10 | `tests/test_phase_a_synisense_unification.py` | 162 | 5 | 2 | module-level | NO | **YES** (`shield_payload_async`) | Shield-adjacency |
| 11 | `tests/test_solva_v2_llm_adapter.py` | 125 | 2 | 2 | module-level | NO | **YES** (`solva_v2.llm_adapter`) | Shield-adjacency |
| 12 | `tests/test_synisense_surface_validation.py` | 78 | 5 | 1 | module-level | NO | **YES** (`pipeline._is_valid_surface`) | Shield-adjacency (pure-Python helper) |
| | **Totals** | **1311** | **38** | **25** | | | | |

**M2 sub-shape catalogue (verified via per-site source-read)**:
- **M2a — bare `asyncio.run(coro())`** — Motor I/O wrapper (iter39 sites at L75/L174/L210/L227/L249/L266; iter53 sites at L86/L113/L128/L149/L166/L175/L220/L227/L235; iter54 sites at L126/L170/L257/L298)
- **M2b — `result = asyncio.run(coro())`** — captures return value (synisense_surface_validation L78, solva_v2_llm_adapter L81)
- **M2c — tuple-unpack `a, b = asyncio.run(coro())`** — captures tuple (phase_a L58: `redacted, shield_map = asyncio.run(_run())`)
- **M2d — `out = asyncio.run(dryrun(...))`** — Shield API call (phase12_2_surfaces L61, phase_a L96, solva_v2_llm_adapter L125)

All 4 sub-shapes convert mechanically to `await` form. The conversion semantics are identical to F.6's M2 shape (verified safe under Shield-adjacency at F.6 close).

### §0.3 — Aggregate totals across all 12 files

| Aggregate | Cluster-F (closed) | Cluster-G (this scope) | Notes |
|---|---:|---:|---|
| Total files | 14 | 12 | -14% smaller surface |
| M1 sites | 13 | 5 | All in single G.1 sub-sprint (uniform mechanism) |
| M2 sites | 2 | 25 | 12.5× more M2 sites (Cluster-G is M2-heavy) |
| Total tests | ~80 | 75 | Comparable |
| Class-based tests | 0 | 23 | **NEW pattern** in 3 iter files |
| Sync-fixture-in-test tests | 0 | likely ≥16 | **NEW risk** in 3 iter files (sync `session.get` inside async-converted tests) |
| Shield-touching files | 1 (F.6) | 4 | 4× more Shield-adjacency surface |
| Total LOC | ~2200 | 2384 | Comparable |
| Locked-area touches | 1 (F.6) | 4 (Shield-adjacency M2 quartet) | 4× more advance-scan candidates |

---

## §1 — Sub-sprint grouping proposal (5 sub-sprints)

Heuristic applied (per Cluster-F precedent): group by mechanism uniformity + test-count proximity + risk class. Advance-scan-default-on per Cluster-F retrospective §5.1.

### G.1 — M1 batch (5 files / 37 sync tests / 5 sites) · **LOW risk · NO advance scan**

Files: rate_limits + mfa + cohort_funnel + csrf_cookie_domain + corrections.

Rationale for batching all 5 M1 files into single sub-sprint:
- Mechanism 100% uniform (all 5 helpers verified canonical Cluster-E/Cluster-F shape)
- Pattern proven at 13 prior M1 sites across F.1 + F.2 + F.4 + F.5 + F.3 (5 prior sub-sprints, 100% success)
- Zero locked-area surface across all 5 files (no Shield / WS Doc / Track-2 / Monitor pre-warmer / OAuth in test bodies)
- LOW risk classification holds without advance scan (uniform mechanism + zero locked-area)

**Opt-out criteria for advance scan SATISFIED** (single-pattern + zero locked-area + 5 files share identical canonical helper shape).

Expected outcome: 5 M1 entries removed from YAML; `M1_CEILING` ratchets 5 → 0; proving slice modeled on F.3's 13-row template scaled to 5 files (~14-15 rows including isolation per file + paired-with-autosave per file + combined + log scan + source-assertion + closure-lock invariant).

### G.2 — M2 class-based iter pair (2 files: iter39 + iter53 / 16 class-method tests / 15 M2 sites) · **MEDIUM risk · ADVANCE-SCAN-DEFAULT-ON**

Files: `test_iter39_briefings_objective_check.py` + `test_iter53_deep_tier_minutes.py`.

Rationale for batching iter39+iter53 (not iter54 which goes to G.3):
- Both files are class-based (`class TestX: def test_y(self, session):`) — NEW conversion shape vs Cluster-F
- Both use `session` fixture (sync requests-style HTTP client) inline within tests that ALSO have `asyncio.run(...)` wrapping Motor coroutines
- Test counts comparable (7 + 9 = 16); M2 site counts comparable (6 + 9 = 15)
- iter54 has only 4 M2 sites + adds virus-scanning + LLM-spend endpoint surface (different test subject) — separate sub-sprint G.3 for clean attribution

**Why advance scan**: the sync `session.get(...)` blocking inside an async-converted test is a NEW conversion property. Advance scan READ-ONLY source-reads will verify:
- (a) Whether the sync `session.get(...)` calls have any blocking-sensitive assertions (timeouts, deadlock detection)
- (b) Whether the class fixture wiring works under `@pytest.mark.asyncio` on the method (pytest-asyncio supports it but the `session` fixture's scope matters)
- (c) Whether the async coroutine helpers being wrapped (`_clear`, `_reset_quota`, `_check`) have any cross-test state binding

Expected outcome: 15 M2 entries removed; `M2_CEILING` ratchets 26 → 11.

### G.3 — M2 class-based iter54 (1 file / 7 tests / 4 M2 sites) · **MEDIUM risk · ADVANCE-SCAN-DEFAULT-ON**

File: `test_iter54_llm_spend_quota_inbound.py`.

Rationale for separating from G.2:
- Different test subject (LLM spend quota + inbound virus rejection vs iter39/53's briefings + deep tier minutes)
- Different surface area (admin LLM quota endpoint + inbound email pipeline with virus scan vs briefings + minute-quota endpoints)
- Cleaner attribution: G.2 closes if iter39+iter53 converted cleanly; G.3 closes if iter54 converts cleanly
- Same class-based pattern + sync-`session` risk as G.2; advance scan same shape

**Why advance scan**: same as G.2 (class-based + sync `session` interaction). Also: virus-rejection test (`test_eicar_attachment_rejected_and_audited`) has 2 M2 sites — advance scan verifies the EICAR pipeline coroutine shape is conversion-safe.

Expected outcome: 4 M2 entries removed; `M2_CEILING` ratchets 11 → 7.

### G.4 — Shield-adjacency M2 trio (3 files / 12 tests / 5 M2 sites) · **HIGH risk · ADVANCE-SCAN-DEFAULT-ON (TWO-DISPATCH per F.6 precedent)**

Files: `test_phase12_2_surfaces.py` (1 M2) + `test_phase_a_synisense_unification.py` (2 M2) + `test_solva_v2_llm_adapter.py` (2 M2).

Rationale for batching as Shield-adjacency trio:
- All 3 touch Shield API surface (`dryrun`, `shield_payload_async`, `llm_adapter`) — F.6 precedent applies
- Module-level tests (no class-based complication)
- Single Shield-touching M2 sub-shape per file: M2d (Shield-call form)
- F.6 (1 file / 2 M2 sites · Shield-adjacency) reclassified from HIGH→LOW under advance scan; same precedent should apply to G.4 but with 3× the Shield-API touch surface

**Why advance scan + TWO-DISPATCH per F.6 precedent**: Shield-adjacency is the load-bearing risk-arming condition from the Cluster-F scope memo §6. F.6 proved that surface-area HIGH → source-read LOW is achievable but required the discipline-pay of a per-test Shield-contract regression check at proving-slice close (Row 11 of F.6's slice). G.4 will need the same discipline-pay — likely Row N of slice = AST-level verification that the converted tests STILL invoke `shield_payload_async` / `dryrun` / `llm_adapter` with the same args AND STILL assert on the same Shield-contract properties (no leaky-key drift, no mode-arg drift).

**Sub-sub-grouping consideration (open question for user dispatch)**: should G.4 be a single sub-sprint (3 files together) or 3 sequential sub-sprints (G.4a / G.4b / G.4c)? Argument for single: same mechanical conversion, same advance-scan shape, 3-file batch matches F.5's 3-file scope. Argument for sequential: Shield-adjacency requires per-file Shield-contract preservation evidence, sequential gives cleaner attribution per file. **Surfacing for user direction at dispatch time.**

Expected outcome: 5 M2 entries removed; `M2_CEILING` ratchets 7 → 2.

### G.5 — Shield-adjacency M2 outlier (1 file / 5 tests / 1 M2 site) · **LOW-MEDIUM risk · ADVANCE-SCAN**

File: `test_synisense_surface_validation.py`.

Rationale for separating from G.4:
- Only 1 M2 site (vs G.4's 5)
- Imports `pipeline._is_valid_surface` and `_VALID_SURFACES` — **pure-Python helper internals**, NOT the Shield API surface (`pipeline_run`)
- 5 tests total; 4 of them are pure-Python helper tests on `_is_valid_surface` — these likely STAY SYNC under conversion per Cluster-F.2 sync-preservation heuristic
- The single M2 site (`test_real_pipeline_run_rejects_bad_subsurface` at L78) calls real `pipeline_run` — Shield-API touch
- So G.5 is a HYBRID: 4 sync-preserved + 1 async-converted

**Why advance scan**: confirm the sync-preservation heuristic applies to the 4 helper tests (no Motor I/O, no async surface in their bodies). Also: validate the 1 M2 site's Shield-contract regression — same shape as G.4 but for `pipeline_run` rejection logic.

Expected outcome: 1 M2 entry removed; `M2_CEILING` ratchets 2 → 1 (final state: A+D-preserved entry remains by design as an intentional exemption).

---

## §2 — Locked-area aggregate scan

| File | Shield | WS Doc UI | Track-2 schema | Monitor pre-warmer | OAuth provider | Verdict |
|---|:---:|:---:|:---:|:---:|:---:|---|
| rate_limits (G.1) | NO | NO | NO | NO | NO | CLEAN |
| mfa (G.1) | NO | NO | NO | NO | NO | CLEAN |
| cohort_funnel (G.1) | NO | NO | NO | NO | NO | CLEAN |
| csrf_cookie_domain (G.1) | NO | NO | NO | NO | NO | CLEAN |
| corrections (G.1) | NO | NO | NO | NO | NO | CLEAN |
| iter39_briefings (G.2) | NO | NO | NO | NO | NO | CLEAN (Motor + briefings endpoint) |
| iter53_deep_tier (G.2) | NO | NO | NO | NO | NO | CLEAN (LLM quota endpoint) |
| iter54_llm_spend (G.3) | NO | NO | NO | NO | NO | CLEAN (LLM quota + inbound email + virus scan) |
| phase12_2_surfaces (G.4) | **YES** (`dryrun`) | NO | NO | NO | NO | Shield-adjacency · TWO-DISPATCH |
| phase_a_synisense (G.4) | **YES** (`shield_payload_async`) | NO | NO | NO | NO | Shield-adjacency · TWO-DISPATCH |
| solva_v2_llm_adapter (G.4) | **YES** (`llm_adapter`) | NO | NO | NO | NO | Shield-adjacency · TWO-DISPATCH |
| synisense_surface_validation (G.5) | **YES** (`pipeline._is_valid_surface` — pure helper) | NO | NO | NO | NO | Shield-adjacency (helper, not API) · ADVANCE-SCAN |

Production-code touch surface: **NONE** in any test body across all 12 files. Tests exercise Shield API surfaces or import production helpers but do NOT modify Shield CODE. Same posture as F.6 — conversion changes test invocation only.

---

## §3 — Latent-flake risk class

Files with `_run` / `asyncio.run` on Motor-touching coroutines (the canonical wrong-loop-binding landmine):

| Risk class | Files | Mechanism |
|---|---|---|
| HIGH (Motor + sync `_run`) | mfa, cohort_funnel, corrections | Same mechanism as Cluster-F polluters that caused FTT-024..026; converting closes the landmine. |
| MEDIUM (Motor coroutines via `asyncio.run(...)` inside class-method tests) | iter39, iter53, iter54 | M2 wraps Motor I/O helpers (`_clear`, `_reset_quota`, `_check`, `_send_inbound`) — wrong-loop-binding propagates the same way. |
| LOW (Shield API surface only, no Motor) | phase12_2_surfaces, phase_a, solva_v2_llm_adapter, synisense_surface_validation | No Motor I/O; the M2 sites wrap pure async Shield calls. Wrong-loop-binding risk is lower but still present if any Shield-internal state binds to the wrong loop. |
| ZERO (no Motor, no Shield) | rate_limits, csrf_cookie_domain | Pure middleware/header tests. M1 helper is still a polluter (binds policy loop) but no Motor downstream effect. |

**Implication for downstream pollution**: HIGH-risk-class files (mfa, cohort_funnel, corrections, iter39, iter53, iter54) are the actual continuing source of cross-test pollution of `autosave` and any other Motor-using async test. Closing these closes the cross-test pollution surface entirely (autosave's pollution set was emptied by Cluster-F arc; Cluster-G HIGH-risk-class closure ensures it stays empty).

---

## §4 — Advance-scan-default-on rule for Cluster-G sub-sprints

Per Cluster-F retrospective §5.1 banked pattern:

| Sub-sprint | Advance scan? | Opt-out rationale |
|---|:---:|---|
| G.1 | **NO** | Single-pattern (all 5 M1 helpers canonical Cluster-E shape) + zero locked-area + 5-file batch within single mechanical class |
| G.2 | **YES** | Class-based test organization (NEW pattern) + sync `session` fixture interaction (NEW risk); advance scan validates conversion shape before fix dispatch |
| G.3 | **YES** | Same class-based + sync `session` interaction as G.2; advance scan also validates virus-scan + LLM-spend endpoint coroutine shape |
| G.4 | **YES** + TWO-DISPATCH | Shield-adjacency at 3 files; F.6 precedent applies (HIGH → LOW reclassification possible but Shield-contract regression discipline-pay required at slice close) |
| G.5 | **YES** | Shield-adjacency at 1 file + HYBRID async/sync conversion (4 sync-preserved + 1 async-converted); advance scan confirms the sync-preservation heuristic applies |

**G.1 is the only sub-sprint with explicit advance-scan opt-out.** All other sub-sprints default to advance-scan-on per the banked rule. Advance-scan memos will be ~280-400 LOC each (similar to F.6-ADVANCE).

---

## §5 — Estimated total Cluster-G LOC

| Component | LOC | Notes |
|---|---:|---|
| G.1 test-file deltas | ~60 | 5 files × ~12 LOC delta (import drops + helper drops + `@pytest.mark.asyncio + async def` decorators on 37 tests) |
| G.2 test-file deltas | ~40 | 2 files × ~20 LOC delta (class-method async decorator + 15 M2 sites converted) |
| G.3 test-file deltas | ~15 | 1 file × ~15 LOC delta (class-method async decorator + 4 M2 sites converted) |
| G.4 test-file deltas | ~25 | 3 files × ~8 LOC delta (5 M2 sites total + `@pytest.mark.asyncio + async def` decorators on 5 tests touching M2) |
| G.5 test-file deltas | ~10 | 1 file × ~10 LOC delta (1 M2 site + 1 test decorator; 4 sync tests preserved) |
| **Test-file total** | **~150** | |
| 5 proving slices @ ~200 LOC each | ~1000 | G.1 ~250 (multi-file isolation), G.2-G.5 ~150-200 each |
| 5 sprint memos @ ~250 LOC each | ~1250 | |
| 4 advance-scan memos @ ~300 LOC each (G.2-G.5) | ~1200 | |
| Invariant YAML/ceiling edits | ~15 | Per-sub-sprint YAML entry removal + ceiling ratchet |
| **Total Cluster-G estimate** | **~3615 LOC** | Vs Cluster-F's ~2920 LOC; +24% due to advance-scan-default-on overhead (4 advance scans vs Cluster-F's 2) |

---

## §6 — Closure-schedule trajectory

`M1_CEILING` (currently 5):
- G.1 close: 5 → 0 (all 5 M1 files closed in single sub-sprint — uniform-mechanism opt-out from advance scan)
- G.2-G.5: 0 → 0 (no M1 in these sub-sprints)
- **Final: M1_CEILING = 0** (no remaining M1 polluters anywhere)

`M2_CEILING` (currently 26, of which 1 is A+D-preserved by design):
- G.1: 26 → 26 (no M2 in G.1)
- G.2 close: 26 → 11 (-15 sites across iter39 + iter53)
- G.3 close: 11 → 7 (-4 sites in iter54)
- G.4 close: 7 → 2 (-5 sites across phase12_2 + phase_a + solva_v2_llm_adapter)
- G.5 close: 2 → 1 (-1 site in synisense_surface_validation)
- **Final: M2_CEILING = 1** (A+D-preserved entry remains as intentional exemption per YAML tag "A+D fix preserves this asyncio.run with snapshot/restore")

At Cluster-G arc close, the bespoke-`_run`/`asyncio.run` polluter surface is **0 M1 + 0 fixable M2 + 1 intentional preserved exemption** = effectively clean. The invariant catcher + drift detector + count-ceiling enforce this floor in perpetuity.

---

## §7 — HALT-and-surface conditions reviewed

Per user dispatch:

1. **Source-read reveals already-converted file**: NO — all 12 files verified with M1/M2 patterns present at YAML-claimed line numbers. Zero false positives.
2. **Source-read reveals file in locked area that we can't touch even with advance-scan discipline**: NO — 4 Shield-adjacency files touch Shield API SURFACE but not Shield CODE (same posture as F.6). Production-code touch = 0 across all 12 files.
3. **Source-read reveals additional polluter files NOT in `Cluster-G (post-F)` YAML tag**: NO — verified by re-running inventory slice at scope-memo-author start; `drift_report` clean; YAML matches live tree; no Cluster-H discovery.
4. **Memo exceeds ~400 LOC**: this memo is ~280 LOC (Cluster-F scope memo was ~230 LOC for 14 files; Cluster-G is ~280 LOC for 12 files due to NEW pattern surfacing — class-based + sync-fixture-in-async-test). Within budget.
5. **File path mismatches between YAML tag and disk**: NO — all 12 file paths exact match on disk. No correction needed.

**NO HALT conditions tripped.** Cluster-G dispatch-ready.

---

## §8 — Open question surfaced for user direction at dispatch

**G.4 Shield-adjacency trio — single sub-sprint or sequential G.4a/G.4b/G.4c?**

- **Argument for single** (3 files together): same mechanical M2 conversion, same advance-scan shape, 3-file batch matches F.5's proven 3-file scope.
- **Argument for sequential** (3 separate sub-sprints): Shield-adjacency requires per-file Shield-contract preservation evidence; sequential gives cleaner attribution + each sub-sprint's proving slice has a tighter Row N Shield-contract regression scope.

Surfacing for user direction at G.4 dispatch time. Default if no user direction: single sub-sprint per F.5/F.3 precedent.

---

## §9 — Discipline notes

- **Scope honoured**: READ-ONLY contract — 0 LOC mutated outside this memo file.
- **No testing subagent used** (per banned-list rule).
- **Source-read evidence verified** against on-disk files + YAML line numbers + inventory slice output (3/3 GREEN at scope-memo-author start: M1=5/5, M2=26/26, zero drift).
- **DEV_PIPELINE.md §9 row added BEFORE memo authoring** per F.3-ADVANCE-slip lesson.
- **Canonical spec on line 1** — anchored on `FAILING_TEST_TRACKER.md` (the next-most-canonical document post-Cluster-F arc closure; Cluster-F scope memo's `P5_7_FIX_SCOPE_CLUSTER_F.md` is the closed predecessor anchor).
- **NEW patterns surfaced honestly**: class-based test organization (3 files) + sync `session.get` inside async-converted tests (3 files) — both NEW vs Cluster-F. Surfaced as MEDIUM-risk classification rather than absorbing into mechanical pattern.
- **G.4 open question surfaced** rather than silently chosen (single vs sequential sub-sprint for Shield-adjacency trio).

---

## §10 — User-direction surface (HARD STOP per dispatch)

Cluster-G scope memo complete. 5 sub-sprints proposed: G.1 (M1 batch, LOW, no advance scan) + G.2 (M2 iter pair, MEDIUM, advance-scan) + G.3 (M2 iter54, MEDIUM, advance-scan) + G.4 (Shield-adjacency trio, HIGH, advance-scan + TWO-DISPATCH) + G.5 (Shield-adjacency outlier, LOW-MEDIUM, advance-scan).

Awaiting next dispatch from user. Recommended sequencing: G.1 → G.2 → G.3 → G.4 → G.5 (uniform mechanism first, NEW-pattern risks second, Shield-adjacency last) but any ordering works.

Standing rules unchanged. Time-gate status: no active time-gate (all Cluster-F arc time-gates closed at the F.6 dispatch).
