"""Phase P2 B.6 — Admin force-reset password endpoint lockdown.

Cluster-F.1 (2026-06-26): converted from sync `_run`-helper pattern to
`@pytest.mark.asyncio + async def` so tests bind to the session-scoped
loop instead of creating local loops that bind Motor to the wrong loop
(same root cause as Cluster-E's FTT-023 closure).
"""
from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import bcrypt
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "backend"))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(REPO / "backend" / ".env")

from httpx import ASGITransport, AsyncClient  # noqa: E402
from server import app  # noqa: E402


def _make_account(email_prefix: str, is_superadmin: bool = False) -> dict:
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    email = f"{email_prefix}-{uuid.uuid4().hex[:8]}@b6.example.com"
    doc = {
        "id":            uuid.uuid4().hex,
        "email":         email,
        "email_lc":      email.lower(),
        "status":        "active",
        "is_superadmin": is_superadmin,
        "auth_provider": "passwordless",
        "created_at":    datetime.now(timezone.utc).isoformat(),
    }
    if is_superadmin:
        doc["password_hash"] = bcrypt.hashpw(b"AdminPass1234!", bcrypt.gensalt()).decode()
        doc["auth_provider"] = "password"
        # Phase P3.3 (2026-02) — newly-created superadmin accounts in
        # tests must satisfy the forced-MFA gate. Seed them as already
        # enrolled so the test's admin call passes.
        doc["mfa_enabled"] = True
        doc["mfa_secret"] = "TESTMFAGATESECRET234567"
    db.accounts.insert_one(dict(doc))
    return doc


async def _admin_token(admin: dict) -> str:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": admin["email"], "password": "AdminPass1234!"},
        )
        return r.json()["access_token"]


@pytest.mark.asyncio
async def test_b6_force_reset_happy_path():
    admin = _make_account("b6-admin", is_superadmin=True)
    target = _make_account("b6-target")
    tok = await _admin_token(admin)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            f"/api/admin/users/{target['id']}/force-reset-password",
            headers={"Authorization": f"Bearer {tok}"},
            json={"send_email": False},
        )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["ok"] is True
    assert data["user_id"] == target["id"]
    assert data["email"] == target["email"]
    assert "/reset-password/" in data["reset_url"]
    assert data["expires_at"]

    # Verify the token is consumable via the existing reset-password flow.
    token = data["reset_url"].rsplit("/", 1)[-1]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        r2 = await ac.post(
            f"/api/auth/reset-password/{token}",
            json={"new_password": "FreshPassword4567!"},
        )
    assert r2.status_code == 200, r2.text


@pytest.mark.asyncio
async def test_b6_non_superadmin_blocked():
    non_admin = _make_account("b6-non-admin", is_superadmin=False)
    # Mint a token for a non-superadmin
    from core import create_access_token
    tok = create_access_token(non_admin["id"], non_admin["email"])
    target = _make_account("b6-target-2")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            f"/api/admin/users/{target['id']}/force-reset-password",
            headers={"Authorization": f"Bearer {tok}"},
            json={"send_email": False},
        )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_b6_unknown_user_returns_404():
    admin = _make_account("b6-admin-404", is_superadmin=True)
    tok = await _admin_token(admin)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            "/api/admin/users/does-not-exist-xyz/force-reset-password",
            headers={"Authorization": f"Bearer {tok}"},
            json={"send_email": False},
        )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_b6_audit_event_written():
    admin = _make_account("b6-admin-audit", is_superadmin=True)
    target = _make_account("b6-target-audit")
    tok = await _admin_token(admin)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        await ac.post(
            f"/api/admin/users/{target['id']}/force-reset-password",
            headers={"Authorization": f"Bearer {tok}"},
            json={"send_email": False},
        )
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    event = db.feature_events.find_one({
        "account_id": target["id"],
        "event_type": "admin.user.password_force_reset",
    }, {"_id": 0})
    assert event, "force-reset audit event must be written"
    assert event["payload"]["triggered_by"] == admin["id"]
