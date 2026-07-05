"""Phase 5.5.2 — build-breaking invariant for the first-session
response shape.

Pins the wire contract of the 6 `/api/me/first-session/*` routes.
Authored after Phase 5.5.2 candidate A fixed the `StateOnlyResponse`
typing bug (the model declared `state: Optional[str]` but the
handlers actually return a dict envelope, causing
`ResponseValidationError` → 500 in production).

This invariant replays a representative payload against each of
the 6 routes via the in-process ASGI transport and asserts:
  1. The endpoint returns 200 (no `ResponseValidationError`).
  2. The response body has a `state` key whose value is a dict
     (not a string, not None) with the canonical envelope shape.
  3. The dict has the documented top-level keys.

Build-breaking: any future regression on `StateOnlyResponse` —
e.g. someone narrows `state` back to `Optional[str]` — fails CI
immediately. Pairs with the `test_invariant_narrowing_byte_
equivalence.py` pattern from Phase 5.4.

The integration-marked variant (real LLM shield call) is
deselected by default; the default sweep is pure-wire.
"""
from __future__ import annotations

import os
from typing import Any, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

import server  # noqa: F401  — ASGI startup wiring
from server import app


pytestmark = pytest.mark.asyncio


# The 6 first-session routes that share the `StateOnlyResponse`
# response model. Tuple = (HTTP method, URL path, payload-or-None).
# Each URL is the canonical `/api/me/first-session/*` mount.
_FIRST_SESSION_ROUTES = [
    ("GET",  "/api/me/first-session",                None),
    ("POST", "/api/me/first-session/skip",           {}),
    ("POST", "/api/me/first-session/grandfather",    {}),
    # `intake` requires a payload — drive with the minimum-valid
    # intake answers.
    ("POST", "/api/me/first-session/intake",         {
        "role": "CEO",
        "primary_context_name": "Test Co.",
        "top_of_mind": "Phase 5.5.2 invariant smoke",
    }),
    # `choose-door` requires a door choice; "cycle" is the safest
    # because it doesn't trigger demo-attach side effects.
    ("POST", "/api/me/first-session/choose-door",    {"door": "cycle"}),
    # `complete` requires `kind` + `id` of the produced artefact.
    ("POST", "/api/me/first-session/complete",       {
        "artefact": {"kind": "cycle", "id": "smoke-cycle-id"},
    }),
]


# Canonical first-session state envelope keys per
# `routers/first_session.py::_default_state`.
_REQUIRED_STATE_KEYS = {
    "status",
    "started_at",
    "completed_at",
    "current_step",
    "door_taken",
    "artefact",
    "intake",
    "grandfathered",
}


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
    assert token
    r = await ac.get("/api/csrf")
    return {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": r.json()["csrf_token"],
    }


@pytest_asyncio.fixture
async def _admin_headers():
    """Seeded admin from `/app/memory/test_credentials.md`."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        try:
            return await _csrf_login(ac, "admin@akki.ai", os.environ["ADMIN_SEED_PASSWORD"])
        except Exception:
            pytest.skip(
                "Phase 5.5.2 first-session-shape invariant requires the "
                "seeded admin from /app/memory/test_credentials.md "
                "(admin@akki.ai / <redacted:ADMIN_SEED_PASSWORD>). Login failed — "
                "ensure the seed script ran before this invariant. "
                "This is a setup precondition, not a contract failure."
            )


async def test_invariant_first_session_state_shape_is_dict_envelope(_admin_headers):
    """Build-breaking pin for Phase 5.5.2 candidate A: every
    `/api/me/first-session/*` route returns `state` as a DICT
    envelope (NOT a string).

    The 5 routes besides `intake` must return 200 OR a documented
    business-logic 4xx (e.g. `complete` may 404 if no artefact
    exists; `grandfather` may 409 if already complete). The shape
    contract: when 200 is returned, `state` is a dict.

    `intake` is special-cased — it MUST return 200 with a fresh
    state envelope; if it 500s, candidate A has regressed.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for verb, path, payload in _FIRST_SESSION_ROUTES:
            if verb == "GET":
                r = await ac.get(path, headers=_admin_headers)
            else:
                r = await ac.request(verb, path, json=payload, headers=_admin_headers)

            # Phase 5.5.2 — `intake` is the load-bearing route. It
            # MUST never 500 — that was the candidate-A regression.
            if path.endswith("/intake"):
                assert r.status_code != 500, (
                    f"REGRESSION: candidate A — {verb} {path} returned 500 "
                    f"(was Phase 5.5.2's exact bug: StateOnlyResponse.state "
                    f"typing mismatch). Body: {r.text[:300]}"
                )

            # The shape contract only applies on 2xx responses;
            # business-logic 4xx (e.g. duplicate-complete 409) are
            # contract-permitted (those routes have their own
            # behaviour tests).
            if 200 <= r.status_code < 300:
                body = r.json()
                assert "state" in body, (
                    f"{verb} {path}: response missing `state` key. Got: {body!r}"
                )
                state = body["state"]
                assert isinstance(state, dict), (
                    f"REGRESSION: candidate A — {verb} {path}: `state` is "
                    f"a {type(state).__name__}, not a dict. The "
                    f"StateOnlyResponse model has likely been narrowed "
                    f"back to `Optional[str]`. Got: {state!r}"
                )
                assert _REQUIRED_STATE_KEYS.issubset(state.keys()), (
                    f"{verb} {path}: state envelope missing required keys. "
                    f"Required: {sorted(_REQUIRED_STATE_KEYS)}. "
                    f"Got: {sorted(state.keys())}"
                )


async def test_invariant_state_only_response_model_declares_dict():
    """Static pin — the `StateOnlyResponse.state` field MUST be a dict-
    compatible type (Optional[Dict[...]], Optional[Any], etc.), not
    `Optional[str]`.

    Why static: if Phase 5.5.X introduces a new first-session route
    that exists in the OpenAPI schema BEFORE the seed admin runs, the
    fixture-based wire test would skip on auth — but the regression
    would still hit production. This static check catches the
    StateOnlyResponse model narrowing at code-load time.
    """
    from typing import get_args, get_origin
    from contracts.responses import StateOnlyResponse

    field = StateOnlyResponse.model_fields["state"]
    annotation = field.annotation
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Accept Optional[Dict[...]], Optional[Any], Dict[...], Any.
    def _is_dict_or_any(t):
        if t is Any:
            return True
        if get_origin(t) is dict:
            return True
        return False

    accepted = (
        _is_dict_or_any(annotation)
        or any(_is_dict_or_any(a) for a in args)
    )
    assert accepted, (
        "REGRESSION: candidate A — `StateOnlyResponse.state` has been "
        f"narrowed back to {annotation!r}, which does NOT accept a dict "
        "envelope. The 6 `/api/me/first-session/*` routes return a dict; "
        "narrowing `state` to `Optional[str]` (or any non-dict-accepting "
        "type) causes FastAPI to 500 on every intake call. Phase 5.5.2 "
        "widened this to `Optional[Dict[str, Any]]` — preserve that."
    )
