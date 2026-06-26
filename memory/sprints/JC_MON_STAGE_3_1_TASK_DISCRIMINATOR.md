# JC-MON Stage 3.1 — Task drawer discriminator + email-update loop

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 3).

**Closed 2026-06-25 · 6/6 acceptance rows GREEN** via
`python backend/scripts/jc_mon_stage_3_1_task_discriminator_slice.py`.

## What shipped

The **discriminator-driven** task drawer + email-update loop.
`objective_id` on `db.tasks` is the ADDITIVE-ONLY discriminator:

- `objective_id == None` → task is a **Task Manager task** (the
  existing F.1-F.5 flow). The TaskDrawer renders contribution
  linkage; the inbound-email handler runs the TM-mode behaviour
  ONLY (contributor_comments push + team status flip + readiness
  recompute + TM audit row). **JC-TM is byte-for-byte unchanged.**
- `objective_id != None` → task is a **Monitor task** linked to
  a strategic objective. The TaskDrawer renders objective linkage
  + `progress_updates[]` history; the inbound-email handler runs
  the TM-mode behaviour ABOVE plus a single Shield-routed progress
  extraction (`solve_v2.monitor_email_update_extract`). **ONE
  inbound path; the discriminator only changes what extra work
  attaches on top.**

ONE entity in `db.tasks`. ONE drawer rendered by context. ONE
inbound email loop. No fork. No second drawer. No second loop.

## Per-task shape (additive fields surfaced via `_sanitize_task`)

```json
{
  "id": "task-...",
  "...": "(existing TM fields unchanged)",
  "objective_id":     "obj-..." | null,         // discriminator
  "progress_updates": [                          // Monitor-mode history
    {
      "id": "...",
      "kind": "email_extract",
      "extracted_at": "...",
      "sender": "...",
      "progress_pct": 65,
      "rationale": "...",
      "target_metric": "...",
      "refused": false,
      "audit_entry_ids": ["..."]
    }
  ]
}
```

## Acceptance rows (verbatim)

```
✅ A. ONE entity: TM-mode + Monitor-mode tasks both in db.tasks (same id prefix)
✅ B. ONE drawer-by-context: objective_id is None for TM, set for Monitor row
✅ C. TM-mode unchanged: comments=1 team_status=['submitted'] monitor_progress_entry=None progress_updates=0
✅ D. Monitor-mode: TM behaviour PRESERVED (comments=1 status=['submitted']) AND additive progress extracted (pct=65)
✅ E. ONE inbound path: both scenarios served by _handle_task_contributor_reply (ok=True both)
✅ F. Honest refusal on opaque body: refused=True progress_pct=None tasks.progress_pct=None

6/6 acceptance rows GREEN — STAGE 3.1 STOP-AND-SHOW ready.
```

## Discipline

- **Additive-only on shared `tasks` entity.** Two new optional fields
  (`objective_id`, `progress_updates`); no rename, no enum mutation,
  no behavioural change to TM-mode tasks.
- **JC-TM regression-free.** Acceptance Row C verifies a TM-mode
  email reply still yields contributor_comments + team status flip
  + readiness recompute, with `monitor_progress_entry: None` in the
  response.
- **ONE inbound email extraction path.** Acceptance Row E verifies
  both kinds of task go through `_handle_task_contributor_reply`.
  The discriminator branch only attaches AFTER the TM-mode behaviour
  has completed.
- **Honest refusal.** Acceptance Row F: opaque body → no fabricated
  progress_pct. `progress_updates[0].refused = True`, task-level
  `progress_pct` left untouched.
- **Shield-routed.** Engine surface `solve_v2.monitor_email_update_extract`;
  audit_entry_ids attached per extraction (auditable from Monitor
  surfaces via a new audit action `monitor.task.progress_extracted_via_email`).
- **Brief affordance NOT in Stage 3.** Per user resolution — origin-
  triggered Briefs belong to per-module builds, not this stage.

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/services/monitor/email_update_extractor.py` | NEW · Shield-routed extractor + history-append helper | +260 |
| `backend/routers/tasks.py` | ADD `objective_id` on `_TaskIn`/`_TaskPatch`/`_sanitize_task` + create + patch + progress_updates surface | +20 |
| `backend/routers/inbound_email.py` | ADD discriminator branch (lines ~837-871) inside `_handle_task_contributor_reply` + audit row `monitor.task.progress_extracted_via_email` + `monitor_progress_entry` on response | +43 |
| `backend/scripts/jc_mon_stage_3_1_task_discriminator_slice.py` | NEW · 6/6 proving slice across 3 scenarios | +290 |

Zero changes to TM contributor flow code paths. The Monitor branch
sits BELOW the TM-mode behaviour with a try/except guard so a
discriminator-side failure NEVER blocks the TM-side behaviour.

## Live extraction sample (from the Monitor-mode scenario)

Input body (paraphrased): *"Week 9 status: Phase 1 exit gate PASSED.
Weekly active sessions index recovered to 97 by Week 9. Checkout
conversion pct now 102% of Q1 mean. Phase 2 reactivation campaign
launched Week 8. Headline monthly active revenue index this period:
92. Overall progress against target: 65%."*

Extraction result (real, Shield-routed):
- `progress_pct = 65`
- `target_metric = "monthly active revenue index"`
- `refused = False`
- audit_entry_ids non-empty (one Shield audit id per extraction).

## Artefacts

- `/app/memory/jc_artifacts/JC-MON/03-experience/3-1-task-discriminator/tm-mode-unchanged.json`
- `/app/memory/jc_artifacts/JC-MON/03-experience/3-1-task-discriminator/monitor-mode-extracts.json`
- `/app/memory/jc_artifacts/JC-MON/03-experience/3-1-task-discriminator/monitor-mode-refusal.json`
