"""Phase P4 — Cohort funnel live-wiring lockdown.

Covers:
  - P4.A receipt email path (flag-off log line, flag-on send shape)
  - P4.B admin approve / decline / hold (state machine + audit row + email gating)
  - P4.C magic-link issue / preview / consume (happy + expired + consumed + tampered)
  - End-to-end: admin approves a synthetic application → consume → session

Cluster-G.1 (2026-06-27): converted from module-level `_run` helper
to `@pytest.mark.asyncio + async def` so async-touching tests bind
to the session-scoped event loop instead of binding the policy loop
to a sync-test-local loop (same root cause as Cluster-E + Cluster-F).
3 pure-Python tests stay sync per Cluster-F.2 heuristic.
"""
from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "backend"))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(REPO / "backend" / ".env")

from httpx import ASGITransport, AsyncClient  # noqa: E402
from server import app  # noqa: E402


def _client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


# ─── helpers ────────────────────────────────────────────────────────
async def _admin_login_token() -> str:
    async with _client() as ac:
        r = await ac.post("/api/auth/login",
                          json={"email": "admin@akki.ai", "password": "AkkiAdmin2026!"})
        return r.json()["access_token"]


def _seed_application(prefix: str = "p4") -> dict:
    """Insert a cohort_application row directly."""
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    row = {
        "id":             uuid.uuid4().hex,
        "name":           "P4 Test Applicant",
        "email":          f"{prefix}-{uuid.uuid4().hex[:6]}@p4.example.com",
        "organisation":   "Probe Ltd",
        "role":           "Tester",
        "use_case":       "Smoke testing the P4 funnel.",
        "referral_source": "qa",
        "status":         "received",
        "created_at":     datetime.now(timezone.utc).isoformat(),
    }
    db.cohort_applications.insert_one(dict(row))
    return row


# ─── P4.A receipt email ─────────────────────────────────────────────
def test_p4_a_receipt_email_word_counts_under_60():
    """Pure-Python helper test — no asyncio surface. STAYS SYNC per
    Cluster-F.2 heuristic."""
    from services.cohort_email import _self_check
    counts = _self_check()
    for kind, n in counts.items():
        assert n <= 60, f"{kind}: {n} words exceeds 60-word cap"


def test_p4_a_receipt_flag_off_logs_redacted(caplog):
    """Pure-Python helper test — no asyncio surface. STAYS SYNC per
    Cluster-F.2 heuristic."""
    import logging
    caplog.set_level(logging.INFO, logger="services.cohort_email")
    from services.cohort_email import send_receipt
    out = send_receipt(to_email="alice@example.com", first_name="Alice")
    assert out == {"status": "flag_off", "kind": "receipt"}
    # Log line must redact the local-part.
    assert any("al***@example.com" in r.message for r in caplog.records)


def test_p4_a_receipt_body_voice_lint_clean():
    """Each body must NOT contain any banned word from
    services.two_pass.BANNED_WORDS.

    Pure-Python helper test — no asyncio surface. STAYS SYNC per
    Cluster-F.2 heuristic."""
    from services.cohort_email import RECEIPT_BODY, APPROVAL_BODY, DECLINE_BODY
    from services.two_pass import BANNED_WORDS
    sample = (RECEIPT_BODY + " " + APPROVAL_BODY + " " + DECLINE_BODY).lower()
    hits = [w for w in BANNED_WORDS if w.lower() in sample]
    assert not hits, f"Banned words in cohort email bodies: {hits}"


# ─── P4.C magic-link ────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_p4_c_admin_issues_and_preview_round_trip():
    app_row = _seed_application("p4c-issue")
    tok = await _admin_login_token()
    async with _client() as ac:
        r = await ac.post("/api/auth/magic-link/issue",
                          headers={"Authorization": f"Bearer {tok}"},
                          json={"application_id": app_row["id"]})
    assert r.status_code == 200, r.text
    raw = r.json()["token"]
    expires_at = r.json()["expires_at"]
    assert raw and expires_at

    async with _client() as ac:
        r2 = await ac.get(f"/api/auth/magic-link/preview/{raw}")
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data["first_name"] == "P4"
    assert data["organisation"] == "Probe Ltd"


@pytest.mark.asyncio
async def test_p4_c_consume_password_mode_creates_account_and_session():
    app_row = _seed_application("p4c-consume")
    tok = await _admin_login_token()
    async with _client() as ac:
        r_issue = await ac.post("/api/auth/magic-link/issue",
                                headers={"Authorization": f"Bearer {tok}"},
                                json={"application_id": app_row["id"]})
    raw = r_issue.json()["token"]

    async with _client() as ac:
        r = await ac.post("/api/auth/magic-link/consume",
                          json={"token": raw, "mode": "password",
                                "password": "NewPass1234!"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["ok"] is True
    assert data["new_account"] is True
    assert data["account"]["email"] == app_row["email"]
    assert data["access_token"]
    # Cookie attributes (HttpOnly + Secure + SameSite=strict).
    cookies = r.headers.get_list("set-cookie")
    access_cookies = [c for c in cookies if c.startswith("access_token=")]
    assert access_cookies
    for c in access_cookies:
        lower = c.lower()
        assert "httponly" in lower and "samesite=strict" in lower and "secure" in lower

    # Application moved to approved_redeemed.
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    fresh = db.cohort_applications.find_one({"id": app_row["id"]}, {"_id": 0})
    assert fresh["status"] == "approved_redeemed"


@pytest.mark.asyncio
async def test_p4_c_consumed_token_cannot_be_reused():
    app_row = _seed_application("p4c-reuse")
    tok = await _admin_login_token()
    async with _client() as ac:
        r_issue = await ac.post("/api/auth/magic-link/issue",
                                headers={"Authorization": f"Bearer {tok}"},
                                json={"application_id": app_row["id"]})
    raw = r_issue.json()["token"]

    async with _client() as ac:
        await ac.post("/api/auth/magic-link/consume",
                      json={"token": raw, "mode": "password",
                            "password": "PassToReuse1234!"})  # first consume succeeds.
    async with _client() as ac:
        r2 = await ac.post("/api/auth/magic-link/consume",
                           json={"token": raw, "mode": "password",
                                 "password": "PassToReuse1234!"})
    assert r2.status_code == 410
    assert r2.json()["detail"]["code"] in ("invalid_or_consumed", "consumed")

    # Preview after consume reflects state.
    async with _client() as ac:
        r3 = await ac.get(f"/api/auth/magic-link/preview/{raw}")
    assert r3.status_code == 410
    assert r3.json()["detail"]["code"] == "consumed"


@pytest.mark.asyncio
async def test_p4_c_expired_token_rejected():
    """Inject a row with expires_at in the past."""
    app_row = _seed_application("p4c-expired")
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    raw = "fake-but-hashed-properly"
    db.cohort_magic_links.insert_one({
        "id":             uuid.uuid4().hex,
        "application_id": app_row["id"],
        "token_hash":     bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode(),
        "issued_at":      (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
        "expires_at":     (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
        "consumed_at":    None,
        "consumed_by_user_id": None,
    })
    async with _client() as ac:
        r = await ac.get(f"/api/auth/magic-link/preview/{raw}")
    assert r.status_code == 410
    assert r.json()["detail"]["code"] == "expired"


@pytest.mark.asyncio
async def test_p4_c_tampered_token_404():
    async with _client() as ac:
        r = await ac.get("/api/auth/magic-link/preview/totally-bogus-token-not-in-db")
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "not_found"


@pytest.mark.asyncio
async def test_p4_c_reissue_invalidates_prior_token():
    app_row = _seed_application("p4c-reissue")
    tok = await _admin_login_token()
    async with _client() as ac:
        r_i1 = await ac.post("/api/auth/magic-link/issue",
                             headers={"Authorization": f"Bearer {tok}"},
                             json={"application_id": app_row["id"]})
        r_i2 = await ac.post("/api/auth/magic-link/issue",
                             headers={"Authorization": f"Bearer {tok}"},
                             json={"application_id": app_row["id"]})
    raw1 = r_i1.json()["token"]
    raw2 = r_i2.json()["token"]
    assert raw1 != raw2

    # raw1 must now be rejected.
    async with _client() as ac:
        r1 = await ac.get(f"/api/auth/magic-link/preview/{raw1}")
        r2 = await ac.get(f"/api/auth/magic-link/preview/{raw2}")
    assert r1.status_code == 410
    assert r2.status_code == 200


# ─── P4.B admin actions ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_p4_b_approve_writes_audit_and_issues_link():
    app_row = _seed_application("p4b-approve")
    tok = await _admin_login_token()
    async with _client() as ac:
        r = await ac.post(
            f"/api/admin/cohort/applications/{app_row['id']}/approve",
            headers={"Authorization": f"Bearer {tok}"},
            json={"note": "auto-test"},
        )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "approved"
    assert "/welcome/" in data["magic_url"]
    # Audit row.
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    audits = list(db.cohort_application_audit.find({"application_id": app_row["id"], "action": "approve"}, {"_id": 0}))
    assert audits
    assert audits[-1]["new_status"] == "approved"


@pytest.mark.asyncio
async def test_p4_b_decline_writes_audit_and_skips_email_when_flag_off():
    app_row = _seed_application("p4b-decline")
    tok = await _admin_login_token()
    async with _client() as ac:
        r = await ac.post(
            f"/api/admin/cohort/applications/{app_row['id']}/decline",
            headers={"Authorization": f"Bearer {tok}"},
            json={"note": None},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "declined"
    assert data["email"]["status"] == "flag_off"


@pytest.mark.asyncio
async def test_p4_b_hold_no_email():
    app_row = _seed_application("p4b-hold")
    tok = await _admin_login_token()
    async with _client() as ac:
        r = await ac.post(
            f"/api/admin/cohort/applications/{app_row['id']}/hold",
            headers={"Authorization": f"Bearer {tok}"},
            json={"note": "needs review"},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "held"
    assert "email" not in data    # hold sends no email.


@pytest.mark.asyncio
async def test_p4_b_non_admin_403():
    """A regular account must NOT be able to call the admin endpoints."""
    import pymongo
    db = pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    email = f"p4-nonadmin-{uuid.uuid4().hex[:6]}@p4.example.com"
    db.accounts.insert_one({
        "id": uuid.uuid4().hex, "email": email, "email_lc": email.lower(),
        "status": "active", "is_superadmin": False,
        "password_hash": bcrypt.hashpw(b"NonAdminPass1234!", bcrypt.gensalt()).decode(),
        "auth_provider": "password",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    async with _client() as ac:
        r1 = await ac.post("/api/auth/login",
                           json={"email": email, "password": "NonAdminPass1234!"})
        tok = r1.json()["access_token"]
        r = await ac.post(
            "/api/admin/cohort/applications/does-not-matter/approve",
            headers={"Authorization": f"Bearer {tok}"},
            json={"note": None},
        )
    assert r.status_code == 403


# ─── End-to-end ─────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_p4_e2e_admin_approves_applicant_consumes_session_valid():
    """Synthetic application → admin approve → applicant consume →
    /me returns the new account."""
    app_row = _seed_application("p4-e2e")
    tok = await _admin_login_token()

    async with _client() as ac:
        r1 = await ac.post(
            f"/api/admin/cohort/applications/{app_row['id']}/approve",
            headers={"Authorization": f"Bearer {tok}"},
            json={"note": "e2e"},
        )
        assert r1.status_code == 200, r1.text
        # Extract raw token from the magic URL.
        url = r1.json()["magic_url"]
        raw_token = url.rsplit("/", 1)[-1]

        # Preview must show first_name.
        r2 = await ac.get(f"/api/auth/magic-link/preview/{raw_token}")
        assert r2.status_code == 200, r2.text
        assert r2.json()["first_name"] == "P4"

        # Consume + use the new session.
        r3 = await ac.post(
            "/api/auth/magic-link/consume",
            json={"token": raw_token, "mode": "password", "password": "E2EPass1234!"},
        )
        assert r3.status_code == 200, r3.text
        new_token = r3.json()["access_token"]

        # Use the new session — /auth/me returns the new account.
        r4 = await ac.get("/api/auth/me", headers={"Authorization": f"Bearer {new_token}"})
        assert r4.status_code == 200, r4.text
        me = r4.json()
        # Shape: {account: {email, ...}} per sanitize_account.
        account_email = (
            (me.get("account") or {}).get("email")
            or me.get("email")
        )
        assert account_email == app_row["email"]
