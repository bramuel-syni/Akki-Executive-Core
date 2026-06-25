# JC-MON Stage 2a — Achievement engine THIN SLICE

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2a).

**Closed 2026-06-25 · 5/5 acceptance rows GREEN** via
`python backend/scripts/jc_mon_stage_2a_engine_thin_slice.py`.

---

## What shipped

A real on-demand assessment of one objective against real BASE +
TRACKING evidence, producing two distinct signals + an honest
refusal short-circuit, all Shield-routed.

| Layer | What | Where |
|---|---|---|
| Adapter | `assess_objective(*, objective, base_docs, tracking_docs)` — single entry-point, on-demand reassess only (no background tracker). | `services/monitor/assessment_service.py:225-318` |
| Progress signal | Shield-routed Gemini extractor at surface `solve_v2.monitor_progress`. Returns `progress_pct` 0-100 + 1-sentence rationale citing tracking doc names. Auto-calibrated fallback on parse failure (honest, not silent). | `assessment_service.py:124-181` |
| Probability signal | Solva `probability_weighting.run(...)` with the single-claim adapter from the Q4 verdict. Returns `confidence_pct` + band (Unlikely / Possible / Likely / High-conviction) + rationale. Engine handles tier-invariant retries. | `assessment_service.py:184-218` |
| Refusal short-circuit | If `tracking_docs == []` → return `refused=True, reason="no_tracking_evidence_yet"` BEFORE any Shield call. Engine-level refusal (twice-failed parse) handled below by `probability_weighting`. | `assessment_service.py:249-265` |

### Live evidence (real assessment, real Shield)

Captured in `/app/memory/jc_artifacts/JC-MON/02-assess-thin/`:

| Artefact | Real value |
|---|---|
| `objective-progress-pct.json` | `progress_pct=98` · 228-char rationale citing tracking docs |
| `probability-via-solva.json` | `probability_pct=65, band="Likely"` · 136-char rationale · 1 Shield audit id |
| `refusal-thin-evidence.json` | `refused=true, reason="no_tracking_evidence_yet"` · empty audit ids · 0 LLM calls |
| `assessed-with-evidence.json` | Combined round-trip payload for one-place review |

Objective tested: a Mara Heritage Bank · Demo "Recover Q3 monthly
active revenue to pre-Q1 baseline" fixture mirroring the MYDAWA
Recovery Programme storyboard. BASE docs: 2 (recovery plan + KPI
contract). TRACKING docs: 3 (Week 4 / Week 9 / Week 16 ops updates).

### Acceptance rows (verbatim from slice output)

```
✅ A. probability_pct in range — got 65
✅ B. probability band valid + rationale non-empty — band=Likely rationale_len=136
✅ C. progress_pct in range + rationale non-empty — pct=98 rationale_len=228
✅ D. refusal short-circuit (no tracking) — refused=True reason=no_tracking_evidence_yet
✅ E. Shield audit ids attached — count=2

5/5 acceptance rows GREEN — STAGE 2a STOP-AND-SHOW ready.
```

---

## Standing-rule adherence (checked)

- **Reuse Solva engine** — yes: `probability_weighting` called via
  `services.solva_v2.engines.probability_weighting.run()` with the
  single-claim adapter shape verified at Q4.
- **Shield-routed every LLM call** — yes: both signals go through
  `shielded_call` (`services/solva_v2/llm_adapter.py:101`). Surfaces:
  `solve_v2.monitor_progress` + `solve_v2.probability_weighting`
  (existing) — both pass the `_SOLVE_V2_SUB_RE` allow-list at
  `services/synisense/pipeline.py:78`. **Zero changes to Shield-path.**
- **Account/context-scoped + audit chain** — yes: the transient
  Monitor session mints `id` + `account_id` + `context_id` from the
  objective record (per Q4 verdict § 6); audit entries flow back via
  `audit_entry_ids`.
- **Refusal discipline** — yes: above-engine adapter short-circuits
  on empty tracking; below-adapter `probability_weighting` auto-
  calibrates on twice-failed parse with explicit "Auto-calibrated"
  rationale.
- **Additive only on shared `tasks` entity** — yes: no change to
  `tasks` collection or its handlers. New collection slot
  `objective_assessments` is reserved for Stage 2b persistence (not
  yet written; Stage 2a is the thin slice).
- **JC-TM regression check** — none required: zero touches to
  TM code paths.

---

## What's NOT in this slice (per the canonical spec's "VERTICAL
SLICE IS LAW" rule)

- **Recommendations** (`Stage 2b` widening item 1)
- **Explanation of performance** (`Stage 2b` widening item 2)
- **Extended health/status** beyond progress + probability (`Stage 2b`
  widening item 3)
- **Persistence** of assessment outcomes into a Monitor-side
  `objective_assessments` collection
- **API endpoint** wiring (this slice runs at the service-layer
  boundary; Stage 2b adds the HTTP surface)
- **Reassess trigger from "tracking doc accepted"** event (Stage 2b
  hooks the existing Journal `accept` endpoint into a reassess call)

The dispatch is explicit: "Do not build five assessment outputs at
once." Stage 2a is the thinnest real thing, end-to-end.

---

## Files touched

| File | Change |
|---|---|
| `backend/services/monitor/__init__.py` | NEW · re-exports `assess_objective` |
| `backend/services/monitor/assessment_service.py` | NEW · ~310 LOC · `assess_objective` + `_assess_progress` + `_build_probability_claim` + JSON parser |
| `backend/scripts/jc_mon_stage_2a_engine_thin_slice.py` | NEW · ~280 LOC · proving slice + 5/5 acceptance rows |

Zero changes to existing code (zero JC-TM regression risk).
