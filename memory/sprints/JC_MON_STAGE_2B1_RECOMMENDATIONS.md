# JC-MON Stage 2b.1 — Recommendations widen

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2b).

**Closed 2026-06-25 · 5/5 acceptance rows GREEN** via
`python backend/scripts/jc_mon_stage_2b1_recommendations_slice.py`.

## What shipped

Additive widen on top of Stage 2a — `recommend_interventions(...)`
public entry, single Shield-routed LLM call per invocation, builds
on a successful `assess_objective` run without re-running it.

| Layer | What | Where |
|---|---|---|
| Adapter | `recommend_interventions(*, objective, assessment, base_docs, tracking_docs)` | `services/monitor/assessment_service.py` |
| Shield surface | `solve_v2.monitor_recommendations` | matches existing `_SOLVE_V2_SUB_RE` allow-list |
| Refusal short-circuits | (a) upstream assessment refused → carry through, zero LLM call; (b) `probability_band="High-conviction"` + `progress_pct ≥ 90` → `objective_on_track_no_intervention`, zero LLM call; (c) parser failure → `recommendations_parse_failed` with explicit `refusal_note` | `services/monitor/assessment_service.py` |

## Live evidence (real assessment + recommendations)

Real Mara Heritage Bank · Demo fixture mirroring the MYDAWA Recovery
Programme. Successful run returned 4 sequenced recommendations, each
with `title` + `rationale` + `evidence_citation` (cited tracking doc
names) + `confidence_band ∈ {Likely-helpful, Possible-helpful,
Worth-trying}`. Refusal paths returned the canonical reasons with
zero LLM call and zero Shield audit ids.

## Acceptance rows (verbatim)

```
✅ A. 2-4 recommendations on success path — got 4
✅ B. each recommendation well-formed (title + rationale + evidence_citation + confidence_band ∈ {Likely-helpful, Possible-helpful, Worth-trying})
✅ C. sequence is 1-based and dense — got [1, 2, 3, 4]
✅ D. upstream refusal carries through — refused=True reason=no_tracking_evidence_yet audit_ids=[]
✅ E. on-track short-circuits — refused=True reason=objective_on_track_no_intervention audit_ids=[]

5/5 acceptance rows GREEN — STAGE 2b.1 STOP-AND-SHOW ready.
```

## Standing-rule adherence

- **Reuse Solva engine + adapter pattern** ✅ — same shielded_call primitive as 2a.
- **Shield-routed every LLM call** ✅ — `solve_v2.monitor_recommendations` sub-surface.
- **Account/context-scoped + audit chain** ✅ — transient session mints id + carries account + context.
- **Refusal discipline (above + below)** ✅ — above-engine on upstream-refused / on-track; below-engine on parse failure.
- **Additive only on shared `tasks` entity** ✅ — no `tasks` collection touch.
- **JC-TM regression check** ✅ — none required; zero TM code path touched.

## Artefacts

- `/app/memory/jc_artifacts/JC-MON/02b1-recommendations/recommendations-success.json`
- `/app/memory/jc_artifacts/JC-MON/02b1-recommendations/recommendations-upstream-refused.json`
- `/app/memory/jc_artifacts/JC-MON/02b1-recommendations/recommendations-on-track.json`

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/services/monitor/assessment_service.py` | NEW section — `recommend_interventions` adapter + parser + prompt builder | +180 |
| `backend/services/monitor/__init__.py` | `recommend_interventions` exported | +2 |
| `backend/scripts/jc_mon_stage_2b1_recommendations_slice.py` | NEW · proving slice + 5/5 acceptance | +290 |

Zero changes to existing files outside the additive service section.
