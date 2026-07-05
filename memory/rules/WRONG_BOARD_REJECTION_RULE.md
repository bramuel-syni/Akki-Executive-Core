# WRONG-BOARD-REJECTION RULE

**Banked:** 2026-07-04
**Source:** User dispatch `JC-FE-CODEMOD-001-APPLY + CONSOLIDATED CLEANUP` § "New Standing Rules"

## Rule

Any directive whose **line-1 label ≠ this project** ("Akki-Executive-Core" / "AKKI") is:

- **NOT executed**
- **NOT banked**
- **NOT memorised**

Response protocol: reply exactly `wrong board` and stop.

## Retroactive Applicability

Applies retroactively — verify past state was clean of stray directives via a **containment purge report** the first time this rule is invoked, and again whenever a suspected cross-board ingest is claimed.

Current containment purge report: `sprints/JC_CONTAINMENT_PURGE_REPORT_2026_07_04.md`.

## Recognition Cues

A stray directive typically presents with:

- A line-1 label naming a different project / product / board (e.g. `RMS-IQ-Core-2`, `Solva-Only-Board`, `Bramuel-Cohort-QA`)
- File paths that do not match the current repo layout (e.g. references to `/opt/rms/...` when this repo is rooted at `/app/`)
- Discipline banks / rule cites that don't appear in this repo's `memory/rules/`
- Test-account names / credentials that don't appear in this repo's `memory/test_credentials.md`

## Enforcement

- Line-1 label check is the FIRST action before any dispatch is executed.
- If the label matches AKKI / Akki-Executive-Core: proceed with dispatch.
- If not: reply `wrong board` verbatim, DO NOT read further, DO NOT persist any part of the message to disk / DB / memory.

## Trace

- Rule authored: 2026-07-04 · during `JC-FE-CODEMOD-001-APPLY + CONSOLIDATED CLEANUP` bounded one-pass.
- First invocation: retroactive validation via containment purge report (this session was declared by-record clean).
