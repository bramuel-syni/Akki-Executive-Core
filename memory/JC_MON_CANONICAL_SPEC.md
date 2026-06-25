# JC-MON — Monitor build · Canonical Specification

> **Source:** User dispatch — 2026-06-25
> **Status:** ACTIVE
> **Supersedes:** Any prior Monitor brief in handoffs / runway docs / sprint memos.
>
> **Handoff-durability contract.** This file + DEV_PIPELINE.md §2 + the most
> recent JC-MON sprint memo together MUST be sufficient to resume the build
> without re-asking the user any locked decision. If a future
> agent-handoff reread of these three files is missing context to resume
> at the current stage, the gap is a defect — fix it inside that stage's
> closure, do not punt.
>
> Every JC-MON sprint memo MUST cite this file at the top, on its first
> line, as "Source of truth".

---

## Item 1 (do FIRST, before Stage 0) — JC-TM close-out breadcrumb

JC-TM Stage 2 fan-out is approved. The deep-link CTA (TaskDrawer →
Work Studio) shipped. The **reverse breadcrumb** (Work Studio → back
to TaskDrawer when opened via the CTA) was approved but did not ship.
Build it as a tiny additive commit BEFORE Stage 0:

- When Work Studio opens via `/app/work-studio?export_id=<eid>` and
  the export row has `source_task_id`, surface a one-line breadcrumb
  at the top of the wizard: `Created from task: <task-name>` with a
  click-back to `/app/tasks?task_id=<source_task_id>` (or whatever the
  TaskDrawer deep-link is on TaskListing).
- ~30 LOC in `WorkStudio.jsx` wizard-init or equivalent. Zero new
  endpoints. `source_task_id` already on the row.
- Commit message: `feat(JC-TM): created-from-task breadcrumb closes the round-trip`
- Smoke: open the CTA → land in Work Studio → see breadcrumb → click →
  back in TaskDrawer. Screenshot to
  `/app/memory/jc_artifacts/JC-TM-roundtrip-breadcrumb.jpg`.
- Append the close-out under a "Post-fan-out breadcrumb close-out"
  section in `sprints/JC_TM_FAN_OUT.md`.
- Do NOT bundle with JC-MON code. Separate, clean, additive commit.

---

## What Monitor IS (framing)

AI performance-monitoring workspace. User uploads a baseline (strategic
plan / performance agreement); the system AUTONOMOUSLY tracks progress
against it from documents marked "use for performance tracking"; two
sections — **strategic objectives** and **tasks**. AI is the
monitoring assistant: computes progress, predicts achievement
likelihood, assigns health, flags risks, recommends interventions.

## Decisions LOCKED (do not re-open)

- Monitor tasks and Task Manager tasks are the **SAME entity** in the
  **SAME `tasks` collection**, discriminated by the presence of an
  `objective_id`. ONE task entity, ONE task drawer rendered BY
  CONTEXT: a Monitor task shows objective linkage + email-update
  history; a TM task shows contribution linkage. **No separate
  `monitor_tasks` collection; no second task drawer.**
- The emailed-docs holding area **LIVES IN THE DOCUMENT JOURNAL** as
  a `pending` state — not a new Monitor surface, not a section in
  ObjectivesProjectsPanel. Emailed docs appear in a "pending" filter
  with an "accept" action; accept flips them to active (and into the
  tracking set if flagged).
- Auto-suggested objectives are a **CANDIDATE LIST** the user
  reviews/edits/confirms — NOT auto-created.
- Notifications are **OUT OF SCOPE** this dispatch — follow-up phase.

## Scope guardrails (protect shared, already-working things)

- The shared `tasks` entity was just stabilized by JC-TM. Any change
  to it for Monitor MUST NOT regress JC-TM's committed behaviour —
  the compile bridge, commit/edit-lock, and confidence invariants
  stay byte-for-byte intact. Adding `objective_id` is **additive
  only**; if making Monitor tasks work requires changing existing TM
  task behaviour, that's a **STOP**, not a quiet edit.
- The drawer-width standard is NOT in this dispatch. It is a
  system-wide change across four modules and ships as its own
  one-line dispatch (**JC-UI-DRAWER**). Do not touch other modules'
  drawers here. Monitor's own drawer is built to whatever the shared
  standard is at build time.

---

## Part 0 — production-quality bar

- Build to the brief; ObjectivesProjectsPanel (817 loc) is approved —
  **extend, don't redesign**.
- The AI assessment must produce a TRUSTWORTHY read grounded in the
  tracked documents — not a decorative score. A probability the user
  can't trust is worse than none. **Refusal discipline:** thin
  evidence → say so; do not emit a confident probability over
  nothing.
- REUSE: Solva `probability_weighting` for likelihood; Document
  Journal + upload + `source_channel` rails for ingestion; Task
  Manager inbound-email loop for task owner updates.
- Every LLM call **Shield-routed**; account/context-scoped; audit +
  fail-closed unchanged.
- **VERTICAL SLICE IS LAW:** prove the thinnest real thing
  end-to-end before widening. Do not build five assessment outputs at
  once.
- "Done" = a real objective assessed from real tracked docs, the
  drawer coherent — **never a green test alone**.

---

## Stage 0 — Prerequisites (gates, not footnotes)

**Q4 + Q2 run in PARALLEL** — they touch different systems (engine
integration vs FE component rollout). Do them concurrently. Surface
both reports together as the Stage 0 STOP-and-show.

### Q4 — Solva probability reuse verification (load-bearing — architectural-fork test)

Before Stage 2 writes anything, classify-by-execution that Solva's
`probability_weighting` ACCEPTS the inputs a Monitor objective +
tracked evidence would hand it.

**REPRODUCIBLE VERDICT REQUIREMENT.** Report side-by-side in
`/app/memory/audit/JC_MON_solva_fit_verification.md`:

- `probability_weighting`'s actual function signature + the shape of
  inputs it requires (cite line numbers in the Solva source)
- The shape of inputs a Monitor objective + tracked evidence would
  hand it (objective record + base doc IDs + tracking doc IDs +
  relevant fields)
- A line-by-line mapping: which Monitor input maps to which
  `probability_weighting` parameter; which are missing; which need
  transformation
- Verdict: **"thin adapter"** (wiring + transformation, proceed) OR
  **"STOP"** (non-trivial reshape) — derived from the table,
  reproducible by the user

This is the **compile-bridge moment of this module**. Prove the
engine fits before building on it. Do not assume the fit.

### Q2 — Tracking-checkbox upload-surface inventory

Backend is one column (`use_for_tracking`). FE is "available
anywhere." First inventory EVERY upload surface (Document Journal,
AddToWorkStudio modal, Brief uploads, Task contributor portal, any
others). Output to `/app/memory/audit/JC_MON_upload_surface_inventory.md`
with surface count + per-surface plan. Implement as **ONE shared
UploadOptions affordance** dropped into each — not reimplemented per
surface. If the inventory is large (>5 surfaces), report the count
before touching many.

---

## Stage 1 — Ingestion model (foundation)

Rides existing document/journal rails — flags on the document
record, not a parallel store.

- **BASE docs**: uploaded ON the Monitor page, marked
  `is_base_document=true`. Define what is tracked against.
- **TRACKING docs**: the "use for performance tracking" checkbox
  (the Q2 shared affordance) at point of upload, anywhere
  (`use_for_tracking=true`). The evidence the assessment reads.
- **EMAILED docs**: arrive via email (`source_channel="email"`) into
  the Journal in a **PENDING** state; a pending filter lists them;
  "accept into journal" moves them active (and into the tracking set
  if flagged). The pending state + accept action are the **new
  pieces**; the surface is the Journal.

**PROVE:** base doc on Monitor page; tracking-flagged doc elsewhere
via the shared affordance; emailed doc accepted from the Journal
pending filter. Show all three landing with their flags.

---

## Stage 2 — Achievement engine (core build; gated on Stage 0 Q4)

Assessment is baseline-vs-evidence, NOT signal-only: it reads BASE
docs + the `use_for_tracking` set (scoped to context/account) and
assesses the objective against them.

### 2a — Proving slice first (the thinnest real thing)

One objective, assessed against a real base doc + real tracking
docs, returning a **real PROGRESS %** and a **real PROBABILITY** (via
Solva). Show the actual output. With thin evidence, it refuses
rather than fabricating. **STOP and show before widening.**

### 2b — Then widen onto the proven slice, ONE AT A TIME

Each its own quality bar:
1. AI recommendations / interventions
2. AI explanation of performance
3. Extended health/status (beyond the current RAG)

**Do not batch these.** Each ships, each shown real.

### Reassess trigger (on-demand, NOT a standing background tracker)

Reassess when:
(a) a new tracking-flagged doc is accepted, or
(b) the user explicitly hits "update / reassess objective."

Background tracking layers on LATER once on-demand proves trustworthy.
**Do not build the background tracker first.**

---

## Stage 3 — Two-section experience + coherent drawer (assembly)

- `Monitor.jsx` (46-loc shell) becomes the **two-section workspace**:
  Strategic Objectives and Tasks. Reuse ObjectivesProjectsPanel for
  the objective board.
- **OBJECTIVES**: generate from a strategy doc as a CANDIDATE LIST
  the user reviews/edits/confirms; list, filter (status/owner/type),
  counts; open into a coherent detail drawer showing details,
  initiatives, owner, type, status, progress %, probability,
  last-updated, recommendations, AI explanation, reassess action.
- **TASKS** (same entity as TM, discriminated by `objective_id`):
  create manually or generate from a doc (review/edit before save),
  owner + owner-email, due date, status, progress, filters, counts;
  **ONE task drawer rendered by context** — Monitor task shows
  objective linkage + email-update history.
- **TASK EMAIL-UPDATE LOOP:** REUSE Task Manager's inbound-email
  mechanism — owner emails an update → AI extracts progress → task
  auto-updates → update history records it. Do NOT build a second
  loop; wire Monitor tasks onto the existing one, **additively**,
  without regressing TM.

---

## Proving slice (end-to-end, show it)

1. Upload a strategy doc as a BASE doc on the Monitor page
2. Generate objectives as a candidate list, confirm them
3. Upload a tracking-flagged progress doc elsewhere (and accept one
   emailed doc from the Journal pending filter)
4. Open an objective → reassess
5. A REAL progress % and REAL probability (via Solva) appear in the
   drawer
6. Create a task with an owner email
7. Simulate an owner email update
8. AI extracts progress and the task auto-updates with history

Show the actual assessment output and the actual auto-updated task.
**STOP and show before any fan-out.**

---

## Standing rules

- Reuse: Solva probability engine, Document Journal rails, Task
  Manager email loop. Do not rebuild these.
- Additive-only on the shared `tasks` entity — no JC-TM regression.
- Every LLM call Shield-routed; account/context-scoped; audit +
  fail-closed unchanged.
- On-demand reassessment is the build; the background tracker waits
  for it to prove out.
- Report by execution evidence: real assessment over real tracked
  docs, the coherent drawer, the auto-updated task. "It works" is the
  real output showing, not a test.
- **Escalate exactly two things**: a genuine STOP (Stage 0 Q4
  reshape; required TM-behaviour change; or an engine can't produce
  a usable result) or a real architectural fork. Else it's yours.

## Acceptance

A user uploads a baseline, marks tracking docs from anywhere (emailed
ones accepted via the Journal pending filter), and the system
autonomously assesses each objective against that evidence — starting
with real progress + probability, then recommendations + explanation
— surfaced in a coherent drawer. Tasks (same entity as TM,
discriminated by `objective_id`) track via owner-email updates that
auto-update progress, **with no JC-TM regression**. Two sections, one
workspace.

---

## Artefact manifest (per-stage handoff durability)

**Item 1 (JC-TM breadcrumb):**
- `/app/memory/jc_artifacts/JC-TM-roundtrip-breadcrumb.jpg` (screenshot)
- Append section to `sprints/JC_TM_FAN_OUT.md`

**Stage 0:**
- `/app/memory/audit/JC_MON_solva_fit_verification.md` (Q4, side-by-side)
- `/app/memory/audit/JC_MON_upload_surface_inventory.md` (Q2, surface count + per-surface plan)
- Sprint memo: `/app/memory/sprints/JC_MON_STAGE_0_PREREQS.md`

**Stage 1:**
- `/app/memory/jc_artifacts/JC-MON/01-ingest/base-doc.json`
- `/app/memory/jc_artifacts/JC-MON/01-ingest/tracking-doc.json`
- `/app/memory/jc_artifacts/JC-MON/01-ingest/emailed-doc-pending.json`
- `/app/memory/jc_artifacts/JC-MON/01-ingest/emailed-doc-accepted.json`
- Sprint memo: `/app/memory/sprints/JC_MON_STAGE_1_INGESTION.md`

**Stage 2:**
- 2a: `/app/memory/jc_artifacts/JC-MON/02-assess-thin/`
  - `objective-progress-pct.json`
  - `probability-via-solva.json`
  - `refusal-thin-evidence.json`
- 2b: `/app/memory/jc_artifacts/JC-MON/02-assess-thin/`
  - `recommendations.json`
  - `explanation.json`
  - `extended-health.json`
- Sprint memos: `sprints/JC_MON_STAGE_2A_ENGINE_THIN.md`
  and `sprints/JC_MON_STAGE_2B_ENGINE_FULL.md`

**Stage 3:**
- `/app/memory/jc_artifacts/JC-MON/03-experience/`
  - objectives section evidence
  - tasks section evidence
  - drawer-by-context evidence
  - email-update simulation + update history
- Sprint memo: `sprints/JC_MON_STAGE_3_EXPERIENCE.md`

All sprint memos: first line cites this file. DEV_PIPELINE.md §1/§2/§4/§9
updated BEFORE each memo. KNOWN_MAPPINGS extended for `JC_MON_*` pattern.
