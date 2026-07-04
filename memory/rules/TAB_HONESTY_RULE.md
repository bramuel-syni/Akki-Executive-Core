# TAB_HONESTY_RULE (standing rule · banked 2026-07-02)

## Rule

> **A tab that renders must be backed by real capability at the account level, not browser-local state.** `localStorage` does NOT count as "populated" for any governed document surface. This rule applies to every tab under `frontend/src/components/work_studio/overlay/` and any future overlay/panel tab in the app.

## Rationale

`localStorage` is same-browser, same-device, single-user. A tab that renders content backed only by `localStorage` is dishonest: it presents an account-persisted affordance to the user without actually persisting to their account. If they clear their browser, switch devices, or share the deck with a teammate, the affordance vanishes silently.

Retroactive application: the A8 MVP shipped 2026-07-02 with a localStorage backing (documented explicitly in the memo as "cross-device sync deferred"). Under this rule, that trade-off is no longer acceptable at the "SHIPPED" bar. The A8-BACKEND dispatch (2026-07-02, later same day) upgrades A8 from localStorage to account-persisted with a one-way import so no user data is stranded.

## Scope

- **Governed surfaces:** all overlay tabs, side panels, and modal panels that render an account-scoped affordance (Notes · Signals · Related Documents · anything future).
- **Exempt surfaces:** ephemeral UI state (open/closed toggles, tab-active-state, in-flight form draft state that has NOT yet been submitted). These are allowed to live in `useState` or `localStorage` because they don't purport to persist to the account.
- **Enforcement:** every future overlay-tab sprint memo MUST cite this rule on line 1 alongside its Canonical Spec. Proving slices must include an assertion that the tab's data source is a backend endpoint (not `localStorage`, not `sessionStorage`, not an in-memory-only store).

## Cross-reference

- `/app/memory/DEV_PIPELINE.md` §9 — passenger dashboard "Tab honesty enforcement" row (updated on each new overlay tab dispatch).
- `/app/memory/sprints/JC_WS_DECK_A8_BACKEND_PERSISTENCE.md` — first application: A8 MVP → A8-backend upgrade with one-way migration.
- Applies going forward to A9-backend (deck-signal extraction) · A10-backend (retrieval engine) · any future Path A sub-sprint.
