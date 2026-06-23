"""Phase 5 Part D — Akki-owned crons.

Owned by Akki:
  • Exco360 weekly digest — Tuesday 10:00 UTC
  • Influence Digest weekly — Monday 08:00 UTC
  • Paragraph anchors sweep — daily 03:00 UTC
  • Chat retention sweep — daily 03:30 UTC
  • Cohort magic-link expiry reminder — daily 09:00 UTC
  • Ideas by Akki weekly digest — Monday 07:00 UTC
  • News aggregator scheduler — internal (no APScheduler entry; the
    news service owns its own loop).

The bundled `server.py` arms these inline; this module is the
extraction point for the standalone `akki_app.py` topology.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

import httpx
from fastapi import FastAPI


def arm(app: FastAPI, db, logger: Optional[logging.Logger] = None) -> None:
    """Arm Akki-owned crons. Idempotent."""
    log = logger or logging.getLogger("akki.akki.crons")

    cron_secret = os.environ.get("AKKI_CRON_SECRET")
    if not cron_secret:
        log.info(
            "[akki crons] AKKI_CRON_SECRET not set — webhook-driven "
            "schedulers skipped (in-process schedulers still arm)."
        )

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        log.warning("[akki crons] apscheduler not installed — skipping.")
        return

    scheduler = AsyncIOScheduler(timezone="UTC")

    base = os.environ.get(
        "INTERNAL_TRANSPORT_BASE_URL_AKKI",
        "http://localhost:8001",
    ).rstrip("/")

    if cron_secret:
        # ── Tuesdays 10:00 UTC — Exco360 weekly digest ───────────────
        async def _fire_weekly_cron() -> None:
            try:
                async with httpx.AsyncClient(timeout=180.0) as ac:
                    resp = await ac.post(
                        f"{base}/api/blog/cron/weekly",
                        headers={"X-Cron-Secret": cron_secret},
                    )
                log.info(
                    "[akki crons] Exco360 weekly: status=%s body=%s",
                    resp.status_code, (resp.text or "")[:200],
                )
            except Exception as exc:
                log.warning(
                    "[akki crons] Exco360 weekly failed: %s",
                    exc, exc_info=True,
                )

        scheduler.add_job(
            _fire_weekly_cron,
            CronTrigger(day_of_week="tue", hour=10, minute=0),
            id="exco360_weekly",
            replace_existing=True,
        )

        # ── Mondays 08:00 UTC — Influence Digest ─────────────────────
        async def _fire_influence_digest() -> None:
            try:
                async with httpx.AsyncClient(timeout=300.0) as ac:
                    resp = await ac.post(
                        f"{base}/api/cron/weekly-digest",
                        headers={"X-Cron-Secret": cron_secret},
                    )
                log.info(
                    "[akki crons] Influence digest: status=%s body=%s",
                    resp.status_code, (resp.text or "")[:200],
                )
            except Exception as exc:
                log.warning(
                    "[akki crons] Influence digest failed: %s",
                    exc, exc_info=True,
                )

        scheduler.add_job(
            _fire_influence_digest,
            CronTrigger(day_of_week="mon", hour=8, minute=0),
            id="influence_digest_weekly",
            replace_existing=True,
        )

        # ── Daily 03:00 UTC — Paragraph anchors sweep ────────────────
        async def _fire_paragraph_anchors_sweep() -> None:
            try:
                async with httpx.AsyncClient(timeout=600.0) as ac:
                    resp = await ac.post(
                        f"{base}/api/cron/paragraph-anchors-sweep",
                        headers={"X-Cron-Secret": cron_secret},
                    )
                log.info(
                    "[akki crons] paragraph anchors sweep: status=%s body=%s",
                    resp.status_code, (resp.text or "")[:200],
                )
            except Exception as exc:
                log.warning(
                    "[akki crons] paragraph anchors sweep failed: %s",
                    exc, exc_info=True,
                )

        scheduler.add_job(
            _fire_paragraph_anchors_sweep,
            CronTrigger(hour=3, minute=0),
            id="paragraph_anchors_daily",
            replace_existing=True,
        )

    # ── Daily 03:30 UTC — Chat retention sweep (in-process) ──────────
    async def _fire_chat_retention_sweep() -> None:
        try:
            from routers.chat import run_chat_retention_sweep
            summary = await run_chat_retention_sweep()
            log.info("[akki crons] chat retention sweep: %s", summary)
        except Exception as exc:
            log.warning(
                "[akki crons] chat retention sweep failed: %s",
                exc, exc_info=True,
            )

    scheduler.add_job(
        _fire_chat_retention_sweep,
        CronTrigger(hour=3, minute=30),
        id="chat_retention_daily",
        replace_existing=True,
    )

    # ── Daily 09:00 UTC — Cohort magic-link expiry reminder ──────────
    async def _fire_cohort_expiry_reminders() -> None:
        try:
            from routers.cohort_expiry_reminder import (
                run_expiry_reminder_sweep,
            )
            summary = await run_expiry_reminder_sweep()
            log.info("[akki crons] cohort expiry reminder: %s", summary)
        except Exception as exc:
            log.warning(
                "[akki crons] cohort expiry reminder failed: %s",
                exc, exc_info=True,
            )

    scheduler.add_job(
        _fire_cohort_expiry_reminders,
        CronTrigger(hour=9, minute=0),
        id="cohort_expiry_reminder_daily",
        replace_existing=True,
    )

    # ── Monday 07:00 UTC — Ideas by Akki weekly digest ───────────────
    async def _fire_ideas_weekly_sweep() -> None:
        try:
            from services.ideas_engine.scheduler import (
                is_scheduler_disabled,
                run_weekly_ideas_sweep,
            )
            if is_scheduler_disabled():
                log.info("[akki crons] Ideas weekly sweep: disabled by env.")
                return
            summary = await run_weekly_ideas_sweep(db)
            log.info(
                "[akki crons] Ideas weekly sweep: %s",
                {k: v for k, v in summary.items() if k != "sample"},
            )
        except Exception as exc:
            log.warning(
                "[akki crons] Ideas weekly sweep failed: %s",
                exc, exc_info=True,
            )

    scheduler.add_job(
        _fire_ideas_weekly_sweep,
        CronTrigger(day_of_week="mon", hour=7, minute=0),
        id="ideas_weekly_sweep",
        replace_existing=True,
    )

    scheduler.start()
    app.state.akki_scheduler = scheduler
    log.info(
        "[akki crons] Schedulers armed: chat retention (03:30) + "
        "cohort expiry (09:00) + Ideas weekly (Mon 07:00)%s.",
        " + Exco360 (Tue 10:00) + Influence (Mon 08:00) + "
        "paragraph anchors (03:00)"
        if cron_secret else " (webhook-driven crons skipped — no secret)",
    )
