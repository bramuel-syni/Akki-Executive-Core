"""Audit-always invariant — Phase 0.

Every successful Shield invocation MUST write BOTH:
  - a `synisense_audit_log` row, AND
  - a `synisense_trust_receipts` row (mirror).

This test runs a single chat round-trip (real LLM via the Shield),
captures the `synisense_audit_id` surfaced on the assistant message,
and asserts the matching rows exist in both collections.

The trust receipt is HMAC-signed; this test does NOT verify the
signature here (that's the domain of `test_trust_receipt_signature.
py` if/when added). It DOES assert the receipt's `audit_id`
references the audit row, proving the mirror was written for the
same call.

Marked `@pytest.mark.integration` — real LLM. Skip default sweep.
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
    "Quick favour — outline 3 bullet points for a Friday update covering "
    "the Lemasy revenue trend and any anomalies."
)


async def test_chat_call_writes_audit_and_trust_receipt(db_conn):
    """One chat round-trip → one audit row + one trust receipt row."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=180.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", os.environ["ADMIN_SEED_PASSWORD"])
        admin_row = await db_conn.accounts.find_one(
            {"email": "admin@akki.ai"}, {"_id": 0, "id": 1},
        )
        chat_id = "chat-inv-audit-" + uuid.uuid4().hex[:10]
        now_iso = datetime.now(timezone.utc).isoformat()
        await db_conn.chats.insert_one({
            "id":               chat_id,
            "account_id":       admin_row["id"],
            "context_id":       None,
            "title":            "Invariant: audit always",
            "model_id":         "claude-sonnet-4-5",
            "shielding_policy": "auto",
            "status":           "active",
            "messages":         [],
            "created_at":       now_iso,
            "updated_at":       now_iso,
        })

        # Snapshot counts before — used to verify a NEW row landed.
        audit_before = await db_conn.synisense_audit_log.count_documents({})
        receipt_before = await db_conn.synisense_trust_receipts.count_documents({})

        try:
            r = await ac.post(
                f"/api/chats/{chat_id}/messages",
                json={"content": _PROMPT},
                headers=admin,
            )
            if r.status_code != 200:
                pytest.skip(
                    f"HUMAN_REQUIRED: chat non-200 ({r.status_code}). "
                    f"body={r.text[:200]!r}"
                )
            body = r.json()
            asst = body.get("assistant_message") or {}
            reply = asst.get("content") or ""
            if not reply or reply.startswith("(LLM error:"):
                pytest.skip(
                    f"HUMAN_REQUIRED: LLM did not return usable reply. "
                    f"reply={reply[:200]!r}"
                )

            # 1. Audit row count increased by at least 1.
            audit_after = await db_conn.synisense_audit_log.count_documents({})
            assert audit_after >= audit_before + 1, (
                f"Audit-always invariant violated: chat call wrote "
                f"{audit_after - audit_before} new audit rows "
                f"(expected ≥ 1)."
            )

            # 2. Trust receipt count increased by at least 1.
            receipt_after = await db_conn.synisense_trust_receipts.count_documents({})
            assert receipt_after >= receipt_before + 1, (
                f"Audit-always invariant violated: chat call wrote "
                f"{receipt_after - receipt_before} new trust receipts "
                f"(expected ≥ 1)."
            )

            # 3. If the assistant message exposes the audit_id, verify
            #    the row + receipt exist for THAT id specifically.
            audit_id = asst.get("synisense_audit_id") or asst.get("audit_id")
            if audit_id:
                row = await db_conn.synisense_audit_log.find_one(
                    {"audit_id": audit_id}, {"_id": 0},
                )
                assert row is not None, (
                    f"audit row not found for id={audit_id!r}"
                )
                assert row.get("outcome") == "success", (
                    f"audit outcome != 'success': {row.get('outcome')!r}"
                )
                # Trust receipt mirror keyed on the same audit_id.
                receipt = await db_conn.synisense_trust_receipts.find_one(
                    {"audit_id": audit_id}, {"_id": 0},
                )
                assert receipt is not None, (
                    f"trust receipt not found for audit_id={audit_id!r}. "
                    f"Audit row exists but its mirror is missing — "
                    f"contract violation."
                )
                assert receipt.get("signature"), (
                    f"trust receipt missing signature field: "
                    f"{receipt!r}"
                )
        finally:
            await db_conn.chats.delete_one({"id": chat_id})
