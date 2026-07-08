# RULE-BORN-IN-CORRECT-LIFECYCLE-STATE

**Status:** Permanent · Effective 2026-07-08 · Banked from user dispatch introducing `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1`.

## Rule

Every generation path — every code path that creates a new lifecycled entity (Deck, Draft, Brief, Signal, Solva Frame, or any future entity with a `lifecycle_state` field) — MUST be checked for correct initial `lifecycle_state` at creation.

**Born-in-wrong-lifecycle-state is a known defect class.** It manifests as: an entity is created but shows up in the wrong list, gets the wrong badge, is missing expected actions, or requires a manual state fix by the user to become usable.

## Reference precedents

- **Deck arcs (fixed prior):** A deck used to be born in a state that surfaced it in "Recents" instead of "Active." Fixed in the Deck QA Recovery Stage-N series by asserting the correct initial `lifecycle_state="draft"` (or equivalent) at creation.
- **Drafts/Briefs arcs (Stage 2 of the current arc):** A Brief is currently born in a lifecycle state that inverts the expected surface. To be fixed in Stage 2 of `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-*` per the same discipline.

## When to invoke this rule

- **Creation-path arcs**: any new "create X" endpoint must include a lifecycle-state assertion in its proving slice. Grep the creation writer; verify the initial state matches the spec's expected surface for the entity type.
- **Surface-listing bugs**: if a user reports "I created X but it went to the wrong list," the FIRST hypothesis to test is a wrong initial `lifecycle_state`, not a router/query bug.
- **Provenance-driven fields**: fields like `provenance="user_authored" | "akki_generated"` also fall under this rule — they are lifecycle-adjacent metadata that must be born correctly on creation.

## Proving-slice pattern

```
Rn · Newly-created X is born in correct lifecycle_state
     · Mongo find({...creation-fingerprint...}) → assert row.lifecycle_state == expected
     · Grep the creation writer to verify the literal is spec-aligned (not stale/hardcoded elsewhere)
```

## Precedence with related rules

- `SPLIT_PATH_VIEWER_IDENTITY_CHECK_RULE.md` — for entities that render via split viewer paths (tenant vs external), initial state MUST be correct on BOTH paths.
- `USER_QA_RE_RUN_IS_FINAL_GATE_RULE.md` — a born-in-wrong-state defect passes structural tests but fails UI QA; user QA re-run is the final gate.

## Origin

Banked in the user dispatch of 2026-07-08 introducing `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1`. Explicit acknowledgment of the pattern that emerged repeatedly across Deck arcs where creation-side state assignment drifted from spec-expected surface behaviour.
