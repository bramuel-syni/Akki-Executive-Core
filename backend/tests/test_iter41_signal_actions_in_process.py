"""Iter-41 — Signal actions / Pulse Resolved (in-process rewrite).

Hardening Step 4 (2026-05-25). Replaces the archived
`test_iter41_signal_actions.py` E2E shell. Same invariants, in-
process httpx ASGI pattern.

Cluster-C fixture-isolation refactor (2026-06-30). Replaced 3
module-level free helper functions (`_client` / `_register` /
`_seed_signal`) with 3 function-scoped pytest fixtures + 1
autouse fixture snapshotting `app.dependency_overrides` for
upstream-pollution defense. Closes FTT-004..009.

Pollution mechanism root cause (per
`memory/sprints/P5_7_FIX_SCOPE_CLUSTER_C_ADVANCE.md §2`): module-
level `import core as core_mod` + `from server import app` exposed
2 shared mutable singletons. Upstream tests that mutated
`app.dependency_overrides` (or held Motor connection state) without
cleanup leaked state into these tests, causing in-context failures
despite isolation PASS. The fixture refactor scopes ALL test state
to function lifetime + restores `app.dependency_overrides` to its
pre-test snapshot at teardown.

Anti-source-string-assertion discipline (closeout §5.8): each test
asserts a CONTROL-FLOW CHAIN — POST → response → Mongo projection
→ summary recompute — not a literal source match.

Coverage:
  s41.A — GET recommendations returns the bucket + 3 next-step
          suggestions for the signal's tone.
  s41.B — POST action with action_type=acted persists a row +
          surfaces in the summary as `acted: True`.
  s41.C — POST action with action_type=shared + recipients
          surfaces in the summary as `shared_count: N`.
  s41.D — GET actions returns most-recent-first ordering AND the
          summary fields are correctly recomputed.
  s41.E — 404 on POST against an unknown signal_id (RBAC integrity).
  s41.F — Pydantic validation rejects `action_type` outside
          {acted, shared} with 422.
"""
from __future__ import annotations

import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
import pytest_asyncio

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "akki_dev")
os.environ.setdefault("JWT_SECRET", "x" * 64)

import core as core_mod
from server import app


# ── Function-scoped fixtures (Cluster-C fixture-isolation refactor) ──

@pytest.fixture(autouse=True)
def _reset_app_dependency_overrides():
    """Snapshot + restore `app.dependency_overrides` per-test.

    Autouse so every test gets the defense even if it doesn't
    declare the fixture explicitly. Addresses the dominant
    upstream-pollution surface (FastAPI dep-override leak)
    identified in the Cluster-C advance scan §2.2 surface (1).
    """
    snapshot = dict(app.dependency_overrides)
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(snapshot)


@pytest_asyncio.fixture
async def client():
    """Fresh httpx ASGI client per-test; closed at teardown."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


@pytest_asyncio.fixture
async def registered_user(client, request):
    """Register a fresh user with a prefix derived from the test
    node name + uuid suffix. Yields `(token, account, ctx_id)`.
    Teardown deletes account + contexts to avoid carry-over."""
    name = request.node.name
    m = re.search(r"s41_([a-f])", name)
    prefix = f"s41-{m.group(1)}" if m else f"s41-{name[-3:]}"
    email = f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"
    r = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!@#",
            "name": f"{prefix.title()} Tester",
            "role": "executive",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    token = body["access_token"]
    account = body["account"]
    ctx_id = body["contexts"][0]["id"]
    yield token, account, ctx_id
    # Teardown — best-effort cleanup; if Mongo is mid-shutdown the
    # next test still gets fresh UUIDs so collisions don't occur.
    try:
        await core_mod.db.accounts.delete_one({"id": account["id"]})
        await core_mod.db.contexts.delete_many({"account_id": account["id"]})
    except Exception:
        pass


@pytest_asyncio.fixture
async def signal_factory(registered_user):
    """Factory: returns an async callable seeding a `signals` row
    for the registered user's context. Tracks every seeded sid;
    teardown deletes them + any associated `signal_actions`.

    Usage:
        sid = await signal_factory()                 # kind='risk'
        sid = await signal_factory(kind="opportunity")
    """
    _, _, ctx_id = registered_user
    created: list[str] = []

    async def _create(*, kind: str = "risk",
                      headline: str = "Test risk surface") -> str:
        sid = str(uuid.uuid4())
        await core_mod.db.signals.insert_one({
            "id": sid,
            "context_id": ctx_id,
            "kind": kind,
            "tone": kind,
            "headline": headline,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        created.append(sid)
        return sid

    yield _create

    # Teardown
    for sid in created:
        try:
            await core_mod.db.signals.delete_one({"id": sid})
            await core_mod.db.signal_actions.delete_many({"signal_id": sid})
        except Exception:
            pass


# ── s41.A — recommendations bucket + 3 suggestions ──────────────────
@pytest.mark.asyncio
async def test_s41_a_get_recommendations_returns_bucket_and_three(
    client, registered_user, signal_factory,
):
    """Anchor chain: seed a `risk` signal → GET recommendations →
    response carries `bucket: "risk"` AND exactly 3 recommendation
    entries each with `label` + `note`."""
    token, _, ctx_id = registered_user
    sid = await signal_factory(kind="risk")
    h = {"Authorization": f"Bearer {token}"}
    r = await client.get(
        f"/api/contexts/{ctx_id}/signals/{sid}/recommendations",
        headers=h,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("bucket") == "risk", body
    recs = body.get("recommendations") or []
    assert len(recs) == 3, f"Expected 3 recs, got {len(recs)}: {recs}"
    for rec in recs:
        assert rec.get("label"), rec
        assert rec.get("note"), rec


# ── s41.B — POST action=acted persists + summary rolls forward ─────
@pytest.mark.asyncio
async def test_s41_b_post_acted_persists_and_summarises(
    client, registered_user, signal_factory,
):
    """Anchor chain: POST action_type=acted with recommendation_idx
    → 200 → row in `signal_actions` collection → GET /actions
    summary.acted is True AND summary.last_acted_label resolves
    from the recommendation templates."""
    token, _, ctx_id = registered_user
    sid = await signal_factory(kind="risk")
    h = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        f"/api/contexts/{ctx_id}/signals/{sid}/actions",
        json={"action_type": "acted", "recommendation_idx": 0},
        headers=h,
    )
    assert r.status_code == 200, r.text
    doc = r.json()
    assert doc["action_type"] == "acted"
    assert doc["recommendation_idx"] == 0
    # Label was resolved from the template because the client
    # didn't echo it back.
    assert doc.get("recommendation_label"), doc
    # GET /actions surfaces the summary fields.
    rs = await client.get(
        f"/api/contexts/{ctx_id}/signals/{sid}/actions", headers=h,
    )
    assert rs.status_code == 200, rs.text
    summary = rs.json()["summary"]
    assert summary["acted"] is True
    assert summary["last_acted_label"] == doc["recommendation_label"]


# ── s41.C — POST action=shared + recipients aggregation ────────────
@pytest.mark.asyncio
async def test_s41_c_post_shared_aggregates_recipients(
    client, registered_user, signal_factory,
):
    """Anchor chain: POST action_type=shared with 2 recipients →
    GET /actions summary.shared_count == 2 AND summary.shared_with
    is a deduplicated sorted list."""
    token, _, ctx_id = registered_user
    sid = await signal_factory(kind="opportunity")
    h = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        f"/api/contexts/{ctx_id}/signals/{sid}/actions",
        json={
            "action_type": "shared",
            "recipients": ["chair@board.com", "audit@board.com"],
            "note": "Sharing for awareness",
        },
        headers=h,
    )
    assert r.status_code == 200, r.text
    # Share to one of the same emails again → dedup keeps count at 2.
    await client.post(
        f"/api/contexts/{ctx_id}/signals/{sid}/actions",
        json={
            "action_type": "shared",
            "recipients": ["chair@board.com"],
        },
        headers=h,
    )
    rs = await client.get(
        f"/api/contexts/{ctx_id}/signals/{sid}/actions", headers=h,
    )
    assert rs.status_code == 200, rs.text
    summary = rs.json()["summary"]
    assert summary["shared_count"] == 2, summary
    assert summary["shared_with"] == sorted(["chair@board.com",
                                              "audit@board.com"])


# ── s41.D — GET actions returns most-recent-first ──────────────────
@pytest.mark.asyncio
async def test_s41_d_actions_list_orders_most_recent_first(
    client, registered_user, signal_factory,
):
    """Anchor chain: 2 actions POSTed sequentially → GET /actions
    returns actions[0].created_at >= actions[1].created_at."""
    token, _, ctx_id = registered_user
    sid = await signal_factory(kind="risk")
    h = {"Authorization": f"Bearer {token}"}
    for label in ("first", "second"):
        r = await client.post(
            f"/api/contexts/{ctx_id}/signals/{sid}/actions",
            json={"action_type": "acted",
                  "recommendation_label": label},
            headers=h,
        )
        assert r.status_code == 200, r.text
    rs = await client.get(
        f"/api/contexts/{ctx_id}/signals/{sid}/actions", headers=h,
    )
    actions = rs.json()["actions"]
    assert len(actions) == 2
    # First in list is the most recent ("second" label).
    assert actions[0]["recommendation_label"] == "second", actions
    assert actions[1]["recommendation_label"] == "first", actions
    # Timestamp ordering reflects insertion order.
    assert actions[0]["created_at"] >= actions[1]["created_at"]


# ── s41.E — 404 on unknown signal ──────────────────────────────────
@pytest.mark.asyncio
async def test_s41_e_post_action_unknown_signal_returns_404(
    client, registered_user,
):
    """Anchor chain: POST action against a context the caller is
    a member of BUT a signal_id that doesn't exist → 404 (RBAC
    integrity, not silent-success)."""
    token, _, ctx_id = registered_user
    h = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        f"/api/contexts/{ctx_id}/signals/00000000-no-such/actions",
        json={"action_type": "acted"},
        headers=h,
    )
    assert r.status_code == 404, r.text


# ── s41.F — Pydantic validation rejects bogus action_type ──────────
@pytest.mark.asyncio
async def test_s41_f_invalid_action_type_returns_422(
    client, registered_user, signal_factory,
):
    """Anchor chain: POST with action_type=`deleted` (not in the
    `^(acted|shared)$` pattern) → 422 Pydantic error."""
    token, _, ctx_id = registered_user
    sid = await signal_factory()
    h = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        f"/api/contexts/{ctx_id}/signals/{sid}/actions",
        json={"action_type": "deleted"},
        headers=h,
    )
    assert r.status_code == 422, r.text
