"""Phase F.4 — Compile Flow wire + live tests (2026-05-26).

**Phase 5.5.1 (2026-06-24) rewrite:** the original Phase-F.4 lockdown
asserted on router-decorator source strings (e.g.
`'@router.get("/tasks/{task_id}/compile")' in src`) which broke
when Phase 5.4 narrowing batch 1 added `response_model=...`
arguments to those decorators.

The wire contract is unchanged — the endpoints still exist and
serve the same payloads. Two tests in this file were
contract-pinned instead of source-string-pinned at file-level
unquarantine:
  - `test_f4_tasks_router_has_all_compile_endpoints` — now reads
    the OpenAPI path-list (the public surface ratchet) and
    asserts each spec'd compile path is present.
  - `test_f4_circulation_endpoint_is_public_no_auth` — now drives
    HTTP against the actual endpoints with no auth header and
    asserts they DON'T return 401/403 (they return 404 on an
    invalid token, which proves the endpoint resolved without
    auth-walling first).

All 22 other tests in the file pass unchanged against the
current architecture.

See `/app/memory/sprints/PHASE_5_5_1_TRACK_A_CLOSURE.md` §2 for
the rewrite rationale + contract-vs-implementation justification.
"""
from __future__ import annotations

import pytest

import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport


REPO = Path(__file__).resolve().parent.parent.parent
FE   = REPO / "frontend" / "src"
BE   = REPO / "backend"

TASK_DRAWER     = FE / "components" / "tasks" / "TaskDrawer.jsx"
TASKS_ROUTER    = BE / "routers" / "tasks.py"
COMPILE_SVC     = BE / "services" / "tasks" / "compile_service.py"
INTEL_SVC       = BE / "services" / "tasks" / "intelligence_service.py"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ═════════════════════════════════════════════════════════════════════
# Wire — UI
# ═════════════════════════════════════════════════════════════════════
def test_f4_compile_tab_progress_strip_renders_5_stages():
    src = _read(TASK_DRAWER)
    # Each stage is keyed in the COMPILE_STAGES array.
    for key in ("drafting", "review", "circulation", "final_production", "commit"):
        assert f'key: "{key}"' in src
    # Progress strip + stage pip testids via template literal.
    assert 'data-testid="task-drawer-compile-progress"' in src
    assert "task-drawer-compile-stage-${s.key}" in src
    assert "task-drawer-compile-stage-pip-${s.key}" in src


def test_f4_compile_start_button_is_always_enabled():
    """Per user directive — readiness is informational. The Start
    button doesn't carry a `disabled={readiness < X}` guard."""
    src = _read(TASK_DRAWER)
    assert 'data-testid="task-drawer-compile-start"' in src
    # The disabled prop is bound only to the in-flight `busy` state.
    block = src.split('data-testid="task-drawer-compile-start"')[0]
    # Walk back to find the Button props.
    button_start = block.rfind("<Button")
    assert button_start != -1
    button_props = block[button_start:]
    assert "disabled={busy}" in button_props
    # Readiness chip carries the "informational only" title.
    assert "informational only" in src


def test_f4_low_readiness_warning_modal_is_non_blocking():
    src = _read(TASK_DRAWER)
    assert 'data-testid="task-drawer-compile-low-readiness-modal"' in src
    assert 'data-testid="task-drawer-compile-low-readiness-cancel"' in src
    assert 'data-testid="task-drawer-compile-low-readiness-continue"' in src
    # Threshold is 80% per brief.
    assert "(task.readiness_score ?? 0) < 80" in src


def test_f4_per_stage_panels_present():
    src = _read(TASK_DRAWER)
    for stage in ("drafting", "review", "circulation", "final", "commit"):
        assert f'data-testid="task-drawer-compile-panel-{stage}"' in src


def test_f4_review_panel_has_skip_circulation_option():
    src = _read(TASK_DRAWER)
    assert 'data-testid="task-drawer-compile-next-circulation"' in src
    assert 'data-testid="task-drawer-compile-skip-circulation"' in src


def test_f4_circulation_panel_has_reviewer_input_and_close():
    src = _read(TASK_DRAWER)
    assert 'data-testid="task-drawer-compile-circulation-emails"' in src
    assert 'data-testid="task-drawer-compile-circulation-send"' in src
    assert 'data-testid="task-drawer-compile-circulation-close"' in src
    # base_url is sent with the request so magic links carry the right host.
    assert "base_url: window.location.origin" in src


def test_f4_final_panel_has_apply_and_discard():
    src = _read(TASK_DRAWER)
    assert "task-drawer-compile-final-apply-${c.id}" in src
    assert "task-drawer-compile-final-discard-${c.id}" in src
    assert 'data-testid="task-drawer-compile-final-complete"' in src


def test_f4_commit_panel_has_commit_final_cta():
    src = _read(TASK_DRAWER)
    assert 'data-testid="task-drawer-compile-commit-final"' in src


# ═════════════════════════════════════════════════════════════════════
# Wire — Backend (Phase 5.5.1 — contract-pinned via OpenAPI path-list)
# ═════════════════════════════════════════════════════════════════════
def test_f4_tasks_router_has_all_compile_endpoints():
    """Phase 5.5.1 — pins the **public surface** of the compile flow
    via the OpenAPI path-list (the same ratchet hashed by
    `/api/* = cdcb23322bb82895`). The original source-string pin
    broke when Phase 5.4 narrowing added `response_model=` args to
    the decorators; the wire contract is the right pin.
    """
    from server import app
    spec = app.openapi()
    paths = set(spec["paths"].keys())
    # Per-method check: every spec'd compile endpoint resolves
    # under the canonical `/api/*` prefix with the right HTTP verb.
    expected = [
        ("get",  "/api/tasks/{task_id}/compile"),
        ("post", "/api/tasks/{task_id}/compile/draft"),
        ("post", "/api/tasks/{task_id}/compile/review/complete"),
        ("post", "/api/tasks/{task_id}/compile/circulation/send"),
        ("get",  "/api/tasks/circulation/{token}"),
        ("post", "/api/tasks/circulation/{token}/comment"),
        ("post", "/api/tasks/{task_id}/compile/circulation/close"),
        ("post", "/api/tasks/{task_id}/compile/final-production/apply-comment"),
        ("post", "/api/tasks/{task_id}/compile/final-production/complete"),
        ("post", "/api/tasks/{task_id}/compile/commit"),
    ]
    for verb, path in expected:
        assert path in paths, (
            f"OpenAPI surface missing compile endpoint: {verb.upper()} {path}"
        )
        methods = {m.lower() for m in spec["paths"][path].keys()}
        assert verb in methods, (
            f"OpenAPI {path} present but missing {verb.upper()} method "
            f"(found: {sorted(methods)})"
        )


def test_f4_compile_service_has_3sec_llm_timeout():
    src = _read(COMPILE_SVC)
    assert "SHIELD_LLM_TIMEOUT_SECONDS = 3.0" in src
    assert "asyncio.wait_for" in src
    # Timeout audit is recorded with the purpose.
    assert "task.compile.llm.timeout" in src


def test_f4_intelligence_service_has_3sec_llm_timeout():
    """F.4 dispatch tweak — the intelligence-service LLM call now has
    a 3-second timeout per orchestrator's one-line ask."""
    src = _read(INTEL_SVC)
    assert "asyncio.wait_for" in src or "_asyncio.wait_for" in src
    assert "timeout=3.0" in src


def test_f4_commit_path_has_rollback_on_partial_failure():
    src = _read(COMPILE_SVC)
    assert "rolled_back" in src or "rollback" in src.lower()
    assert "task.compile.commit.failed" in src
    assert "task.compile.commit.completed" in src


@pytest.mark.asyncio
async def test_f4_circulation_endpoint_is_public_no_auth():
    """Phase 5.5.1 — drive the actual HTTP endpoint with NO auth
    header. A public endpoint resolves and returns 404 on an
    unknown token (or 422 on malformed input); an auth-walled
    endpoint returns 401/403 BEFORE looking up the token. The
    status-code distinction proves the wire contract without
    coupling to the handler's `Depends(get_current_account)`
    source signature.
    """
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        # GET — public landing on unknown token must NOT 401/403.
        r = await c.get("/api/tasks/circulation/no-such-token")
        assert r.status_code != 401 and r.status_code != 403, (
            f"GET /api/tasks/circulation/{{token}} returned {r.status_code} "
            f"without auth — expected the endpoint to resolve as public "
            f"and return 404 on the missing token. Body: {r.text[:200]}"
        )
        # POST comment — public submission on unknown token must NOT 401/403.
        r = await c.post(
            "/api/tasks/circulation/no-such-token/comment",
            json={"comment": "hi"},
        )
        assert r.status_code != 401 and r.status_code != 403, (
            f"POST /api/tasks/circulation/{{token}}/comment returned "
            f"{r.status_code} without auth — expected public. "
            f"Body: {r.text[:200]}"
        )


# ═════════════════════════════════════════════════════════════════════
# Live HTTP
# ═════════════════════════════════════════════════════════════════════
@pytest.fixture
async def compile_actor():
    from core import db, hash_password
    uid = f"test-f4-{uuid.uuid4().hex[:8]}"
    cid = f"ctx-f4-{uuid.uuid4().hex[:8]}"
    email = f"f4-{uuid.uuid4().hex[:6]}@example.com"
    await db.accounts.insert_one({
        "id": uid, "email": email,
        "password_hash": hash_password("Pw!1234567Abc"),
        "name": "F4", "tier": "executive",
        "declared_role": "executive", "mfa_enrolled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    await db.contexts.insert_one({
        "id": cid, "name": "F4 Co", "owner_account_id": uid,
        "type": "executive_personal",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    await db.memberships.insert_one({
        "id": f"mem-{uuid.uuid4().hex[:8]}",
        "account_id": uid, "context_id": cid,
        "role": "executive", "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    yield {"uid": uid, "cid": cid, "email": email, "password": "Pw!1234567Abc"}
    await db.tasks.delete_many({"account_id": uid})
    await db.task_intelligence.delete_many({})
    await db.task_circulation_tokens.delete_many({})
    await db.documents.delete_many({"context_id": cid})
    await db.audit_log.delete_many({"account_id": uid})
    await db.memberships.delete_many({"account_id": uid})
    await db.contexts.delete_one({"id": cid})
    await db.accounts.delete_one({"id": uid})


async def _login(c, actor):
    r = await c.post("/api/auth/login",
                     json={"email": actor["email"], "password": actor["password"]})
    token = r.json().get("access_token") or r.json().get("token")
    return {"Authorization": f"Bearer {token}", "X-Active-Context": actor["cid"]}


async def _seed_task(db, actor, **overrides):
    tid = f"task-{uuid.uuid4().hex[:12]}"
    base = {
        "id": tid, "account_id": actor["uid"], "context_id": actor["cid"],
        "name": "F4 task", "objective": "Ship a polished thing.",
        "success_criteria": "Sign-off captured.",
        "output_spec": {"kind": "template", "template_id": "briefing", "formats": ["pdf"]},
        "team": [
            {"name": "A", "email": "a@x.com", "status": "approved",
             "contribution": "section a", "contribution_mode": "akki_account"},
        ],
        "state": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    await db.tasks.insert_one(base)
    return tid


@pytest.mark.asyncio
async def test_f4_get_compile_returns_empty_session_when_none_started(compile_actor):
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        r = await c.get(f"/api/tasks/{tid}/compile", headers=hdr)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["active"] is False
        assert body["current_stage"] is None
        assert body["draft_artefact_ids"] == []


@pytest.mark.asyncio
async def test_f4_stage1_drafting_creates_draft_documents(compile_actor):
    """POST /compile/draft generates draft docs linked to the task."""
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        r = await c.post(f"/api/tasks/{tid}/compile/draft", headers=hdr)
        assert r.status_code == 200, r.text
        body = r.json()
        # Single-section template ("briefing") returns synchronously.
        assert body["status"] == "completed"
        ids = body["draft_artefact_ids"]
        assert len(ids) >= 1
        # All linked back to the task.
        n = await db.documents.count_documents({"task_id": tid, "state": "draft"})
        assert n == len(ids)
        # Audit row fired.
        a = await db.audit_log.find_one({"resource_id": tid, "action": "task.compile.drafting.completed"})
        assert a is not None


@pytest.mark.asyncio
async def test_f4_stage2_review_complete_advances_to_circulation(compile_actor):
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        await c.post(f"/api/tasks/{tid}/compile/draft", headers=hdr)
        r = await c.post(f"/api/tasks/{tid}/compile/review/complete",
                         json={"skip_circulation": False}, headers=hdr)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["current_stage"] == "circulation"
        assert body["circulation"]["enabled"] is True


@pytest.mark.asyncio
async def test_f4_stage2_review_complete_can_skip_circulation(compile_actor):
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        await c.post(f"/api/tasks/{tid}/compile/draft", headers=hdr)
        r = await c.post(f"/api/tasks/{tid}/compile/review/complete",
                         json={"skip_circulation": True}, headers=hdr)
        assert r.status_code == 200
        assert r.json()["current_stage"] == "final_production"


@pytest.mark.asyncio
async def test_f4_stage3_circulation_send_creates_tokens_and_public_view_works(compile_actor):
    """The circulation-send endpoint generates per-reviewer tokens.
    The public view endpoint accepts the token WITHOUT auth and
    returns the docs the reviewer can see. The public comment
    endpoint persists the comment to the session."""
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        await c.post(f"/api/tasks/{tid}/compile/draft", headers=hdr)
        await c.post(f"/api/tasks/{tid}/compile/review/complete",
                     json={"skip_circulation": False}, headers=hdr)
        r = await c.post(f"/api/tasks/{tid}/compile/circulation/send",
                         json={"reviewer_emails": ["alice@reviewer.com"],
                               "base_url": "http://test"}, headers=hdr)
        assert r.status_code == 200, r.text
        sent = r.json()["sent"]
        assert len(sent) == 1
        token = sent[0]["token"]
        # Public view — no auth header.
        r = await c.get(f"/api/tasks/circulation/{token}")
        assert r.status_code == 200, r.text
        view = r.json()
        assert view["reviewer_email"] == "alice@reviewer.com"
        assert isinstance(view["docs"], list)
        # Public comment — no auth header.
        r = await c.post(f"/api/tasks/circulation/{token}/comment",
                         json={"comment": "Tighten the executive summary."})
        assert r.status_code == 200, r.text
        # Comment landed on the session.
        t = await db.tasks.find_one({"id": tid})
        comments = t["compile_session"]["circulation"]["comments"]
        assert len(comments) == 1
        assert comments[0]["reviewer"] == "alice@reviewer.com"
        assert "Tighten" in comments[0]["comment"]


@pytest.mark.asyncio
async def test_f4_invalid_circulation_token_returns_404(compile_actor):
    from server import app  # noqa: F401
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/tasks/circulation/no-such-token")
        assert r.status_code == 404


@pytest.mark.asyncio
async def test_f4_stage3_close_circulation_advances_to_final(compile_actor):
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        await c.post(f"/api/tasks/{tid}/compile/draft", headers=hdr)
        await c.post(f"/api/tasks/{tid}/compile/review/complete",
                     json={"skip_circulation": False}, headers=hdr)
        await c.post(f"/api/tasks/{tid}/compile/circulation/send",
                     json={"reviewer_emails": ["alice@reviewer.com"],
                           "base_url": "http://test"}, headers=hdr)
        r = await c.post(f"/api/tasks/{tid}/compile/circulation/close", headers=hdr)
        assert r.status_code == 200
        body = r.json()
        assert body["current_stage"] == "final_production"
        assert body["circulation"]["closed_at"]


@pytest.mark.asyncio
async def test_f4_stage4_apply_comment_records_action(compile_actor):
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        await c.post(f"/api/tasks/{tid}/compile/draft", headers=hdr)
        await c.post(f"/api/tasks/{tid}/compile/review/complete",
                     json={"skip_circulation": False}, headers=hdr)
        r = await c.post(f"/api/tasks/{tid}/compile/circulation/send",
                         json={"reviewer_emails": ["alice@reviewer.com"],
                               "base_url": "http://test"}, headers=hdr)
        token = r.json()["sent"][0]["token"]
        await c.post(f"/api/tasks/circulation/{token}/comment",
                     json={"comment": "Tighten the exec summary."})
        # Close, then apply.
        await c.post(f"/api/tasks/{tid}/compile/circulation/close", headers=hdr)
        t = await db.tasks.find_one({"id": tid})
        cid = t["compile_session"]["circulation"]["comments"][0]["id"]
        r = await c.post(f"/api/tasks/{tid}/compile/final-production/apply-comment",
                         json={"comment_id": cid, "action": "discard"}, headers=hdr)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        assert body["action"] == "discard"
        # Comment status persisted.
        t = await db.tasks.find_one({"id": tid})
        c2 = next(c for c in t["compile_session"]["circulation"]["comments"] if c["id"] == cid)
        assert c2["status"] == "discard"


@pytest.mark.asyncio
async def test_f4_stage5_commit_lifts_watermark_and_can_auto_close(compile_actor):
    """Stage 5 — commit sets state from draft → committed for every
    draft in the session. If no other open drafts remain on the task,
    the task auto-transitions to closed."""
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        await c.post(f"/api/tasks/{tid}/compile/draft", headers=hdr)
        await c.post(f"/api/tasks/{tid}/compile/review/complete",
                     json={"skip_circulation": True}, headers=hdr)
        await c.post(f"/api/tasks/{tid}/compile/final-production/complete", headers=hdr)
        r = await c.post(f"/api/tasks/{tid}/compile/commit", headers=hdr)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["ok"] is True
        assert len(body["committed"]) >= 1
        # All draft docs now committed.
        n_draft = await db.documents.count_documents({"task_id": tid, "state": "draft"})
        n_committed = await db.documents.count_documents({"task_id": tid, "state": "committed"})
        assert n_draft == 0
        assert n_committed == len(body["committed"])
        # Task auto-closed because no other drafts remain.
        t = await db.tasks.find_one({"id": tid})
        assert t["state"] == "closed"
        assert t["compile_session"]["active"] is False
        # Audit rows.
        completed = await db.audit_log.find_one({"resource_id": tid, "action": "task.compile.commit.completed"})
        assert completed is not None
        auto_closed = await db.audit_log.find_one({"resource_id": tid, "action": "task.state.auto_closed"})
        assert auto_closed is not None


@pytest.mark.asyncio
async def test_f4_commit_partial_failure_rolls_back(compile_actor):
    """Manually craft a scenario where the second of two draft docs
    is in the wrong state — commit fails, the first commit rolls back."""
    from server import app  # noqa: F401
    from core import db
    tid = await _seed_task(db, compile_actor)
    # Seed 2 drafts directly in the documents collection; mark one
    # as already committed so the second `update_one` in run_commit
    # fails to match (modified_count != 1).
    d1 = f"doc-{uuid.uuid4().hex[:8]}"
    d2 = f"doc-{uuid.uuid4().hex[:8]}"
    await db.documents.insert_many([
        {"id": d1, "context_id": compile_actor["cid"], "task_id": tid,
         "state": "draft", "status": "ready", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": d2, "context_id": compile_actor["cid"], "task_id": tid,
         "state": "committed", "status": "ready", "created_at": datetime.now(timezone.utc).isoformat()},
    ])
    # Manually set compile session to point at both ids.
    await db.tasks.update_one({"id": tid}, {"$set": {"compile_session": {
        "active": True, "current_stage": "commit",
        "draft_artefact_ids": [d1, d2], "review_artefact_ids": [],
        "circulation": {"enabled": False, "reviewer_emails": [], "sent_at": None,
                        "comments": [], "closed_at": None},
        "final_artefact_ids": [d1, d2], "committed_artefact_ids": [],
        "started_at": datetime.now(timezone.utc).isoformat(), "completed_at": None,
    }}})
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        hdr = await _login(c, compile_actor)
        r = await c.post(f"/api/tasks/{tid}/compile/commit", headers=hdr)
        assert r.status_code == 400
        body = r.json()
        assert "partial_commit_failed" in str(body)
        # Roll-back: d1 should be reverted to "draft" again.
        d1_doc = await db.documents.find_one({"id": d1})
        assert d1_doc["state"] == "draft"
        # Failure audit row.
        failed = await db.audit_log.find_one({"resource_id": tid, "action": "task.compile.commit.failed"})
        assert failed is not None


# ═════════════════════════════════════════════════════════════════════
# F.4 log presence
# ═════════════════════════════════════════════════════════════════════
def test_f4_section_present_in_home_cleanup_log():
    log = (REPO / "memory" / "sprints" / "HOME_CLEANUP_LOG.md").read_text("utf-8")
    assert "F.4" in log and "Compile" in log
