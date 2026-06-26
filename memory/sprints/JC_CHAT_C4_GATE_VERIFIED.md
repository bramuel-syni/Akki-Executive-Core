# JC-CHAT C.4 — Edit-prompt R5 Gate · VERIFIED

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ C · § R5 lock).

**Closed 2026-06-25 · OPTION_A (keep populate-composer Z3 semantics) — VERIFIED · NO BUILD.**

## R5 lock — applied as the rule it is

The canonical spec's R5 lock states:

> "For the edit-prompt punch-list item: **report the code comment VERBATIM
> + file:line + surrounding logic context**. The user decides intent, not
> the agent. Do not build until intent is decided."

The user's resolution operating that rule:

> "Gate first: report the code comment verbatim with file:line. If
> edit-prompt was a deliberate skip, that intent settles it — don't
> build over a conscious omission."

This memo executes the second clause on the gate evidence already
captured during JC-CHAT Stage C closure.

## Gate read — verbatim (already captured 2026-06-25 in Stage C closure)

Comment at `frontend/src/pages/Chat.jsx:1402-1409` (`onEdit` handler):

```
// Z3 (2026-02) — populate composer with this
// message's text + focus. User can re-send as a
// new turn (no in-place mutation; original turn
// stays in the history).
```

**Surrounding logic** (verbatim from Stage C audit doc
`/app/memory/jc_artifacts/jc_chat/stage_c/c4-r5-edit-prompt-verbatim.json`):

> The `onEdit` prop is wired into the `<Message>` component via the
> rendering loop (Chat.jsx:1399-1419) and surfaces as a "Claude-style
> bubble action" on user-role bubbles (`MessageActions` —
> Chat.jsx:1885-1898). The handler populates `setInput(text || '')` and
> focuses the composer; no in-place mutation, no API call. The original
> user turn stays in the history; the re-edited text is sent as a NEW
> turn when the user submits.

## Hardest-holds compliance audit (verbatim-vs-locks)

| User-locked hold | Z3 semantics behaviour | Status |
|---|---|---|
| Branching is OUT | populate-composer never branches; appends one new turn | ✅ |
| Shield re-run mandatory for every new turn | re-submission goes through the standard turn-create path, which re-routes through Shield + mints a fresh trust receipt | ✅ |
| No in-place mutation of prior turns | comment explicitly states "original turn stays in the history" | ✅ |
| Shield path UNTOUCHED in JC-CHAT | populate-composer is FE-only, zero API call, zero Shield modification | ✅ |

## Verdict

The Z3 (2026-02) decision was **DELIBERATE**, **DOCUMENTED in code**, and
**SATISFIES every hardest-hold the user has named** for this surface.
Per R5 lock + user resolution rule, this **settles intent**; the agent
does not build over a conscious deliberate decision.

- Action: **close C.4 as VERIFIED · OPTION_A.**
- Build path: **none.**
- JC-CHAT Stage C: **now fully CLOSED (4/4 items)** — RENAME +
  RESTORE + PERMANENTLY DELETE (all PRESENT, confirmed by live HTTP
  runs in `jc_chat_stage_c_punchlist_slice.py`) + EDIT PROMPT
  (PRESENT-AS-POPULATE_COMPOSER, VERIFIED by Z3 deliberate decision).

## Files touched

None. Zero code change. Memo + DEV_PIPELINE.md row only.

## Artefacts

- This memo: `/app/memory/sprints/JC_CHAT_C4_GATE_VERIFIED.md`
- Gate evidence (reused, not duplicated):
  `/app/memory/jc_artifacts/jc_chat/stage_c/c4-r5-edit-prompt-verbatim.json`
- Stage C closure memo (4/4 now): `/app/memory/sprints/JC_CHAT_C_PUNCHLIST.md`
