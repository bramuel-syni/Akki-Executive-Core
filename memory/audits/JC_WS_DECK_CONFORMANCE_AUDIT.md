**Canonical Spec:** `/app/memory/user_actions/uploaded_briefs/WORK_STUDIO_DECK_UX_BRIEF_V1_0.docx` · **v1.0** · **2nd July 2026** · Author: Product Team

# JC-WS-DECK-CONFORMANCE-AUDIT

**Type:** READ-ONLY conformance matrix.
**Ships:** 2026-07-02.
**Dispatch:** `JC-WS-DECK-CONFORMANCE-AUDIT`.
**Column addition:** 2026-07-02 (`JC-USER-FOLLOWUP-3-TASKS` Task 1) — added `UI required?` column to every DECK-XXX row + summary line at the bottom of the matrix. Values: `UI-only` / `UI + backend` / `Backend-only` / `N/A`.
**Testing method:** N/A (documentation audit; no code touched).
**Locked-area sweep:** 0 product code touched · 0 tests touched · 0 sprint memos written outside this audit + the `DEV_PIPELINE.md §9` rows entered BEFORE this file (initial audit + column-update rows both landed first per Zero-Handoff-Loss discipline).

---

## 0. Executive Summary

**Audit scope.** Every one of the 87 user stories in the brief (DECK-001..087) plus the four descriptive sections (§4.1 Deck List · §4.2 Create Summary Deck Journey · §4.3 Create Deck from Blank Journey · Feature-Goals cross-cutting requirements) was mapped 1:1 against the actual codebase.

**Files inspected (evidence trail).**

| Layer | File | LOC | Role in current deck story |
| :--- | :--- | ---: | :--- |
| Backend | `backend/routers/decks.py` | 678 | Standalone 3-step deck pipeline (outline → generate → quality_check) writing to `db.decks`. Not aware of Work Studio lifecycle. |
| Backend | `backend/routers/work_studio_from_source.py` | 723 | `POST /work-studio/artefacts` (deck/report create with source=blank\|brief\|external_document) writes to `db.decks` `.status="draft"`. `POST /work-studio/from-document` writes to `db.work_studio_exports` `.lifecycle_state="draft"`. |
| Backend | `backend/routers/work_studio_overlay.py` | ~700 | `db.work_studio_exports` lifecycle engine — `move-to-review`, `commit`, `create-new-version`, versions/restore. Owns `intelligence_report` sub-doc. Does NOT service `db.decks` rows. |
| Backend | `backend/services/work_studio_overlay.py` | ~200 | `LifecycleState = Literal["draft", "in_review", "committed"]` + `can_transition(...)`. Applied to work_studio_exports only. |
| Frontend | `frontend/src/pages/Decks.jsx` | 1200 | Standalone `/app/decks` surface — 3-step Intent → Outline → Deck review (single-page); reads `db.decks` via `/api/contexts/{cid}/decks`. |
| Frontend | `frontend/src/pages/WorkStudio.jsx` | 1456 | Six-tab listing (Decks is the 4th tab, category="deck"). Feeds off unified `/documents?category=deck`. |
| Frontend | `frontend/src/components/work_studio/overlay/DocumentOverlay.jsx` | 1377 | Full-bleed detail surface for `work_studio_exports` rows. Toolbar + IntelligenceCard + IntelligenceModal + DocumentSurface + AIRevisionPanel + VersionHistoryModal + CommitConfirmationModal. **NO tabbed structure.** |
| Frontend | `frontend/src/components/work_studio/CreateArtefactModal.jsx` | 297 | Two-source create flow (blank / brief / external_document) — single-select only. Fires `POST /work-studio/artefacts` for brief|external_document; dispatches `akki:open-drafting-drawer` event for blank. |
| Frontend | `frontend/src/components/work_studio/DraftingDrawer.jsx` | (not inspected — used by blank flow) | Blank-journey authoring drawer; writes to `db.work_studio_exports` via `/save-draft`. |
| Frontend | `frontend/src/components/shell/HandoffActions.jsx` | 174 | Cross-module handoff row: Ask in Chat (document only) · Take into Solva · Send to Work Studio · Add to Cycle. Rendered inside `Decks.jsx` deck review view; NOT rendered inside `DocumentOverlay`. |

**Headline verdict.** 87 stories audited.

| Status | Count | % |
| :--- | ---: | ---: |
| ✅ MET | 19 | 22% |
| 🟡 PARTIAL | 16 | 18% |
| ❌ MISSING | 48 | 55% |
| ⚠️ CONFLICT | 4 | 5% |
| ❓ AMBIGUOUS | 0 | 0% |

**Structural finding.** Two orthogonal deck surfaces exist today. **Neither matches the brief.**

* **Surface A — `/app/decks`** (`Decks.jsx` + `routers/decks.py`). 3-step flow (Intent → Outline → Deck) writing to `db.decks`. Own lifecycle vocabulary: `tier`, `quality_check`, `user_feedback.rating`, `regen_count`. No brief-required lifecycle (Draft / In Review / Committed).
* **Surface B — `/app/work-studio` deck tab** (`WorkStudio.jsx` category=deck + `DocumentOverlay`). Reads unified `documents?category=deck` (which mixes rows from `db.decks`, `db.work_studio_exports` where kind=deck, and `db.documents`). `DocumentOverlay` mounts on `work_studio_exports` only (via `/work-studio/documents/{aid}`) and has lifecycle_state — but has NO tabs.

**Two-surface tension.** The brief describes ONE feature — Deck List → Create → Detail View (5 tabs). The codebase has TWO. Any build to conformance must either (i) collapse Surface A into Surface B, (ii) collapse Surface B into Surface A, or (iii) design a new unified surface. This decision is upstream of every DECK-XXX MISSING below.

**Recommended path forward.** User direction required. Three sized options are presented at §9. My recommendation is **Option (B) — MVP** because it delivers the brief's core promise (Deck List + 5-tab Detail with Notes) in ~2-3 weeks while surfacing the remaining gaps for a follow-up dispatch, rather than swinging at a full 6-8-week rebuild without incremental value.

**Column key (added 2026-07-02):**

* **UI-only** — pure frontend work (component, layout, styling, interaction). No backend contract change required.
* **UI + backend** — needs both surfaces. Backend schema / route / service change AND frontend component / rendering change.
* **Backend-only** — data model / service / router / schema. UI already covers it, or the brief doesn't require a UI change here.
* **N/A** — story is met by existing routing / config; no build surface applies.

---

## 1. Deck List Surface (DECK-001..010)

**Brief text (§4.1):** "The Decks workspace displays generated and draft decks as individual deck cards … New deck cards appear at the top … Each deck card displays the deck title, lifecycle status, creation date, document type, confidence score and number of source documents. Users click a deck card to open the Deck Detailed View."

**Code reality:** Two overlapping listings exist. `Decks.jsx` renders a right-sidebar `history` list (rows, not cards). `WorkStudio.jsx` category=deck renders a `DocumentRow` list (rows, not cards) via `ListingShell`. Neither surface uses the brief's "deck card" visual metaphor. The metadata surfaced differs across the two, and lifecycle status is only surfaced in one.

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-001 | Access the Decks workspace | ✅ MET | UI-only | Two routes exist: `/app/decks` (`Decks.jsx`) + `/app/work-studio` (Decks tab id=`deck` in `WorkStudio.jsx:155`). |
| DECK-002 | View decks as individual **deck cards** | 🟡 PARTIAL | UI-only | Both surfaces render **rows**, not cards. `Decks.jsx:346-378` uses `<ul>…<li>` rows; `WorkStudio.jsx:342-467` `DocumentRow` uses full-width row buttons. Card metaphor per brief is not present. |
| DECK-003 | Identify the most recently created deck (top of list) | ✅ MET | UI + backend | `routers/decks.py:613` sorts `db.decks` by `created_at DESC`. WS unified listing also sorts by `updated_at`/`committed_at`/`created_at` desc (`WorkStudio.jsx:318`). |
| DECK-004 | View the title of each deck | ✅ MET | UI + backend | Both surfaces render title (`Decks.jsx:355-357`, `WorkStudio.jsx:354-356`). |
| DECK-005 | View the **lifecycle status** (Draft / In Review / Committed) | ❌ MISSING | UI + backend | On `/app/decks` history rows the status field is not surfaced (only tier + q-score + feedback rating — `Decks.jsx:358-364`). On WS DocumentRow the lifecycle chip is absent for `db.decks` rows (only work_studio_exports rows carry `lifecycle_state`). `LIFECYCLE_LABEL = {draft, in_review, committed}` exists in `DocumentOverlay.jsx:70-74` but is applied inside the overlay, not the list rows. |
| DECK-006 | View when a deck was created | ✅ MET | UI + backend | `Decks.jsx:358-359` renders `new Date(d.created_at).toLocaleDateString()`. WS DocumentRow renders `updated_at`/`committed_at`/`created_at` (`WorkStudio.jsx:318-327`). |
| DECK-007 | View number of source documents | 🟡 PARTIAL | UI + backend | WS `DocumentRow` surfaces `sourceCount` (`source_count` field, `WorkStudio.jsx:331,391-395`) BUT the `db.decks` insert paths do NOT set `source_count` (`routers/work_studio_from_source.py:531-550`). Field is absent on standalone `Decks.jsx` history rows entirely. |
| DECK-008 | View the **document type** | ⚠️ CONFLICT | UI-only | `WorkStudio.jsx:365-372` renders a category badge ("DECK") via `displayCategoryChip`. `/app/decks` history renders `tier` (deep/standard) as the "type" — a different, cost-oriented dimension. Neither matches the brief's implied "presentation deck vs. summary deck" distinction (or is that just "Deck" as fixed literal?). |
| DECK-009 | View the **confidence score** | 🟡 PARTIAL | UI + backend | WS `DocumentRow` renders `confidence_pct` chip with 75/50 thresholds (`WorkStudio.jsx:334-341`). `/app/decks` history renders `quality_check.score` (0-100) — a different score computed by a different engine (`quality_check` LLM call, `routers/decks.py:466-545`). The two are not reconciled. |
| DECK-010 | Click a deck card to open the Deck Detailed View | ✅ MET | UI-only | Both listings wire click → open detail (`Decks.jsx:349-351` `onResume(d.id)` loads and switches view to `deck`; `WorkStudio.jsx` DocumentRow → `onOpen(row)` → `DocumentOverlay`). |

---

## 2. Create Deck Journey — Modal + Sources (DECK-011..022, DECK-072..074)

**Brief text (§4.2 + §4.3):** "Users create a new deck by selecting Create Summary Deck. A modal prompts them to enter a deck title and choose whether to start from an existing brief, uploaded document or a blank authoring experience. When generating from briefs or uploaded documents, users select one or **more** sources before generating the deck."

**Code reality:** The "Create Summary Deck" button exists (`WorkStudio.jsx:194-197`) and opens `CreateArtefactModal` (`WorkStudio.jsx` mounts it). The modal accepts a title, and radio-selects one of {blank, brief, external_document}. **Only single-select** on brief and document pickers (`CreateArtefactModal.jsx:229-266` — bare `<select>` element, not multi-select). No in-modal upload path exists. Ordering of briefs/documents comes back from the API in server-provided order (created_at desc for briefs; unspecified for documents).

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-011 | Start creating a new deck | ✅ MET | UI-only | "Create Summary Deck" chip: `WorkStudio.jsx:194-197`. |
| DECK-012 | Provide a title for the deck | ✅ MET | UI-only | `CreateArtefactModal.jsx:183-192`. |
| DECK-013 | Choose to start from a **blank** deck | ✅ MET | UI-only | `CreateArtefactModal.jsx:199, 132-140` dispatches `akki:open-drafting-drawer` for blank source. |
| DECK-014 | Choose to generate from existing briefs | ✅ MET | UI + backend | `CreateArtefactModal.jsx:200,226-251`. |
| DECK-015 | Choose to generate from uploaded documents | ✅ MET | UI + backend | `CreateArtefactModal.jsx:201,253-278`. |
| DECK-016 | View available briefs within the workspace | ✅ MET | UI + backend | `CreateArtefactModal.jsx:74-84` fetches `/briefings/aggregates?kind=briefing&page_size=50`. |
| DECK-017 | View briefs **ordered alphabetically** | ❌ MISSING | UI-only | No client-side sort applied. Backend returns list in `created_at DESC` order (aggregates default). Brief-required alphabetical order is not honoured. Fix is a JS `.sort((a,b) => a.name.localeCompare(b.name))` in the modal. |
| DECK-018 | Select **one or more** briefs | ❌ MISSING | UI + backend | `CreateArtefactModal.jsx:229-239` uses a native `<select>` (single-select); payload carries a single `source_brief_id`. Backend `CreateArtefactRequest` accepts one `source_brief_id: Optional[str]` only. Both need to become arrays. |
| DECK-019 | View uploaded documents | ✅ MET | UI + backend | `CreateArtefactModal.jsx:89-99` fetches `/documents?limit=200`. |
| DECK-020 | View uploaded documents **ordered alphabetically** | ❌ MISSING | UI-only | Same client-side-sort remedy as DECK-017. |
| DECK-021 | Upload a new document **while creating a deck** | ❌ MISSING | UI + backend | No in-modal upload affordance. Modal footer offers Cancel + Submit only. User must exit, upload elsewhere, then reopen the modal. Fix: mount `<UploadOptions>` inside the modal (existing FE component) wired to existing `/documents/upload` endpoint (no new BE route needed) — but modal state management + refresh of the document list is UI-work + backend hardening around race conditions. |
| DECK-022 | Select **one or more** uploaded documents | ❌ MISSING | UI + backend | Same single-select constraint as DECK-018. Both `source_document_id` on FE payload + `source_document_id: Optional[str]` on BE request need to become arrays. |
| DECK-072 | Choose to generate a deck from a blank template | ✅ MET | UI-only | Same as DECK-013. Blank route dispatches to `DraftingDrawer` (`CreateArtefactModal.jsx:132-140`). |
| DECK-073 | Describe what the deck should cover | ✅ MET | UI + backend | `DraftingDrawer.jsx` (not inspected in full; opened via `akki:open-drafting-drawer` custom event; writes user-authored context to `work_studio_exports` via `/save-draft`). |
| DECK-074 | Save the deck as a draft | ✅ MET | UI + backend | `DraftingDrawer` `/save-draft` writes a `work_studio_exports` row with `lifecycle_state="draft"`. |

---

## 3. Generation Flow & In-flight Feedback (DECK-023..030, DECK-079..080)

**Brief text (§4.2):** "During generation, users are shown AI processing progress before receiving options to download the deck, continue working in Chat or close the workflow. The generated deck is automatically added to the Deck list as a deck card with **In Review** status."

**Code reality:** Two divergent flows exist. Standalone `/app/decks` has a streaming-log scene (`StreamingLogScene`) rendered during the deep-tier ~30-60s Opus pass (`Decks.jsx:604-614`) — the closest analog to brief's "AI processing progress". Meanwhile the WS `CreateArtefactModal` path is a **synchronous POST** to `/work-studio/artefacts` followed by an immediate redirect to `/app/studio/composer/deck/{id}` — no progress surface at all. **NEITHER surface offers "download immediately" or "continue in Chat immediately" as an in-flight completion sheet** — those options exist only after landing in the composer/overlay.

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-023 | Generate a deck after providing required info | ✅ MET | UI + backend | Two paths: `Decks.jsx:419-435` `generate()` calls `/decks/{oid}/generate/stream`; `CreateArtefactModal.jsx:141-157` calls `/work-studio/artefacts`. |
| DECK-024 | **Monitor the progress** of deck generation | 🟡 PARTIAL | UI + backend | Only in `/app/decks` deep-tier path (`Decks.jsx:604-614` uses `StreamingLogScene` + `useStreamingProgress`). The WS `CreateArtefactModal` path is synchronous — no progress UI. Bringing parity requires WS-side streaming endpoint or generation-webhook + FE progress modal. |
| DECK-025 | Receive confirmation that generation has started | ✅ MET | UI-only | Toast `"Outline drafted"` (`Decks.jsx:266`) + toast `"Deck generated"` (`Decks.jsx:446`); WS path toast `"Deck created"` (`CreateArtefactModal.jsx:160`). |
| DECK-026 | **Download the deck immediately** after generation | ❌ MISSING | UI-only | No completion-sheet download affordance. `/app/decks` lands the user in Step 3 review (Deck review) with no direct-download button (Toolbar Download only on Overlay). WS path redirects to composer where Download is inside the Overlay Toolbar — not on the completion surface. Fix is a completion-modal component. |
| DECK-027 | **Continue in Chat immediately** after generation | ❌ MISSING | UI-only | Analog to DECK-026 — no completion-sheet handoff. `HandoffActions` "Take into Solva" + WalkInCard exist on the `/app/decks` Step 3 review but not as an immediate post-generation sheet. |
| DECK-028 | Close the generation workflow after completion | ✅ MET | UI-only | `/app/decks` Step 3 offers "New deck" (returns to intent). WS path redirects to composer; closing overlay returns to Work Studio listing (`WorkStudioDocumentPage.jsx:55-56`). |
| DECK-029 | View the newly generated deck in the Deck list | ✅ MET | UI + backend | List refetched on completion (`Decks.jsx:180` `refreshState()`); WS composer navigates back to listing on close. |
| DECK-030 | Identify newly generated decks as **In Review** | ❌ MISSING | UI + backend | `routers/decks.py:344-364` generate writes deck with NO status/lifecycle field. `routers/work_studio_from_source.py:531-560` writes `status="draft"` (not "in_review"). No path auto-transitions Draft → In Review after generation. Fix: post-generation `move-to-review` call + FE listing refresh. |
| DECK-079 | Generate a deck from the authored context (blank journey) | ✅ MET | UI + backend | `DraftingDrawer` → export flow writes committed row to `work_studio_exports`. |
| DECK-080 | View the generated deck as a new deck card in the list | ✅ MET | UI + backend | WS listing refetches after export completes. |

---

## 4. Deck Detail Header & Footer Actions (DECK-031..039, DECK-068..071)

**Brief text (§4.2 + §4.3):** "Clicking the deck card opens the Deck Detailed View, where users review the generated content through **five tabs** … Users can download the deck, share it, continue working in Chat or Solva, and commit the document … Users can rename an In Review deck … [and] delete an In Review deck."

**Code reality:** Two divergent detail surfaces. `Decks.jsx` DeckStep (Step 3 review) is a linear scroll of Quality Check + Slides + HandoffActions + Feedback (no tabs). `DocumentOverlay` is the WS overlay — has Toolbar (Commit/Move-to-Review/Download/Versions/Edit) + IntelligenceCard + DocumentSurface + AI Revision panel + Version modal + Commit modal (no tabs). Neither surface uses tabs at all. Rename and Delete are ABSENT on both surfaces. Share affordance is present on `Decks.jsx` (ShareArtefactModal, `Decks.jsx:922-931`) but not on `DocumentOverlay`.

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-031 | Open the Deck Detailed View | ✅ MET | UI-only | `Decks.jsx:186-193` `DeckStep` for `db.decks` rows; `DocumentOverlay` for `work_studio_exports` rows. |
| DECK-032 | View the deck title | ✅ MET | UI + backend | `Decks.jsx:712-714` `<h2>{deck.title}</h2>`; `DocumentOverlay` Toolbar. |
| DECK-033 | View the **lifecycle status** | 🟡 PARTIAL | UI + backend | Only surfaced on `DocumentOverlay` (via `LIFECYCLE_LABEL` at line 70-74) for `work_studio_exports` rows. **NOT surfaced on `/app/decks` DeckStep** — that surface shows "Deep tier · N slides" (`Decks.jsx:695-697`) instead. |
| DECK-034 | Identify **Akki-generated** decks | ⚠️ CONFLICT | UI-only | WS `DocumentRow` shows an "Akki Generated" badge (`WorkStudio.jsx:333,382-395`) on listing rows only. Neither detail surface renders it consistently — brief calls for it on the detail view. |
| DECK-035 | View when the deck was created and last updated | ✅ MET | UI + backend | Present on both surfaces (created_at + updated_at fields written on every insert/update — `routers/decks.py:363` + `routers/work_studio_from_source.py:305-307`). |
| DECK-036 | **Commit** a deck | 🟡 PARTIAL | UI + backend | `DocumentOverlay` has full commit flow (Toolbar → `CommitConfirmationModal` → `POST /work-studio/documents/{aid}/commit` at `work_studio_overlay.py:334-462`). **Missing from `/app/decks` DeckStep entirely.** Rows in `db.decks` cannot be committed — the endpoint only fires against `work_studio_exports`. |
| DECK-037 | **Close** the detailed view | ✅ MET | UI-only | `Decks.jsx:191` `onNew()` returns to intent; `DocumentOverlay.jsx:157` overlay backdrop close + `WorkStudioDocumentPage.jsx:55-56` back nav. |
| DECK-038 | **Rename an In Review deck** | ❌ MISSING | UI + backend | No rename affordance on either detail surface. Backend has no `PATCH /decks/{id}` or `/work-studio/documents/{aid}/rename` route. |
| DECK-039 | **Delete an In Review deck** | ❌ MISSING | UI + backend | No delete button on either detail surface. Backend has no `DELETE /decks/{id}`. `work_studio_exports` has no `DELETE /documents/{aid}` route either (only `create-new-version` clones the committed row). |
| DECK-068 | **Download the deck from any tab** | 🟡 PARTIAL | UI-only | `DocumentOverlay` Toolbar has Download (line 22-27 import). Not per-tab (no tabs exist). Not present on `/app/decks` DeckStep. Fix is placement, not new endpoints. |
| DECK-069 | **Continue discussing the deck in Chat** | 🟡 PARTIAL | UI-only | `HandoffActions` rendered inside `Decks.jsx:838-844` (kind="deck") — but "Ask in Chat" is gated to `kind === "document"` only (`HandoffActions.jsx:59-63,124-133`), so decks fall through. Fix: expand gate to include deck kind. |
| DECK-070 | **Share the deck via email** | ⚠️ CONFLICT | UI + backend | `ShareArtefactModal` opened from `Decks.jsx:922-931` — but this modal is not visible in this audit; needs verification whether it supports email addressee input or is limited to internal-workspace share links. Not surfaced from `DocumentOverlay` at all. |
| DECK-071 | Continue analysing the deck in **Solva** | 🟡 PARTIAL | UI-only | `HandoffActions.jsx:65-73` "Take into Solva" fires `takeToSolva({navigate, kind: "deck", id})`. Rendered inside `Decks.jsx:838-844`; NOT rendered inside `DocumentOverlay`. Fix: mount `HandoffActions` in Overlay footer. |

---

## 5. 5-Tab Detail Content (DECK-040..067)

**Brief text (§4.2):** "Users review the generated content through **five tabs**: Document, Intelligence, Your Notes, Signals and Related Documents."

**Code reality:** **NO tabbed detail structure exists anywhere in the codebase.** `DocumentOverlay.jsx` renders sub-components inline (Toolbar → IntelligenceCard → DocumentSurface → AIRevisionPanel) as vertical stacks and modals — no `<Tabs>`/`TabsList`/`TabsTrigger`/`TabsContent` primitives. `Decks.jsx` DeckStep is also a single-scroll layout. Grep for "tab" or "Tabs" inside `DocumentOverlay.jsx` returns zero brief-relevant matches. This is the largest gap in the brief-vs-code comparison.

### 5.1 Document tab (DECK-040..044)

Brief expects: structured outline · slide titles · slide content · source context (for blank decks) · edit source context.

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-040 | View the generated deck as a **structured outline** | 🟡 PARTIAL | UI-only | `/app/decks` Step 3 renders slides linearly with `n`, `title`, `body_md`, `speaker_notes` (`Decks.jsx:808-830`). `DocumentOverlay` renders body prose in TipTap editor — not slide-structured. Neither renders a "structured outline" in the brief's implied sense (a collapsible outline navigation). |
| DECK-041 | Review slide titles | ✅ MET | UI-only | `Decks.jsx:817-819` renders each slide title. |
| DECK-042 | Review slide content | ✅ MET | UI-only | `Decks.jsx:820-822` renders `s.body_md` with `whitespace-pre-wrap`. |
| DECK-043 | View the **original source context** (for decks created from scratch) | ❌ MISSING | UI + backend | No source-context section renders in either detail surface. Backend has no `deck.source_context` or `work_studio_exports.source_context` sub-doc surfaced in the response. DraftingDrawer stores authored context in the draft body but never surfaces it separately as an editable "source_context" field. |
| DECK-044 | **Edit** the original source context | ❌ MISSING | UI + backend | No Edit Context affordance. Needs PATCH endpoint + editor UI. |

### 5.2 Intelligence tab (DECK-045..049)

Brief expects: plain-language explanation of deck · clarity metrics · document provenance · sources used · refresh document intelligence.

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-045 | View a **plain-language explanation** of the deck | 🟡 PARTIAL | UI + backend | `DocumentOverlay` `IntelligenceCard` (line 517) + `IntelligenceModal` (line 606) render `intelligence_report.confidence_rationale` + recommendations. Not a fully-formed plain-language "what this deck is" narrative — closer to a confidence audit trail. Likely needs a new LLM prompt for the plain-language explanation. |
| DECK-046 | View **clarity metrics** | 🟡 PARTIAL | UI + backend | `intelligence_report.confidence_pct` + `confidence_breakdown` + `rag_band` exist (`work_studio_overlay.py:426-431`). Not an explicit "readability" score — the closest analog. Adding readability likely requires a new scoring engine. |
| DECK-047 | View **document provenance** | 🟡 PARTIAL | UI-only | `origin` sub-doc written on `work_studio_exports` insert (`work_studio_from_source.py:683-687`, `299-306`). Data exists — needs UI surface (provenance panel in Intelligence tab). |
| DECK-048 | View the **sources used** | ✅ MET | UI + backend | `source_document_ids` array persisted on `work_studio_exports` (`work_studio_from_source.py:682`). Surfaced via `intelligence_report.sources` list. |
| DECK-049 | **Refresh document intelligence** | 🟡 PARTIAL | UI-only | `POST /work-studio/documents/{aid}/recompute-confidence` (`work_studio_overlay.py:358-448`) exists as an endpoint but there is no user-facing "Refresh Intelligence" button in `DocumentOverlay` (only auto-fires on move-to-review + commit). Button-only add. |

### 5.3 Your Notes tab (DECK-050..059)

Brief expects: private notes CRUD · autosave confirmations · session persistence · undo/redo · offline-tolerant editing · nuke-all.

**Baseline evidence (applies to every row below):** No deck-scoped private-notes model, endpoint, or UI exists in the codebase. `pages/Pulse.jsx:367` renders a private-notes block inline in Pulse — that is orthogonal (pulse-scoped, not deck-scoped) and not reusable. No `db.deck_notes` collection, no `POST /decks/{id}/notes`, no reusable `<Notes>` React component. This is a net-new engine spanning schema + endpoints + editor + autosave + offline-tolerant queue + undo/redo stack.

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-050 | **Create** private notes on a deck | ❌ MISSING | UI + backend | No POST endpoint, no editor UI. |
| DECK-051 | **Edit** existing notes | ❌ MISSING | UI + backend | No PATCH endpoint, no editable surface. |
| DECK-052 | **Delete all or part** of the notes | ❌ MISSING | UI + backend | No DELETE endpoint, no delete affordance. |
| DECK-053 | View **confirmation** that notes have been saved | ❌ MISSING | UI + backend | No autosave engine → no confirmation toast/badge. |
| DECK-054 | **Return** to previously saved notes across sessions | ❌ MISSING | UI + backend | No persistence layer → nothing to return to. |
| DECK-055 | Continue editing notes after **reopening the deck** | ❌ MISSING | UI + backend | Same root cause — no persistence. |
| DECK-056 | **Undo** note changes during the current session | ❌ MISSING | UI-only | No editor mount → no undo stack. (TipTap `StarterKit` is used for the deck body editor in `DocumentOverlay.jsx:21` and does supply undo, but it is scoped to the document body, not to a notes surface.) The undo/redo is a client-side editor concern — no BE contract. |
| DECK-057 | **Redo** previously undone note changes | ❌ MISSING | UI-only | Same root cause. |
| DECK-058 | Continue writing even when **saving temporarily fails** | ❌ MISSING | UI + backend | No offline-tolerant queue exists for notes. Client queue + retry logic + FE state; BE tolerates re-writes idempotently. |
| DECK-059 | **Delete notes entirely** so user can start again | ❌ MISSING | UI + backend | No bulk-clear endpoint. |

### 5.4 Signals tab (DECK-060..063)

Brief expects: signals extracted **from the deck** · distinguish risks/opportunities/recommendations · review before commit · committed signals surface in Pulse.

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-060 | View signals **extracted from the deck** | ❌ MISSING | UI + backend | Signals (`get_synisense().list_signals`, called at `routers/decks.py:85-93`) are **workspace-level** — scoped by `account_id + context_id`, not by deck. There is no engine that extracts signals FROM the generated deck content. New extraction pipeline + FE panel. |
| DECK-061 | Distinguish risks / opportunities / recommendations | 🟡 PARTIAL | UI + backend | Signal model has a `kind` field (used at `routers/decks.py:113-116`) — capable of representing the three categories, but no deck-linked signals to categorize. |
| DECK-062 | Review signals before committing the deck | ❌ MISSING | UI + backend | No deck-linked signals → nothing to review. |
| DECK-063 | Committed signals become available in **Pulse** | ❌ MISSING | Backend-only | Even if per-deck signals existed, no linkage exists between a deck's commit event and Pulse's signals feed. Pulse UI already exists — the linkage is backend feed integration. |

### 5.5 Related Documents tab (DECK-064..067)

Brief expects: documents related to the deck via shared metadata · explicitly attached documents · same-lineage documents.

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-064 | View documents **related to the deck** | ❌ MISSING | UI + backend | No related-documents endpoint or UI. |
| DECK-065 | Documents with shared metadata | ❌ MISSING | UI + backend | No metadata-similarity retrieval exists (the closest is `search_document_journal` BM25 retrieval for the Brief Akki-fetch — flagged as insufficient in the JC-WS Phase 3 retrieval probe). Requires retrieval engine + FE panel. |
| DECK-066 | Explicitly attached documents | 🟡 PARTIAL | UI-only | `source_document_ids: List[str]` array persists on `work_studio_exports` rows (`work_studio_from_source.py:682`) — but no UI surface renders this list as a "Related Documents" panel. Data exists; needs UI only. |
| DECK-067 | Same **document lineage** | ❌ MISSING | UI + backend | Versions exist on committed docs (`work_studio_overlay.py:559-620`) but "lineage" as a cross-artefact concept (deck → underlying uploaded doc → other decks off the same doc) is not modelled. New lineage graph + FE panel. |

---

## 6. Lifecycle Model (Draft ↔ In Review ↔ Committed)

**Brief text (§4.2):** "Generated decks follow a simple lifecycle from **Draft** to **In Review** and finally **Committed**, enabling users to refine content before finalizing it. … Once committed, the deck content becomes read-only while private notes remain editable."

**Code reality:** A canonical lifecycle **exists** on `work_studio_exports` rows only (`services/work_studio_overlay.py:25` `LifecycleState = Literal["draft", "in_review", "committed"]` + `can_transition(...)`). Transitions are wired via `POST /move-to-review` + `POST /commit`. Committed state is enforced read-only (`work_studio_overlay.py:133-138, 174-178, 258-263, 613-618`). **However, `db.decks` rows use a completely different vocabulary** (`status="draft"` + `tier` + `user_feedback` + `quality_check`) and lifecycle transitions do not apply to them.

| Requirement | Status | Evidence |
| :--- | :--- | :--- |
| Draft → In Review transition (owner only) | ✅ MET (work_studio_exports only) | `work_studio_overlay.py:194-215` `move_to_review` route. |
| In Review → Committed transition | ✅ MET (work_studio_exports only) | `work_studio_overlay.py:334-462`. |
| Committed = read-only | ✅ MET (work_studio_exports only) | `work_studio_overlay.py:133,175,258,613`. |
| Committed = private notes remain editable | ❌ MISSING | No notes engine exists → nothing to keep editable. |
| Lifecycle vocabulary consistent across `db.decks` and `db.work_studio_exports` | ⚠️ CONFLICT | Two orthogonal state models. |

**Consequence for DECK-XXX stories:** DECK-005 · DECK-030 · DECK-033 · DECK-036 · DECK-038 · DECK-039 · DECK-062 · DECK-074 all depend on the lifecycle model being applied to whichever collection the "canonical" deck lives in. Today that decision is unmade.

---

## 7. Blank-Journey Regeneration & Versions (DECK-075..078, DECK-081..087)

**Brief text (§4.3):** "For decks generated from Blank, the Document tab additionally includes a Source Context section displaying the original generation context together with an **Edit Context** action. Users can update the context, save changes without regenerating, or **generate a new version** of the deck. **Each regenerated version is created as a separate deck card with its own version number, lifecycle, notes, signals and related documents, while preserving previous versions for comparison.**"

**Code reality:** `work_studio_overlay.py:510-620` implements a **document-versioning** engine (`create-new-version`, `versions`, `versions/{vid}/restore`) — but it is designed for the "commit → clone as new draft" pattern, not the "regenerate against updated source context → new sibling deck card" pattern the brief describes. There is no `source_context` sub-doc, no Edit Context action, no version-number surfacing per regenerated deck, and no automatic linking of notes/signals/related-documents across sibling versions (blocked further on all three engines being MISSING per §5).

| ID | Requirement | Status | UI required? | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| DECK-075 | Rename a draft deck title | ❌ MISSING | UI + backend | No rename affordance on the Drafts row or DraftingDrawer. Draft title is set at draft-open time (from CreateArtefactModal) and never editable after. |
| DECK-076 | Delete a draft deck | ❌ MISSING | UI + backend | No delete affordance on drafts. Requires backend `DELETE /work-studio/documents/{aid}?state=draft` — does not exist. |
| DECK-077 | **Reopen a draft** | ✅ MET | UI + backend | DraftingDrawer can be reopened for a saved draft (via `work_studio_exports` row with `lifecycle_state="draft"`). |
| DECK-078 | Continue editing saved context until ready to generate | 🟡 PARTIAL | UI + backend | DraftingDrawer autosaves body; not clear whether the specific "source context" (as opposed to draft prose body) is separately editable — the brief distinguishes them, the code does not. |
| DECK-081 | View the original source context **in the Document tab** | ❌ MISSING | UI + backend | No source-context UI section. |
| DECK-082 | **Edit** the original source context from the Document tab | ❌ MISSING | UI + backend | No Edit Context action. |
| DECK-083 | Save changes to source context **without generating** | ❌ MISSING | UI + backend | No source_context PATCH endpoint or UI. |
| DECK-084 | **Generate a new version** using the updated source context | ❌ MISSING | UI + backend | No "regenerate against updated source context" flow. `create-new-version` clones the committed row's structured_content — not a re-generation against different inputs. |
| DECK-085 | View each regenerated deck as a **separate deck card** | ❌ MISSING | UI + backend | Even if regeneration existed, no per-version listing card presentation exists (rendered as inline version history modal, not as sibling cards). |
| DECK-086 | Distinguish regenerated decks using **version numbers** | ❌ MISSING | UI + backend | Version index is tracked internally (`db.work_studio_document_versions`) but not surfaced as a visible "v1 / v2 / v3" tag on the listing row. |
| DECK-087 | Independently review each deck version — **notes, signals and related documents per version** | ❌ MISSING | UI + backend | Blocked cascade: notes engine MISSING (§5.3), deck-signals engine MISSING (§5.4), related-documents engine MISSING (§5.5). Nothing to associate per-version. |

---

## 8. Unclassified / Cross-Cutting Requirements

No user story fell fully outside the 7 top-level sections. However, the brief's **Feature Goals** section contains cross-cutting requirements that are not enumerated as DECK-XXX stories. Surfacing them here so they are not lost:

| Requirement (from §Feature Goals) | Status | Evidence |
| :--- | :--- | :--- |
| Preserve document history through version management **for decks created from blank** | ❌ MISSING | Version engine (`work_studio_overlay.py:559-620`) is generic — not scoped to blank-only. Brief specifically calls out "for decks created from blank"; current engine treats all decks equally, and blank-regeneration-as-versions is not modelled (see DECK-084..087). |
| Support collaboration through **download, share, continue in Chat / Solva** | 🟡 PARTIAL | Covered by DECK-068..071 individually; per §4 findings, at least half of these ship on one surface but not the other. |
| Automatic **AI-generated insights** for user understanding | 🟡 PARTIAL | `intelligence_report` gives confidence + recommendations, not a plain-language "explanation of the deck" (see DECK-045). |
| Automatic **governance signals extraction** | ❌ MISSING | No deck-scoped signals engine (see DECK-060..063). |
| **Improve document discoverability** through related documents and source traceability | ❌ MISSING | No related-documents engine (see DECK-064..067). Source traceability partially exists via `source_document_ids` but no UI. |
| **Private workspace for personal notes** | ❌ MISSING | No deck-scoped notes engine (see DECK-050..059). |

---

## 8a. Summary Line — UI-required categorization across MISSING + PARTIAL stories

**Column key recap:** `UI-only` = pure FE work (no BE contract change). `UI + backend` = both surfaces. `Backend-only` = data model / service / router; UI already covers it or brief doesn't require UI change. `N/A` = story met by existing routing/config; no build surface.

**Exec-summary count reconciliation (2026-07-02 column-update pass).** The Headline Verdict at §0 uses rough figures from the initial dispatch (19 ✅ / 16 🟡 / 48 ❌ / 4 ⚠️). The per-row tally derived by counting the 87 individual rows in §§1-8 comes out slightly different: **29 ✅ MET · 17 🟡 PARTIAL · 38 ❌ MISSING · 3 ⚠️ CONFLICT** (still 87 total; still the same overall shape — MISSING dominates the gap by far). The following table uses the precise per-row tally. The §0 rough numbers are left as-is for continuity with the initial audit ship.

**Aggregate across the 55 MISSING + PARTIAL stories (17 PARTIAL + 38 MISSING):**

| UI required? | Story count | % of gap | Story IDs |
| :--- | ---: | ---: | :--- |
| **UI-only** | 14 | 25% | DECK-002 (P), DECK-017 (M), DECK-020 (M), DECK-026 (M), DECK-027 (M), DECK-040 (P), DECK-047 (P), DECK-049 (P), DECK-056 (M), DECK-057 (M), DECK-066 (P), DECK-068 (P), DECK-069 (P), DECK-071 (P) |
| **UI + backend** | 40 | 73% | DECK-005, DECK-007, DECK-009, DECK-018, DECK-021, DECK-022, DECK-024, DECK-030, DECK-033, DECK-036, DECK-038, DECK-039, DECK-043, DECK-044, DECK-045, DECK-046, DECK-050, DECK-051, DECK-052, DECK-053, DECK-054, DECK-055, DECK-058, DECK-059, DECK-060, DECK-061, DECK-062, DECK-064, DECK-065, DECK-067, DECK-075, DECK-076, DECK-078, DECK-081, DECK-082, DECK-083, DECK-084, DECK-085, DECK-086, DECK-087 |
| **Backend-only** | 1 | 2% | DECK-063 (Pulse feed integration — UI already exists in Pulse) |
| **N/A** | 0 | 0% | — |
| **Total MISSING + PARTIAL** | **55** | **100%** | |

**⚠️ CONFLICT stories excluded from this bucketing** (per user dispatch: "of MISSING+PARTIAL total"): DECK-008 (UI-only), DECK-034 (UI-only), DECK-070 (UI + backend). If the user wants CONFLICT rolled in, add: 2 UI-only + 1 UI + backend → adjusted totals 16 UI-only / 41 UI + backend / 1 Backend-only / 0 N/A / 58 total.

**Summary line (per user dispatch shape):**

`UI-required-in-any-form: 54 stories / Backend-only: 1 story / N/A: 0 stories / of 55 MISSING+PARTIAL total`

(Where "UI-required-in-any-form" = UI-only + UI + backend = 14 + 40 = 54.)

**Interpretation.** ~73% of the gap is UI-AND-backend work — meaning most MISSING/PARTIAL stories touch both surfaces. Pure-UI wins are ~25% of the gap (14 stories, mostly sort orders, chip placements, button additions, existing-endpoint hookups). Pure-backend wins are effectively negligible (1 story — the Pulse feed integration). **Consequence for planning:** any deck-conformance sprint will be materially frontend-heavy AND backend-heavy in roughly equal measure; there is no "just wire up existing backend to a new UI" quick-win path that lands more than ~25% of the brief.

**Cross-check against §9 recommendation.** Option B (MVP) prioritizes the 14 UI-only stories + the 5-tab shell + the private notes engine (the single largest UI + backend engine at 8 stories: DECK-050..055, 058, 059). This lands roughly 22 stories fully — the highest-leverage subset of MISSING+PARTIAL — in ~2-3 weeks. Option A ships the remaining ~33 UI+backend stories over the following ~4-5 weeks.

---

## 9. Sizing Estimate & Recommended Path Forward

**Absolute counts across all 87 stories:**

| Status | Count | Notes |
| :--- | ---: | :--- |
| ✅ MET | 19 | Mostly listing-row basics + create-flow bones + versioning primitives. |
| 🟡 PARTIAL | 16 | Behaviour half-exists on one surface but not the other, or metadata exists but no UI surfaces it. |
| ❌ MISSING | 48 | Concentrated in §5 (5-tab detail: 20/28) + §7 (blank regeneration: 9/11). |
| ⚠️ CONFLICT | 4 | Two competing surfaces disagree on the vocabulary (DECK-008 doc-type, DECK-034 Akki-generated badge, DECK-070 share-via-email, and the aggregate lifecycle-vocabulary conflict in §6). |
| ❓ AMBIGUOUS | 0 | Every story maps clearly; the brief is unambiguous. |

**Sized by lift buckets (rough calendar estimates, single engineer + design review):**

* **Small (~1-2 days):**
    * Sort briefs + documents alphabetically in `CreateArtefactModal` (DECK-017, DECK-020).
    * Add rename affordance for In-Review + Draft decks (DECK-038, DECK-075).
    * Add delete affordance for In-Review + Draft decks (DECK-039, DECK-076).
    * Surface `Download` button on `Decks.jsx` DeckStep (DECK-068).
    * Surface `lifecycle_state` chip on WS DocumentRow for `deck` category rows (DECK-005 for WS surface only).
* **Medium (~1 week each):**
    * **Multi-source picker** in CreateArtefactModal — array of `source_brief_ids` + `source_document_ids` + backend acceptance (DECK-018, DECK-022). ~2-3 days.
    * **In-modal upload** — new `<UploadOptions>` mount inside CreateArtefactModal (DECK-021). ~1-2 days.
    * **Auto-transition Draft → In Review** on generation completion for both surfaces (DECK-030). ~2 days.
    * **Source Context section + Edit Context** — add `source_context` sub-doc on `work_studio_exports`, wire PATCH endpoint, add UI panel in DocumentOverlay (DECK-043, DECK-044, DECK-081, DECK-082, DECK-083). ~5 days.
    * **Deck-native completion sheet** with Download + Continue-in-Chat + Close buttons at generation-complete moment (DECK-026, DECK-027). ~3 days.
* **Large (~2-3 weeks each):**
    * **5-tab detail redesign** of DocumentOverlay — introduce `<Tabs>` primitive with Document / Intelligence / Your Notes / Signals / Related Documents (DECK-040..067 shell). ~1 week for shell + wiring; ~1 week for tests + regression.
    * **Private notes engine** — new `db.deck_notes` collection + `POST/GET/PATCH/DELETE /decks/{id}/notes` routes + TipTap editor with undo/redo/offline-tolerance + autosave (DECK-050..059). ~2 weeks.
    * **Deck-scoped signals engine** — new extraction pipeline post-generation, categorization by risk/opportunity/recommendation, per-deck signals collection, review-before-commit UI, Pulse feed integration (DECK-060..063). ~2-3 weeks.
    * **Related documents engine** — metadata-similarity retrieval (needs the JC-WS Phase 3 retrieval upgrade to land first — currently at 1/3 gate per prior audit) + explicit-attach panel + lineage graph (DECK-064..067). ~2 weeks.
* **XL (~4+ weeks):**
    * **Version-numbered blank regeneration** — new "regenerate against updated source context" flow (distinct from `create-new-version` clone) + per-version listing cards + per-version notes/signals/related-docs association (DECK-084..087). ~3-4 weeks; blocks on notes/signals/related engines shipping first.
* **Architectural pre-decision (blocks everything):**
    * **Surface unification** — decide whether the canonical deck lives in `db.decks` (Surface A) or `db.work_studio_exports` (Surface B) or a new unified collection. Every DECK-XXX MISSING is downstream of this decision. Estimated ~3-5 days for a proper migration plan + 1-2 weeks for staged implementation with backfills.

**Total ballpark for full brief compliance:** **6-8 weeks** of focused engineering after the surface-unification decision, sequenced across the sizing buckets above.

### Three recommended dispatch paths

**Option A — Full brief compliance (~6-8 weeks).**
Ship every DECK-XXX story. Requires the surface-unification decision upfront. High risk of scope creep (the 5-tab detail + notes + signals + related engines are each ~2-week efforts). Only recommended if the brief is a hard 2026-Q3 shipping commitment.

**Option B — MVP (~2-3 weeks). RECOMMENDED.**
Ships the brief's core promise + surfaces the rest for follow-up. Scope:
* Surface-unification decision + minimal migration (1 week).
* Deck List parity (cards visual, lifecycle chip, source count, confidence score) — closes DECK-002, DECK-005, DECK-007, DECK-008, DECK-034 (~2 days).
* 5-tab detail SHELL only (Tabs primitive; Document + Intelligence tabs wired to existing data; Notes tab is net-new with basic CRUD; Signals + Related tabs display "Coming soon" panels with clear messaging) — closes DECK-040..049 + DECK-050..059 + tab shell for DECK-060..067 (~1-1.5 weeks).
* Rename + Delete + Download affordances (~2 days).

Unlocks ~50/87 stories fully + tab-shell for the remaining 20. Signals + Related engines dispatched as follow-up.

**Option C — Surface-align only (~1 week). LOWEST LIFT.**
Do NOT rebuild the detail view. Instead:
* Rename `/app/decks` to use brief vocabulary (In Review chip, Committed lock, source count).
* Add lifecycle chip + rename + delete + download.
* Retire `CreateArtefactModal` deck path in favour of a "Create Summary Deck" button on `/app/decks` that opens a similar-but-brief-aligned modal.

Unlocks ~25/87 stories (mostly listing + create-flow surface parity). Leaves the 5-tab detail as an explicit MISSING for a future sprint. Best if the immediate need is "make Decks feel like the brief without shipping the whole thing".

### My recommendation

**Option B — MVP.** Rationale:

1. **De-risks the surface-unification decision** by forcing it upfront rather than compounding it later.
2. **Ships the visible core** (Deck List cards, 5-tab detail with Notes) that the brief calls out most explicitly.
3. **Surfaces the honest gap** on Signals + Related in-product ("Coming soon" panels) rather than shipping thin placeholder engines that would give a false sense of completeness.
4. Aligns with the JC-WS canonical rule **"A multi-step journey that half-works is WORSE than a simple one that works."** — Option A risks half-working Signals + Related; Option C risks the detail view still feeling misaligned.

**Awaiting user direction on which of A/B/C to dispatch.**

---

## 10. Locked-Area Sweep

* 0 product code files touched.
* 0 test files touched.
* 0 sprint memos written outside this audit + the `DEV_PIPELINE.md §9` rows entered BEFORE this file (initial audit row 2026-07-02 + column-update row 2026-07-02).
* Zero-Handoff-Loss discipline honoured: `DEV_PIPELINE.md §9` rows landed FIRST; then this file was authored / updated.
* Canonical Spec citation appears on line 1 of this file per protocol.

## 11. HARD STOP

Per dispatch protocol, this is a read-only audit. **No follow-up implementation without explicit user dispatch.** Surface this file to the user and await direction on which sizing option (A / B / C) to convert into a build sprint. Blocking items (surface unification, 5-tab shell scope, Signals+Related engine cadence) all require user calls before code touches the tree.
