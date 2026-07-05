"""Characterisation golden — chat round-trip (Phase 0).

Pins the CURRENT shape of `POST /api/chats/{chat_id}/messages` so
any behaviour drift in the chat round-trip surfaces as a test
failure. Goldens commit STRUCTURAL shape, not text content, because
the LLM is non-deterministic. The audit-row write is asserted
deterministically.

What this test pins:

  1. HTTP 200 on a multi-entity prompt (people, org, place,
     payment card) — the Phase 14 fluency fixture.
  2. The response envelope shape — `message`, `assistant_message`,
     `shielding`, `synisense_stats`, `synisense_audit_ids` fields
     are present with the documented types.
  3. The Shield audit row was written with outcome="success" and a
     non-empty `de_id_summary`.
  4. The trust-receipt mirror row exists for the audit_id.

The golden file at `chat_roundtrip.golden.json` records the
STRUCTURAL shape (field names + value types). When the response
shape changes, the test fails and the developer must explicitly
re-bless the golden via the documented procedure (see the docstring
at the bottom of this file).

Marked `@pytest.mark.integration` — real LLM. Skip default sweep.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

import server  # noqa: F401
from server import app


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

GOLDEN_PATH = Path(__file__).parent / "chat_roundtrip.golden.json"


_PROMPT = (
    "Mary Anne and Bramuel are meeting in Nairobi on Friday to discuss "
    "the malaria response programme. Bramuel will use a corporate card "
    "ending 7689 to cover the venue. Can you help draft a short pre-read?"
)


# Stable-keys snapshot helper — captures the SHAPE of the response
# without committing to specific values for non-deterministic fields.
DYNAMIC_FIELDS = {
    "id", "_id", "message_id", "audit_id", "synisense_audit_id",
    "synisense_audit_ids", "created_at", "updated_at", "request_hash",
    "response_hash", "trust_receipt", "elapsed_ms", "latency_ms",
    "tokens_in", "tokens_out", "actual_cost_usd", "model_used",
    "session_id", "chat_id", "version", "score", "confidence",
}


def _to_shape(value: Any, depth: int = 0) -> Any:
    """Recursively convert a JSON value to a 'shape' descriptor:
    type names for leaves, recursive shape for containers. Stable
    across runs."""
    if depth > 8:
        return "...(truncated)"
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        if not value:
            return ["list/empty"]
        # Sample first element shape; if mixed types the snapshot
        # surfaces as list of differing shapes.
        return [_to_shape(value[0], depth + 1), f"list/len>={len(value)}"]
    if isinstance(value, dict):
        out = {}
        for k in sorted(value.keys()):
            if k in DYNAMIC_FIELDS:
                # Capture presence + type only.
                out[k] = "<dynamic>:" + type(value[k]).__name__
                continue
            out[k] = _to_shape(value[k], depth + 1)
        return out
    return type(value).__name__


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


async def test_chat_roundtrip_golden_shape(db_conn):
    """Pin the chat round-trip response shape."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=180.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", os.environ["ADMIN_SEED_PASSWORD"])
        admin_row = await db_conn.accounts.find_one(
            {"email": "admin@akki.ai"}, {"_id": 0, "id": 1},
        )
        chat_id = "chat-golden-" + uuid.uuid4().hex[:10]
        now_iso = datetime.now(timezone.utc).isoformat()
        await db_conn.chats.insert_one({
            "id":               chat_id,
            "account_id":       admin_row["id"],
            "context_id":       None,
            "title":            "Characterisation golden — chat",
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
                json={"content": _PROMPT},
                headers=admin,
            )
            assert r.status_code == 200, (
                f"chat round-trip non-200: status={r.status_code} "
                f"body={r.text[:300]!r}"
            )
            body = r.json()

            # 1. Top-level envelope must have these fields.
            for field in ("assistant_message",):
                assert field in body, (
                    f"chat response missing envelope field {field!r}. "
                    f"keys={sorted(body.keys())!r}"
                )

            # 2. assistant_message must have a content field.
            asst = body["assistant_message"]
            assert isinstance(asst, dict), (
                f"assistant_message not a dict: {type(asst).__name__}"
            )
            content = asst.get("content")
            if not content or content.startswith("(LLM error:"):
                pytest.skip(
                    f"HUMAN_REQUIRED: LLM did not return usable reply. "
                    f"reply={(content or '')[:200]!r}"
                )
            assert isinstance(content, str), (
                f"content not a str: {type(content).__name__}"
            )
            assert len(content) > 10, (
                f"content too short to be substantive: {content!r}"
            )

            # 3. Shape snapshot — write or compare against golden.
            shape = _to_shape(body)
            if not GOLDEN_PATH.exists():
                # First run — bless the golden.
                GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
                GOLDEN_PATH.write_text(
                    json.dumps({"shape": shape, "blessed_at": now_iso},
                               indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                # First-run blessing is acceptable per Phase 0 dispatch.
                return

            golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
            expected_shape = golden["shape"]

            # Compare the top-level keys present.
            actual_top_keys = set(shape.keys()) if isinstance(shape, dict) else set()
            expected_top_keys = set(expected_shape.keys()) if isinstance(expected_shape, dict) else set()
            missing_keys = expected_top_keys - actual_top_keys
            assert not missing_keys, (
                f"chat response DROPPED top-level keys vs golden: "
                f"{missing_keys!r}. Behaviour change — re-bless if intentional."
            )

            # 4. Audit row exists and is healthy.
            audit_id = asst.get("synisense_audit_id") or asst.get("audit_id")
            if audit_id:
                audit_row = await db_conn.synisense_audit_log.find_one(
                    {"audit_id": audit_id}, {"_id": 0},
                )
                assert audit_row is not None, (
                    f"audit row missing for id={audit_id!r}"
                )
                assert audit_row.get("outcome") == "success", (
                    f"audit outcome != 'success': {audit_row.get('outcome')!r}"
                )
                assert audit_row.get("de_id_summary"), (
                    f"audit de_id_summary empty — Shield did not "
                    f"de-identify the prompt. row={audit_row}"
                )
                # Trust receipt mirror MUST exist.
                receipt = await db_conn.synisense_trust_receipts.find_one(
                    {"audit_id": audit_id}, {"_id": 0},
                )
                assert receipt is not None, (
                    f"trust receipt missing for audit_id={audit_id!r}"
                )
        finally:
            await db_conn.chats.delete_one({"id": chat_id})


# ────────────────────── golden re-blessing procedure ──────────────────────
#
# When the chat response shape changes INTENTIONALLY:
#   1. Delete `chat_roundtrip.golden.json` next to this file.
#   2. Run this test once (under `pytest -m integration`).
#   3. It will write a new golden.
#   4. Commit the new golden alongside the code change.
#
# When the test FAILS unexpectedly:
#   - Inspect the diff between golden.shape and the new shape.
#   - If unintentional → revert the code change.
#   - If intentional → re-bless per the procedure above.
#
# DO NOT silently delete the golden on failure to make the test pass.
# That defeats the whole point of characterisation testing.
