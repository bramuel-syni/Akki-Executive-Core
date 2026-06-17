"""Phase 14 (2026-06-05) — chat system_msg must reach the LLM.

Pre-Phase-14, `routers/chat.py:1833` built a `system_msg` variable
that was NEVER appended to `full_prompt` and NEVER threaded through
`shield_invoke`. The model received zero persona / fluency framing,
which caused the user-visible "I can't parse the redacted tokens"
prose-leak from the screenshot.

This test monkeypatches `shield_invoke` to capture its kwargs, fires
the chat sync send-message route end-to-end, and asserts the AKKI
editorial preamble was passed via `system_msg=`.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

import server  # noqa: F401
from server import app

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def db_conn():
    mclient = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = mclient[os.environ["DB_NAME"]]
    yield db
    mclient.close()


async def _csrf_login(ac: AsyncClient, email: str, password: str) -> Dict[str, str]:
    r = await ac.get("/api/csrf")
    csrf = r.json()["csrf_token"]
    r = await ac.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers={"X-CSRF-Token": csrf},
    )
    r.raise_for_status()
    token = r.json().get("access_token") or r.json().get("token")
    r = await ac.get("/api/csrf")
    return {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": r.json()["csrf_token"],
    }


async def test_chat_system_msg_reaches_shield_invoke(db_conn, monkeypatch):
    """End-to-end: send a chat message; capture shield_invoke kwargs;
    assert the AKKI editorial preamble landed in `system_msg=`."""
    captured: Dict[str, Any] = {}

    async def fake_shield(**kwargs):
        captured.update(kwargs)
        return {
            "response": "Acknowledged.",
            "audit_id": "phase14-fake-audit",
            "de_id_summary": {},
            "trust_receipt": {"audit_id": "phase14-fake-audit"},
        }

    monkeypatch.setattr("services.synisense.shield.client.invoke", fake_shield)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")
        admin_row = await db_conn.accounts.find_one(
            {"email": "admin@akki.ai"}, {"_id": 0, "id": 1, "default_context_id": 1},
        )
        cid = admin_row.get("default_context_id") or "ctx-phase14"

        # Seed a general (context-less) chat thread so the route's
        # default no-X-Active-Context path resolves.
        chat_id = "chat-phase14-" + uuid.uuid4().hex[:10]
        now_iso = datetime.now(timezone.utc).isoformat()
        await db_conn.chats.insert_one({
            "id": chat_id,
            "account_id": admin_row["id"],
            "context_id": None,
            "title": "Phase 14 system_msg test",
            "model_id": "claude-sonnet-4-5",
            "shielding_policy": "auto",
            "status": "active",
            "messages": [],
            "created_at": now_iso,
            "updated_at": now_iso,
        })

        try:
            r = await ac.post(
                f"/api/chats/{chat_id}/messages",
                json={"content": "What's the latest?"},
                headers=admin,
            )
            assert r.status_code == 200, r.text
        finally:
            await db_conn.chats.delete_one({"id": chat_id})

    # Assert shield_invoke saw the kwargs we expect.
    assert captured, "shield_invoke was not called"
    assert "system_msg" in captured, (
        f"system_msg kwarg missing from shield_invoke call: {sorted(captured.keys())}"
    )
    system_msg = captured["system_msg"]
    assert system_msg, "system_msg passed empty"
    assert "calm, editorial intelligence partner" in system_msg, (
        f"AKKI editorial preamble missing from system_msg: {system_msg[:200]!r}"
    )
    assert "[[ENT_" in system_msg, (
        "system_msg must reference the actual [[ENT_*]] token shape, "
        f"got: {system_msg[:300]!r}"
    )
    assert "redacted" in system_msg, (
        "system_msg must explicitly forbid the word 'redacted' "
        "(must appear in the prompt as part of the forbidden-vocab list)"
    )
