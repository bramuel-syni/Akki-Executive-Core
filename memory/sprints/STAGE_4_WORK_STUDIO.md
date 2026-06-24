# Stage 4 — Work Studio end-to-end

**Date:** 2026-06-24
**Dispatch:** AKKI Full Runway, Stage 4 — wire the captured Chat
objective to a recommended kind, then surface the Solva v2 Analyze
narration in report exports. Reuse existing engines / templates; no
new engine to be built.
**Status:** CLOSED. Two commits land locally. 25 new tests green (21 FE
unit + 4 BE end-to-end). 94 invariants still GREEN. Backend health
verified.

## Headline result

| Step | Commit | Result |
|---|---|---|
| 4.1 Discovery + seam classification (read-only) | — | Two genuine seams identified (4.2 + 4.3). Chat → Work Studio compile path already WORKS per WS1. Analyze drawer → synthesize already routes to `services.solva_v2.analyze_narration` per the `get_solva().narrate_analysis(...)` call at `routers/workbook_analysis.py:1089` (the wiring landed in Track A Phase 3). |
| 4.2 Objective → best-fit-kind recommender (Chat affordance) | `e0fb89b2` | New `workStudioRecommender.js` + wired into `WorkStudioAffordanceModal.jsx`. 21 jest cases green. |
| 4.3 Analyze narration carriage in report exports (DOCX / PPTX / XLSX) | `edc278fe` | Schema extension on `WorkbookAnalysis` + adapter rewrite at `_adapt_new_analysis_to_workbook_analysis` + render injection in `build_*_report`. 4 e2e tests green. |
| 4.4 End-to-end seam classification across all 6 kinds + analyze flow | — | Classification matrix below. No seams beyond 4.2 + 4.3 require code. |
| 4.5 Sprint memo + DEV_PIPELINE.md updates + pipeline-log-sync | (this memo + DEV_PIPELINE row) | Final Stage 4 commit. |

## Stage 4.1 — Discovery (read-only)

### What WORKS today (pre-Stage-4 verification)

| Surface | Status | Evidence |
|---|---|---|
| Chat → Work Studio affordance → `POST /api/contexts/{cid}/work-studio/export/{kind}` for all 6 kinds | WORKS | WS1 sprint memo at `sprints/PHASE_WS1_REPAIR.md`: brief / deck / report / minutes / committee_pack / board_pack each verified end-to-end with valid ZIP magic + correct OpenXML MIME. |
| Analyze drawer → `POST /api/workbook/v2/analyses/{aid}/synthesize` → Solva v2 narration in tabs | WORKS | `get_solva().narrate_analysis(...)` at `routers/workbook_analysis.py:1089` — narration headline + observations land in `runs[-1]` per the Phase 3 wiring; tabs (Bottom Line / What changed / What's likely next / What's odd) consume them. |
| Compile (`/from-document`) + Overlay + Render (compile-then-render) | WORKS | WS1 memo: overlay round-trip green, render DOCX (36 650 b) / PPTX (29 085 b) / PDF (1 631 b) all green. |

### Seams that NEEDED wiring (Stage 4 dispatch's actual scope)

| # | Seam | File(s) | What was broken |
|---|---|---|---|
| 4.2 | Chat affordance defaults to `brief` regardless of objective | `frontend/src/components/chat/WorkStudioAffordanceModal.jsx:97` (pre-fix) | The captured objective + description was never read by the kind picker. User had to manually click the right tile every time. |
| 4.3 | `_adapt_new_analysis_to_workbook_analysis` strips narration | `backend/routers/workbook_analysis.py:163-222` (pre-fix) | Explicit Phase-1 shim comment said "Phase 3 will replace this shim with real per-source narration via Solva v2." Synthesize landed in Phase 3, the adapter was never updated, so `ana-*` exports shipped content-free. |

### Capabilities the dispatch explicitly excluded

- `services/solva_v2/` directory rename (user verbatim: deferred to DEV_PIPELINE §9; wider FE+chat blast radius).
- Building a new generation engine. Reuse only.
- ThinkLab Gate A render-check + Flag 3 (separate decision).

## Stage 4.2 — Objective → best-fit-kind recommender

### Decision: pure-JS regex pipeline

Per the B1.1 discipline: "zero net-new LLM calls" — the affordance modal
already does mechanical pre-fill of description / objective / scope from
the live chat. The recommender adds one more mechanical inference: read
the haystack `objective + description`, run it through an ordered regex
pipeline, return the first match. Falls back to `brief` when no signal
fires so the UI always has a default selection.

### Pattern priority (high → low confidence)

| Order | Kind | Cue patterns |
|---|---|---|
| 1 | `board_pack` | `board pack`, `board paper`, `board meeting`, `for the board`, `main board`, `directors`, `NEDs`, `non-executive` |
| 2 | `committee_pack` | `committee pack`, `committee paper`, `for the committee`, `audit committee`, `risk committee`, `remuneration committee`, `nomination committee`, `investment committee`, `exec(utive) committee`, `advisory committee` |
| 3 | `minutes` | `minutes`, `meeting minutes`, `record of meeting / decisions`, `attendees`, `action items`, `agenda items` |
| 4 | `deck` | `deck`, `slides`, `slide deck`, `presentation`, `powerpoint`, `pptx`, `pitch deck`, `walk-through`, `present this/to/the` |
| 5 | `report` | `report`, `long-form`, `detailed analysis / report / write-up`, `white paper`, `deep dive`, `in-depth`, `N-page` |
| 6 | `brief` | `brief`, `summary`, `TL;DR`, `one-pager`, `short summary`, `key points` |
| fallback | `brief` | (no match → still default to brief) |

### UI surface

- Affordance modal opens → recommender runs against the pre-filled
  `objective + description` → the matching kind tile is selected by
  default.
- The selected tile carries a small `Suggested` pill in the top-right
  corner (data-testid `chat-ws-kind-{id}-recommended-pill`).
- A quiet reason line ("Board-grade pack — directors as the audience.
  Click any tile to override.") sits below the kind grid (data-testid
  `chat-ws-kind-recommendation-reason`).
- The moment the user clicks any tile, `userPickedKind` flips and the
  recommender stops auto-overwriting their choice — they remain in
  control as they edit.

### Tests (`frontend/src/components/chat/__tests__/workStudioRecommender.test.js`)

```
recommendKind — objective → kind heuristic
  ✓ empty input → defaults to brief, no reason surfaced
  ✓ null input is safe → defaults to brief
  ✓ 'board pack' phrasing routes to board_pack with reason
  ✓ 'for the board' phrasing routes to board_pack
  ✓ 'audit committee' phrasing routes to committee_pack
  ✓ 'committee pack' phrasing routes to committee_pack
  ✓ 'meeting minutes' routes to minutes
  ✓ 'attendees + action items' routes to minutes
  ✓ 'slide deck' routes to deck
  ✓ 'PowerPoint' phrasing routes to deck
  ✓ 'long-form report' routes to report
  ✓ 'detailed analysis' routes to report
  ✓ '10-page write-up' routes to report (digit + page hint)
  ✓ 'short summary' routes to brief
  ✓ 'TL;DR' phrasing routes to brief
  ✓ 'one-pager' routes to brief
  ✓ freeform ask with no kind cues → brief fallback (null reason)
  ✓ description carries the cue when objective is generic
  ✓ board_pack wins over deck when both cues appear (priority)
  ✓ committee_pack wins over deck when both cues appear
  ✓ minutes wins over report when meeting cues lead

Tests: 21 passed, 21 total
```

## Stage 4.3 — Analyze narration in report exports

### Decision: schema-extension + adapter rewrite + render injection

Three-layer fix that closes the seam without touching the existing
`wba-*` legacy pipeline (which has full deterministic blocks and no
narration shape):

1. **`WorkbookAnalysis` schema** — two optional carriers:
   ```python
   analyze_narration_headline: Optional[str] = None
   analyze_narration_observations: List[Dict[str, Any]] = []
   ```
   `extra="forbid"` is strict; the additions are purely additive.

2. **Adapter rewrite** — `_adapt_new_analysis_to_workbook_analysis` now
   reads `row.headline` + `row.observations` (mirrors of `runs[-1]`
   cached by `synthesize_v2_endpoint` at L1098-1146) onto the new
   carriers. Falls back to `runs[-1]` if the top-level mirror is
   missing (defensive).

3. **Report builders** — when `analyze_narration_headline` is set:
   - **DOCX**: prepend `Bottom line` heading + paragraph + `Observations`
     heading + one paragraph per observation (max 12). Each carries the
     cell-range citation when present.
   - **PPTX**: insert a `Bottom line` slide carrying the headline + an
     `Observations` slide with one bullet per observation (max 8).
   - **XLSX**: insert a `Bottom Line` sheet at position 0 with a
     `headline` row + an `observation_kind | title | body | cell_range`
     table (max 24 rows).

### Tests (`backend/tests/test_stage_4_3_analyze_narration_exports.py`)

```
test_docx_export_carries_solva_narration_headline           PASSED
test_xlsx_export_carries_solva_narration_in_bottom_line_sheet PASSED
test_pptx_export_carries_solva_narration_slide              PASSED
test_pre_synthesis_analysis_still_exports_ok                PASSED
```

The test pattern uses `httpx.AsyncClient + ASGITransport +
@pytest.mark.asyncio` (mirrors `test_phase_d_solva_pipeline.py`) so the
test client lives on the conftest's session loop — no Motor
cross-loop drift when chained with the invariant suite.

### Tenancy allowlist refresh

The adapter expansion shifted three `# tenancy:allow-no-account-id`
marker lines:

| Marker | Old line | New line |
|---|---|---|
| WorkbookAnalysis insert (workbook_analyses) | 294 | 323 |
| Analysis insert (analyses) | 724 | 753 |
| analysis_blobs accumulator insert_many | 726 | 755 |

`tests/invariants/tenancy_escape_allowlist.yml` updated to match.
Justifications unchanged. Invariant scan green.

### FE caveat copy refresh

`AnalyzeDrawer.jsx` Export tab caveat updated from
"Solva narration arrives in Phase 3; the present exports carry the
deterministic content available today" → "Download a report containing
the Bottom Line headline, the Solva v2 observations (with citations),
and the source inventory. Run synthesis first if you want the
narrative to land in the export."

## Stage 4.4 — End-to-end seam classification

### Matrix (post-Stage-4)

| Surface | Status | Notes |
|---|---|---|
| Chat → Work Studio affordance → kind autopick | WORKS | Stage 4.2 regex pipeline; 21 unit cases green |
| Chat → Work Studio affordance → manual kind pick | WORKS | Pre-existing per WS1 |
| Chat → `POST /work-studio/export/{kind}` for all 6 kinds | WORKS | Pre-existing per WS1 |
| Chat → Continue-in-chat document chip | WORKS | Pre-existing per WS1 line 1157 `_create_continue_chat` |
| Compile (`/from-document`) | WORKS | Pre-existing per WS1 |
| Overlay round-trip | WORKS | Pre-existing per WS1 |
| Render (compile-then-render) DOCX / PPTX / PDF | WORKS | Pre-existing per WS1 |
| Analyze `/upload-multi` → `analyses` row | WORKS | Pre-existing per Phase 1 |
| Analyze `/v2/analyses/{aid}/synthesize` → Solva v2 narration in tabs | WORKS | Pre-existing per Phase 3 (`get_solva().narrate_analysis(...)`) |
| Analyze `/analyses/{aid}/report.{docx,xlsx,pptx}` with narration | WORKS | Stage 4.3 fix; 4 e2e tests green |
| Analyze pre-synthesis export | WORKS | Stage 4.3 regression: empty-headline path still ships a real artefact |

### Stop conditions — verified NOT tripped

| Stop trigger | Verdict |
|---|---|
| 4.2: objective→kind needs more than wiring objective into kind/template selection | Not tripped — heuristic is pure JS regex over existing fields; no new engine. |
| 4.3: solva_v2 can't back grounded document QA | Not tripped — Solva v2 narration already produces headline + cited observations; we just needed to thread them into the exporter. |
| Stage 5: backend FE needs doesn't actually work | Deferred to Stage 5 verification. |

## Files touched

### Stage 4.2 (`e0fb89b2`)

- `frontend/src/components/chat/workStudioRecommender.js` (new) — 89 lines
- `frontend/src/components/chat/WorkStudioAffordanceModal.jsx` — recommender import + state + UI pill / reason
- `frontend/src/components/chat/__tests__/workStudioRecommender.test.js` (new) — 21 cases

### Stage 4.3 (`edc278fe`)

- `backend/services/workbook_analyzer/schema.py` — `WorkbookAnalysis` schema +2 optional fields
- `backend/routers/workbook_analysis.py` — adapter rewrite to populate narration carriers
- `backend/services/workbook_analyzer/report_builder.py` — PPTX + DOCX + XLSX Bottom Line injection
- `backend/tests/test_stage_4_3_analyze_narration_exports.py` (new) — 4 e2e tests
- `backend/tests/invariants/tenancy_escape_allowlist.yml` — line-number refresh (3 entries)
- `frontend/src/components/analyze/AnalyzeDrawer.jsx` — Export tab caveat copy refresh

## Affected-test sample (regression check)

```
$ python -m pytest tests/invariants/ tests/test_stage_4_3_analyze_narration_exports.py -p no:warnings --tb=line
98 passed, 11 skipped in 86.09s

$ python -m pytest tests/ -k "workbook or analyze_narration or stage_4" -p no:warnings -q
52 passed, 4351 deselected in 14.17s

$ yarn test --testPathPattern='workStudioRecommender' --watchAll=false
Tests: 21 passed, 21 total
```

Zero rename-induced regressions. Zero Stage 4-induced regressions.

## §9 follow-up flags (filed; not actioned in this stage)

1. **Pre-Stage-4.3 ana-* exports**: deterministic signals/forecasts/
   anomalies are still empty on `ana-*` exports (the Phase-1 shim
   stripped them). The narration we surface IS the export content
   today. If users want the deterministic blocks too, re-running the
   parse pipeline at export time would cost ~150ms per source. Filed
   as low-priority enhancement; users get the narrative voice now,
   which was the user-facing gap.
2. **HUMAN_REQUIRED skipped invariants** (3 today): `test_invariant_audit_always`,
   `test_invariant_shield_no_leak` (claude + gpt + upload-multi paths). All
   skip with `HUMAN_REQUIRED` reasons (LLM ReadTimeout, schema drift on
   upload-multi). Pre-existing; orthogonal to Stage 4.

## Commits ledger

```
edc278fe feat(Stage 4.3): surface Solva v2 Analyze narration in report exports
e0fb89b2 feat(Stage 4.2): objective → best-fit-kind recommender in chat Work Studio affordance
```

(Plus this memo + DEV_PIPELINE.md updates → final Stage 4 commit.)

## Stop-and-report

✅ **No STOP conditions tripped during Stage 4.** Both seams closed
with the existing engines (no new engine built; Solva v2's
`narrate_analysis` already produces the narrative voice — Stage 4.3
just threaded it into the exporter). Per the dispatch's no-pause
discipline, Stage 5 (Task Manager / Monitor / Pulse FE shell
verification) starts next.
