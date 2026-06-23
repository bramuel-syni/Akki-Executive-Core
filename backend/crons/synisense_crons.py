"""Phase 5 Part D — SyniSense-owned crons.

Owned by SyniSense:
  • Synisense Engine hourly derivation pass — top of every hour UTC.
    Mongo-locked across replicas (the lock collection lives in the
    shared db); per-(job_id, hour_bucket) lease prevents duplicate
    runs.
  • spaCy NER warm-up at startup — Shield prerequisite. Asynchronous;
    runs in a worker thread so startup isn't blocked.

The bundled `server.py` arms these inline; this module is the
extraction point for the standalone `synisense_app.py` topology.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from fastapi import FastAPI


def arm(app: FastAPI, db, logger: Optional[logging.Logger] = None) -> None:
    """Arm SyniSense-owned crons. Idempotent — safe to call repeatedly.

    A previously-armed scheduler is reused; the `replace_existing=True`
    contract on `add_job` keeps the active scheduler clean on restart.
    """
    log = logger or logging.getLogger("akki.synisense.crons")

    # ── spaCy NER warm-up ────────────────────────────────────────────
    try:
        from services.synisense.shield import deidentifier as _deid

        def _warm_spacy_sync() -> None:
            try:
                _deid._ensure_spacy()
            except Exception as exc:
                log.warning(
                    "[synisense crons] spaCy warm-up failed: %s",
                    type(exc).__name__,
                )

        try:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, _warm_spacy_sync)
            log.info("[synisense crons] spaCy NER warm-up scheduled.")
        except RuntimeError:
            # No running loop yet — schedule once the loop spins up.
            log.info(
                "[synisense crons] spaCy NER warm-up deferred "
                "(no running loop at arm time)."
            )
    except Exception as exc:
        log.warning(
            "[synisense crons] spaCy warm-up scheduling failed: %s: %s",
            type(exc).__name__, exc, exc_info=True,
        )

    # ── Synisense Engine hourly derivation pass ──────────────────────
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        from services.synisense.engine import scheduler_lock as engine_lock
        from services.synisense.engine.derivation_scheduler import (
            run_hourly_pass as engine_hourly,
        )

        async def _arm_async() -> None:
            await engine_lock.ensure_indexes()

            async def _fire_engine_hourly_pass() -> None:
                await engine_lock.run_locked(
                    job_id="synisense_engine_hourly",
                    fn=engine_hourly,
                    bucket=engine_lock.current_hour_bucket(),
                    lease_seconds=3600,
                )

            scheduler = AsyncIOScheduler(timezone="UTC")
            scheduler.add_job(
                _fire_engine_hourly_pass,
                CronTrigger(minute=0),
                id="synisense_engine_hourly",
                replace_existing=True,
            )
            scheduler.start()
            app.state.synisense_engine_scheduler = scheduler
            log.info(
                "[synisense crons] Engine hourly cron armed "
                "(replica=%s).",
                engine_lock.replica_id(),
            )

        # Run the async arm immediately if we have a loop; otherwise
        # defer to the first startup event.
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_arm_async())
        except RuntimeError:
            @app.on_event("startup")
            async def _deferred_engine_arm() -> None:
                await _arm_async()

    except Exception as exc:
        log.warning(
            "[synisense crons] engine hourly cron arm failed: %s: %s",
            type(exc).__name__, exc, exc_info=True,
        )
