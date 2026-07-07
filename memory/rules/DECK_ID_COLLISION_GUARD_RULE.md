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

---

## Addendum 2026-07-05 · v1.1 Detailed-View extraction basis (applies to Stage 3e only)

**Source:** user amendment relayed 2026-07-05 during `JC-WS-DECK-QA-RECOVERY-STAGE-1` re-fire. Amendment substantiated against `memory/briefs/UX_BRIEF_V1_1_2026_07_07.md`:
- §4.6 "Deck Detailed View" is specified in **prose only** (verified: header, artefact, Akki prompt bar, footer, commit flow, committed-state read-only, delete/archive modals all present in §4.6 body).
- v1.1 story tables enumerate **77 IDs** (verified via grep: `DECK-001..060` + `DECK-082..098`; unique count = 77).
- **DECK-061 through DECK-081** are **ABSENT** from every table (verified: `grep -c "DECK-0[678][0-9]"` returns 0 for all IDs in range).
- Objective 5 (which would logically house the Detailed View stories) is **missing entirely** from the catalogue — jump from Objective 4 (Enhance) to Objective 6 (Commit/share/delete/archive).

### Amendment statement

Catalogue regeneration (Stage 3e) MUST combine:

1. **The 77 tabulated IDs verbatim** (as they appear in v1.1 tables, verbatim story text, verbatim ID)
2. **PLUS a derived block for DECK-061 to DECK-081** extracted sentence-by-sentence from §4.6 prose

### Extraction discipline (mandatory)

- **Extraction only, zero invention.** Every derived story must trace to a specific §4.6 sentence.
- **Sentence anchor citation.** Each derived story cites its §4.6 sentence anchor (line number or verbatim leading phrase — the user can trivially verify the trace).
- **Distinct flag in the catalogue.** The 21-item derived block is separated from the 77-item tabulated block via a clear section header AND a column marker (e.g. `source_type = tabulated | derived-from-§4.6`) so the user can spot it in one pass.
- **User reviews the derived block BEFORE any test executes against it.** Agent does NOT run acceptance tests against DECK-061-081 until user has signed off on the derived block's fidelity to §4.6.

### Acceptance-gate implication

- The QA re-run acceptance gate (per `USER_QA_RE_RUN_IS_FINAL_GATE_RULE`) is **invalid without Detailed View coverage**. The Detailed View is a first-class feature surface — omitting DECK-061-081 from the catalogue would silently under-scope the acceptance gate.

### Scope

- **Applies to Stage 3e only** (catalogue regeneration). Stage 1 (structural fix), Stage 2 (Enhance bug), and Stages 3a-3d are unaffected by this addendum.
- **Amendment is banking-only for now.** No Stage 3e work may begin under this dispatch — it is DEFERRED to a future arc that explicitly invokes Stage 3e. This addendum documents the constraint so any future Stage 3e dispatch inherits the extraction rule automatically.

### Substantiation record (for future audit)

Verified 2026-07-05 by agent:
- `grep -c "^4\.6 Deck Detailed View" /app/memory/briefs/UX_BRIEF_V1_1_2026_07_07.md` = 1 (§4.6 present)
- `grep -oE "DECK-[0-9]{3}" .../UX_BRIEF_V1_1_2026_07_07.md | sort -u | wc -l` = 77 (77 unique tabulated IDs)
- `grep -c "DECK-061"` = 0 (and same for 062, 063, 070, 075, 080, 081 — full range 061-081 absent)
- Objective sections present: 1, 2, 3, 4, 6 (Objective 5 missing — matches Detailed View gap)
