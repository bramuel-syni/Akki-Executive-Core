# RULE-USER-QA-RE-RUN-IS-FINAL-GATE

**Banked 2026-07-05 · effective now · applies to ALL Deck feature arcs and any arc with an explicit user-QA-re-run gate.**

**Canonical Spec Source (banked-rule origin):** user dispatch 2026-07-05 · `JC-WS-DECK-QA-RECOVERY-STAGE-1` · Part 0.

## Statement

The arc closes when the **user's QA re-run against the REGENERATED v1.1 catalogue passes** — NOT when slices are green, NOT when the agent declares completion, NOT when UI-layer screenshots merely exist.

Slice-GREEN + UI-layer screenshots are NECESSARY conditions. User QA re-run pass is the SUFFICIENT close.

## Enforcement

- Every Deck-recovery arc's Trigger-2 close block MUST declare status as one of:
  - **SHIPPED-PENDING-USER-QA** (agent work complete; awaiting user's QA re-run pass)
  - **SHIPPED-USER-QA-CONFIRMED** (user has re-run and reported pass rate ≥ target on v1.1 catalogue)
- Agent does NOT self-declare `CLOSED` on Deck arcs. Only the user's QA re-run result triggers the CLOSED state.
- The QA re-run MUST be against the REGENERATED v1.1 catalogue (per `DECK_ID_COLLISION_GUARD_RULE`), not the v1.0 catalogue.

## Enforcement mechanism

- DEV_PIPELINE.md §9 row for any Deck-recovery arc MUST show 🟢 SHIPPED-PENDING-USER-QA until user confirms; then flipped to 🟢 SHIPPED-USER-QA-CONFIRMED with the user's confirmation quote / pass-rate cited.
- Proving slice MUST include a row asserting "user QA re-run against regenerated v1.1 catalogue: PENDING (or CONFIRMED with pass-rate)".

## Rule interaction

- **Composes with `UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE`:** UI-layer evidence enables the user to re-run QA meaningfully; without evidence, re-run is impossible.
- **Composes with `DECK_ID_COLLISION_GUARD_RULE`:** the re-run catalogue MUST be regenerated from v1.1 story IDs.
- **Composes with `CLOSE_IS_NOT_CLOSED_UNTIL_PUSHED_RULE`:** SHIPPED-USER-QA-CONFIRMED still requires push discipline (cite commit hash or SHIPPED-UNPUSHED).

## Not modifiable

Any change requires explicit new dispatch.
