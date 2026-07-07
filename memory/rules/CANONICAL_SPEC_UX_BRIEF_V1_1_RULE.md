# RULE-CANONICAL-SPEC-UX-BRIEF-V1-1

**Banked 2026-07-05 · effective now · applies to ALL Deck feature arcs (past, present, future).**

**Canonical Spec Source (banked-rule origin):** user dispatch 2026-07-05 · `JC-WS-DECK-QA-RECOVERY-STAGE-1` · Part 0.

## Statement

UX Brief v1.1 (7 July 2026) is the **SOLE canonical spec** for the Deck feature. The v1.0 87-story catalogue is RETIRED. No story closes against any other document. Every claim in every report maps to a v1.1 story ID.

## Enforcement

- Every Deck feature arc memo MUST cite the v1.1 brief on Line 1 (Canonical Spec cite).
- Every acceptance line in every Deck-related Trigger-2 close block MUST reference a v1.1 story ID.
- Zero v1.0 story IDs allowed in any Deck arc evidence, memo, slice, or CHANGELOG entry going forward.
- Prior arcs that already closed against v1.0 remain closed (historical record) but any NEW work on v1.1 stories re-enters via a new arc.

## Rule interaction

- **Interacts with `DECK_ID_COLLISION_GUARD_RULE`:** v1.0 IDs collide numerically with v1.1 IDs. This rule (canonical-spec) says which side of the collision wins: **v1.1 always**. The collision guard rule enforces the mechanical separation via a regenerated test catalogue.
- **Interacts with `UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE`:** v1.1 UI stories close on UI-layer evidence; the canonical text of those stories comes from v1.1.
- **Interacts with `USER_QA_RE_RUN_IS_FINAL_GATE_RULE`:** the user's QA re-run must be against the REGENERATED v1.1 catalogue, not v1.0.

## Storage

Canonical brief location convention: `memory/briefs/UX_BRIEF_V1_1_2026_07_07.md` (or wherever user places it — path may drift, presence is what matters).

## Not modifiable

This rule cannot be silently amended. Any change requires an explicit new dispatch that names this rule and either extends or supersedes it.
