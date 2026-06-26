# JC-MON Stage 3.0 — Candidate-objectives generator (Reassess action)

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 3).

**Closed 2026-06-25 · 5/5 acceptance rows GREEN** via
`python backend/scripts/jc_mon_stage_3_0_candidate_objectives_slice.py`.

## What shipped

The Reassess action's **candidate-list generator**. Reads BASE doc
evidence (`is_base_document=true` documents in the Monitor context)
and proposes 2-6 candidate strategic objectives. The user reviews /
edits / confirms each candidate BEFORE anything is persisted —
**no objective exists until confirmed**.

Generation call, not classifier:
- Service: `services/monitor/objective_candidate_service.py` ·
  `generate_candidate_objectives(...)` · Shield-routed under
  `solve_v2.monitor_candidate_objectives`.
- Endpoint: `POST /api/contexts/{cid}/monitor/objectives/generate-candidates`
  body `{base_doc_ids?: [...], context_label?: str}` →
  `{candidates: [...], refused, refusal_reason, refusal_note,
  audit_entry_ids, generated_at, base_doc_ids}`.

## Per-candidate shape

```json
{
  "title": "Recover monthly active revenue index to ≥ 100",
  "description": "<one-paragraph context, ≤ 480 chars>",
  "target_metric": "monthly_active_revenue_index",
  "target_value": "Index ≥ 100 within 180 days from programme start",
  "due_date": "YYYY-MM-DD" | "",
  "rationale": "<one sentence why this comes from the BASE doc>",
  "evidence_citation": "<BASE doc name or quote>",
  "confidence_band": "Strongly-grounded" | "Reasonably-grounded" | "Speculative"
}
```

## Acceptance rows (verbatim)

```
✅ A. 2-6 candidates returned — got 5 (refused=False)
✅ B. every candidate has title + target_value + evidence_citation (n=5)
✅ C. refusal short-circuit on no_baseline_evidence — refused=True audits=0
✅ D. confirmed candidate persists via existing path (delta=1)
✅ E. Shield audit ids attached on live run — count=1

5/5 acceptance rows GREEN — STAGE 3.0 STOP-AND-SHOW ready.
```

## Discipline

- **No objective exists until confirmed.** The generator NEVER writes.
  Confirmed candidates flow through the EXISTING
  `POST /api/contexts/{cid}/monitor/objective` route.
- **Honest refusal.** Empty BASE docs → no LLM call, reason
  `no_baseline_evidence`. Parse failure → audit trail preserved,
  reason `candidate_parse_failed`.
- **Every successful candidate cites the BASE doc.** No fabricated
  goals — the LLM is instructed to RETURN AN EMPTY LIST + a refusal
  note if evidence is thin.
- **Additive.** Zero changes to existing objectives CRUD or
  auto-suggest endpoints. The new endpoint sits alongside.

## Sample output (from the live run)

5 candidates grounded in the MYDAWA Recovery BASE docs (all
Strongly-grounded):

1. Recover monthly active revenue index to ≥ 100 · Index ≥ 100 within 180 days from programme start
2. Restore weekly active sessions index to ≥ 95 (Phase 1 exit gate) · Index ≥ 95 by Phase 1 completion
3. Achieve revenue index ≥ 95 through customer reactivation (Phase 2 exit gate) · Index ≥ 95 by Phase 2 completion
4. Lift checkout conversion to pre-incident mean · Achieve pre-incident mean by Day 60
5. Achieve 12% reactivation email response rate · Response rate ≥ 12% by Day 120

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/services/monitor/objective_candidate_service.py` | NEW · Shield-routed LLM generator + hardened parser | +257 |
| `backend/routers/monitor_strategic_items.py` | ADD endpoint `POST /contexts/{cid}/monitor/objectives/generate-candidates` + `_CandidateGenIn` schema | +73 |
| `backend/scripts/jc_mon_stage_3_0_candidate_objectives_slice.py` | NEW · 5/5 proving slice | +250 |

Zero changes to existing endpoints or auto-suggest. Additive only.

## Artefacts

- `/app/memory/jc_artifacts/JC-MON/03-experience/3-0-candidate-objectives/candidates-from-base-doc.json`
- `/app/memory/jc_artifacts/JC-MON/03-experience/3-0-candidate-objectives/refusal-no-baseline.json`
- `/app/memory/jc_artifacts/JC-MON/03-experience/3-0-candidate-objectives/confirmation-persists-via-existing-endpoint.json`
