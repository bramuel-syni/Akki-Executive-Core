# JC-TM — TASK MANAGER BUILD (Canonical Spec)

> **Source:** User dispatch — 2026-06-25
> **Status:** ACTIVE — canonical source of truth for Task Manager assembly
> **Runs in parallel with** JC-WS Phase 3 fan-out (different submodules, no tree collision expected)
> **Survives next context compaction.** Every JC-TM sprint memo cites this file at the top.

---

## Framing (do not drift)

> "An AI-ORCHESTRATED MULTI-CONTRIBUTOR document assembly workspace. The user coordinates HUMAN
> contributors; the AI is the orchestration ASSISTANT (finds missing info, detects conflicts, scores
> readiness, drafts reminders/revision requests, compiles approved contributions). It is NOT a fully
> autonomous agent that does the work alone."

The backend is the most complete of the secondary modules — task lifecycle, contributors,
contributions, readiness + AI intelligence, and a full compile→circulation→final→commit pipeline
are all wired, and the components exist (TaskDrawer, TaskListing, TaskSetupWizard,
CompilationReadinessSection, FollowUpDraftsCard). The gap is experience fluency: the components
aren't assembled into a journey a user can run end-to-end. This phase's ONE job: assemble them into
a fluent experience that produces real output. Proof = a real end-to-end run, shown — not "wired /
tests pass."

---

## Part 0 — Production-quality bar

- UI components exist and the brief's flows are approved — assemble and wire, do NOT redesign.
- Quality is a requirement: the compiled document must be professional best-shape (forward-to-a-board
  good), and the AI orchestration (gaps / conflicts / readiness / recommendations) must surface
  REAL findings, not decorative scores. "It rendered a number" is not done; "the readiness call is
  trustworthy" is.
- REUSE existing engines. Critically: compile must produce documents through the SAME generators
  and the SAME export wizard as Document Generation (board packs, committee packs, briefings, decks,
  financial models/XLS). Do NOT build a parallel generation stack. Task Manager orchestrates
  contributions; Document Generation's engines produce the document.
- Every LLM call Shield-routed; account-scoped; audit + fail-closed unchanged.
- Vertical slice: prove ONE full task end-to-end, shown, before polishing every surface.
- "Done" = the produced document opening cleanly and the real orchestration findings showing —
  never a green test alone.

---

## The Keystone — the Task Drawer (build/assemble FIRST)

The brief's core promise is "view task details, contributors, contributions, readiness, and
generated documents IN ONE PLACE." That one place is the task drawer. Today TaskDrawer.jsx exists
and is imported, but the page may still open a "coming soon" placeholder.

1. **FIRST:** classify by execution — does clicking a task open the real `TaskDrawer` or the
   placeholder? Report which. If placeholder, wiring the real drawer in is step one; everything
   else hangs off it.
2. The drawer is the single surface that brings together, for one task:
   - **task details** (objective, success criteria, template, output format, due date, status);
   - **contributors** (who, assigned responsibility, invite status) + add/reinvite;
   - **contributions** (submitted inputs, versions, approve / request-revision);
   - **readiness** (score + breakdown + the AI intelligence: missing info, conflicts, recommendations);
   - **generated documents** (drafts + final, with the compile flow reachable from here).

   These map to wired endpoints (`/tasks/{id}`, `/contributions`, `/intelligence`, `/compile…`) —
   assemble, don't rebuild.

---

## The journeys (assemble the wired backend into fluent flows)

1. **Create a task** — `TaskSetupWizard`: objective, success criteria, template, output format, due
   date; agent-prefill assists setup; save as draft or activate (commission). (Most-assembled flow
   — verify it runs clean.)
2. **Coordinate contributors** — add contributors, assign responsibilities, send invite links
   (3 modes: akki-account / email-reply / portal), reinvite. The contributor portal
   (`contribute/{token}`) lets them upload + submit + comment.
3. **Manage contributions** — as contributions arrive, the user reviews, APPROVES, or requests
   revisions; the AI drafts suggested revision requests; contributors submit updated versions; all
   versions accessible (audit trail).
4. **Assess readiness** — surface the readiness score + breakdown and the AI intelligence (missing
   info, conflicting inputs, objective-coverage, recommendations, reminder drafts). This must be a
   real, trustworthy read — the orchestration value lives here. **Refusal discipline:** if
   contributions are too thin to assess, say so; do not emit a confident score over nothing.
5. **Generate the document** — drive the wired compile pipeline from the drawer: compile draft from
   APPROVED contributions → review → (optional) circulation to reviewers → apply comments → final
   production → commit (locks). Multiple draft versions; edit; regenerate from updated
   contributions. Output via the Document Generation generators + export wizard
   (DOCX / PPTX / PDF / XLS).
6. **Monitor** — list all tasks; filter by status (draft / active / completed); search; delete
   draft tasks; open any into the drawer.
7. **Complete** — mark completed; task stays accessible; all contribution + document versions
   preserved.

---

## Proving slice (show the real run end-to-end)

Create a board-pack task (objective + success criteria + template + due date) → activate → invite
one contributor → contributor submits via the portal → user reviews and approves it → request a
revision on a second contribution (AI drafts the request) → contributor resubmits → open readiness:
a REAL score + breakdown + at least one real gap/conflict/recommendation from the AI → compile a
draft from approved contributions → run it to final → commit (locks) → download the produced
document (via the export wizard). Show the ACTUAL compiled document and the ACTUAL readiness
findings. **STOP and show before polishing the rest of the surfaces.**

---

## Standing rules

- Assemble and reuse — do not rebuild backend, generators, or the export wizard. Compile routes
  through Document Generation's engines.
- Every LLM call Shield-routed; account-scoped; audit + fail-closed unchanged.
- The drawer is the keystone — build/verify it first; the journeys hang off it.
- Report by execution evidence: show the real compiled document + the real readiness findings + the
  reachable compile flow. "It works" is the run completing and the artefact opening cleanly, not a
  test.
- Escalate exactly two things: a genuine STOP (a wired capability doesn't actually produce a usable
  result at runtime) or a real architectural fork (e.g. compile cannot reuse doc-gen generation
  without change). Everything else is yours within these rules.

---

## Acceptance

A user creates a task, coordinates real contributors, reviews and approves contributions, reads a
trustworthy readiness assessment with real AI findings, compiles approved inputs into a professional
document through the shared generators, runs it to a locked final, and downloads it — all from one
coherent surface. The orchestration is fluent and the output is forward-to-a-board good. The
keystone drawer brings details, contributors, contributions, readiness, and documents together in
one place, as the brief promises.

---

## Integration point with JC-WS

The compile step MUST route through Document Generation's engines and the shared Export Wizard
built in JC-WS Phase 1. This is a real integration point — verify by execution:

- Compile uses the same generator code paths as the Board Pack proving slice (same `pptx_exporter`
  / `work_studio_export` / etc.).
- The export wizard handoff produces a file in the same format set (DOCX / PPTX / PDF / XLS for
  financial models).
- No parallel generation stack. If you find one being created (or any temptation to fork the
  generator for TM), STOP — that's the architectural-fork escalation.

---

## Execution order

**Step 1 (mandatory, before anything else): KEYSTONE CLASSIFICATION**
- Classify by execution: does clicking a task in `TaskListing.jsx` open the real `TaskDrawer.jsx`
  or a "coming soon" placeholder? Read the page route + the click handler. Report which.
- If placeholder: wiring the real drawer in is the FIRST commit. The five drawer sections (details
  / contributors / contributions / readiness / generated documents) must surface against the wired
  endpoints.
- Output: `/app/memory/audit/JC_TM_keystone_classification.md`.

**Step 2: PROVING SLICE (end-to-end board-pack task)**
Walk the full proving slice per the canonical spec. Save artefacts under
`/app/memory/jc_artifacts/`:
- `JC-TM-task-created.json`
- `JC-TM-contributor-invite-state.json`
- `JC-TM-contribution-1-approved.json`
- `JC-TM-contribution-2-revision-request.json`
- `JC-TM-contribution-2-resubmitted-approved.json`
- `JC-TM-readiness-real-findings.json`
- `JC-TM-compiled-draft.docx`
- `JC-TM-final-locked.docx`
- `JC-TM-exported-via-wizard.docx`

**Step 3: STOP after proving slice for user inspection.**

**Step 4: After approval — fan out the remaining 6 journeys.**
- Memo: `/app/memory/sprints/JC_TM_JOURNEY_FAN_OUT.md`.
