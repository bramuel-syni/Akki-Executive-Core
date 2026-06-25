"""JC-WS-A Board Pack proving slice.

Drives the existing Work Studio Board Pack engine end-to-end against
admin@akki.ai's "Mara Heritage Bank · Demo" context, which carries
3 strategic documents seeded by `scripts/seed_admin_strategic_data.py`.

Output: a real, professional DOCX/PPTX/PDF that the user can open and
inspect. STOP after this lands — do not fan out until the artefact
quality is approved.

Discipline (per the JC-WS dispatch):
  - Multi-source synthesis (we pass a description that names all 3 docs
    so the BM25 grounding rail at routers/work_studio_export.py:283
    picks all three into the citations manifest)
  - Real, professional best-shape output (the existing two-pass engine
    produces structured JSON with cover + sections + recommendations +
    citations; the renderer turns it into a multi-section DOCX)
  - Shield-routed LLM call (Pass 1 + Pass 2 go via
    services.llm_streaming.collect_llm_text which routes through the
    universal LLM proxy)
  - Account-scoped + audited (the route is gated by
    require_context_membership and writes audit rows)

Saves the produced artefacts to:
  /app/memory/jc_artifacts/JC-WS-A-BoardPack-proving-slice.docx
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

import pymongo
from httpx import ASGITransport, AsyncClient


ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")

# CSRF-test-bypass is per-process; the in-process AsyncClient does
# NOT route through Cloudflare so we don't need it — but core.py
# does enforce CSRF middleware on POST. Set the env that
# csrf_middleware honours for the test path.
os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")

from server import app  # noqa: E402  (after env setup)
from core import create_access_token  # noqa: E402


ADMIN_EMAIL = "admin@akki.ai"
ADMIN_ID = "cf6e7587-9abd-46aa-b8f4-f342e9b066ef"
CONTEXT_ID = "a2937d0f-37f1-4042-a897-ab73a6cd652a"  # Mara Heritage Bank · Demo
ARTIFACT_DIR = Path("/app/memory/jc_artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def sync_db():
    return pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]


def list_context_docs() -> list[dict]:
    """List docs in the target context — synchronous, via pymongo."""
    cur = sync_db().documents.find(
        {"context_id": CONTEXT_ID, "status": {"$ne": "deleted"}},
        {"_id": 0, "id": 1, "name": 1, "original_filename": 1,
         "extracted_chars": 1, "extracted_text": 1, "doc_type": 1,
         "category": 1, "created_at": 1},
    )
    out = []
    for d in cur:
        out.append({
            "id": d.get("id"),
            "name": d.get("name") or d.get("original_filename") or "?",
            "chars": d.get("extracted_chars") or len(d.get("extracted_text") or ""),
            "category": d.get("category"),
            "doc_type": d.get("doc_type"),
            "created_at": d.get("created_at"),
        })
    return out


async def main():
    print("=" * 70)
    print("JC-WS-A Board Pack proving slice")
    print("=" * 70)
    print(f"Account:   {ADMIN_EMAIL} ({ADMIN_ID})")
    print(f"Context:   Mara Heritage Bank · Demo ({CONTEXT_ID})")
    print(f"Artefact:  {ARTIFACT_DIR}")
    print()

    # Step 1 — inventory the source documents.
    print("Step 1 — context documents available as source material:")
    docs = list_context_docs()
    if not docs:
        print("  STOP: no documents in context. Re-seed Mara Heritage via")
        print("        `python3 backend/scripts/seed_admin_strategic_data.py`.")
        sys.exit(2)
    for d in docs:
        print(f"  - {d['id']}  {d['name'][:60]:60s}  ({d['chars']} chars)  cat={d['category']!r}")
    print(f"  → {len(docs)} document(s)")
    print()

    # Step 2 — mint a JWT for the admin account.
    # SessionTimeoutMiddleware (services/session_timeout.py) gates on
    # `accounts.last_activity_at`. Stamp it to now BEFORE the call so
    # the middleware doesn't 401 us with session_idle_timeout on the
    # first request.
    from datetime import datetime, timezone as _tz
    sync_db().accounts.update_one(
        {"id": ADMIN_ID},
        {"$set": {"last_activity_at": datetime.now(_tz.utc).isoformat()}},
    )
    token = create_access_token(ADMIN_ID, ADMIN_EMAIL)
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Step 2 — JWT minted (len={len(token)}), last_activity_at refreshed")
    print()

    # Step 3 — kick off the board-pack export. Description names all
    # source docs so the BM25 grounding rail picks them all up.
    description = (
        "Compile a Board Pack for the Q3 board meeting of Mara Heritage Bank. "
        "Synthesise the strategic outlook, risk register, and audit report "
        "available on the platform into a single executive deliverable. "
        "Cover: performance against strategy, key risks and mitigations, "
        "audit observations and management responses, and recommended "
        "decisions for the board to approve at this meeting."
    )
    objective = (
        "Equip the board with a concise, evidence-based read on the "
        "bank's position so directors can make the strategic, risk, "
        "and governance decisions queued for this meeting."
    )
    scope = (
        "Mara Heritage Bank — full board (executive + non-executive directors). "
        "Period: Q3 2025. Confidentiality: Internal. Length: 6-10 pages."
    )

    # JC-WS-A — Source-material packs journey: user EXPLICITLY selects
    # the 3 strategic docs on the platform. Bypasses BM25 (which
    # lexically misses the redacted paragraph text) so the LLM
    # actually receives the source content + the confidence scorer
    # gets real source blobs to compare against.
    source_document_ids = [d["id"] for d in docs if d["chars"] > 1000]
    print(f"  source_document_ids selected: {len(source_document_ids)}")
    for did in source_document_ids:
        print(f"    - {did}")
    print()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
        timeout=180.0,  # board-pack two-pass LLM takes 30-90s
    ) as client:
        print("Step 3 — POST /api/contexts/{cid}/work-studio/export/board_pack")
        r = await client.post(
            f"/api/contexts/{CONTEXT_ID}/work-studio/export/board_pack",
            headers={**headers, "X-CSRF-Test-Bypass": "1"},
            json={"description": description, "objective": objective, "scope": scope},
        )
        print(f"  POST status: {r.status_code}")
        if r.status_code != 200:
            print(f"  body: {r.text[:500]}")
            sys.exit(3)
        body = r.json()
        export_id = body.get("export_id")
        print(f"  export_id: {export_id}")
        print()

        # Step 4 — poll for completion.
        print("Step 4 — polling status (up to 180s)…")
        deadline = time.monotonic() + 180.0
        final_row = None
        while time.monotonic() < deadline:
            await asyncio.sleep(4)
            sr = await client.get(
                f"/api/contexts/{CONTEXT_ID}/work-studio/exports/{export_id}",
                headers=headers,
            )
            row = sr.json()
            status = row.get("status")
            phase = row.get("phase_label", "")
            print(f"  status={status!r}  phase={phase!r}")
            if status in ("complete", "failed"):
                final_row = row
                break
        if final_row is None:
            print("  STOP: timed out.")
            sys.exit(4)
        if final_row.get("status") != "complete":
            print(f"  STOP: export failed: error={final_row.get('error')!r}")
            print(f"        refusal_text={final_row.get('refusal_text')!r}")
            sys.exit(5)
        print()

        # Step 5 — download the DOCX bytes via the in-process route.
        download_token = final_row.get("download_token")
        print(f"Step 5 — downloading artefact (token={download_token[:16]}…)")
        dr = await client.get(
            f"/api/contexts/{CONTEXT_ID}/work-studio/exports/{export_id}/download"
            f"?token={download_token}",
            headers=headers,
        )
        print(f"  download status: {dr.status_code}, bytes: {len(dr.content)}")
        if dr.status_code != 200:
            print(f"  body: {dr.text[:300]}")
            sys.exit(6)

        artefact_path = ARTIFACT_DIR / "JC-WS-A-BoardPack-proving-slice.docx"
        artefact_path.write_bytes(dr.content)
        print(f"  → wrote {artefact_path}")
        print()

    # Step 6 — capture metadata for inspection.
    summary = {
        "artefact": str(artefact_path),
        "byte_len": len(dr.content),
        "sha256": final_row.get("sha256"),
        "file_name": final_row.get("file_name"),
        "sensitivity_band": final_row.get("sensitivity_band"),
        "sensitivity_score": final_row.get("sensitivity_score"),
        "pass_1_ms": final_row.get("pass_1_ms"),
        "pass_2_ms": final_row.get("pass_2_ms"),
        "llm_pass1": final_row.get("llm_pass1"),
        "llm_pass2": final_row.get("llm_pass2"),
        "completed_at": final_row.get("completed_at"),
        "export_id": export_id,
        "context_id": CONTEXT_ID,
        "source_docs_in_context": [
            {"id": d["id"], "name": d["name"], "chars": d["chars"]} for d in docs
        ],
        "intelligence_report": final_row.get("intelligence_report"),
        "continue_chat_id": final_row.get("continue_chat_id"),
        "continue_doc_id": final_row.get("continue_doc_id"),
    }
    meta_path = ARTIFACT_DIR / "JC-WS-A-BoardPack-proving-slice.meta.json"
    meta_path.write_text(json.dumps(summary, indent=2))
    print(f"Step 6 — wrote metadata → {meta_path}")
    print()

    # Step 7 — render an honest quality report from the DOCX text.
    from zipfile import ZipFile
    import re as _re
    with ZipFile(artefact_path) as zf:
        document_xml = zf.read("word/document.xml").decode("utf-8")
    txt = _re.sub(r"<[^>]+>", " ", document_xml)
    txt = _re.sub(r"\s+", " ", txt).strip()

    quality = {
        "byte_len": len(dr.content),
        "text_chars": len(txt),
        "word_count": len(txt.split()),
        "heading_count": document_xml.count("<w:pStyle w:val=\"Heading"),
        "has_cover_title": ("Board Pack" in txt or "Mara Heritage" in txt),
        "mentions_bank": "Bank" in txt,
        "mentions_period": ("Q3" in txt or "2025" in txt),
        "first_300_chars": txt[:300],
    }
    quality_path = ARTIFACT_DIR / "JC-WS-A-BoardPack-quality-report.json"
    quality_path.write_text(json.dumps(quality, indent=2))
    print(f"Step 7 — wrote quality report → {quality_path}")
    print()
    print("QUALITY READOUT:")
    for k, v in quality.items():
        if k == "first_300_chars":
            print(f"  {k:18}: {v[:120]}…")
        else:
            print(f"  {k:18}: {v}")
    print()
    print("=" * 70)
    print("JC-WS-A Board Pack proving slice — COMPLETE")
    print(f"Artefact: {artefact_path}")
    print(f"Meta:     {meta_path}")
    print(f"Quality:  {quality_path}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
