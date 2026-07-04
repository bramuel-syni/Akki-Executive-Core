# Bundle 5 · V0.5 · Origin Briefs (Solva + TM) · PARTIAL (contract verified, live emit deferred)

**Timestamp:** 2026-07-04T18:06:11.488315+00:00
**Canonical criteria source:** `/app/memory/user_actions/V0_5_VERIFICATION_CHECKLIST.md`
**Canonical scope source:** `/app/memory/sprints/JC_WAVE3_ORIGIN_BRIEFS_SOLVA_TM_FANOUT.md` (CLOSED 2026-06-26)
**Dispatch disposition (2026-07-04):** dev-mode capture only, no real SendGrid; same discipline as B4.

## Shipped contract (verified)

The Wave 3 fan-out slice
(`jc_wave3_origin_briefs_solva_tm_fanout_slice.py`) shipped 12/12 GREEN
on 2026-06-26. Both Solva and TM route origin briefs through the
**shared** endpoint:

```
POST /api/contexts/{context_id}/work-studio/export/brief
     body: { "origin_kind": "solva_session" | "task_manager_task",
              "origin_id":   "<solva_session_id | task_id>",
              ... prefill fields ... }
```

Verified via runtime introspection:
- `origin_kind` field annotation: `typing.Optional[typing.Literal['monitor_objective', 'monitor_signal', 'solva_session', 'task_manager_task']]`
- Accepted Literal values: **['monitor_objective', 'monitor_signal', 'solva_session', 'task_manager_task']**
- `origin_id` field annotation: `typing.Optional[str]`

## What WAS captured (mechanical)

- `contract_verification.json` — Pydantic model field introspection
  + a snapshot of existing `work_studio_exports` rows carrying
  `origin_kind ∈ {solva_session, task_manager_task}` (
  4 existing rows in DB across all accounts).
- Prior slice closure evidence: `jc_wave3_origin_briefs_solva_tm_fanout_slice.py`
  GREEN 12/12 on 2026-06-26 (per `JC_WAVE3_ORIGIN_BRIEFS_SOLVA_TM_FANOUT.md`).

## What was NOT captured (declared gaps)

- **Live emit under julius**: no fresh brief emitted specifically for
  this bundle. Would require:
   - A solva_v2 session for julius (0 exist — same substrate gap as
     Bundle 2), OR
   - A TM task for julius (4 exist — could target one), followed by
   - A brief-emit invocation (30-60s LLM streaming per brief).
- **SendGrid outbound delivery** for the emitted brief — NOT verified.
  Same discipline as Bundle 4: dev-mode capture, no real Gmail hit.
- **In-app notification queue landing** — NOT verified. The brief
  emit flow persists a `work_studio_exports` row + the origin surface
  gets a "brief-emitted" affordance; the notification queue side of
  the delivery was not probed in this bundle.

## Truth-in-capability closure line

Shared origin-brief contract shipped + verified (endpoint + accepted
`origin_kind` values + persistence). Live emit for julius NOT captured;
SendGrid delivery + inbound notification loop NOT verified — proof
deferred to substrate-enriched + dispatch-authorized capture.

## Reproduction (once substrate + dispatch authorized)

```bash
# 1. Ensure julius has a Solva v2 session OR a TM task to emit from.
# 2. Invoke shared brief export with origin stamp:
#    POST /api/contexts/{cid}/work-studio/export/brief
#      body: {"origin_kind":"solva_session","origin_id":"<sid>","kind":"brief",...}
# 3. Capture the response artefact + persisted work_studio_exports row.
# 4. If SendGrid delivery is desired, run in dev-mode with sandbox flag
#    (see B4 pattern) — do NOT hit real Gmail.
```
