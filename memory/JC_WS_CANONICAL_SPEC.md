# JC-WS Canonical Spec — Work Studio Build (Document Generation + Analyze)

**Source:** User dispatch — verbatim, no paraphrasing.
**Status:** ACTIVE — canonical source of truth for all Work Studio work (Document Generation + Analyze).
**Supersedes:** prior fragmented Work Studio briefs in handoffs / runway docs (e.g., Stage 4 framing). This file is the single reference; cite it from every JC-WS sprint memo's "Source of truth" line.
**UI rule:** No pixel of the current Generate Document UI changes during JC-WS. Adding REAL data to existing UI fields = BEHAVIOUR (allowed). Adding new UI elements not named by this spec = UI (STOP). See §UI-rule below.

> **Stage 4.2 recommender note**: the regex-based kind recommender shipped at commit `e0fb89b2` (Chat Work Studio affordance modal) stays as-is — a quiet "Suggested" pill on the chat affordance. JC-WS does NOT extend or rely on it for kind routing. **The KIND is selected by the journey the user enters — NOT inferred.**

---

## PART 0 — SHARED PRODUCTION-QUALITY BAR (applies to BOTH halves)

- UI is approved — do NOT redesign. Build output and behaviour, not chrome.
- Quality is a requirement, not a bonus. Outputs must be professional best-shape — structure, depth, formatting — good enough to forward to a board/executive without rework. "It generated something" is NOT done; "it generated something usable" is.
- Reuse existing engines (generators, exporters, solva_v2, workbook_analyzer). Do not rebuild.
- Every LLM call Shield-routed; account-scoped; audit + fail-closed unchanged.
- Vertical slices: prove ONE journey end-to-end with the ACTUAL artefact, then fan the proven pattern out. Do not build horizontally (all generators, then all exports, then all detail views).
- One sample per kind for inspection before bulk-generating — then proceed; not per-document approval.
- "Done" = the produced artefact opening cleanly and being usable, demonstrated — never a green test alone.

---

## PART A — DOCUMENT GENERATION

### Canonical design (locked — UI approved; build to the UX doc)

Document types: **Board Pack, Committee Pack, Minutes, Draft, Brief, Deck, Report**.

The KIND is selected by the journey the user enters — **NOT inferred**. Objective / scope / description shape CONTENT, not kind. (Do not build or expand a kind-recommender.)

### Engine reality (verified — this is wiring + quality, not a rebuild)

Generators exist and are wired to render/export (docx / pdf / pptx / brief / enhance, ~1,700 LOC). The objective (goal + context) is already injected into generation. Cards persist with a lifecycle.

### How the journeys are wired (do not assume this is obvious)

Five entry patterns. Each MUST produce a real, professional document.

**1. Source-material packs — Board Pack, Committee Pack, Minutes:**
- User selects documents already on the platform OR uploads new ones; MULTIPLE sources combine into ONE output (synthesise across all sources — not echo one).
- Cadence: one-off / recurring / scheduled. Recurring & scheduled produce a NEW card each cycle — never overwrite the prior pack; the history of compiled packs is preserved.
- Wire: gather sources → kind generator → professional structured document → card in Draft.

**2. Blank-start — Reports, Decks:**
- User types or pastes their own content into the editor, then prompts Akki to enhance/expand it.
- Wire: editor content is the seed → enhance pass refines/expands → card in Draft.

**3. Brief — three source origins (user picks ONE):**
- (a) a chat artefact, (b) a Think Lab session, (c) documents + signals + cycle data on-platform.
- User provides a description, the objective it should serve, and the scope it should cover.
- Wire: resolve the chosen source → generate brief against description/objective/scope → card in Draft.

**4. Enhance an existing document — Minutes, Reports, Decks:**
- User uploads the document to improve + custom instructions; Akki applies the instructions to the file.
- Wire: apply instructions via enhance → visibly improved doc → downloadable as DOCX or PDF.

**5. Draft — create and edit content with Akki assistance in the editor.**

### Production-quality bar (what "real output" means per kind)

Each kind produces a professional, well-structured document — never a sparse shell:

- **Board / Committee Pack**: cover, contents/agenda, sectioned content SYNTHESISED from ALL sources, executive-grade prose; DOCX / PPTX / PDF.
- **Minutes**: structured — attendees, agenda items, decisions, actions with owners — drawn from the sources; DOCX / PPTX / PDF.
- **Brief**: description-driven, objective-serving, scope-bounded; PDF / DOCX.
- **Deck**: real, presentable slides built from the source material; PPTX.
- **Report**: structured report from uploaded docs + Akki content.
- **Enhanced docs**: VISIBLY improved against the instructions (clarity, completeness, quality); DOCX / PDF.

Produce best-shape; surface ONE sample per kind for inspection, then proceed.

### Lifecycle + detail view (must be real, not placeholder)

Every generated document is a card under its type, entering as **Draft**:
- **Draft** — generated, not yet opened by the user.
- **In Review** — opened, not yet committed.
- **Committed** — explicit, final; LOCKS the document from further edits.

Opening a card → detail view, where the user can:
- edit the document title;
- see REAL, computed values: a confidence score, the source documents used, and the period covered (these are the basis to trust/question/refine — they must be real, not placeholder text);
- review RECOMMENDATIONS Akki has surfaced and accept them as refinements (recs are GENERATED, not hardcoded; accepting one applies the refinement to the document);
- commit — a deliberate, final action that locks the document.

### Export wizard (shared — Analyze's "Finish & export" routes here)

Export is a WIZARD, not a one-click dump. The user chooses the export objective and the format (DOCX / PPTX / PDF; enhanced documents export as DOCX / PDF). It produces the downloadable file in the chosen format. **This is the SINGLE export path for the whole module — build it once, here.** Analyze hands its finished analysis into this same wizard as source material; Analyze builds no exporter of its own.

### Persistence / revisit

Cards persist per-account under their type. A document stays editable through Draft → In Review until Committed (which locks it). Reopening a non-committed card resumes work — the document-side equivalent of revisiting an analysis thread. One mental model across the module: work persists as cards you reopen and continue until you finalise (commit a document / synthesise + export an analysis).

### Proving slice (show the real document)

**Board Pack end-to-end** — select MULTIPLE source docs → set cadence one-off → generate → a REAL, professional, multi-section DOCX (and PPTX/PDF) lands as a card in Draft → open the detail view showing real confidence + real source list + real period → review real Akki recommendations, accept one (the refinement applies) → Commit (locks) → export via the wizard. Show the ACTUAL produced document. STOP and show before fanning out.

### Fan out (after the Board Pack slice is shown)

Replicate the proven pattern across Committee Pack, Minutes, Brief (3-source selector), Deck, Report, Draft, and the three enhance flows (minutes / reports / decks). Reuse the slice pattern; do not re-architect per kind.

### Acceptance (Document Generation)

A user runs each journey and receives a professional, committable, downloadable document per the promises list; the lifecycle and commit-lock work; the detail view shows real confidence / sources / period; recommendations generate and apply on accept; the export wizard produces clean files in the chosen format. The bar is "forward-to-a-board good," not "a document appeared."

---

## PART B — ANALYZE (NotebookLM-style analysis workspace, drawer)

### Canonical design (locked — build to this, do not redesign)

A right-side **DRAWER** (reuse the existing DocumentDrawer/Sheet chrome — one shell across both halves of Work Studio). Inside: the built capabilities run BEHIND the surface and post their outputs as **HIGHLIGHTS** (tweet-type cards, each tagged by the capability that produced it) grouped under **TOPICS**. A prompt tool and data-aware question tips dock at the bottom. "Finish & export" is a wizard that hands the analysis to Document Generation's export wizard — Analyze builds no exporter of its own.

### Engine reality (verified — this is wiring + UX, not a new engine)

Built endpoints already exist on an analysis: `/forecast`, `/simulate` (Monte Carlo), `/signals/extract`, `/anomalies`, plus `narrate_analysis` (human language) and `refuse_to_decide` (anti-fabrication guard). Persistence exists: `workbook_analyses` is a per-account list; each analysis ACCRETES artefacts, carries notes, has a session lifecycle.

### How the capabilities are wired (do not assume this is obvious)

**Validate / Forecast / Simulate / Extract are PRE-BUILT capabilities, NOT menu items.** They run behind the surface. Wire them like this:

**Output path (same for every capability):**
- capability endpoint → `narrate_analysis` (plain language) → a HIGHLIGHT card tagged with the capability (validate / anomaly / forecast / extract) → grouped under a TOPIC → accreted onto the analysis in `workbook_analyses` → rehydrates on reopen.
- Highlights ARE the narrated outputs of the capabilities. Do not hardcode highlights; they are generated.

**Trigger path A — initial run (objective + data shape decide what runs):**
- Always on first pass: **Validate** (integrity / totals reconcile / anomalies / schema) and **Analyze** (descriptive trends & insights) — these work on almost any sheet.
- Conditional: **Forecast** (only if an ordered/time series exists), **Extract** (if the objective names a subset / region / metric).
- Do NOT auto-run **Simulate** — it needs a user-defined scenario, so it is follow-up-driven.
- The stated objective is a light router to which capabilities fire first — a capability selector for the opening pass, NOT a document-kind selector.

**Trigger path B — follow-up (prompt + question tips):**
- A natural-language ask or a tapped tip routes to the right capability with the right params ("forecast without the outlier" → `/forecast` excluding that row; "simulate East down 40%" → `/simulate` with that scenario).
- Each follow-up result accretes as a NEW highlight — nothing overwrites.
- **Degradation rule**: if intent routing is uncertain, fall back to letting the user confirm the operation. Never a dead end; never a wrong silent run.
- **Refusal guard** MUST be wired into the ask path, not just the first run: if the data can't support the ask (forecast off 3 months; "why did X drop" with no driver columns), say so, name what's missing, suggest what to add — do NOT fabricate. Follow-ups are where a weak system starts inventing; this is the guardrail.

**Preconditions** (confirm exact params from each endpoint signature — do not guess):
- Forecast needs an ordered/numeric series; Simulate needs a scenario variable; Anomalies need a numeric column; Extract needs a target. When the objective implies a capability but its precondition isn't met, surface a gentle prompt ("point me at the time column and I'll forecast") rather than failing or faking.

### Subtle user note (discoverability without a menu)

Because there is no verb menu, the user needs a quiet signal of what Analyze can do. Add a subtle, plain-language cue — pick one, keep it light:
- Prompt placeholder: **"Ask Akki to forecast, simulate a what-if, validate, or dig into a region — in plain language."**
- Or a one-line note under the highlights on first open: **"Akki checked your data, flagged what's odd, and projected the trend. Ask it to simulate a scenario, focus a region, or pull a subset."**

Question tips must be DATA-AWARE (generated from the actual sheet and findings), not a static list — they double as teaching the user the range.

### Persistence / revisit

The per-account analyses list IS the thread history. Reopening an analysis rehydrates its accreted highlights, topics, and notes; the prompt stays live so the user continues — runs another capability, adds context, re-asks. Recurring uploads each keep their own analysis.

### Export

"Finish & export…" opens the Document Generation export wizard (user chooses export objective + format: DOCX / PPTX / PDF). Analyze passes the finished thread as source material; it does not build its own exporter.

### Proving slice (demonstrate with a real spreadsheet)

Upload Q3 sales + objective "check before forwarding · forecast Q4" → first run auto-surfaces Validate + Analyze highlights (totals reconcile, East anomaly, broken row) and, since a time series exists, a Forecast highlight → user taps "simulate East staying down" → a new simulate highlight accretes → user closes, reopens → thread is intact, asks one more → Finish → hands to the export wizard. Show the ACTUAL highlights and the reopened thread. **CFO test**: would this let a non-analyst trust and forward the sheet?

### Acceptance (Analyze)

A non-analyst uploads a sheet, gets real plain-language findings surfaced from the built capabilities, asks follow-ups that route correctly (or degrade gracefully) with the refusal guard live, reopens the thread later to continue, and exports through Document Generation. The workspace is a workspace.

---

## STANDING RULES (both halves)

- Reuse the existing engines (generators, exporters, solva_v2, workbook_analyzer) — do not rebuild.
- Every LLM call Shield-routed; account-scoped; audit + fail-closed unchanged.
- Confirm real endpoint params before wiring — do not guess capability inputs.
- Report by execution evidence: show the produced document / the real highlights + reopened thread. "It works" is the artefact opening cleanly and being usable, not a green test.
- Escalate exactly two things: a genuine STOP (an engine can't produce the required output) or a real architectural fork. Everything else is yours within these rules.

---

## ARTEFACT DELIVERY

Save proving-slice artefacts under `/app/memory/jc_artifacts/` with descriptive filenames:

- `JC-WS-A-BoardPack-proving-slice.docx` (+ `.pptx`, `.pdf`)
- `JC-WS-A-CommitteePack-sample.docx`
- `JC-WS-A-Minutes-sample.docx`
- `JC-WS-A-Brief-sample.pdf`
- `JC-WS-A-Deck-sample.pptx`
- `JC-WS-A-Report-sample.docx`
- `JC-WS-A-Enhanced-sample.docx` (before + after)
- `JC-WS-B-Analyze-Q3sales-highlights-and-reopen.json` (the highlights + reopened thread structure) + the exported file the wizard produced.

Each sample is the actual produced document. The user opens these to verify "forward-to-a-board good."

---

## EXECUTION ORDER

1. **PART A proving slice — Board Pack end-to-end.** Show the actual document. STOP. Surface for user inspection before fanning out.
2. **PART A fan-out** — replicate proven pattern across the remaining kinds + enhance flows. ONE sample per kind to `/app/memory/jc_artifacts/`. Surface a manifest of all samples for inspection. STOP before bulk-availability rollout (if "bulk rollout" even means anything separate — likely not, since the proven pattern is the rollout).
3. **PART B proving slice — Analyze Q3 sales journey end-to-end.** Show the actual highlights + reopened thread + exported file. STOP. Surface.
4. **Shared export wizard** — confirmed built once during Part A, surface its proof point inside Part A.
5. **Acceptance pass** — run both halves' acceptance criteria as written and report each one as pass/fail with the evidence artefact.

---

## SPRINT MEMO + PIPELINE

- Per-slice sprint memos under `/app/memory/sprints/`:
  - `JC_WS_A_BOARD_PACK_PROVING_SLICE.md`
  - `JC_WS_A_FAN_OUT.md`
  - `JC_WS_B_ANALYZE_PROVING_SLICE.md`
- Each memo MUST cite this file (`/app/memory/JC_WS_CANONICAL_SPEC.md`) as its "Source of truth" line at the top.
- DEV_PIPELINE.md §1/§4/§5/§9 updated BEFORE each memo (Maintenance Protocol).
- pipeline-log-sync exit 0 maintained.
- No new invariants needed unless a real fitness regression appears.

---

## BACKLOG PARKED (do not touch this phase)

- Auto-trigger Work Studio affordance from Shield turn classification (future, needs proper modeling per user direction)
- `services/solva_v2/` directory rename
- `solva_phase_d_sessions` collection rename
- URL canonicalization for `/api/contexts/{cid}/solva/v2/*`
- `synisense_observability` mount investigation
- Branch protection on `main`
- Phase 5.5.3 broader-suite drift triage
- ThinkLab Gate A — comes AFTER JC-WS closes per user's ordering (Work Studio → ThinkLab → Chat)

---

## USER'S ANCHOR (verbatim, hold this lens throughout)

> "The product primary objective is not secondary dynamic that have been amplified. It's the stated user experience and function. Needs to avoid loops that distract the core objective."

> "Avoid creating technical loops that detracts you from the core job."

> Real-user feedback (the one this phase has to retire): "your workspace isn't a workspace, nothing works."

**Build the workspace. Show the artefacts.**

---

## UI-RULE (Hard constraint — added 2026-06-25 pinning; SCOPED 2026-06-25)

**Scope clarification (2026-06-25):** the UI-untouched rule applies **only to the Generate Document submodule** of Work Studio. The Analyze submodule UI is OPEN — build per Part B of this spec (highlights-as-cards, docked prompt tool, data-aware question tips, Finish-&-export wizard handoff) without further user approval.

**For the Generate Document submodule** (CompilationWizard, CreateArtefactModal, DocumentOverlay, DocumentCardsSection, IntelligenceCard, AIRevisionPanel, ExportModal, BlockComposer):
- No JSX structural changes; no CSS/Tailwind changes that alter visible layout, spacing, typography, or colors.
- No new buttons / labels / placeholders / tooltips added unless the user-supplied spec EXPLICITLY names them.
- Adding REAL data to fields the UI already renders (e.g., real confidence score where placeholder text exists today, real source list where placeholder exists, real recommendations where stub list exists) is BEHAVIOUR not UI — that's allowed and required.

**Decision rule when in doubt (Generate Document only):** if your change would alter what a user sees with empty state / no data, it's UI — STOP and surface. If your change only alters what appears once real data flows in (because the UI element already exists but currently shows placeholder), it's BEHAVIOUR — proceed.

If any JC-WS Generate Document journey requires a UI element that doesn't already exist (e.g., the Brief 3-source selector — does that UI exist today?), STOP and surface BEFORE building it. The user will direct whether to (a) add the missing UI element per the UX doc, or (b) defer that journey to a later phase.

**For the Analyze submodule** (AnalyzeDrawer, WorkStudioAnalyze, AnalyzeJournal, and any new components added under `frontend/src/components/analyze/`):
- The 4 MISSING items identified in the inventory (highlights-as-cards-grouped-under-topics, docked free-text prompt tool, data-aware question tips strip, Finish-&-export wizard handoff) are now **UNBLOCKED** and must be built per Part B of this spec.
- The spec-allowed "subtle plain-language cue" docks on the prompt tool surface as the placeholder.
- No further user approval needed for Analyze surfaces.

Inventory MUST be output to `/app/memory/audit/JC_WS_ui_inventory.md` before the Board Pack proving slice begins. Done.

---

## Future work surfaced during JC-WS

- **LLM_MODELS_REFRESH** (NEXT SPRINT) — refresh the model selection across Shield-routed LLM paths to include the latest Anthropic Claude / OpenAI GPT / Gemini releases. Per-context canonical model per task (chat default · deep-analysis · narration · doc-generation · classification). Pinned at `/app/memory/DEV_PIPELINE.md` §9. **DO NOT action during JC-WS** — would confound the "forward-to-a-board good" verdict.
