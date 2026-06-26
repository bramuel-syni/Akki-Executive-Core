"""Owner Digest v0 router — cron + preview endpoints.

Canonical spec: /app/memory/JC_MON_CANONICAL_SPEC.md (Wave 3 backlog).

Endpoints:
  POST /api/cron/owner-digest-weekly      — cron-only, X-Cron-Secret gated
  GET  /api/contexts/{cid}/owner-digest/preview  — owner-only,
                                                    composes WITHOUT persisting
  GET  /api/contexts/{cid}/owner-digest/latest   — owner-only, last persisted

The cron sweeps all contexts that have at least one owner + at least
one strategic goal, composes a digest per (context, owner), and skips
when no delta. Persisted digests live in `db.owner_digests`; the
delivery rail (email transport, in-app notification) is v0.5 and not
in scope for this slice.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from core import db, require_context_membership
from services.owner_digest import (
    build_owner_digest, compose_or_skip, persist_digest,
)

logger = logging.getLogger("akki.owner_digest")

router = APIRouter(prefix="/api")


@router.get("/contexts/{context_id}/owner-digest/preview")
async def preview_owner_digest(
    context_id: str,
    week_label: Optional[str] = None,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
) -> Dict[str, Any]:
    """Compose the digest WITHOUT persisting.

    Useful for the owner-facing surface to render a "what would this
    week's digest say?" preview before/after the cron run. Anyone
    with context membership can preview; the cron itself respects
    the per-context owner only.
    """
    owner_id = ctx["context"].get("owner_account_id") or ctx["account"]["id"]
    payload = await build_owner_digest(
        context_id=context_id, owner_account_id=owner_id,
        week_label=week_label,
    )
    return payload


@router.get("/contexts/{context_id}/owner-digest/latest")
async def latest_owner_digest(
    context_id: str,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
) -> Dict[str, Any]:
    """Return the latest persisted digest row for this context+owner."""
    owner_id = ctx["context"].get("owner_account_id") or ctx["account"]["id"]
    row = await db.owner_digests.find_one(
        {"context_id": context_id, "owner_account_id": owner_id},
        sort=[("generated_at", -1)],
    )
    if not row:
        return {"latest": None}
    row.pop("_id", None)
    return {"latest": row}


@router.post("/cron/owner-digest-weekly")
async def cron_owner_digest_weekly(
    x_cron_secret: Optional[str] = Header(default=None, alias="X-Cron-Secret"),
) -> Dict[str, Any]:
    """Cron entry point — Monday 09:00 owner-tz.

    Sweep all contexts; for each (context, owner) compose a digest;
    skip when no delta; otherwise persist. Returns a summary the
    APScheduler job logs. Idempotent — re-running on the same week
    is a no-op after the first persisted row.
    """
    expected = os.environ.get("AKKI_CRON_SECRET")
    if not expected:
        raise HTTPException(503, detail="cron_secret_not_configured")
    if x_cron_secret != expected:
        raise HTTPException(403, detail="cron_secret_invalid")

    summary: Dict[str, Any] = {
        "contexts_scanned": 0,
        "digests_persisted": 0,
        "skipped_no_delta":  0,
        "skipped_no_goals":  0,
        "errors":            0,
    }

    contexts: List[Dict[str, Any]] = await db.contexts.find(
        {"owner_account_id": {"$exists": True, "$ne": None}}, {"_id": 0},
    ).to_list(2000)

    for ctx_row in contexts:
        summary["contexts_scanned"] += 1
        owner_id = ctx_row.get("owner_account_id")
        cid = ctx_row.get("id")
        if not owner_id or not cid:
            continue
        # Cheap pre-flight: skip contexts with no strategic goals at all.
        goals_count = await db.strategic_goals.count_documents({"context_id": cid})
        if goals_count == 0:
            summary["skipped_no_goals"] += 1
            continue
        try:
            payload, should_skip = await compose_or_skip(
                context_id=cid, owner_account_id=owner_id,
            )
            if should_skip:
                summary["skipped_no_delta"] += 1
                continue
            await persist_digest(payload)
            summary["digests_persisted"] += 1
        except Exception:
            logger.exception(
                "owner_digest_compose_failed context_id=%s owner_id=%s",
                cid, owner_id,
            )
            summary["errors"] += 1

    return summary
