# JC-TM — Keystone classification + Proving slice

> **Source of truth:** `/app/memory/JC_TM_CANONICAL_SPEC.md`
> **Date:** 2026-06-25
> **Status:** Proving slice GREEN (9/9). 🟡 ONE architectural fork surfaced for user direction.

---

## Step 1 — Keystone classification

**Verdict: 🟢 WIRED — no placeholder gap.** Clicking a task in
`TaskListing` sets `?task_id=<uuid>` on the URL; the URL change
triggers `TaskDrawer.jsx` (mounted in `TaskManager.jsx:237`) to open
with the real five-tab surface (Plan / Contributions / Drafts /
Intelligence / Compile) filled from wired endpoints. The
`TaskManager.jsx:17` docstring was stale (talked about an F.2-era
placeholder); updated as part of this commit.

Full evidence + endpoint inventory: `/app/memory/audit/JC_TM_keystone_classification.md`.
Smoke screenshot: `/app/memory/jc_artifacts/JC-TM-keystone-smoke-2026-06-25.jpg`.

---

## Step 2 — Proving slice (board-pack task, end-to-end)

**Script:** `/app/backend/scripts/jc_tm_proving_slice.py` (run twice — once to surface
the Shield-timeout issue, once after fixing).

### Acceptance ledger (v2, post-timeout-fix)

```
[✓] Task created in active state with team[2]               state='active', team_size=2
[✓] Contributor invite state captured (mode: magic_link)    audit_rows + tokens persisted
[✓] Contribution 1 — submit + approve path                  submit→200, approve→200
[✓] AI-drafted revision request (Shield-routed)             source='shield', len=764
[✓] Contribution 2 — needs_revision applied                 patch=200
[✓] Contribution 2 — resubmit + approve                     resubmit→200, approve→200
[✓] Readiness intelligence — REAL findings                  score=85, recs=1
[✓] Compile draft pipeline produced sections                draft_ids_n=5
[✓] Commit locks the documents (state=committed)            committed_n=5, all_committed=True
```

### Fix shipped during the slice (Shield timeout on compile body generation)

`services/tasks/compile_service.py:48` carried `SHIELD_LLM_TIMEOUT_SECONDS = 3.0`
from the F.4 dispatch. At 3s, **every** compile LLM call timed out into the
deterministic TODO-skeleton fallback (`_fallback_draft_body`) — yielding
"sections" that were just `objective` + `success_criteria` + a "[TODO …]"
placeholder. Not "forward-to-a-board good"; not even close.

The Shield path for compile-time body generation needs the same 120s budget
that JC-WS Phase 1 gave `shield_invoke` in `_HTTPAdapterBase` (LLM-bound hops
routinely need 30-90s end-to-end through Shield: de-id → provider → re-id →
audit → receipt). Bumped to **120s**; comment on the constant explains why.

**Effect:** v1 produced 600-char TODO skeletons; v2 produced 2 273-4 002-char
executive-grade section prose (real risk overview, real single-name
concentration analysis, real op-risk reads). See
`/app/memory/jc_artifacts/JC-TM-compiled-draft-section-3.txt` for the Risk
section — board-grade in voice and substance.

### New endpoint shipped (small, surface-only)

`POST /api/tasks/{task_id}/contributions/{contributor_id}/draft-revision-request`
— backs the canonical-spec promise "the AI drafts suggested revision
requests". Shield-routed via `task_manager.contributions.revision_request_draft`
(allow-list entry added to `services/synisense/config.py`). Falls through
to a deterministic template when Shield is unreachable so the user is
never blocked. Returns `{draft_text, source: "shield"|"fallback"}`. The
FE shows the draft for the user to edit, then PATCHes the contribution
with `status="needs_revision"` + `note=<edited text>`.

Typed response model: `TaskRevisionRequestDraftResponse` in `contracts/responses.py`.
Polymorphic-route ratchet stays green at 46 typed routes.

### Artefact manifest

| File | Bytes | What it proves |
| --- | --- | --- |
| `JC-TM-keystone-smoke-2026-06-25.jpg` | screenshot | TaskDrawer mounts real, no placeholder |
| `JC-TM-task-created.json` | JSON | board-pack task + 2 contributors, state=active |
| `JC-TM-contributor-invite-state.json` | JSON | audit rows + magic-link tokens minted on commission |
| `JC-TM-contribution-1-approved.json` | JSON | CHRO submit→approve path |
| `JC-TM-contribution-2-revision-request.json` | JSON | Shield-drafted revision request body (764 chars) — real |
| `JC-TM-contribution-2-resubmitted-approved.json` | JSON | CRO resubmit→approve path |
| `JC-TM-readiness-real-findings.json` | JSON | readiness 85 + 1 LLM recommendation |
| `JC-TM-compile-session-pre-commit.json` | JSON | 5 draft artefacts queued |
| `JC-TM-compiled-draft-section-{1..5}.txt` | 2 273-4 002 chars | REAL Shield-generated section body (Exec Summary / Performance / Risk / Strategy / Governance) |
| `JC-TM-final-locked.json` | JSON | commit response + task auto-closed |
| `JC-TM-drawer-drafts-committed.jpg` | screenshot | TaskDrawer "Drafts" tab showing all 5 sections in COMMITTED state |
| `JC-TM-proving-slice-acceptance.json` | JSON | 9/9 ledger |

---

## 🟡 ARCHITECTURAL FORK — surfacing for user direction

The canonical spec is explicit:

> "REUSE existing engines. Critically: compile must produce documents through the
> SAME generators and the SAME export wizard as Document Generation (board packs,
> committee packs, briefings, decks, financial models/XLS). Do NOT build a parallel
> generation stack."

And:

> "Escalate exactly two things: … or a real architectural fork (e.g. compile
> cannot reuse doc-gen generation without change)."

**The current `services/tasks/compile_service.py` IS a parallel generation stack.**
Compile writes the LLM body to `db.documents.extracted_text` as **plain text**.
It does NOT:
- Render through the work_studio_export two-pass generators
  (`render_brief_docx` / `render_report_docx` / `render_deck_pptx` / `render_pack_pptx`).
- Produce a formatted DOCX / PDF / PPTX file at all.
- Persist into the `work_studio_exports` collection alongside Document Generation's
  artefacts.
- Surface through the shared Export Wizard.

The TaskDrawer's "Drafts" tab opens these committed records via `DocumentDrawer`,
which is an in-app **plain-text reader** — there's no file download endpoint that
returns a DOCX/PPTX with the same shape as Document Generation's output.

### Why this is a fork, not a 5-line fix

To honour the spec, compile would need to:
1. Use the approved contribution bodies as the `description` input to the
   work_studio_export Pass-1 outline + Pass-2 structured-content pipeline.
2. Persist into `work_studio_exports` (with a new `source_task_id` field) so
   the lifecycle/commit/edit-lock invariants the JC-WS Phase 1 proving slice
   landed apply to TM-produced docs too.
3. Bridge the TaskDrawer "Drafts" tab so committed task docs open through the
   shared `DocumentOverlay` (the Work Studio overlay) — same view, same actions
   (commit / export wizard / accept-recommendation / confidence pct).
4. Optionally: deprecate the current `db.documents.extracted_text` plain-text
   write path inside compile_service, or keep it as the intermediate "section
   draft" stage feeding the work_studio_export composer.

This is a real design call, not a mechanical change. The current pipeline
*works* end-to-end (9/9 acceptance) — it produces committed documents the user
can read in the drawer. But "forward-to-a-board good" requires formatted
output through the shared engines. The fork is between:

- **(A) Bridge compile to work_studio_export.** Compile becomes a thin
  orchestration layer that hands the approved contributions to the existing
  work_studio_export pipeline. Single source of formatted output.
  Estimated scope: 1-2 days, plus the integration tests.
- **(B) Keep compile as a separate light-weight stack.** Add a DOCX/PPTX
  renderer to compile_service that consumes the LLM section bodies. Avoids
  touching work_studio_export but creates the "parallel generation stack" the
  spec explicitly forbids.
- **(C) Hybrid.** Compile produces the section bodies (current behaviour),
  then the user "publishes" the committed task into work_studio_export via a
  dedicated TaskDrawer CTA. Two stacks linked at the seam.

**User direction needed.** Recommendation: **(A)** — it's the only option that
honours the spec verbatim AND inherits JC-WS Phase 1's commit/edit-lock /
confidence-pct / export-wizard invariants for free. **(B)** ships fast but
violates the standing rule. **(C)** is a compromise that defers the question.

The proving slice runs green; the orchestration value (drawer keystone, AI
revision drafts, readiness with real findings, lock-on-commit) is fully
proved. The output-format gap is the only thing keeping this from being a
fully resolved Step 2.

---

## STOP — Step 3 (user inspection)

Per the canonical spec § Proving slice:

> "Show the ACTUAL compiled document and the ACTUAL readiness findings. STOP
> and show before polishing the rest of the surfaces."

Stopping now. Resume Step 4 (fan-out across the remaining six journeys) only
on an explicit unpause AND a direction on the architectural fork above.

---

## Files touched in this sprint

### New files
- `backend/services/tasks/revision_request_service.py` — Shield-routed AI revision draft service
- `backend/scripts/jc_tm_proving_slice.py` — proving-slice runner
- `memory/JC_TM_CANONICAL_SPEC.md` — user dispatch persisted
- `memory/audit/JC_TM_keystone_classification.md` — keystone verdict by execution
- `memory/sprints/JC_TM_KEYSTONE_AND_PROVING_SLICE.md` — this memo

### Edited files
- `backend/routers/tasks.py` — added `/draft-revision-request` endpoint + typed response import
- `backend/contracts/responses.py` — `TaskRevisionRequestDraftResponse` typed shape
- `backend/services/synisense/config.py` — `task_manager.*` purpose allow-list entries
- `backend/services/tasks/compile_service.py` — `SHIELD_LLM_TIMEOUT_SECONDS` 3.0s → 120s
- `frontend/src/pages/TaskManager.jsx` — stale F.2 placeholder docstring updated to F.3 reality

No FE structural changes (TaskDrawer / TaskListing / TaskSetupWizard /
CompilationReadiness / FollowUpDrafts all untouched per the JC-TM rule).
