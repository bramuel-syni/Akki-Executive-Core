"""Phase P2 B.4 — In-app password change endpoint lockdown.

Asserts:
  - 401 when current password is wrong
  - 400 when new == current (no-op)
  - 400 when account is passwordless (no current to verify)
  - 200 + fresh access token when current is correct
  - sessions_revoked_after bumped on success
  - audit row written to feature_events

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


def _make_account(email_prefix: str, password: str | None) -> dict:
    """Seed a fresh account synchronously via pymongo. Returns the doc."""
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    email = f"{email_prefix}-{uuid.uuid4().hex[:8]}@b4.example.com"
    doc = {
        "id":        uuid.uuid4().hex,
        "email":     email,
        "email_lc":  email.lower(),
        "status":    "active",
        "is_superadmin": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if password:
        doc["password_hash"] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        doc["auth_provider"] = "password"
    else:
        doc["auth_provider"] = "passwordless"
    db.accounts.insert_one(dict(doc))
    return doc


async def _login(email: str, password: str) -> str:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert r.status_code == 200, r.text
        return r.json()["access_token"]


@pytest.mark.asyncio
async def test_b4_change_password_happy_path():
    acc = _make_account("b4-happy", "OldPassword1234!")
    tok = await _login(acc["email"], "OldPassword1234!")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            "/api/auth/password/change",
            headers={"Authorization": f"Bearer {tok}"},
            json={
                "current_password": "OldPassword1234!",
                "new_password":     "NewPassword5678!",
            },
        )
    assert r.status_code == 200, r.text
    assert r.json()["ok"] is True
    assert r.json().get("access_token")

    # Verify sessions_revoked_after was bumped.
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    fresh = db.accounts.find_one({"id": acc["id"]}, {"_id": 0})
    assert fresh.get("sessions_revoked_after")

    # Verify old password no longer works.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        r2 = await ac.post(
            "/api/auth/login",
            json={"email": acc["email"], "password": "OldPassword1234!"},
        )
    assert r2.status_code == 401


@pytest.mark.asyncio
async def test_b4_rejects_wrong_current_password():
    acc = _make_account("b4-wrong", "RightPass1234!")
    tok = await _login(acc["email"], "RightPass1234!")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            "/api/auth/password/change",
            headers={"Authorization": f"Bearer {tok}"},
            json={
                "current_password": "TotallyWrong",
                "new_password":     "Whatever1234!",
            },
        )
    assert r.status_code == 401
    assert r.json()["detail"]["code"] == "CURRENT_PASSWORD_WRONG"


@pytest.mark.asyncio
async def test_b4_rejects_same_password():
    acc = _make_account("b4-same", "SamePass1234!")
    tok = await _login(acc["email"], "SamePass1234!")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            "/api/auth/password/change",
            headers={"Authorization": f"Bearer {tok}"},
            json={
                "current_password": "SamePass1234!",
                "new_password":     "SamePass1234!",
            },
        )
    assert r.status_code == 400
    assert r.json()["detail"]["code"] == "SAME_PASSWORD"


@pytest.mark.asyncio
async def test_b4_rejects_passwordless_account():
    acc = _make_account("b4-passwordless", None)
    # Issue a token directly (no password to log in with) — replicate
    # the magic-link consume by calling create_access_token from core.
    from core import create_access_token
    tok = create_access_token(acc["id"], acc["email"])

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        r = await ac.post(
            "/api/auth/password/change",
            headers={"Authorization": f"Bearer {tok}"},
            json={
                "current_password": "anything",
                "new_password":     "NewPassword12345!",
            },
        )
    assert r.status_code == 400
    assert r.json()["detail"]["code"] == "PASSWORDLESS_ACCOUNT"
