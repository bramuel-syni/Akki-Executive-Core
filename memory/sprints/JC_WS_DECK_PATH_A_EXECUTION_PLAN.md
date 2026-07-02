**Canonical Spec:** `/app/memory/user_actions/uploaded_briefs/WORK_STUDIO_DECK_UX_BRIEF_V1_0.docx` v1.0 · 2nd July 2026 · **+ User Path-A pick 2026-07-02 with 2 constraints**: (1) "UX architecture does not get affected" — extend existing surfaces, no shell/nav redesign. (2) "Be careful not to make a journey completion action with a new feature or a UI surfacing ask" — each dispatch must close an existing journey, not create new ones.

# JC-WS-DECK-PATH-A-EXECUTION-PLAN

**Type:** READ-ONLY execution plan memo. **NOT a build dispatch.**
**Ships:** 2026-07-02.
**Dispatch:** Path-A user pick from `/app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §9`.
**Testing method:** N/A (planning memo; no code touched).
**Locked-area sweep:** 0 product code touched · 0 test files touched · 0 sprint memos written outside this memo + the `DEV_PIPELINE.md §9` row entered BEFORE this file.

---

## 0. Executive Summary

Path A = full compliance with the 87-story UX brief. Audit found **55 MISSING+PARTIAL** stories + **3 CONFLICT** stories = **58 stories to close**. Timeline: **6-8 weeks** across **10 JC-shaped sub-sprints**, each ~3-5 days, each closing an existing journey (not creating new ones) per user constraint (2).

**Discipline:** every sub-sprint MUST be a legitimate journey closure. A sub-sprint that "adds a new tab UI" is NOT allowed — that's a UI surfacing ask disguised as a JC. A sub-sprint that "closes the Document tab journey by wiring source-context surfacing to the existing DocumentOverlay" IS allowed — that closes an existing (broken) journey.

**Architectural constraint:** per user constraint (1), the underlying UX architecture is not touched. Concretely: no route renames, no shell/nav redesign, no new top-level surfaces. The two existing deck surfaces (`/app/decks` and `/app/work-studio` Deck tab) both continue to exist. Path A extends the `/app/work-studio` + `DocumentOverlay` surface as the primary compliance target (see §7 Surface-unification note — this is an explicit decision point).

**Non-scope (§10):** LLM_MODELS_REFRESH .3 (Solva quality) · storage arc · Google OAuth · K8s ingress · any non-brief feature.

**HARD STOP protocol** between sub-sprints (Cluster-G arc discipline): advance scan (if risk warrants) → fix dispatch → proving slice → surface → user approval → next.

---

## 1. Sub-Sprint Decomposition (10 sub-sprints, 55 gap-stories + 3 CONFLICT resolutions)

Each sub-sprint closes ONE user-visible journey. Each ships with a proving slice (~5-10 rows) gated on the sub-sprint's DECK-XXX story closures.

### JC-WS-DECK-A1 · Deck List completion (6 stories, ~3-4 days)

**Journey closed:** "User opens Decks and can identify what state each deck is in at a glance."

**Stories:**
- DECK-002 🟡 — decks as individual **deck cards** (visual metaphor; row → card).
- DECK-005 ❌ — **lifecycle status** chip on listing (Draft / In Review / Committed).
- DECK-007 🟡 — number of source documents on listing.
- DECK-008 ⚠️ CONFLICT — document type reconciliation (two competing sources — `category` vs `tier`).
- DECK-009 🟡 — confidence score reconciliation (`confidence_pct` vs `quality_check.score`).
- DECK-034 ⚠️ CONFLICT — "Akki-generated" badge on detail view (currently only on listing).

**Extends surface:** `WorkStudio.jsx` DocumentRow (already exists) + `DocumentOverlay` header for DECK-034.

**Risks:** DECK-008 + DECK-009 have upstream data-shape reconciliation — `db.decks` and `db.work_studio_exports` use different fields for "type" and "score". Sub-sprint MUST NOT propose a data migration; instead surface both fields in a unified way in the listing row.

**Backend changes:** minimal. `source_count` field needs backfill on `db.decks` rows during the read path (aggregate field on response, not schema).

**Proving slice:** ~8 rows. F.6 discipline-pay: N/A (no Shield-path changes).

**Success criteria:** 4 stories flip to ✅ MET (DECK-002, DECK-005, DECK-007, DECK-034). DECK-008 + DECK-009 flip to ✅ MET after reconciliation call.

---

### JC-WS-DECK-A2 · From-Source create journey closure (5 stories, ~4 days)

**Journey closed:** "User creates a deck from one or more briefs or uploaded documents, sorted alphabetically, with in-modal upload."

**Stories:**
- DECK-017 ❌ — briefs sorted alphabetically in `CreateArtefactModal`.
- DECK-018 ❌ — select **one or more** briefs.
- DECK-020 ❌ — uploaded documents sorted alphabetically.
- DECK-021 ❌ — upload a new document while creating a deck (in-modal upload).
- DECK-022 ❌ — select **one or more** uploaded documents.

**Extends surface:** `CreateArtefactModal.jsx` (already exists) — single-select → multi-select, sort added, `<UploadOptions>` mount added.

**Risks:** Multi-source ingestion — backend `CreateArtefactRequest` accepts singular `source_brief_id` / `source_document_id`. Extending to arrays MUST maintain backward compatibility (accept both singular and array shapes; deprecate singular in a future sprint).

**Backend changes:** `CreateArtefactRequest` schema extension (arrays). Downstream generator must aggregate multiple sources into one deck's `source_document_ids`.

**Proving slice:** ~7 rows. F.6 applicability: N/A.

**Success criteria:** 5 stories flip to ✅ MET.

---

### JC-WS-DECK-A3 · Generation-flow completion (4 stories, ~3-4 days)

**Journey closed:** "After user hits Generate, they see progress, then get immediate access to Download / Continue-in-Chat / Close, and the deck lands in the list as **In Review**."

**Stories:**
- DECK-024 🟡 — monitor progress of deck generation (WS-side parity with `/app/decks` streaming).
- DECK-026 ❌ — download immediately after generation.
- DECK-027 ❌ — continue in Chat immediately after generation.
- DECK-030 ❌ — newly generated deck as **In Review** (auto Draft → In Review transition on generation complete).

**Extends surface:** `CreateArtefactModal.jsx` completion state + WS-side generator streaming. Reuses existing `HandoffActions` "Take into Chat" logic (already open per JC-CHAT-STAGE-A-AMENDMENT).

**Risks:** DECK-024 requires WS-side generation streaming or webhook — current WS path is a synchronous POST. Options: (a) polling on `POST /work-studio/artefacts` response id (interim, no BE change); (b) SSE endpoint mirroring `/decks/{oid}/generate/stream`. Recommend (a) for A3 scope; (b) as a follow-on optimization if UX flags it insufficient.

**Backend changes:** Draft → In Review auto-transition on generation complete for both `db.decks` and `db.work_studio_exports` write paths (DECK-030). No new endpoints.

**Proving slice:** ~7 rows. F.6 applicability: N/A.

**Success criteria:** 4 stories flip to ✅ MET.

---

### JC-WS-DECK-A4 · From-Blank + Draft-lifecycle journey closure (6 stories, ~4 days)

**Journey closed:** "User authors a blank deck via DraftingDrawer, saves as draft, renames, deletes, or reopens as many times as they need."

**Stories:**
- DECK-075 ❌ — rename a draft deck title.
- DECK-076 ❌ — delete a draft deck.
- DECK-078 🟡 — continue editing saved context until ready to generate (source context vs draft body distinction surfaced).
- DECK-081 ❌ — view the original source context in the Document tab (foundation for A6).
- DECK-082 ❌ — edit the original source context from the Document tab.
- DECK-083 ❌ — save changes to source context without generating.

**Extends surface:** `DraftingDrawer.jsx` (rename + delete affordances) + `db.work_studio_exports` schema (new `source_context` sub-doc).

**Risks:** DECK-078 conceptually distinguishes "source context" (what the user typed to describe the deck) from "draft body" (the generated draft prose). Current code treats them as one. Sub-sprint MUST preserve backwards compat — existing drafts pre-migration have `source_context = null`, treated as "same as body" for read purposes.

**Backend changes:** `work_studio_exports.source_context` sub-doc (nullable string). New PATCH endpoints: `/work-studio/documents/{aid}/rename` + `/work-studio/documents/{aid}/source-context`. `DELETE /work-studio/documents/{aid}?state=draft`.

**Proving slice:** ~9 rows. F.6 applicability: N/A.

**Success criteria:** 6 stories flip to ✅ MET (DECK-081/082/083 close the SCHEMA-side; the UI surfacing lives in A6).

---

### JC-WS-DECK-A5 · Detail-view header + footer parity + share (8 stories, ~5 days)

**Journey closed:** "In the deck detail view, user can commit, close, rename, delete, download from any tab, share via email, continue in Chat, and continue in Solva."

**Stories:**
- DECK-033 🟡 — lifecycle status on detail view (both surfaces).
- DECK-036 🟡 — Commit action on `/app/decks` DeckStep (WS side already has it).
- DECK-038 ❌ — rename an In Review deck.
- DECK-039 ❌ — delete an In Review deck.
- DECK-068 🟡 — Download from any tab (button placement; needs tabs from A6 — see sequencing).
- DECK-069 🟡 — Continue in Chat (expand HandoffActions `kind` gate to include "deck").
- DECK-070 ⚠️ CONFLICT — Share via email (`ShareArtefactModal` present but semantics unclear).
- DECK-071 🟡 — Continue in Solva (mount HandoffActions in Overlay footer).

**Extends surface:** `DocumentOverlay.jsx` toolbar + `HandoffActions.jsx` gate expansion + `ShareArtefactModal.jsx` verification/extension.

**Risks:** DECK-070 CONFLICT — needs a decision: does the current ShareArtefactModal support email addressees, or is it link-only? Sub-sprint MUST audit before touching. If email-addressee flow is missing, needs a backend `POST /work-studio/documents/{aid}/share/email` endpoint. Recommend: surface as an A5-blocker decision point in the sub-sprint's advance scan.

**Backend changes:** `PATCH /work-studio/documents/{aid}/rename` (shared with A4). `DELETE /work-studio/documents/{aid}` (In-Review scope; Draft scope closed in A4). Potentially `/share/email` endpoint.

**Proving slice:** ~10 rows. F.6 applicability: partial (Continue-in-Chat handoff routes through Shield).

**Success criteria:** 6-8 stories flip to ✅ MET depending on DECK-070 decision.

---

### JC-WS-DECK-A6 · Document tab (structured outline + source context surfacing) (3 stories, ~3 days)

**Journey closed:** "User reviews the deck as a structured outline in the Document tab with source-context section for blank decks."

**Stories:**
- DECK-040 🟡 — structured outline navigation.
- DECK-043 ❌ — view original source context (Document tab).
- DECK-044 ❌ — edit original source context (Document tab).

**Extends surface:** `DocumentOverlay.jsx` — introduce `<Tabs>` primitive at the Overlay level with the Document tab as the default landing. Source-context section only renders for blank-origin decks.

**Risks:** ⚠️ This is the sub-sprint most-at-risk of violating user constraint (1). Adding a Tabs primitive to DocumentOverlay is arguably a UX-architecture extension. **Mitigation:** propose the tabs as a subtle inline switcher inside the existing DocumentOverlay body, NOT a new shell-level nav element. Style guardrails: no top-navbar-style tabs; use pill-style filter chips or a section-header switcher matching existing Akki idiom.

**Backend changes:** none (DECK-043/044 backend done in A4).

**Proving slice:** ~6 rows.

**Success criteria:** 3 stories flip to ✅ MET. Foundation for A7/A8/A9/A10.

---

### JC-WS-DECK-A7 · Intelligence tab completion (4 stories, ~4 days)

**Journey closed:** "User reads a plain-language explanation of the deck, sees clarity metrics and provenance, and can refresh intelligence."

**Stories:**
- DECK-045 🟡 — plain-language explanation of the deck.
- DECK-046 🟡 — clarity metrics (readability).
- DECK-047 🟡 — document provenance surfaced.
- DECK-049 🟡 — Refresh document intelligence button.

**Extends surface:** `DocumentOverlay.jsx` Intelligence tab (A6 shell) — mounts existing `IntelligenceCard` + `IntelligenceModal` into the tab; adds a Provenance sub-section rendering `origin` data; adds a Refresh button wired to existing `recompute-confidence` endpoint.

**Risks:** DECK-045 (plain-language) + DECK-046 (readability) may require a NEW LLM prompt or scoring engine. Sub-sprint MUST decide: (a) synthesize a plain-language explanation on-demand from `intelligence_report.confidence_rationale` + `recommendations` (no new LLM call, cheap) or (b) dedicated LLM prompt (new prompt, ties into LLM_MODELS_REFRESH .3). Recommend (a) for A7; (b) surfaces as an option to LLM_MODELS_REFRESH .3.

**Backend changes:** none required. Optional (Recommend A): extend `intelligence_report.plain_language_summary` derived field on read path.

**Proving slice:** ~7 rows. F.6 applicability: none.

**Success criteria:** 4 stories flip to ✅ MET.

---

### JC-WS-DECK-A8 · Your Notes engine (10 stories, ~7-10 days · BIGGEST SUB-SPRINT)

**Journey closed:** "User creates, edits, undoes, redoes, autosaves, and (if needed) clears private notes tethered to a deck, across sessions, with offline tolerance."

**Stories:**
- DECK-050 ❌ — Create notes.
- DECK-051 ❌ — Edit notes.
- DECK-052 ❌ — Delete parts of notes.
- DECK-053 ❌ — Autosave confirmation.
- DECK-054 ❌ — Return across sessions.
- DECK-055 ❌ — Continue editing after reopen.
- DECK-056 ❌ — Undo (session).
- DECK-057 ❌ — Redo (session).
- DECK-058 ❌ — Offline-tolerant editing.
- DECK-059 ❌ — Delete notes entirely.

**Extends surface:** `DocumentOverlay.jsx` Your Notes tab (A6 shell) — new `<DeckNotes>` component using TipTap StarterKit (undo/redo built in). Autosave via debounced PATCH with retry queue.

**Risks:** Largest single sub-sprint. Split into two dispatches if slice gets unwieldy: A8a (CRUD + persistence · DECK-050..055 + 059) and A8b (undo/redo + offline · DECK-056/057/058).

**Backend changes:** New `db.deck_notes` collection. New endpoints: `POST/GET/PATCH/DELETE /decks/{id}/notes` (idempotent PATCH). Tenancy scoped by deck's context_id + creator's user_id (notes are private).

**Proving slice:** ~12-15 rows. F.6 applicability: none (notes stay off the Shield path).

**Success criteria:** 10 stories flip to ✅ MET (or 7 for A8a + 3 for A8b if split).

---

### JC-WS-DECK-A9 · Signals tab + Pulse feed integration (4 stories, ~5-7 days)

**Journey closed:** "User reviews deck-scoped governance signals (risks/opportunities/recommendations) before commit; committed signals appear in Pulse."

**Stories:**
- DECK-060 ❌ — signals extracted **from the deck**.
- DECK-061 🟡 — categorize risks / opportunities / recommendations.
- DECK-062 ❌ — review signals before commit.
- DECK-063 ❌ — committed signals available in Pulse (Backend-only).

**Extends surface:** `DocumentOverlay.jsx` Signals tab (A6 shell) + Pulse's existing signals feed (no new UI surface in Pulse — just backend feed extends).

**Risks:** DECK-060 requires a new extraction pipeline post-generation. Options: (a) run signals extraction inline after deck generation (adds ~5-10s to generation latency); (b) run async post-generation via background task (introduces new delivery-status affordance on the tab). Recommend (b) — matches board-review latency expectations. **This crosses into governance-first territory** — see §7 for cross-cutting governance decision.

**Backend changes:** New `services/synisense/deck_signal_extraction.py` (Shield-routed LLM prompt on `structured_content`). New `db.deck_signals` collection scoped `{deck_id, kind, ...}`. Integration into `get_synisense().list_signals` filter for Pulse feed inclusion (DECK-063).

**Proving slice:** ~9 rows. F.6 applicability: ⚠️ YES — extraction goes through Shield. F.6 discipline-pay tests must be re-run and confirmed GREEN.

**Success criteria:** 4 stories flip to ✅ MET.

---

### JC-WS-DECK-A10 · Related Documents tab + version-numbered blank regeneration (8 stories, ~7-10 days)

**Journey closed:** "User sees documents related to the deck via shared metadata / explicit attachment / same lineage; and for blank decks, regenerating produces a new deck card with a version number, preserving previous versions."

**Stories:**
- DECK-064 ❌ — view related documents.
- DECK-065 ❌ — documents with shared metadata.
- DECK-066 🟡 — explicitly attached documents.
- DECK-067 ❌ — same document lineage.
- DECK-084 ❌ — generate a new version using updated source context.
- DECK-085 ❌ — each regenerated deck as separate card.
- DECK-086 ❌ — version numbers surfaced.
- DECK-087 ❌ — independent notes/signals/related per version.

**Extends surface:** `DocumentOverlay.jsx` Related Documents tab (A6 shell) + WS listing (per-version cards + version-number badges).

**Risks:** 
- DECK-065 (shared metadata retrieval) BLOCKS on the JC-WS Phase 3 retrieval upgrade (currently at 1/3 gate per audit). If Phase 3 hasn't landed by A10 dispatch time, sub-sprint MUST scope DECK-065 as PARTIAL with a follow-up dispatch trigger.
- DECK-087 (independent per-version notes/signals/related) is a cascade dependency on A8 (Notes) + A9 (Signals) + A10 (Related) all shipping. Blocked cascade — this sub-sprint is the FINAL brick in the wall.
- DECK-084 (regenerate against updated source context) is a NEW generation pattern distinct from `create-new-version` (which clones committed content). Requires re-invoking the deck generator with the updated `source_context` from A4.

**Backend changes:** New retrieval engine for DECK-065 (deferred if Phase 3 not landed). Metadata + lineage graph model. Version-tagged listing projection. `POST /work-studio/documents/{aid}/regenerate` (new endpoint distinct from create-new-version).

**Proving slice:** ~12-15 rows. F.6 applicability: partial (regeneration goes through Shield).

**Success criteria:** 8 stories flip to ✅ MET (or 7 if DECK-065 remains PARTIAL pending Phase 3).

---

## 2. Sequencing / Dependency Graph

```
Independent kickoffs (parallel-safe):
  A1 (Deck List)  ────┐
                      │
  A2 (From-Source) ───┤
                      │
  A3 (Generation)  ───┤
                      │
                      ▼
                    [foundation done]
                      │
                      ▼
  A4 (From-Blank+Draft-lifecycle) ─────► A6 (Document tab · needs A4 source_context)
                                          │
                                          ▼
  A5 (Detail header+footer parity) ─────► A6 tabs shell mounts (blocks on A6)
                                          │
                                          ▼
                                        A7 (Intelligence tab) ────┐
                                        A8 (Your Notes engine) ───┤ parallel-safe once A6 lands
                                        A9 (Signals tab) ─────────┘
                                          │
                                          ▼
                                        A10 (Related + Version) ──── blocks on A8+A9
```

**Critical path (linear, no parallelization):** A1 → A4 → A6 → A8 → A10. **~6 weeks.**

**Parallel opportunities:**
- A1, A2, A3 can ship in parallel (no cross-dependencies).
- A7, A8, A9 can ship in parallel once A6 shell is live.
- A5 can start alongside A1-A3; must land BEFORE A6 (tabs shell needs the header/footer affordances alongside).

**Total calendar:** 6 weeks critical path · +1-2 weeks buffer for A8 split (A8a + A8b) and A10 dependency on Phase 3 retrieval upgrade = **~7-8 weeks realistic**.

---

## 3. Backend Contract Surface (cross-sub-sprint summary)

| Change | Owner sub-sprint | Type |
| :--- | :--- | :--- |
| `CreateArtefactRequest` — arrays for source_brief_ids / source_document_ids (backward-compat) | A2 | Extension |
| Draft → In Review auto-transition on generation complete | A3 | Behaviour |
| `work_studio_exports.source_context` sub-doc | A4 | Schema |
| `PATCH /work-studio/documents/{aid}/rename` | A4 (shared A5) | New route |
| `PATCH /work-studio/documents/{aid}/source-context` | A4 | New route |
| `DELETE /work-studio/documents/{aid}?state=draft` | A4 | New route |
| `DELETE /work-studio/documents/{aid}` (In Review scope) | A5 | New route |
| `POST /work-studio/documents/{aid}/share/email` (if A5 decision requires) | A5 | New route |
| HandoffActions `kind` gate expansion (FE-only) | A5 | FE-only |
| `intelligence_report.plain_language_summary` derived field | A7 | Read-path |
| `db.deck_notes` collection + full CRUD routes | A8 | New collection |
| `services/synisense/deck_signal_extraction.py` + `db.deck_signals` collection | A9 | New engine (F.6-adjacent) |
| Related-documents retrieval engine | A10 | New engine |
| Lineage graph + version-tagged listing projection | A10 | Read-path |
| `POST /work-studio/documents/{aid}/regenerate` | A10 | New route |

**F.6 Shield-contract discipline-pay applicability:** A9 (deck-signal extraction) + A10 (regenerate). Both sub-sprints must include F.6 GREEN verification in their proving slice.

**JC-CHAT invariant applicability:** A3 + A5 (Continue-in-Chat handoff routes). Both sub-sprints must include JC-CHAT invariant GREEN verification.

---

## 4. Cross-Integration Expectations (Chat / Solva / Pulse)

**Chat hook:**
- DECK-027 (Continue in Chat immediately after generation) — A3.
- DECK-069 (Continue discussing the deck in Chat) — A5. Existing HandoffActions "Ask in Chat" component; gate expansion only.

**Solva hook:**
- DECK-071 (Continue analysing in Solva) — A5. Existing `takeToSolva` handoff; mount in Overlay footer.

**Pulse hook:**
- DECK-063 (committed signals available in Pulse) — A9. Backend-only feed integration; no new Pulse UI.

All three hooks use EXISTING infrastructure. No new integration endpoints. No new authentication flows. Full compliance is achieved through affordance placement + backend feed extension.

---

## 5. Surface-Unification Note (EXPLICIT DECISION POINT for user)

The audit surfaces two orthogonal deck surfaces:

* **Surface A — `/app/decks`** (`Decks.jsx` · 3-step Intent → Outline → Deck flow · writes to `db.decks`).
* **Surface B — `/app/work-studio` Deck tab** (`WorkStudio.jsx` · `DocumentOverlay` · reads unified `documents?category=deck` · writes to `db.work_studio_exports`).

**User constraint (1):** "UX architecture does not get affected." Meaning: neither surface is deprecated / removed as part of Path A.

**Recommendation:** Path A extends Surface B as the primary compliance target. Reasoning:
1. Surface B already has the brief-required lifecycle vocabulary (`draft` / `in_review` / `committed` on `work_studio_exports`).
2. Surface B has the DocumentOverlay slot into which A6 tabs can be introduced without shell/nav changes.
3. Surface B has intelligence_report + versioning infrastructure aligned with the brief.
4. Surface A remains as the "3-step wizard" fast-path for power users; it does NOT need to gain 5-tab detail (retain its current linear review UX).

**Explicit user decision required BEFORE A1 dispatches:**
- **Option (i) RECOMMENDED:** Surface B is authoritative. Path A extends Surface B only. Surface A is preserved as a legacy fast-path but does NOT gain brief-required features (lifecycle chip, 5 tabs, etc.). Brief conformance is measured against Surface B only.
- **Option (ii):** Both surfaces must reach brief compliance. Roughly doubles the FE scope for Deck List + Detail-view sub-sprints (A1, A5, A6-A10 each need dual-implementation).
- **Option (iii):** Surface A is authoritative. Migrate Surface B's lifecycle model back onto `db.decks`; retire the `work_studio_exports` deck path. This IS a UX-architecture change per user constraint (1), so recommend REJECT.

**User must pick (i) / (ii) before A1 fires.**

---

## 6. Governance-First Requirement (cross-cutting decision)

The brief's "governance signals extraction" + "provenance / source traceability" requirements are cross-cutting across A5, A7, A9, A10.

**Option A — Dedicated sub-sprint (A11 Governance):** Bundle all governance surfaces into one sub-sprint. **REJECTED** because this violates user constraint (2) — "governance sub-sprint" is a UI-surfacing dispatch, not a journey closure.

**Option B — Thread through existing sub-sprints (RECOMMENDED):**
- A5 (Detail-view header+footer) picks up: provenance chip in header (part of DECK-032/033 completion).
- A7 (Intelligence tab) picks up: provenance panel (DECK-047).
- A9 (Signals tab) picks up: deck-scoped signals extraction (DECK-060..062) + Pulse feed integration (DECK-063).
- A10 (Related tab) picks up: metadata + lineage source-traceability (DECK-064..067).

Each closes an existing tab-journey; governance is the natural infrastructure landing under each.

**Verdict: Option B.**

---

## 7. Solva Output Quality FAIL Loop-in

User separately signaled Solva deck output is not board-forward today. Path A is a structural set of changes. Some of it will move the quality needle; some won't.

**Structural moves in Path A that ARE quality-adjacent:**
- **A6** — Source-context surfacing gives reviewers visibility into what the user asked for (currently invisible → suddenly explainable). Materially improves review-desk feel.
- **A7** — Plain-language explanation + clarity metrics (currently only a confidence rationale) improves board-forward comprehension.
- **A9** — Deck-scoped signals extraction converts implicit governance concerns into explicit review artifacts. High board-forward impact.
- **A10** — Related documents + lineage answers "where did this come from" — high provenance value for board settings.

**NOT quality-adjacent (pure UX plumbing):**
- A1, A2, A3, A4, A5, A8 — these fix journey completeness but don't touch generation quality.

**LLM-model quality dimension (orthogonal):**
- `LLM_MODELS_REFRESH .3` — deck-generation model bump (backlogged pending user sign-off in the audit).
- Deck-generation prompt engineering — not currently in Path A scope; recommend a separate sub-track (`LLM_MODELS_REFRESH .4` or similar) if user wants to attack the pure prompt-tuning dimension.

**Recommendation:** Ship Path A as-is; observe the quality delta after A6+A7+A9+A10 land. If quality is still sub-par, dispatch `LLM_MODELS_REFRESH .3` + prompt tuning as a separate track.

---

## 8. What Path A Will NOT Do (scope-creep prevention)

* Will NOT rewrite UX architecture (user constraint 1).
* Will NOT create new top-level surfaces beyond the brief.
* Will NOT create new UI surfaces beyond DocumentOverlay tabs shell + inline additions.
* Will NOT deprecate `/app/decks` Surface A (retained as legacy fast-path).
* Will NOT bundle non-brief features (no Solva output quality → separate track).
* Will NOT resolve `LLM_MODELS_REFRESH .3` (separate track, backlogged).
* Will NOT touch storage arc (separate track — Azure Blob path pending creds).
* Will NOT touch Google OAuth native flow (parked, no creds).
* Will NOT extend beyond DocumentOverlay for the 5-tab detail — the brief specifies 5 tabs, no more.
* Will NOT proceed to next sub-sprint without user approval on prior sub-sprint's proving slice (Cluster-G arc discipline).
* Will NOT ship a sub-sprint that fails F.6 discipline-pay or JC-CHAT invariant checks (hard gate).

---

## 9. HARD STOP Protocol Between Sub-Sprints

Same discipline as Cluster-G arc:

1. **Advance scan** (only if risk warrants — e.g., A5 CONFLICT resolutions, A9 F.6-adjacent extraction pipeline, A10 Phase 3 dependency).
2. **Fix dispatch** — sub-sprint dispatch memo authored (Canonical Spec line 1 = this Path A plan + specific sub-sprint's brief clause).
3. **Proving slice** — 5-15 rows, ALL GREEN.
4. **Surface** to user with proving-slice results + DECK-XXX story-status flips.
5. **User approval** required before next sub-sprint dispatches.
6. **Next sub-sprint** per sequencing map in §2.

Non-negotiable gates on every sub-sprint's proving slice:
* JC-CHAT invariants GREEN (if any Chat handoff touched).
* F.6 Shield-contract discipline-pay GREEN (if any Shield-adjacent path touched — A3 handoff, A9 extraction, A10 regenerate).
* Existing test suite GREEN (no regression tolerance).
* Locked-area sweep clean.
* Zero-Handoff-Loss adherence — `DEV_PIPELINE.md §9` row BEFORE sub-sprint dispatch memo.
* Canonical Spec citation on line 1 of every sub-sprint memo.

---

## 10. Explicit User Decision Points Before A1 Dispatches

1. **Surface-unification (§5)** — pick (i) or (ii). (iii) is not recommended.
2. **Governance-first (§6)** — confirm Option B (thread through) vs Option A (dedicated sub-sprint).
3. **A5 DECK-070 share-via-email semantics** — needs advance-scan verdict (email addressee vs link-only).
4. **A6 Tabs primitive style** — subtle inline switcher inside DocumentOverlay body (per user constraint 1) vs top-bar tabs. Recommend subtle inline.
5. **A7 DECK-045/046 quality** — synthesize on read (no new LLM call) vs new prompt (ties into LLM_MODELS_REFRESH .3). Recommend synthesize.
6. **A8 split** — A8a + A8b if scope blows up during dispatch, or single A8 dispatch. Recommend single A8; split contingently if slice grows > 15 rows.
7. **A10 DECK-065 dependency** — proceed if Phase 3 retrieval upgrade landed; else scope DECK-065 as PARTIAL with follow-on trigger. Advance scan required before A10 fires.

**All 7 decisions are surfaced here in one memo to minimize back-and-forth. User can approve in bulk or per-item.**

---

## 11. Locked-Area Sweep

* 0 product code touched.
* 0 test files touched.
* 0 sprint memos written outside this memo.
* `DEV_PIPELINE.md §9` row landed BEFORE this file per Zero-Handoff-Loss.
* Canonical Spec citation on line 1 of this memo (audit brief path + Path A user pick date + 2 user constraints).
* Six banked lessons in play (locked-area sweep, F.6, JC-CHAT, Zero-Handoff-Loss, UNQUARANTINED runtime baseline, Cluster-G arc HARD-STOP protocol).

## 12. HARD STOP

Read-only execution plan complete. **No sub-sprint dispatches without explicit user approval on §10 decision points.** Surfacing for user direction on:

* Which surface-unification option (§5).
* Confirm governance-first thread (§6).
* Any pre-dispatch clarifications on the 10 sub-sprints or 7 §10 decision points.
* Timing — start immediately or wait until upstream blocked items (LLM_MODELS_REFRESH .3, storage arc) clear.

Once approved, Path A opens with `JC-WS-DECK-A1` dispatch on the sequencing map.
