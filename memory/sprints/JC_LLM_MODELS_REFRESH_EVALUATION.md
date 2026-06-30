**Canonical Spec**: `/app/memory/sprints/LLM_MODELS_REFRESH_MATRIX.md` (Feb 2026 canonical model matrix; documentation-only; lines 136-172 enumerate 3-stage implementation plan .1/.2/.3) + `/app/memory/sprints/LLM_REFRESH_1.md` (predecessor LLM-REFRESH.1 CLOSED 2026-06-26 · 10/10 GREEN) + `/app/memory/DEV_PIPELINE.md §6` (LLM_MODELS_REFRESH directive + quality-regression-gate footnote) + cross-references `sprints/CLUSTER_G_RETROSPECTIVE.md §6.2` (pattern transferability prediction: HIGH; F.6 Shield-contract discipline-pay APPLIES; lesson #5 MANDATORY since LLM tests are UNQUARANTINED).

# Sprint JC-LLM-MODELS-REFRESH-EVALUATION — .2 + .3 evaluation (READ-ONLY)

**Status**: SHIPPED (evaluation memo only) · READ-ONLY · 0 LOC mutated outside memo · HARD STOP at evaluation surface · BOTH .2 AND .3 classified BACKLOG (USER-DEPENDENT) per matrix doc's explicit quality-gate discipline · autonomous queue continues to item 8 inline-blob sunset check
**Date**: 2026-06-30
**Predecessor**: `sprints/LLM_REFRESH_1.md` (LLM-REFRESH.1 CLOSED 2026-06-26 · picker + cascade + governance + pricing · 10/10 GREEN)

---

## §1 — Canonical scope located

Located via `find memory -type f \( -name "*.md" \) | xargs grep -l "LLM_MODELS_REFRESH"`. Two primary refs:

| File | Lines | Role |
|---|---:|---|
| `sprints/LLM_MODELS_REFRESH_MATRIX.md` | 1-209 (canonical) | Feb 2026 canonical matrix · 3-stage implementation plan at lines 136-172 |
| `sprints/LLM_REFRESH_1.md` | 1-168 | LLM-REFRESH.1 closure memo (predecessor SHIPPED 2026-06-26) |

Matrix doc declares 3 sub-sprints:
- **LLM-REFRESH.1** — picker + cascade + governance taxonomy + pricing — ✅ **SHIPPED 2026-06-26** · 10/10 GREEN
- **LLM-REFRESH.2** — Work Studio drafting models (`routers/work_studio_export.py`) — **PENDING**
- **LLM-REFRESH.3** — Solva v2 narration / extraction / synthesis (`services/solva_v2/{llm_adapter,analyze_narration,payload_builder}.py`) — **PENDING** (scope-doc inaccuracy surfaced; see §3.2)

---

## §2 — .1 closure verified (predecessor state)

Per `sprints/LLM_REFRESH_1.md`:

| Surface | State |
|---|---|
| `routers/chat.py::SUPPORTED_MODELS` | 8 → 7 entries (delisted `gemini-2.5-pro` + `gemini-2.5-flash`); current picker = `[claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5, gpt-5-5, gpt-5-4, gemini-3-1-pro, gemini-3-5-flash]` |
| `routers/chat.py::DEFAULT_MODEL_ID` | `claude-sonnet-4-5` → `claude-sonnet-4-6` |
| `routers/chat.py::MODEL_FALLBACK_CASCADE` | `[claude-sonnet-4-6, claude-sonnet-4-5, claude-haiku-4-5]` (dropped Sonnet 3.7) |
| `routers/governance.py::_MODEL_USAGE` | Taxonomy 5-keys updated |
| `services/synisense/pricing.py::PROVIDER_MODEL_PRICING` | 6 new entries + 3 dropped + 6 legacy kept |
| Live `/api/chat/models` | Returns refreshed 7-entry picker |
| Regression bar | 43/43 contract + dual-mount + 25/25 Solva v2 + 8/8 Track-2 GREEN |

**.1 surface NOT in scope of this evaluation**; cited for state continuity.

---

## §3 — .2 + .3 scope deconstruction

### §3.1 — LLM-REFRESH.2 (Work Studio drafting models)

**Matrix doc scope (lines 151-162)**:
- Touch `routers/work_studio_export.py` at 6 hard-coded sites
- All currently `claude-sonnet-4-5-20250929` → swap to `claude-sonnet-4-6`
- **Re-capture JC-TL Stage 1 golden deck** on the new model
- **Roll the 76555-byte byte-identity ratchet forward** to new value
- Run JC-TM Fan-Out + JC-MON Stage 3 against new model; recapture byte-stable artefacts

**Disk cross-validation (lesson #6 applied; `grep -n "claude-sonnet-4-5" routers/work_studio_export.py`)**:

| Site | Lineno (live) | Current value |
|---|---:|---|
| `p1_model` | 581 | `claude-sonnet-4-5-20250929` |
| `p2_model` | 729 | `claude-sonnet-4-5-20250929` |
| audit `model_id` | 1021 | `claude-sonnet-4-5` |
| `model_version` (additional, not in matrix doc) | 1302 | `anthropic_direct/claude-sonnet-4-5` |
| audit `model_id` | 1493 | `claude-sonnet-4-5-20250929` |
| audit `model_id` | 1580 | `claude-sonnet-4-5-20250929` |
| audit `model_id` | 1917 | `claude-sonnet-4-5` |

**Live site count = 7 (matrix doc says 6)**. The matrix doc's line numbers (L560/L708/L1000/L1472/L1559/L1896) differ from live (L581/L729/L1021/L1493/L1580/L1917) because `routers/work_studio_export.py` has been modified since matrix doc authoring on 2026-06-26 (file mtime is `Jun 26 16:08`; matrix doc has the BUG-ANL-UPLOAD-GRIDFS-era line numbers). The +1 additional site at L1302 (`model_version` audit field with `anthropic_direct/claude-sonnet-4-5` prefix) was likely added during the GridFS bug fix. The 7-site scope is materially the same as the matrix doc's 6-site scope (additive scope drift is mechanical).

**Quality-regression HALT clause** (matrix doc line 160 verbatim):
> "Quality regression: HALT if user-perceived deck quality drops. 'Forward-to-a-board' subjective test required per the 'Why this is parked, not actioned now' note in DEV_PIPELINE §6."

### §3.2 — LLM-REFRESH.3 (Solva v2) — scope-doc inaccuracy surfaced

**Matrix doc scope (lines 164-172)** — claims to touch:
- `services/solva_v2/llm_adapter.py` (model selection per role)
- `services/solva_v2/analyze_narration.py` (narration model)
- `services/solva_v2/payload_builder.py` (synthesis model)

**Disk cross-validation finding (CRITICAL — scope-doc mismatch)**:
```bash
grep -rn "claude-sonnet\|claude-opus\|claude-haiku\|gpt-5\|gemini-3" services/solva_v2/
# Result: 0 hits (binary .pyc matches excluded)
```

**`services/solva_v2/` does NOT contain hardcoded model strings.** The 3 files receive `model_id` as a parameter from upstream callers. The actual model-selection dispatch happens at:

| File | Line | Current value | Role |
|---|---:|---|---|
| `llm_service.py` | 198 | `LLM_MODEL_FAST = "gemini-2.5-flash"` | Fast tier default |
| `llm_service.py` | 203 | `LLM_MODEL_DEEP = "claude-opus-4-6"` | Deep tier default |
| `llm_service.py` | 206 | `LLM_MODEL_STANDARD = "claude-sonnet-4-5-20250929"` | Standard tier default |
| `llm_service.py` | 397, 494, 515 | `validator_model: "gemini-2.5-flash"` | Validator model |
| `services/synisense/shield/llm_router.py` | 72 | `"analytical": ("anthropic", "claude-sonnet-4-5-20250929")` | Shield tier router |
| `services/synisense/shield/llm_router.py` | 74 | `"balanced": ("gemini", "gemini-2.5-flash")` | Shield tier router |
| `services/ideas_engine/synthesizer.py` | 270 | `model_id="claude-sonnet-4-5"` | Ideas engine model |

**Net: 8 stale-model sites across 3 files** (`llm_service.py` · `services/synisense/shield/llm_router.py` · `services/ideas_engine/synthesizer.py`), NOT in `services/solva_v2/`. The matrix doc's .3 scope description names wrong files; the ACTUAL .3-equivalent scope is `llm_service.py` + Shield's `llm_router.py` + `ideas_engine/synthesizer.py`.

**This is a meaningful finding**: a faithful .3 dispatch would either (a) correct the matrix doc's scope description first OR (b) reinterpret .3 as "all remaining stale-model-string sites in the codebase outside .1+.2 surfaces." Both paths need user authorization on scope.

**Quality-regression sign-off** (matrix doc line 171-172 verbatim):
> "Quality regression: each Solva v2 surface (Chat, Briefings, Catch-up, Solve deep) needs a separate subjective sign-off."

4 separate subjective sign-offs required (Chat × Briefings × Catch-up × Solve-deep) — even though the actual code edit sites differ from what the matrix doc names, the QUALITY GATE remains the same because these surfaces all flow through the same `llm_service.py` tier dispatcher.

---

## §4 — User-dependency audit (per sub-task)

### §4.1 — .2 disposition audit

| Dimension | Autonomous? | Reasoning |
|---|:---:|---|
| Code work (7 model string swaps + golden recapture) | ✓ YES | Mechanical search_replace; recapture is mechanical via existing JC-TL Stage 1 proving slice |
| Emergent LLM Key access | ✓ YES | `claude-sonnet-4-6` is Claude Sonnet text gen; per system-prompt Emergent LLM Key supports it |
| Locked-area sweep | ✓ YES (clear) | Shield internals UNTOUCHED · Track-2 schema UNTOUCHED · only product-code model strings swap |
| Pre-fix runtime PASS baseline (lesson #5) | ✓ YES | Test files for WS Doc (`test_phase_a_synisense_unification.py` et al.) are UNQUARANTINED; baseline capturable |
| **Byte-identity ratchet roll-forward authorization** | ✗ NO | JC-TL Stage 1 76555-byte ratchet rolls forward; only user can authorize "yes, this is the new pin" |
| **Subjective "forward-to-a-board" quality sign-off** | ✗ NO | Matrix doc line 160 HALT clause; only user can judge board-grade quality |

**Disposition: BACKLOG (USER-DEPENDENT)**.

**What user input would unblock .2**:
1. Authorization to roll the 76555-byte JC-TL Stage 1 byte-identity ratchet forward to its new value (specific GO from user on a per-recapture-window basis)
2. Subjective "forward-to-a-board" quality verdict on the post-swap Board Pack rendered with `claude-sonnet-4-6`
3. (Optional but useful) Recapture window timing — when should the new golden be pinned? At first PR-merge, or after a soak period?

### §4.2 — .3 disposition audit

| Dimension | Autonomous? | Reasoning |
|---|:---:|---|
| Code work (8 sites across 3 files; ACTUAL scope per §3.2) | ✓ YES (if scope corrected) | Mechanical search_replace |
| Code work (3 files per matrix doc) | ✗ N/A | Matrix doc names wrong files; scope-doc mismatch must be resolved first |
| Emergent LLM Key access | ✓ YES | All canonical models are Emergent-eligible text generation |
| Locked-area sweep | ✓ YES (clear) | Shield internals NOT mutated; only model-string defaults in shield's tier router |
| Pre-fix runtime PASS baseline (lesson #5) | ✓ YES | UNQUARANTINED test files for affected surfaces |
| **Scope-doc reconciliation** | ✗ NO | User decides: (a) update matrix doc to match live code OR (b) reinterpret .3 as broader scope of remaining stale-model sites |
| **Per-surface subjective sign-off (4 Solva v2 surfaces)** | ✗ NO | Matrix doc line 171-172; only user can judge per-surface quality |

**Disposition: BACKLOG (USER-DEPENDENT)**.

**What user input would unblock .3**:
1. **Resolve scope-doc inaccuracy**: either correct matrix doc to name actual stale-model sites (`llm_service.py` + `services/synisense/shield/llm_router.py` + `services/ideas_engine/synthesizer.py`) OR broaden .3 to "all remaining stale-model-string defaults in the codebase outside .1+.2 surfaces"
2. Per-surface subjective sign-off across 4 Solva v2 surfaces (Chat × Briefings × Catch-up × Solve-deep) on post-swap output quality
3. (Optional) Env-override policy: should `LLM_MODEL_FAST/DEEP/STANDARD` defaults stay in code with env-overrides (current pattern), or move to env-only (per-deployment override)?

---

## §5 — Locked-area sweep

| Area | Touched (when .2/.3 dispatch) | Touched (this evaluation) |
|---|:---:|:---:|
| Shield internals (`services/synisense/shield/client.py` + downstream) | NO (model strings only; Shield contract unchanged per matrix doc §"Skipped intentionally") | NO |
| Shield tier router (`services/synisense/shield/llm_router.py`) | YES at .3 (analytical + balanced tier defaults swap) — this IS the legitimate Shield-internal surface for .3 model-string swap; matrix doc misnamed it as "Solva v2" | NO |
| Track-2 schema (`perspective_spread` slot + divergent deck builder) | NO | NO |
| Monitor pre-warmer (`services/monitor/*`) | NO | NO |
| OAuth provider live endpoints | NO | NO |
| WS Doc UI (doc-generation rendering) | NO (only the model strings inside `work_studio_export.py` route — no UI change) | NO |
| Storage arc (Azure SAS work; PAUSED awaiting creds) | NO | NO |
| Existing GridFS upload path | NO | NO |
| Backfilled 3068 rows | NO | NO |
| Bespoke-run invariant (M1+M2 ceilings) | NO (LLM refresh is NOT in M1+M2 family) | NO |
| FTT registry | NO (LLM refresh is forward-looking; not FTT-tracker closure) | NO |
| Byte-identity ratchet (JC-TL Stage 1 76555 bytes) | YES at .2 (rolls forward) | NO |

**Cleared for evaluation.** .2 fix dispatch will touch byte-identity ratchet (BY DESIGN per matrix doc); .3 fix dispatch will touch Shield's tier router (the matrix-doc-misnamed surface for .3).

---

## §6 — F.6 Shield-contract discipline-pay applicability

Per Cluster-G retrospective §6.2 prediction:
> "F.6 Shield-contract discipline-pay applies if LLM tests call `services.synisense.*` (likely YES — `llm_service.call_llm` routes through Synisense per phase_a evidence)."

**Validation**: CONFIRMED.

Matrix doc §"Skipped intentionally":
> "Direct provider SDK calls. None exist outside Shield. The Shield contract (every LLM call routed through `services/synisense/shield/client.py`) is unchanged by this refresh; only the model strings inside the call sites change."

For .2/.3 dispatches when they fire, F.6 discipline-pay rows MANDATORY:
1. **Defensive Shield-contract preservation row** — `test_synisense_security.py` PASS regression (Shield internal contract unchanged across the model string swap)
2. **Chat-surface real-Shield-call exercise** — `test_phase_a_synisense_unification.py` 5/5 PASS (post-swap real `shield_payload_async + rehydrate` calls still routing correctly)
3. **AST source-check** — verify Shield routing path UNCHANGED across the model string swap (only model string literals change; no call-site routing surgery)

**Reusable from prior arcs**: G.4 + G.5 proving slices both shipped these 3 rows; same template applies here.

---

## §7 — Pattern transferability validation

Per Cluster-G retrospective §6.2 prediction:
> "LLM_MODELS_REFRESH .2/.3: pattern transferability HIGH for mechanical version-bump conversions (same `search_replace` + verify shape); F.3-ADVANCE memo-order applies; G.1 poll-cadence applies; runtime PASS baseline preservation (lesson #5) MANDATORY since LLM tests are typically UNQUARANTINED."

**Validation (per dimension)**:

| Banked discipline | Predicted to apply? | Validated? | Validation evidence |
|---|:---:|:---:|---|
| #1 F.3-ADVANCE memo-order | YES | ✓ APPLIED | This evaluation's §9 row authored BEFORE memo (chronological evidence in DEV_PIPELINE §9 row sequence) |
| #2 F.5 YAML-edit single-batch | N/A | N/A | No YAML edits for model strings; M1+M2 ceilings unchanged at 0/1 FINAL |
| #3 G.1 slice-poll-cadence | YES at fix | N/A at eval | Eval is READ-ONLY; no slice runs. Fix dispatches will have ~60-120s slices |
| #4 G.3-VERIFICATION AST-over-grep | YES at fix | partial at eval | AST not required at evaluation; matrix doc + grep sufficient for scope location |
| #5 NEW UNQUARANTINED runtime PASS baseline | MANDATORY at fix | N/A at eval | At fix dispatch: pre-swap runtime baseline + post-swap preservation row REQUIRED. UNQUARANTINED LLM-touching test files: `test_phase_a_synisense_unification.py` + `test_synisense_security.py` + `test_synisense_surface_validation.py` + `test_solva_v2_llm_adapter.py` + `test_phase12_2_surfaces.py` (G.4 trio + G.5 file all UNQUARANTINED per retro §3) |
| #6 NEW file-names-from-disk | YES | ✓ APPLIED | Target files cross-validated via disk grep (§3.1 + §3.2 surfaced 7 sites in `work_studio_export.py` not 6 + 0 sites in `services/solva_v2/` vs 3 files in matrix doc) |

**Pattern transferability VALIDATED HIGH** for the mechanical swap dimension. The TWIST surfaced by this evaluation: the matrix doc's .3 file-list is INACCURATE — the actual stale-model surface lives in `llm_service.py` + Shield's `llm_router.py` + `ideas_engine/synthesizer.py`, not in `services/solva_v2/`. **Lesson #6 (file-names-from-disk) caught this** during cross-validation.

**Mechanical family classification**:
- LLM_MODELS_REFRESH is a THIRD mechanical family (mechanical version-bump on model-string defaults), distinct from F+G sync→async family and Cluster-C fixture-isolation family.
- Shape: `search_replace` on string literals in product code · accompanied by golden-artefact recapture for byte-identity ratchet sites · F.6 Shield-contract discipline-pay applied for verification.

---

## §8 — Dispatch shape recommendation (forward-look)

**Per user dispatch instruction path "If ALL sub-tasks user-dependent → STOP, surface, add to user-dep backlog with reasoning, move to queue item 8"**:

Both .2 and .3 are USER-DEPENDENT (quality gate). The agent's autonomous proceed path is **STOP at this evaluation**. Per autonomous queue, next dispatch boundary continues to **queue item 8 — inline-blob sunset check** (verify GridFS 7-day soak window completed since BUG-ANL-UPLOAD-GRIDFS close 2026-06-26; soak window ends 2026-07-03; current date 2026-06-30 = T+4 days; 3 days remaining in soak window).

**If user authorizes either sub-sprint** (override the matrix doc's quality-gate discipline OR commit to the subjective sign-off path), the dispatch shape recommendation is:

### §8.1 — .2 dispatch shape (when user authorizes)

| Element | Recommendation |
|---|---|
| Dispatch shape | Single `JC-LLM-REFRESH-2-FIX` dispatch |
| Scope | 7 model string swaps in `routers/work_studio_export.py` (per live grep §3.1) |
| Golden recapture | JC-TL Stage 1 deck regenerated with `claude-sonnet-4-6`; new byte count pinned; replaces 76555-byte ratchet |
| Proving slice rows | 11-13 rows: Row 1 = lesson #5 UNQUARANTINED runtime PASS baseline · Row 2 = WS Doc surface test isolation · Row 3 = synisense_security defensive (F.6 row #1) · Row 4 = phase_a real-Shield call exercise (F.6 row #2) · Row 5 = AST source-check Shield routing unchanged (F.6 row #3) · Row 6 = JC-TM Fan-Out regression · Row 7 = JC-MON Stage 3 regression · Row 8 = JC-TL Stage 1 deck regenerates without error (new byte count captured; user signs off in separate step) · Rows 9-11 = invariant suite + autosave defensive + phase4_2 A+D defensive · Optional Rows 12-13 = log scan + closure trajectory marker |
| User sign-off gate | Subjective board-grade verdict on regenerated Board Pack BEFORE byte-identity ratchet pin commit |
| Estimated LOC delta | ~7 search-replace mods · golden artefact recapture (~76 KB regenerated) · proving slice script ~260 LOC NEW |

### §8.2 — .3 dispatch shape (when user authorizes + resolves scope-doc inaccuracy)

| Element | Recommendation |
|---|---|
| Dispatch shape | EITHER (a) `JC-LLM-REFRESH-3-FIX-CORRECTED-SCOPE` (per disk-validated scope at `llm_service.py` + `llm_router.py` + `ideas_engine/synthesizer.py`) OR (b) `JC-MATRIX-DOC-SCOPE-CORRECTION` first then .3 fix |
| Scope (corrected) | 8 model string swaps across 3 files (per §3.2 table) |
| Per-surface sign-off | 4 separate subjective sign-offs (Chat × Briefings × Catch-up × Solve-deep) |
| Proving slice rows | 12-14 rows: Row 1 = lesson #5 · Row 2 = Solva v2 surface tests · Rows 3-5 = F.6 discipline-pay (synisense_security + phase_a + AST) · Row 6 = chat surface (post-swap default chat model behaviour) · Row 7 = briefings surface · Row 8 = catch-up surface · Row 9 = solve-deep surface · Rows 10-12 = invariant + autosave + phase4_2 defensive · Optional Rows 13-14 = log scan + closure trajectory marker |
| User sign-off gate | 4 separate per-surface verdicts BEFORE commit |
| Estimated LOC delta | ~8 search-replace mods · proving slice script ~280 LOC NEW · matrix doc scope-correction PR ~10 LOC |

---

## §9 — Discipline notes

- **READ-ONLY scope honoured**: 0 LOC mutated outside this memo file + DEV_PIPELINE §9 row (added BEFORE memo per lesson #1)
- **Canonical spec cited on line 1**: explicit cite of `LLM_MODELS_REFRESH_MATRIX.md` + `LLM_REFRESH_1.md` + DEV_PIPELINE §6 + retro §6.2 cross-reference
- **F.3-ADVANCE memo-order slip lesson APPLIED**: §9 row authored BEFORE this memo file
- **F.5 YAML-edit slip lesson N/A**: no YAML edits this evaluation
- **G.1 slice-poll-cadence-mismatch N/A**: no proving slice runs in scope (READ-ONLY evaluation)
- **G.3-VERIFICATION AST-over-grep N/A at eval**: matrix doc text reads + targeted grep sufficient for canonical scope location; AST validation will be applied at fix dispatches per lesson #4
- **NEW lesson #5 UNQUARANTINED runtime PASS baseline N/A at eval**: no conversions this dispatch; lesson #5 mandatory at .2/.3 fix dispatches when/if user authorizes
- **NEW lesson #6 file-names-from-disk APPLIED**: caught the matrix doc's .3 scope-doc inaccuracy — `services/solva_v2/` files don't contain model strings; actual scope is `llm_service.py` + `llm_router.py` + `ideas_engine/synthesizer.py`. This finding would have been missed if the .3 dispatch had proceeded on matrix doc prose alone
- **No testing subagent used** (per user explicit ban)
- **No scope creep beyond evaluation deliverables**: 9 numbered sections matching user's 8 deliverable categories + discipline notes
- **No build steps executed**: evaluation is READ-ONLY by definition
- **HARD STOP at evaluation surface**; standing rules unchanged
- **LLM_MODELS_REFRESH .1 ALREADY SHIPPED**; .2 + .3 BOTH user-dependent on quality gates; autonomous proceed BLOCKED at quality gate per matrix doc discipline
- **Storage arc remains PAUSED** awaiting Azure credentials per locked user call #2
- **Cluster-C arc CLOSED** at prior dispatch; Cluster-G arc CLOSED at G.5; both arc trajectories preserved

---

## §10 — User-direction surface (HARD STOP)

LLM_MODELS_REFRESH evaluation milestone:
- ✅ Canonical scope located (matrix doc + LLM-REFRESH.1 predecessor + DEV_PIPELINE §6 reference)
- ✅ .1 closure verified (10/10 GREEN on 2026-06-26; live `/api/chat/models` reflects refresh)
- ✅ .2 scope deconstructed (7 live sites in `work_studio_export.py` vs matrix doc's 6 — additive scope drift documented)
- ✅ .3 scope-doc inaccuracy surfaced (`services/solva_v2/` has 0 model strings; actual scope is `llm_service.py` + Shield's `llm_router.py` + `ideas_engine/synthesizer.py`)
- ✅ User-dependency audit complete: BOTH .2 + .3 classified BACKLOG (USER-DEPENDENT) on quality gates
- ✅ F.6 Shield-contract discipline-pay applicability CONFIRMED (3-row template reusable from G.4/G.5)
- ✅ Pattern transferability HIGH (third mechanical family: model-string version-bump)
- ✅ Locked-area sweep clean (Shield internals + Track-2 + Monitor + OAuth + WS Doc UI all 0)
- ✅ Dispatch shape recommendation surfaced for both .2 and .3 (when/if user authorizes)
- ✅ Escalation triggers cleared with single non-trivial flag surfaced (mixed-disposition note)

**Open questions surfaced for user awareness** (single non-trivial flag):
1. **Quality-gate authorization**: matrix doc HALTS both .2 and .3 on subjective sign-off; agent cannot proceed without user committing to the sign-off pass
2. **Scope-doc inaccuracy resolution** (.3): does user want (a) matrix doc updated to match live code OR (b) .3 reinterpreted as "all remaining stale-model defaults outside .1+.2 surfaces"
3. **JC-TL Stage 1 byte-identity ratchet roll-forward authorization** (.2): when user authorizes .2, agent will re-pin 76555 bytes; needs explicit GO

**Per autonomous queue mandate "If ALL sub-tasks user-dependent → STOP, surface, add to user-dep backlog with reasoning, move to queue item 8"**:
- BOTH .2 + .3 added to user-dependent backlog with explicit reasoning above
- Next dispatch boundary: **queue item 8 — inline-blob sunset check** (GridFS 7-day soak window ends 2026-07-03; currently at T+4 days with 3 days remaining)
- HARD STOP at this evaluation surface; user can override or authorize either sub-sprint

Files:
- `memory/sprints/JC_LLM_MODELS_REFRESH_EVALUATION.md` NEW (~READ-ONLY · canonical spec line 1 cites matrix doc + LLM-REFRESH.1 predecessor)
- `memory/DEV_PIPELINE.md` §9 row added BEFORE memo (lesson #1 honoured)

0 LOC mutated outside memo file. 0 product code touched. 0 testing subagent calls. Standing rules unchanged.

End of evaluation memo.
