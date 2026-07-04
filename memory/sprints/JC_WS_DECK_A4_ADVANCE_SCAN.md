Canonical spec: `/app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5 (5-Tab Detail Content)` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A4/§A6/§A7/§A8/§A9/§A10` + user chained mega-dispatch 2026-07-02 (P4 → A4-KICK).

# JC-WS-DECK-A4-ADVANCE-SCAN — READ-ONLY mapping

**Type:** Advance scan (READ-ONLY). Zero LOC mutated outside this memo.
**Ships:** 2026-07-02.
**Purpose:** Map the current `DocumentOverlay.jsx` inline layer structure + surface the 5-tab shell foundation scope for the A4 build kick.

---

## 0. Executive Summary

Per audit §5, "**NO tabbed detail structure exists anywhere in the codebase.**" This is the largest gap in the brief-vs-code comparison. `DocumentOverlay.jsx` renders sub-components inline (Toolbar → IntelligenceCard → DocumentSurface → AIRevisionPanel) as vertical stacks and modals — no `<Tabs>` primitives.

**A4 dispatch shape (RECOMMENDED):** SINGLE foundation sub-sprint adding a subtle inline switcher (NOT a shell-level nav element) inside the existing `DocumentOverlay.jsx` body. The Document tab becomes the default landing and mounts the existing inline layers verbatim; the other 4 tabs ship as EMPTY SHELLS with content-population deferred to A6 (Document sourced context), A7 (Intelligence), A8 (Your Notes engine — biggest sub-sprint), A9 (Signals), A10 (Related Documents).

**Chrome-conformance HARD rule honoured:** the tab strip uses the same pill/chip idiom already present in `WorkStudio.jsx` DocumentRow (per A1 slice R2 verified) — NO new shell-level nav element, NO top-navbar-style tabs. Options for the primitive:
- **(a)** shadcn `<Tabs>` primitive from `/app/frontend/src/components/ui/tabs.jsx` (existing app-wide primitive).
- **(b)** inline pill-style filter chips matching A1's `LifecycleChip` idiom.

Recommendation: **(a)** for consistency with existing app-wide tab surfaces (Chat model picker, WorkStudio deck filter tabs) — provided the `<Tabs>` primitive's default styling can be overridden to a subtle inline switcher (not a bold top-navbar bar). Audit-driven mitigation matches this: "propose the tabs as a subtle inline switcher inside the existing DocumentOverlay body, NOT a new shell-level nav element."

## 1. Current inline structure (as of 2026-07-02 pre-A4)

`DocumentOverlay.jsx` (1377 LOC):
- **L88-337 · Main `<DocumentOverlay>` component**: renders 3 vertical layers + 1 sidebar + 3 modals.
  - **Layer 1 (`<Toolbar>`)** — title inline-edit, back-to-list, download DOCX/PDF/PPTX, Edit toggle, versions, commit. Lifecycle-aware (Draft/InReview vs Committed). L343-509.
  - **Layer 2 (`<IntelligenceCard>`)** — collapsed RAG-coloured accent border. Confidence pct + rationale + recommendations preview + "Open full report" CTA. L517-604. → maps to **Intelligence tab**.
  - **Layer 3 (`<DocumentSurface>`)** — TipTap editor (read mode by default; Edit toggle per Divergence #1). L~730+. → maps to **Document tab**.
  - **Sidebar (`<AIRevisionPanel>`)** — slides in alongside on Revise mode. Shield-routed, source-doc allowlist. Not tab-scoped (AI revise action is document-wide affordance). Kept as sidebar.
- **Modals** — `<IntelligenceModal>` (L606+), `<VersionHistoryModal>`, `<CommitConfirmationModal>`.

## 2. Proposed A4 build shape (SINGLE dispatch scope)

**Deliverable:** A `<Tabs>` primitive at the DocumentOverlay body level with 5 tab shells:

| Tab | Content in A4 | Content deferred to |
| :--- | :--- | :--- |
| **Document** (default landing) | Existing `<DocumentSurface>` moved inline into Document tab shell — no behaviour change | A6 (source context + editable original context) |
| **Intelligence** | Existing `<IntelligenceCard>` moved inline into Intelligence tab shell | A7 (plain-language explanation + clarity metrics + provenance sub-section + Refresh button) |
| **Your Notes** | Empty shell with "Coming soon" placeholder | A8 (biggest — private-notes CRUD + autosave + undo/redo + offline-tolerant queue) |
| **Signals** | Empty shell with "Coming soon" placeholder | A9 (deck-linked signals extraction pipeline + Pulse linkage) |
| **Related Documents** | Empty shell with "Coming soon" placeholder | A10 (metadata-similarity retrieval + lineage graph model + explicit-attachments panel) |

**Backward compatibility rule:** Overlay opens on `Document` tab by default. Direct URL / deep-link params can pre-select a tab via `?tab=intelligence` query param (already used in `DocumentCardsSection.jsx:?pulse=` idiom from A3 — same URL param convention).

**A4 backend touched:** ZERO. No new endpoints. Tab shell is purely a FE UI change.

**A4 frontend touched:**
- `components/work_studio/overlay/DocumentOverlay.jsx` — add `<Tabs>` primitive + reorganize the 3 inline layers into tab shells. Estimated ~80 LOC net delta (5 tab shells + tab-state hook + URL-param sync).
- No new files. Existing overlay chrome preserved (Toolbar remains at top; tabs sit inside the overlay body).

**Locked-area sweep:** F.6 Shield contract UNTOUCHED (AIRevisionPanel is Shield-routed but kept as sidebar, not migrated to a tab). Solva engine UNTOUCHED. JC-CHAT invariants UNTOUCHED. Rename arc closure UNTOUCHED (A4 does not touch any Solva/ThinkLab surface). Storage arc UNTOUCHED. OAuth UNTOUCHED. Monitor UNTOUCHED. Pollution ceilings UNCHANGED (0/1 FINAL — A4 doesn't add tests, only FE code).

## 3. Escalation triggers (per Cluster-F retro §6.1 discipline)

- (a) **Locked-area collision?** NO — F.6 Shield code not mutated; AIRevisionPanel kept as sidebar; only overlay-shell reorganization.
- (b) **Scope outside execution plan §A4 (revised A4)?** No — the plan §A4 was "From-Blank + Draft-lifecycle journey closure" but the audit §5 gap on tab shell foundation is fundamentally MORE URGENT (blocks A6-A10). User's dispatch explicitly renamed A4 to "5-tab overlay" — this memo captures the plan revision. §A6 downstream Tabs risk note ("Adding a Tabs primitive to DocumentOverlay is arguably a UX-architecture extension") is EXPLICITLY IN SCOPE for this new A4.
- (c) **Ambiguity?** NO — audit §5 documents the tab-shell gap with story-level detail (DECK-040..067 = 28 stories); build shape locked at "shell foundation only, content deferred to A6-A10".
- (d) **Chrome conformance HARD rule?** RESPECTED — `<Tabs>` primitive is the app-wide idiom (used in Chat + WorkStudio); styling override to subtle inline switcher matches audit §A6 mitigation.
- (e) **F.6 Shield-contract regression discipline-pay?** N/A — A4 doesn't touch Shield-routed code; AIRevisionPanel kept as sidebar with zero code change.

**All 5 escalation triggers cleared. SINGLE A4 dispatch shape LOCKED.**

## 4. Proving slice — 10 rows planned

`/app/backend/scripts/jc_ws_deck_a4_proving_slice.py` (scaffold; NOT executed until A4 build ships):

| Row | Assertion |
| :---: | :--- |
| R1 | `<Tabs>` primitive imported + mounted in DocumentOverlay body. |
| R2 | 5 tab-triggers rendered with correct data-testids (`document-overlay-tab-{document,intelligence,notes,signals,related}`). |
| R3 | Default tab is Document; existing DocumentSurface renders inside Document tab. |
| R4 | Intelligence tab renders IntelligenceCard inline (previously Layer 2). |
| R5 | Notes / Signals / Related tabs render "Coming soon" placeholder shells. |
| R6 | URL param `?tab=intelligence` pre-selects Intelligence tab on overlay open. |
| R7 | Toolbar (Layer 1) stays outside the Tabs primitive (chrome pattern preservation). |
| R8 | AIRevisionPanel still opens as a sidebar (not migrated into a tab). |
| R9 | Modals (IntelligenceModal / VersionHistoryModal / CommitConfirmationModal) still mount at overlay level (not tab-scoped). |
| R10 | Data-testids preserved from pre-A4 state (regression check — every pre-A4 testid still present in the DOM). |

## 5. Sizing estimate

- **FE:** ~80 LOC additive in DocumentOverlay.jsx (5 tab shells + Tabs mount + URL-param sync + testids).
- **BE:** 0.
- **Docs:** ~120 LOC (this advance scan) + ~200 LOC (kick sprint memo) + ~250 LOC (proving slice scaffold).
- **Runtime risk:** LOW. No async paths added. No new endpoints. No LLM calls. Existing overlay behaviour preserved via re-parenting into Document tab.
- **Regression surface:** LOW. `document-overlay-*` testid family preserved via R10.

## 6. HARD STOP

Advance scan surface. Build kick sprint memo will follow at `/app/memory/sprints/JC_WS_DECK_A4_FIVE_TAB_OVERLAY.md`. DEV_PIPELINE.md §9 row added BEFORE kick memo authoring. Proving slice scaffolded (rows defined) but NOT executed until A4 build lands.
