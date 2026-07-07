# RULE-DECK-ID-COLLISION-GUARD

**Banked 2026-07-05 · effective now · applies to ALL Deck feature arcs.**

**Canonical Spec Source (banked-rule origin):** user dispatch 2026-07-05 · `JC-WS-DECK-QA-RECOVERY-STAGE-1` · Part 0.

## Statement

v1.0 catalogue IDs collide numerically with v1.1 catalogue IDs — same IDs, DIFFERENT stories.

**Concrete example given by user (verbatim in dispatch):**
- v1.0 `DECK-084` = "generate a new version"
- v1.1 `DECK-084` = "commit confirmation modal wording"

This is a semantic collision, not a versioning bump. The IDs cannot coexist in the same test catalogue without corrupting results.

## Enforcement

**No test ever executes against v1.0 IDs again.** Test catalogue MUST be regenerated from v1.1 (single xlsx / csv / md with columns: Test ID · v1.1 Story ID · story text · status · comments) BEFORE the user's acceptance re-run.

## Mechanical separation

- Storage convention for regenerated catalogue: `memory/qa/DECK_TEST_CATALOGUE_V1_1.xlsx` (or `.md`, format at user's discretion — presence + v1.1-sourced content is what matters).
- Legacy v1.0 catalogue: freeze under `memory/qa/archive/DECK_TEST_CATALOGUE_V1_0_ARCHIVED_2026_07_05/*` — never edited, never referenced by any live acceptance step.
- Proving slice for any Deck arc MUST include a row asserting "zero v1.0 story IDs referenced in memo / evidence / slice".

## Rule interaction

- **Composes with `CANONICAL_SPEC_UX_BRIEF_V1_1_RULE`:** v1.1 is canonical; v1.0 is RETIRED. This rule mechanically enforces the retirement in test catalogue form.
- **Composes with `USER_QA_RE_RUN_IS_FINAL_GATE_RULE`:** the re-run catalogue used by the user MUST be the REGENERATED v1.1 catalogue.

## Not modifiable

Any change requires explicit new dispatch.
