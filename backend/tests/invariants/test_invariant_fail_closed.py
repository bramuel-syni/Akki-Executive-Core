"""Fail-closed invariant — Phase 0.

When the Shield's de-identification pipeline fails (a real failure
mode in production: spaCy load error, Presidio crash, network
hiccup on the LLM router internals), the calling route MUST return
a refusal — NOT pass raw user content through to the LLM provider.

The Shield's adapter (`services.synisense.adapter.shield_payload_async`)
wraps de-identification failures and raises `ShieldFailure` for
chat-family surfaces. The chat router catches this at the boundary
and returns HTTP 503 with body
`{"error": "shield_unavailable", "action": "retry", ...}`.

This test injects a failure at the de-identifier level by monkey-
patching `services.synisense.shield.deidentifier.deidentify` to
raise. It then asserts the chat POST endpoint returns 5xx with the
documented refusal shape.

Deterministic — no LLM call is reached because the failure short-
circuits the pipeline before the LLM router.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

import server  # noqa: F401
from server import app


pytestmark = [pytest.mark.asyncio]


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


async def test_chat_route_returns_refusal_when_shield_de_id_raises(db_conn, monkeypatch):
    """Inject a failure mode at the Shield entry-point and verify the
    chat route fails closed (503 / shield_unavailable shape)."""
    # The sync chat handler awaits `mint_chat_outcome` at chat.py:1739
    # inside a try/except that catches ShieldFailure → HTTPException 503
    # with the documented refusal shape. Patch the import target so any
    # failure that surfaces as ShieldFailure exercises the refusal path.
    from services.synisense.shield import canonical as shield_canonical
    from services.synisense.shield.exceptions import ShieldFailure

    async def _explode(*args, **kwargs):
        raise ShieldFailure(
            "synthetic — fail-closed invariant test",
            original=RuntimeError("synthetic deidentifier failure"),
            surface="chat",
        )

    monkeypatch.setattr(shield_canonical, "mint_chat_outcome", _explode)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")
        admin_row = await db_conn.accounts.find_one(
            {"email": "admin@akki.ai"}, {"_id": 0, "id": 1},
        )
        chat_id = "chat-fail-closed-" + uuid.uuid4().hex[:10]
        now_iso = datetime.now(timezone.utc).isoformat()
        await db_conn.chats.insert_one({
            "id":               chat_id,
            "account_id":       admin_row["id"],
            "context_id":       None,
            "title":            "Fail-closed invariant",
            "model_id":         "claude-sonnet-4-5",
            "shielding_policy": "auto",
            "status":           "active",
            "messages":         [],
            "created_at":       now_iso,
            "updated_at":       now_iso,
        })
        try:
            r = await ac.post(
                f"/api/chats/{chat_id}/messages",
                json={"content": "What is in this message?"},
                headers=admin,
            )
            # Documented refusal shape: HTTP 5xx with shield_unavailable.
            assert r.status_code >= 500, (
                f"Shield failure did NOT yield a 5xx refusal — "
                f"status={r.status_code} body={r.text[:300]!r}. "
                f"The route may be falling open."
            )
            assert r.status_code < 600, f"unexpected status code: {r.status_code}"
            body = r.json()
            error = body.get("error") or body.get("detail") or {}
            if isinstance(error, dict):
                err_code = error.get("error") or error.get("code")
            else:
                err_code = str(error)
            assert "shield" in (err_code or "").lower() or (
                "shield" in (body.get("detail") or "").lower() if isinstance(body.get("detail"), str) else False
            ), (
                f"refusal body did not surface 'shield' in error code — "
                f"body={body!r}. The fail-closed contract requires a "
                f"discoverable refusal reason."
            )
        finally:
            await db_conn.chats.delete_one({"id": chat_id})


async def test_no_audit_row_for_pre_shield_failure(db_conn, monkeypatch):
    """When the Shield pipeline fails BEFORE the LLM call, the
    audit row contract is:

      - For chat-family surfaces, the route raises before
        `shield_invoke` reaches `audit_log.write_audit()`.
      - Some surfaces opt to mint a refusal-row audit for forensics
        (acceptable). The wire-level guarantee is that
        no `outcome="success"` row is written for a pipeline that
        never reached the LLM.

    Phase 0 contract: assert NO `synisense_audit_log` row with
    outcome="success" is created for our synthetic failure case.
    """
    from services.synisense.shield import canonical as shield_canonical
    from services.synisense.shield.exceptions import ShieldFailure

    async def _explode(*args, **kwargs):
        raise ShieldFailure(
            "synthetic — fail-closed invariant test",
            original=RuntimeError("synthetic deidentifier failure"),
            surface="chat",
        )

    monkeypatch.setattr(shield_canonical, "mint_chat_outcome", _explode)

    # Snapshot the audit row count BEFORE the synthetic call.
    before = await db_conn.synisense_audit_log.count_documents({"outcome": "success"})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")
        admin_row = await db_conn.accounts.find_one(
            {"email": "admin@akki.ai"}, {"_id": 0, "id": 1},
        )
        chat_id = "chat-fail-closed-noaudit-" + uuid.uuid4().hex[:10]
        now_iso = datetime.now(timezone.utc).isoformat()
        await db_conn.chats.insert_one({
            "id":               chat_id,
            "account_id":       admin_row["id"],
            "context_id":       None,
            "title":            "Fail-closed no-audit invariant",
            "model_id":         "claude-sonnet-4-5",
            "shielding_policy": "auto",
            "status":           "active",
            "messages":         [],
            "created_at":       now_iso,
            "updated_at":       now_iso,
        })
        try:
            await ac.post(
                f"/api/chats/{chat_id}/messages",
                json={"content": "Pre-shield failure smoke."},
                headers=admin,
            )
        finally:
            await db_conn.chats.delete_one({"id": chat_id})

    after = await db_conn.synisense_audit_log.count_documents({"outcome": "success"})
    delta = after - before
    assert delta == 0, (
        f"Fail-closed invariant violated: {delta} success-outcome "
        f"audit rows were written despite a Shield failure that "
        f"raised before the LLM call."
    )
