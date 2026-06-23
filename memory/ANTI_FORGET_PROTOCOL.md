# Anti-Forget Protocol — Syni / Akki

**Purpose:** maintain operating discipline across agent restarts, context compactions, and session breaks. This file is the durable contract between orchestrator and builder. Read this on every resume.

**Status:** Standing instructions. Override only via explicit user directive.

---

## 1 · Read-on-resume order (every session, every restart)

1. `/app/memory/MASTER_STATE.md` — Section 6 (latest phase status) + Section 8 (re-architecture backlog).
2. The most recent sprint memo for any in-flight phase: `/app/memory/sprints/PHASE_*.md`.
3. Any Pre-Read attached to the in-flight phase (also under `/app/memory/sprints/`).
4. The last ~5 messages of conversation context.

Do not ask the user to re-supply already-decided items. If a decision was recorded in MASTER_STATE.md or a sprint memo, it stands.

## 2 · Discipline Rails (R1–R7)

- **R1 · Pre-Read protocol** — any phase with exploratory surface gets a read-only investigation first, written to `/app/memory/sprints/`, surfaced for approval before code dispatch.
- **R2 · Approval Gate** — no code dispatch without explicit user sign-off. "Implement this" / "go ahead" / "yes" on a written plan counts as sign-off. Ambiguous requests trigger a Pre-Read first.
- **R3 · One phase in flight** — never dispatch a new broad phase while another is in-flight. Targeted follow-ups inside the same phase are allowed.
- **R4 · One backlog** — Section 8 of MASTER_STATE.md is canonical. No parallel plans permitted. Retire superseded plans explicitly.
- **R5 · Honesty Protocol** — every exception path logs with `exc_info=True`. Failures surface to the frontend with typed flags (e.g. `confidence_recompute_failed`), never silently swallowed. No claiming success on a red harness.
- **R6 · No auto-starting declined / parked items** — items marked DECLINED or GATED stay so until explicitly unblocked.
- **R7 · Status drift prevention** — exact status terms only: `IN PROGRESS`, `Pending`, `GATED`, `DONE`, `DECLINED`, `BLOCKED`. No paraphrasing.

## 3 · Testing discipline

- **Real-LLM tests carry `@pytest.mark.integration`.** No mocking of `shield_invoke` for feature validation.
- **Characterisation goldens** (Phase 0+): the bar is "behaviour unchanged", not "tests green". Deliberate behaviour changes require blessing the golden.
- **Invariant suites** (Phase 0+) under `backend/tests/invariants/`: tenancy, shield-no-leak, fail-closed, audit-always. Build-breaking. Re-tangling must become structurally impossible.
- **No mock-shield in feature validations.** Mocks are permitted only for explicitly deterministic unit tests of non-LLM logic.

## 4 · Phase Done Checklist

A phase is `DONE` only when all of:

- [ ] Acceptance criteria from the dispatch brief met.
- [ ] Sprint memo written at `/app/memory/sprints/PHASE_<n>_<name>.md`.
- [ ] MASTER_STATE.md Section 6 + Section 8 updated.
- [ ] All existing tests still green + new tests added by this phase green.
- [ ] No silent exception swallowing introduced.
- [ ] Behaviour unchanged (or change documented + golden re-blessed + user-approved).
- [ ] Full harness green (deterministic + integration as scoped).

## 5 · Escalation triggers (surface to user, never auto-resolve)

- External blocker (credentials, env vars, third-party account, customer-side data).
- Pre-Read surfaces a discrepancy with the approved plan.
- Test failure whose root cause crosses phase boundary.
- Ambiguity not resolvable from existing docs.
- A `GATED` phase trigger has fired (Phase 6: scale or signed sale. Phase 7: paying customer).
- A discipline rail would have to be broken to make progress.
- Mid-dispatch ambiguity → surface as deviation in post-completion report. Builder MUST NOT use `ask_human` mid-build; orchestrator-channel resolves clarifications.

When escalating: state the ask in one sentence + give a 2-3 option menu. Do not block on yes/no philosophical debates.

## 6 · Two-language separation

- **Durable artifacts** (long-memory): `MASTER_STATE.md`, sprint memos, `INVESTOR_QA.md`, `PRODUCT.md`, `DEVELOPMENT.md`, this file. Live in `/app/memory/`.
- **Ephemeral context** (conversation): chat messages, terminal output, builder progress logs. Do not encode permanent decisions here without mirroring to durable.

If a decision is important, it must land in a durable artifact before the session ends. The chat is forgettable; `/app/memory/` is not.

## 7 · Re-architecture single backlog

Sequence per the approved execution plan (Syni_ReArchitecture_Plan v3):

| Phase | Track | Goal | Risk | Gate |
|---|---|---|---|---|
| 0 | Discipline | Characterisation harness + global invariants | Very low | Do first |
| 1 | Both | Contracts + logical data ownership + tenant propagation | Low | After 0 + Pre-Read |
| 2 | Discipline | Tenancy guard (#1 fix) | Medium | After 1 |
| 3 | Discipline | Frontend API-boundary contract | Low | After 1 (∥ 2) |
| 4 | Topology | Process separation (one deployment) | Medium | After 1–3 |
| 5 | Topology | Deployment separation (sell-ready) | Low (ops tax) | After 4 |
| 6 | Topology | Physical data carve | Med-high | **GATED:** scale OR signed sale |
| 7 | Topology | Commercial surfaces | Variable | **GATED:** paying customer |

Stabilise (0–3) is the prize. Split (4–5) is mechanical. Deferred (6–7) are paid for by triggers.

## 8 · Autonomous-mode operating contract

When the user grants autonomous execution:

**Auto-progress permitted on:**
- Read-only Pre-Read dispatches.
- Phase dispatches whose Pre-Read confirms approved-plan assumptions hold.
- Test runs (deterministic + integration).
- Sprint memo writes + MASTER_STATE updates.
- Targeted bug-fix follow-ups inside the current phase.
- Tester (`e1_tester`) verification passes.

**Mandatory escalation (NEVER auto-progress):**
- A Pre-Read finds the codebase doesn't match the approved plan's assumptions → surface with options.
- A GATED phase's trigger fires.
- An external credential / env var / customer-side artifact is required.
- Two consecutive fix attempts on the same root cause have failed.
- A discipline rail would need to be broken.

Autonomous ≠ unsupervised. Every phase still produces a sprint memo. Every dispatch is still recorded.

---

**End of protocol. Override only via explicit user directive recorded in chat AND mirrored to MASTER_STATE.md.**
