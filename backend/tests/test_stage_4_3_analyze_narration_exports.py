"""Stage 4.3 — Analyze narration carriage in report exports.

Locks the seam closed: when an `ana-*` analysis row has been
synthesized via POST /workbook/v2/analyses/{aid}/synthesize, the
cached Solva v2 narration MUST surface in the PPTX / DOCX / XLSX
exports. Pre-Stage-4.3, `_adapt_new_analysis_to_workbook_analysis`
was a Phase-1 shim that dropped narration on the floor so exports
were content-free.

This suite seeds a cached-narration `analyses` row via pymongo
(sync, no loop conflict with TestClient) and walks the three
export endpoints, asserting the headline + an observation title
round-trip into the file bytes.
"""
from __future__ import annotations

import io
import os
import re
import uuid
import zipfile
from datetime import datetime, timezone

import pytest
import pymongo
from httpx import ASGITransport, AsyncClient

from server import app


_HEADLINE = "Revenue fell 18% across three of the four product lines this quarter."
_OBS_TITLE = "Storefront-A volume collapsed in week 7"
_OBS_BODY = (
    "Sales of the dominant SKU dropped from 412 units to 71 units between "
    "weeks 6 and 7, with no recovery in weeks 8-9."
)
_CELL_RANGE = "Sheet1!B14:C20"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sync_db():
    """Sync pymongo handle on the same Mongo + DB the app uses.

    Mirrors the URL/DB from backend/.env so the row we seed lands
    in the same collection the FastAPI handlers read."""
    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ["DB_NAME"]
    return pymongo.MongoClient(mongo_url)[db_name]


def _seed_analysis_row(account_id: str, context_id: str, aid: str) -> None:
    """Insert a synthesized `analyses` row carrying a Solva v2
    narration shape. Mirrors what synthesize_v2_endpoint persists
    at lines 1098-1146 of routers/workbook_analysis.py."""
    obs_id = "obs-" + uuid.uuid4().hex[:12]
    run_id = "run-" + uuid.uuid4().hex[:12]
    observations = [{
        "id": obs_id,
        "kind": "what_changed",
        "title": _OBS_TITLE,
        "detail": _OBS_BODY,
        "source_id": None,
        "citations": [{
            "index": 0,
            "cell_range": _CELL_RANGE,
            "excerpt": "412 → 71 units (week 6 vs 7)",
            "kind": "signal",
        }],
        "created_at": _now_iso(),
    }]
    row = {
        "id": aid,
        "account_id": account_id,
        "context_id": context_id,
        "title": "Quarterly product revenue review",
        "objective": "Understand why three product lines dropped in Q4.",
        "status": "ready",
        "headline": _HEADLINE,
        "observations": observations,
        "notes_history": [],
        "sources": [{
            "source_id": "src-" + uuid.uuid4().hex[:12],
            "filename": "Q4-revenue.xlsx",
            "file_format": "xlsx",
            "file_size_bytes": 12345,
            "uploaded_at": _now_iso(),
        }],
        "runs": [{
            "run_id": run_id,
            "created_at": _now_iso(),
            "triggered_by_account_id": account_id,
            "headline": _HEADLINE,
            "observations": observations,
            "citations": [{"cell_range": _CELL_RANGE, "kind": "signal"}],
            "forecast_meta": None,
            "cache_key": "ck-" + uuid.uuid4().hex[:12],
            "refused": False,
            "source_files": [],
        }],
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    _sync_db().analyses.insert_one(row)


def _seed_account(account_id: str, email: str) -> None:
    """Insert a stub account row good enough for get_current_account."""
    _sync_db().accounts.insert_one({
        "id": account_id,
        "email": email,
        "full_name": "Stage 4.3 Test",
        "hashed_password": "x",
        "active_context_id": None,
        "created_at": _now_iso(),
    })


def _auth_token_for(account_id: str, email: str) -> str:
    """Mint a JWT the test client can use against the live server."""
    from core import create_access_token
    return create_access_token(account_id, email)


@pytest.fixture
async def stage_4_3_client():
    """httpx.AsyncClient wired straight to the ASGI app. The same
    pattern test_phase_d_solva_pipeline.py uses — keeps every call
    on the conftest session loop so there is no Motor cross-loop
    drift when multiple test files run in the same session."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def stage_4_3_world():
    """Per-test ana-* row + JWT, cleaned up afterwards."""
    aid = "ana-" + uuid.uuid4().hex[:12]
    account_id = "acct-stg43-" + uuid.uuid4().hex[:8]
    context_id = "ctx-stg43-" + uuid.uuid4().hex[:8]
    email = f"stage43-{account_id}@test.local"

    _seed_account(account_id, email)
    _seed_analysis_row(account_id, context_id, aid)
    token = _auth_token_for(account_id, email)
    try:
        yield {"aid": aid, "account_id": account_id, "token": token}
    finally:
        sdb = _sync_db()
        sdb.analyses.delete_one({"id": aid})
        sdb.accounts.delete_one({"id": account_id})


def _client_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_docx_export_carries_solva_narration_headline(
    stage_4_3_client, stage_4_3_world,
):
    """DOCX export of a synthesized ana-* row contains the cached
    headline. Without the Stage 4.3 fix, the DOCX shipped with an
    empty signal-count blurb and no narrative voice."""
    r = await stage_4_3_client.get(
        f"/api/workbook/analyses/{stage_4_3_world['aid']}/report.docx",
        headers=_client_headers(stage_4_3_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]
    assert r.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # DOCX is a zip of XML; grep for the headline string inside
    # word/document.xml.
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        document_xml = zf.read("word/document.xml").decode("utf-8")
    assert _HEADLINE in document_xml, (
        f"Headline missing from DOCX: head={document_xml[:400]!r}"
    )
    assert _OBS_TITLE in document_xml, "Observation title missing from DOCX"
    # Cell-range citation should be present too.
    assert _CELL_RANGE in document_xml, "Citation cell range missing from DOCX"


@pytest.mark.asyncio
async def test_xlsx_export_carries_solva_narration_in_bottom_line_sheet(
    stage_4_3_client, stage_4_3_world,
):
    """XLSX export of a synthesized ana-* row contains the headline
    in a 'Bottom Line' sheet (sheet position 0)."""
    r = await stage_4_3_client.get(
        f"/api/workbook/analyses/{stage_4_3_world['aid']}/report.xlsx",
        headers=_client_headers(stage_4_3_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]

    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(r.content), read_only=False)
    assert "Bottom Line" in wb.sheetnames, (
        f"Bottom Line sheet missing. Sheets present: {wb.sheetnames}"
    )
    # The Bottom Line sheet should be at position 0 (insert_idx=0).
    assert wb.sheetnames[0] == "Bottom Line"
    bl = wb["Bottom Line"]
    flat_text = "\n".join(
        " | ".join(str(c) for c in row if c is not None)
        for row in bl.iter_rows(values_only=True)
    )
    assert _HEADLINE in flat_text, f"Headline missing from XLSX bottom line: {flat_text!r}"
    assert _OBS_TITLE in flat_text, "Observation title missing from XLSX bottom line"
    assert _CELL_RANGE in flat_text, "Citation cell range missing from XLSX bottom line"


@pytest.mark.asyncio
async def test_pptx_export_carries_solva_narration_slide(
    stage_4_3_client, stage_4_3_world,
):
    """PPTX export of a synthesized ana-* row contains a Bottom Line
    slide carrying the headline."""
    r = await stage_4_3_client.get(
        f"/api/workbook/analyses/{stage_4_3_world['aid']}/report.pptx",
        headers=_client_headers(stage_4_3_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]

    from pptx import Presentation
    prs = Presentation(io.BytesIO(r.content))
    all_text: list[str] = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            for para in shape.text_frame.paragraphs:
                all_text.append("".join(run.text for run in para.runs))
    blob = "\n".join(all_text)
    assert _HEADLINE in blob, f"Headline missing from PPTX text: {blob[:600]!r}"
    assert _OBS_TITLE in blob, "Observation title missing from PPTX text"


@pytest.mark.asyncio
async def test_pre_synthesis_analysis_still_exports_ok(
    stage_4_3_client, stage_4_3_world,
):
    """Regression: an `ana-*` row WITHOUT synthesis (no narration
    fields) must still produce a downloadable export — the new
    code path branches on `analyze_narration_headline` being set,
    so the legacy empty-shell path stays alive."""
    aid = stage_4_3_world["aid"]
    # Strip the narration fields off the row to simulate pre-synthesis.
    _sync_db().analyses.update_one(
        {"id": aid},
        {"$set": {"headline": "", "observations": [], "runs": []}},
    )
    r = await stage_4_3_client.get(
        f"/api/workbook/analyses/{aid}/report.docx",
        headers=_client_headers(stage_4_3_world["token"]),
    )
    assert r.status_code == 200, r.text[:300]
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        document_xml = zf.read("word/document.xml").decode("utf-8")
    # Headline shouldn't be present (we wiped it).
    assert _HEADLINE not in document_xml
    # But the cover heading + filename are still there — confirms
    # the document is a real artefact, not a 500-or-empty.
    assert re.search(r"Workbook Analysis", document_xml), (
        "Expected cover heading missing in pre-synthesis export"
    )
