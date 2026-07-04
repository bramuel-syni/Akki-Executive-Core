Canonical spec: `/app/memory/rules/TAB_HONESTY_RULE.md` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A6` + user dispatch 2026-07-02 (autonomous chain phase 3 of 4).

# JC-WS-DECK-A6-DOCUMENT-TAB-CONTENT — sprint memo

> **TAB HONESTY RULE applies** — outline sections computed from authoritative `doc.structured_content.sections` (returned by `/work-studio/documents/{aid}` GET). Not browser-local state.

> Corrected A5–A10 mapping (verified against JC_WS_DECK_PATH_A_EXECUTION_PLAN.md): A5=Detail-view header + footer parity + share · A6=Document tab (structured outline + source context) · A7=Intelligence tab completion · A8=Your Notes engine · A9=Signals tab + Pulse feed integration · A10=Related Documents tab + version-numbered blank regeneration.

**Type:** Document tab content-population · MVP. Autonomous chain phase 3 of 4.
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a6_proving_slice.py` (8 rows including REAL RENDER + regression).
**F.6 discipline-pay: N/A · pure FE render of existing document data, no LLM path.**
**Locked-area sweep:** F.6 UNTOUCHED · Solva engine UNTOUCHED · Rename arc hash intact · Chrome hard line (R7-R10) preserved.

---

## 0. Executive Summary

Populates the Document tab with:
- **DECK-040 · Structured outline** — clickable list of section headings (from `doc.structured_content.sections[i].heading`) rendered above `DocumentSurface`. Clicking a heading scrolls the surface editor to that `<h2>` via DOM text-match.
- **DECK-043 · Source-context pointer** — compact "Generated from N source documents" line + `Related →` button that switches active tab to `related` (using the existing `setActiveTab("related")` state setter).

## 1. Stories closed (MVP-level)

| Story | Coverage | Notes |
| :---: | :--- | :--- |
| DECK-040 Structured outline | ✅ MET | Reads `doc.structured_content.sections`; renders nested list; click-to-scroll via `scrollIntoView` on matching `<h2>` element. |
| DECK-043 Source-context pointer | ✅ MET | Renders count of `doc.source_document_ids` + link-out to Related Documents tab. |
| DECK-044 Edit source-context | ⚪ DEFERRED | Requires new PATCH endpoint for `source_context` field on documents + backend engine. Scope-escalation candidate. |

## 2. Files touched

**New (1):** `frontend/src/components/work_studio/overlay/DocumentOutline.jsx` (~100 LOC · outline list + source-context pointer + scrollIntoView helper).

**Modified (1):** `DocumentOverlay.jsx` — import DocumentOutline + mount above `<DocumentSurface>` inside Document `<TabsContent>` (~5 LOC net additive).

**Total: ~105 LOC additive FE · 0 backend LOC.**

## 3. Proving slice — 8 rows

`/app/backend/scripts/jc_ws_deck_a6_proving_slice.py`

| Row | Assertion |
| :---: | :--- |
| R1 | `DocumentOutline.jsx` file exists + default export + accepts `doc` + `onOpenRelatedTab` props. |
| R2 | REAL RENDER — outline reads `doc.structured_content.sections` + `.map()` over headings. |
| R3 | Click-to-scroll wiring — `scrollIntoView` invoked with heading-text match. |
| R4 | REAL RENDER — source-context section reads `doc.source_document_ids.length`. |
| R5 | Related tab pointer button dispatches `setActiveTab("related")` via `onOpenRelatedTab`. |
| R6 | Stable testids: `document-outline-root` · `document-outline-item` · `document-outline-open-related-btn` · `document-outline-source-context`. |
| R7 | Document `<TabsContent>` mounts `<DocumentOutline>` BEFORE `<DocumentSurface>` (outline is above surface content). |
| R8 | Regressions — A4 + A5 + A8-MVP + A8-BACKEND + A9 + A10 all GREEN. |

## 4. Chain gate — next dispatch

On A6 R1-R8 GREEN + regressions preserved: auto-fire A7 (Intelligence tab completion · plain-language + clarity metrics + provenance + Refresh button).
