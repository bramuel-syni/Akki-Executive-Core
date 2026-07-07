# RULE-UI-STORIES-CLOSE-ON-UI-LAYER-ONLY

**Banked 2026-07-05 · effective now · applies to ALL Deck feature arcs (and by extension, any UI feature where the user QA'd via UI journey).**

**Canonical Spec Source (banked-rule origin):** user dispatch 2026-07-05 · `JC-WS-DECK-QA-RECOVERY-STAGE-1` · Part 0.

## Statement

UI stories close on **UI-layer evidence only**. Bash/curl/static Python slices prove backends and serve as regression floors underneath — they **CANNOT close** a UI story.

Per journey: screenshots (or recording) of the actual flow on the **live preview**, each specified step visible.

## Enforcement

- A UI story is considered CLOSED only when at least one screenshot (or recording frame) demonstrates the specified step visible on the live preview URL (frontend `REACT_APP_BACKEND_URL` from `.env`).
- The proving slice (`backend/scripts/jc_*_proving_slice.py`) is a **regression floor**, not a close condition. Slice-GREEN alone does not close UI stories.
- Screenshots taken against static / staging / mocked-DOM environments do NOT close. Live-preview only.
- No fabricated / composite / edited screenshots. If capture isn't possible in this pod, emit `WAIT-FOR-USER-CAPTURE` and let the user capture during their QA re-run.
- Truth-in-Capability: if screenshot capture isn't available, say so up-front; do NOT invent screenshots.

## Enforcement mechanism

- Every Deck (or applicable UI) arc's proving slice MUST have a row asserting "UI-layer evidence artefact present at `memory/evidence/<arc>/screenshot_N.png` (or explicit `WAIT-FOR-USER-CAPTURE` block declared)".
- Trigger-2 close blocks MUST inline (or link with checksum) the UI-layer screenshots per journey step.

## Rule interaction

- **Interacts with `USER_QA_RE_RUN_IS_FINAL_GATE_RULE`:** UI-layer evidence is a NECESSARY condition for user QA re-run to succeed; the user's re-run pass is the SUFFICIENT close.
- **Interacts with `CANONICAL_SPEC_UX_BRIEF_V1_1_RULE`:** the UI evidence must demonstrate the v1.1 spec's specified end-state, not v1.0.

## Not modifiable

Any change requires explicit new dispatch that names this rule.

---

## Corollary · 2026-07-05 · State-injection captures do not close UI stories

**Banked 2026-07-05 · effective permanent · applies to ALL UI story closes.**

**Canonical Spec Source:** user dispatch 2026-07-05 · `JC-GEN-PATH-CONNECTTIMEOUT` · Corollary block.

### Statement

State-injection captures (Playwright `page.evaluate` state-set, forced React state, mocked backend responses, `data-testid`-scoped state manipulation, or any UI-state manipulation that bypasses the actual user-triggered flow) **MAY SUPPLEMENT** evidence but **NEVER CLOSE** a UI story. Only **organic user-flow captures** — where the UI state is arrived at via the actual user journey — close.

### Enforcement

- Every UI-layer screenshot used as a close artefact MUST be traceable to a user-triggered flow. The Playwright script (or manual capture instructions) MUST show the actual clicks / typing / navigation that arrive at the state, NOT a `page.evaluate("setPhase('complete')")` or equivalent.
- Backend mock responses (intercepting `fetch` / `XMLHttpRequest` to return canned data) do NOT satisfy organic capture. If the real backend endpoint fails in the capture environment, either (a) fix the environment so the real endpoint succeeds, or (b) declare the story BLOCKED-BY-ENV and defer the close — do NOT manufacture the state.
- Code-inspection evidence (grep + line references confirming a data-testid exists, or that the render branch exists) is REGRESSION FLOOR only. It does not close a UI story on its own.
- If the state-injection was used only during development for iteration (e.g. faster loop), that's fine — but the FINAL close artefact MUST be organic.

### Interaction

- **Extends `UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE`** (the parent rule above) — this corollary tightens the "UI-layer evidence" definition to exclude manufactured / injected states.
- **Composes with `USER_QA_RE_RUN_IS_FINAL_GATE_RULE`** — user's QA re-run naturally arrives at UI states organically; the agent's evidence must meet the same bar so the user's re-run is meaningful.

### Not modifiable

Any change requires explicit new dispatch that names this corollary.
