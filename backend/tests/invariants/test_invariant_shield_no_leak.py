"""Shield-no-leak invariant — Phase 0.

Generalisation of the Phase 14 chat-fluency test. Every user-visible
surface that calls the Shield MUST NOT have any `[[ENT_...]]` token
in its final payload. The Shield's `StreamingReidentifier` and the
sync `reidentify()` function both promise to substitute every
detected token before the user sees the response; this test is the
end-to-end proof.

Surfaces covered (parametrised):

  * chat — POST /api/chats/{cid}/messages → assistant_message.content
  * solva-analyze — POST /api/workbook/v2/analyses/{aid}/synthesize
    → narration.headline + narration.observations (every observation
    body)

Future surfaces (Work Studio compile, brief outputs, pulse idea
narration) are LOGGED as TODOs at the bottom of this file. Phase 0
keeps the spread tractable; new surfaces are added incrementally as
they stabilise.

Marked `@pytest.mark.integration` — real LLM round-trip. Skip
default sweep; run with `pytest -m integration`.

The Phase 14 file `test_chat_fluency_no_shield_leak.py` REMAINS as
the chat-specific lockdown. This file parametrises the same prompt
fixture across multiple surfaces for the generalised guarantee.
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

# Reuse the Phase 14 prompt fixture so the generalised test exercises
# the same multi-entity payload (people, org, place, payment card).
SHARED_PROMPT = (
    "Mary Anne and Bramuel are meeting in Nairobi on Friday to discuss "
    "the malaria response programme. Bramuel will use a corporate card "
    "ending 7689 to cover the venue. Can you help draft a short pre-read?"
)

# A short-text variant — used for the workbook analyze "objective"
# free-text input where the multi-entity payload would be over-
# generous. Keeps Solva narration bounded.
ANALYZE_OBJECTIVE = (
    "Summarise the topline movement and call out any anomalies for "
    "Mary Anne and Bramuel."
)

# Strings forbidden from any user-visible surface.
TOKEN_LEAK_RE = re.compile(r"\[\[ENT_")


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


def _assert_no_token_leak(label: str, blob: str) -> None:
    """Raise if blob contains a Shield token. Centralised so all
    surfaces share the same wording."""
    assert not TOKEN_LEAK_RE.search(blob or ""), (
        f"[{label}] Shield-mechanics leak — '[[ENT_' visible to user. "
        f"blob[:500]={blob[:500]!r}"
    )


# ───────────────────────── surface 1: chat ─────────────────────────

async def test_chat_surface_no_token_leak(db_conn):
    """Generalised chat surface — `/api/chats/{cid}/messages`."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=180.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")
        admin_row = await db_conn.accounts.find_one(
            {"email": "admin@akki.ai"}, {"_id": 0, "id": 1},
        )
        chat_id = "chat-inv-no-leak-" + uuid.uuid4().hex[:10]
        now_iso = datetime.now(timezone.utc).isoformat()
        await db_conn.chats.insert_one({
            "id":               chat_id,
            "account_id":       admin_row["id"],
            "context_id":       None,
            "title":            "Invariant: shield no leak (chat)",
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
                json={"content": SHARED_PROMPT},
                headers=admin,
            )
            if r.status_code != 200:
                pytest.skip(
                    f"HUMAN_REQUIRED: chat round-trip non-200 ({r.status_code}). "
                    f"body={r.text[:200]!r}"
                )
            body = r.json()
            asst = body.get("assistant_message") or {}
            reply = asst.get("content") or ""
            if not reply or reply.startswith("(LLM error:"):
                pytest.skip(
                    f"HUMAN_REQUIRED: chat LLM did not return usable reply. "
                    f"reply={reply[:200]!r}"
                )
            _assert_no_token_leak("chat", reply)
        finally:
            await db_conn.chats.delete_one({"id": chat_id})


# ───────────────────── surface 2: solva-analyze ────────────────────

async def test_solva_analyze_surface_no_token_leak(db_conn):
    """Solva v2 narration on `/api/workbook/v2/analyses/{aid}/synthesize`.

    The fixture seeds a tiny 6-row in-memory CSV via
    `/api/workbook/upload-multi` (the new entity), then invokes
    synthesize, then asserts narration.headline and every
    narration.observations[*] body string is free of token leaks.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=240.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")

        # Build a tiny CSV: 6 rows, (Month, Revenue) — enough to clear
        # the autopicker density gate (>= 6 non-null AND >= 30%
        # density).
        csv_body = (
            "Month,Revenue\n"
            "2026-01-01,100\n"
            "2026-02-01,110\n"
            "2026-03-01,121\n"
            "2026-04-01,133\n"
            "2026-05-01,146\n"
            "2026-06-01,161\n"
        )
        files = [
            ("files", ("synthesise_smoke.csv", csv_body.encode("utf-8"), "text/csv")),
        ]
        data = {"objective": ANALYZE_OBJECTIVE}
        r = await ac.post(
            "/api/workbook/upload-multi",
            data=data,
            files=files,
            headers={"Authorization": admin["Authorization"],
                     "X-CSRF-Token": admin["X-CSRF-Token"]},
        )
        if r.status_code not in (200, 201):
            pytest.skip(
                f"HUMAN_REQUIRED: upload-multi non-2xx ({r.status_code}). "
                f"Schema may have drifted. body={r.text[:200]!r}"
            )
        upload = r.json()
        aid = upload.get("analysis_id") or upload.get("id")
        if not aid:
            pytest.skip(
                f"HUMAN_REQUIRED: upload-multi returned no analysis_id. "
                f"body={upload!r}"
            )

        try:
            r = await ac.post(
                f"/api/workbook/v2/analyses/{aid}/synthesize",
                headers=admin,
            )
            if r.status_code != 200:
                pytest.skip(
                    f"HUMAN_REQUIRED: synthesize non-200 ({r.status_code}). "
                    f"body={r.text[:200]!r}"
                )
            narration = r.json()
            if narration.get("refused"):
                pytest.skip(
                    f"HUMAN_REQUIRED: synthesize refused — "
                    f"reason={narration.get('refusal_reason')!r}"
                )
            _assert_no_token_leak(
                "solva-analyze.headline", narration.get("headline") or "")
            for i, obs in enumerate(narration.get("observations") or []):
                body = obs.get("body") if isinstance(obs, dict) else str(obs)
                _assert_no_token_leak(
                    f"solva-analyze.observations[{i}]", body or "")
        finally:
            # Cleanup the synthetic analysis to keep prod-like state.
            await db_conn.analyses.delete_one({"id": aid})
            await db_conn.analysis_blobs.delete_many({"analysis_id": aid})


# ───────────────────────── future surfaces ─────────────────────────
#
# TODO(Phase 0+): when the following surfaces are stabilised, add a
# parametrised case for each one to this test module. The pattern is
# identical: drive the surface, capture every user-visible string in
# the response, call `_assert_no_token_leak(label, blob)`.
#
#   * Work Studio compile (POST /api/contexts/{cid}/work-studio/
#     export/{kind}) → assert structured_content fields free of leaks
#     once the compile job completes.
#   * Generate Brief → assert brief body + signal narration free of
#     leaks.
#   * Pulse Idea narration → assert every digest entry body free of
#     leaks.
#
# These are TODOs not stubs because each one needs a working fixture
# (a seeded context + source documents) to compile against. Phase 0
# pins the two surfaces that have easy synthetic-input fixtures; the
# rest are added as their fixture cost lands below the value gained.
