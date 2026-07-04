Canonical spec: `/app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5 (5-Tab Detail Content · Signals tab, DECK-060..063)` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A9 (Signals tab + Pulse feed integration)` + user dispatch 2026-07-02 (populate-chain step 2 of 3).

# JC-WS-DECK-A9-SIGNALS-MVP — sprint memo

> Corrected A5–A10 mapping (verified against JC_WS_DECK_PATH_A_EXECUTION_PLAN.md): A5=Detail-view header + footer parity + share · A6=Document tab (structured outline + source context) · A7=Intelligence tab completion · A8=Your Notes engine · A9=Signals tab + Pulse feed integration · A10=Related Documents tab + version-numbered blank regeneration.

**Type:** Content-population sub-sprint · MVP scope. Populate-chain step 2 of 3.
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a9_proving_slice.py` (8 rows including REAL RENDER assertion). Testing sub-agents BANNED.
**Locked-area sweep:** F.6 Shield contract UNTOUCHED for MVP (0 Shield-routed code · 0 LLM calls · full-A9 extraction WILL pay F.6 discipline) · JC-CHAT invariants UNTOUCHED · Solva engine UNTOUCHED · Storage arc UNTOUCHED · Rename arc closure UNTOUCHED · A1/A2/A3/A4/A8 slices unaffected.

---

## 0. Executive Summary

Populates the "Signals" tab shell (A4 foundation) with an **FE-only MVP** that renders existing `doc.intelligence_report.recommendations` — no backend LOC, no new extraction pipeline, no F.6 discipline-pay.

**MVP shape:** categorized list of recommendations (existing shape doesn't distinguish risks vs opportunities; those require full backend engine). Each item shows text + addressed-state badge. Empty state when `intelligence_report` is null or `recommendations` is empty.

**Data contract (existing):**
- `doc.intelligence_report.recommendations` → `[{id: string, text: string, addressed: bool}, ...]` per `backend/routers/work_studio_export.py:1237`.
- No transformation needed. Just read + render.

**Deferred to full-A9 backend engine dispatch:**
- DECK-060 (extract signals FROM the deck) — new LLM prompt + `services/synisense/deck_signal_extraction.py` engine + `db.deck_signals` collection + F.6 Shield-contract discipline-pay verification.
- DECK-063 (committed signals available in Pulse) — backend feed integration into `get_synisense().list_signals` filter.

## 1. Stories closed (MVP-level)

| Story | Coverage | Notes |
| :---: | :--- | :--- |
| DECK-060 Signals extracted **from the deck** | ⚪ DEFERRED | Requires new LLM prompt + F.6 discipline-pay. Backend engine scope-escalation. |
| DECK-061 Categorize risks / opportunities / recommendations | 🟡 PARTIAL | Existing shape only distinguishes "recommendations"; risks/opportunities gated on full-A9 engine. |
| DECK-062 Review signals before commit | ✅ MET | `intelligence_report.recommendations` IS present pre-commit (populated at generation time). |
| DECK-063 Committed signals in Pulse | ⚪ DEFERRED | Backend feed integration required. |

**Net:** 1 story ✅ MET · 1 story 🟡 PARTIAL · 2 stories ⚪ DEFERRED (full-A9 engine).

## 2. Content acquisition (per user directive)

- **Grep-first result:** `db.signals` collection exists · `SyniSense.list_signals` exists · `services/synisense/engine/signal_derivation.py` exists — but all context-scoped, NOT deck-scoped. Extending to `deck_signals` requires new collection OR new field on `db.signals`.
- **Existing infrastructure USED:** `doc.intelligence_report.recommendations` (returned by `work_studio_overlay.py:311` in the doc payload). This IS the "existing shipped surface" per user's directive.
- **Backend LOC:** 0. Deck-signal extraction pipeline stays queued as scope-escalation.

## 3. §9 dashboard update

**On A9 MVP close:** 🟠 IN FLIGHT → 🟢 SHIPPED · FE-only MVP scope · Signals tab affordance visible + Signals flag flipped to `true`.

## 4. Proving slice — 8 rows

`/app/backend/scripts/jc_ws_deck_a9_proving_slice.py`

| Row | Assertion |
| :---: | :--- |
| R1 | `SignalsPanel.jsx` file exists at `frontend/src/components/work_studio/overlay/SignalsPanel.jsx` + exports default component + accepts `doc` prop. |
| R2 | Reads `doc.intelligence_report.recommendations` (existing shape). |
| R3 | Renders each recommendation with text + addressed-state (REAL RENDER: `.map(` over recommendations + JSX text binding). |
| R4 | `TAB_VISIBILITY.signals === true` in DocumentOverlay.jsx (flag flipped for MVP ship). |
| R5 | Signals `<TabsContent value="signals">` mounts `<SignalsPanel doc={doc} />` + "Coming soon" placeholder REMOVED. |
| R6 | Empty state rendered when `intelligence_report` is null or `recommendations` is empty (data-testid `signals-panel-empty-state`). |
| R7 | Stable testids on SignalsPanel: `signals-panel-root` · `signals-panel-item` · `signals-panel-empty-state`. |
| R8 | A4 slice regression 11/11 GREEN + A8 slice regression 9/9 GREEN (foundation + prior panel preserved). |

## 5. Acceptance criteria

- [ ] Proving slice 8/8 GREEN.
- [ ] A4 slice + A8 slice re-run GREEN (regression).
- [ ] `test_thinklab_uilabel_only.py` GREEN.
- [ ] `test_solva_v1_unchanged.py` GREEN.
- [ ] Webpack compiles clean.
- [ ] DEV_PIPELINE.md §9 A9 row flipped 🟠 IN FLIGHT → 🟢 SHIPPED.

## 6. User decision provenance

- 2026-07-02 · User dispatched populate-chain (Notes → Signals → Related Docs) with numbering-reconcile step.
- 2026-07-02 · User guardrail: "If content acquisition requires backend work beyond ~50 LOC, HARD STOP and surface — that's a scope escalation candidate."
- 2026-07-02 · Interpretation: FE-only render of existing `intelligence_report.recommendations` fits guardrail (0 backend LOC used). Full A9 backend extraction engine (~150+ LOC + F.6 discipline-pay) deferred.

## 7. Chain gate — next dispatch

On A9 R1-R8 GREEN + regression preserved: fire A10 (Related Docs MVP).
