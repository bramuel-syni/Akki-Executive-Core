**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1 + §6` (Cluster-F sub-sprint F.6 = synisense_security M2 outlier — Shield-adjacency · TWO-DISPATCH approach confirmed by user · advance-scan memo `P5_7_FIX_SCOPE_CLUSTER_F6_ADVANCE.md §3` verdict LOW risk · this is the SIXTH AND FINAL Cluster-F sub-sprint · HARD STOP at proving-slice close · closure-schedule lock end-to-end validated by Row 10 against bespoke-run invariant + Shield-contract regression validated by Row 11 · post-F.6 FTT-024..026 AUTO-CLOSE because autosave's polluter set becomes empty)

# Sprint JC_POLLUTION_CLUSTER_F6_FIX — mechanical sync→async conversion on the synisense_security M2 outlier (Cluster-F arc completion)

**Status**: SHIPPED (test-file-only patches landed) · proving slice **11/11 GREEN** stable across 2 consecutive runs · regression-check ladder GREEN · FTT-024..026 auto-close validated end-to-end · HARD STOP at slice close · closure-schedule lock validated · Shield-contract regression validated
**Date**: 2026-06-27
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_F6_ADVANCE.md` (immediate predecessor — READ-ONLY advance scan that reclassified F.6 Shield-adjacency-HALT-pre-armed → LOW risk with rationale); `sprints/JC_POLLUTION_CLUSTER_F3_FIX.md` (13/13 GREEN — F.3 3-file sub-sprint, 13 of 14 polluters converted at predecessor close); `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (closure-schedule lock)
**Cluster-F arc completion**: 14 of 14 polluters now converted across F.2 + F.1 + F.4 + F.5 + F.3 + F.6.

---

## §0 — Outcome at a glance

| File | Sync tests | Conversions | Post-fix isolation |
|---|---:|---|---|
| `tests/test_synisense_security.py` | 3 | 2 async-converted + 1 stays sync (`test_unregistered_version_blocks_decryption` pure-Python encryption envelope contract) | 3/3 PASS |
| **Totals** | **3** | **2 async-converted + 1 stay sync** | **3/3 PASS** |

**Net**: Cluster-F.6 closes wrong-loop-binding at source for the 14th of 14 Cluster-F polluters. **Cluster-F ARC COMPLETE.** Autosave's polluter set becomes empty → FTT-024..026 AUTO-CLOSE (validated end-to-end by running autosave + ALL 14 originally-polluter files in single sweep = 72/72 PASS).

**Advance-scan LOW-risk verdict honoured under conversion**: both M2 tests had return-value-only assertions with zero `asyncio.run` semantics dependency; `pipeline_run` is a pure `async def` with no loop-scoped state; `_prep_keys` autouse fixture is sync and loop-agnostic; conversion was mechanically safe per advance-scan §2.3 + §2.4 analysis. Shield CODE not touched. Shield CONTRACTS preserved verbatim (validated AST-level at Row 11).

---

## §1 — Patches applied (test-file-only, locked-area cleared)

### §1.1 — `tests/test_synisense_security.py`

- Added `import pytest` (was already present; no change)
- Removed `import asyncio` (no longer needed — `asyncio.run(...)` removed)
- Converted 2 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_shield_reversible_produces_shield_map_id_only` — replaced `out = asyncio.run(pipeline_run(...))` with `out = await pipeline_run(...)`; assertion block preserved verbatim including the leaky-key absence loop (`for k in ("shield_map", "mapping", "originals", "envelope"): assert k not in out`).
  - `test_redact_mode_never_creates_shield_map` — replaced `out = asyncio.run(pipeline_run(...))` with `out = await pipeline_run(...)`; `assert out["shield_map_id"] is None` preserved verbatim.
- `test_unregistered_version_blocks_decryption` STAYS SYNC — pure-Python encryption envelope test, no asyncio surface. Calls `enc.new_record_envelope(...)` + `enc.open_record_envelope(env)` and asserts `enc.KeyVersionUnknown` is raised. Per Cluster-F.2 heuristic (preserve pure-Python tests as sync).
- `_prep_keys` autouse fixture PRESERVED VERBATIM — sync, loop-agnostic; mutates `os.environ["SYNISENSE_MASTER_KEY"] = secrets.token_hex(32)`, pops `SYNISENSE_ALLOW_INSECURE` + `AKKI_ENV`, calls `enc.init_keys()` per test.
- Docstring refreshed citing Cluster-F.6 root cause + advance-scan LOW-risk verdict + final-Cluster-F-sub-sprint flag.

### §1.2 — Closure-schedule lock edits (F.5-slip lesson applied)

Per the F.5 mid-flight YAML-edit slip recorded in `JC_POLLUTION_CLUSTER_F5_FIX.md §1.5`, applied a SINGLE BATCHED `mcp_search_replace` removing both F.6 entries at once. Post-edit `yaml.safe_load` verify confirmed exact state BEFORE running the slice:
- M1 count: 5 (UNCHANGED from F.3 close — F.6 had no M1 entries)
- M2 count: 26 (down from 28; matches new `M2_CEILING`)
- All 5 remaining M1 entries are `Cluster-G (post-F)`
- 25 of 26 remaining M2 entries are `Cluster-G (post-F)`; 1 is `A+D fix preserves this asyncio.run with snapshot/restore`
- 0 stale entries · 0 new ungrandfathered sites

`M2_CEILING` ratcheted from `28` → `26` in `test_no_bespoke_run_helper.py` to reflect the new baseline post-F.6 closure. **`M1_CEILING` UNCHANGED at 5** (F.6 was M2-only; F.6 closed 0 M1 entries).

**Final closure-schedule lock state post-F.6**:
- M1_CEILING = 5 (5/5 Cluster-G remain)
- M2_CEILING = 26 (25/26 Cluster-G + 1/26 A+D-preserved)
- Trajectory: M1 13 → 11 (F.4) → 8 (F.5) → 5 (F.3) ✓ FINAL · M2 28 → 26 (F.6) ✓ FINAL

### §1.3 — F.3-ADVANCE-slip lesson applied (memo-before-DEV_PIPELINE order)

Per the F.3-ADVANCE-scan discipline slip recorded in `P5_7_FIX_SCOPE_CLUSTER_F3_ADVANCE.md` close-surface, the DEV_PIPELINE.md §9 row update was applied BEFORE authoring this memo. Verified row addition pre-memo. Discipline standing rule "DEV_PIPELINE.md updated before sprint memo" honoured.

### §1.4 — Locked-area re-confirmation (advance-scan §2.2 already verified clean)

| Area | Touched? |
|---|---|
| Shield internals (`services/synisense/run/*` non-API code) | NO |
| Shield API entry (`pipeline_run`) | NO — same call, different invocation (`await` vs `asyncio.run`) |
| Shield encryption envelope (`services/synisense/encryption`) | NO — test 3 stays sync, no change |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| OAuth provider live endpoints | NO |
| Product code | NO |

Cleared. All edits are test-side or invariant-side (the invariant edit is the closure-schedule lock).

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_f6_proving_slice.py`)

```
============================================================================
P5.7-Cluster-F.6 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1 + §6
============================================================================
  Row  1  GREEN  tests/test_synisense_security.py in isolation post-fix (3 passed)
            3 passed, 21 warnings in 4.90s  [dur=6.8s]
  Row  2  GREEN  tests/test_synisense_security.py + autosave (B.2 polluter pair, post-fix)
            6 passed, 21 warnings in 6.16s  [dur=8.3s]
  Row  3  GREEN  tests/test_synisense_security.py + tests/test_phase4_2_http_transport_smoke.py (A+D defensive)
            11 passed, 21 warnings in 5.10s  [dur=6.9s]
  Row  4  GREEN  tests/test_synisense_security.py + tests/test_phase_p5_10_audit_panel_direct_linkage.py (Cluster-E defensive)
            8 passed, 21 warnings in 5.33s  [dur=7.4s]
  Row  5  GREEN  tests/test_synisense_security.py + tests/test_phase_p2_a2_microsoft_pkce.py (F.5 defensive)
            10 passed, 21 warnings in 5.25s  [dur=7.1s]
  Row  6  GREEN  tests/test_synisense_security.py + tests/test_phase_p3_1_csrf.py (F.3 defensive)
            10 passed, 23 warnings in 5.45s  [dur=7.8s]
  Row  7  GREEN  Broad sweep (F.6 + autosave + all prior cluster-fixed)
            33 passed, 23 warnings in 6.89s  [dur=8.9s]
  Row  8  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 7's full stdout
  Row  9  GREEN  AST source-assertion: zero asyncio.run() in test_* bodies
            no asyncio.run() calls remain
  Row 10  GREEN  bespoke-run invariant PASSES (M2_CEILING=26 + drift detector)
            3 passed, 21 warnings in 5.84s  [dur=7.1s]
  Row 11  GREEN  Shield-contract regression: pipeline_run modes + leaky-key absence set preserved
            modes=['redact', 'shield_reversible'] · leaky_keys=['envelope', 'mapping', 'originals', 'shield_map'] · both test pipeline_run calls present
============================================================================
RESULT  11/11 GREEN
============================================================================
```

**Stable across 2 consecutive runs** (run-1 + run-2 both 11/11 GREEN; deterministic).

**Key signals**:
- **Row 1**: F.6 file in isolation 3/3 PASS post-conversion (2 async-converted + 1 sync-preserved).
- **Row 2**: F.6 + autosave (the B.2 polluted target) 6/6 PASS — the LAST polluter→polluted pair closes here.
- **Rows 3-6**: defensive checks confirm A+D, Cluster-E, F.5, F.3 closures aren't regressed by F.6 conversion.
- **Row 7**: broad sweep with all prior cluster-fixed files + F.6 + autosave = 33/33 PASS (single pytest invocation; no pollution).
- **Row 8**: zero `Future attached to a different loop` occurrences — canonical wrong-loop-binding signature silenced for the FINAL polluter.
- **Row 9**: AST source-assertion confirms no `asyncio.run(...)` remains in any `test_*` body of `test_synisense_security.py` (M2-specific shape).
- **Row 10**: closure-schedule lock validated end-to-end — invariant catcher + drift detector + count-ceiling ALL PASS (3 tests) after YAML edits + `M2_CEILING` ratchet 28→26.
- **Row 11 (F.6-specific)**: Shield-contract regression at AST level — both converted tests STILL invoke `pipeline_run(...)` AND test 1 STILL asserts on the same leaky-key absence set (`shield_map`, `mapping`, `originals`, `envelope`). The discipline-pay for Shield-adjacency: even though the analysis says the conversion is safe, the slice explicitly verifies the contract didn't drift.

---

## §3 — FTT-024..026 auto-close validation (end-to-end)

Per dispatch directive: "Verify FTT-024..026 status — they should AUTO-CLOSE (autosave polluter set empties when F.6 ships). If they don't auto-close → HALT, surface — that's a discovery about the autosave polluter dependency model."

**Validation method**: ran autosave + ALL 14 originally-polluter files in a single pytest invocation. If autosave's polluter set is truly empty, the result must be GREEN with zero `Future attached to a different loop` errors.

```
pytest -q --no-header --tb=short -m "not integration and not deploy_smoke and not runtime_playwright" -p no:cacheprovider \
  tests/test_synisense_security.py \
  tests/test_phase_p2_b1_security_headers.py \
  tests/test_phase_p3_2_cookie_hardening.py \
  tests/test_phase_p2_d2_health_composite.py \
  tests/test_phase_p2_b4_password_change.py \
  tests/test_phase_p2_b6_admin_force_reset.py \
  tests/test_phase_p5_7_5_bounce_webhook.py \
  tests/test_phase_p5_7_waitlist_reminder.py \
  tests/test_phase_p2_a2_microsoft_pkce.py \
  tests/test_phase_p5_8_inbox_migration.py \
  tests/test_phase_p5_9_admin_button_and_badge.py \
  tests/test_phase_p3_1_csrf.py \
  tests/test_phase_p3_4_session_timeout.py \
  tests/test_phase_p5_5_session_reauth.py \
  tests/test_track_b_phase_b5_g6_notes_autosave.py

→ 72 passed, 23 warnings in 13.94s
```

**Result: 72/72 PASS · zero failures · zero RuntimeError signatures.** Autosave's polluter set is empty. FTT-024..026 AUTO-CLOSED end-to-end as predicted by the closure model. No HALT condition tripped.

---

## §4 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Cluster's own proving slice | yes (11/11) | **11/11 GREEN** stable across 2 runs |
| Invariant suite `tests/invariants/*` (bespoke-run subset) | yes | **3 passed** (catcher + drift + count-ceiling with M2_CEILING=26) |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via inventory slice + standing ratchet — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` in lockstep (last refreshed at JC-TL GP ship close 2026-06-26; unchanged by F.6 test-only edits) |
| JC-TM email path smoke | yes | **N/A** | No SendGrid send code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Shield contract regression (F.6-specific) | yes | **GREEN** | Row 11 AST-level verification: `pipeline_run` modes preserved (`shield_reversible` + `redact`); leaky-key absence set preserved (`shield_map`, `mapping`, `originals`, `envelope`) |
| Inventory slice sibling re-run | yes | **3/3 GREEN** · M1=5/5 ceiling, M2=26/26 ceiling, zero drift |
| FTT-024..026 auto-close validation | yes | **72/72 PASS** (autosave + all 14 originally-polluter files in single invocation) |

---

## §5 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_synisense_security.py` | MOD | `import asyncio` drop + 2 sync→async decorator+body conversion + `_prep_keys` fixture preserved verbatim + `test_unregistered_version_blocks_decryption` preserved as sync + docstring refresh (~15 LOC delta) |
| `tests/invariants/bespoke_run_helper_grandfathered.yml` | MOD | 2 F.6 `m2_entries:` rows DELETED in SINGLE BATCHED edit (F.5-slip lesson applied) |
| `tests/invariants/test_no_bespoke_run_helper.py` | MOD | `M2_CEILING` 28 → 26 (`M1_CEILING` UNCHANGED at 5) + module docstring/comment update |
| `backend/scripts/jc_pollution_cluster_f6_proving_slice.py` | NEW | 11-row proving slice with Row 10 closure-schedule-lock end-to-end validation + Row 11 Shield-contract AST regression (F.6-specific) |
| `memory/sprints/JC_POLLUTION_CLUSTER_F6_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added BEFORE memo authored (F.3-ADVANCE-slip lesson applied) |
| `memory/jc_artifacts/FAILING_TEST_TRACKER.md` | UPDATED | FTT-024..026 row CLOSED — auto-close validated end-to-end |
| `memory/PRD.md` | UPDATED | Head-entry blockquote summarising Cluster-F arc completion |

**Files NOT touched**: any product code, any other test file, any other invariant file, any fixture file, Shield internals, Shield API.

---

## §6 — Discipline notes

- **Scope honoured**: only the 1 F.6 file + invariant lock edits + memo/pipeline/tracker/PRD updates.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 11/11 GREEN stable across 2 consecutive runs** — HARD STOP at slice close.
- **Locked-area check** done before + after — clear.
- **No production code changes** — entirely test-side + invariant lock + docs.
- **Pattern uniformity confirmed at 6 sub-sprints**: same conversion logic applied to F.2 (3 M1) + F.1 (2 M1) + F.4 (2 M1) + F.5 (3 M1) + F.3 (3 M1) + F.6 (1 M2). The M2 variant differs only in HOW the coroutine is invoked (`asyncio.run` inline vs `_run` helper); the conversion mechanics are identical.
- **Sync-test preservation continues** to honour the Cluster-F.2 heuristic (1 of 3 tests stays sync — the pure-Python envelope contract).
- **Two prior discipline-slip lessons applied successfully**:
  - **F.5 slip lesson** (mid-flight YAML edit): used SINGLE batched search_replace + `yaml.safe_load` verify-before-slice — no slip occurred this sprint.
  - **F.3-ADVANCE slip lesson** (memo-before-DEV_PIPELINE): updated `DEV_PIPELINE.md §9` row BEFORE authoring this memo — verified pre-memo.
- **Shield-adjacency discipline-pay honoured**: Row 11 (AST-level Shield-contract regression) added even though advance-scan analysis cleared the conversion as safe. The discipline-pay caught zero drift — Shield contract preserved verbatim.
- **F.6-ADVANCE LOW-risk reclassification validated under conversion**: the scope memo's "high risk / HALT pre-armed" was conservative on surface area; the advance scan's "LOW" verdict was correct. F.6 followed the same mechanical pattern as F.5/F.3 with zero adaptation needed.
- **Cluster-F arc closure**: 14 of 14 polluters converted. FTT-024..026 auto-closed. The "polluter set empty" hypothesis from the closure model is now empirically validated.

---

## §7 — Cluster-F arc summary (closed at F.6 ship)

| Sub-sprint | Date | Files | Sites | Pattern |
|---|---|---|---|---|
| F.2 | 2026-06-26 | 3 (security_headers + cookie_hardening + health_composite) | 3 M1 | First Cluster-F sub-sprint after dispatch |
| F.1 | 2026-06-27 | 2 (password_change + admin_force_reset) | 2 M1 | Second sub-sprint |
| F.4 | 2026-06-27 | 2 (bounce_webhook + waitlist_reminder) | 2 M1 | Third sub-sprint (SendGrid surfaces) |
| F.5 | 2026-06-27 | 3 (microsoft_pkce + inbox_migration + admin_button_and_badge) | 3 M1 | Fourth sub-sprint (largest test count: 18) |
| F.3 | 2026-06-27 | 3 (csrf + session_timeout + session_reauth) | 3 M1 | Fifth sub-sprint (advance-scan LOW reclassification proven) |
| F.6 | 2026-06-27 | 1 (synisense_security) | 2 M2 | Sixth and FINAL sub-sprint (advance-scan LOW reclassification proven under Shield-adjacency) |
| **TOTAL** | | **14 files** | **13 M1 + 2 M2 = 15 sites total** (sites > files because F.6 file has 2 M2 sites) | |

**Pattern uniformity validated across all 6 sub-sprints**: the same Cluster-E mechanical conversion was applied identically to 14 files without per-file customization (only the M2 variant differed in HOW the coroutine was invoked — the conversion mechanics were identical).

**Auto-close cascade**:
- FTT-023 closed by Cluster-E (2026-06-26)
- FTT-015..022 closed by A+D (2026-06-26)
- FTT-010..012 closed by B.1 (2026-06-26)
- FTT-024..026 closed by Cluster-F arc completion (this sprint, 2026-06-27) — validated end-to-end

**Trajectory complete**:
- M1_CEILING: 13 → 11 → 8 → 5 ✓ FINAL
- M2_CEILING: 28 → 26 ✓ FINAL
- Closure-schedule lock now serves as a floor — Cluster-G will ratchet DOWN from here as each sub-sprint ships.

---

## §8 — User-direction surface (HARD STOP)

Per the original dispatch directive: **HARD STOP & surface to user — single consolidated handoff including all required evidence**.

**Cluster-F arc complete**:
- ✅ F.2 (security_headers + cookie_hardening + health_composite) — 3 files closed
- ✅ F.1 (password_change + admin_force_reset) — 2 files closed
- ✅ F.4 (bounce_webhook + waitlist_reminder) — 2 files closed
- ✅ F.5 (microsoft_pkce + inbox_migration + admin_button_and_badge) — 3 files closed
- ✅ F.3 (csrf + session_timeout + session_reauth) — 3 files closed
- ✅ F.6 (synisense_security) — 1 M2 outlier file closed
- ✅ **14 of 14 polluters converted**

**FTT closure status**:
- ✅ FTT-024..026 AUTO-CLOSED (end-to-end validated; 72/72 PASS sweep)
- Remaining active FTT IDs: only FTT-004..009 (Cluster C intra-file refactor) + FTT-014 (Cluster D deterministic regression — handled by Step 3 of this dispatch) + FTT-027..035 (thin-assertion grandfathered debt with machine-enforced ceiling).

**Next dispatch options**:
1. **Cluster-F retrospective memo** (~150 LOC pure narrative; codifies the advance-scan-default-on pattern proven by F.3+F.6 reclassification consistency)
2. **Cluster-G READ-ONLY scope memo** (~30 files: 5 M1 + 25 M2 from invariant baseline scan discovery)
3. **Cluster-G sub-sprints** with advance-scan-default-on (sized per scope memo)
4. **Cluster-C intra-file refactor** (FTT-004..009)

Awaiting next dispatch from user. Standing rules unchanged.

---

## §9 — Time-gate status at slice close

`Sat Jun 27 09:12:42 UTC 2026` at F.6 proving-slice close (Run 1). The 09:12 UTC window crossed during F.6 close. Per user's standing pre-authorization, Steps 2 (GridFS backfill `--commit`) + 3 (FTT-014 re-run) are now eligible to fire after this F.6 surface. See dispatch dispatch's Step 4 consolidated handoff for backfill log + FTT-014 branch outcome.
