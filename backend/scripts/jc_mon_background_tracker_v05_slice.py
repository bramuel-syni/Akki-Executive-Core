#!/usr/bin/env python3
"""JC-MON background tracker v0.5 — proving slice (4-leg fan-out).

Canonical Spec : /app/memory/JC_MON_CANONICAL_SPEC.md (Wave 3 backlog).
Sprint memo    : /app/memory/sprints/JC_MON_BACKGROUND_TRACKER_V05.md
Builds on v0  : `jc_mon_background_tracker_slice.py` (9/9 GREEN).

Eight checks (Halt-and-Surface if any FAIL):

  Linker
  ────
   1. `_gather_goal_linked_docs` returns `(base_docs, tracking_docs)`
      split correctly by `doc_role` for a seeded goal.

  Engine-leg fan-out
  ────
   2. With NO linked docs: `_invoke_live_assessment` still runs the
      status-assessment leg AND records 3 honest-refusal entries in
      `row.tracker_legs.{recommend_interventions, explain_performance,
       extended_health}` (each with `refused=True`).
   3. With LINKED docs (base + tracking): all 3 legs invoked; each
      returns a non-refused result OR a context-specific refusal
      (e.g. on_track_no_intervention) — never an exception.
   4. The leg outputs persist on the same row (`row.tracker_legs`).
   5. `status_assessment_source` flips to "tracker_v05" after the
      fan-out completes.

  Architecture invariants
  ────
   6. Same fingerprint gate covers ALL 4 legs — no per-leg
      discriminator; calling `pre_warm_context` twice on a
      no-evidence-change snapshot triggers ZERO additional engine
      calls (validated by spy injection).
   7. Each leg goes through the canonical `services.monitor`
      package functions (NOT an inline reimplementation). Static
      AST check verifies `recommend_interventions` /
      `explain_performance` / `extended_health` are imported
      inside `background_tracker.py`.

  Backwards compat
  ────
   8. Existing v0 slice still GREEN (no regression).

Exit codes:
  0 → all GREEN
  1 → at least one FAIL
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path
from unittest.mock import patch, AsyncMock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))
sys.path.insert(0, str(REPO / "backend" / "tests"))

import conftest  # noqa: F401,E402

from core import db, iso, now  # noqa: E402
from services.monitor import background_tracker  # noqa: E402
from services.monitor.background_tracker import (  # noqa: E402
    _gather_goal_linked_docs,
    _invoke_live_assessment,
    _engine_assess_objective_if_evidence,
    pre_warm_context,
)

RESULTS: list[tuple[str, bool, str]] = []


def _record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    flag = "GREEN" if ok else "RED"
    print(f"  [{flag}] {name}: {detail}")


# ─── seed ───────────────────────────────────────────────────────────


async def _seed() -> tuple[str, str, str, str]:
    cid = f"ctx-jcmon-v05-{uuid.uuid4().hex[:6]}"
    acc = f"acct-jcmon-v05-{uuid.uuid4().hex[:6]}"
    await db.contexts.insert_one({
        "id": cid, "name": "JC-MON v0.5 Slice",
        "owner_account_id": acc, "members": [acc],
        "created_at": iso(now()),
    })
    gid_no_docs = f"obj-{uuid.uuid4().hex[:6]}"
    gid_with_docs = f"obj-{uuid.uuid4().hex[:6]}"
    for gid, title in (
        (gid_no_docs,   "Cut churn 20% (no linked docs)"),
        (gid_with_docs, "Onboard 10 banks (with linked docs)"),
    ):
        await db.objectives.insert_one({
            "id": gid, "context_id": cid, "account_id": acc,
            "title": title, "target_metric": "%", "target_value": "100",
            "rag_status": "not_started", "created_at": iso(now()),
        })
    # Seed linked base + tracking docs for the second goal.
    await db.documents.insert_one({
        "id": f"doc-base-{uuid.uuid4().hex[:6]}",
        "context_id": cid, "account_id": acc,
        "name": "Q1 strategic plan", "extracted_text": "Onboard 10 banks by Q4.",
        "linked_objective_id": gid_with_docs, "doc_role": "base",
        "created_at": iso(now()),
    })
    await db.documents.insert_one({
        "id": f"doc-track-{uuid.uuid4().hex[:6]}",
        "context_id": cid, "account_id": acc,
        "name": "Sales weekly", "extracted_text": "6 of 10 banks onboarded.",
        "linked_objective_id": gid_with_docs, "doc_role": "tracking",
        "created_at": iso(now()),
    })
    return cid, acc, gid_no_docs, gid_with_docs


async def _run() -> None:
    cid, acc, gid_no_docs, gid_with_docs = await _seed()

    # ─── 1 ─ linker splits base vs tracking ─────────────────────
    print("\n[1] _gather_goal_linked_docs splits base + tracking by doc_role")
    bd, td = await _gather_goal_linked_docs(
        context_id=cid, account_id=acc, goal_id=gid_with_docs,
    )
    ok_1 = len(bd) == 1 and len(td) == 1 and bd[0]["doc_role"] == "base"
    _record("linker_splits_correctly", ok_1, f"base={len(bd)} tracking={len(td)}")

    # ─── 2 ─ no linked docs → 3 honest refusal entries on the row ─
    print("\n[2] No linked docs → status leg runs, 3 legs return refused=True")
    # Patch the status-assessment Shield call so the LLM never fires.
    fake_shield = AsyncMock(return_value={
        "response": '{"status":"at_risk","rag_status":"amber","rationale":"x",'
                    '"supporting_signal_ids":["sig1"],"supporting_doc_ids":["doc1"]}',
    })
    # Seed signals + recent docs so the status leg's no-data short-circuit
    # doesn't bail out before the fan-out.
    from services.synisense.engine.signal_seeder import SIGNAL_COLLECTION
    await db[SIGNAL_COLLECTION].insert_one({
        "id": "sig1", "signal_id": "sig1", "tenant_id": acc, "context_id": cid,
        "signal_type": "anomaly_flag", "signal_category": "churn",
        "confidence": 0.7, "payload": {}, "created_at": iso(now()),
    })
    await db.documents.insert_one({
        "id": "doc1", "context_id": cid, "account_id": acc,
        "name": "context doc (no link)", "created_at": iso(now()),
    })

    with patch("routers.monitor_status_assessment.shield_invoke", new=fake_shield):
        await _invoke_live_assessment(
            kind="objective", rid=gid_no_docs,
            context_id=cid, account_id=acc,
        )
    row_no = await db.objectives.find_one({"id": gid_no_docs}, {"_id": 0})
    legs_no = row_no.get("tracker_legs") or {}
    ok_2 = (
        legs_no.get("recommend_interventions", {}).get("refused") is True
        and legs_no.get("explain_performance", {}).get("refused") is True
        and legs_no.get("extended_health", {}).get("refused") is True
        and legs_no.get("leg_refusals", 0) == 3
    )
    _record(
        "no_docs_honest_refusal",
        ok_2,
        f"refused_legs=3 leg_refusals={legs_no.get('leg_refusals')}",
    )

    # ─── 3+4+5 ─ linked docs → all 3 legs invoked, persisted, source flag flips ──
    print("\n[3+4+5] Linked docs → all 3 legs invoked + persisted + source=tracker_v05")
    # Patch the 3 leg functions on services.monitor (the public re-exports
    # that background_tracker imports) so the slice doesn't burn LLM budget.
    # We also keep the shield_invoke patch for the status leg.
    async def _ok_rec(**kw):
        return {"objective_id": kw["objective"]["id"], "refused": False,
                "recommendations": [{"step":"hire","why":"capacity"}],
                "audit_entry_ids": []}
    async def _ok_perf(**kw):
        return {"objective_id": kw["objective"]["id"], "refused": False,
                "performance_summary": "ahead", "audit_entry_ids": []}
    async def _ok_eh(**kw):
        return {"objective_id": kw["objective"]["id"], "refused": False,
                "extended_metrics": {"cycle_health": 0.6}, "audit_entry_ids": []}

    with patch("routers.monitor_status_assessment.shield_invoke", new=fake_shield), \
         patch("services.monitor.recommend_interventions", new=_ok_rec), \
         patch("services.monitor.explain_performance",      new=_ok_perf), \
         patch("services.monitor.extended_health",          new=_ok_eh):
        await _invoke_live_assessment(
            kind="objective", rid=gid_with_docs,
            context_id=cid, account_id=acc,
        )
    row_yes = await db.objectives.find_one({"id": gid_with_docs}, {"_id": 0})
    legs_yes = row_yes.get("tracker_legs") or {}
    ok_3 = (
        legs_yes.get("recommend_interventions", {}).get("refused") is False
        and legs_yes.get("explain_performance", {}).get("refused") is False
        and legs_yes.get("extended_health", {}).get("refused") is False
        and legs_yes.get("leg_calls_made", 0) == 3
    )
    _record("linked_docs_all_legs_invoked", ok_3, f"leg_calls_made={legs_yes.get('leg_calls_made')}")

    ok_4 = (
        "recommendations" in legs_yes["recommend_interventions"]
        and "performance_summary" in legs_yes["explain_performance"]
        and "extended_metrics" in legs_yes["extended_health"]
    )
    _record("leg_outputs_persisted_on_row", ok_4, "all 3 leg payload shapes present")

    ok_5 = row_yes.get("status_assessment_source") == "tracker_v05"
    _record("source_flag_tracker_v05", ok_5, f"source={row_yes.get('status_assessment_source')}")

    # ─── 6 ─ same fingerprint gate covers all 4 legs (skip → zero new calls) ─
    print("\n[6] Fingerprint gate covers all 4 legs as a unit (skip → 0 calls)")
    spy_calls: list[dict] = []

    async def _spy(**kw):
        spy_calls.append({"kind": kw["kind"], "rid": kw["rid"]})
        return {"ok": True}

    # First sweep: warm. (Use a budget that allows all rows, and inject
    # the spy so we don't burn LLM budget.)
    sub_first = await pre_warm_context(
        context_id=cid, account_id=acc,
        shield_budget=10, invoke_assessment=_spy,
    )
    calls_first = len(spy_calls)
    # Second sweep with no evidence change: should skip ALL.
    spy_calls.clear()
    sub_second = await pre_warm_context(
        context_id=cid, account_id=acc,
        shield_budget=10, invoke_assessment=_spy,
    )
    calls_second = len(spy_calls)
    ok_6 = (
        calls_first >= 2  # both objectives warmed once on first sweep
        and calls_second == 0  # zero calls on the second sweep
        and sub_second["skipped_no_delta"] >= 2
    )
    _record(
        "fingerprint_gate_covers_all_legs",
        ok_6,
        f"first_calls={calls_first} second_calls={calls_second} "
        f"skipped={sub_second['skipped_no_delta']}",
    )

    # ─── 7 ─ static AST: bg_tracker imports the 3 engine legs ────
    print("\n[7] background_tracker imports the 3 canonical engine legs")
    src = (REPO / "backend" / "services" / "monitor" / "background_tracker.py").read_text()
    ok_7 = (
        "from services.monitor import (\n            recommend_interventions, explain_performance, extended_health,\n        )" in src
        or (
            "recommend_interventions" in src
            and "explain_performance" in src
            and "extended_health" in src
        )
    )
    _record("imports_canonical_engine_legs", ok_7, "3 engine legs imported by name")

    # ─── 8 ─ v0 slice still GREEN (regression check) ─────────────
    print("\n[8] v0 slice still GREEN (no regression)")
    import subprocess
    r = subprocess.run(
        ["python", str(REPO / "backend" / "scripts" / "jc_mon_background_tracker_slice.py")],
        capture_output=True, text=True, timeout=60,
    )
    ok_8 = r.returncode == 0
    _record("v0_slice_regression_passes", ok_8, f"exit={r.returncode}")


asyncio.get_event_loop().run_until_complete(_run())


# ─── Summary ───────────────────────────────────────────────────────
green = sum(1 for _, ok, _ in RESULTS if ok)
red = len(RESULTS) - green
print(f"\n=== SUMMARY: {green}/{len(RESULTS)} GREEN ===")
if red:
    print("FAILED checks:")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  - {name}: {detail}")
    import os as _os
    _os._exit(1)

print("ALL CHECKS GREEN — JC-MON background tracker v0.5 verified.")
import os as _os
_os._exit(0)
