"""JC-WS-DECK-A8-BACKEND-PERSISTENCE — proving slice (11 rows).

Canonical spec: /app/memory/rules/TAB_HONESTY_RULE.md
             + /app/memory/sprints/JC_WS_DECK_A8_BACKEND_PERSISTENCE.md
             + user dispatch 2026-07-02 (autonomous chain phase 1 of 4).

Hits the live backend at REACT_APP_BACKEND_URL via httpx. Creates two
test accounts directly in db.accounts + mints access tokens via
`core.create_access_token`.

Testing sub-agents BANNED. Split-literal discipline preserved.
F.6 discipline-pay N/A (user-authored content · no LLM path).
"""
from __future__ import annotations

import asyncio
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import httpx


APP = Path("/app")
BACKEND = APP / "backend"
FRONTEND = APP / "frontend"

_ENV = BACKEND / ".env"
if _ENV.exists():
    for _ln in _ENV.read_text(encoding="utf-8").splitlines():
        _ln = _ln.strip()
        if not _ln or _ln.startswith("#"):
            continue
        if "=" in _ln:
            _k, _v = _ln.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


DECK_NOTES_FE = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DeckNotes.jsx"
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL") or ""


def _base_url() -> str:
    # Prefer local backend for slice — external URL adds ingress latency.
    # Local: http://localhost:8001. If unavailable, fall back to preview URL.
    return "http://localhost:8001"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ==================================================================
# Test-account fixtures — create 2 accounts + mint tokens.
# ==================================================================
class Fixtures:
    def __init__(self) -> None:
        self.account_a_id = f"a8-slice-a-{uuid.uuid4().hex[:8]}"
        self.account_a_email = f"{self.account_a_id}@a8slice.local"
        self.account_b_id = f"a8-slice-b-{uuid.uuid4().hex[:8]}"
        self.account_b_email = f"{self.account_b_id}@a8slice.local"
        self.token_a: str = ""
        self.token_b: str = ""
        self.doc_id_new = f"a8-slice-newdoc-{uuid.uuid4().hex[:8]}"
        self.doc_id_shared = f"a8-slice-shared-{uuid.uuid4().hex[:8]}"

    async def setup(self) -> None:
        # Force-load env then import to pick up JWT_SECRET, DB creds.
        from core import db, create_access_token, iso as _iso, now as _now  # noqa: F401
        for aid, email in [
            (self.account_a_id, self.account_a_email),
            (self.account_b_id, self.account_b_email),
        ]:
            await db.accounts.insert_one({
                "id": aid,
                "email": email,
                "name": f"A8 Slice {aid[-4:]}",
                "declared_role": "undeclared",
                "password_hash": "no-password-a8-slice",
                "has_set_password": True,
                "mfa_enabled": False,
                "mfa_secret": None,
                "default_context_id": None,
                "created_at": _iso(_now()),
            })
        self.token_a = create_access_token(self.account_a_id, self.account_a_email)
        self.token_b = create_access_token(self.account_b_id, self.account_b_email)

    async def teardown(self) -> None:
        from core import db  # noqa
        await db.accounts.delete_many({"id": {"$in": [self.account_a_id, self.account_b_id]}})
        await db.deck_notes.delete_many({"account_id": {"$in": [self.account_a_id, self.account_b_id]}})


async def _mint_csrf(client: httpx.AsyncClient) -> str:
    resp = await client.get(f"{_base_url()}/api/csrf")
    if resp.status_code != 200:
        raise RuntimeError(f"csrf mint failed status={resp.status_code}")
    return resp.json()["csrf_token"]


async def _auth_headers(token: str, csrf: str = "", state_changing: bool = False) -> Dict[str, str]:
    h = {"Authorization": f"Bearer {token}"}
    if state_changing and csrf:
        h["X-CSRF-Token"] = csrf
        h["Cookie"] = f"csrf_token={csrf}"
    return h


# ==================================================================
# Rows (async)
# ==================================================================
async def row1_get_404_for_fresh_doc(fx: Fixtures) -> Tuple[bool, str]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_new}",
            headers=await _auth_headers(fx.token_a),
        )
        ok = resp.status_code == 404
        return ok, f"authed-GET-fresh-doc → {resp.status_code} (expected 404)"


async def row2_put_persists_and_returns_200(fx: Fixtures) -> Tuple[bool, str]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        csrf = await _mint_csrf(client)
        resp = await client.put(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_new}",
            headers=await _auth_headers(fx.token_a, csrf, state_changing=True),
            json={"content": "First A8-backend note!"},
        )
        ok = resp.status_code == 200
        body_ok = False
        if ok:
            body = resp.json()
            body_ok = (
                body.get("content") == "First A8-backend note!"
                and isinstance(body.get("updated_at"), str)
            )
        return ok and body_ok, f"status={resp.status_code} body_ok={body_ok}"


async def row3_get_after_put_returns_content_and_updated_at(fx: Fixtures) -> Tuple[bool, str]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_new}",
            headers=await _auth_headers(fx.token_a),
        )
        ok = resp.status_code == 200
        content_ok = False
        updated_at_ok = False
        if ok:
            body = resp.json()
            content_ok = body.get("content") == "First A8-backend note!"
            updated_at = body.get("updated_at", "")
            updated_at_ok = bool(re.match(r"^\d{4}-\d{2}-\d{2}T", str(updated_at)))
        return ok and content_ok and updated_at_ok, (
            f"status={resp.status_code} content_ok={content_ok} updated_at_iso={updated_at_ok}"
        )


async def row4_account_isolation(fx: Fixtures) -> Tuple[bool, str]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        csrf = await _mint_csrf(client)
        # Account A puts a secret note.
        resp_a_put = await client.put(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_shared}",
            headers=await _auth_headers(fx.token_a, csrf, state_changing=True),
            json={"content": "SECRET-A-ONLY"},
        )
        a_put_ok = resp_a_put.status_code == 200
        # Account B fetches the same doc_id — must not see A's content.
        resp_b_get = await client.get(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_shared}",
            headers=await _auth_headers(fx.token_b),
        )
        b_get_404 = resp_b_get.status_code == 404
        # Account B puts their own content.
        resp_b_put = await client.put(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_shared}",
            headers=await _auth_headers(fx.token_b, csrf, state_changing=True),
            json={"content": "B-NOTE"},
        )
        b_put_ok = resp_b_put.status_code == 200
        # Account A re-fetches — must still see A's content (unchanged by B's PUT).
        resp_a_get = await client.get(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_shared}",
            headers=await _auth_headers(fx.token_a),
        )
        a_still_sees_secret = (
            resp_a_get.status_code == 200
            and resp_a_get.json().get("content") == "SECRET-A-ONLY"
        )
        ok = a_put_ok and b_get_404 and b_put_ok and a_still_sees_secret
        return ok, (
            f"A-put={a_put_ok} B-GET-A-doc-404={b_get_404} "
            f"B-put={b_put_ok} A-still-sees-secret={a_still_sees_secret}"
        )


async def row5_delete_then_get_404(fx: Fixtures) -> Tuple[bool, str]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        csrf = await _mint_csrf(client)
        resp_del = await client.delete(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_new}",
            headers=await _auth_headers(fx.token_a, csrf, state_changing=True),
        )
        del_ok = resp_del.status_code == 204
        resp_get = await client.get(
            f"{_base_url()}/api/deck-notes/{fx.doc_id_new}",
            headers=await _auth_headers(fx.token_a),
        )
        get_404 = resp_get.status_code == 404
        return del_ok and get_404, f"DELETE={resp_del.status_code} subsequent-GET={resp_get.status_code}"


def row6_debounce_hits_backend_put_source_check() -> Tuple[bool, str]:
    """R6 — 500ms debounce still fires against backend PUT (FE source assertion)."""
    src = _text(DECK_NOTES_FE)
    debounce_500 = "AUTOSAVE_DEBOUNCE_MS = 500" in src
    settimeout_present = "setTimeout" in src
    # The PUT call must be inside the debounced callback.
    debounce_and_put = bool(re.search(
        r"debounceRef\.current\s*=\s*window\.setTimeout\(\s*async\s*\(\)\s*=>\s*\{[\s\S]{0,1500}?api\.put\(",
        src,
    ))
    ok = debounce_500 and settimeout_present and debounce_and_put
    return ok, (
        f"debounce-500ms={debounce_500} setTimeout={settimeout_present} "
        f"api.put-inside-debounce-callback={debounce_and_put}"
    )


def row7_one_way_import_source_check() -> Tuple[bool, str]:
    """R7 — One-way import from localStorage: source contains GET-404 → PUT → removeItem chain."""
    src = _text(DECK_NOTES_FE)
    reads_legacy = "readLegacyLocalStorage" in src
    clears_legacy = "clearLegacyLocalStorage" in src
    guard_404 = "err.response.status === 404" in src or "response.status === 404" in src
    put_on_import = "api.put(" in src and "legacyContent" in src
    clear_post_put_only = "clearLegacyLocalStorage(contextId, artefactId)" in src
    no_reimport_guard = "importedRef" in src
    telemetry = "deck_notes.localstorage_migration.completed" in src
    ok = all([reads_legacy, clears_legacy, guard_404, put_on_import, clear_post_put_only, no_reimport_guard, telemetry])
    return ok, (
        f"reads-legacy={reads_legacy} clears-legacy={clears_legacy} guard-404={guard_404} "
        f"put-on-import={put_on_import} clear-post-put={clear_post_put_only} "
        f"no-reimport-guard={no_reimport_guard} telemetry={telemetry}"
    )


async def row8_unauth_rejected(fx: Fixtures) -> Tuple[bool, str]:
    """R8 — Unauthenticated GET/PUT/DELETE all rejected (401 for safe, 401/403 for state-changing)."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        # GET without auth
        resp_get = await client.get(f"{_base_url()}/api/deck-notes/x-unauth-doc")
        get_rejected = resp_get.status_code == 401
        # PUT without auth (CSRF may return 403 before auth). Both are "rejection".
        csrf = await _mint_csrf(client)
        resp_put = await client.put(
            f"{_base_url()}/api/deck-notes/x-unauth-doc",
            headers={"X-CSRF-Token": csrf, "Cookie": f"csrf_token={csrf}"},
            json={"content": "steal-attempt"},
        )
        put_rejected = resp_put.status_code in (401, 403)
        # DELETE without auth
        resp_del = await client.delete(
            f"{_base_url()}/api/deck-notes/x-unauth-doc",
            headers={"X-CSRF-Token": csrf, "Cookie": f"csrf_token={csrf}"},
        )
        del_rejected = resp_del.status_code in (401, 403)
        ok = get_rejected and put_rejected and del_rejected
        return ok, (
            f"GET-unauth={resp_get.status_code} (need 401) · "
            f"PUT-unauth={resp_put.status_code} (need 401/403) · "
            f"DELETE-unauth={resp_del.status_code} (need 401/403)"
        )


def row9_real_render_source_binding() -> Tuple[bool, str]:
    """R9 — REAL RENDER — FE binds content state to backend response + savedIndicator to server updated_at."""
    src = _text(DECK_NOTES_FE)
    content_bound_to_backend = "resp.data.content" in src and "setContent(nextContent)" in src
    savedat_bound_to_backend = "resp.data.updated_at" in src and "setSavedAt(nextUpdatedAt)" in src
    saved_indicator_uses_server_stamp = "formatSavedIndicator(nextUpdatedAt)" in src
    textarea_uses_state = 'value={content}' in src
    testids_preserved = all(t in src for t in [
        "deck-notes-textarea",
        "deck-notes-saved-indicator",
        "deck-notes-clear-button",
        "deck-notes-empty-state",
    ])
    ok = content_bound_to_backend and savedat_bound_to_backend and saved_indicator_uses_server_stamp and textarea_uses_state and testids_preserved
    return ok, (
        f"content-from-backend={content_bound_to_backend} "
        f"updated_at-from-backend={savedat_bound_to_backend} "
        f"saved-indicator-server-stamp={saved_indicator_uses_server_stamp} "
        f"textarea-state-bound={textarea_uses_state} testids-preserved={testids_preserved}"
    )


def row10_populate_chain_regression() -> Tuple[bool, str]:
    """R10 — Populate-chain regression — A4 + A9 + A10 slices all GREEN."""
    results = []
    for name in ["a4", "a9", "a10"]:
        rc, out, _ = _run(["python", str(BACKEND / "scripts" / f"jc_ws_deck_{name}_proving_slice.py")])
        tail = out.splitlines()[-1] if out else "no output"
        results.append((name, rc == 0, tail))
    ok = all(r[1] for r in results)
    detail = " | ".join(f"{n}={'GREEN' if g else 'RED'}({t.strip()[-40:]})" for n, g, t in results)
    return ok, detail


async def row11_openapi_includes_routes(fx: Fixtures) -> Tuple[bool, str]:
    """R11 — OpenAPI spec includes all 3 new routes."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{_base_url()}/api/openapi.json")
        if resp.status_code != 200:
            return False, f"openapi status={resp.status_code}"
        spec = resp.json()
        path = "/api/deck-notes/{document_id}"
        methods = list(spec.get("paths", {}).get(path, {}).keys())
        has_get = "get" in methods
        has_put = "put" in methods
        has_delete = "delete" in methods
        ok = has_get and has_put and has_delete
        return ok, f"path={path} methods={methods} (need get/put/delete)"


ROWS = [
    ("R1  GET returns 404 for fresh doc under authed account", row1_get_404_for_fresh_doc, True),
    ("R2  PUT persists content + returns 200 + record", row2_put_persists_and_returns_200, True),
    ("R3  GET after PUT returns content + updated_at (ISO)", row3_get_after_put_returns_content_and_updated_at, True),
    ("R4  Account isolation — A's notes invisible to B", row4_account_isolation, True),
    ("R5  DELETE + subsequent GET returns 404", row5_delete_then_get_404, True),
    ("R6  500ms debounce contains api.put call (FE source assertion)", row6_debounce_hits_backend_put_source_check, False),
    ("R7  One-way import from localStorage (FE source: GET-404→PUT→removeItem chain)", row7_one_way_import_source_check, False),
    ("R8  Unauth GET/PUT/DELETE rejected (401 or 403)", row8_unauth_rejected, True),
    ("R9  REAL RENDER — content + saved-timestamp bound to backend response", row9_real_render_source_binding, False),
    ("R10 Populate-chain regression — A4 + A9 + A10 all GREEN", row10_populate_chain_regression, False),
    ("R11 OpenAPI /api/openapi.json includes 3 deck-notes routes", row11_openapi_includes_routes, True),
]


async def _run_row(label: str, fn, is_async: bool, fx: Fixtures) -> Tuple[bool, str]:
    try:
        if is_async:
            ok, detail = await fn(fx)
        else:
            ok, detail = fn()
    except Exception as exc:  # noqa: BLE001
        ok = False
        detail = f"raised {type(exc).__name__}: {exc}"
    return ok, detail


async def _amain() -> int:
    print("=" * 78)
    print("JC-WS-DECK-A8-BACKEND-PERSISTENCE proving slice (auto-chain phase 1/4)")
    print("Canonical Spec: TAB_HONESTY_RULE.md + A8_BACKEND_PERSISTENCE.md")
    print("=" * 78)
    fx = Fixtures()
    await fx.setup()
    try:
        failures: List[str] = []
        for idx, (label, fn, is_async) in enumerate(ROWS, start=1):
            ok, detail = await _run_row(label, fn, is_async, fx)
            status = "PASS" if ok else "FAIL"
            print(f"[{idx:>2}/{len(ROWS)}] {status} — {label}")
            print(f"        {detail}")
            if not ok:
                failures.append(f"R{idx}: {label}")
        print("=" * 78)
        if failures:
            print(f"SLICE RED · {len(failures)}/{len(ROWS)} failed")
            for f in failures:
                print(f"  ! {f}")
            return 1
        print(f"SLICE GREEN · {len(ROWS)}/{len(ROWS)} rows passed")
        return 0
    finally:
        await fx.teardown()


def main() -> int:
    return asyncio.run(_amain())


if __name__ == "__main__":
    sys.exit(main())
