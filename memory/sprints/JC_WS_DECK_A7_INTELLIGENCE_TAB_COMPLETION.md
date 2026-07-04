Canonical spec: `/app/memory/rules/TAB_HONESTY_RULE.md` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A7` + user dispatch 2026-07-02 (autonomous chain phase 4 of 4 · CHAIN CLOSE).

# JC-WS-DECK-A7-INTELLIGENCE-TAB-COMPLETION — sprint memo

> **TAB HONESTY RULE applies.** Intelligence data sourced from authoritative `doc.intelligence_report` (server-computed). Refresh is a pure GET re-fetch of already-computed data.

> Corrected A5–A10 mapping (verified against JC_WS_DECK_PATH_A_EXECUTION_PLAN.md): A5=Detail-view header + footer parity + share · A6=Document tab (structured outline + source context) · A7=Intelligence tab completion · A8=Your Notes engine · A9=Signals tab + Pulse feed integration · A10=Related Documents tab + version-numbered blank regeneration.

**Type:** Intelligence tab content-population · MVP. Autonomous chain phase 4 of 4 · CHAIN CLOSE.
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a7_proving_slice.py` (9 rows including REAL RENDER + regression + F.6 classification).

**F.6 discipline-pay: N/A · classified by execution.** Refresh Intelligence in this MVP is a **pure GET re-fetch** of the already-computed `intelligence_report` (via `loadDoc()` which calls the existing `GET /work-studio/documents/{aid}` endpoint). NO new LLM path. NO Shield-routed extraction. Full-A7 LLM-driven regeneration (if a future dispatch wants it) WILL require F.6 discipline-pay verification. This MVP dispatch does not touch that path.

**Locked-area sweep:** F.6 UNTOUCHED (Refresh path is pure re-fetch) · Solva engine UNTOUCHED · Rename arc hash intact · Storage UNTOUCHED · Chrome hard line (R7-R10) preserved · A4/A5/A6/A8-MVP/A8-BACKEND/A9/A10 slices unaffected.

---

## 0. Executive Summary

Populates the Intelligence tab with:
- **DECK-045 · Plain-language explanation** — renders `doc.confidence_rationale` (or `intelligence_report.confidence_rationale`) as prose.
- **DECK-046 · Clarity metrics** — 3-column grid showing `confidence_pct` · `sources_count` · `pending_recommendations`, with a `scored_at` timestamp.
- **DECK-047 · Provenance sub-section** — list of `doc.source_document_ids` as fixed-font chip IDs.
- **DECK-049 · Refresh Intelligence button** — calls `loadDoc()` prop (pure GET re-fetch); no LLM path.

Existing `<IntelligenceCard>` (compact confidence card) remains at top of the tab (backward compatible). New `<IntelligencePanelExpanded>` mounts BELOW the card.

## 1. Stories closed (MVP-level)

| Story | Coverage | Notes |
| :---: | :--- | :--- |
| DECK-045 Plain-language explanation | ✅ MET | Renders `confidence_rationale` prose. |
| DECK-046 Clarity metrics | ✅ MET | 3-col grid with confidence_pct + sources_count + pending_recs. |
| DECK-047 Provenance sub-section | ✅ MET | Lists `source_document_ids`. |
| DECK-049 Refresh Intelligence | ✅ MET | Pure re-fetch via `loadDoc` prop. F.6 N/A. |

## 2. Files touched

**New (1):** `frontend/src/components/work_studio/overlay/IntelligencePanelExpanded.jsx` (~150 LOC).

**Modified (1):** `DocumentOverlay.jsx` — import + mount below IntelligenceCard in Intelligence TabsContent (~7 LOC).

**Total: ~157 LOC additive FE · 0 backend LOC.**

## 3. Proving slice — 9 rows

`/app/backend/scripts/jc_ws_deck_a7_proving_slice.py`

| Row | Assertion |
| :---: | :--- |
| R1 | `IntelligencePanelExpanded.jsx` file exists + default export + accepts `doc` + `onRefresh` props. |
| R2 | REAL RENDER — reads `doc.confidence_rationale` (or `intelligence_report.confidence_rationale`) and renders as prose. |
| R3 | REAL RENDER — clarity metrics grid renders `confidence_pct` + `sources_count` + `pending_recommendations`. |
| R4 | REAL RENDER — provenance section renders `source_document_ids.map(...)`. |
| R5 | Refresh button calls `onRefresh()` prop (bound to `loadDoc` in DocumentOverlay). |
| R6 | Stable testids: `intelligence-panel-expanded-root` · `intelligence-panel-clarity-metrics` · `intelligence-panel-explanation` · `intelligence-panel-provenance` · `intelligence-panel-refresh-btn` · `intelligence-panel-confidence-pct` · `intelligence-panel-sources-count` · `intelligence-panel-pending-recs`. |
| R7 | Intelligence TabsContent mounts IntelligencePanelExpanded AFTER IntelligenceCard. |
| R8 | F.6 classification — no `shield_invoke` / no `get_synisense()` / no new LLM call introduced by A7 code (pure re-fetch). |
| R9 | Regressions — A4 + A5 + A6 + A8-MVP + A8-BACKEND + A9 + A10 all GREEN + P4 hash invariant GREEN. |

## 4. Chain gate — chain close

On A7 R1-R9 GREEN + regressions preserved: HARD STOP per user directive. Auto-chain A8-BACKEND → A5 → A6 → A7 closes here. Surface Trigger-2 to Orchestrator.
