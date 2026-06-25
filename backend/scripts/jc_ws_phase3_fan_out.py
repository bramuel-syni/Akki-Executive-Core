"""JC-WS Phase 3 fan-out — one artefact per kind, REAL outputs.

Source of truth: /app/memory/JC_WS_CANONICAL_SPEC.md

Per the spec § Fan out: "Replicate the proven pattern across Committee
Pack, Minutes, Brief (in-Studio: uploads first, then the Akki-fetch
input only once retrieval proves relevant), Deck, Report, Draft, and
the three enhance flows (minutes / reports / decks)."

Group A — Source-material packs (direct pattern reuse):
  Committee Pack:  DOCX + PPTX + PDF
  Minutes:         DOCX + PDF + TXT  (no PPTX renderer for minutes)

Group B — Blank-start (Report / Deck):
  Report:          DOCX
  Deck:            PPTX

Group C — Draft (save-draft endpoint, not export):
  Draft:           Save-draft to lifecycle_state="draft" via the
                   `/work-studio/documents/save-draft` endpoint.

Group D — Enhance (3 flows):
  Enhance Minutes / Report / Deck — each produces a "before" + "after"
  pair showing visible improvement against custom instructions.

Group E — Brief (in-Studio):
  Brief-uploads:   Generated from explicit source_document_ids (the
                   "uploads + AddToWorkStudio" path). Always works.
  Brief-akki-fetch: Generated from a NAMED context. Wires to existing
                   BM25 retrieval. GATED by the retrieval-quality
                   check on ≥3 named-context test cases.

Each kind writes:
  /app/memory/jc_artifacts/JC-WS-A-{Kind}-sample.{ext}
  /app/memory/jc_artifacts/JC-WS-A-{Kind}-sample.meta.json

Plus a roll-up acceptance report at the end.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone as _tz
from pathlib import Path
from typing import Any, Dict, List, Optional

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


def fetch_row(export_id: str) -> dict:
    return sync_db().work_studio_exports.find_one({"id": export_id}, {"_id": 0}) or {}


async def run_export(
    client: AsyncClient, headers: dict, *,
    kind: str, output_format: str,
    description: str, objective: str, scope: str,
    source_document_ids: List[str], cadence: str = "one_off",
    timeout_s: float = 240.0,
) -> dict:
    """POST export → poll → return final row + downloaded bytes (under
    `_download_bytes` if successful, else `error`)."""
    stamp_account_activity()
    r = await client.post(
        f"/api/contexts/{CONTEXT_ID}/work-studio/export/{kind}",
        headers=headers,
        json={
            "description": description,
            "objective":   objective,
            "scope":       scope,
            "output_format": output_format,
            "source_document_ids": source_document_ids,
            "cadence":     cadence,
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
                headers=headers, timeout=20.0,
            )
        except Exception:
            continue
        row = sr.json()
        st = row.get("status")
        if st in ("complete", "failed"):
            final = row
            break
    if not final:
        from_db = fetch_row(export_id) or {}
        if from_db.get("status") in ("complete", "failed"):
            final = from_db
        else:
            return {"_timeout": True, "id": export_id}
    final.setdefault("id", export_id)
    if final.get("status") != "complete":
        return final
    tok = final.get("download_token")
    if not tok:
        from_db = fetch_row(export_id) or {}
        tok = from_db.get("download_token") or tok
        if from_db:
            final = {**from_db, **final}
    if not tok:
        return {**final, "_no_download_token": True}
    dr = await client.get(
        f"/api/contexts/{CONTEXT_ID}/work-studio/exports/{export_id}/download?token={tok}",
        headers=headers, timeout=60.0,
    )
    final["_download_status"] = dr.status_code
    final["_download_bytes"] = dr.content
    return final


# ─────────────────────────────────────────────────────────────────────
# Kind-specific descriptions / objectives / scopes (executive-grade).
# These shape the LLM Pass-1 / Pass-2 content.
# ─────────────────────────────────────────────────────────────────────
KIND_BRIEFS: Dict[str, Dict[str, Any]] = {
    "committee_pack": {
        "description": (
            "Compile a Risk Committee pack for Mara Heritage Bank's quarterly "
            "review. Synthesise the credit risk, capital adequacy, operational "
            "risk, and concentration-risk material on the platform into a single "
            "Risk Committee deliverable. Cover: NPL trajectory, CET1 buffer "
            "movement, single-name concentration, and the risk-tolerance bands "
            "the committee needs to set or affirm at this meeting."
        ),
        "objective": (
            "Equip the Risk Committee with a focused, evidence-based read on "
            "where the bank's risk position sits versus tolerance, so members "
            "can recalibrate limits and approve the mitigation plans queued for "
            "this meeting."
        ),
        "scope": (
            "Mara Heritage Bank — Risk Committee. Period: Q3 2025. "
            "Confidentiality: Restricted. Length: 5-8 pages."
        ),
        "formats": ["docx", "pptx", "pdf"],
    },
    "minutes": {
        "description": (
            "Draft the formal minutes of the Mara Heritage Bank Q3 Board "
            "meeting. The materials on the platform record the agenda, the "
            "attendees, the substantive discussion on capital allocation, "
            "and the decisions queued. The minutes should capture "
            "attendees, agenda items, substantive discussion, decisions "
            "taken, dissent if any, and the action list with owners."
        ),
        "objective": (
            "Produce a faithful, structured record of the Q3 board meeting "
            "fit for the company secretary's books and for circulation to "
            "directors who could not attend."
        ),
        "scope": (
            "Mara Heritage Bank — Board of Directors. Meeting: Q3 2025. "
            "Confidentiality: Confidential. Length: 4-6 pages."
        ),
        "formats": ["docx", "pdf"],
    },
    "report": {
        "description": (
            "Write an executive report for Mara Heritage Bank's leadership "
            "team on the bank's strategic and operational position at the "
            "close of Q3 2025. Draw on the strategic, capital, and "
            "performance material on the platform. The report should set "
            "context, present analysis with citations, surface risks, and "
            "close with a clear set of recommendations."
        ),
        "objective": (
            "Give the CEO and direct reports a written, board-ready read on "
            "performance, risks, and the decisions the executive committee "
            "needs to take before the next board cycle."
        ),
        "scope": (
            "Mara Heritage Bank — Executive Committee. Period: Q3 2025. "
            "Confidentiality: Internal. Length: 8-12 pages."
        ),
        "formats": ["docx"],
    },
    "deck": {
        "description": (
            "Build a strategic update deck for Mara Heritage Bank's Q3 board "
            "session. Translate the strategic, capital, and risk material "
            "on the platform into a presentable deck: one section per "
            "strategic theme, one slide per substantive point, recommendations "
            "and decisions queued at the end."
        ),
        "objective": (
            "Allow the chair to walk the board through the substantive "
            "strategic update in a clear, evidence-backed sequence — "
            "decision-ready, not data-dumping."
        ),
        "scope": (
            "Mara Heritage Bank — full board. Meeting: Q3 2025. "
            "Confidentiality: Internal. Length: 12-18 slides."
        ),
        "formats": ["pptx"],
    },
    # Brief — uploads path (in-Studio 3b first input)
    "brief_uploads": {
        "_kind_for_export": "brief",
        "description": (
            "Prepare a one-page brief for the Mara Heritage Bank chair on the "
            "single most material strategic decision queued at the Q3 board "
            "meeting: how to allocate the projected Q4 capital headroom — "
            "between accelerating digital transformation, repurposing into "
            "SME lending, or holding for capital strength. The brief should "
            "frame the trade-off, summarise the evidence on each option, and "
            "name the recommended path."
        ),
        "objective": (
            "Give the chair a clear, decision-ready read on the capital "
            "allocation choice in time to set the board's discussion frame."
        ),
        "scope": (
            "Mara Heritage Bank — Chair (single reader). Decision window: "
            "Q3 2025 board meeting. Confidentiality: Confidential. Length: "
            "1-2 pages."
        ),
        "formats": ["pdf", "docx"],
    },
}


KIND_TO_ARTEFACT_LABEL = {
    "committee_pack": "CommitteePack",
    "minutes":        "Minutes",
    "report":         "Report",
    "deck":           "Deck",
    "brief_uploads":  "Brief-uploads",
}


def kind_for_export(k: str) -> str:
    return KIND_BRIEFS[k].get("_kind_for_export", k)


# ─────────────────────────────────────────────────────────────────────
async def ship_kind(client: AsyncClient, headers: dict, brief_key: str,
                    source_document_ids: List[str], results: Dict[str, Any]):
    """Generate ALL formats for a kind; persist each format + a meta.json."""
    brief = KIND_BRIEFS[brief_key]
    export_kind = kind_for_export(brief_key)
    label = KIND_TO_ARTEFACT_LABEL[brief_key]
    print(f"\n── {label.upper()} ─────────────────────────────────────────────────")
    results[brief_key] = {"label": label, "formats": {}}

    for fmt in brief["formats"]:
        print(f"  ▶ {label}/{fmt} — POST /export/{export_kind}")
        out = await run_export(
            client, headers,
            kind=export_kind, output_format=fmt,
            description=brief["description"],
            objective=brief["objective"],
            scope=brief["scope"],
            source_document_ids=source_document_ids,
            cadence="one_off",
            timeout_s=300.0,
        )
        if "_download_bytes" in out:
            ext_map = {"docx": "docx", "pdf": "pdf", "pptx": "pptx", "txt": "txt"}
            ext = ext_map.get(fmt, fmt)
            path = ARTIFACT_DIR / f"JC-WS-A-{label}-sample.{ext}"
            path.write_bytes(out["_download_bytes"])
            byte_len = len(out["_download_bytes"])
            print(f"    ✓ {fmt}: {byte_len} bytes → {path.name}")
            results[brief_key]["formats"][fmt] = {
                "ok": True, "bytes": byte_len, "path": str(path),
                "export_id": out.get("id"),
            }
        else:
            err = out.get("error") or out.get("refusal_text") or out.get("_post_body") or out.get("_no_download_token") or "unknown"
            print(f"    ✗ {fmt}: FAILED — {str(err)[:200]}")
            results[brief_key]["formats"][fmt] = {"ok": False, "error": str(err)[:600]}

    # Roll-up meta for this kind.
    meta_path = ARTIFACT_DIR / f"JC-WS-A-{label}-sample.meta.json"
    meta_path.write_text(json.dumps({
        "kind": export_kind,
        "label": label,
        "description": brief["description"],
        "objective":   brief["objective"],
        "scope":       brief["scope"],
        "source_document_ids_count": len(source_document_ids),
        "formats":     results[brief_key]["formats"],
        "generated_at": datetime.now(_tz.utc).isoformat(),
    }, indent=2, default=str))


# ─────────────────────────────────────────────────────────────────────
async def ship_draft(client: AsyncClient, headers: dict, results: Dict[str, Any]):
    """Draft journey — exercises the save-draft endpoint (lifecycle="draft")."""
    print("\n── DRAFT ──────────────────────────────────────────────────────────")
    structured_content = {
        "sections": [
            {
                "heading": "Q3 strategic update — draft",
                "paragraphs": [
                    "This is an in-progress draft. Akki and I are co-authoring the "
                    "strategic update for the EC in the editor. Once final, we will "
                    "commit to lock and export.",
                    "The capital allocation question is the single most material item "
                    "queued for Q3. The bank has projected $42M of CET1 headroom by "
                    "year-end; allocating that headroom to SME lending versus "
                    "accelerating digital transformation versus holding for capital "
                    "strength is the choice the board will need to take."
                ],
            },
        ],
    }
    body = {
        "draft_session_id": "draft-jc-ws-phase3-" + uuid.uuid4().hex[:12],
        "title": "Q3 2025 strategic update — co-authored draft",
        "structured_content": structured_content,
        "kind": "report",
    }
    stamp_account_activity()
    r = await client.post(
        f"/api/contexts/{CONTEXT_ID}/work-studio/documents/save-draft",
        headers=headers, json=body,
    )
    print(f"  POST /save-draft → {r.status_code}")
    if r.status_code == 200:
        payload = r.json()
        eid = payload.get("export_id")
        lc = payload.get("lifecycle_state")
        print(f"  ✓ Draft saved — export_id={eid}, lifecycle_state={lc!r}")
        # Persist the draft state as the artefact (no DOCX yet — that's
        # the deliberate canonical-spec promise for Draft: it's an
        # in-editor in-progress surface, not a generated file).
        artefact = {
            "export_id": eid,
            "lifecycle_state": lc,
            "kind": "report",
            "draft_session_id": body["draft_session_id"],
            "title": body["title"],
            "structured_content": structured_content,
            "saved_at": datetime.now(_tz.utc).isoformat(),
        }
        (ARTIFACT_DIR / "JC-WS-A-Draft-sample.json").write_text(
            json.dumps(artefact, indent=2, default=str)
        )
        print("  ✓ Draft artefact → JC-WS-A-Draft-sample.json")
        results["draft"] = {"label": "Draft", "ok": True, "export_id": eid, "lifecycle_state": lc}
    else:
        print(f"  ✗ Draft save failed: {r.text[:300]}")
        results["draft"] = {"label": "Draft", "ok": False, "error": r.text[:400]}


# ─────────────────────────────────────────────────────────────────────
ENHANCE_FLOWS = [
    {
        "key":  "enhance_minutes",
        "label": "Enhance-Minutes",
        "kind": "minutes",
        "before": (
            "Minutes of Q3 2025 board meeting.\n\nAttendees: see attached.\n\n"
            "Agenda items discussed.\n\nResolutions passed.\n\n"
            "Actions to be done.\n\nNext meeting: TBC."
        ),
        "instructions": (
            "Expand these minutes into a fully structured, company-secretary-grade "
            "document. Add a formal opening (date, time, location, chair, quorum), "
            "section the discussion by agenda item, capture substantive points with "
            "the directors who raised them, record decisions in resolution form, "
            "list actions with named owners and target dates, and close with "
            "any dissent and the date of the next meeting. Maintain the formal "
            "register; do not invent facts not present in the source."
        ),
        "ext": "docx",
    },
    {
        "key":  "enhance_report",
        "label": "Enhance-Report",
        "kind": "report",
        "before": (
            "Q3 performance report.\n\nRevenue: up.\n\nCosts: up too.\n\n"
            "Capital position: stable.\n\nRisks: same as last quarter.\n\n"
            "Conclusion: we are doing fine."
        ),
        "instructions": (
            "Rebuild this report into a board-grade executive report. Quantify "
            "the revenue and cost movements (state direction AND magnitude), "
            "present the capital position with a CET1 number, name the specific "
            "risks (concentration, credit, operational) and their current status, "
            "and close with a recommendation block. Drop hedging weasel words; "
            "lead each section with the substantive read. Cite the source documents."
        ),
        "ext": "docx",
    },
    {
        "key":  "enhance_deck",
        "label": "Enhance-Deck",
        "kind": "deck",
        "before": (
            "Slide 1: Title.\n\n"
            "Slide 2: Performance.\nGood.\n\n"
            "Slide 3: Risks.\nManaged.\n\n"
            "Slide 4: Outlook.\nPositive."
        ),
        "instructions": (
            "Rebuild this deck into a strategic update suitable for the board. "
            "Replace each placeholder with a substantive, single-headline slide "
            "(performance figures with directionality, named risks with current "
            "status, outlook with the decisions the board needs to take). One "
            "idea per slide. Include a recommendations slide at the end. "
            "Maintain executive register; remove platitudes."
        ),
        "ext": "pptx",
    },
]


async def ship_enhance(client: AsyncClient, headers: dict, results: Dict[str, Any]):
    """Enhance flows — produce a before + after pair per kind."""
    print("\n── ENHANCE FLOWS ──────────────────────────────────────────────────")
    for flow in ENHANCE_FLOWS:
        label = flow["label"]
        kind = flow["kind"]
        ext = flow["ext"]
        print(f"\n  ▶ {label} ({kind}/{ext})")

        # Persist the "before" as plain text we can reference in the meta.
        before_path = ARTIFACT_DIR / f"JC-WS-A-{label}-before.txt"
        before_path.write_text(flow["before"])
        print(f"    ✓ before (input snapshot) → {before_path.name}")

        # The "after" is generated via the standard generate-export endpoint
        # with the before text as the description and the instructions
        # threaded into the objective. This mirrors the enhance flow
        # contract (EnhanceModal posts to the same /export/{kind} surface).
        stamp_account_activity()
        out = await run_export(
            client, headers,
            kind=kind, output_format=ext,
            description=flow["before"],
            objective=flow["instructions"],
            scope="Mara Heritage Bank · Demo. Period: Q3 2025. Confidentiality: Internal.",
            source_document_ids=[],
            cadence="one_off",
            timeout_s=300.0,
        )
        if "_download_bytes" in out:
            after_path = ARTIFACT_DIR / f"JC-WS-A-{label}-after.{ext}"
            after_path.write_bytes(out["_download_bytes"])
            byte_len = len(out["_download_bytes"])
            print(f"    ✓ after: {byte_len} bytes → {after_path.name}")
            results[flow["key"]] = {
                "label": label, "ok": True,
                "before_path": str(before_path),
                "after_path":  str(after_path),
                "after_bytes": byte_len,
                "kind": kind,
                "format": ext,
            }
        else:
            err = out.get("error") or out.get("_post_body") or "unknown"
            print(f"    ✗ after FAILED — {str(err)[:200]}")
            results[flow["key"]] = {
                "label": label, "ok": False, "error": str(err)[:600],
            }


# ─────────────────────────────────────────────────────────────────────
async def main():
    print("=" * 78)
    print("JC-WS Phase 3 Fan-out — one artefact per kind, REAL outputs")
    print("=" * 78)
    print(f"Account:   {ADMIN_EMAIL}")
    print("Context:   Mara Heritage Bank · Demo")
    print(f"Artefacts: {ARTIFACT_DIR}")
    print()

    docs = list_context_docs()
    source_document_ids = [d["id"] for d in docs if d["chars"] > 1000]
    print(f"Source pool: {len(source_document_ids)} docs with >1000 chars.")
    print()

    token = create_access_token(ADMIN_ID, ADMIN_EMAIL)
    headers = hdrs(token)

    results: Dict[str, Any] = {}

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=600.0,
    ) as client:

        # ── Group A — Source-material packs (Committee Pack, Minutes)
        # ── Group B — Blank-start (Report, Deck)
        # ── Group E (uploads input) — Brief
        for brief_key in ("committee_pack", "minutes", "report", "deck", "brief_uploads"):
            await ship_kind(client, headers, brief_key, source_document_ids, results)

        # ── Group C — Draft
        await ship_draft(client, headers, results)

        # ── Group D — Enhance flows (3)
        await ship_enhance(client, headers, results)

    # ── Acceptance summary ─────────────────────────────────────────────
    print()
    print("=" * 78)
    print("PHASE 3 ROLL-UP")
    print("=" * 78)
    rows = []
    for key, r in results.items():
        label = r.get("label", key)
        if "formats" in r:
            for fmt, info in r["formats"].items():
                ok = bool(info.get("ok"))
                detail = (f"{info.get('bytes')} bytes" if ok
                          else (info.get("error","")[:120] or "fail"))
                rows.append((f"{label}/{fmt}", ok, detail))
        elif "before_path" in r:
            ok = bool(r.get("ok"))
            detail = (f"after={r.get('after_bytes',0)}B"
                      if ok else (r.get("error","")[:120] or "fail"))
            rows.append((f"{label}", ok, detail))
        else:
            ok = bool(r.get("ok"))
            detail = (r.get("export_id","") if ok else (r.get("error","")[:120] or "fail"))
            rows.append((f"{label}", ok, detail))
    passed = sum(1 for _, ok, _ in rows if ok)
    failed = len(rows) - passed
    for label, ok, detail in rows:
        sym = "✓" if ok else "✗"
        print(f"  [{sym}] {label:36s}  {detail}")
    print()
    print(f"  Result: {passed} passed, {failed} failed")
    print(f"  Artefacts: {ARTIFACT_DIR}")
    print("=" * 78)
    (ARTIFACT_DIR / "JC-WS-A-Phase3-fan-out-roll-up.json").write_text(
        json.dumps({
            "rows": [{"label": lbl, "ok": ok, "detail": d} for lbl, ok, d in rows],
            "passed": passed,
            "failed": failed,
            "generated_at": datetime.now(_tz.utc).isoformat(),
        }, indent=2, default=str)
    )
    print("  ✓ roll-up → JC-WS-A-Phase3-fan-out-roll-up.json")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
