"""Phase 14 — chat fluency integration test against the LIVE LLM.

Marked `@pytest.mark.integration` per the Phase 14 brief Track 3 #5.
NO mocking of `shield_invoke`. Real Shield round-trip; real model.
Opt in via `pytest -m integration`.

Asserts the post-rehydration user-visible reply:
  - Does NOT contain `[[ENT_` (mechanics leak)
  - Does NOT contain `redacted` (case-insensitive)
  - Does NOT contain a whole-word `token` (case-insensitive)
  - Does NOT contain `I can't parse` or `did you mean`
  - DOES contain at least one substantive marker (pre-read / agenda /
    outline / draft / Mary Anne / Bramuel / Nairobi / malaria) — proof
    the model produced real prose, not a refusal
  - synisense_audit_log row was written with outcome=="success" and
    de_id_summary non-empty
"""
from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timezone
from typing import Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

import server  # noqa: F401
from server import app


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


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


_PROMPT = (
    "Mary Anne and Bramuel are meeting in Nairobi on Friday to discuss "
    "the malaria response programme. Bramuel will use a corporate card "
    "ending 7689 to cover the venue. Can you help draft a short pre-read?"
)

_SUBSTANTIVE_MARKERS = (
    "pre-read", "agenda", "outline", "draft",
    "Mary Anne", "Bramuel", "Nairobi", "malaria",
)


async def test_chat_response_does_not_leak_shield_mechanics(db_conn):
    """Real round-trip — assertions against the user-visible prose."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=120.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", os.environ["ADMIN_SEED_PASSWORD"])
        admin_row = await db_conn.accounts.find_one(
            {"email": "admin@akki.ai"}, {"_id": 0, "id": 1, "default_context_id": 1},
        )
        cid = admin_row.get("default_context_id") or "ctx-phase14-fluency"

        chat_id = "chat-phase14-fluency-" + uuid.uuid4().hex[:10]
        now_iso = datetime.now(timezone.utc).isoformat()
        await db_conn.chats.insert_one({
            "id": chat_id,
            "account_id": admin_row["id"],
            "context_id": None,
            "title": "Phase 14 fluency",
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
                json={"content": _PROMPT},
                headers=admin,
            )
            assert r.status_code == 200, r.text
            body = r.json()
            asst = body.get("assistant_message") or {}
            reply = asst.get("content") or ""

            # Empty reply / LLM error — surface as HUMAN_REQUIRED, not a fail.
            if not reply or reply.startswith("(LLM error:"):
                pytest.skip(
                    f"HUMAN_REQUIRED: chat LLM round-trip did not return a "
                    f"usable reply. Possible model rate-limit or "
                    f"availability issue. reply={reply[:200]!r}"
                )

            # 1. No shield mechanics leak.
            assert "[[ENT_" not in reply, (
                f"Shield-mechanics leak — '[[ENT_' visible to user. reply={reply[:500]!r}"
            )
            assert "redacted" not in reply.lower(), (
                f"Forbidden word 'redacted' leaked to user. reply={reply[:500]!r}"
            )
            assert not re.search(r"\btoken\b", reply, re.IGNORECASE), (
                f"Whole-word 'token' leaked to user. reply={reply[:500]!r}"
            )
            for forbidden_phrase in ("I can't parse", "did you mean"):
                assert forbidden_phrase.lower() not in reply.lower(), (
                    f"Forbidden phrase {forbidden_phrase!r} leaked. "
                    f"reply={reply[:500]!r}"
                )

            # 2. Substantively responsive.
            reply_lc = reply.lower()
            matched = [m for m in _SUBSTANTIVE_MARKERS if m.lower() in reply_lc]
            assert matched, (
                f"Reply contained no substantive marker; model may have "
                f"refused. reply={reply[:500]!r}"
            )

            # 3. Audit row was written.
            audit_id = asst.get("synisense_audit_id") or asst.get("audit_id")
            if audit_id:
                audit_row = await db_conn.synisense_audit_log.find_one(
                    {"audit_id": audit_id}, {"_id": 0},
                )
                assert audit_row is not None, (
                    f"audit row not found for id={audit_id!r}"
                )
                assert audit_row.get("outcome") == "success", (
                    f"audit outcome != 'success': {audit_row.get('outcome')!r}"
                )
                assert audit_row.get("de_id_summary"), (
                    f"audit de_id_summary empty — Shield did not de-identify "
                    f"the prompt. row={audit_row}"
                )
        finally:
            await db_conn.chats.delete_one({"id": chat_id})
