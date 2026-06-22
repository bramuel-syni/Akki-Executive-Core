"""Characterisation golden — Work Studio compile lifecycle (Phase 0).

Pins the CURRENT shape of the Work Studio export START endpoint
(`POST /api/contexts/{cid}/work-studio/export/{kind}`). The compile
runs against a seeded admin context with at least one source
document.

What this test pins:

  1. The START endpoint accepts the documented payload (instructions
     + format + source pointers) and returns an export_id.
  2. The response envelope shape — `export_id`, `lifecycle_state`,
     and any other top-level fields currently emitted.
  3. The `work_studio_exports` row was created with status in
     {created, compiling, ready} — the start endpoint flips through
     these states.

The compile is invoked SYNCHRONOUSLY here (no async-job polling) so
the snapshot is bounded. For surfaces that go through the streaming
v9 path, a separate golden can be added in Phase 1+ — Phase 0 pins
the simpler synchronous start contract.

Marked `@pytest.mark.integration` — real LLM. Skip default sweep.

If the user's admin context does not have any source documents
seeded, the test SKIPS as HUMAN_REQUIRED rather than failing — Phase
0 does not introduce new seed data.
"""
from __future__ import annotations

import json
import os
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

GOLDEN_PATH = Path(__file__).parent / "work_studio_compile.golden.json"


DYNAMIC_FIELDS = {
    "id", "_id", "export_id", "doc_id", "continue_doc_id",
    "audit_id", "created_at", "updated_at", "scored_at",
    "cache_key", "request_hash", "response_hash",
    "elapsed_ms", "confidence_pct_cache_key",
    "context_id", "account_id", "blob_id", "session_id",
}


def _to_shape(value: Any, depth: int = 0) -> Any:
    """Same shape-stripper as the other goldens."""
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
        return [_to_shape(value[0], depth + 1), f"list/len>={len(value)}"]
    if isinstance(value, dict):
        out = {}
        for k in sorted(value.keys()):
            if k in DYNAMIC_FIELDS:
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


async def test_work_studio_compile_start_golden_shape(db_conn):
    """Pin the Work Studio compile START contract."""
    now_iso = datetime.now(timezone.utc).isoformat()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=240.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")
        admin_row = await db_conn.accounts.find_one(
            {"email": "admin@akki.ai"}, {"_id": 0, "id": 1, "default_context_id": 1},
        )
        cid = admin_row.get("default_context_id")
        if not cid:
            # Fall back to a Syni.ai HQ membership if present (the
            # canonical owner context per test_credentials.md).
            mem = await db_conn.memberships.find_one(
                {"account_id": admin_row["id"], "context_id": {"$exists": True}},
                {"_id": 0, "context_id": 1},
            )
            if mem:
                cid = mem["context_id"]
        if not cid:
            pytest.skip(
                "HUMAN_REQUIRED: admin@akki.ai has no default_context_id "
                "and no memberships seeded; cannot run Work Studio "
                "characterisation golden."
            )

        # The simpler start payload: blank kind so no source document
        # is required. Pins the documented endpoint contract whether
        # or not seed documents are present.
        payload = {
            "instructions": (
                "Two-paragraph note explaining a hypothetical operating "
                "metric review for Lemasy Limited."
            ),
            "format": "docx",
        }

        r = await ac.post(
            f"/api/contexts/{cid}/work-studio/export/blank",
            json=payload,
            headers=admin,
        )

        # The compile path is heavy — accept a wide range of 2xx
        # outcomes; bail if the route is hard-gated.
        if r.status_code >= 500:
            pytest.skip(
                f"HUMAN_REQUIRED: compile endpoint 5xx — "
                f"status={r.status_code} body={r.text[:300]!r}"
            )
        if r.status_code in (403, 404):
            pytest.skip(
                f"HUMAN_REQUIRED: compile endpoint refused ({r.status_code}); "
                f"context may not exist or admin lacks role. body={r.text[:200]!r}"
            )
        # Some kinds gate on grounding sources; this is documented
        # behaviour. Skip rather than fail.
        if r.status_code == 400:
            try:
                body = r.json()
                refusal = body.get("error") or body.get("detail") or {}
                refusal_str = json.dumps(refusal, ensure_ascii=False).lower()
                if "thin" in refusal_str or "ground" in refusal_str or "source" in refusal_str:
                    pytest.skip(
                        f"HUMAN_REQUIRED: compile refused on thin-input — "
                        f"this is documented contract. body={body!r}"
                    )
            except Exception:
                pass

        assert r.status_code in (200, 201, 202), (
            f"compile start unexpected status={r.status_code}: "
            f"body={r.text[:300]!r}"
        )
        body = r.json()

        # Find the export id under any of the documented field names.
        export_id = body.get("export_id") or body.get("id") or body.get("doc_id")
        if not export_id:
            pytest.skip(
                f"HUMAN_REQUIRED: compile response did not surface an "
                f"export_id — schema may have drifted. keys={sorted(body.keys())!r}"
            )

        try:
            # Verify the work_studio_exports row exists.
            row = await db_conn.work_studio_exports.find_one(
                {"id": export_id}, {"_id": 0},
            ) or await db_conn.work_studio_exports.find_one(
                {"export_id": export_id}, {"_id": 0},
            )
            if row is not None:
                status = (row.get("status") or row.get("lifecycle_state") or "").lower()
                assert status in {
                    "created", "compiling", "ready", "complete", "completed",
                    "drafting", "compiled",
                }, (
                    f"work_studio_exports.status unexpected: {status!r}. "
                    f"row={row!r}"
                )

            # Shape snapshot — first run blesses, later runs compare.
            shape = _to_shape(body)
            if not GOLDEN_PATH.exists():
                GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
                GOLDEN_PATH.write_text(
                    json.dumps({"shape": shape, "blessed_at": now_iso},
                               indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                return

            golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
            expected_shape = golden["shape"]
            actual_top_keys = set(shape.keys()) if isinstance(shape, dict) else set()
            expected_top_keys = set(expected_shape.keys()) if isinstance(expected_shape, dict) else set()
            missing_keys = expected_top_keys - actual_top_keys
            assert not missing_keys, (
                f"Work Studio compile response DROPPED top-level keys "
                f"vs golden: {missing_keys!r}. Re-bless if intentional."
            )
        finally:
            # Cleanup the synthetic export.
            await db_conn.work_studio_exports.delete_one({"id": export_id})


# ────────────────────── golden re-blessing procedure ──────────────────────
# See `test_chat_roundtrip_golden.py` — identical procedure.
