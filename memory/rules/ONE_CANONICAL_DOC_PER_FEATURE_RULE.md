# RULE-ONE-CANONICAL-DOC-PER-FEATURE

**Status:** Permanent · Effective 2026-07-08 · Banked from user dispatch introducing `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1` · Applies to BOTH tracks (Deck feature AND Drafts/Briefs feature) and all future features.

## Rule

Every product feature has EXACTLY ONE canonical specification document. It is named at arc time. No story or claim closes against any other spec document — not a prior version, not a sibling feature's brief, not an inferred draft.

**Prior GREEN does not transfer across spec versions.** A story that closed against v1.0 of a feature's brief does NOT automatically close against v1.1 unless the story explicitly re-verifies against v1.1.

## Canonical map (as of 2026-07-08)

| Feature | Canonical spec | Path |
|---|---|---|
| **Deck** (Work Studio → decks) | UX Brief v1.1 (7 July 2026) | `/app/memory/briefs/UX_BRIEF_V1_1_2026_07_07.md` |
| **Drafts/Briefs** (Work Studio → drafts/briefs feature) | UX Brief v1.0 (8 July 2026) | `/app/memory/briefs/UX_BRIEF_V1_0_2026_07_08.md` (**PENDING user placement**) |

The Drafts/Briefs v1.0 is NOT the retired Deck v1.0. They are different documents for different features. Cross-contamination of story IDs (e.g., using DECK-### IDs in a Drafts/Briefs closure) is a `WRONG_BOARD_REJECTION` violation and requires reclassification.

## When to invoke this rule

- Arc dispatch: cite the canonical spec on line 1 of the sprint memo. Every arc's memo Line-1 canonical rationale MUST reference the exact document path.
- Story closure: every claim maps to a story ID from the SOLE canonical spec for the feature under work. No cross-feature ID re-use.
- Proving slice: R# rows for a UI story arc should include an ID-family check (e.g., "all cited IDs are DB-### format, not DECK-### format"). See Deck arcs' `story-id-namespace-check` pattern.

## Precedence with related rules

- `CANONICAL_SPEC_UX_BRIEF_V1_1_RULE.md` — feature-specific application of this rule to the Deck feature (v1.1 is the sole canonical for Deck arcs).
- `WRONG_BOARD_REJECTION_RULE.md` — cross-feature contamination detection.
- `REPLACEMENT_NAMING_RULE.md` — how to name replacement/successor documents so they don't shadow prior canonical (e.g., a hypothetical v1.1 of Drafts/Briefs would supersede v1.0 exactly as Deck v1.1 superseded Deck v1.0).

## Origin

Banked in the user dispatch of 2026-07-08 introducing `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1`. Explicit reinforcement of the pattern that emerged from the Deck arc's v1.0→v1.1 replacement discipline, extended to a second feature (Drafts/Briefs) to prevent the two features from bleeding into each other's evidence.
