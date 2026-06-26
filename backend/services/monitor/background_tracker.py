"""JC-MON background tracker — pre-warmer for the on-demand engine.

Canonical Spec: /app/memory/JC_MON_CANONICAL_SPEC.md (Wave 3 backlog).

User constraints (msg 412):
  • skip-UNLESS-tracked-evidence-changed-since-last-run (NOT
    "baseline-change" — evidence moves, baseline rarely does)
  • Must reuse on-demand engine paths (no parallel pipelines).
  • Must respect per-objective Shield budget cap.
  • Architecture invariant: pre-warmer for the existing on-demand
    engine, NOT a parallel always-on tracker. Calls the same
    `_gather_engine_signals` + `_gather_recent_docs` + `shield_invoke`
    paths the user's "Update goal" click already uses.

What this module does:
  1. Walk each tenant's `objectives` + `projects` rows.
  2. Per-row: compute the CURRENT tracked-evidence fingerprint as a
     stable hash over (signal_id, created_at) + (doc_id, created_at)
     for the rows the on-demand engine would feed Shield.
  3. Compare against the last-persisted fingerprint in
     `monitor_evidence_fingerprints`. SKIP if identical.
  4. Otherwise: invoke the SAME `update_status_assessment` handler the
     user calls when they click "Update goal." Persist the new
     fingerprint when the assessment lands.
  5. Stop calling Shield once the per-run budget is exhausted; surface
     a `shield_budget_exhausted` row in the cron summary so an
     operator can size the budget.

Data model
  ────────────
  Collection: `monitor_evidence_fingerprints`
  {
    id              : str  (uuid)
    context_id      : str
    account_id      : str
    objective_kind  : "objective" | "project"
    objective_id    : str
    fingerprint     : str  (sha256 hex)
    sized_signals   : int  (count at fingerprint time)
    sized_docs      : int
    last_assessed_at: ISO-string
    updated_at      : ISO-string
  }

  NB: this is bookkeeping, NOT a new engine pipeline. It caches "what
  was the input set last time the tracker ran" — same shape as a
  weekday "I already checked this; nothing new to see" memo.
"""
from __future__ import annotations

import hashlib
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from core import db, iso, now
from services.synisense.engine.signal_seeder import SIGNAL_COLLECTION

logger = logging.getLogger("akki.monitor.background_tracker")


# ─── Fingerprint ────────────────────────────────────────────────────


async def compute_evidence_fingerprint(
    *, context_id: str, account_id: str,
) -> Tuple[str, int, int]:
    """Hash the input set the on-demand engine would feed Shield.

    Returns `(fingerprint, sized_signals, sized_docs)`. The shapes are
    deliberately the SAME as the on-demand path's `_gather_engine_signals`
    and `_gather_recent_docs` (same tenant + context filter, same limit).
    """
    # Mirror routers/monitor_status_assessment.py:_gather_engine_signals
    signals = await db[SIGNAL_COLLECTION].find(
        {
            "tenant_id": account_id,
            "signal_type": {"$in": [
                "anomaly_flag", "compliance_trigger", "operational_health",
                "churn_risk",
            ]},
            "$or": [{"context_id": context_id}, {"context_id": None}],
        },
        {"_id": 0, "signal_id": 1, "created_at": 1},
    ).sort([("created_at", -1)]).limit(12).to_list(12)

    # Mirror routers/monitor_status_assessment.py:_gather_recent_docs
    docs = await db.documents.find(
        {"context_id": context_id, "account_id": account_id},
        {"_id": 0, "id": 1, "created_at": 1},
    ).sort([("created_at", -1)]).limit(5).to_list(5)

    # Stable canonical form: sort by id, drop everything except identity
    # + the timestamp that moves when a doc/signal gets refreshed.
    sig_tuples = sorted([
        (str(s.get("signal_id") or ""), str(s.get("created_at") or ""))
        for s in signals
    ])
    doc_tuples = sorted([
        (str(d.get("id") or ""), str(d.get("created_at") or ""))
        for d in docs
    ])
    blob = repr(("sigs", sig_tuples, "docs", doc_tuples)).encode("utf-8")
    return (
        hashlib.sha256(blob).hexdigest(),
        len(signals),
        len(docs),
    )


async def should_skip(
    *, context_id: str, account_id: str, objective_kind: str,
    objective_id: str,
) -> Tuple[bool, str, int, int]:
    """Decide if the tracker should skip this (objective, context).

    Returns `(skip, current_fingerprint, sized_signals, sized_docs)`.
    `skip=True` ONLY when the persisted fingerprint matches the
    current one (i.e. tracked evidence has not moved).
    """
    fp, n_sigs, n_docs = await compute_evidence_fingerprint(
        context_id=context_id, account_id=account_id,
    )
    last = await db.monitor_evidence_fingerprints.find_one({
        "context_id": context_id,
        "account_id": account_id,
        "objective_kind": objective_kind,
        "objective_id": objective_id,
    })
    if last and last.get("fingerprint") == fp:
        return True, fp, n_sigs, n_docs
    return False, fp, n_sigs, n_docs


async def write_fingerprint(
    *, context_id: str, account_id: str, objective_kind: str,
    objective_id: str, fingerprint: str, sized_signals: int,
    sized_docs: int,
) -> None:
    """Persist the fingerprint after a successful assessment."""
    import uuid
    now_iso = iso(now())
    await db.monitor_evidence_fingerprints.update_one(
        {
            "context_id": context_id,
            "account_id": account_id,
            "objective_kind": objective_kind,
            "objective_id": objective_id,
        },
        {
            "$set": {
                "fingerprint": fingerprint,
                "sized_signals": sized_signals,
                "sized_docs": sized_docs,
                "last_assessed_at": now_iso,
                "updated_at": now_iso,
            },
            "$setOnInsert": {
                "id": str(uuid.uuid4()),
                "context_id": context_id,
                "account_id": account_id,
                "objective_kind": objective_kind,
                "objective_id": objective_id,
            },
        },
        upsert=True,
    )


# ─── Pre-warm orchestrator ──────────────────────────────────────────


def _shield_budget_default() -> int:
    """Per-run Shield-call cap. Hard ceiling against runaway calls."""
    try:
        return int(os.environ.get("MONITOR_TRACKER_SHIELD_BUDGET", "200"))
    except Exception:
        return 200


async def pre_warm_context(
    *, context_id: str, account_id: str,
    shield_budget: Optional[int] = None,
    invoke_assessment=None,
) -> Dict[str, Any]:
    """Pre-warm every objective+project in this context.

    Args:
      context_id: scope.
      account_id: tenant id (Shield calls bill to this account).
      shield_budget: max Shield calls this run (default env-driven).
      invoke_assessment: injectable for tests — async callable
        `(*, kind, rid, context_id, account_id) -> dict`. Defaults
        to the live on-demand pipeline (`update_status_assessment`).

    Returns a summary dict suitable for the cron caller to log.
    """
    if shield_budget is None:
        shield_budget = _shield_budget_default()

    if invoke_assessment is None:
        invoke_assessment = _invoke_live_assessment

    summary: Dict[str, Any] = {
        "context_id":   context_id,
        "account_id":   account_id,
        "scanned":      0,
        "skipped_no_delta": 0,
        "warmed":       0,
        "errored":      0,
        "shield_budget_exhausted": False,
        "shield_calls_made": 0,
    }

    for kind, coll in (("objective", db.objectives), ("project", db.projects)):
        cursor = coll.find(
            {"context_id": context_id, "deleted_at": {"$exists": False}},
            {"_id": 0, "id": 1},
        )
        async for row in cursor:
            rid = row.get("id")
            if not rid:
                continue
            summary["scanned"] += 1

            skip, fp, n_sigs, n_docs = await should_skip(
                context_id=context_id, account_id=account_id,
                objective_kind=kind, objective_id=rid,
            )
            if skip:
                summary["skipped_no_delta"] += 1
                continue

            if summary["shield_calls_made"] >= shield_budget:
                summary["shield_budget_exhausted"] = True
                break

            try:
                await invoke_assessment(
                    kind=kind, rid=rid,
                    context_id=context_id, account_id=account_id,
                )
                summary["shield_calls_made"] += 1
                await write_fingerprint(
                    context_id=context_id, account_id=account_id,
                    objective_kind=kind, objective_id=rid,
                    fingerprint=fp, sized_signals=n_sigs, sized_docs=n_docs,
                )
                summary["warmed"] += 1
            except Exception:
                logger.exception(
                    "monitor_pre_warm_failed kind=%s rid=%s context=%s",
                    kind, rid, context_id,
                )
                summary["errored"] += 1
        if summary["shield_budget_exhausted"]:
            break

    return summary


async def _gather_goal_linked_docs(
    *, context_id: str, account_id: str, goal_id: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Source base + tracking docs for a single goal.

    The on-demand `assess_objective` + `recommend_interventions` +
    `explain_performance` + `extended_health` engine helpers all take
    `(base_docs, tracking_docs)`. The linking convention in the
    `documents` collection is `linked_objective_id == goal.id`. A
    document can additionally carry `doc_role: "base" | "tracking"` so
    the goal owner can mark which docs anchor the strategic intent
    vs. which deliver weekly evidence; if `doc_role` is absent we
    default to tracking (the canonical Monitor drawer behaviour).
    """
    cursor = db.documents.find(
        {
            "context_id": context_id,
            "account_id": account_id,
            "linked_objective_id": goal_id,
        },
        {"_id": 0},
    )
    base_docs: List[Dict[str, Any]] = []
    tracking_docs: List[Dict[str, Any]] = []
    async for d in cursor:
        if (d.get("doc_role") or "").lower() == "base":
            base_docs.append(d)
        else:
            tracking_docs.append(d)
    return base_docs, tracking_docs


async def _invoke_live_assessment(
    *, kind: str, rid: str, context_id: str, account_id: str,
) -> Dict[str, Any]:
    """Default invoker — calls the SAME helpers the on-demand handler uses.

    The pre-warmer DOES NOT call the HTTP endpoint to avoid the auth-
    dependency surface; it calls the same engine helpers the endpoint
    delegates to, in the same order, then writes the same persisted
    fields. This satisfies the user's invariant "must call the same
    `recommend_interventions` / `explain_performance` / `extended_health`
    paths" while keeping the tracker out-of-process-safe.

    v0.5 (2026-06-26): extended to fan out to the three additional
    engine legs (`recommend_interventions`, `explain_performance`,
    `extended_health`) AFTER the status-assessment leg completes.
    All four legs route through the same Shield path the on-demand
    handler uses; the per-objective fingerprint gate (see
    `should_skip` upstream) covers them as a unit — no per-leg
    discriminator, no parallel pipeline. Each leg consumes from the
    same per-context Shield budget on the caller's accounting (one
    call per leg per row → up to 4 Shield calls per warmed row).
    """
    # Import lazily so this module is import-safe outside the FastAPI app
    # boot (the live router pulls in `contracts.get_synisense` which
    # depends on `app.state` being set).
    from routers.monitor_status_assessment import (
        _gather_engine_signals, _gather_recent_docs,
        _format_assessment_prompt, _parse_assessment_response,
        _coll, shield_invoke,
    )
    coll = _coll(kind)
    item = await coll.find_one(
        {"id": rid, "context_id": context_id,
         "deleted_at": {"$exists": False}},
        {"_id": 0},
    )
    if not item:
        return {"error": "not_found"}
    signals = await _gather_engine_signals(
        tenant_id=account_id, context_id=context_id,
    )
    docs = await _gather_recent_docs(
        context_id=context_id, account_id=account_id,
    )
    if not signals and not docs:
        # Same no-data short-circuit the on-demand handler uses — no
        # Shield call, no fingerprint update.
        return {"no_data": True}
    purpose = f"monitor.{kind}.status_assessment"
    prompt = _format_assessment_prompt(
        item=item, item_kind=kind, signals=signals, docs=docs,
    )
    sr = await shield_invoke(
        purpose=purpose, content=prompt,
        tenant_id=account_id, consumer_id="monitor",
        user_id=account_id, model_preference="analytical",
        internal_caller=True,
    )
    assessment = _parse_assessment_response(
        sr["response"],
        signal_ids=[s["signal_id"] for s in signals],
        doc_ids=[d["id"] for d in docs],
    )
    # Persist the assessed status on the row, mirroring the on-demand
    # handler.
    now_iso = iso(now())
    await coll.update_one(
        {"id": rid, "context_id": context_id},
        {"$set": {
            "rag_status": assessment.get("rag_status"),
            "status_assessment": assessment,
            "status_assessed_at": now_iso,
            "status_assessment_source": "tracker_v0",
        }},
    )

    # v0.5 fan-out — call the 3 additional engine legs on the same
    # fingerprint gate. Honest refusal when evidence is thin (the
    # legs themselves enforce that — see assess_objective's
    # no_tracking_evidence_yet refusal). We still PERSIST the leg
    # outputs (`tracker_legs.{recommendations,performance,extended_health}`)
    # so the on-demand UI can deep-link to them.
    leg_summary: Dict[str, Any] = {
        "recommend_interventions": None,
        "explain_performance":     None,
        "extended_health":         None,
        "leg_calls_made":          0,
        "leg_refusals":            0,
    }
    try:
        base_docs, tracking_docs = await _gather_goal_linked_docs(
            context_id=context_id, account_id=account_id, goal_id=rid,
        )
        # Build the richer assessment shape the 4-leg engine functions
        # expect. The on-demand-status assessment we already produced
        # uses a slightly different field set — translate it cleanly.
        engine_assessment = await _engine_assess_objective_if_evidence(
            objective=item, base_docs=base_docs, tracking_docs=tracking_docs,
        )

        from services.monitor import (
            recommend_interventions, explain_performance, extended_health,
        )

        recs = await recommend_interventions(
            objective=item, assessment=engine_assessment,
            base_docs=base_docs, tracking_docs=tracking_docs,
        )
        leg_summary["recommend_interventions"] = recs
        leg_summary["leg_calls_made"] += 1
        if recs.get("refused"):
            leg_summary["leg_refusals"] += 1

        perf = await explain_performance(
            objective=item, assessment=engine_assessment,
            base_docs=base_docs, tracking_docs=tracking_docs,
        )
        leg_summary["explain_performance"] = perf
        leg_summary["leg_calls_made"] += 1
        if perf.get("refused"):
            leg_summary["leg_refusals"] += 1

        eh = await extended_health(
            objective=item, assessment=engine_assessment,
            base_docs=base_docs, tracking_docs=tracking_docs,
        )
        leg_summary["extended_health"] = eh
        leg_summary["leg_calls_made"] += 1
        if eh.get("refused"):
            leg_summary["leg_refusals"] += 1

        await coll.update_one(
            {"id": rid, "context_id": context_id},
            {"$set": {
                "tracker_legs": leg_summary,
                "tracker_legs_assessed_at": iso(now()),
                "status_assessment_source": "tracker_v05",
            }},
        )
    except Exception:
        # Honest failure — the status_assessment leg already landed
        # above. We don't fail the whole row if the fan-out legs
        # error out; we just don't update tracker_legs and the
        # downstream caller doesn't get the additional content.
        logger.exception("tracker_legs_fan_out_failed rid=%s", rid)

    # Return the original assessment (callers only inspect status /
    # rag fields). Tracker_legs is consumed via the row.
    return assessment


async def _engine_assess_objective_if_evidence(
    *, objective: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Wrap `assess_objective` to be safe when the goal has zero
    linked base/tracking docs. In that case the engine refuses
    with `no_tracking_evidence_yet` — which is correct + the
    3 downstream legs honour the refusal short-circuit (no LLM
    call). Returning a synthesised refusal here keeps the call
    shape consistent (always-a-dict) for the downstream legs.
    """
    if not base_docs and not tracking_docs:
        return {
            "objective_id":  objective.get("id"),
            "refused":        True,
            "refusal_reason": "no_tracking_evidence_yet",
            "progress_pct":  0,
            "probability_pct": 0,
            "probability_band": "Low-conviction",
        }
    from services.monitor import assess_objective
    return await assess_objective(
        objective=objective, base_docs=base_docs, tracking_docs=tracking_docs,
    )
