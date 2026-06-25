# JC-WS Phase 1 + Phase 2 — Proving Slices

> **Source of truth:** `/app/memory/JC_WS_CANONICAL_SPEC.md`
> **Closed:** 2026-06-25
> **Artefacts:** `/app/memory/jc_artifacts/`

Two proving-slice journeys landed today, both producing REAL artefacts
(not assertions) per the user's "report by evidence" rule.

---

## Phase 1 — Board Pack proving slice (Part A) — 10/10 GREEN

### What was fixed

**Fix #1 — Shield timeout on confidence scoring.** The
`_HTTPAdapterBase._call` in `contracts/_adapters/_http_client.py`
used a global 5s timeout for every internal hop. `shield_invoke`
carries an LLM call end-to-end (de-id → provider → re-id → audit →
receipt) and routinely needs 30-90s on board-pack-sized prompts. The
3-retry ReadTimeout loop surfaced as `confidence_pct=None` on
committed documents. **Decision:** per-method timeout override map
keyed on `method_name`. `shield_invoke` → 120s. Everything else
keeps the 5s discipline.

**Fix #2 — Commit-time tenancy widening.** `routers/work_studio_overlay.py`
commit-path was reading `db.documents` with a strict
`account_id == ctx["account"]["id"]` filter. Context-shared seed
docs (account_id=None / missing) that the export-time
`_resolve_source_blobs_for_scoring` widens for were excluded. Result:
`source_blobs=[]` → `confidence_score_skipped_no_sources=True` on
commit. **Decision:** the canonical lifecycle store is
`work_studio_exports` (DocumentOverlay reads from this collection);
the legacy `documents` mirror is partial and does NOT carry the
Work-Studio commit fields. Brought commit-time blob lookup in line
with export-time using the same `$or: [account_id=X, None, missing]`
widening. Also migrated `scripts/jc_ws_a_board_pack_proving_slice.py`
to read lifecycle/intel from `work_studio_exports` (instead of the
partial `documents` mirror) — this is what the UI reads, so the
proving slice should read the same store.

**Fix #3 — PPTX renderer for board_pack.** Canonical spec is explicit:
"Board / Committee Pack: cover, contents/agenda, sectioned content
SYNTHESISED from ALL sources, executive-grade prose; DOCX / PPTX / PDF."
PPTX was missing. **Decision:** new `render_pack_pptx` in
`services/work_studio_export.py`. Takes the SAME report-shaped
content_dict the DOCX/PDF paths consume; converts each section's
paragraphs to slide bullets via first-sentence-per-paragraph (cap 6,
220 chars). Slide order: cover → contents → exec summary →
one slide per section → recommendations → sources. No new engine;
reuses existing `_pptx_add_text`, `_pptx_set_slide_bg`, `PPalette`.
Wired into the dispatcher at
`routers/work_studio_export.py::_run_export`.

**Fix #4 — JSON parse hardening on Pass-2 LLM emissions.** Sonnet
occasionally emits malformed JSON at 16K+ char prompts (trailing
commas, missing delimiters; the leading ```` ```json ```` fence
sometimes ships without a closing fence). `_strip_json_fence`
now matches a leading-only fence too; `_try_parse_json` falls through
to `json_repair` (added to `requirements.txt`) for deterministic
syntax repair. Repair NEVER fabricates content — only fixes syntax.

**Fix #5 — Edit-lock probe in proving slice.** Canonical spec
promise: "Committed — explicit, final; LOCKS the document from
further edits." Added a `PATCH` probe after commit; asserts `409`.
Surfaces the write-lock as a tested acceptance row.

### Acceptance ledger

```
[✓] REAL confidence score computed                    pct=60
[✓] REAL source list (sources_count > 0)              16 docs
[✓] REAL period                                       Q3 2025
[✓] REAL recommendations (count > 0)                  8
[✓] Accept-one-recommendation flow works              applied_count=1
[✓] Commit-lock works                                 lifecycle_state='committed'
[✓] Committed document is write-locked (PATCH→409)    edit_locked_probe_status=409
[✓] DOCX export shipped (>20 KB)                      42 491 bytes
[✓] PDF export shipped via wizard                     31 277 bytes
[✓] PPTX export shipped via wizard                    39 916 bytes
```

### Artefacts

| File | Bytes | What it proves |
| --- | --- | --- |
| `JC-WS-A-BoardPack-proving-slice.docx` | 42 491 | DOCX renderer end-to-end |
| `JC-WS-A-BoardPack-proving-slice.pptx` | 39 916 | NEW PPTX renderer (Fix #3) |
| `JC-WS-A-BoardPack-proving-slice.pdf` | 31 277 | PDF renderer + confidence path |
| `JC-WS-A-BoardPack-detail-view-state.json` | 19 812 | Three lifecycle states (pre-accept → post-accept → post-commit) with real confidence pct, intel report, edit-lock probe |
| `JC-WS-A-BoardPack-acceptance-report.json` | 1 954 | 10/10 ledger |

---

## Phase 2 — Analyze proving slice (Part B) — 7/7 GREEN

### What was built

Per canonical spec Part B, the Analyze submodule UI is OPEN — built
the FOUR missing elements on top of the existing AnalyzeDrawer:

**(d) Highlights-as-tweet-cards grouped under topics.** New
`HighlightsWorkspace.jsx` (≈340 lines) renders a closed-vocabulary
topic grouping (trend / anomaly / forecast / simulate / target /
validate / refusal). Each topic has a coloured badge + count chip.
Each card carries title (≤90 chars) + body (140-260 chars) + citation
hint + confidence pill. Refusal cards get a rose-tinted border + an
"Can't answer" topic so the user sees what's missing rather than a
fabricated answer.

**(e) Docked free-text prompt.** Bottom-of-drawer dock that's ALWAYS
visible. ⌘↵ to send. Subtle "Plain language works. Capabilities run
under the surface; you see the highlight." cue — verbatim from the
spec.

**(f) Data-aware question tips strip.** Above the dock (when
highlights exist) AND as the empty-state primary CTA. 5 chips by
default. Tips are derived from actual sheet columns + the recent
highlights on the thread, with intent classification on each chip
(forecast / simulate / extract / validate / anomaly). Shield-routed;
deterministic column-derived fallback when Shield is unreachable.

**(g) Finish & export wizard handoff.** Top-right CTA in the
Workspace header. Composes a `description` from the accreted
(non-refused) highlights and returns it to the FE. The FE feeds it
to the existing `/api/contexts/{cid}/work-studio/exports` POST —
SAME wizard the Document Generation pipeline uses. No fabrication:
if no highlights have accreted, returns `ok=false, reason=no_highlights`.

### Backend endpoints

```
GET  /api/workbook/v2/analyses/{aid}/tips
POST /api/workbook/v2/analyses/{aid}/ask
POST /api/workbook/v2/analyses/{aid}/finish
```

All three are Shield-routed (`analyze_workspace.intent_router`,
`analyze_workspace.narrate`, `analyze_workspace.tips`), tenant-scoped
(account_id boundary same as the existing `/v2/analyses/{aid}` route),
and use typed Pydantic response models (`AnalyzeWorkspaceAskResponse`,
`AnalyzeWorkspaceTipsResponse`, `AnalyzeWorkspaceFinishResponse`) in
`contracts/responses.py`. Polymorphic-response-route ratchet stays
green at 45 routes.

### Intent classifier rules (locked in `services/analyze_workspace/ask.py`)

- DECISIVENESS RULE — when the question contains an explicit action
  verb (forecast / simulate / extract / validate / anomaly), USE that
  verb. Don't refuse for "ambiguity" when the verb is explicit.
- Refuse ONLY when: (a) the question references a column / metric NOT
  in the loaded sheet, (b) the question implies time-series analysis
  but no date column exists, (c) the data is insufficient (e.g. fewer
  than 3 periods for a forecast), or (d) the question references
  category values NOT shown in the column sample values.
- Five short refusal reason codes carried verbatim onto the highlight
  card: `no_time_series` · `missing_target` · `out_of_scope` ·
  `ambiguous_intent` · `insufficient_data`.

### Acceptance ledger

```
[✓] Auto-run highlights seeded (Path A: Validate + Analyze + Forecast)
[✓] Data-aware tips returned from /tips                (5 chips, all data-grounded)
[✓] POST /ask (simulate) accretes a non-refusal highlight  (intent=simulate)
[✓] POST /ask (out-of-scope) surfaces a REFUSAL highlight (topic=refusal)
[✓] Close + reopen — thread intact (initial + 2 follow-ups = 5)
[✓] Continued accretion — one more highlight added
[✓] Finish & export composes brief from highlights (no fabrication)
```

### Artefacts

| File | What it proves |
| --- | --- |
| `JC-WS-B-Analyze-initial-run-highlights.json` | Path A: 3 auto-run highlights seeded across trend/forecast/validate |
| `JC-WS-B-Analyze-followup-simulate-highlight.json` | Free-text question → intent=simulate, topic=simulate, real narration |
| `JC-WS-B-Analyze-refusal-guard-evidence.json` | Out-of-scope question (Pluto revenue) surfaced as a refusal card with `topic=refusal` |
| `JC-WS-B-Analyze-reopened-thread-state.json` | After close+reopen the thread has all 5 highlights (initial + 2 follow-ups) intact |
| `JC-WS-B-Analyze-finish-export-payload.json` | Composed 1122-char brief from 5 non-refused highlights ready for the export wizard |
| `JC-WS-B-Analyze-acceptance-report.json` | 7/7 ledger |
| `JC-WS-B-Analyze-drawer-screenshots/01-workspace-with-highlights-and-dock.jpg` | FE smoke: Workspace tab default-active, 6 highlight cards across 4 topic buckets, 5 tip chips, docked prompt, Finish & export CTA |

---

## What's NOT in this dispatch

- **Phase 3** (Generate Document fan-out across Committee Pack, Minutes,
  Brief, Deck, Report, Draft + 3 enhance flows). The Board Pack pattern
  is now proven and can be replicated kind-by-kind with ONE artefact
  per kind.
- **`LLM_MODELS_REFRESH`** — pinned to next sprint per user directive.
- **`services/solva_v2/` rename + `solva_phase_d_sessions` collection
  rename** — backlog.
- **Brief 3-source origin selector UI** — flagged in the UI inventory
  as MISSING; user direction pending.

---

## Files touched

### New files
- `services/analyze_workspace/__init__.py`
- `services/analyze_workspace/ask.py`
- `services/analyze_workspace/tips.py`
- `frontend/src/components/analyze/HighlightsWorkspace.jsx`
- `scripts/jc_ws_b_analyze_proving_slice.py`
- `memory/sprints/JC_WS_PHASE_1_2_PROVING_SLICES.md` (this file)

### Edited files (BE)
- `contracts/_adapters/_http_client.py` — `_PER_METHOD_TIMEOUT_S` map
- `routers/work_studio_overlay.py` — commit-path tenancy widening
- `routers/work_studio_export.py` — board_pack PPTX dispatch + json_repair fallback
- `services/work_studio_export.py` — `validate_content` accepts pack kinds + `render_pack_pptx`
- `services/synisense/config.py` — Shield allow-list `analyze_workspace.*`
- `routers/workbook_analysis.py` — 3 new endpoints
- `contracts/responses.py` — 5 new typed response shapes
- `scripts/jc_ws_a_board_pack_proving_slice.py` — read from canonical store + edit-lock probe + cosmetic byte-len fix
- `requirements.txt` — `json_repair==0.61.0`

### Edited files (FE)
- `frontend/src/components/analyze/AnalyzeDrawer.jsx` — new "Workspace" tab as the default
