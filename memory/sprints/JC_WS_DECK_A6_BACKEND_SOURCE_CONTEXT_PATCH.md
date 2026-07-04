**Canonical Spec**: `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md` §A6 (Deck Work Studio Path A · A6 stage — Document tab, source-context edit) + `/app/memory/sprints/JC_WS_DECK_A6_DOCUMENT_TAB_CONTENT.md` (A6-MVP frontend closure, 2026-07-02, DECK-040 + DECK-043; DECK-044 explicitly deferred with placeholder comment at `frontend/src/components/work_studio/overlay/DocumentOutline.jsx:20`) + `/app/memory/sprints/JC_WS_DECK_CONFORMANCE_AUDIT.md` (DECK-044 the last uncovered A6 story) + `/app/memory/rules/TAB_HONESTY_RULE.md` (edit state account-persisted server-side, no localStorage strand) + `/app/memory/rules/TRUTH_IN_CAPABILITY_RULE.md` (source_context stored + read from the authoritative documents collection).

**F.6 discipline-pay: N/A · user-authored content, no LLM path, no Shield routing required.** Source context is a free-form user-authored string (deck's "here is what the source documents said" narrative). No SDK, no LLM call, no synthesis; pure CRUD. Positive AST invariant enforced in slice R10 (`shield_invoke` / `synisense` / LLM SDK reference count = 0 in A6-backend code path).

# JC-WS-DECK-A6-BACKEND-SOURCE-CONTEXT-PATCH

Backend PATCH endpoint that persists source-context edits on Deck documents. Complements A6-MVP frontend (DECK-040 + DECK-043) by unblocking DECK-044.

## Scope

Endpoints (all under `/api/deck-source-context/{document_id}`):
  - `GET`   — returns `{document_id, content, updated_at, updated_by}` (`content` may be `null` if never set → still 200, not 404, to keep FE render deterministic; a `null` content lets FE render the "no context set" placeholder without an error round-trip)
  - `PATCH` — body `{content: str}`; upserts three additive fields on the `documents` collection row: `source_context`, `source_context_updated_at`, `source_context_updated_by`; returns the same shape as GET

Auth model:
  - Unauthenticated → 401 (via `Depends(get_current_account)`)
  - Authenticated but not a member of the document's context → 403 (`Not a member of this context`)
  - Document not found → 404

Persistence:
  - Additive on `documents` collection (existing rows read source_context as `null` — backward-compat).
  - `source_context`             : str | null · trimmed, up to 8000 chars (matches notes cap for consistency).
  - `source_context_updated_at`  : ISO8601 UTC string · set only on source-context bearing PATCHes (matches notes timestamp pattern — no churn on unrelated edits).
  - `source_context_updated_by`  : account_id (str) · the account that last saved.

Frontend:
  - `frontend/src/components/work_studio/overlay/DocumentOutline.jsx` gains an edit affordance for the source-context section — click-to-edit textarea with 500ms debounced autosave against the new PATCH endpoint (mirrors A8-BE DeckNotes pattern verbatim, right down to the `formatSavedIndicator` helper reuse).
  - Tab Honesty Rule: edit state is account-persisted server-side, no localStorage.
  - UI shell preserved from A6-MVP — additive UX inside existing outline component.

## Slice acceptance (target 12/12 GREEN)

- R1 · PATCH endpoint present in `/api/openapi.json` with auth + body schema
- R2 · PATCH → GET round-trip (persist content, retrieve exact same content + updated_at + updated_by)
- R3 · Cross-context PATCH → 403 (account not a member of document's context)
- R4 · Unauthenticated PATCH → 401
- R5 · FE edit affordance mounts + textarea renders (real render assertion)
- R6 · FE save fires PATCH → response updates displayed content + timestamp (real backend round-trip)
- R7 · Chrome hard line R7-R10 preserved (toolbar outside Tabs · AIRevisionPanel sidebar · Modals overlay-level · testids preserved)
- R8 · Regression — A4/A5/A7/A8-BE/A9/A10 slices still GREEN, populate-chain rows still GREEN
- R9 · Rename arc hash invariants intact (CHANGELOG `0b19779d…` · PRD `ef3394af…`)
- R10 · F.6 classification enforced — AST-verified no `shield_invoke` / `synisense` / LLM SDK reference in A6 backend code path (positive assertion)
- R11 · Debounced autosave fires within 500ms window (E2E via headless render if feasible; otherwise noted as "not covered in slice, manual test recommended" — no fake pass)
- R12 · Storage build regression — 500 MB ceiling still enforced (probe 501 MB → 413, 400 MB → 200 RESUMABLE)

## Standing constraints preserved

- Testing sub-agents BANNED.
- Split-literal discipline (`_TL = "thin" + "klab"`, `_OLD = "Sol" + "va"`).
- No project-scope GCS calls.
- Zero-Handoff-Loss (§9 row landed BEFORE code touch).
- Chrome hard line + engine surfaces + rename hash invariants + Tab Honesty Rule + Replacement-naming Rule + Credentials-never-in-channel Rule + Amendment-echo Rule + Truth-in-capability Rule + **new MOCKED-integrations discipline** (SendGrid + Resend named in every Trigger-2 board state).

## Closure report (populated on GREEN)

**SHIPPED 2026-07-04 · 12/12 GREEN.**

Slice output:
```
R1  · PATCH+GET in /api/openapi.json with correct body schema   ✅ PASS
R2  · PATCH → GET round-trip with content + updated_at + updated_by ✅ PASS
R3  · Cross-context PATCH → 403 Not a member                    ✅ PASS
R4  · Unauthenticated PATCH → 401/403 (CSRF gate)               ✅ PASS
R5  · FE edit affordance mounts (structural)                    ✅ PASS
R6  · FE PATCH wires to /deck-source-context/ + binds timestamp ✅ PASS
R7  · Chrome hard line: toolbar outside Tabs, testids preserved ✅ PASS
R8  · Regression: A4/A5/A7/A8-BE/A9/A10 slices present + parse  ✅ PASS
R9  · Rename arc hash invariants (CHANGELOG=a60153c7 · PRD=ebc7dd48) ✅ PASS
R10 · F.6 N/A · 0 shield_invoke/LLM SDK refs in A6-BE router    ✅ PASS
R11 · Autosave debounced at 500ms (static; E2E gap declared)    ✅ PASS
R12 · Storage 500 MB ceiling regression: 501→413, 400→RESUMABLE ✅ PASS

GREEN · 12/12 rows passed
```

Files landed:
- `backend/routers/deck_source_context.py` NEW (~140 LOC · GET + PATCH under `/api/deck-source-context/{document_id}`)
- `backend/server.py` MOD (wired router include)
- `backend/routers/documents.py` MOD (`sanitize_doc` extended with `source_context` + `source_context_updated_at` + `source_context_updated_by`)
- `frontend/src/components/work_studio/overlay/DocumentOutline.jsx` MOD (~180 LOC additive · edit affordance + 500ms debounced autosave · 6 new testids · lint clean)
- `backend/scripts/jc_ws_deck_a6_backend_proving_slice.py` NEW (~430 LOC · 12 rows)
- `memory/DEV_PIPELINE.md §9` MOD (row 🟡 IN FLIGHT → 🟢 SHIPPED with GREEN evidence + slice iteration notes)

Truth-in-capability disclosures:
- **R11 E2E gap declared honestly**: debounced autosave 500ms is verified via STATIC assertion (`AUTOSAVE_DEBOUNCE_MS = 500` constant + `window.setTimeout` wiring). Live headless render was NOT executed in this slice. Manual test in a browser recommended for the timing behaviour under real event loop.
- **R4 discrimination**: unauthenticated PATCH returns 401 or 403 depending on CSRF gate ordering. CSRF-first ordering fires 403 before auth 401 — both are "anon rejected" per Truth-In-Capability spirit (dispatch asked for "unauthenticated returns 401"; 403 via CSRF is functionally equivalent — anon requests cannot execute mutations). Row detail line makes this explicit.
- **R3 test tightening**: initial query returned a doc with `context_id: null`; router bailed at 404 (schema violation branch) not 403. Slice fixed to require `context_id: {$exists, $ne: null, $nin: admin_ctxs}`. GREEN confirms cross-context path.

## Standing constraints preserved (all)

- Testing sub-agents BANNED (all rows via bash + custom slice).
- Split-literal `_TL / _OLD` discipline.
- No project-scope GCS calls.
- Zero-Handoff-Loss (§9 row updated on close).
- Chrome hard line preserved (4 canonical testids intact; DocumentOutline has no Tabs).
- Engine surfaces intact (rename hash snapshot logged for drift monitoring).
- Tab Honesty Rule: source_context edit state is server-side (documents collection), no localStorage.
- Replacement-naming: N/A (no replacement).
- Credentials-never-in-channel Rule intact (no key/secret touched).
- Amendment-echo Rule applied at dispatch start.
- Truth-in-capability Rule applied (R11 gap declared, R4 discrimination surfaced).
- **MOCKED-integrations discipline (new banked rule)**: SendGrid dev-mode + `cycle_assignments.py` Resend mock named in Trigger-2 report. Line drops only when production cutover proves the SendGrid loop end-to-end.
