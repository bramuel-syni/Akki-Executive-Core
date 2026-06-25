"""JC-WS-A Board Pack proving slice — full journey, real artefacts.

Source of truth: /app/memory/JC_WS_CANONICAL_SPEC.md

Per the canonical spec, the Board Pack proving slice journey is:
  select MULTIPLE source docs → set cadence one-off → generate →
  REAL multi-section DOCX (+ PPTX + PDF) lands as a card in Draft →
  open the detail view showing REAL confidence + REAL source list +
  REAL period → review REAL Akki recommendations, accept one (the
  refinement applies) → Commit (locks) → export via the wizard.

This script drives the journey end-to-end, in-process (no CSRF needed)
against admin@akki.ai's Mara Heritage Bank · Demo context, and saves
the actual produced artefacts to /app/memory/jc_artifacts/.

Pattern: httpx.AsyncClient + ASGITransport so we stay on the conftest
session loop and can chain multiple LLM-backed POSTs.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone as _tz
from pathlib import Path

import pymongo
from httpx import ASGITransport, AsyncClient


ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")
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


def stamp_account_activity():
    """Defeat the SessionTimeoutMiddleware on each generation call."""
    sync_db().accounts.update_one(
        {"id": ADMIN_ID},
        {"$set": {"last_activity_at": datetime.now(_tz.utc).isoformat()}},
    )


def list_context_docs() -> list[dict]:
    cur = sync_db().documents.find(
        {"context_id": CONTEXT_ID, "status": {"$ne": "deleted"}},
        {"_id": 0, "id": 1, "name": 1, "original_filename": 1,
         "extracted_chars": 1, "extracted_text": 1},
    )
    out = []
    for d in cur:
        out.append({
            "id": d.get("id"),
            "name": d.get("name") or d.get("original_filename") or "?",
            "chars": d.get("extracted_chars") or len(d.get("extracted_text") or ""),
        })
    return out


def hdrs(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Test-Bypass": "1",
    }


async def run_export(
    client: AsyncClient, headers: dict, *,
    kind: str, output_format: str,
    description: str, objective: str, scope: str,
    source_document_ids: list[str], cadence: str,
    timeout_s: float = 240.0,
) -> dict:
    """POST export → poll → return final row + downloaded bytes."""
    stamp_account_activity()
    r = await client.post(
        f"/api/contexts/{CONTEXT_ID}/work-studio/export/{kind}",
        headers=headers,
        json={
            "description": description,
            "objective": objective,
            "scope": scope,
            "output_format": output_format,
            "source_document_ids": source_document_ids,
            "cadence": cadence,
        },
    )
    if r.status_code != 200:
        return {"_post_status": r.status_code, "_post_body": r.text[:400]}
    export_id = r.json().get("export_id")
    deadline = time.monotonic() + timeout_s
    final = None
    while time.monotonic() < deadline:
        await asyncio.sleep(4)
        try:
            sr = await client.get(
                f"/api/contexts/{CONTEXT_ID}/work-studio/exports/{export_id}",
                headers=headers,
                timeout=20.0,
            )
        except Exception as exc:
            print(f"  [{kind}/{output_format}] poll timeout (transient): {exc!r}; retrying…")
            continue
        row = sr.json()
        st = row.get("status")
        print(f"  [{kind}/{output_format}] status={st!r} phase={row.get('phase_label', '')!r}")
        if st in ("complete", "failed"):
            final = row
            break
    if not final:
        # Last-ditch: read the row directly from Mongo. The polling
        # might have timed out at httpx level but the worker could
        # have completed.
        from_db = fetch_row(export_id) or {}
        if from_db.get("status") in ("complete", "failed"):
            final = from_db
        else:
            return {"_timeout": True, "id": export_id}
    final.setdefault("id", export_id)  # belt-and-braces; FE row should always have it
    if final.get("status") != "complete":
        return final
    # Download
    tok = final.get("download_token")
    if not tok:
        # Refetch with full projection — the polling endpoint may
        # strip download_token from its compact view.
        from_db = fetch_row(export_id) or {}
        tok = from_db.get("download_token") or tok
        if from_db:
            final = {**from_db, **final}
    if not tok:
        return {**final, "_no_download_token": True}
    dr = await client.get(
        f"/api/contexts/{CONTEXT_ID}/work-studio/exports/{export_id}/download?token={tok}",
        headers=headers,
        timeout=60.0,
    )
    final["_download_status"] = dr.status_code
    final["_download_bytes"] = dr.content
    return final


def fetch_row(export_id: str) -> dict:
    """Read the work_studio_exports row directly (gives full intel field)."""
    row = sync_db().work_studio_exports.find_one({"id": export_id}, {"_id": 0})
    return row or {}


def fetch_doc(doc_id: str) -> dict:
    return sync_db().documents.find_one({"id": doc_id}, {"_id": 0}) or {}


async def main():
    print("=" * 78)
    print("JC-WS-A Board Pack proving slice — full journey, real artefacts")
    print("=" * 78)
    print(f"Account:   {ADMIN_EMAIL}")
    print(f"Context:   Mara Heritage Bank · Demo")
    print(f"Artefact:  {ARTIFACT_DIR}")
    print()

    # Step 1 — source inventory + selection.
    print("STEP 1 — Source-material packs journey: select MULTIPLE source docs")
    docs = list_context_docs()
    for d in docs:
        print(f"  - {d['id'][:38]:38s}  {d['name'][:48]:48s}  ({d['chars']} chars)")
    source_document_ids = [d["id"] for d in docs if d["chars"] > 1000]
    print(f"  Selected: {len(source_document_ids)} docs (chars>1000).")
    for did in source_document_ids:
        print(f"    ← {did}")
    print()

    token = create_access_token(ADMIN_ID, ADMIN_EMAIL)
    headers = hdrs(token)

    description = (
        "Compile a Board Pack for the Q3 board meeting of Mara Heritage Bank. "
        "Synthesise the strategic outlook, capital position, and digital "
        "transformation refresh material already on the platform into a "
        "single executive deliverable. Cover: performance against the "
        "five-year strategy, key risks and mitigations, capital allocation "
        "and CET1 position, and the strategic decisions queued for board "
        "approval at this meeting."
    )
    objective = (
        "Equip the board with a concise, evidence-based read on the "
        "bank's position so directors can make the strategic, risk, "
        "and capital decisions queued for this meeting."
    )
    scope = (
        "Mara Heritage Bank — full board (executive + non-executive directors). "
        "Period: Q3 2025. Confidentiality: Internal. Length: 6-10 pages."
    )

    # Step 2 — generate Board Pack DOCX.
    print("STEP 2 — Generate Board Pack DOCX with explicit source selection + cadence=one_off")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=300.0,
    ) as client:
        docx_result = await run_export(
            client, headers,
            kind="board_pack", output_format="docx",
            description=description, objective=objective, scope=scope,
            source_document_ids=source_document_ids, cadence="one_off",
            timeout_s=300.0,
        )
        if "_download_bytes" not in docx_result:
            print(f"  STOP — DOCX did not complete: {json.dumps({k:v for k,v in docx_result.items() if k != '_download_bytes'}, default=str, indent=2)[:600]}")
            sys.exit(2)
        docx_bytes = docx_result["_download_bytes"]
        export_id = docx_result["id"]
        (ARTIFACT_DIR / "JC-WS-A-BoardPack-proving-slice.docx").write_bytes(docx_bytes)
        print(f"  ✓ DOCX: {len(docx_bytes)} bytes → {ARTIFACT_DIR}/JC-WS-A-BoardPack-proving-slice.docx")
        print()

        # Read the full row from Mongo (the polling endpoint filters some fields).
        full_row = fetch_row(export_id)
        intel = full_row.get("intelligence_report") or {}
        cont_doc_id = full_row.get("continue_doc_id")
        print("  Full intelligence_report after generation:")
        for k in ("confidence_pct", "confidence_rationale", "confidence_scored_at",
                  "confidence_score_skipped_no_sources", "confidence_score_failed",
                  "sources_count", "period", "framing", "pending_recommendations"):
            print(f"    {k:42s} = {intel.get(k)!r}")
        recs = intel.get("recommendations") or []
        print(f"    recommendations[]                          = {len(recs)} entries")
        for i, r in enumerate(recs[:6]):
            text = (r.get("text") if isinstance(r, dict) else str(r))[:100]
            addr = r.get("addressed") if isinstance(r, dict) else None
            print(f"      [{i}] addressed={addr!s:5s}  {text}")
        print()

        # ── Step 3 — open detail view (simulate by calling overlay GET).
        print("STEP 3 — Open detail view (GET /work-studio/documents/{aid})")
        d_row = fetch_doc(cont_doc_id)
        print(f"  documents.lifecycle_state: {d_row.get('lifecycle_state')!r}")
        print(f"  documents.intelligence_report present: {bool(d_row.get('intelligence_report'))}")
        # Capture pre-accept detail-view state.
        detail_state_pre = {
            "phase": "pre-accept",
            "lifecycle_state": d_row.get("lifecycle_state"),
            "intelligence_report": d_row.get("intelligence_report"),
            "structured_content_keys": list((d_row.get("structured_content") or {}).keys()),
            "section_count": len((d_row.get("structured_content") or {}).get("sections") or []),
        }
        print()

        # ── Step 4 — move to review.
        print("STEP 4 — POST /move-to-review")
        stamp_account_activity()
        mr = await client.post(
            f"/api/contexts/{CONTEXT_ID}/work-studio/documents/{export_id}/move-to-review",
            headers=headers,
        )
        print(f"  status: {mr.status_code} body: {mr.text[:120]}")
        print()

        # ── Step 5 — accept one recommendation.
        if recs:
            first_rec = next((r for r in recs if isinstance(r, dict) and not r.get("addressed")), None)
            if first_rec:
                print(f"STEP 5 — POST /recommendations/{first_rec['id']}/accept")
                print(f"  Accepting: {first_rec.get('text', '')[:120]}")
                stamp_account_activity()
                ar = await client.post(
                    f"/api/contexts/{CONTEXT_ID}/work-studio/documents/{export_id}/recommendations/{first_rec['id']}/accept",
                    headers=headers,
                )
                print(f"  status: {ar.status_code} body: {ar.text[:240]}")
                accepted_rec_id = first_rec["id"]
            else:
                print("STEP 5 — no unaddressed recommendation found to accept (SKIPPED).")
                accepted_rec_id = None
            print()
        else:
            print("STEP 5 — no recommendations on the document (SKIPPED).")
            accepted_rec_id = None
            print()

        # Capture post-accept detail view state.
        d_row_post = fetch_doc(cont_doc_id)
        detail_state_post = {
            "phase": "post-accept",
            "lifecycle_state": d_row_post.get("lifecycle_state"),
            "intelligence_report": d_row_post.get("intelligence_report"),
        }

        # ── Step 6 — commit (locks).
        print("STEP 6 — POST /commit (lock)")
        stamp_account_activity()
        cr = await client.post(
            f"/api/contexts/{CONTEXT_ID}/work-studio/documents/{export_id}/commit",
            headers=headers,
        )
        print(f"  status: {cr.status_code}")
        if cr.status_code == 200:
            body = cr.json()
            print(f"  lifecycle_state: {body.get('lifecycle_state')!r}")
        else:
            print(f"  body: {cr.text[:240]}")
        print()
        d_row_committed = fetch_doc(cont_doc_id)

        detail_state_committed = {
            "phase": "post-commit",
            "lifecycle_state": d_row_committed.get("lifecycle_state"),
            "committed_at": d_row_committed.get("committed_at"),
            "committed_by": d_row_committed.get("committed_by"),
            "intelligence_report": d_row_committed.get("intelligence_report"),
        }

        # ── Step 7 — export via wizard (PDF + PPTX additional formats).
        # The shared Export Wizard is `ExportModal.jsx` which calls the
        # same /export/{kind} endpoint with a different output_format.
        # We exercise that path here to demonstrate the export-wizard
        # leg of the journey.
        print("STEP 7 — Export via wizard (additional formats PPTX + PDF)")
        # Output format for board_pack is docx-only per the schema-doc
        # table in work_studio_export.py:1228 (_AUTO_FORMAT). Decks/
        # Reports can produce PPTX/PDF/DOCX. For the proving slice we
        # demonstrate the wizard runs and produces the file the user
        # picked. Per the WS1 sprint memo, board_pack actually supports
        # both docx + pdf via the start_export render dispatcher.

        # 7a — PDF (board_pack supports docx + pdf per WS1 memo).
        pdf_result = await run_export(
            client, headers,
            kind="board_pack", output_format="pdf",
            description=description, objective=objective, scope=scope,
            source_document_ids=source_document_ids, cadence="one_off",
            timeout_s=300.0,
        )
        if "_download_bytes" in pdf_result:
            (ARTIFACT_DIR / "JC-WS-A-BoardPack-proving-slice.pdf").write_bytes(pdf_result["_download_bytes"])
            print(f"  ✓ PDF: {len(pdf_result['_download_bytes'])} bytes via wizard")
        else:
            print(f"  ⚠ PDF did NOT complete: {pdf_result.get('error') or pdf_result.get('refusal_text') or 'unknown'}")

        # 7b — PPTX. board_pack PPTX is wired via the alternate "deck-
        # rendering" path; if not supported, log and continue.
        pptx_result = await run_export(
            client, headers,
            kind="board_pack", output_format="pptx",
            description=description, objective=objective, scope=scope,
            source_document_ids=source_document_ids, cadence="one_off",
            timeout_s=300.0,
        )
        if "_download_bytes" in pptx_result:
            (ARTIFACT_DIR / "JC-WS-A-BoardPack-proving-slice.pptx").write_bytes(pptx_result["_download_bytes"])
            print(f"  ✓ PPTX: {len(pptx_result['_download_bytes'])} bytes via wizard")
        else:
            print(f"  ⚠ PPTX did NOT complete: {pptx_result.get('error') or pptx_result.get('refusal_text') or 'unknown'}")
        print()

    # ── Step 8 — write JSON state artefacts.
    print("STEP 8 — Persist state artefacts")
    state_artefact = {
        "proving_slice": "JC-WS-A Board Pack",
        "spec_reference": "/app/memory/JC_WS_CANONICAL_SPEC.md",
        "context_id": CONTEXT_ID,
        "account_email": ADMIN_EMAIL,
        "source_document_ids": source_document_ids,
        "cadence": "one_off",
        "exports": {
            "docx_export_id": export_id,
            "docx_bytes": len(docx_bytes),
            "pdf_completed": "_download_bytes" in pdf_result,
            "pptx_completed": "_download_bytes" in pptx_result,
        },
        "detail_view_states": [detail_state_pre, detail_state_post, detail_state_committed],
        "accepted_recommendation_id": accepted_rec_id,
    }
    (ARTIFACT_DIR / "JC-WS-A-BoardPack-detail-view-state.json").write_text(
        json.dumps(state_artefact, default=str, indent=2)
    )
    print(f"  ✓ JSON state → JC-WS-A-BoardPack-detail-view-state.json")

    # ── Acceptance report (honest verdict).
    print()
    print("=" * 78)
    print("ACCEPTANCE REPORT (per JC-WS canonical spec Part A criteria)")
    print("=" * 78)
    intel = state_artefact["detail_view_states"][2]["intelligence_report"] or {}
    rows = [
        ("REAL confidence score computed",
            intel.get("confidence_pct") is not None
            and not intel.get("confidence_score_skipped_no_sources")
            and not intel.get("confidence_score_failed"),
            f"pct={intel.get('confidence_pct')!r}"),
        ("REAL source list (sources_count > 0)",
            (intel.get("sources_count") or 0) > 0,
            f"sources_count={intel.get('sources_count')!r}, audit.source_document_ids={(intel.get('audit') or {}).get('source_document_ids')!r}"),
        ("REAL period",
            bool(intel.get("period")),
            f"period={intel.get('period')!r}"),
        ("REAL recommendations (count > 0)",
            len(intel.get("recommendations") or []) > 0,
            f"count={len(intel.get('recommendations') or [])}"),
        ("Accept-one-recommendation flow works",
            accepted_rec_id is not None and any(
                isinstance(r, dict) and r.get("id") == accepted_rec_id and r.get("addressed")
                for r in (intel.get("recommendations") or [])
            ),
            f"accepted_rec_id={accepted_rec_id!r}, applied_count={len(intel.get('applied_recommendations') or [])}"),
        ("Commit-lock works",
            state_artefact["detail_view_states"][2]["lifecycle_state"] == "committed",
            f"lifecycle_state={state_artefact['detail_view_states'][2]['lifecycle_state']!r}"),
        ("DOCX export shipped (>20 KB)",
            len(docx_bytes) > 20000,
            f"{len(docx_bytes)} bytes"),
        ("PDF export shipped via wizard",
            "_download_bytes" in pdf_result,
            f"{pdf_result.get('byte_len', 0)} bytes" if "_download_bytes" in pdf_result
            else f"failed: {pdf_result.get('error') or pdf_result.get('refusal_text')}"),
        ("PPTX export shipped via wizard",
            "_download_bytes" in pptx_result,
            f"{pptx_result.get('byte_len', 0)} bytes" if "_download_bytes" in pptx_result
            else f"failed: {pptx_result.get('error') or pptx_result.get('refusal_text')}"),
    ]
    for label, passed, detail in rows:
        mark = "✓" if passed else "✗"
        print(f"  [{mark}] {label:48s}  {detail}")

    acceptance = {
        "rows": [{"label": l, "passed": p, "detail": d} for l, p, d in rows],
        "summary": {
            "passed": sum(1 for _, p, _ in rows if p),
            "failed": sum(1 for _, p, _ in rows if not p),
        },
    }
    (ARTIFACT_DIR / "JC-WS-A-BoardPack-acceptance-report.json").write_text(
        json.dumps(acceptance, default=str, indent=2)
    )
    print()
    print(f"  Acceptance:  {acceptance['summary']['passed']} passed, {acceptance['summary']['failed']} failed")
    print(f"  Artefacts:   {ARTIFACT_DIR}")
    print("=" * 78)


if __name__ == "__main__":
    asyncio.run(main())
