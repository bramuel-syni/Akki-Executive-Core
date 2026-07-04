Canonical spec: `/app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5 (5-Tab Detail Content)` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md` + `/app/memory/sprints/JC_WS_DECK_A4_ADVANCE_SCAN.md` + user chained mega-dispatch 2026-07-02 (P4 → A4-KICK).

# JC-WS-DECK-A4-FIVE-TAB-OVERLAY — sprint kick memo

**Type:** Build sub-sprint. **Third Path A dispatch. IN FLIGHT.**
**Ships:** 2026-07-02 (kick) → build execution in this or next dispatch.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a4_proving_slice.py` (10 rows, scaffolded, executed on build close). Testing sub-agents BANNED.
**Locked-area sweep:** F.6 Shield contract UNTOUCHED · JC-CHAT invariants UNTOUCHED · Solva engine UNTOUCHED · Storage arc UNTOUCHED · OAuth UNTOUCHED · Monitor UNTOUCHED · Surface A UNTOUCHED · Rename arc closure UNTOUCHED · Path A A1/A2/A3 slices UNCHANGED.

---

## 0. Executive Summary

Path A's third dispatch. Fills the largest brief-vs-code gap surfaced by the conformance audit §5: `NO tabbed detail structure exists anywhere in the codebase`. A4 adds the tab-shell foundation as a subtle inline switcher inside `DocumentOverlay.jsx` — the Document tab becomes the default landing and mounts the existing inline layers verbatim; the other 4 tabs ship as EMPTY SHELLS with content-population deferred to A6-A10.

**Story flips deferred to A6-A10.** A4's stories are foundational — it establishes the 5-tab shell that A6 (Document tab content), A7 (Intelligence tab content), A8 (Your Notes engine), A9 (Signals tab content), A10 (Related Documents) will populate in subsequent sub-sprints.

**What ships in A4:**

| Deliverable | State |
| :--- | :--- |
| `<Tabs>` primitive mounted at DocumentOverlay body level | ✅ Foundation |
| 5 tab shells (Document · Intelligence · Your Notes · Signals · Related Documents) | ✅ Foundation |
| Document tab as default landing (existing DocumentSurface re-parented) | ✅ Foundation |
| Intelligence tab renders existing IntelligenceCard (Layer 2 re-parented) | ✅ Foundation |
| Notes / Signals / Related tabs render "Coming soon" placeholder | ✅ Placeholder |
| URL param `?tab=<name>` pre-selects tab (same idiom as A3's `?pulse=` scroll-and-glow) | ✅ Foundation |
| Data-testids preserved from pre-A4 state (regression check) | ✅ Preserved |

**Chrome conformance HARD rule honoured:** `<Tabs>` primitive is the app-wide idiom (shadcn `/app/frontend/src/components/ui/tabs.jsx`). Styling overridden to a subtle inline switcher matching audit §A6 mitigation ("propose the tabs as a subtle inline switcher inside the existing DocumentOverlay body, NOT a new shell-level nav element"). Pill-style filter chips matching A1's `LifecycleChip` idiom serve as the fallback style if shadcn `<Tabs>` default styling proves too prominent.

**Backend touched:** ZERO. No new endpoints. No new DB schema. No new LLM prompts. Tab shell is purely a FE UI reorganization.

**Frontend touched:** `components/work_studio/overlay/DocumentOverlay.jsx` (~80 LOC net additive: 5 tab shells + Tabs mount + URL-param sync + testids).

## 1. Chrome conformance recap

Per user A1 dispatch amendment 2026-07-02 (three-pick resolution): **"new features arrive INSIDE existing shells and conform to existing patterns"**. A4 honours this by:

- Reusing shadcn `<Tabs>` primitive (already imported in Chat model picker, WorkStudio deck filter).
- Preserving the existing overlay chrome (Toolbar stays outside Tabs; Modals stay overlay-level; AIRevisionPanel stays as sidebar).
- Re-parenting existing inline layers (DocumentSurface, IntelligenceCard) into tab shells without behaviour change.
- Preserving every pre-A4 `data-testid` value (R10 regression check).
- No parallel components. No new drawer variant. No shell-level nav.

## 2. Deferred to A6-A10 (out of A4 scope)

| Sub-sprint | Fills |
| :--- | :--- |
| A5 | Detail-view header + footer parity + share (unchanged from execution plan §A5). |
| A6 | Document tab content: structured outline navigation (DECK-040), source-context section (DECK-043/044). |
| A7 | Intelligence tab content: plain-language explanation (DECK-045), clarity metrics (DECK-046), provenance sub-section (DECK-047), Refresh Intelligence button (DECK-049). |
| A8 | Your Notes engine (DECK-050..059) — biggest sub-sprint; net-new backend + FE. |
| A9 | Signals tab: deck-linked signals extraction pipeline + Pulse linkage (DECK-060..063). |
| A10 | Related Documents: metadata-similarity retrieval + lineage graph + explicit-attachments (DECK-064..067). |

## 3. §9 dashboard update

`DEV_PIPELINE.md §9`:
- **JC-WS-DECK-A4-FIVE-TAB-OVERLAY**: 🟠 IN FLIGHT · foundation kick shipped 2026-07-02 · build execution pending.

## 4. Proving slice — 10 rows (SCAFFOLDED, NOT executed until build lands)

`/app/backend/scripts/jc_ws_deck_a4_proving_slice.py`:

| Row | Assertion |
| :---: | :--- |
| R1 | `<Tabs>` primitive imported from `@/components/ui/tabs` + mounted in `DocumentOverlay.jsx` body. |
| R2 | 5 tab-triggers rendered with data-testids `document-overlay-tab-{document,intelligence,notes,signals,related}` (positive-count assertion). |
| R3 | Default active tab is `document`; DocumentSurface renders inside the Document `<TabsContent>` shell. |
| R4 | Intelligence tab renders IntelligenceCard inline (previously Layer 2 — re-parented, not duplicated). |
| R5 | Notes / Signals / Related tabs render "Coming soon" placeholder shells with data-testid `document-overlay-tab-content-{notes,signals,related}-placeholder`. |
| R6 | URL param `?tab=intelligence` pre-selects Intelligence tab on overlay open (query-string sync via `useSearchParams` or equivalent). |
| R7 | Toolbar (Layer 1) stays OUTSIDE the Tabs primitive — chrome pattern preservation. |
| R8 | AIRevisionPanel still opens as a sidebar (not migrated into a tab). |
| R9 | Modals (IntelligenceModal / VersionHistoryModal / CommitConfirmationModal) still mount at overlay level (not tab-scoped). |
| R10 | Data-testid preservation — every pre-A4 `document-overlay-*` testid still present in the DOM (regression check via source scan). |

## 5. Acceptance criteria (on build close)

- [ ] Proving slice 10/10 GREEN.
- [ ] `DocumentOverlay.jsx` diff shows only tab-shell reorganization (no behavioural changes to Toolbar / IntelligenceCard / DocumentSurface / AIRevisionPanel / Modals).
- [ ] Test-id preservation confirmed (R10).
- [ ] FE compiles clean; supervisor `frontend` uptime stable ≥60s after final restart.
- [ ] `test_thinklab_uilabel_only.py` invariant GREEN.
- [ ] `test_solva_v1_unchanged.py` GREEN.
- [ ] Path A A1/A2/A3 slices still GREEN (regression check).
- [ ] DEV_PIPELINE.md §9 A4 row flipped to 🟢 SHIPPED with slice count.
- [ ] CHANGELOG entry added at top on build close.

## 6. User decision provenance

- 2026-07-02 · User chained mega-dispatch (P3 → P4 → A4-KICK).
- 2026-07-02 · User confirmed "additive changes in existing shell" + chain-forward authority through A4-KICK.
- 2026-07-02 · Advance scan (`JC_WS_DECK_A4_ADVANCE_SCAN.md`) locks SINGLE A4 dispatch shape; all 5 escalation triggers cleared.

## 7. Chain gate — next dispatch

Report back to Orchestrator using Msg #329 Trigger-2 format on A4 kick shipped + 5 evidence bundles staged. Build execution pending; kick memo + §9 row + proving slice scaffold + advance scan constitute the "A4 IN FLIGHT" state.
