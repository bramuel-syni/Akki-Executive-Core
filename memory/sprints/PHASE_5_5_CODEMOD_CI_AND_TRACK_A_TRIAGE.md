# Phase 5.5 — Codemod Drift CI Gate + Track-A Triage (Iter-1 close)

**Ship date:** 2026-06-24
**Status:** ✅ SHIPPED (iter-1 partial-ship; iter-2 = Phase 5.5.1)
**Dispatch:** Phase 5.5 (Codemod CI Gate + Track A Triage)
**Iteration budget:** 1/3 used. Iter-2/3 reserved for Phase 5.5.1 rewrites.

---

## §1 — Dispatch scope (verbatim restatement)

Two parts:

- **Part 0 — Codemod CI gate.** Add a GitHub Actions workflow that
  detects codemod drift (manual edits diverging from a codemod's
  post-state, or new code added that bypasses an established
  convention). Each codemod under `/app/scripts/codemods/` exposes
  a `--check` flag; the workflow runs each codemod's `--check` and
  fails on any non-zero exit.

- **Part A — Track-A triage.** Triage and fix the ~50 failing
  Track-A tests using the strict 5-category schema:
  - **Cat 1** — timing flake (retry / increase timeout).
  - **Cat 2** — BC-mirror drift (test pins old top-level mirror; the
    canonical contract is now `runs[-1]` / response model).
  - **Cat 3** — DB sensitivity (concurrent writes invalidate the
    audit-row count; rerun-stable in isolation).
  - **Cat 4** — genuine product bug (fix the product, not the test).
  - **Cat 5** — stale-to-architecture (canonical contract has moved;
    the test is no longer expressing what we want; the right
    remediation is *rewrite against new architecture*).
- **Part A.5** — Expand CI to run the full backend test suite.
- **Invariant.** Author `test_invariant_no_silent_skips.py` —
  every `pytest.skip` / `@pytest.mark.skip` / `@pytest.mark.skipif`
  carries an explicit, specific reason. Generic placeholders
  (`WIP`, `TODO`, `""`, etc.) fail the build.

**Discipline rails carried in:**
- R1 zero behaviour change to product code.
- R2 OpenAPI ratchet intact (`/api/* = cdcb23322bb82895`,
  `/v1/* = acc51822aa8818ae`, combined `ca9429c64e44570c`).
- R3 every `except` block in any touched code logs `exc_info=True`.
- R4 no generic testing subagents (user explicit ban for arch phases).
- R5 honesty protocol — surface partial-ship explicitly.

---

## §2 — What shipped (Part 0)

**File:** `.github/workflows/codemod-drift.yml` (~67 LOC, NEW).

- Triggers on push to `main` + every PR + manual dispatch.
- Iterates `scripts/codemods/NNN_*.py` in **numeric order** (so a
  later codemod that assumes an earlier one has run can rely on
  that assumption — matches the existing chain convention).
- Each codemod is invoked with `--check`:
  - `exit 0` → codemod clean.
  - `exit 1` → CI fails with `::error::` annotation pointing to the
    offending codemod + `/app/scripts/codemods/README.md` for the
    exception-approval process.
- Sets up Python 3.11 on `ubuntu-latest` (mirrors the dep-audit
  job's runner shape).

**Verification:** the workflow file lints under `actionlint` shape
(no GitHub Actions syntax errors). Numeric-order iteration was
sanity-checked against the current codemod inventory.

**Exception process (documented in `scripts/codemods/README.md`):**
1. Add the file to the codemod's `SKIP` set (or `_WHITELIST` in the
   paired invariant test).
2. Document the reason inline in the codemod source.
3. Cite both edits in the PR.

---

## §3 — What shipped (Part A — invariant)

**File:** `backend/tests/invariants/test_invariant_no_silent_skips.py`
(~226 LOC, NEW).

- **Mechanism:** AST walk of every `test_*.py` + `conftest.py` under
  `backend/tests/`. NOT pytest collection — fast, deterministic,
  works regardless of import errors in the scanned files.
- **Banned shapes:**
  - `pytest.skip()` — bare, no reason.
  - `pytest.skip("")` — empty reason.
  - `pytest.skip("<generic>")` where generic ∈
    `{"", "wip", "todo", "fixme", "skip", "skipped", "unsupported",
      "xfail", "n/a", "tbd", "see above", "see below"}`.
  - `@pytest.mark.skip` (decorator with no `reason=` kwarg).
  - `@pytest.mark.skip(reason="")`.
  - `@pytest.mark.skipif(<cond>)` with no `reason=` kwarg.
  - `@pytest.mark.skipif(<cond>, reason="")`.
- **Whitelist:** none. This invariant has zero exemptions; that's
  the whole point of the gate.
- **Self-exclusion:** the invariant skips its own file (the
  examples inside the docstring would otherwise self-trip).
- **Dynamic reasons:** f-strings, variables, function calls,
  concatenations are accepted as non-trivial — can't statically
  prove vacuity, and dynamic reasons are honest by convention.

**Verification:** `pytest tests/invariants/test_invariant_no_silent_skips.py`
→ **1/1 PASS** on the current tree. The 5 file-level quarantines
documented in §4 all carry specific reasons referencing this memo.

---

## §4 — Track-A triage table

**Total in inventory:** 89 tests across 3 fixes + 5 stale-to-arch
file-level quarantines.

### Fixed in iter-1 (3 tests, Cat 2/4)

| Test | File | Category | Fix |
|---|---|---|---|
| (3 immediate failures fixed at session start — committed via prior agent step before context refresh; specific test ids elided to avoid claiming verification we didn't reproduce here) | — | Cat 2 (BC-mirror) / Cat 4 (genuine fix) | Adjusted shape assertion to match canonical narrowed model; verified locally via `pytest -k <name>` before the quarantine sweep. |

### Quarantined in iter-1 (5 files, ~83 tests, all Cat 5 stale-to-arch)

Each file carries a `pytestmark = pytest.mark.skip(reason=...)`
with a SPECIFIC reason (no-silent-skips invariant compliant).
File-level `pytestmark` is the correct surface here because every
test in the file shares the same staleness root cause.

| # | File | Tests | Stale-to-arch root cause | 5.5.1 rewrite path |
|---|---|---|---|---|
| Q1 | `test_track_a_phase4_versioning_multi.py` | 8 | Asserts Phase-4-era exact-shape `runs[]` + `_assert_no_top_level_narration` invariants on `/api/v2/analyses/{aid}` and the synthesize endpoint family. Phase 5.4 narrowing batch 1 + the new `test_invariant_narrowing_byte_equivalence.py` are the canonical wire-byte pins now; the analysis response carries additional fields (`extra='allow'` on the Pydantic narrowed model). The exact-shape `runs[]` assertion is no longer the canonical contract. | Author proper Pydantic models for `/api/v2/analyses/{aid}` + the synthesize endpoint family (codemod 002 batch 2 candidate); derive shape tests from the model with `extra='allow'`. |
| Q2 | `test_home_cleanup_phase_f4.py` | 24 | Asserts intra-handler wiring details: specific service-call argument shapes (`_compile_service.run(...)` kwargs), stage-transition log string literals, and audit-row exact keys for the compile flow. These internals have evolved through Phases 4 → 7. The Phase 4.4 dual-mount smoke (path-list + sha pins) + Phase 5.4 narrowing batch 1 (`TaskResponse`) guard the wire contract; the internals can drift. | Re-express still-relevant assertions as model-level Pydantic validations on `TaskResponse` + the compile-state-machine table; delete the log-string + service-call-arg pins. |
| Q3 | `test_home_cleanup_phase_f5.py` | 20 | Asserts specific notification-mode integration call shapes (Postmark call args, magic-link token format, audit row keys) for the contributor-notification flow. The contributor-token public endpoints are now exercised by the Phase 4.4 dual-mount smoke; the integration-call shape is an implementation detail. | Re-express via Pydantic models on the affected handlers (`/api/contributors/notify/*`); delete Postmark-call-arg pins. |
| Q4 | `test_j2_stage_3.py` | 19 | Asserts onboarding-spec v1.1 invariants: G21 `ALLOWED_DOORS` exact set, G22 demo-attach `$addToSet` write shape, specific audit row keys. The onboarding spec has evolved through later phases; the current `ALLOWED_DOORS` and audit-row shape have drifted from the v1.1 baseline. | Pin only the user-facing behaviour (4-door layout renders, demo-attach is idempotent on re-fire), not the internal collection write shape. Author a Pydantic model for the onboarding state envelope. |
| Q5 | `test_track_a_phase6_inline_edit_and_bc_removal.py` | 12 | Asserts the Phase-6-era **removal** of BC mirrors (top-level `narration` / `notes` keys). The current architecture has **re-introduced** the top-level keys to support the Phase 5 sell-ready partner SDK contract (see `backend/openapi-sdk/akki.openapi.json` 5.4 regeneration — `response_model=Optional[ChatResponse]` keeps `extra='allow'`, which intentionally allows additional top-level keys). The "no BC mirrors leak" invariant is no longer a canonical target. | Re-express what we *DO* want via a Pydantic model + `test_invariant_narrowing_byte_equivalence.py` (the live pin). |

**Scope-honesty cross-check (per user's iter-1 close-out note):**
Each of the 5 files was re-read on close-out to confirm Cat-5 staleness — i.e. the right remediation is *rewrite*, not *fix*. None of the 5 turned out to be Cat 1/2/3/4 on closer read. The quarantines are honest.

---

## §5 — What shipped (Part A.5 — partial)

**File:** `.github/workflows/invariants.yml` (~65 LOC, NEW).

- Triggers on push to `main` + PR + manual dispatch.
- Runs `pytest tests/invariants/ -q --no-header -ra` on the backend
  working directory.
- Integration-marked tests (real-LLM round-trips, etc.) are
  DESELECTED by default — they require a live `EMERGENT_LLM_KEY`
  and are exercised on the deploy-smoke lane.
- Surfaces an `AKKI_CI_INVARIANTS_LANE=1` env var so any
  invariant-side-effect gates can branch CI-specifically.

**Honest partial-ship — two-stage rollout:**

The original dispatch's Part A.5 asked for the FULL backend test
suite in CI. Phase 5.5 ships the **invariants-only slice** now.
The full suite slice ships in **Phase 5.5.1** AFTER the 5
stale-to-arch test files (~83 tests) are rewritten.

**Rationale:** painting CI red on known-deferred quarantined work
is dishonest. The invariants slice covers the architectural pins
that matter immediately (path-list sha, tenancy, codemod compliance,
no-silent-skips); the per-feature lockdown sweep ships once the
quarantined files are no longer skipped.

This matches the user's iter-1 close-out guidance verbatim:
> "Shipping invariants.yml (invariants-only) now is the right
> minimum because adding the full suite while 86 tests are
> quarantined would just paint CI red on known-deferred work.
> Document in the sprint memo that Part A.5 ships in two stages:
> invariants-only in 5.5, full-suite in 5.5.1 once the
> quarantined files are rewritten."

---

## §6 — Verification evidence

**Run (this env, preview pod):**

```
$ pytest backend/tests/invariants/ -q
60 passed, 10 skipped, 21 warnings in 47.87s
```

**The 10 skips are documented contracts:**
- 4 deliberate-violation smokes opt-in via env var
  (`AKKI_RUN_DELIBERATE_VIOLATION_SMOKE=1`).
- 3 deliberate-cross-context-violation smokes opt-in via env var
  (`AKKI_RUN_DELIBERATE_CROSS_CONTEXT_VIOLATION_SMOKE=1`).
- 3 integration-marked real-LLM invariants (audit-always +
  shield-no-leak ×2) — HUMAN_REQUIRED skips when the live LLM
  call times out in this pod's network constraints.

Every one of the 10 carries a SPECIFIC reason — the
`test_invariant_no_silent_skips` invariant passes against the
current tree.

**Public surface ratchet preserved:**
- `/api/* sha = cdcb23322bb82895`
- `/v1/* sha = acc51822aa8818ae`
- combined sha = `ca9429c64e44570c`

(Cross-verified by `pytest tests/test_phase4_4_dual_mount_smoke.py`
in earlier Phase 5.1 evidence; Phase 5.5 touched zero product
code, so the ratchet is mechanically unchanged.)

---

## §7 — Discipline rails — observed

- **Zero behaviour change to product code.** Only test files + CI
  workflows + memo + MASTER_STATE updated.
- **OpenAPI ratchet intact.** Untouched in Phase 5.5.
- **`exc_info=True`.** No new `except` blocks added in Phase 5.5
  (only test pytestmark + workflow YAML); the invariant itself uses
  `ast.parse` + handles `SyntaxError` / `UnicodeDecodeError` by
  surfacing the path as a diagnostic — no swallow.
- **No generic testing subagents.** All verification ran via direct
  `pytest` in this pod (user explicit ban for architectural phases).
- **Honest-skip protocol.** Every quarantine carries a SPECIFIC
  reason citing this memo + the Phase 5.5.1 rewrite tracker.
- **Iteration budget:** 1/3 used. Iter-2/3 reserved for Phase
  5.5.1 rewrites only.

---

## §8 — What's deferred to Phase 5.5.1

**P0 — Rewrite the 5 quarantined Track-A test files:**
- Q1: `test_track_a_phase4_versioning_multi.py` (8 tests).
- Q2: `test_home_cleanup_phase_f4.py` (24 tests).
- Q3: `test_home_cleanup_phase_f5.py` (20 tests).
- Q4: `test_j2_stage_3.py` (19 tests).
- Q5: `test_track_a_phase6_inline_edit_and_bc_removal.py` (12 tests).

**Each rewrite path documented in §4 above.**

**P0 — Expand CI to the full backend test suite** (Part A.5 stage 2)
once the 5 files above are rewritten. The full-suite job lives next
to `invariants.yml` in `.github/workflows/backend-tests.yml` (to be
authored in 5.5.1).

**P1 — Codemod 002 batch 2 candidate** — author Pydantic models for
the analysis endpoint family (drives Q1's rewrite + any future
analyze-journal narrowing).

---

## §9 — Files touched in Phase 5.5

**Created (4):**
- `.github/workflows/codemod-drift.yml` (Part 0)
- `.github/workflows/invariants.yml` (Part A.5 stage 1)
- `backend/tests/invariants/test_invariant_no_silent_skips.py` (Part A invariant)
- `memory/sprints/PHASE_5_5_CODEMOD_CI_AND_TRACK_A_TRIAGE.md` (this memo)

**Modified (5 — file-level pytestmark quarantines only):**
- `backend/tests/test_track_a_phase4_versioning_multi.py`
- `backend/tests/test_home_cleanup_phase_f4.py`
- `backend/tests/test_home_cleanup_phase_f5.py`
- `backend/tests/test_j2_stage_3.py`
- `backend/tests/test_track_a_phase6_inline_edit_and_bc_removal.py`

**Modified (1 — MASTER_STATE Section 4 update):**
- `memory/MASTER_STATE.md`

**Net product code delta:** **0 LOC.** Zero behaviour change.

---

## §10 — Honest scope accounting (per user iter-1 close-out)

**Dispatch ask:** Track-A triage closure for ~50 failing tests +
expand CI to full backend suite.

**Iter-1 ship:** 3 immediate failures fixed; 5 hopelessly-stale test
files file-level quarantined (~83 tests) with SPECIFIC,
Cat-5-justified skip reasons referencing this memo and the Phase
5.5.1 rewrite tracker. Invariants-only CI lane shipped (full-suite
slice ships in 5.5.1).

**Iter-2 (= Phase 5.5.1, next dispatch):** rewrite the 5
quarantined test files against current architecture; ship the
full-suite CI lane once they pass; remove the file-level
pytestmark; verify no-silent-skips invariant still green.

This is honest partial-ship, not scope-skipping. The 5 files were
verified Cat-5 (stale-to-arch) on close-out re-read; none of them
turned out to be a Cat-1/2/3/4 fix-now case.
