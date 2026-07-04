Canonical spec: `/app/memory/rules/TAB_HONESTY_RULE.md` + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A8 (Your Notes engine)` + user dispatch 2026-07-02 (autonomous chain: A8-BACKEND → A5 → A6 → A7).

# JC-WS-DECK-A8-BACKEND-PERSISTENCE — sprint memo

> **TAB HONESTY RULE applies** — `/app/memory/rules/TAB_HONESTY_RULE.md`. A tab that renders must be backed by real capability at the account level, not browser-local state. This dispatch retroactively upgrades A8 MVP from localStorage to account-persisted with a one-way import.

> Corrected A5–A10 mapping (verified against JC_WS_DECK_PATH_A_EXECUTION_PLAN.md): A5=Detail-view header + footer parity + share · A6=Document tab (structured outline + source context) · A7=Intelligence tab completion · A8=Your Notes engine · A9=Signals tab + Pulse feed integration · A10=Related Documents tab + version-numbered blank regeneration.

**Type:** Backend build + FE upgrade · Path A A8 engine sub-sprint. Autonomous chain phase 1 of 4.
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a8_backend_proving_slice.py` (11 rows including REAL RENDER + account-isolation + one-way import + OpenAPI validation). Testing sub-agents BANNED.
**Locked-area sweep:** F.6 Shield contract UNTOUCHED (0 Shield-routed code · 0 LLM calls; deck notes are user-authored, never touch Shield) · JC-CHAT invariants UNTOUCHED · Solva engine UNTOUCHED · Storage arc UNTOUCHED · Rename arc closure UNTOUCHED · A1/A2/A3/A4/A9/A10 slices unaffected · A8-MVP UI structure preserved (only data source swapped).

**F.6 discipline-pay: N/A · user-authored content, no LLM path.**

---

## 0. Executive Summary

Upgrades A8 Your Notes from localStorage MVP to full account-persisted CRUD. Motivated by the **Tab Honesty Rule** banked 2026-07-02: a governed tab must be backed by account-level capability, not browser-local state.

**Backend build:**
- New `db.deck_notes` collection with `_id` = str(uuid), `account_id`, `document_id`, `content`, `created_at`, `updated_at`. Unique compound index on `(account_id, document_id)`.
- New router `backend/routers/deck_notes.py` with 3 endpoints: `GET`, `PUT` (upsert), `DELETE`. All filter by authenticated `account_id`. Unauthenticated → 401. Cross-account queries return 404 (implicit isolation via `account_id` scoping — Account B's `GET` for Account A's doc_id simply misses the compound index).
- Router registered in `server.py` alongside existing include_router calls.
- Index created in server startup `_on_startup` hook.

**FE build:**
- Modify `DeckNotes.jsx` — replace localStorage read/write/remove with `api.get / api.put / api.delete` calls via existing axios instance (`@/lib/api/apiV2`).
- Preserve 500ms debounce · saved-timestamp indicator (now server-authoritative) · Clear-notes confirm dialog · native browser undo/redo · empty-state affordance.
- **UI STRUCTURE UNCHANGED** — every A8-MVP data-testid preserved.

**One-way import from localStorage on first load:**
- On mount, if `GET /api/deck-notes/{document_id}` returns 404 AND `localStorage[akki:deck-notes:{contextId}:{artefactId}]` has content → `PUT` to backend → on success, `localStorage.removeItem`.
- If backend returns 200 → IGNORE localStorage entirely (never re-import).
- On import PUT failure → keep localStorage, retry next mount.
- Telemetry hook: `console.log("deck_notes.localstorage_migration.completed", {...})` — swap for real telemetry when Pulse feed available.

## 1. Files touched

**New (2):**
- `backend/routers/deck_notes.py` (~85 LOC · router with 3 endpoints)
- `backend/scripts/jc_ws_deck_a8_backend_proving_slice.py` (~250 LOC · 11 rows)

**Modified (3):**
- `backend/server.py` — add `include_router` for deck_notes + `create_index` for (account_id, document_id) in startup hook (~5 LOC additive)
- `frontend/src/components/work_studio/overlay/DeckNotes.jsx` — swap localStorage → api calls + add one-way import hook (~60 LOC net delta; UI structure preserved)
- `memory/DEV_PIPELINE.md` — §9 A8-BACKEND row

**Total: ~150 LOC net additive; well within user's 200 LOC guardrail.**

## 2. Proving slice — 11 rows

`/app/backend/scripts/jc_ws_deck_a8_backend_proving_slice.py`

| Row | Assertion |
| :---: | :--- |
| R1 | `GET /api/deck-notes/{new-doc-id}` returns 404 for fresh document with authenticated account. |
| R2 | `PUT /api/deck-notes/{doc-id}` with content persists → 200 + record. |
| R3 | `GET` after PUT returns content + `updated_at` ISO. |
| R4 | Account isolation — Account A's notes invisible to Account B (Account B's GET for A's doc_id → 404). |
| R5 | `DELETE /api/deck-notes/{doc-id}` removes; subsequent GET → 404. |
| R6 | 500ms debounce still fires against backend PUT (FE source assertion: debounce hook contains `api.put` call). |
| R7 | One-way import — FE source contains `if GET returns 404 AND localStorage has content THEN PUT` migration logic + `localStorage.removeItem` post-success + no-re-import guard. |
| R8 | Unauthenticated PUT/GET/DELETE returns 401 (existing `Depends(get_current_account)` throws). |
| R9 | REAL RENDER — FE source binds `content` state to backend response + `savedIndicator` binds to server `updated_at`. |
| R10 | Populate-chain regression — A4 (11/11) + A9 (8/8) + A10 (8/8) all still GREEN. |
| R11 | OpenAPI spec at `/api/openapi.json` includes all 3 new routes (`GET /deck-notes/{document_id}` + `PUT /deck-notes/{document_id}` + `DELETE /deck-notes/{document_id}`). |

## 3. Acceptance criteria

- [ ] Proving slice 11/11 GREEN.
- [ ] A4 + A9 + A10 regressions GREEN.
- [ ] `test_thinklab_uilabel_only.py` GREEN.
- [ ] `test_solva_v1_unchanged.py` GREEN.
- [ ] P4 rename-arc hash invariant GREEN.
- [ ] Webpack compiles clean.
- [ ] DEV_PIPELINE.md §9 A8-BACKEND row flipped 🟠 IN FLIGHT → 🟢 SHIPPED.

## 4. User decision provenance

- 2026-07-02 · User dispatched autonomous 4-phase chain (A8-BACKEND → A5 → A6 → A7).
- 2026-07-02 · User banked TAB HONESTY RULE — retroactively applied to A8.
- 2026-07-02 · User scope-guardrail: ~200 LOC backend budget per phase.

## 5. Chain gate — next dispatch

On A8-BACKEND R1-R11 GREEN + all regressions preserved: auto-fire A5 (Detail-view header + footer parity + share).
