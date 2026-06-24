"""Stage 5 — Task Manager / Monitor / Pulse FE shell verification.

Per the Full Runway dispatch's Stage 5 STOP gate ("a backend a frontend
needs doesn't actually work at runtime"), this suite walks the three
Stage 5 FE pages' main read endpoints — classify-by-execution before
declaring the surface healthy.

Coverage (read-only; CRUD writes are exercised by the per-router suites
already green at this commit):

  • /api/tasks/counts                          → Task Manager top counts
  • /api/contexts/{cid}/monitor                → Monitor dashboard (CEO/CFO/...)
  • /api/contexts/{cid}/monitor/{kind}         → Monitor strategic items (CRUD)
  • /api/contexts/{cid}/monitor/owner-roles    → Monitor owner role catalogue
  • /api/contexts/{cid}/pulse/feed             → Pulse signal feed

Each endpoint must return HTTP 200 for an authenticated member of the
target context. Anything else (401 / 404 / 500) trips the STOP gate.

Pattern mirrors test_stage_4_3_analyze_narration_exports.py:
httpx.AsyncClient + ASGITransport + @pytest.mark.asyncio so we stay on
the conftest session loop.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
import pymongo
from httpx import ASGITransport, AsyncClient

from server import app


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sync_db():
    return pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]


def _seed_stage5_world(account_id: str, email: str, context_id: str) -> None:
    """Seed: account + context + membership (owner). Empty by design
    so each endpoint exercises the empty-listing happy path. The
    routers shouldn't 500 on empty data."""
    sdb = _sync_db()
    sdb.accounts.insert_one({
        "id": account_id,
        "email": email,
        "email_lc": email,
        "full_name": "Stage 5 Tester",
        "hashed_password": "x",
        "active_context_id": context_id,
        "default_context_id": context_id,
        "created_at": _now_iso(),
    })
    sdb.contexts.insert_one({
        "id": context_id,
        "name": "Stage 5 Test Context",
        "owner_account_id": account_id,
        "created_at": _now_iso(),
    })
    sdb.memberships.insert_one({
        "id": "mem-" + uuid.uuid4().hex[:12],
        "account_id": account_id,
        "context_id": context_id,
        "role": "owner",
        "status": "active",
        "created_at": _now_iso(),
    })


def _cleanup_stage5_world(account_id: str, context_id: str) -> None:
    sdb = _sync_db()
    sdb.accounts.delete_one({"id": account_id})
    sdb.contexts.delete_one({"id": context_id})
    sdb.memberships.delete_many({"context_id": context_id})


def _token_for(account_id: str, email: str) -> str:
    from core import create_access_token
    return create_access_token(account_id, email)


@pytest.fixture
def stage_5_world():
    account_id = "acct-stg5-" + uuid.uuid4().hex[:8]
    context_id = "ctx-stg5-" + uuid.uuid4().hex[:8]
    email = f"stage5-{account_id}@test.local"
    _seed_stage5_world(account_id, email, context_id)
    try:
        yield {
            "account_id": account_id,
            "context_id": context_id,
            "email": email,
            "token": _token_for(account_id, email),
        }
    finally:
        _cleanup_stage5_world(account_id, context_id)


@pytest.fixture
async def stage_5_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as ac:
        yield ac


def _h(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────
# Task Manager (Stage 5.1)
# ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_task_manager_counts_endpoint(stage_5_client, stage_5_world):
    """`GET /api/tasks/counts?context_id=<cid>` → 200 with the
    `{active, draft, closed}` shape the TaskManager.jsx top-of-page
    badges consume."""
    r = await stage_5_client.get(
        f"/api/tasks/counts?context_id={stage_5_world['context_id']}",
        headers=_h(stage_5_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]
    body = r.json()
    # Counts on a fresh context are 0 across the board but the keys
    # must be present so the FE doesn't render NaN.
    for k in ("active", "draft", "closed"):
        assert k in body, f"missing key {k!r} in counts payload: {body!r}"
        assert isinstance(body[k], int)


@pytest.mark.asyncio
async def test_task_manager_list_endpoint(stage_5_client, stage_5_world):
    """`GET /api/tasks?context_id=<cid>` → 200 (empty list on a
    fresh context). The TaskManager.jsx mounts a TaskListing that
    fans out to this endpoint per tab."""
    r = await stage_5_client.get(
        f"/api/tasks?context_id={stage_5_world['context_id']}",
        headers=_h(stage_5_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]
    body = r.json()
    # Shape may be a list or {items: [...]} — both have been live.
    items = body if isinstance(body, list) else body.get("items") or body.get("tasks") or []
    assert isinstance(items, list)


# ─────────────────────────────────────────────────────────────────
# Monitor (Stage 5.2)
# ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_monitor_dashboard_endpoint(stage_5_client, stage_5_world):
    """`GET /api/contexts/{cid}/monitor?function=ceo` → 200. Backed
    by `routers/monitor_dashboard.py` post-Stage-3 rename. Used by
    pages/Monitor.jsx:110 for the top dashboard payload."""
    r = await stage_5_client.get(
        f"/api/contexts/{stage_5_world['context_id']}/monitor?function=ceo",
        headers=_h(stage_5_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]


@pytest.mark.asyncio
async def test_monitor_strategic_items_endpoints(stage_5_client, stage_5_world):
    """`GET /api/contexts/{cid}/monitor/{kind}` → 200 for each of the
    valid strategic-item kinds. Backed by
    `routers/monitor_strategic_items.py` (post-Stage-3 rename); the
    FE drives this via `ObjectivesProjectsPanel.jsx`. The router
    accepts `objective` and `project` (`task` + `initiative` are
    served by `tasks_initiatives.py` under a different path)."""
    for kind in ("objective", "project"):
        r = await stage_5_client.get(
            f"/api/contexts/{stage_5_world['context_id']}/monitor/{kind}",
            headers=_h(stage_5_world["token"]),
        )
        # Empty fresh context → expected 200 with items: []
        assert r.status_code == 200, (
            f"monitor/{kind} returned {r.status_code}: {r.text[:200]}"
        )


@pytest.mark.asyncio
async def test_monitor_owner_roles_endpoint(stage_5_client, stage_5_world):
    """`GET /api/contexts/{cid}/monitor/owner-roles` → 200, returns
    the canonical owner-role catalogue used by the strategic-item
    create flow."""
    r = await stage_5_client.get(
        f"/api/contexts/{stage_5_world['context_id']}/monitor/owner-roles",
        headers=_h(stage_5_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]


# ─────────────────────────────────────────────────────────────────
# Pulse (Stage 5.3)
# ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pulse_feed_endpoint(stage_5_client, stage_5_world):
    """`GET /api/contexts/{cid}/pulse/feed` → 200. Backed by
    `routers/pulse.py`. Used by pages/Pulse.jsx for the signal
    timeline."""
    r = await stage_5_client.get(
        f"/api/contexts/{stage_5_world['context_id']}/pulse/feed",
        headers=_h(stage_5_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]


@pytest.mark.asyncio
async def test_pulse_across_boards_endpoint(stage_5_client, stage_5_world):
    """`GET /api/contexts/{cid}/pulse/across-boards?window_days=30&limit=10` → 200.
    Used by pages/Pulse.jsx and PulseIdeas.jsx for the cross-board
    radar surface."""
    r = await stage_5_client.get(
        f"/api/contexts/{stage_5_world['context_id']}/pulse/across-boards"
        "?window_days=30&limit=10",
        headers=_h(stage_5_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]
