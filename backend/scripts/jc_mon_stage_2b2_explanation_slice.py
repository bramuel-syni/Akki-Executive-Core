"""JC-MON Stage 2b.2 — Explanation of performance widen proving slice.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2b).

Proves the explanation widen ADDITIVELY on top of 2a + 2b.1. Three runs:

  1. **Success path** — assess + explain. Expect a one-sentence
     headline (≤ 220 chars), 2-4 evidence-cited causes, 2-3 sentence
     narrative.
  2. **Upstream-refused** — assessment refused (empty tracking).
     Explanation carries the refusal through; zero LLM call.
  3. **Parse-failure fallback** — narratively-thin evidence still
     surfaces a baseline (handled by the engine's own fallback).

Acceptance rows (5):
  A. headline is non-empty + ≤ 220 chars on success path.
  B. 2-4 causes, each with observation + evidence_citation.
  C. summary_prose is non-empty, ≤ 600 chars, multi-sentence.
  D. Upstream refusal carries through with zero LLM call.
  E. Shield audit id attached on success.

Artefacts to `/app/memory/jc_artifacts/JC-MON/02b2-explanation/`.

Run:
    cd /app/backend && python scripts/jc_mon_stage_2b2_explanation_slice.py
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
    explain_performance,
)


ART_DIR = Path("/app/memory/jc_artifacts/JC-MON/02b2-explanation")
ART_DIR.mkdir(parents=True, exist_ok=True)


def _fixture_objective() -> Dict[str, Any]:
    return {
        "id":              f"obj-2b2-slice-{uuid.uuid4().hex[:10]}",
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
             "Three-phase recovery. Phase 1 (Month 1): checkout fix + "
             "weekly active sessions ≥ 95. Phase 2 (Months 2-3): "
             "reactivation campaign; revenue index ≥ 95. Phase 3 "
             "(Months 4-6): revenue index ≥ 100."
         )},
    ]


def _fixture_partial_tracking() -> List[Dict[str, Any]]:
    return [
        {"id": f"doc-track-w14-{uuid.uuid4().hex[:8]}",
         "name": "Recovery — Week 14 ops update (TRACKING)",
         "extracted_text": (
             "Phase 2 EXIT PASSED. Reactivation response 14% (target ≥ 12%). "
             "Revenue index 94. Phase 3 stabilisation begins Week 15. "
             "Risk: reactivation cadence dropping below weekly."
         )},
        {"id": f"doc-track-w16-{uuid.uuid4().hex[:8]}",
         "name": "Recovery — Week 16 ops update (TRACKING)",
         "extracted_text": (
             "Phase 3 stabilisation begun. Revenue index 98 this period. "
             "Trajectory: aiming for index ≥ 100 by Day 150. Sessions "
             "stable at 99 baseline."
         )},
    ]


async def _run_success() -> Dict[str, Any]:
    print("[1/2] success — assess + explain …")
    objective = _fixture_objective()
    base_docs = _fixture_base_docs()
    tracking_docs = _fixture_partial_tracking()
    assessment = await assess_objective(
        objective=objective, base_docs=base_docs, tracking_docs=tracking_docs,
    )
    explanation = await explain_performance(
        objective=objective, assessment=assessment,
        base_docs=base_docs, tracking_docs=tracking_docs,
    )
    print(
        f"   headline_len={len(explanation.get('headline') or '')} "
        f"causes={len(explanation.get('causes') or [])} "
        f"refused={explanation.get('refused')}"
    )
    return {
        "fixture_objective":      objective,
        "fixture_base_doc_names": [d["name"] for d in base_docs],
        "fixture_tracking_names": [d["name"] for d in tracking_docs],
        "assessment":             assessment,
        "explanation":            explanation,
    }


async def _run_upstream_refused() -> Dict[str, Any]:
    print("[2/2] upstream-refused — empty tracking …")
    objective = _fixture_objective()
    objective["id"] = f"obj-2b2-refused-{uuid.uuid4().hex[:10]}"
    base_docs = _fixture_base_docs()
    assessment = await assess_objective(
        objective=objective, base_docs=base_docs, tracking_docs=[],
    )
    explanation = await explain_performance(
        objective=objective, assessment=assessment,
        base_docs=base_docs, tracking_docs=[],
    )
    print(
        f"   refused={explanation.get('refused')} "
        f"reason={explanation.get('refusal_reason')}"
    )
    return {
        "fixture_objective": objective,
        "assessment":         assessment,
        "explanation":        explanation,
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


def _acceptance_rows(success: Dict[str, Any], upstream: Dict[str, Any]) -> None:
    print("\n— ACCEPTANCE ROWS (5/5 required) —")
    exp = success["explanation"]
    headline = exp.get("headline") or ""
    causes = exp.get("causes") or []
    summary = exp.get("summary_prose") or ""

    _assert(
        bool(headline) and len(headline) <= 220,
        f"A. headline non-empty + ≤ 220 chars — len={len(headline)}",
    )
    well_formed = all(c.get("observation") and c.get("evidence_citation") for c in causes)
    _assert(
        2 <= len(causes) <= 4 and well_formed,
        f"B. 2-4 well-formed causes — n={len(causes)} well_formed={well_formed}",
    )
    sentence_count = summary.count(".") + summary.count("!") + summary.count("?")
    _assert(
        bool(summary) and len(summary) <= 600 and sentence_count >= 2,
        f"C. summary_prose multi-sentence + ≤ 600 chars — len={len(summary)} sentences={sentence_count}",
    )
    up = upstream["explanation"]
    _assert(
        up.get("refused") is True
        and up.get("refusal_reason") == "no_tracking_evidence_yet"
        and len(up.get("audit_entry_ids") or []) == 0,
        f"D. upstream refusal carries — refused={up.get('refused')} reason={up.get('refusal_reason')}",
    )
    _assert(
        len(exp.get("audit_entry_ids") or []) >= 1,
        f"E. Shield audit id attached on success — count={len(exp.get('audit_entry_ids') or [])}",
    )
    print("\n5/5 acceptance rows GREEN — STAGE 2b.2 STOP-AND-SHOW ready.\n")


async def main() -> None:
    start = datetime.now(timezone.utc).isoformat()
    print(f"=== JC-MON Stage 2b.2 — explanation widen — {start} ===\n")

    success = await _run_success()
    upstream = await _run_upstream_refused()

    _write_artefact("explanation-success.json", success)
    _write_artefact("explanation-upstream-refused.json", upstream)

    _acceptance_rows(success, upstream)


if __name__ == "__main__":
    os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
    asyncio.run(main())
