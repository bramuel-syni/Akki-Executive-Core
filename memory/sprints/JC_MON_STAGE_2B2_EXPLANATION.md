# JC-MON Stage 2b.2 — Explanation of performance widen

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2b).

**Closed 2026-06-25 · 5/5 acceptance rows GREEN** via
`python backend/scripts/jc_mon_stage_2b2_explanation_slice.py`.

## What shipped

Additive widen #2 on top of 2a + 2b.1 — `explain_performance(...)`
public entry, single Shield-routed LLM call per invocation. NARRATES
why the objective is tracking the way it is; does NOT prescribe
actions (per canonical spec quality bar — staying narrative vs 2b.1's
imperative shape).

| Surface | Where |
|---|---|
| Adapter | `services/monitor/assessment_service.py` · `explain_performance(...)` |
| Shield surface | `solve_v2.monitor_explanation` (allow-list pass) |
| Output shape | `{headline (≤ 240 chars), causes (2-4, each cited), summary_prose (≤ 600 chars, multi-sentence)}` |
| Refusal short-circuits | (a) upstream-refused carries through, zero LLM call; (b) parse failure → `explanation_parse_failed` with explicit `refusal_note` |

## Live evidence

Success path on Mara Heritage Bank · Demo Q3 recovery fixture
(headline 186 chars, 3 evidence-cited causes, multi-sentence
narrative). Upstream-refused path carried through with zero LLM
call and zero audit ids.

## Acceptance rows

```
✅ A. headline non-empty + ≤ 220 chars — len=186
✅ B. 2-4 well-formed causes — n=3 well_formed=True
✅ C. summary_prose multi-sentence + ≤ 600 chars
✅ D. upstream refusal carries — refused=True reason=no_tracking_evidence_yet
✅ E. Shield audit id attached on success — count=1

5/5 acceptance rows GREEN — STAGE 2b.2 STOP-AND-SHOW ready.
```

## Note — parser hardening

The 2b.2 build surfaced a brittle-regex defect in 2b.1's
`_parse_recommendations` (and the new `_parse_explanation` it
mirrored). The fence-strip + brace-balance parser pattern is now the
shared shape across all four monitor widens (`recommendations`,
`explanation`, `risk_surface`, `progress`). Tested live; LLM JSON
extraction is now robust to (a) markdown fence wrapping (\`\`\`json
… \`\`\`), (b) leading whitespace, (c) surrounding prose.

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/services/monitor/assessment_service.py` | NEW section — `explain_performance` + parser hardening (shared across 2b.1/2b.2/2b.3) | +180 |
| `backend/services/monitor/__init__.py` | `explain_performance` exported | +1 |
| `backend/scripts/jc_mon_stage_2b2_explanation_slice.py` | NEW · proving slice + 5/5 acceptance | +210 |
