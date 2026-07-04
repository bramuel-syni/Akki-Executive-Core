Canonical spec: `/app/memory/rules/TAB_HONESTY_RULE.md` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A5` + user dispatch 2026-07-02 (autonomous chain phase 2 of 4).

# JC-WS-DECK-A5-HEADER-FOOTER-PARITY-SHARE — sprint memo

> **TAB HONESTY RULE applies.** Share now stands on real persistence (A8-BACKEND deck_notes CRUD shipped 2026-07-02 same dispatch). Share URLs reference `artefact_id` + `activeTab` only; recipient's own notes fetched per-their-account (private-per-account · never leak).

> Corrected A5–A10 mapping (verified against JC_WS_DECK_PATH_A_EXECUTION_PLAN.md): A5=Detail-view header + footer parity + share · A6=Document tab (structured outline + source context) · A7=Intelligence tab completion · A8=Your Notes engine · A9=Signals tab + Pulse feed integration · A10=Related Documents tab + version-numbered blank regeneration.

**Type:** Detail-view content-population sub-sprint. Autonomous chain phase 2 of 4.
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a5_proving_slice.py` (9 rows including REAL RENDER + share URL builder + regression).
**Locked-area sweep:** F.6 UNTOUCHED · Solva engine UNTOUCHED · Rename arc hash intact · Storage UNTOUCHED · Chrome hard line (R7-R10) preserved · A4/A8/A8-BACKEND/A9/A10 unaffected.

**F.6 discipline-pay: N/A · pure FE content-population with client-side URL builder + custom-event dispatches. Zero backend LOC. No LLM path.**

---

## 0. Executive Summary

Populates the detail-view **footer** with 4 affordances reachable from any active tab:
- **Continue in Chat** — dispatches `akki:continue-in-chat` window event (consumer wire-up deferred to a Chat sub-sprint; button EXISTS + dispatches per §A5 spec).
- **Continue in ThinkLab** — dispatches `akki:continue-in-solva` window event (same pattern; branded ThinkLab per rename arc).
- **Download** — reuses existing render endpoint `/work-studio/documents/{aid}/render?format=docx` (default DOCX; DOCX/PDF/PPTX in Toolbar remain unchanged).
- **Share** — client-side URL builder: `${window.location.href}?artefact_id={aid}&tab={activeTab}`; copies to clipboard via `navigator.clipboard.writeText`; toast confirmation + "Copied!" state.

Header parity: existing Toolbar chrome already carries deck title (inline-edit) + lifecycle chip + owner/timestamp + Version-history + Move-to-Review + Commit + DOCX/PDF/PPTX (via T4.1). A5 does NOT rewrite Toolbar — the pre-existing header IS parity-ready.

## 1. Chrome hard line (R7-R10) preserved

- **R7 Toolbar outside Tabs:** UNCHANGED. Toolbar was already outside `<Tabs>`.
- **R8 AIRevisionPanel sidebar:** UNCHANGED. Not touched.
- **R9 Modals overlay-level:** UNCHANGED. Not touched.
- **R10 Testid preservation:** every pre-A5 testid preserved. DetailFooter adds 5 NEW testids (`document-overlay-detail-footer` + 4 button testids).
- **DetailFooter mounts OUTSIDE the Tabs primitive** — it's overlay chrome, not a tab shell child. Same chrome-preservation rule as Toolbar. ✅

## 2. Files touched

**New (1):** `frontend/src/components/work_studio/overlay/DetailFooter.jsx` (~110 LOC · 4 buttons with lucide icons + share URL builder + clipboard writer + toast confirmation).

**Modified (2):**
- `DocumentOverlay.jsx` — import DetailFooter + extract `handleDownload` shared callback + mount `<DetailFooter>` immediately after `</Tabs>` (~15 LOC net additive after callback extraction).
- `memory/DEV_PIPELINE.md` §9 A5 row.

**Total: ~125 LOC additive FE · 0 backend LOC.**

## 3. Proving slice — 9 rows

`/app/backend/scripts/jc_ws_deck_a5_proving_slice.py`

| Row | Assertion |
| :---: | :--- |
| R1 | `DetailFooter.jsx` file exists + default export + accepts `contextId`, `artefactId`, `activeTab`, `onDownload` props. |
| R2 | 4 affordance testids present: `document-overlay-continue-in-chat-btn` · `document-overlay-continue-in-solva-btn` · `document-overlay-footer-download-btn` · `document-overlay-share-btn`. |
| R3 | REAL RENDER: Continue-in-Chat button dispatches `akki:continue-in-chat` window CustomEvent with `{contextId, artefactId}`. |
| R4 | REAL RENDER: Continue-in-Solva button dispatches `akki:continue-in-solva` window CustomEvent. |
| R5 | REAL RENDER: Share button constructs URL via `URLSearchParams`, includes `artefact_id` and `tab` params, calls `navigator.clipboard.writeText`. |
| R6 | Footer download button calls the shared `handleDownload` callback (chain wiring). |
| R7 | DocumentOverlay imports + mounts `<DetailFooter>` OUTSIDE the `<Tabs>` primitive (chrome hard line preservation). |
| R8 | Existing DOCX/PDF/PPTX Toolbar affordances preserved (data-testids intact). |
| R9 | Regressions: A4 (11/11) + A8-MVP (9/9) + A8-BACKEND (11/11 · via server call) + A9 (8/8) + A10 (8/8) all GREEN. |

## 4. Acceptance criteria

- [ ] Proving slice 9/9 GREEN.
- [ ] All prior slices regression GREEN.
- [ ] Webpack compiles clean.
- [ ] Chrome hard line R7-R10 preserved.

## 5. Chain gate — next dispatch

On A5 R1-R9 GREEN + regressions preserved: auto-fire A6 (Document tab content: structured outline + source-context section + edit-source-context).
