"""Phase 5 Part D — Per-context cron arming helpers.

Each helper module exposes ``arm(app, db, logger)`` that registers the
cron jobs owned by that bounded context. The functions are designed to
be:

  • Idempotent (callable multiple times without duplicating jobs).
  • Defensive (a failure to arm a cron logs + continues; the app
    keeps serving traffic).
  • Independent (no helper imports another context's helper or makes
    cross-context decisions).

In the **bundled** topology (the current platform default), the same
single `server.py` process arms all crons inline in its startup hook.
In the **multi-process** topology (Phase 5 sell-ready, gated on the
supervisor unlock — see PHASE_4_3_TOPOLOGY.md §1 deviation), each
`<context>_app.py` calls its own context's `arm(...)` from its lifespan
event handler so the cron lives in exactly one process.
"""
from __future__ import annotations
