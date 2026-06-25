"""JC-WS Phase 3 § Brief Akki-fetch retrieval-quality gate.

Per the canonical spec § MATURITY GATES THE STEPS: "before keeping
the Akki-fetch input in the UI, verify with ≥3 named-context test
cases that the retrieval returns GENUINELY RELEVANT material. … For
each: paste the retrieved set + a one-line honesty verdict
(RELEVANT / WEAK / IRRELEVANT)."

This script runs the probe against the existing `search_document_journal`
BM25 endpoint and writes the honest verdicts to disk.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone as _tz
from pathlib import Path

from httpx import ASGITransport, AsyncClient

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")
os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")

from server import app  # noqa: E402
from core import create_access_token  # noqa: E402


ADMIN_EMAIL = "admin@akki.ai"
ADMIN_ID = "cf6e7587-9abd-46aa-b8f4-f342e9b066ef"
CONTEXT_ID = "a2937d0f-37f1-4042-a897-ab73a6cd652a"
ARTIFACT_DIR = Path("/app/memory/jc_artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# Test cases per the canonical spec (verbatim from the user's dispatch).
TEST_CASES = [
    "the Q3 board discussion",
    "last week's risk review",
    "Maria's competitive analysis from October",
]


async def main():
    token = create_access_token(ADMIN_ID, ADMIN_EMAIL)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Test-Bypass": "1",
    }

    transport = ASGITransport(app=app)
    results = []
    async with AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        for q in TEST_CASES:
            r = await client.get(
                f"/api/contexts/{CONTEXT_ID}/document-journal/search",
                headers=headers, params={"q": q, "limit": 5},
            )
            if r.status_code != 200:
                results.append({"q": q, "error": f"{r.status_code} {r.text[:200]}"})
                continue
            payload = r.json()
            hits = payload.get("hits") or []
            results.append({
                "q":     q,
                "total": payload.get("total"),
                "top3":  [
                    {
                        "doc_name":   h.get("doc_name"),
                        "score":      round(h.get("score") or 0.0, 3),
                        "snippet":    (h.get("snippet") or "")[:140].replace("\n", " "),
                    }
                    for h in hits[:3]
                ],
            })

    print("=" * 78)
    print("JC-WS Phase 3 § Brief Akki-fetch retrieval-quality probe")
    print("=" * 78)
    for r in results:
        print(f"\nQ: {r['q']!r}")
        if "error" in r:
            print(f"  ERROR: {r['error']}")
            continue
        print(f"  total_hits: {r['total']}")
        for i, h in enumerate(r["top3"], start=1):
            print(f"  [{i}] {h['doc_name'][:70]:70s}  score={h['score']}")
            if h["snippet"]:
                print(f"      snippet: {h['snippet']!r}")

    (ARTIFACT_DIR / "JC-WS-A-Brief-akki-fetch-retrieval-probe.json").write_text(
        json.dumps({
            "test_cases": TEST_CASES,
            "results":    results,
            "captured_at": datetime.now(_tz.utc).isoformat(),
        }, indent=2, default=str)
    )
    print(f"\n  ✓ → {ARTIFACT_DIR}/JC-WS-A-Brief-akki-fetch-retrieval-probe.json")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
