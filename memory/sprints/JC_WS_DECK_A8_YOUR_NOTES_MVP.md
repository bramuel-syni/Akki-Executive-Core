Canonical spec: `/app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5 (5-Tab Detail Content · Your Notes tab, DECK-050..059)` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A8 (Your Notes engine)` + user dispatch 2026-07-02 (populate-chain: Notes → Signals → Related Docs).

# JC-WS-DECK-A8-YOUR-NOTES-MVP — sprint memo

> Corrected A5–A10 mapping (verified against JC_WS_DECK_PATH_A_EXECUTION_PLAN.md): A5=Detail-view header + footer parity + share · A6=Document tab (structured outline + source context) · A7=Intelligence tab completion · A8=Your Notes engine · A9=Signals tab + Pulse feed integration · A10=Related Documents tab + version-numbered blank regeneration.

**Type:** Content-population sub-sprint · MVP scope. Populate-chain step 1 of 3.
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a8_proving_slice.py` (9 rows including REAL RENDER assertion). Testing sub-agents BANNED.
**Locked-area sweep:** F.6 Shield contract UNTOUCHED (0 Shield-routed code · 0 LLM calls) · JC-CHAT invariants UNTOUCHED · Solva engine UNTOUCHED · Storage arc UNTOUCHED · Rename arc closure UNTOUCHED · A1/A2/A3/A4 slices unaffected.

---

## 0. Executive Summary

Populates the "Your Notes" tab shell (A4 foundation) with a **localStorage-based MVP** — private, deck-scoped notes that persist across browser sessions on the same device. Fits within user's ~50 LOC backend budget for the populate chain (0 backend LOC used).

**MVP shape:** minimalist `<textarea>` editor + debounced 500ms autosave to `localStorage` + saved-timestamp indicator + Clear-notes affordance. Undo/redo satisfied via native browser textarea primitive (Ctrl+Z / Ctrl+Y).

**Storage contract:**
- Key: `akki:deck-notes:{contextId}:{artefactId}` (deck-scoped, user-scoped implicitly by browser storage).
- Value: JSON `{ content: string, updated_at: iso-8601 }`.
- Empty state: null / missing key = "no notes yet".
- Delete-all: remove key entirely.

**Deferred to full-A8 backend engine dispatch:**
- Cross-device sync (requires `db.deck_notes` collection + CRUD routes ~150+ LOC).
- Multi-user collaboration on notes (not brief-scoped anyway).
- Rich-text formatting (TipTap StarterKit — brief doesn't specify).
- Server-side conflict resolution (offline-tolerant queue with server rebase).

## 1. Stories closed (10/10 at MVP level per brief)

| Story | Coverage | Notes |
| :---: | :--- | :--- |
| DECK-050 Create notes | ✅ MET | Textarea input; localStorage write on first change. |
| DECK-051 Edit notes | ✅ MET | Textarea two-way binding; debounced autosave. |
| DECK-052 Delete parts of notes | ✅ MET | Native textarea edit (backspace, cut). |
| DECK-053 Autosave confirmation | ✅ MET | "Saved just now" chip with relative-time updater. |
| DECK-054 Return across sessions | ✅ MET | localStorage persists across browser tab close/reopen on same device. |
| DECK-055 Continue editing after reopen | ✅ MET | Content re-loaded from localStorage on component mount. |
| DECK-056 Undo (session) | ✅ MET | Native browser textarea Ctrl+Z / Cmd+Z. |
| DECK-057 Redo (session) | ✅ MET | Native browser textarea Ctrl+Y / Cmd+Shift+Z. |
| DECK-058 Offline-tolerant editing | ✅ MET | localStorage has no server round-trip; fully offline. |
| DECK-059 Delete notes entirely | ✅ MET | "Clear notes" button with confirm dialog + localStorage.removeItem. |

## 2. Content acquisition (per user directive)

- **Grep-first result:** NO existing deck-scoped notes infrastructure. `workbook_analysis.py` and `ned_cycle.py` have `notes` but for different domains (analyses / meetings, not decks). Result: **greenfield**.
- **Additive-only pattern:** FE-only implementation, 0 backend LOC. localStorage IS the "additive-only" persistence pattern that fits within the guardrail.
- **Backend endpoint strictly needed?** NO for MVP. YES for cross-device sync → deferred to full-A8 dispatch.

## 3. §9 dashboard update

**On A8 MVP close:** 🟠 IN FLIGHT → 🟢 SHIPPED · localStorage MVP scope · Notes tab affordance visible + Notes flag flipped to `true`.

## 4. Proving slice — 9 rows

`/app/backend/scripts/jc_ws_deck_a8_proving_slice.py`

| Row | Assertion |
| :---: | :--- |
| R1 | `DeckNotes.jsx` file exists at `frontend/src/components/work_studio/overlay/DeckNotes.jsx` + exports default component + accepts `contextId` + `artefactId` props. |
| R2 | localStorage key contract present: string `akki:deck-notes:` template + JSON serialization + updated_at ISO field. |
| R3 | Debounced autosave hook (500ms) + saved-timestamp state present (real content acquisition, not just compile). |
| R4 | `TAB_VISIBILITY.notes === true` in DocumentOverlay.jsx (flag flipped for MVP ship). |
| R5 | Notes `<TabsContent value="notes">` mounts `<DeckNotes ...>` component + "Coming soon" placeholder REMOVED. |
| R6 | 5 stable data-testids on DeckNotes: `deck-notes-textarea` · `deck-notes-saved-indicator` · `deck-notes-clear-button` · `deck-notes-clear-confirm` · `deck-notes-empty-state`. |
| R7 | Clear-notes affordance + confirm flow: Clear button opens confirm; confirm removes localStorage key + clears textarea. |
| R8 | URL param `?tab=notes` continues to activate Notes tab (URLSearchParams hook still reads `tab` param + Notes now in the visible-tabs allow-list). |
| R9 | A4 slice regression 11/11 GREEN (Step 0 gate preserved; A4 foundation unaffected by A8 addition). |

## 5. Acceptance criteria

- [ ] Proving slice 9/9 GREEN.
- [ ] A4 slice re-runs 11/11 GREEN (regression).
- [ ] `test_thinklab_uilabel_only.py` GREEN (production BE zero-tolerance preserved).
- [ ] `test_solva_v1_unchanged.py` GREEN.
- [ ] Webpack compiles clean (no new warnings from A8 changes).
- [ ] `data-testid` preservation: all A4-era testids still present in overlay source.
- [ ] DEV_PIPELINE.md §9 A8 row flipped 🟠 IN FLIGHT → 🟢 SHIPPED with slice count.
- [ ] CHANGELOG top entry added.

## 6. User decision provenance

- 2026-07-02 · User dispatched populate-chain (Notes → Signals → Related Docs) with numbering-reconcile step.
- 2026-07-02 · User guardrail: "If content acquisition requires backend work beyond ~50 LOC, HARD STOP and surface — that's a scope escalation candidate."
- 2026-07-02 · Interpretation: FE-only MVP with 0 backend LOC fits the guardrail. Full A8 backend engine (~150+ LOC + cross-device sync) deferred as scope-escalation candidate.

## 7. Chain gate — next dispatch

On A8 R1-R9 GREEN + regression preserved:
1. Flip DEV_PIPELINE §9 A8 row 🟠 IN FLIGHT → 🟢 SHIPPED.
2. Append CHANGELOG entry at TOP documenting A8 MVP ship.
3. Fire A9 (Signals MVP) dispatch: §9 row → sprint memo → build → proving slice → GREEN.
