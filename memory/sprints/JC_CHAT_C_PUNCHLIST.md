# JC-CHAT Stage C — Punch-list verify-then-close

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ C).

**Closed 2026-06-25 · 6/6 acceptance rows GREEN** via
`python backend/scripts/jc_chat_stage_c_punchlist_slice.py`.

## Classification by execution

All four punch-list items inspected against live BE + FE code:

| # | Item | Status | BE | FE |
|---|---|---|---|---|
| C.1 | RENAME conversation | **CLOSED — present** | `PATCH /chats/{cid}` body.title (routers/chat.py:1202-1204) | inline title edit `onPatch({ title })` (Chat.jsx:1506) |
| C.2 | RESTORE archived | **CLOSED — present** | `POST /chats/{cid}/restore` (routers/chat.py:1364) | `onRestoreChat` (Chat.jsx:1029) + button (Chat.jsx:1165) |
| C.3 | PERMANENTLY DELETE archived | **CLOSED — present** | `DELETE /chats/{cid}?hard=true` (routers/chat.py:1282-1321, 400 precondition if not archived) | `onHardDeleteChat` (Chat.jsx:1045) + button (Chat.jsx:1173) |
| C.4 | EDIT submitted prompt — **R5 lock** | **PRESENT_AS_POPULATE_COMPOSER** | n/a | Chat.jsx:1402-1409 (`onEdit` populates composer, focuses input — Z3 pattern, no in-place mutation). Verbatim code comment captured in audit doc. |

## Acceptance rows (verbatim)

```
✅ A. RENAME persists — patched='jc-chat-stage-c renamed ff498a' refreshed='jc-chat-stage-c renamed ff498a'
✅ B. RESTORE round-trip — archived_status=archived restored_status=active
✅ C. PERMANENT DELETE — purge_status=200 gone=True
✅ D. PERMANENT DELETE PRECONDITION — early_purge_status=400 (expected 400)
✅ E. R5 verbatim captured — status=PRESENT_AS_POPULATE_COMPOSER
✅ F. audit chain preservation — verified statically via routers/chat.py audit_payload writes

6/6 acceptance rows GREEN — STAGE C STOP-AND-SHOW ready.
```

## R5 verbatim report — `c4-r5-edit-prompt-verbatim.json`

The R5 lock requires showing the existing code comment verbatim +
file:line + intent-decision surface (user decides, not the agent).
Done. The Z3 interpretation (2026-02) of edit-prompt is
**populate-composer** semantics — Claude-style; not in-place
mutation. Three decision options surfaced for the user:

- **OPTION_A_KEEP_POPULATE_COMPOSER** — agent recommendation; no
  build needed. Z3 semantics coherent with rest of surface.
- **OPTION_B_IN_PLACE_REVISION** — in-place edit of prior turn;
  build-scoped phase beyond Stage C.
- **OPTION_C_BRANCHING_REVISION** — ChatGPT-style branches;
  substantially larger build, data-model shift.

Per R5 lock: agent does NOT build until user decides between B and C
(or accepts A's no-action close).

## Discipline

- **Shield path** ✅ UNTOUCHED throughout.
- **Verify-then-close pattern** ✅ — classified each item by
  execution before claiming closure.
- **R5 lock** ✅ — verbatim report only; no build.

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/scripts/jc_chat_stage_c_punchlist_slice.py` | NEW · verify-then-close BE-level HTTP slice + R5 verbatim report | +370 |

Zero changes to existing code (the four punch-list items were already wired).

## Artefacts

- `/app/memory/jc_artifacts/jc_chat/stage_c/c1-rename.json`
- `/app/memory/jc_artifacts/jc_chat/stage_c/c2-restore.json`
- `/app/memory/jc_artifacts/jc_chat/stage_c/c3-hard-delete.json`
- `/app/memory/jc_artifacts/jc_chat/stage_c/c3-hard-delete-precondition.json`
- `/app/memory/jc_artifacts/jc_chat/stage_c/c4-r5-edit-prompt-verbatim.json`
