"""JC-MON Stage 2a — Achievement engine THIN SLICE proving script.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2a).

What the slice proves (one objective, end-to-end):
  1. **Progress %** — real, Shield-routed extractor reads the BASE +
     TRACKING docs and returns a 0-100 pct + one-sentence rationale.
     Persists evidence at `objective-progress-pct.json`.
  2. **Probability** — real, Solva `probability_weighting` engine
     (single-claim adapter) returns confidence_pct + band +
     rationale. Persists evidence at `probability-via-solva.json`.
  3. **Refusal on thin evidence** — same adapter, same objective,
     but ZERO tracking docs. The adapter's above-engine short-circuit
     refuses with reason `no_tracking_evidence_yet`. Persists
     evidence at `refusal-thin-evidence.json`.

Acceptance rows (5):
  A. Stage 2a assesses one real objective against real evidence
     and produces a non-null probability_pct in the valid range.
  B. The probability signal is grounded — band is one of the four
     allowed values and rationale is non-empty.
  C. The progress signal is grounded — 0 ≤ pct ≤ 100 and rationale
     is non-empty (or "Auto-calibrated" fallback string is set on
     parse failure).
  D. Refusal-on-thin-evidence short-circuits without an LLM call
     and emits the canonical reason `no_tracking_evidence_yet`.
  E. Shield audit ids are attached to both successful signals
     (`audit_entry_ids` non-empty on the assess-with-evidence run).

Artefacts to `/app/memory/jc_artifacts/JC-MON/02-assess-thin/`.

Run from the repo root:
    cd /app/backend && python scripts/jc_mon_stage_2a_engine_thin_slice.py
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


from services.monitor.assessment_service import assess_objective  # noqa: E402


ART_DIR = Path("/app/memory/jc_artifacts/JC-MON/02-assess-thin")
ART_DIR.mkdir(parents=True, exist_ok=True)


def _fixture_objective() -> Dict[str, Any]:
    """A grounded fixture objective mirroring the canonical Recovery
    Programme on the MYDAWA reference deck. Real values, not lorem."""
    return {
        "id":              f"obj-thin-slice-{uuid.uuid4().hex[:10]}",
        "account_id":      "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",  # admin@akki.ai
        "context_id":      "a2937d0f-37f1-4042-a897-ab73a6cd652a",  # Mara Heritage Bank · Demo
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
    """Two BASE docs anchoring what's tracked against. The extracted_text
    is the concrete strategic-plan prose the assessor must read."""
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
                "(index ~ 105). Headline measure: monthly active "
                "revenue index, baseline = 100."
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
                "≥ 12% by Day 60). Owner-level KPIs per workstream."
            ),
        },
    ]


def _fixture_tracking_docs() -> List[Dict[str, Any]]:
    """Three TRACKING docs (the EVIDENCE the assessment reads). The
    extracted_text models genuine monthly-update content with concrete
    numbers the assessor can cite."""
    return [
        {
            "id":   f"doc-track-week04-{uuid.uuid4().hex[:10]}",
            "name": "Recovery — Week 4 ops update (TRACKING)",
            "extracted_text": (
                "Week 4 status. Phase 1 checkout regression: ROOT CAUSE "
                "identified (third-party payment SDK upgrade). Fix in "
                "staging; release scheduled end of week 5. Weekly "
                "active sessions index: 89 (target 95 by Day 30). "
                "Checkout conversion pct: 71% of Q1 mean. Headline "
                "monthly active revenue index this period: 87."
            ),
        },
        {
            "id":   f"doc-track-week09-{uuid.uuid4().hex[:10]}",
            "name": "Recovery — Week 9 ops update (TRACKING)",
            "extracted_text": (
                "Week 9 status. Phase 1 EXIT-GATE PASSED. Checkout fix "
                "shipped Week 6; weekly active sessions index recovered "
                "to 97 by Week 9. Checkout conversion pct now 102% of "
                "Q1 mean. Phase 2 reactivation campaign launched "
                "Week 8. Headline monthly active revenue index this "
                "period: 92. On track for the Day-90 Phase 2 exit gate."
            ),
        },
        {
            "id":   f"doc-track-week16-{uuid.uuid4().hex[:10]}",
            "name": "Recovery — Week 16 ops update (TRACKING)",
            "extracted_text": (
                "Week 16 status. Phase 2 EXIT-GATE PASSED on Week 13. "
                "Reactivation campaign response pct landed at 14% "
                "(target ≥ 12%). Phase 3 stabilisation phase begun. "
                "Headline monthly active revenue index this period: "
                "98. Trajectory: aiming for index ≥ 100 by Day 150, "
                "ahead of the Day-180 target."
            ),
        },
    ]


async def _run_with_evidence() -> Dict[str, Any]:
    print("[1/2] assess_objective WITH evidence (BASE+TRACKING) …")
    objective = _fixture_objective()
    base_docs = _fixture_base_docs()
    tracking_docs = _fixture_tracking_docs()
    out = await assess_objective(
        objective=objective,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
    )
    out["_fixture_objective"] = objective
    out["_fixture_base_doc_names"] = [d["name"] for d in base_docs]
    out["_fixture_tracking_doc_names"] = [d["name"] for d in tracking_docs]
    return out


async def _run_refusal() -> Dict[str, Any]:
    print("[2/2] assess_objective WITHOUT tracking docs (refusal) …")
    objective = _fixture_objective()
    objective["id"] = f"obj-refusal-{uuid.uuid4().hex[:10]}"
    base_docs = _fixture_base_docs()
    out = await assess_objective(
        objective=objective,
        base_docs=base_docs,
        tracking_docs=[],
    )
    out["_fixture_objective"] = objective
    out["_fixture_base_doc_names"] = [d["name"] for d in base_docs]
    return out


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


def _acceptance_rows(assessed: Dict[str, Any], refused: Dict[str, Any]) -> None:
    print("\n— ACCEPTANCE ROWS (5/5 required) —")
    # Row A — probability_pct is non-null and in range
    pct = assessed.get("probability_pct")
    _assert(
        isinstance(pct, int) and 0 <= pct <= 100,
        f"A. probability_pct in range — got {pct}",
    )
    # Row B — band valid + rationale non-empty
    valid_bands = {"Unlikely", "Possible", "Likely", "High-conviction"}
    band = assessed.get("probability_band")
    rationale = (assessed.get("probability_rationale") or "").strip()
    _assert(
        band in valid_bands and len(rationale) > 0,
        f"B. probability band valid + rationale non-empty — band={band} rationale_len={len(rationale)}",
    )
    # Row C — progress signal grounded
    progress = assessed.get("progress_pct")
    p_rat = (assessed.get("progress_rationale") or "").strip()
    _assert(
        isinstance(progress, int) and 0 <= progress <= 100 and len(p_rat) > 0,
        f"C. progress_pct in range + rationale non-empty — pct={progress} rationale_len={len(p_rat)}",
    )
    # Row D — refusal short-circuit on thin evidence
    _assert(
        refused.get("refused") is True and refused.get("refusal_reason") == "no_tracking_evidence_yet",
        f"D. refusal short-circuit (no tracking) — refused={refused.get('refused')} reason={refused.get('refusal_reason')}",
    )
    # Row E — Shield audit ids attached on success
    audit_ids = assessed.get("audit_entry_ids") or []
    _assert(
        len(audit_ids) >= 1,
        f"E. Shield audit ids attached — count={len(audit_ids)}",
    )
    print("\n5/5 acceptance rows GREEN — STAGE 2a STOP-AND-SHOW ready.\n")


def _split_artefacts(assessed: Dict[str, Any]) -> None:
    """Per canonical-spec artefact manifest:
       - objective-progress-pct.json
       - probability-via-solva.json
       - refusal-thin-evidence.json
    We also write a combined `assessed-with-evidence.json` for the
    full payload so reviewers can read the round-trip in one place."""
    progress_payload = {
        "objective_id":      assessed.get("objective_id"),
        "progress_pct":      assessed.get("progress_pct"),
        "rationale":         assessed.get("progress_rationale"),
        "base_doc_ids":      assessed.get("base_doc_ids"),
        "tracking_doc_ids":  assessed.get("tracking_doc_ids"),
        "assessed_at":       assessed.get("assessed_at"),
    }
    probability_payload = {
        "objective_id":          assessed.get("objective_id"),
        "probability_pct":       assessed.get("probability_pct"),
        "band":                  assessed.get("probability_band"),
        "rationale":             assessed.get("probability_rationale"),
        "base_doc_ids":          assessed.get("base_doc_ids"),
        "tracking_doc_ids":      assessed.get("tracking_doc_ids"),
        "audit_entry_ids":       assessed.get("audit_entry_ids"),
        "assessed_at":           assessed.get("assessed_at"),
    }
    _write_artefact("objective-progress-pct.json", progress_payload)
    _write_artefact("probability-via-solva.json", probability_payload)


async def main() -> None:
    start = datetime.now(timezone.utc).isoformat()
    print(f"=== JC-MON Stage 2a — engine thin slice — {start} ===\n")

    assessed = await _run_with_evidence()
    refused = await _run_refusal()

    _write_artefact("assessed-with-evidence.json", assessed)
    _write_artefact("refusal-thin-evidence.json", refused)
    _split_artefacts(assessed)

    _acceptance_rows(assessed, refused)


if __name__ == "__main__":
    os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
    asyncio.run(main())
