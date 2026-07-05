# CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED RULE

**Banked:** 2026-07-04
**Source:** User dispatch `JC-FE-CODEMOD-001-APPLY + CONSOLIDATED CLEANUP` § "New Standing Rules"

## Rule

A close claim is not valid until either:

- **(a)** Pushed state substantiates the close AND the Trigger-2 report cites the **commit hash** verbatim, OR
- **(b)** The report explicitly declares **"shipped-unpushed"** with cause (e.g. "git remote unavailable in this preview pod — commit hash cited for local reconciliation; user to push from their side").

No implicit closes. Report-vs-repo reconciliation is **mandatory** on every close.

## Enforcement

On every `finish` / Trigger-2 close:

1. `git log --oneline -1` to capture the top commit hash covering the arc's changes.
2. Attempt `git push` where a remote is configured.
3. If push succeeds → cite the pushed commit hash in the Trigger-2 close as `SHIPPED · commit=<hash>`.
4. If no remote OR push fails → declare `SHIPPED-UNPUSHED · commit=<hash> · cause=<one-line>` in the Trigger-2 close.
5. Never say "closed" / "shipped" / "green" without one of (3) or (4).

## §9 Discipline Interaction

`DEV_PIPELINE.md §9` row flip discipline:
- 🟡 IN FLIGHT lands BEFORE any code touch.
- 🟢 SHIPPED (with commit hash appended) OR 🟢 SHIPPED-UNPUSHED (with commit hash + cause) at close.

## Trace

- Rule authored: 2026-07-04 · during `JC-FE-CODEMOD-001-APPLY + CONSOLIDATED CLEANUP`.
- First application: this arc's own close will cite commit hash under this rule.
