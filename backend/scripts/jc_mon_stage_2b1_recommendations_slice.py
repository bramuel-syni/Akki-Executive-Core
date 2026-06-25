"""JC-MON Stage 2b.1 — Recommendations widen proving slice.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2b).

Proves the recommendations widen ADDITIVELY on top of the Stage 2a
proven slice. Three runs:

  1. **Successful interventions** — assess one objective with real
     BASE + TRACKING evidence (Stage 2a), then call
     `recommend_interventions(...)` on the assessment. Expect 2-4
     sequenced recommendations, each with evidence_citation.

  2. **Refusal on upstream-refused assessment** — start from an
     assessment with empty tracking (`refused=true,
     no_tracking_evidence_yet`). Recommendations adapter must NOT
     make an LLM call; refusal carries through.

  3. **Refusal on objective already-on-track** — synthesise an
     assessment with `probability_band="High-conviction"` and
     `progress_pct=95`. Recommendations adapter must short-circuit
     with reason `objective_on_track_no_intervention`. No LLM call.

Acceptance rows (5):
  A. 2-4 recommendations returned in the successful path.
  B. Each recommendation is well-formed (title + rationale +
     evidence_citation + confidence_band in the allowed set).
  C. `sequence` is 1-based and dense (1, 2, … N).
  D. Upstream-refused assessment carries through → zero LLM calls,
     refusal reason preserved.
  E. On-track objective short-circuits with the canonical reason.

Artefacts to `/app/memory/jc_artifacts/JC-MON/02b1-recommendations/`.

Run from the repo root:
    cd /app/backend && python scripts/jc_mon_stage_2b1_recommendations_slice.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")


from services.monitor.assessment_service import (  # noqa: E402
    assess_objective,
    recommend_interventions,
)


ART_DIR = Path("/app/memory/jc_artifacts/JC-MON/02b1-recommendations")
ART_DIR.mkdir(parents=True, exist_ok=True)


# ---- fixtures (mirror 2a slice for continuity) ----

def _fixture_objective() -> Dict[str, Any]:
    return {
        "id":              f"obj-2b1-slice-{uuid.uuid4().hex[:10]}",
        "account_id":      "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",
        "context_id":      "a2937d0f-37f1-4042-a897-ab73a6cd652a",
        "kind":            "objective",
        "title":           "Recover Q3 monthly active revenue to pre-Q1 baseline",
        "description":     (
            "After a −5.5% MoM revenue contraction triggered by a"
            " checkout regression, recover monthly active digital"
            " revenue back to the pre-Q1 baseline within two quarters."
        ),
        "target_metric":   "monthly_active_revenue_index",
        "target_value":    "Index ≥ 100 (Q1 baseline = 100) within 180 days",
        "due_date":        "2026-12-31",
        "status":          "active",
    }


def _fixture_base_docs() -> List[Dict[str, Any]]:
    return [
        {
            "id":   f"doc-base-recovery-plan-{uuid.uuid4().hex[:10]}",
            "name": "MYDAWA Recovery Programme — Strategic Plan (BASE)",
            "extracted_text": (
                "Recovery Plan — six months in three phases.\n"
                "Phase 1 (Month 1): fix checkout regression and "
                "restore weekly active sessions to pre-Q1 baseline. "
                "Exit gate: weekly_active_sessions_index ≥ 95.\n"
                "Phase 2 (Months 2-3): re-engage lapsed customers via "
                "targeted reactivation and restore monthly active "
                "revenue to ≥ 95% of baseline. Exit gate: revenue index ≥ 95.\n"
                "Phase 3 (Months 4-6): grow revenue index above 100 "
                "and stabilise. Floor scenario: only Phase 1 lands "
                "(index ~ 92). Plan scenario: all phases succeed "
                "(index ~ 105)."
            ),
        },
        {
            "id":   f"doc-base-kpi-contract-{uuid.uuid4().hex[:10]}",
            "name": "KPI Contract — Eight Workstreams (BASE)",
            "extracted_text": (
                "Headline number for the board: monthly_active_revenue_index, "
                "baseline 100, target ≥ 100 by Day 180. Lead indicators "
                "for the COO: weekly_active_sessions_index (target ≥ 95 "
                "by Day 30), checkout_conversion_pct (target ≥ Q1 mean "
                "by Day 30), reactivation_email_response_pct (target "
                "≥ 12% by Day 60)."
            ),
        },
    ]


def _fixture_partial_tracking() -> List[Dict[str, Any]]:
    """Three tracking docs but with a meaningful gap: Phase-2 exit is
    PASSED but Phase-3 stabilisation is still in flight. Plenty of room
    for interventions to recommend."""
    return [
        {
            "id":   f"doc-track-week04-{uuid.uuid4().hex[:10]}",
            "name": "Recovery — Week 4 ops update (TRACKING)",
            "extracted_text": (
                "Week 4: Phase 1 checkout regression ROOT-CAUSED; fix in "
                "staging; release scheduled Week 5. Weekly active "
                "sessions index 89. Checkout conversion pct 71% of Q1 "
                "mean. Headline revenue index 87."
            ),
        },
        {
            "id":   f"doc-track-week09-{uuid.uuid4().hex[:10]}",
            "name": "Recovery — Week 9 ops update (TRACKING)",
            "extracted_text": (
                "Week 9: Phase 1 EXIT PASSED. Checkout shipped Week 6. "
                "Sessions index 97. Conversion 102% of Q1. Phase 2 "
                "reactivation campaign launched Week 8. Headline "
                "revenue index 92. On track for the Day-90 Phase 2 "
                "exit gate."
            ),
        },
        {
            "id":   f"doc-track-week14-{uuid.uuid4().hex[:10]}",
            "name": "Recovery — Week 14 ops update (TRACKING)",
            "extracted_text": (
                "Week 14: Phase 2 EXIT PASSED. Reactivation response "
                "pct 14% (target ≥ 12%). Headline revenue index 94. "
                "Phase 3 stabilisation begins Week 15. Risk: "
                "reactivation campaign frequency dropping below "
                "weekly cadence; team capacity stretched. Headline "
                "still below 100 target by 6 points."
            ),
        },
    ]


# ---- runs ----

async def _run_success() -> Dict[str, Any]:
    print("[1/3] success path — assess + recommend …")
    objective = _fixture_objective()
    base_docs = _fixture_base_docs()
    tracking_docs = _fixture_partial_tracking()
    assessment = await assess_objective(
        objective=objective,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
    )
    print(
        f"   assessment: progress={assessment.get('progress_pct')} "
        f"probability={assessment.get('probability_pct')} "
        f"band={assessment.get('probability_band')}"
    )
    recommendations = await recommend_interventions(
        objective=objective,
        assessment=assessment,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
    )
    print(
        f"   recs: count={len(recommendations.get('recommendations') or [])} "
        f"refused={recommendations.get('refused')}"
    )
    return {
        "fixture_objective":       objective,
        "fixture_base_doc_names":  [d["name"] for d in base_docs],
        "fixture_tracking_names":  [d["name"] for d in tracking_docs],
        "assessment":              assessment,
        "recommendations":         recommendations,
    }


async def _run_upstream_refused() -> Dict[str, Any]:
    print("[2/3] upstream-refused path — no tracking docs …")
    objective = _fixture_objective()
    objective["id"] = f"obj-2b1-refused-upstream-{uuid.uuid4().hex[:10]}"
    base_docs = _fixture_base_docs()
    assessment = await assess_objective(
        objective=objective,
        base_docs=base_docs,
        tracking_docs=[],
    )
    print(f"   assessment.refused={assessment.get('refused')}")
    recommendations = await recommend_interventions(
        objective=objective,
        assessment=assessment,
        base_docs=base_docs,
        tracking_docs=[],
    )
    print(
        f"   recs.refused={recommendations.get('refused')} "
        f"reason={recommendations.get('refusal_reason')}"
    )
    return {
        "fixture_objective": objective,
        "assessment":        assessment,
        "recommendations":   recommendations,
    }


async def _run_on_track() -> Dict[str, Any]:
    print("[3/3] on-track path — synthesised High-conviction assessment …")
    objective = _fixture_objective()
    objective["id"] = f"obj-2b1-on-track-{uuid.uuid4().hex[:10]}"
    base_docs = _fixture_base_docs()
    tracking_docs = _fixture_partial_tracking()
    # Synthesise the on-track assessment directly — does not call the
    # engine. Tests the recommend_interventions short-circuit.
    synthetic_assessment = {
        "objective_id":           objective["id"],
        "refused":                False,
        "refusal_reason":         None,
        "progress_pct":           96,
        "progress_rationale":     "Synthetic: objective already at index 96 per Week-16 tracking.",
        "probability_pct":        90,
        "probability_band":       "High-conviction",
        "probability_rationale":  "Synthetic: high-conviction trajectory based on Phase-2 + Phase-3 indicators.",
        "base_doc_ids":           [d["id"] for d in base_docs],
        "tracking_doc_ids":       [d["id"] for d in tracking_docs],
        "audit_entry_ids":        [],
        "assessed_at":            datetime.now(timezone.utc).isoformat(),
    }
    recommendations = await recommend_interventions(
        objective=objective,
        assessment=synthetic_assessment,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
    )
    print(
        f"   recs.refused={recommendations.get('refused')} "
        f"reason={recommendations.get('refusal_reason')}"
    )
    return {
        "fixture_objective": objective,
        "assessment":        synthetic_assessment,
        "recommendations":   recommendations,
    }


def _write_artefact(name: str, payload: Dict[str, Any]) -> Path:
    path = ART_DIR / name
    path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"  → {path}")
    return path


def _assert(cond: bool, msg: str) -> None:
    label = "✅" if cond else "❌"
    print(f"  {label} {msg}")
    if not cond:
        raise AssertionError(msg)


def _acceptance_rows(
    success: Dict[str, Any],
    upstream: Dict[str, Any],
    on_track: Dict[str, Any],
) -> None:
    print("\n— ACCEPTANCE ROWS (5/5 required) —")

    recs = success["recommendations"].get("recommendations") or []
    # Row A — 2-4 recommendations on the successful path
    _assert(
        2 <= len(recs) <= 4,
        f"A. 2-4 recommendations on success path — got {len(recs)}",
    )
    # Row B — each well-formed
    valid_bands = {"Likely-helpful", "Possible-helpful", "Worth-trying"}
    well_formed = all(
        (r.get("title") and r.get("rationale") and r.get("evidence_citation")
         and r.get("confidence_band") in valid_bands)
        for r in recs
    )
    _assert(
        well_formed,
        f"B. each recommendation well-formed (title + rationale + evidence_citation + confidence_band ∈ {valid_bands})",
    )
    # Row C — sequence 1-based and dense
    sequences = [r["sequence"] for r in recs]
    dense = sequences == list(range(1, len(recs) + 1))
    _assert(
        dense,
        f"C. sequence is 1-based and dense — got {sequences}",
    )
    # Row D — upstream-refused carries through; zero audit ids
    upstream_recs = upstream["recommendations"]
    _assert(
        upstream_recs.get("refused") is True
        and upstream_recs.get("refusal_reason") == "no_tracking_evidence_yet"
        and len(upstream_recs.get("audit_entry_ids") or []) == 0,
        f"D. upstream refusal carries through — refused={upstream_recs.get('refused')} "
        f"reason={upstream_recs.get('refusal_reason')} "
        f"audit_ids={upstream_recs.get('audit_entry_ids')}",
    )
    # Row E — on-track short-circuits with canonical reason
    on_track_recs = on_track["recommendations"]
    _assert(
        on_track_recs.get("refused") is True
        and on_track_recs.get("refusal_reason") == "objective_on_track_no_intervention"
        and len(on_track_recs.get("audit_entry_ids") or []) == 0,
        f"E. on-track short-circuits — refused={on_track_recs.get('refused')} "
        f"reason={on_track_recs.get('refusal_reason')} "
        f"audit_ids={on_track_recs.get('audit_entry_ids')}",
    )

    print("\n5/5 acceptance rows GREEN — STAGE 2b.1 STOP-AND-SHOW ready.\n")


async def main() -> None:
    start = datetime.now(timezone.utc).isoformat()
    print(f"=== JC-MON Stage 2b.1 — recommendations widen — {start} ===\n")

    success = await _run_success()
    upstream = await _run_upstream_refused()
    on_track = await _run_on_track()

    _write_artefact("recommendations-success.json", success)
    _write_artefact("recommendations-upstream-refused.json", upstream)
    _write_artefact("recommendations-on-track.json", on_track)

    _acceptance_rows(success, upstream, on_track)


if __name__ == "__main__":
    os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
    asyncio.run(main())
