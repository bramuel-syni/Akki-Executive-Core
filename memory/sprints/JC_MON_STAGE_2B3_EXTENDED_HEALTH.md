# JC-MON Stage 2b.3 — Extended health / status widen

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2b).

**Closed 2026-06-25 · 6/6 acceptance rows GREEN** via
`python backend/scripts/jc_mon_stage_2b3_extended_health_slice.py`.

## What shipped

Additive widen #3 on top of 2a + 2b.1 + 2b.2 — `extended_health(...)`
public entry. Composes FOUR signals:

| Signal | Computation | Source |
|---|---|---|
| `rag_status` | Deterministic from `probability_pct` (≥ 70 green / ≥ 40 amber / else red) | `_derive_rag` |
| `plan_compliance` | Deterministic from progress + probability (`ahead-of-plan` / `on-plan` / `behind-plan` / `unassessed`) | `_derive_plan_compliance` |
| `confidence_trend` | Deterministic delta vs prior assessment (`improving` ≥ +8pp / `degrading` ≤ −8pp / `stable` / `first_assessment_baseline` if no prior) | `_derive_confidence_trend` |
| `risk_surface` | Shield-routed LLM call — 1-3 named risks with severity + evidence_citation | `solve_v2.monitor_risk_surface` |

## Live evidence

Three runs:
1. With-prior — deterministic signals + LLM-narrated risks. `improving` trend confirmed (Δ +12pp).
2. First-assessment — `confidence_trend.status == "first_assessment_baseline"` confirmed.
3. Upstream-refused — deterministic signals still emit `unassessed`; risk_surface skipped (zero LLM call, zero audit ids).

## Acceptance rows

```
✅ A. rag_status valid — got amber
✅ B. plan_compliance.status valid — got ahead-of-plan
✅ C. confidence_trend valid + delta_pp int — status=improving delta_pp=12
✅ D. 1-3 well-formed risks on success — n=2
✅ E. upstream-refused emits no risk_surface LLM call — refused=True audit_ids=[]
✅ F. first-assessment baseline — status=first_assessment_baseline

6/6 acceptance rows GREEN — STAGE 2b.3 STOP-AND-SHOW ready.
```

## Stage 2b closure

With 2b.3 closed, **Stage 2b is complete in its entirety**:
- 2b.1 (recommendations) — 5/5 GREEN
- 2b.2 (explanation) — 5/5 GREEN
- 2b.3 (extended health) — 6/6 GREEN

The achievement engine now produces:
- Progress % + rationale (2a)
- Probability % + band + rationale (2a · Solva probability_weighting)
- 2-4 sequenced recommendations (2b.1)
- Headline + causes + summary prose (2b.2)
- RAG + plan compliance + confidence trend + risk surface (2b.3)

All on-demand, all Shield-routed, all account/context-scoped, all
with honest refusal short-circuits.

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/services/monitor/assessment_service.py` | NEW section — `extended_health` (3 deterministic helpers + Shield-routed risk_surface) | +200 |
| `backend/services/monitor/__init__.py` | `extended_health` exported | +2 |
| `backend/scripts/jc_mon_stage_2b3_extended_health_slice.py` | NEW · proving slice + 6/6 acceptance | +230 |
