"""JC-MON background tracker cron endpoint.

Canonical spec: /app/memory/JC_MON_CANONICAL_SPEC.md (Wave 3 backlog).

Endpoint:
  POST /api/cron/monitor-background-tracker
    Headers: X-Cron-Secret: $AKKI_CRON_SECRET
    Body: {} (no fields; the run sweeps every context the tenant owns)

The endpoint is fully decoupled from the live FastAPI dependency tree
(no `Depends(require_context_membership)`) so APScheduler can call it
in-proc without minting a JWT. The X-Cron-Secret gate is the same
contract the existing weekly digests use.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException

from core import db
from services.monitor.background_tracker import pre_warm_context

logger = logging.getLogger("akki.monitor.background_tracker.cron")

router = APIRouter(prefix="/api")


@router.post("/cron/monitor-background-tracker")
async def cron_monitor_background_tracker(
    x_cron_secret: Optional[str] = Header(default=None, alias="X-Cron-Secret"),
) -> Dict[str, Any]:
    """Cron entry — pre-warm every (account, context) pair.

    For each tenant that has ≥1 monitor row, sweep their contexts and
    invoke `pre_warm_context`. Per-context budget cap controlled by
    env `MONITOR_TRACKER_SHIELD_BUDGET` (default 200 Shield calls).

    Idempotent — the skip-UNLESS-tracked-evidence-changed-since-
    last-run discriminator on `monitor_evidence_fingerprints` ensures
    a re-run on unchanged inputs is a free no-op (zero Shield calls).
    """
    expected = os.environ.get("AKKI_CRON_SECRET")
    if not expected:
        raise HTTPException(503, detail="cron_secret_not_configured")
    if x_cron_secret != expected:
        raise HTTPException(403, detail="cron_secret_invalid")

    run_summary: Dict[str, Any] = {
        "contexts_scanned": 0,
        "objectives_scanned": 0,
        "warmed":            0,
        "skipped_no_delta":  0,
        "errored":           0,
        "shield_calls_made": 0,
        "shield_budget_exhausted_contexts": [],
    }

    # Enumerate every context that has at least one monitor row.
    obj_contexts = set(await db.objectives.distinct("context_id", {"deleted_at": {"$exists": False}}))
    prj_contexts = set(await db.projects.distinct("context_id", {"deleted_at": {"$exists": False}}))
    active_contexts: List[str] = sorted(obj_contexts | prj_contexts)

    for cid in active_contexts:
        # Resolve the account that owns this context. The on-demand
        # path bills Shield to `account_id` (== tenant_id in this
        # collection). The tracker should bill the same way.
        cdoc = await db.contexts.find_one({"id": cid}, {"_id": 0, "owner_account_id": 1})
        owner = (cdoc or {}).get("owner_account_id")
        if not owner:
            continue

        try:
            sub = await pre_warm_context(
                context_id=cid, account_id=owner,
            )
            run_summary["contexts_scanned"] += 1
            run_summary["objectives_scanned"] += sub["scanned"]
            run_summary["warmed"] += sub["warmed"]
            run_summary["skipped_no_delta"] += sub["skipped_no_delta"]
            run_summary["errored"] += sub["errored"]
            run_summary["shield_calls_made"] += sub["shield_calls_made"]
            if sub.get("shield_budget_exhausted"):
                run_summary["shield_budget_exhausted_contexts"].append(cid)
        except Exception:
            logger.exception("monitor_tracker_context_failed cid=%s", cid)
            run_summary["errored"] += 1

    return run_summary
