"""Phase 4.2 — HTTP transport smoke test.

Exercises the cross-context contract layer in `BOUNDED_CONTEXT_TRANSPORT=http`
mode by:

  1. Booting an httpx-backed adapter for Akki and SyniSense.
  2. Issuing one Akki contract call (`count_documents`) — represents
     Solva → Akki and SyniSense-engine → Akki traffic.
  3. Issuing one SyniSense contract call (`get_signal`) — represents
     Solva → SyniSense traffic.
  4. Verifying:
     a. The transport secret is enforced (401 without `X-Internal-Auth`).
     b. With the secret, calls succeed and return the expected DTO shape.
     c. The retry/timeout policy is in place
        (`INTERNAL_TRANSPORT_RETRIES=3`, `INTERNAL_TRANSPORT_TIMEOUT_S=5`).
     d. The OpenAPI surface is unchanged (internal endpoints are
        excluded from `include_in_schema`).

The internal transport is mounted on the SAME uvicorn host
(`127.0.0.1:8001`) in Phase 4.2 single-process mode; Phase 4.3 will
split each context onto its own port. Flipping the toggle then is
just an env var change.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
import urllib.request
from pathlib import Path

import pytest


SUPERVISOR_HOST = "http://127.0.0.1:8001"


def _http_get(url: str, headers: dict[str, str] | None = None, timeout_s: float = 10.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode("utf-8") if e.fp else "")


def _http_post_json(url: str, body: dict, headers: dict[str, str] | None = None, timeout_s: float = 10.0) -> tuple[int, str]:
    payload = json.dumps(body).encode("utf-8")
    h = dict(headers or {})
    h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=payload, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode("utf-8") if e.fp else "")


@pytest.fixture(scope="module")
def transport_secret() -> str:
    """Generate (or reuse) a shared secret + push it into the running
    backend's process env via the running uvicorn's environment.

    The supervisor-managed backend reads `INTERNAL_TRANSPORT_SECRET`
    at request time (not at import time), so setting it here in the
    test process AND in the supervisor's env via a sidecar mechanism
    isn't possible. Instead we read the value the backend already has
    (if any) by sending a no-auth request and asserting 503 is
    returned when the env is unset, or 401 when it's set.
    """
    return os.environ.get("INTERNAL_TRANSPORT_SECRET", "")


def test_internal_transport_endpoints_excluded_from_openapi() -> None:
    """The /api/internal/v1/<context>/* endpoints must NOT appear in
    the public OpenAPI document — preserves the Phase 4.1 byte-
    identical surface contract."""
    status, body = _http_get(f"{SUPERVISOR_HOST}/api/openapi.json")
    assert status == 200
    spec = json.loads(body)
    paths = list(spec.get("paths", {}).keys())
    internal_paths = [p for p in paths if "/internal/" in p]
    assert internal_paths == [], (
        f"Phase 4.2 invariant: internal transport paths must be "
        f"excluded from public OpenAPI; found: {internal_paths!r}"
    )


def test_internal_transport_openapi_hash_unchanged() -> None:
    """The exact `paths_sha256[:16]` set by Phase 4.1 close must
    remain stable through Phase 4.2. The sha is computed over the
    sorted path list (no body, no methods)."""
    EXPECTED = "cdcb23322bb82895"  # Phase 4.1 close ratchet
    status, body = _http_get(f"{SUPERVISOR_HOST}/api/openapi.json")
    assert status == 200
    spec = json.loads(body)
    paths = sorted(spec.get("paths", {}).keys())
    h = hashlib.sha256("\n".join(paths).encode()).hexdigest()[:16]
    assert h == EXPECTED, (
        f"OpenAPI surface drift! expected={EXPECTED} got={h} "
        f"(paths={len(paths)})"
    )


def test_internal_transport_fails_closed_without_secret(transport_secret: str) -> None:
    """When `INTERNAL_TRANSPORT_SECRET` is not set in the backend
    env, the transport returns 503; when it IS set but the request
    omits the header (or sends a wrong value), the transport
    returns 401."""
    url = f"{SUPERVISOR_HOST}/api/internal/v1/akki/method/count_documents"
    status, body = _http_post_json(url, {"account_id": "test"})
    if not transport_secret:
        # Backend has no secret configured — must fail-closed at 503.
        assert status == 503, (
            f"Phase 4.2: missing INTERNAL_TRANSPORT_SECRET should "
            f"return 503, got {status}: {body[:200]}"
        )
    else:
        # Secret configured but header missing — must be 401.
        assert status == 401, (
            f"Phase 4.2: missing X-Internal-Auth header should "
            f"return 401, got {status}: {body[:200]}"
        )


def test_internal_transport_rejects_wrong_secret(transport_secret: str) -> None:
    """A wrong `X-Internal-Auth` value must return 401 (or 503 if
    backend has no secret configured at all)."""
    url = f"{SUPERVISOR_HOST}/api/internal/v1/synisense/method/get_signal"
    status, body = _http_post_json(
        url,
        {"account_id": "test", "signal_id": "x", "untenanted": True},
        headers={"X-Internal-Auth": "definitely-wrong-secret-" + secrets.token_hex(8)},
    )
    if not transport_secret:
        assert status == 503
    else:
        assert status == 401, (
            f"Phase 4.2: wrong X-Internal-Auth must return 401, "
            f"got {status}: {body[:200]}"
        )


@pytest.mark.skipif(
    not os.environ.get("INTERNAL_TRANSPORT_SECRET"),
    reason="HTTP-mode end-to-end smoke requires INTERNAL_TRANSPORT_SECRET to be set in the backend env",
)
def test_http_mode_akki_count_documents_round_trip(transport_secret: str) -> None:
    """One Akki contract call exercised via HTTP — proves Solva → Akki
    + SyniSense-engine → Akki round-trip works end-to-end."""
    url = f"{SUPERVISOR_HOST}/api/internal/v1/akki/method/count_documents"
    status, body = _http_post_json(
        url,
        {"account_id": "smoke-account-id-" + secrets.token_hex(4)},
        headers={"X-Internal-Auth": transport_secret},
    )
    assert status == 200, f"unexpected status {status}: {body[:200]}"
    payload = json.loads(body)
    assert "result" in payload
    # Result is an int (count_documents returns int). For an unknown
    # account id the count should be 0 (no rows).
    assert isinstance(payload["result"], int), (
        f"expected int from count_documents; got {type(payload['result']).__name__}"
    )
    assert payload["result"] >= 0


@pytest.mark.skipif(
    not os.environ.get("INTERNAL_TRANSPORT_SECRET"),
    reason="HTTP-mode end-to-end smoke requires INTERNAL_TRANSPORT_SECRET to be set in the backend env",
)
def test_http_mode_synisense_get_signal_round_trip(transport_secret: str) -> None:
    """One SyniSense contract call exercised via HTTP — proves Solva
    → SyniSense round-trip works end-to-end. With an unknown signal
    id the response is `{"result": null}`."""
    url = f"{SUPERVISOR_HOST}/api/internal/v1/synisense/method/get_signal"
    status, body = _http_post_json(
        url,
        {
            "account_id": "smoke-account-id-" + secrets.token_hex(4),
            "signal_id": "nonexistent-signal-" + secrets.token_hex(4),
            "untenanted": True,
        },
        headers={"X-Internal-Auth": transport_secret},
    )
    assert status == 200, f"unexpected status {status}: {body[:200]}"
    payload = json.loads(body)
    assert "result" in payload
    # Unknown signal -> Optional[Signal] -> None.
    assert payload["result"] is None


@pytest.mark.skipif(
    not os.environ.get("INTERNAL_TRANSPORT_SECRET"),
    reason="HTTP-mode end-to-end smoke requires INTERNAL_TRANSPORT_SECRET to be set in the backend env",
)
def test_http_mode_adapter_class_reconstructs_dto(transport_secret: str) -> None:
    """The HTTP adapter class generated from the in-process Protocol
    correctly reconstructs the typed DTO from the JSON response.
    Exercises the `_http_client._reconstruct` codepath."""
    # We pre-set the env var so `get_akki()` returns the HTTP variant.
    os.environ["BOUNDED_CONTEXT_TRANSPORT"] = "http"
    try:
        # Load `dotenv` so `MONGO_URL` is present for the in-process
        # adapter introspection (the HTTP adapter is built off the
        # in-process adapter's signatures).
        try:
            from dotenv import load_dotenv  # noqa: WPS433
            load_dotenv(Path("/app/backend/.env"))
        except Exception:
            pass
        from contracts import get_akki, Document

        async def _run() -> Document | None:
            akki = get_akki()
            return await akki.get_document(
                account_id="smoke-account-id-" + secrets.token_hex(4),
                document_id="nonexistent-document-" + secrets.token_hex(4),
                untenanted=True,
            )

        result = asyncio.run(_run())
        # Unknown document -> Optional[Document] -> None.
        assert result is None, (
            f"expected None for unknown document; got {result!r}"
        )
    finally:
        # Restore default to avoid contaminating other tests.
        os.environ.pop("BOUNDED_CONTEXT_TRANSPORT", None)


def test_phase4_2_transport_config_constants() -> None:
    """Sanity-check the retry/timeout policy hard-defaults match the
    Phase 4.2 dispatch contract (3 retries, 5s timeout, jittered
    back-off)."""
    try:
        from dotenv import load_dotenv  # noqa: WPS433
        load_dotenv(Path("/app/backend/.env"))
    except Exception:
        pass
    from contracts._adapters._http_client import (
        DEFAULT_BACKOFF_BASE_S,
        DEFAULT_RETRIES,
        DEFAULT_TIMEOUT_S,
    )
    assert DEFAULT_RETRIES == 3, f"expected 3 retries, got {DEFAULT_RETRIES}"
    assert DEFAULT_TIMEOUT_S == 5.0, f"expected 5.0s timeout, got {DEFAULT_TIMEOUT_S}"
    assert 0.05 <= DEFAULT_BACKOFF_BASE_S <= 0.5, (
        f"jittered back-off base should be a small positive number; got {DEFAULT_BACKOFF_BASE_S}"
    )
