"""Phase 5 Part D — Solva-owned crons.

Owned by Solva:
  • Solva v2 stale-session sweep — daily 04:00 UTC. Marks v2 sessions
    idle > 30 days as abandoned with `abandoned_reason="stale_30d"`.
    Idempotent. Gated on `AKKI_CRON_SECRET` because it's a webhook
    invocation against the running Solva surface.

The bundled `server.py` arms this inline; this module is the
extraction point for the standalone `solva_app.py` topology.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

import httpx
from fastapi import FastAPI


def arm(app: FastAPI, db, logger: Optional[logging.Logger] = None) -> None:
    """Arm Solva-owned crons. Idempotent."""
    log = logger or logging.getLogger("akki.solva.crons")

    cron_secret = os.environ.get("AKKI_CRON_SECRET")
    if not cron_secret:
        log.info(
            "[solva crons] AKKI_CRON_SECRET not set — Solva v2 "
            "stale-session sweep skipped."
        )
        return

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger

        async def _fire_solva_v2_stale_sweep() -> None:
            base = os.environ.get(
                "INTERNAL_TRANSPORT_BASE_URL_SOLVA",
                "http://localhost:8001",
            )
            try:
                async with httpx.AsyncClient(timeout=120.0) as ac:
                    resp = await ac.post(
                        f"{base.rstrip('/')}/api/solva/v2/cron/stale-session-sweep",
                        headers={"X-Cron-Secret": cron_secret},
                    )
                log.info(
                    "[solva crons] stale-session sweep: status=%s body=%s",
                    resp.status_code, (resp.text or "")[:200],
                )
            except Exception as exc:
                log.warning(
                    "[solva crons] stale-session sweep failed: %s",
                    exc, exc_info=True,
                )

        scheduler = AsyncIOScheduler(timezone="UTC")
        scheduler.add_job(
            _fire_solva_v2_stale_sweep,
            CronTrigger(hour=4, minute=0),
            id="solva_v2_stale_session_daily",
            replace_existing=True,
        )
        scheduler.start()
        app.state.solva_scheduler = scheduler
        log.info(
            "[solva crons] Solva v2 stale-session sweep armed "
            "(daily 04:00 UTC)."
        )
    except Exception as exc:
        log.warning(
            "[solva crons] arm failed: %s: %s",
            type(exc).__name__, exc, exc_info=True,
        )
