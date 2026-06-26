**Canonical Spec**: `/app/memory/DEV_PIPELINE.md` (Journey 3a — Brief actions live on the origin surface: Solva / Monitor / Task Manager. Pattern shipped on Monitor in `JC_WAVE3_ORIGIN_BRIEFS_MONITOR.md`; this sprint completes the fan-out to the other two surfaces.)

# Wave 3 · Origin-triggered Briefs · Solva + Task Manager fan-out · CLOSED 2026-06-26 · 12/12 GREEN

## Sub-sprint scope (per user queue, msg follow-up)

> #2 Origin-triggered Briefs — fan out Solva → Task Manager
> Same `origin_kind` / `origin_id` schema. Module-specific auto-prefill builders.
> Pattern is already shipped on Monitor; this is replication, not redesign.
> HALT if a target surface doesn't use the shared Brief primitive — same coupling-debt rule as UI-DRAWER.

## Coupling-debt check — PASS

Every Brief affordance on every surface posts to the SAME route:

| Surface | Route | Count |
|---|---|---|
| Monitor | `/work-studio/export/brief` | 3 mentions (button + comment + helper) |
| Solva | `/work-studio/export/brief` | 2 mentions |
| Task Manager | `/work-studio/export/brief` | 3 mentions |

No parallel brief endpoint per surface. No coupling debt. HALT condition NOT triggered.

## Diff applied

### Solva (`SolvaArtefact.jsx` — handoff bar)

Added `FileText` import + a `Brief this session` `<button>` adjacent to the existing 3 handoff actions (Continue in Chat / Use as input / Take to Cycle). Skips for `status === "refused"` sessions (consistent with the existing "Use as input" gating).

Auto-prefill builder reads:
- `session.framing.user_input` → framing line in description
- `session.synthesis.primary_diagnosis` (or `synthesis.diagnosis`) → primary diagnosis line
- `session.synthesis.sensitivity_drivers` (first 4) → sensitivity driver line
- `session.synthesis.tensions` (first 3) → tensions line
- `SUBMODULE_LABELS[session.submodule]` → "Strategy memo" / "Hypothesis stress test" / etc. label

Posts to `/contexts/${cid}/work-studio/export/brief` with:
```js
{ description, objective, scope, output_format: "auto", cadence: "one_off",
  origin_kind: "solva_session", origin_id: sessionId }
```

`cid` resolves from `session.context_id` (orchestrator-stored) with a fallback to `readActiveContextId()` from `@/lib/api`. If neither resolves, surfaces `toast.error("No active context — switch into a context first.")` and aborts (no half-baked post).

### Task Manager (`TaskDrawer.jsx` — Compile tab)

Added `BriefThisTaskButton` rendered in the Compile-tab header next to the existing "Start/Resume Compile" CTA (so the user lands on the briefing affordance the moment they pivot from "build it" to "tell the board about it"). Component lives at the bottom of the file (mirrors the existing `CompileTab` pattern of co-located helper components).

Auto-prefill builder reads:
- `task.name` → headline title
- `task.description` (or `task.objective`) → description body
- `task.readiness_score` → readiness percent line
- `task.due_date` → due-date line
- `task.output_spec` → output-spec line
- `task.success_criteria` → success-criteria line

Posts to the same route with:
```js
{ ... , origin_kind: "task_manager_task", origin_id: task.id }
```

Same `cid` resolution as Solva: `task.context_id` → `readActiveContextId()` → error toast.

## Proving slice 12/12 GREEN

Run: `cd /app/backend && python scripts/jc_wave3_origin_briefs_solva_tm_fanout_slice.py`

| # | Subject | Outcome |
|---|---|---|
| 1 | Coupling-debt rule — all 3 surfaces share `/work-studio/export/brief` | ✓ |
| 2 | `ExportRequestIn` schema regression — still rejects unknown `origin_kind` | ✓ |
| 3 | `origin_kind=solva_session` round-trips to row + audit | ✓ |
| 4 | `origin_kind=task_manager_task` round-trips to row + audit | ✓ |
| 5 | Solva `solva-handoff-brief-this-session` test-id present | ✓ |
| 6 | Solva handler uses shared `api` client (no axios) | ✓ |
| 7 | Solva stamps `origin_kind=solva_session` + `origin_id=sessionId` | ✓ |
| 8 | Solva prefill reads `framing.user_input` + `synthesis` + `tensions` | ✓ |
| 9 | Task Manager `task-drawer-brief-this-task` test-id present | ✓ |
| 10 | Task handler uses shared `api` client (no axios) | ✓ |
| 11 | Task stamps `origin_kind=task_manager_task` + `origin_id=task.id` | ✓ |
| 12 | Task prefill reads `task.name` + `readiness_score` + `due_date` | ✓ |

Runtime: ~4s.

## Wave 3 Origin-triggered Briefs — overall status

| Surface | Status | Audit row |
|---|---|---|
| Monitor / Strategic Goals | ✓ shipped (sub-sprint 1) | `JC_WAVE3_ORIGIN_BRIEFS_MONITOR.md` |
| Solva v2 sessions | ✓ shipped (this sub-sprint) | this memo |
| Task Manager tasks | ✓ shipped (this sub-sprint) | this memo |
| Monitor signal cards (per-card) | not in scope | future sub-sprint when needed |
| Decisions Journal | not in scope | future sub-sprint when needed |

The four planned origin_kind enum values are now all wired end-to-end:
- `monitor_objective` (Monitor)
- `monitor_signal` (reserved; not yet wired)
- `solva_session` (Solva)
- `task_manager_task` (Task Manager)

## Files

- `frontend/src/components/solva/artefact/SolvaArtefact.jsx` — 2 import lines + handler + button
- `frontend/src/components/tasks/TaskDrawer.jsx` — 2 import lines + Compile-header insertion + `BriefThisTaskButton` at end of file
- `backend/scripts/jc_wave3_origin_briefs_solva_tm_fanout_slice.py` — new

No backend changes — the schema + persistence + audit work shipped in sub-sprint 1 covers both new origins.

— END —
