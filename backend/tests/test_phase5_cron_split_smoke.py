"""Phase 5 Part D — Cron supervisor split smoke.

Asserts that each `<ctx>_app.py` standalone process arms only its
own crons (no cross-context cron leakage). The smoke is a unit-level
import test that:

  1. Loads `crons.{synisense,solva,akki}_crons` modules — each must
     expose an `arm(app, db, logger)` callable.
  2. Verifies the standalone app modules (`synisense_app`,
     `solva_app`, `akki_app`) each register a single
     `_arm_<ctx>_crons_if_standalone` startup hook that no-ops when
     `AKKI_PROCESS_NAME` doesn't match the context.
  3. Verifies the bundled `server.py` still owns the inline crons
     (Phase 5 keeps the bundled topology working — the standalone
     hooks are additive).
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Callable

import pytest


def _import_cron_module(name: str):
    mod = __import__(f"crons.{name}", fromlist=["arm"])
    return mod


def test_crons_package_exposes_three_helpers() -> None:
    for ctx in ("synisense", "solva", "akki"):
        mod = _import_cron_module(f"{ctx}_crons")
        arm = getattr(mod, "arm", None)
        assert callable(arm), (
            f"crons.{ctx}_crons must expose an `arm(app, db, logger)` callable"
        )


def test_synisense_app_registers_standalone_arm_hook() -> None:
    """The standalone `synisense_app:app` must have a startup hook that
    routes to `crons.synisense_crons.arm` when run as the entry process.
    """
    from synisense_app import app
    # FastAPI keeps lifespan handlers internally; check the on-startup
    # event handler list contains our named function.
    handlers = app.router.on_startup or []
    names = [getattr(h, "__name__", "") for h in handlers]
    assert any("synisense_crons" in n for n in names), (
        f"synisense_app missing standalone cron hook (handlers: {names})"
    )


def test_solva_app_registers_standalone_arm_hook() -> None:
    from solva_app import app
    handlers = app.router.on_startup or []
    names = [getattr(h, "__name__", "") for h in handlers]
    assert any("solva_crons" in n for n in names), (
        f"solva_app missing standalone cron hook (handlers: {names})"
    )


def test_akki_app_registers_standalone_arm_hook() -> None:
    from akki_app import app
    handlers = app.router.on_startup or []
    names = [getattr(h, "__name__", "") for h in handlers]
    assert any("akki_crons" in n for n in names), (
        f"akki_app missing standalone cron hook (handlers: {names})"
    )


def test_standalone_hook_no_ops_under_bundled_topology() -> None:
    """When `AKKI_PROCESS_NAME` is empty or set to something other than
    the context name (the bundled topology), the standalone hook must
    no-op so the bundled `server.py` retains exclusive cron ownership.

    The hook reads the env var at call time, NOT import time, so the
    same `<ctx>_app.app` object behaves correctly in both topologies.
    """
    from synisense_app import app as syni_app
    orig = os.environ.get("AKKI_PROCESS_NAME")
    try:
        # Bundled topology — env var unset or set to "server" / etc.
        os.environ.pop("AKKI_PROCESS_NAME", None)
        for handler in (syni_app.router.on_startup or []):
            if "synisense_crons" in getattr(handler, "__name__", ""):
                # Call the hook directly — it must NOT raise and must
                # short-circuit because env doesn't match.
                result = asyncio.get_event_loop().run_until_complete(handler()) \
                    if not asyncio.iscoroutinefunction(handler) \
                    else asyncio.new_event_loop().run_until_complete(handler())
                # No assertion on return value — the contract is that
                # the call returns cleanly and doesn't arm a scheduler.
                assert not hasattr(syni_app.state, "synisense_engine_scheduler"), (
                    "Standalone hook armed a scheduler under bundled topology"
                )
    finally:
        if orig is None:
            os.environ.pop("AKKI_PROCESS_NAME", None)
        else:
            os.environ["AKKI_PROCESS_NAME"] = orig


def test_bundled_server_retains_inline_cron_block() -> None:
    """Phase 5 preserves the bundled topology — `server.py` still owns
    the inline cron-arming block. Verified by import; the block is
    inside an @app.on_event("startup") handler so we can't directly
    assert behaviour without booting the app. Instead we check the
    source file still contains the cron-arming pattern.
    """
    from pathlib import Path
    server_py = Path(__file__).resolve().parents[1] / "server.py"
    src = server_py.read_text()
    # Sentinel substrings that prove the inline block is intact.
    sentinels = [
        "AsyncIOScheduler",
        "exco360_weekly",
        "ideas_weekly_sweep",
        "synisense_engine_hourly",
    ]
    for s in sentinels:
        assert s in src, (
            f"Bundled server.py missing inline cron sentinel '{s}' — "
            f"Phase 5 Part D was not supposed to remove the bundled "
            f"crons (the standalone hooks are additive)."
        )
