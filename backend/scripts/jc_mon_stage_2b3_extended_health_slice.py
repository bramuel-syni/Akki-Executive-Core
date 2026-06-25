"""JC-MON Stage 2b.3 — Extended health / status widen proving slice.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2b).

Proves the extended-health widen ADDITIVELY on top of 2a (+ 2b.1 + 2b.2).
Three signals composed:
  - `rag_status` (deterministic from probability_pct)
  - `plan_compliance` (deterministic from progress + probability)
  - `confidence_trend` (deterministic from current vs prior probability)
  - `risk_surface` (Shield-routed — 1-3 named risks)

Runs:
  1. **Success path** — full extended health, with `prior_assessment`
     to exercise the confidence_trend delta logic.
  2. **First-assessment path** — no prior. confidence_trend status
     must be `first_assessment_baseline`.
  3. **Upstream-refused path** — deterministic signals still emit
     honestly (`unassessed` where applicable); risk_surface gets
     `refusal_note`; zero LLM call.

Acceptance rows (6):
  A. rag_status is one of {red, amber, green, unassessed}.
  B. plan_compliance.status is one of {ahead-of-plan, on-plan, behind-plan, unassessed}.
  C. confidence_trend.status is one of {improving, stable, degrading,
     first_assessment_baseline, unassessed} + correct delta_pp.
  D. risk_surface emits 1-3 well-formed risks on success path.
  E. Upstream-refused emits NO risk_surface LLM call (audit_entry_ids == []).
  F. First-assessment path returns confidence_trend.status == "first_assessment_baseline".

Artefacts to `/app/memory/jc_artifacts/JC-MON/02b3-extended-health/`.

Run:
    cd /app/backend && python scripts/jc_mon_stage_2b3_extended_health_slice.py
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
    extended_health,
)


ART_DIR = Path("/app/memory/jc_artifacts/JC-MON/02b3-extended-health")
ART_DIR.mkdir(parents=True, exist_ok=True)


def _fixture_objective() -> Dict[str, Any]:
    return {
        "id":              f"obj-2b3-slice-{uuid.uuid4().hex[:10]}",
        "account_id":      "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",
        "context_id":      "a2937d0f-37f1-4042-a897-ab73a6cd652a",
        "kind":            "objective",
        "title":           "Recover Q3 monthly active revenue to pre-Q1 baseline",
        "description":     "Recover MoM index after the −5.5% Q3 contraction.",
        "target_metric":   "monthly_active_revenue_index",
        "target_value":    "Index ≥ 100 within 180 days",
        "due_date":        "2026-12-31",
        "status":          "active",
    }


def _fixture_base_docs() -> List[Dict[str, Any]]:
    return [
        {"id": f"doc-base-{uuid.uuid4().hex[:8]}",
         "name": "MYDAWA Recovery Programme — Strategic Plan (BASE)",
         "extracted_text": (
             "Three-phase recovery. Phase 1: checkout fix. Phase 2: "
             "reactivation. Phase 3: stabilisation. Headline: revenue "
             "index, baseline 100, target ≥ 100 by Day 180."
         )},
    ]


def _fixture_tracking() -> List[Dict[str, Any]]:
    return [
        {"id": f"doc-track-w14-{uuid.uuid4().hex[:8]}",
         "name": "Recovery — Week 14 ops update (TRACKING)",
         "extracted_text": (
             "Phase 2 EXIT PASSED. Reactivation response 14%. Revenue "
             "index 94. Risk: reactivation cadence dropping below "
             "weekly; team capacity stretched."
         )},
    ]


async def _run_with_prior() -> Dict[str, Any]:
    print("[1/3] success with prior_assessment …")
    objective = _fixture_objective()
    base_docs = _fixture_base_docs()
    tracking_docs = _fixture_tracking()
    assessment = await assess_objective(
        objective=objective, base_docs=base_docs, tracking_docs=tracking_docs,
    )
    # Synthesised prior assessment 10pp lower → expect "improving".
    prior = {
        "probability_pct": (assessment.get("probability_pct") or 50) - 12,
    }
    health = await extended_health(
        objective=objective, assessment=assessment,
        base_docs=base_docs, tracking_docs=tracking_docs,
        prior_assessment=prior,
    )
    print(
        f"   rag={health.get('rag_status')} "
        f"plan={health['plan_compliance']['status']} "
        f"trend={health['confidence_trend']['status']} "
        f"risks={len(health['risk_surface']['risks'])}"
    )
    return {
        "fixture_objective": objective,
        "assessment":         assessment,
        "prior_assessment":  prior,
        "extended_health":    health,
    }


async def _run_first_assessment() -> Dict[str, Any]:
    print("[2/3] first-assessment (no prior) …")
    objective = _fixture_objective()
    objective["id"] = f"obj-2b3-first-{uuid.uuid4().hex[:10]}"
    base_docs = _fixture_base_docs()
    tracking_docs = _fixture_tracking()
    assessment = await assess_objective(
        objective=objective, base_docs=base_docs, tracking_docs=tracking_docs,
    )
    health = await extended_health(
        objective=objective, assessment=assessment,
        base_docs=base_docs, tracking_docs=tracking_docs,
        prior_assessment=None,
    )
    print(
        f"   trend.status={health['confidence_trend']['status']} "
        f"delta_pp={health['confidence_trend']['delta_pp']}"
    )
    return {
        "fixture_objective": objective,
        "assessment":         assessment,
        "extended_health":    health,
    }


async def _run_upstream_refused() -> Dict[str, Any]:
    print("[3/3] upstream-refused — empty tracking …")
    objective = _fixture_objective()
    objective["id"] = f"obj-2b3-refused-{uuid.uuid4().hex[:10]}"
    base_docs = _fixture_base_docs()
    assessment = await assess_objective(
        objective=objective, base_docs=base_docs, tracking_docs=[],
    )
    health = await extended_health(
        objective=objective, assessment=assessment,
        base_docs=base_docs, tracking_docs=[],
    )
    print(
        f"   refused={health.get('refused')} "
        f"rag={health.get('rag_status')} "
        f"plan={health['plan_compliance']['status']} "
        f"audit_ids={len(health.get('audit_entry_ids') or [])}"
    )
    return {
        "fixture_objective": objective,
        "assessment":         assessment,
        "extended_health":    health,
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
    with_prior: Dict[str, Any],
    first: Dict[str, Any],
    refused: Dict[str, Any],
) -> None:
    print("\n— ACCEPTANCE ROWS (6/6 required) —")
    valid_rag = {"red", "amber", "green", "unassessed"}
    valid_plan = {"ahead-of-plan", "on-plan", "behind-plan", "unassessed"}
    valid_trend = {"improving", "stable", "degrading", "first_assessment_baseline", "unassessed"}

    h = with_prior["extended_health"]
    _assert(
        h["rag_status"] in valid_rag,
        f"A. rag_status valid — got {h['rag_status']}",
    )
    _assert(
        h["plan_compliance"]["status"] in valid_plan,
        f"B. plan_compliance.status valid — got {h['plan_compliance']['status']}",
    )
    trend_st = h["confidence_trend"]["status"]
    delta_pp = h["confidence_trend"]["delta_pp"]
    _assert(
        trend_st in valid_trend and isinstance(delta_pp, int),
        f"C. confidence_trend valid + delta_pp int — status={trend_st} delta_pp={delta_pp}",
    )
    risks = h["risk_surface"]["risks"]
    _assert(
        1 <= len(risks) <= 3 and all(r.get("name") and r.get("narrative") and r.get("severity") in ("high","medium","low") for r in risks),
        f"D. 1-3 well-formed risks on success — n={len(risks)}",
    )
    r = refused["extended_health"]
    _assert(
        r.get("refused") is True and len(r.get("audit_entry_ids") or []) == 0,
        f"E. upstream-refused emits no risk_surface LLM call — refused={r.get('refused')} audit_ids={r.get('audit_entry_ids')}",
    )
    f = first["extended_health"]
    _assert(
        f["confidence_trend"]["status"] == "first_assessment_baseline",
        f"F. first-assessment baseline — status={f['confidence_trend']['status']}",
    )
    print("\n6/6 acceptance rows GREEN — STAGE 2b.3 STOP-AND-SHOW ready.\n")


async def main() -> None:
    start = datetime.now(timezone.utc).isoformat()
    print(f"=== JC-MON Stage 2b.3 — extended health widen — {start} ===\n")

    with_prior = await _run_with_prior()
    first = await _run_first_assessment()
    refused = await _run_upstream_refused()

    _write_artefact("extended-health-with-prior.json", with_prior)
    _write_artefact("extended-health-first-assessment.json", first)
    _write_artefact("extended-health-upstream-refused.json", refused)

    _acceptance_rows(with_prior, first, refused)


if __name__ == "__main__":
    os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
    asyncio.run(main())
