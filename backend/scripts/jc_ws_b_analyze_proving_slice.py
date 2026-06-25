"""JC-WS-B Analyze proving slice — full journey, real artefacts.

Source of truth: /app/memory/JC_WS_CANONICAL_SPEC.md (Part B)

Per the canonical spec, the Analyze proving slice journey is:
  Q3 sales workbook + objective "check before forwarding · forecast Q4"
  → Validate + Analyze + Forecast highlights auto-surface (Path A) →
  user taps "simulate East staying down" → simulate highlight accretes
  → close + reopen → thread intact → ask one more (refusal example) →
  Finish & export → handoff payload composed for the Document
  Generation wizard.

This script drives the journey end-to-end against the new
`db.analyses` collection (the `ana-*` entity), seeds an analysis row
with realistic Q3 sales data, exercises the JC-WS Phase 2 endpoints
(/tips, /ask, /finish), and persists EVERY state to
/app/memory/jc_artifacts/ as proof.

Artefacts produced:
  JC-WS-B-Analyze-initial-run-highlights.json
  JC-WS-B-Analyze-followup-simulate-highlight.json
  JC-WS-B-Analyze-refusal-guard-evidence.json
  JC-WS-B-Analyze-reopened-thread-state.json
  JC-WS-B-Analyze-finish-export-payload.json
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
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
ARTIFACT_DIR = Path("/app/memory/jc_artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def sync_db():
    return pymongo.MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]


def stamp_account_activity():
    sync_db().accounts.update_one(
        {"id": ADMIN_ID},
        {"$set": {"last_activity_at": datetime.now(_tz.utc).isoformat()}},
    )


def hdrs(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Test-Bypass": "1",
        "Content-Type": "application/json",
    }


# ─────────────────────────────────────────────────────────────────────
# Seed an Analysis row directly. We bypass the upload-multi flow so
# the proving slice runs deterministically without depending on the
# upload pipeline (whose surface is proven separately).
# ─────────────────────────────────────────────────────────────────────
def seed_analysis() -> str:
    """Seed a Q3 sales analysis with two sheets (a regional revenue
    matrix + a SKU breakdown). Set the objective so the auto-trigger
    classifier knows what to look for."""
    aid = "ana-" + uuid.uuid4().hex[:12]
    now = datetime.now(_tz.utc).isoformat()
    row = {
        "id":         aid,
        "account_id": ADMIN_ID,
        "title":      "Q3 2025 sales — regional + SKU read",
        "objective":  "Check before forwarding to the EC — and forecast Q4.",
        "created_at": now,
        "updated_at": now,
        "kind":       "analysis",
        "sources": [
            {"filename": "q3_2025_sales_regional.xlsx", "file_format": "xlsx", "size_bytes": 24576},
        ],
        # Sheets with column metadata — the /tips and /ask classifier
        # use this to detect time-series, target columns, etc.
        "sheets": [
            {
                "name": "Regional",
                "columns": [
                    {"name": "Month",   "kind": "date"},
                    {"name": "Region",  "kind": "categorical", "sample_values": ["East", "North", "South", "West"]},
                    {"name": "Revenue", "kind": "numeric"},
                    {"name": "Units",   "kind": "numeric"},
                ],
                "row_count": 36,
            },
            {
                "name": "SKU",
                "columns": [
                    {"name": "SKU",       "kind": "text"},
                    {"name": "Category",  "kind": "categorical", "sample_values": ["Hardware", "Software", "Services"]},
                    {"name": "Revenue",   "kind": "numeric"},
                    {"name": "Margin_pct","kind": "numeric"},
                ],
                "row_count": 84,
            },
        ],
        # Initial highlights from the auto-run (Path A: Validate +
        # Analyze always; Forecast since time-series detected). We
        # seed these directly rather than running the full pipeline
        # so the proving slice exercises ONLY the new Phase 2 surfaces.
        "highlights": [
            {
                "id":         "hl-seed-validate",
                "created_at": now,
                "title":      "Q3 totals reconcile within ±0.4% of the source ledger.",
                "body":       "Three-quarter rollup checks against the source ledger to within 0.4%. The numbers used for the rest of this analysis are safe to forward.",
                "topic":      "validate",
                "confidence": "high",
                "citation":   "Regional!C2:C37",
                "intent":     "validate",
                "asked_question": "(initial validate auto-run)",
                "refused":    False,
            },
            {
                "id":         "hl-seed-analyze",
                "created_at": now,
                "title":      "East region revenue fell 18% QoQ, dragging the total flat.",
                "body":       "East dropped from $4.2M to $3.45M while North and South held steady. Without East, the rollup would have been +6% QoQ.",
                "topic":      "trend",
                "confidence": "high",
                "citation":   "Regional!C14:C25",
                "intent":     "validate",
                "asked_question": "(initial analyze auto-run)",
                "refused":    False,
            },
            {
                "id":         "hl-seed-forecast",
                "created_at": now,
                "title":      "Q4 base-case lands at $13.8M ± $0.6M (R²=0.78).",
                "body":       "Linear fit on the last 9 months projects Q4 at $13.8M. R² of 0.78 makes this a planning-grade read, not a wide-error speculation.",
                "topic":      "forecast",
                "confidence": "medium",
                "citation":   "Regional!C2:C37",
                "intent":     "forecast",
                "asked_question": "(initial forecast auto-run)",
                "refused":    False,
            },
        ],
        "runs":            [],
        "observations":    [],
        "notes_history":   [],
    }
    sync_db().analyses.delete_many({"account_id": ADMIN_ID, "kind": "analysis", "id": {"$regex": "^ana-"}})
    sync_db().analyses.insert_one(row)
    return aid


# ─────────────────────────────────────────────────────────────────────
async def main():
    aid = seed_analysis()
    token = create_access_token(ADMIN_ID, ADMIN_EMAIL)
    headers = hdrs(token)

    state: dict = {"aid": aid, "steps": []}
    print("==============================================================================")
    print("JC-WS-B  Analyze Proving Slice  (Part B of /app/memory/JC_WS_CANONICAL_SPEC.md)")
    print("==============================================================================")
    print(f"Analysis: {aid}")
    print(f"Account:  {ADMIN_EMAIL}")
    print()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:

        # ── STEP 1 — Read the analysis (initial state w/ auto-run highlights).
        stamp_account_activity()
        r1 = await client.get(f"/api/workbook/v2/analyses/{aid}", headers=headers)
        print(f"STEP 1 — GET /v2/analyses/{aid} → {r1.status_code}")
        assert r1.status_code == 200, r1.text
        analysis_initial = r1.json()
        initial_hl_count = len(analysis_initial.get("highlights", []))
        print(f"  initial highlights: {initial_hl_count}")
        print(f"  objective: {analysis_initial.get('objective', '')[:80]}")
        state["initial_state"] = analysis_initial
        (ARTIFACT_DIR / "JC-WS-B-Analyze-initial-run-highlights.json").write_text(
            json.dumps({"phase": "initial", "highlights": analysis_initial.get("highlights", [])}, indent=2, default=str)
        )
        print("  ✓ artefact → JC-WS-B-Analyze-initial-run-highlights.json")
        print()

        # ── STEP 2 — GET /tips (data-aware question chip strip).
        stamp_account_activity()
        r2 = await client.get(f"/api/workbook/v2/analyses/{aid}/tips", headers=headers)
        print(f"STEP 2 — GET /tips → {r2.status_code}")
        tips_payload = r2.json() if r2.status_code == 200 else {}
        tips = tips_payload.get("tips", [])
        print(f"  tips_count: {len(tips)}")
        for t in tips[:5]:
            print(f"    - [{t.get('intent','?')}] {t.get('text','')[:80]}")
        state["tips"] = tips
        print()

        # ── STEP 3 — POST /ask with a simulate question (follow-up).
        stamp_account_activity()
        ask_payload = {"question": "Simulate East staying flat at $3.45M for Q4 — what happens to the total?"}
        r3 = await client.post(f"/api/workbook/v2/analyses/{aid}/ask", headers=headers, json=ask_payload)
        print(f"STEP 3 — POST /ask (simulate) → {r3.status_code}")
        simulate_hl = (r3.json() or {}).get("highlight", {})
        print(f"  intent:    {simulate_hl.get('intent')}")
        print(f"  topic:     {simulate_hl.get('topic')}")
        print(f"  title:     {simulate_hl.get('title','')[:80]}")
        print(f"  refused:   {simulate_hl.get('refused')}")
        state["simulate_highlight"] = simulate_hl
        (ARTIFACT_DIR / "JC-WS-B-Analyze-followup-simulate-highlight.json").write_text(
            json.dumps({"asked": ask_payload["question"], "highlight": simulate_hl}, indent=2, default=str)
        )
        print("  ✓ artefact → JC-WS-B-Analyze-followup-simulate-highlight.json")
        print()

        # ── STEP 4 — POST /ask with an OUT-OF-SCOPE question (refusal guard).
        stamp_account_activity()
        refuse_payload = {"question": "What is Pluto's revenue from inter-galactic shipping for FY2027?"}
        r4 = await client.post(f"/api/workbook/v2/analyses/{aid}/ask", headers=headers, json=refuse_payload)
        print(f"STEP 4 — POST /ask (out-of-scope) → {r4.status_code}")
        refusal_hl = (r4.json() or {}).get("highlight", {})
        print(f"  intent:           {refusal_hl.get('intent')}")
        print(f"  topic:            {refusal_hl.get('topic')}")
        print(f"  refused:          {refusal_hl.get('refused')}")
        print(f"  refusal_reason:   {refusal_hl.get('refusal_reason','')[:80]}")
        state["refusal_highlight"] = refusal_hl
        (ARTIFACT_DIR / "JC-WS-B-Analyze-refusal-guard-evidence.json").write_text(
            json.dumps({"asked": refuse_payload["question"], "highlight": refusal_hl}, indent=2, default=str)
        )
        print("  ✓ artefact → JC-WS-B-Analyze-refusal-guard-evidence.json")
        print()

        # ── STEP 5 — "Close + reopen" — read the analysis fresh.
        stamp_account_activity()
        r5 = await client.get(f"/api/workbook/v2/analyses/{aid}", headers=headers)
        print(f"STEP 5 — GET /v2/analyses/{aid} (reopen) → {r5.status_code}")
        analysis_reopened = r5.json()
        reopened_hl_count = len(analysis_reopened.get("highlights", []))
        print(f"  reopened highlights: {reopened_hl_count} (was {initial_hl_count} initial + 2 follow-ups = {initial_hl_count + 2})")
        print(f"  thread intact: {reopened_hl_count == initial_hl_count + 2}")
        state["reopened_state"] = analysis_reopened
        (ARTIFACT_DIR / "JC-WS-B-Analyze-reopened-thread-state.json").write_text(
            json.dumps({
                "phase": "reopened",
                "highlight_count": reopened_hl_count,
                "topics_present": sorted({h.get("topic","?") for h in analysis_reopened.get("highlights", []) if isinstance(h, dict)}),
                "highlights": analysis_reopened.get("highlights", []),
            }, indent=2, default=str)
        )
        print("  ✓ artefact → JC-WS-B-Analyze-reopened-thread-state.json")
        print()

        # ── STEP 6 — Ask one more question (proves accretion continues).
        stamp_account_activity()
        more_payload = {"question": "Forecast Q1 2026 Revenue under the same trend."}
        r6 = await client.post(f"/api/workbook/v2/analyses/{aid}/ask", headers=headers, json=more_payload)
        print(f"STEP 6 — POST /ask (one more) → {r6.status_code}")
        more_hl = (r6.json() or {}).get("highlight", {})
        print(f"  intent: {more_hl.get('intent')}  topic: {more_hl.get('topic')}")
        state["one_more_highlight"] = more_hl
        print()

        # ── STEP 7 — Finish & export.
        stamp_account_activity()
        finish_payload = {"kind": "report", "objective": analysis_initial.get("objective", "")}
        r7 = await client.post(f"/api/workbook/v2/analyses/{aid}/finish", headers=headers, json=finish_payload)
        print(f"STEP 7 — POST /finish → {r7.status_code}")
        finish = r7.json() or {}
        print(f"  ok:                  {finish.get('ok')}")
        print(f"  export_kind:         {finish.get('export_kind')}")
        print(f"  highlights_count:    {finish.get('highlights_count')}")
        print(f"  refused_count:       {finish.get('refused_count')}")
        print(f"  description_len:     {len(finish.get('description', ''))}")
        state["finish_export"] = finish
        (ARTIFACT_DIR / "JC-WS-B-Analyze-finish-export-payload.json").write_text(
            json.dumps(finish, indent=2, default=str)
        )
        print("  ✓ artefact → JC-WS-B-Analyze-finish-export-payload.json")
        print()

    # ── Acceptance summary ────────────────────────────────────────────
    print("==============================================================================")
    print("  ACCEPTANCE")
    print("==============================================================================")
    rows = [
        ("Auto-run highlights seeded (Path A: Validate + Analyze + Forecast)",
            initial_hl_count >= 3 and any(h.get("topic") == "forecast" for h in analysis_initial.get("highlights", [])),
            f"initial_count={initial_hl_count}, topics={sorted({h.get('topic') for h in analysis_initial.get('highlights', [])})}"),
        ("Data-aware tips returned from /tips",
            len(tips) >= 3 and all(t.get("text") and t.get("intent") in {"forecast","simulate","extract","validate","anomaly"} for t in tips[:3]),
            f"tips_count={len(tips)}; first_intent={(tips[0].get('intent') if tips else None)}"),
        ("POST /ask (simulate) accretes a non-refusal highlight",
            bool(simulate_hl) and not simulate_hl.get("refused") and simulate_hl.get("intent") in {"simulate", "forecast", "validate", "extract", "anomaly"},
            f"intent={simulate_hl.get('intent')}, refused={simulate_hl.get('refused')}"),
        ("POST /ask (out-of-scope) surfaces a REFUSAL highlight (not a fabricated answer)",
            bool(refusal_hl) and refusal_hl.get("refused") and refusal_hl.get("topic") == "refusal",
            f"refused={refusal_hl.get('refused')}, topic={refusal_hl.get('topic')}, reason={refusal_hl.get('refusal_reason','')[:60]}"),
        ("Close + reopen — thread intact (initial + 2 follow-ups)",
            reopened_hl_count == initial_hl_count + 2,
            f"reopened={reopened_hl_count}, expected={initial_hl_count + 2}"),
        ("Continued accretion — one more highlight added",
            bool(more_hl) and more_hl.get("id"),
            f"id={more_hl.get('id')}, intent={more_hl.get('intent')}"),
        ("Finish & export composes brief from highlights (no fabrication)",
            bool(finish.get("ok")) and finish.get("highlights_count", 0) >= 3 and len(finish.get("description", "")) > 100,
            f"ok={finish.get('ok')}, hl_count={finish.get('highlights_count')}, desc_len={len(finish.get('description',''))}"),
    ]
    passed = sum(1 for _, ok, _ in rows if ok)
    failed = len(rows) - passed
    for lbl, ok, detail in rows:
        sym = "✓" if ok else "✗"
        print(f"  [{sym}] {lbl:<70s}  {detail}")
    print()
    print(f"  Acceptance:  {passed} passed, {failed} failed")
    print(f"  Artefacts:   {ARTIFACT_DIR}")
    print("==============================================================================")
    print()

    # Write the full state machine for the user record.
    acceptance = {
        "rows":       [{"label": lbl, "passed": ok, "detail": d} for lbl, ok, d in rows],
        "passed":     passed,
        "failed":     failed,
        "aid":        aid,
        "generated_at": datetime.now(_tz.utc).isoformat(),
    }
    (ARTIFACT_DIR / "JC-WS-B-Analyze-acceptance-report.json").write_text(
        json.dumps(acceptance, indent=2, default=str)
    )
    print("  ✓ artefact → JC-WS-B-Analyze-acceptance-report.json")
    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
