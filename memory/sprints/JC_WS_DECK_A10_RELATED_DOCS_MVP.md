Canonical spec: `/app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5 (5-Tab Detail Content · Related Documents tab, DECK-064..067)` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A10 (Related Documents tab + version-numbered blank regeneration)` + user dispatch 2026-07-02 (populate-chain step 3 of 3).

# JC-WS-DECK-A10-RELATED-DOCS-MVP — sprint memo

> Corrected A5–A10 mapping (verified against JC_WS_DECK_PATH_A_EXECUTION_PLAN.md): A5=Detail-view header + footer parity + share · A6=Document tab (structured outline + source context) · A7=Intelligence tab completion · A8=Your Notes engine · A9=Signals tab + Pulse feed integration · A10=Related Documents tab + version-numbered blank regeneration.

**Type:** Content-population sub-sprint · MVP scope. Populate-chain step 3 of 3 (chain close).
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a10_proving_slice.py` (8 rows including REAL RENDER assertion). Testing sub-agents BANNED.
**Locked-area sweep:** F.6 Shield contract UNTOUCHED (0 Shield-routed code · 0 LLM calls) · JC-CHAT invariants UNTOUCHED · Solva engine UNTOUCHED · Storage arc UNTOUCHED · Rename arc closure UNTOUCHED · A1/A2/A3/A4/A8/A9 slices unaffected.

---

## 0. Executive Summary

Populates the "Related Documents" tab shell (A4 foundation) with an **FE-only MVP** that renders existing `doc.source_document_ids` — no backend LOC, no retrieval engine, no lineage graph.

**MVP shape:** list of source document IDs (existing `List[str]` on `work_studio_exports`) rendered as clickable chip-like items. Empty state when list is empty (blank-origin deck).

**Data contract (existing):**
- `doc.source_document_ids` → `List[str]` per `backend/services/work_studio_overlay.py:311`.
- No transformation needed. Just read + render.

**Deferred to full-A10 backend engine dispatch:**
- DECK-064 (view related documents) — requires new retrieval engine.
- DECK-065 (documents with shared metadata) — requires Phase 3 retrieval upgrade dependency.
- DECK-067 (same document lineage) — requires new lineage graph model.
- DECK-084/085/086/087 (version-numbered blank regeneration + independent per-version notes/signals/related) — requires `POST /work-studio/documents/{aid}/regenerate` route + version-tagged listing projection + partial F.6 discipline-pay for regenerate path.

## 1. Stories closed (MVP-level)

| Story | Coverage | Notes |
| :---: | :--- | :--- |
| DECK-064 View related documents | ⚪ DEFERRED | Requires new retrieval engine. |
| DECK-065 Documents with shared metadata | ⚪ DEFERRED | Requires Phase 3 retrieval upgrade. |
| DECK-066 Explicitly attached documents | ✅ MET | `source_document_ids` IS the explicit-attachment list. |
| DECK-067 Same document lineage | ⚪ DEFERRED | Requires new lineage graph model. |
| DECK-084/085/086/087 Version-numbered regeneration | ⚪ DEFERRED | Requires new regenerate route + partial F.6 pay. |

**Net:** 1 story ✅ MET · 7 stories ⚪ DEFERRED (full-A10 engine + F.6 payment).

## 2. Content acquisition (per user directive)

- **Grep-first result:** `attached_document_ids` exists on `chat` + `solva_v2` (session-scoped, not deck-scoped). No existing deck-related-documents retrieval engine. No lineage graph.
- **Existing infrastructure USED:** `doc.source_document_ids` (returned by `work_studio_overlay.py:311` in the doc payload). This IS the "existing shipped surface" per user's directive — decks created via A2's multi-source ingestion path already carry these IDs.
- **Backend LOC:** 0. Retrieval engine + lineage graph stays queued as scope-escalation.

## 3. §9 dashboard update

**On A10 MVP close:** 🟠 IN FLIGHT → 🟢 SHIPPED · FE-only MVP scope · Related Documents tab affordance visible + Related flag flipped to `true`. **POPULATE-THE-SHELL CHAIN CLOSED.** All 5 tabs (Document · Intelligence · Notes · Signals · Related) now visible + populated at MVP level.

## 4. Proving slice — 8 rows

`/app/backend/scripts/jc_ws_deck_a10_proving_slice.py`

| Row | Assertion |
| :---: | :--- |
| R1 | `RelatedDocuments.jsx` file exists at `frontend/src/components/work_studio/overlay/RelatedDocuments.jsx` + exports default component + accepts `doc` prop. |
| R2 | Reads `doc.source_document_ids` (existing shape). |
| R3 | REAL RENDER — `.map(` over source_document_ids + JSX chip rendering + click handler dispatching source-doc open event. |
| R4 | `TAB_VISIBILITY.related === true` in DocumentOverlay.jsx (flag flipped for MVP ship). |
| R5 | Related `<TabsContent value="related">` mounts `<RelatedDocuments doc={doc} />` + "Coming soon" placeholder REMOVED. |
| R6 | Empty state rendered when `source_document_ids` is empty (data-testid `related-docs-empty-state`). |
| R7 | Stable testids on RelatedDocuments: `related-docs-root` · `related-docs-item` · `related-docs-empty-state`. |
| R8 | A4 slice + A8 slice + A9 slice regressions GREEN (foundation + prior panels preserved). |

## 5. Acceptance criteria

- [ ] Proving slice 8/8 GREEN.
- [ ] A4 + A8 + A9 regressions GREEN.
- [ ] `test_thinklab_uilabel_only.py` GREEN.
- [ ] `test_solva_v1_unchanged.py` GREEN.
- [ ] Webpack compiles clean.
- [ ] DEV_PIPELINE.md §9 A10 row flipped 🟠 IN FLIGHT → 🟢 SHIPPED.
- [ ] Populate-the-shell chain status flipped to CHAIN CLOSED.

## 6. Chain gate — chain close

On A10 R1-R8 GREEN + regressions preserved:
1. Flip DEV_PIPELINE §9 A10 row 🟠 IN FLIGHT → 🟢 SHIPPED.
2. Flip populate-the-shell chain status to CLOSED.
3. Append 3 CHANGELOG entries at TOP (A10, A9, A8 in reverse-ship order).
4. Surface Trigger-2 report to user (chain-close close-out).
5. HARD STOP at chain close per user directive — no auto-fire beyond the 3 panels.
