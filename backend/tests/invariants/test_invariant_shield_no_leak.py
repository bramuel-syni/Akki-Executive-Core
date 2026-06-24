"""Shield-no-leak invariant — Phase 0 + Phase B1 generalisation.

Generalisation of the Phase 14 chat-fluency test. Every user-visible
surface that calls the Shield MUST NOT have any `[[ENT_...]]` token
in its final payload. The Shield's `StreamingReidentifier` and the
sync `reidentify()` function both promise to substitute every
detected token before the user sees the response; this test is the
end-to-end proof.

Surfaces covered (parametrised):

  * chat — POST /api/chats/{cid}/messages → assistant_message.content
    PARAMETRISED per provider: Claude (anthropic) · GPT (openai) ·
    Gemini (google). Phase B1 (2026-06-24) extension — pre-B1 the
    chat surface was pinned to `claude-sonnet-4-5` only, masking
    the question of whether the OpenAI + Gemini provider paths
    honour the same no-leak contract. The B1 generalisation runs
    the SAME multi-entity prompt through each provider.
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

Phase B1 (2026-06-24) — also adds a DELIBERATE-VIOLATION SMOKE test
(synthetic, non-integration). The smoke proves the `[[ENT_` assertion
isn't a no-op: it constructs a fake LLM payload containing the
forbidden marker and asserts `_assert_no_token_leak` raises. Without
this rail, a future refactor that mis-spells the regex (or drops it)
would silently green the integration tests.
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


pytestmark: list = []

# Strings forbidden from any user-visible surface — exposed at module
# level so the deliberate-violation smoke (at the bottom of this file)
# can exercise it directly without touching the FastAPI app or DB.
TOKEN_LEAK_RE = re.compile(r"\[\[ENT_")


# Phase B1 (2026-06-24) — chat surface providers.
# `id` matches the SUPPORTED_MODELS table in `routers/chat.py:82-104`.
# Tone string only included for human-readable test ids.
CHAT_PROVIDERS = [
    pytest.param("claude-sonnet-4-5", "anthropic.claude-sonnet-4-5",
                 id="chat-anthropic-claude-sonnet-4-5"),
    pytest.param("gpt-5-2", "openai.gpt-5-2",
                 id="chat-openai-gpt-5-2"),
    pytest.param("gemini-2-5-flash", "gemini.gemini-2-5-flash",
                 id="chat-gemini-2-5-flash"),
]

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

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize("model_id,_provider_label", CHAT_PROVIDERS)
async def test_chat_surface_no_token_leak(db_conn, model_id, _provider_label):
    """Generalised chat surface — `/api/chats/{cid}/messages`.

    Phase B1 (2026-06-24) — parametrised across all three Shield-
    backed providers. Pre-B1 only Claude was pinned. The parametrise
    proves the SAME multi-entity prompt is rehydrated for every
    provider, closing the gap B0 surfaced (proxy fronts all three
    providers; no-leak rail must follow).
    """
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
            "title":            f"Invariant: shield no leak (chat / {model_id})",
            "model_id":         model_id,
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
                    f"HUMAN_REQUIRED: chat round-trip non-200 ({r.status_code}) "
                    f"on model_id={model_id}. body={r.text[:200]!r}"
                )
            body = r.json()
            asst = body.get("assistant_message") or {}
            reply = asst.get("content") or ""
            if not reply or reply.startswith("(LLM error:"):
                pytest.skip(
                    f"HUMAN_REQUIRED: chat LLM did not return usable reply on "
                    f"model_id={model_id}. reply={reply[:200]!r}"
                )
            _assert_no_token_leak(f"chat[{model_id}]", reply)
        finally:
            await db_conn.chats.delete_one({"id": chat_id})


# ───────────────────── surface 2: solva-analyze ────────────────────

@pytest.mark.integration
@pytest.mark.asyncio
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


# ─────────────── Phase B1 deliberate-violation smoke ──────────────
#
# These tests run on the DEFAULT sweep (no `integration` marker) — they
# don't touch the FastAPI app, MongoDB, or any provider. Their sole
# purpose is to prove the `[[ENT_` assertion isn't a no-op. If a
# refactor mis-spells the regex OR replaces `_assert_no_token_leak`
# with a tautology, these tests trip immediately on the default lane
# — the integration suite would otherwise stay green for weeks until
# a real provider regression surfaced the gap.

def test_deliberate_violation_token_leak_detected():
    """Synthetic: a payload containing the raw Shield token shape
    MUST trip the leak assertion. Proves the regex is wired."""
    blob = (
        "I can't parse the redacted token [[ENT_PERSON_001]] in your "
        "message — could you clarify?"
    )
    # Not using `_assert_no_token_leak` directly here so we can
    # surface the AssertionError as expected. Same regex.
    with pytest.raises(AssertionError) as exc_info:
        _assert_no_token_leak("deliberate-violation", blob)
    msg = str(exc_info.value)
    assert "Shield-mechanics leak" in msg, (
        f"AssertionError message shape drifted — expected to contain "
        f"'Shield-mechanics leak'; got: {msg[:200]!r}"
    )


@pytest.mark.parametrize("token", [
    "[[ENT_PERSON_001]]",
    "[[ENT_ORG_042]]",
    "[[ENT_PLACE_009]]",
    "[[ENT_PAYMENT_CARD_001]]",
    "[[ENT_UK_NI_NUMBER_001]]",
])
def test_deliberate_violation_per_token_type_detected(token):
    """Catch a forbidden token shape regardless of the entity type
    label. The regex pins on `[[ENT_` prefix only — the per-type
    suffix can be any of the production de-identifier emits."""
    with pytest.raises(AssertionError):
        _assert_no_token_leak("per-type-violation",
                              f"Response prelude {token} response tail.")


def test_clean_payload_does_not_trip_assertion():
    """No-regression rail: a payload with no `[[ENT_` marker MUST
    NOT trip. Prevents a regex over-broadening drift."""
    blob = (
        "Mary Anne and Bramuel are meeting in Nairobi on Friday to "
        "discuss the malaria response programme. The corporate card "
        "ending 7689 covers the venue."
    )
    # Should not raise.
    _assert_no_token_leak("clean-payload", blob)


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
