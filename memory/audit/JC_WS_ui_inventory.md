# JC-WS UI Inventory — what already exists vs what's missing

**Source of truth:** `/app/memory/JC_WS_CANONICAL_SPEC.md`
**Date:** 2026-06-25
**Purpose:** Per the UI-untouched hard rule (pinned 2026-06-25), every JC-WS journey is inventoried here against the existing FE. Each surface is classified EXISTS-TODAY (wire behaviour only) or MISSING (STOP and surface). The user directs whether to add the missing UI per the UX doc or defer the journey.
**Decision rule:** if a change would alter empty-state visuals, it's UI (STOP). If it only changes what appears once real data lands in an existing UI shell, it's BEHAVIOUR (proceed).

---

## Part A — Document Generation journeys

### Journey 1 — Source-material packs (Board Pack · Committee Pack · Minutes)

| Surface | Status | Evidence | Behaviour delta needed? |
|---|---|---|---|
| Multi-source document selector | ✅ EXISTS-TODAY | `CompilationWizard.jsx:117-119, 207-264` — Step 2 multi-select via `Set`, fans across Akki-generated artefacts (`/briefings/aggregates`) AND uploaded documents (`/documents?origin=upload`). "Select all ready" shortcut + nested upload affordance. | YES — BE wiring already in progress: thread `source_ids` from `compilations` row → `_run_export` via `source_document_ids` field. |
| Cadence picker (one-off / recurring / scheduled) | ✅ EXISTS-TODAY | `CompilationWizard.jsx:136-138` — Step 4 `cadenceKind` state with `one_off / recurring / scheduled`. Recurring carries an `interval` (weekly/fortnightly/monthly/quarterly); scheduled carries `scheduled_at`. | YES — persist `cadence` on the export row (already partially wired). Recurring/scheduled cycle scheduler is OUT OF SCOPE for the proving slice (user said scheduler is separate). |
| Kind selection (board_pack / minutes / committee_pack / deck / report / briefing) | ✅ EXISTS-TODAY | `CompilationWizard.jsx:36-43` — all 6 artefact types in `ARTEFACT_TYPES`. Step 1 radio. | NO behaviour delta — wizard already calls `/start` which routes by `artefact_type`. |
| Format picker (DOCX / PPTX / PDF) | ✅ EXISTS-TODAY | `CompilationWizard.jsx:140` — `formats` state. Per-type defaults at `:97-104` (board_pack=docx, deck=pptx, etc.). | NO behaviour delta. |
| Contributors step | ✅ EXISTS-TODAY | `CompilationWizard.jsx:134` — Step 3 `excludedContribIds`. Derived from source contributors. | NO behaviour delta. |

### Journey 2 — Blank-start (Reports · Decks)

| Surface | Status | Evidence | Behaviour delta needed? |
|---|---|---|---|
| Blank-source entry on Create modal | ✅ EXISTS-TODAY | `CreateArtefactModal.jsx:199` — radio option `Blank — I'll write it from scratch.` | NO. |
| Editor for in-place composition (Reports / Decks) | ✅ EXISTS-TODAY | `BlockComposer` mounted via `StudioComposerPage.jsx` at `/app/studio/composer/:kind/:artefactId`. Deck renders slide-mode by Heading-1 boundaries. | YES — the JC-WS Blank-start spec says "user prompts Akki to enhance/expand it." Need to confirm the in-editor "ask Akki to enhance" affordance exists in BlockComposer; if not, this is a MISSING UI subsidiary surface. **NEEDS VERIFICATION** below. |

### Journey 3 — Brief (REVISED 2026-06-25 per JC-WS Phase 3 dispatch)

> **The original "3 source origins (chat artefact · ThinkLab session · docs+signals+cycle)" model is
> SUPERSEDED.** That spec described plumbing as a user choice — it is removed, not deferred. The
> revised canonical model has TWO paths: **(3a) ORIGIN-TRIGGERED** briefs (built WITH each module
> on Solva / Monitor / Task Manager — net-new per surface, not a Work Studio picker entry) and
> **(3b) IN-STUDIO** briefs (uploads + Akki-fetch-by-name, gated by retrieval maturity). Source of
> truth: `/app/memory/JC_WS_CANONICAL_SPEC.md` Journey 3. The original MISSING items below are
> closed out as SUPERSEDED.

| Surface | Status | Evidence | Behaviour delta needed? |
|---|---|---|---|
| Brief kind entry | ✅ EXISTS-TODAY | "Create a Brief" button at `WorkStudio.jsx:191`; `CompilationWizard.jsx:42` lists `briefing`. | NO. |
| Source picker: uploads (document journal + fresh upload) | ✅ EXISTS-TODAY | `CreateArtefactModal.jsx:198-202` `external_document` path; document journal AddToWorkStudio path exists. | NO behaviour delta — this is the "uploads first" path of revised Journey 3b. |
| **Source picker: Add context from Akki (name it → fetch by BM25)** | 🟡 **GATED BY RETRIEVAL QUALITY** | New input. Wire to existing chat BM25 / `search_document_journal`; do NOT build new search. Ship only after ≥2/3 named-context test cases return RELEVANT material per Phase 3 retrieval-quality gate. | **BUILD UPLOADS PATH FIRST; AKKI-FETCH WAITS ON GATE.** |
| ~~Source picker: chat artefact~~ | ⛔ **SUPERSEDED 2026-06-25** | Original spec model removed. Chat-originated briefs land in Journey 3a (origin-triggered on the chat surface) when chat module gets its "brief this" affordance — not a Work Studio picker. | N/A — closed out. |
| ~~Source picker: ThinkLab session~~ | ⛔ **SUPERSEDED 2026-06-25** | Original spec model removed. ThinkLab-originated briefs land in Journey 3a (origin-triggered on the ThinkLab surface) when ThinkLab module gets its "brief this" affordance. | N/A — closed out. |
| ~~Source picker: docs + signals + cycle~~ | ⛔ **SUPERSEDED 2026-06-25** | Original spec model removed. Signals/cycle-originated briefs land in Journey 3a (origin-triggered on Monitor / Task Manager). | N/A — closed out. |
| Description / Objective / Scope inputs | ✅ EXISTS-TODAY | `WorkStudioAffordanceModal.jsx` collects all three (Stage 4.2 work). | NO. |

### Journey 4 — Enhance existing document (Minutes · Reports · Decks)

| Surface | Status | Evidence | Behaviour delta needed? |
|---|---|---|---|
| Enhance modal (upload + instructions) | ✅ EXISTS-TODAY | `EnhanceModal.jsx` — two paths share the same shape (kind ∈ minutes/report/deck). | NO behaviour delta. |
| Upload affordance | ✅ EXISTS-TODAY | Inside EnhanceModal. | NO. |
| Instructions text input | ✅ EXISTS-TODAY | Inside EnhanceModal. | NO. |
| Output (DOCX / PDF) | ✅ EXISTS-TODAY | `enhance` endpoint already produces both formats per spec. | NO. |

### Journey 5 — Draft (create-and-edit with Akki assistance)

| Surface | Status | Evidence | Behaviour delta needed? |
|---|---|---|---|
| "+ New draft" entry | ✅ EXISTS-TODAY | `WorkStudio.jsx:182, 191` — drafts_briefs tab. | NO. |
| Editor with Akki assistance | ✅ EXISTS-TODAY | `BlockComposer` (same as Blank-start path). Drafts file under `draft` category. | Same caveat as Journey 2: in-editor "ask Akki" affordance needs verification. |

---

## Document Generation — Lifecycle + Detail View + Export

| Surface | Status | Evidence | Behaviour delta needed? |
|---|---|---|---|
| Card list under each kind tab | ✅ EXISTS-TODAY | `DocumentCardsSection.jsx` + `WorkStudio.jsx` tabs. Card rows render age + readiness + state badge. | NO. |
| **Lifecycle states: Draft / In Review / Committed** | ✅ EXISTS-TODAY | `DocumentOverlay.jsx:71-79` — exact strings: `Draft`, `In Review`, `Committed`. Status colors amber/sky/emerald. | NO behaviour delta on labels — the lifecycle_state field must populate. |
| Edit document title | ✅ EXISTS-TODAY | `DocumentOverlay.jsx` toolbar — `onTitleChange` already wired (`:345`). | NO. |
| **Real confidence score (RAG band + %)** | ✅ EXISTS-TODAY | `DocumentOverlay.jsx:543-589` — IntelligenceCard. Shows `conf %` chip + `RAG_BORDER[band]` + tooltip with `confidenceRationale + confidenceScoredAt`. Empty state: "Intelligence report not captured for this document." | YES — BE wiring: ensure `intelligence_report.confidence_pct + confidence_band + confidence_rationale + confidence_scored_at` populate for ana-* exports. Stage-4-prep work already partial. |
| **Source documents used** | ✅ EXISTS-TODAY | `DocumentOverlay.jsx:553` — "Synthesised from N sources". Full modal shows `audit.source_document_ids[]` (`:699-701`). | YES — BE wiring: persist `source_document_ids` on the export row. **Already partial via my edits in the prior turn (held).** |
| **Period covered** | ✅ EXISTS-TODAY | `DocumentOverlay.jsx:556` — `report.period`. | YES — BE wiring: persist a `period` field on the intelligence_report (derive from the source docs' date range or the user's scope text). |
| **Recommendations panel** | ✅ EXISTS-TODAY | `DocumentOverlay.jsx:685-693` — renders `report.recommendations[]` with `r.text` + `r.addressed` checkmark. Commit confirmation checks `unaddressed = report.recommendations.filter(r => !r.addressed)`. | YES — BE wiring: real recommendations generated at compile time and persisted to `intelligence_report.recommendations[]`. |
| **Accept a recommendation → applies refinement** | ⚠️ **PARTIAL** | `unaddressed` list rendered + commit checks it. But the "accept/apply" UX itself — is there a button on each rec? Let me check… `DocumentOverlay.jsx:685-693` only renders the list. No accept action. The AIRevisionPanel (`:289-300`) appears to be the in-place revision path but it's a side panel, not a per-rec accept button. | ⚠️ **NEEDS VERIFICATION — possibly MISSING.** |
| **Commit action (locks document)** | ✅ EXISTS-TODAY | `DocumentOverlay.jsx:320-331` — `CommitConfirmationModal` with `onCommitted` callback. Lifecycle flips to `committed` → edit mode force-exits at `:127-130`. Toast: "Document committed and locked." | YES — BE wiring: ensure the commit endpoint exists and atomically transitions the row. |
| **Move to review** | ✅ EXISTS-TODAY | `DocumentOverlay.jsx:193` — `/work-studio/documents/{id}/move-to-review` already wired. | NO. |
| **Export wizard (shared — Analyze handoff target)** | ⚠️ **PARTIAL** | Existing `ExportModal.jsx` at `/app/frontend/src/components/studio/ExportModal.jsx` is the per-artefact export modal. The JC-WS spec says: "Export is a WIZARD, not a one-click dump. The user chooses the export objective and the format." | ⚠️ **NEEDS INSPECTION** — does ExportModal already accept an "objective" input + a format-choice step? **Needs verification** below. |

---

## Part B — Analyze drawer

| Surface | Status | Evidence | Behaviour delta needed? |
|---|---|---|---|
| Right-side drawer (Sheet chrome) | ✅ EXISTS-TODAY | `AnalyzeDrawer.jsx:17` — uses `Sheet + SheetContent`. | NO. |
| Topline (filename / size / objective input / notes) | ✅ EXISTS-TODAY | `AnalyzeDrawer.jsx:215-227`. | NO. |
| **Tabs: Bottom Line / What changed / What's likely next / What's odd / Sources / Export** | ✅ EXISTS-TODAY | `AnalyzeDrawer.jsx:230-277`. Tabs ARE the current capability surface (analyze / forecast-narration / anomaly-narration). | YES — BE: ensure each tab populates from solva_v2 narrations. Already done (Stage 4.3 work on the export side). |
| **Validate / Forecast / Simulate / Extract capabilities run behind the surface** | ⚠️ **PARTIAL** | `/v2/analyses/{aid}/synthesize` runs Validate + Forecast narration + Anomalies narration today (Solva v2 narrate_analysis). **Simulate is NOT wired into the synthesize call** — the dispatch says it shouldn't auto-run on initial, only on follow-up. | YES — BE: classify what synthesize currently runs vs the JC-WS spec; wire missing capabilities. |
| **"Highlights as tweet-style cards grouped under topics"** | ❌ **MISSING UI** | Current is tab-based narrative, NOT card-style highlights with topic groups. Restructuring to card+topic layout would alter empty-state visuals. | **STOP — surface to user.** Choices: (a) restructure tabs → cards-with-topics per UX doc, (b) accept current tab UI as the canonical highlight surface and only deepen the content. |
| **Prompt tool docked at bottom (free-text follow-up ask)** | ❌ **MISSING UI** | No docked prompt input. Current "Run synthesis" button is one-shot. The objective textarea is a parameter, not a follow-up prompt. | **STOP — surface to user.** |
| **Data-aware question tips** | ❌ **MISSING UI** | No tips strip on AnalyzeDrawer. | **STOP — surface to user.** |
| **Subtle plain-language cue ("Ask Akki to forecast, simulate, validate, dig into a region")** | ❌ **MISSING UI** | Current objective placeholder is "What are you trying to learn from these files?" — does not name the capability range. The JC-WS spec EXPLICITLY allows adding this cue ("the JC-WS spec's subtle plain-language cue for Analyze IS specced — that one is allowed because the spec calls for it"). | ✅ **ALLOWED** per UI-rule exception. Awaits the prompt tool surface to dock on. |
| **Refusal guard wired into ask path** | ⚠️ **PARTIAL** | `refuse_to_decide` exists in solva_v2 (initial synthesis path). Whether it's also wired on the follow-up ask path can't be answered until the follow-up ask path itself exists. | Depends on follow-up prompt surface — see MISSING above. |
| **"Finish & export" → opens Document Generation export wizard** | ❌ **MISSING UI** | Current Export tab does direct DOCX/PPTX/XLSX downloads. Not a wizard handoff. | **STOP — surface to user.** Choice: (a) add a "Finish & export" button that opens the shared wizard, (b) keep current direct downloads and defer the wizard handoff. |
| **Per-account analyses list (rehydrates on reopen)** | ✅ EXISTS-TODAY | `WorkStudioAnalyze.jsx` / `AnalyzeJournal.jsx` lists analyses; opening rehydrates `notes_history`, `objective`, `runs`. | NO. |

---

## STOP-and-surface summary — MISSING UI elements

The following JC-WS surfaces have **no existing UI today** and require user direction before I touch them:

1. **Brief — chat artefact source** (Journey 3)
2. **Brief — ThinkLab session source** (Journey 3)
3. **Brief — combined docs + signals + cycle source** (Journey 3, partial)
4. **Analyze — highlights-as-cards-grouped-under-topics** (Part B drawer structural)
5. **Analyze — docked prompt tool for follow-up asks** (Part B drawer)
6. **Analyze — data-aware question tips strip** (Part B drawer)
7. **Analyze — "Finish & export" → wizard handoff** (Part B export)

**The subtle plain-language cue** on Analyze (#6's neighbour) is the only MISSING element the UI-rule explicitly allows because the spec names it. It will dock on the prompt tool surface once that exists.

**The shared Export Wizard** (used by Analyze handoff + Document Generation native export) needs verification — is the existing ExportModal a wizard with objective + format choice, or a one-click dump? See `NEEDS VERIFICATION` rows above.

**The "Accept a recommendation → apply refinement" per-rec accept action** also needs verification — the rec list renders but the accept-button-per-row isn't visible from what I read.

---

## What CAN proceed without STOP (BEHAVIOUR-only, UI untouched)

Per the UI-untouched rule, these BE wiring tasks are clear-to-go:

1. Thread `source_ids` from `compilations` row → `_run_export` via the `source_document_ids` field on `ExportRequestIn`. (Already partial in this turn; held.)
2. Persist `cadence` on the export row + the documents card row. (Already partial; held.)
3. Resolver widening for context-shared docs in `_resolve_source_blobs_for_scoring`. (Already partial; held.)
4. Wire real `intelligence_report.confidence_pct + confidence_band + confidence_rationale + confidence_scored_at + sources_count + source_document_ids + period + recommendations[]` for Source-material pack exports. The IntelligenceCard already renders these fields when populated; the seam is in the BE generation pipeline.
5. Wire real lifecycle transitions (Draft → In Review → Committed) onto Source-material pack cards. The UI surfaces are present; BE state machine needs to support all 3 states for `kind=board_pack/committee_pack/minutes` rows.
6. Wire the `confidence_score_skipped_no_sources` regression-shutter — explicit source selection feeds the scorer real source blobs so confidence becomes a real number.

---

## Verification items — CLOSED

Three reads completed:

- **A. BlockComposer ask-Akki affordance:** ❌ **Not in BlockComposer directly.** Grep confirmed: zero matches for `akki|enhance|generate|expand|prompt|/api/.../generate|/api/.../enhance` (the only hit is `window.prompt` for sharing emails at L743). **However**, the spec's "user prompts Akki to enhance/expand it" requirement IS satisfied through a parallel surface: `AIRevisionPanel` (invoked from `DocumentOverlay` via the Revise button at `:289`). The user-facing flow is: write in BlockComposer → close (saves a Draft) → reopen via DocumentOverlay → click Revise → AIRevisionPanel proposes section-level refinements → accept/reject per section. **VERDICT: EXISTS-TODAY via parallel route; counts as adequate-existing-UI for Journey 2 / Journey 5.** If the user later wants an in-editor "ask Akki" button on BlockComposer itself, that's a separate UI decision.

- **B. ExportModal is already a wizard:** ✅ **EXISTS-TODAY.** `ExportModal.jsx` collects `description / objective / scope / outputFormat` with `phase = compose → running → complete`, embeds a `SourceStep` component, polls status, surfaces a Download button on complete. **The "shared Export Wizard" the JC-WS spec mandates is already this component.** The previously-flagged "Finish & export → wizard handoff" on AnalyzeDrawer remains MISSING (Analyze's Export tab does direct downloads); but the wizard target it would hand off to is built. **The AnalyzeDrawer-side "Finish & export" affordance + handoff remains the only MISSING piece on the export side.**

- **C. Per-recommendation Accept-and-apply:** ⚠️ **PARTIAL.** The recommendation list at `DocumentOverlay.jsx:685-693` is read-only (each `<li>` shows `r.text` + a green ✓ when `r.addressed`). **No per-rec Accept button.** The apply-refinement path is `AIRevisionPanel` (`:289-300, :1015-1188`) which operates at the SECTION level (not the per-recommendation level): AI proposes per-section revisions, the user accepts/rejects each section via checkboxes (`accepted[section_index]`), and `apply()` writes back the chosen sections. **VERDICT:** the user can apply refinements but not via the spec's exact "accept this recommendation" gesture — they go via the AIRevisionPanel which is a parallel path. For the proving slice, this is acceptable as-is; if the user wants a per-rec accept button bound to specific refinement scope, that's a separate UI decision.

### Updated MISSING inventory after verification

The ONLY items that remain truly MISSING UI per the JC-WS spec:

1. **Brief — chat artefact source** (Journey 3) — no entry on Create modal.
2. **Brief — ThinkLab session source** (Journey 3) — no entry on Create modal.
3. **Brief — combined docs + signals + cycle source** (Journey 3) — partial; the external_document picker is single-doc and doesn't pull signals/cycle.
4. **Analyze — highlights-as-cards-grouped-under-topics** (Part B) — current is tab-based narration.
5. **Analyze — docked prompt tool for follow-up asks** (Part B) — none today.
6. **Analyze — data-aware question tips strip** (Part B) — none today.
7. **Analyze — "Finish & export → opens shared Export Wizard"** (Part B) — current Export tab does direct downloads.
8. **Subtle plain-language cue** ("Ask Akki to forecast, simulate, validate, dig into a region") — JC-WS spec EXPLICITLY allows this one; docks on the prompt tool surface once that exists. **Allowed by UI-rule exception.**

**EXISTS-TODAY adequately:**
- Source-material packs whole journey (Journey 1)
- Blank-start whole journey (Journey 2) — via AIRevisionPanel parallel path
- Enhance whole journey (Journey 4)
- Draft whole journey (Journey 5)
- Document Generation lifecycle (Draft/In Review/Committed) + detail view + edit title + commit-lock
- Document Generation IntelligenceCard fields (sources count + period + framing + recommendations count + confidence band/chip/rationale/scored-at) — fields render correctly when populated
- Shared Export Wizard (ExportModal) — already a wizard

**EXISTS-TODAY with caveats (BEHAVIOUR-only deltas needed):**
- IntelligenceCard fields need real BE wiring per Source-material pack journey
- Per-rec Accept ergonomics: refinements apply via AIRevisionPanel (section-level), not per-rec (item-level)
- AIRevisionPanel may need additional wiring to consume real `report.recommendations[]` and apply them

---

## Final Recommendation

**The Board Pack proving slice (Journey 1) can proceed immediately on EXISTS-TODAY UI**, wiring BEHAVIOUR only:
1. Thread `source_ids` from compilations → `_run_export` (BE)
2. Persist `cadence` + `source_document_ids` on the export row (BE)
3. Real intelligence_report fields populate (BE) — IntelligenceCard already renders them
4. Lifecycle transitions on Source-material pack cards (BE)
5. Confidence scorer runs with real source blobs (BE)

No UI changes. No new buttons. No structural diffs. The artefact lands; the user opens DocumentOverlay; the existing IntelligenceCard surfaces real values where placeholder text previously read "Intelligence report not captured for this document."

The 7 MISSING UI items above are surfaced for user direction BEFORE I touch them. None of them block the Board Pack proving slice.
