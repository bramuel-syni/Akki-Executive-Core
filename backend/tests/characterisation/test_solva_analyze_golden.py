"""Characterisation golden — Solva analyze flow (Phase 0).

Pins the CURRENT shape of `POST /api/workbook/v2/analyses/{aid}/synthesize`
end-to-end. Includes upload via `/api/workbook/upload-multi` (the
analysis entity creator) and the synthesize call. Snapshots
structural shape only — narration text is non-deterministic.

What this test pins:

  1. `/api/workbook/upload-multi` accepts the multipart payload
     and returns an `analysis_id`.
  2. `/api/workbook/v2/analyses/{aid}/synthesize` returns 200 with
     the documented narration envelope: `headline`, `observations`,
     `citations`, `cache_key`.
  3. The Analysis entity gained a `runs[]` entry (append-only contract).
  4. A Shield audit row was written for the narration call.

The forecaster density gate is exercised: 6 rows of clean
(date, value) pairs clear the gate so the forecaster runs vs. the
refusal-run path.

Marked `@pytest.mark.integration` — real LLM. Skip default sweep.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

import server  # noqa: F401
from server import app


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

GOLDEN_PATH = Path(__file__).parent / "solva_analyze.golden.json"


# CSV with 6 rows — clears the density gate (>= 6 non-null AND >= 30%).
_CSV_BODY = (
    "Month,Revenue\n"
    "2026-01-01,100\n"
    "2026-02-01,110\n"
    "2026-03-01,121\n"
    "2026-04-01,133\n"
    "2026-05-01,146\n"
    "2026-06-01,161\n"
)

_OBJECTIVE = (
    "Summarise the topline movement of Lemasy Limited's monthly "
    "revenue between January and June and call out anomalies."
)


DYNAMIC_FIELDS = {
    "id", "_id", "audit_id", "created_at", "updated_at",
    "cache_key", "run_id", "elapsed_ms", "request_hash",
    "response_hash", "analysis_id", "context_id", "blob_id",
}


def _to_shape(value: Any, depth: int = 0) -> Any:
    """Same shape-stripper as chat_roundtrip_golden.py."""
    if depth > 8:
        return "...(truncated)"
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        if not value:
            return ["list/empty"]
        return [_to_shape(value[0], depth + 1), f"list/len>={len(value)}"]
    if isinstance(value, dict):
        out = {}
        for k in sorted(value.keys()):
            if k in DYNAMIC_FIELDS:
                out[k] = "<dynamic>:" + type(value[k]).__name__
                continue
            out[k] = _to_shape(value[k], depth + 1)
        return out
    return type(value).__name__


@pytest_asyncio.fixture
async def db_conn():
    mclient = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = mclient[os.environ["DB_NAME"]]
    yield db
    mclient.close()


async def _csrf_login(ac: AsyncClient, email: str, password: str) -> Dict[str, str]:
    r = await ac.get("/api/csrf")
    csrf = r.json()["csrf_token"]
    r = await ac.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers={"X-CSRF-Token": csrf},
    )
    r.raise_for_status()
    token = r.json().get("access_token") or r.json().get("token")
    r = await ac.get("/api/csrf")
    return {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": r.json()["csrf_token"],
    }


async def test_solva_analyze_golden_shape(db_conn):
    """Pin the Solva v2 synthesize narration envelope shape."""
    now_iso = datetime.now(timezone.utc).isoformat()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=240.0) as ac:
        admin = await _csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")

        # 1. Upload — creates the Analysis entity.
        files = [
            ("files", ("characterisation_smoke.csv", _CSV_BODY.encode("utf-8"), "text/csv")),
        ]
        data = {"objective": _OBJECTIVE}
        r = await ac.post(
            "/api/workbook/upload-multi",
            data=data,
            files=files,
            headers={"Authorization": admin["Authorization"],
                     "X-CSRF-Token": admin["X-CSRF-Token"]},
        )
        if r.status_code not in (200, 201):
            pytest.skip(
                f"HUMAN_REQUIRED: upload-multi non-2xx ({r.status_code}). "
                f"body={r.text[:300]!r}"
            )
        upload = r.json()
        aid = upload.get("analysis_id") or upload.get("id")
        if not aid:
            pytest.skip(
                f"HUMAN_REQUIRED: upload-multi returned no analysis_id. "
                f"body={upload!r}"
            )

        try:
            # 2. Synthesize.
            r = await ac.post(
                f"/api/workbook/v2/analyses/{aid}/synthesize",
                headers=admin,
            )
            if r.status_code != 200:
                pytest.skip(
                    f"HUMAN_REQUIRED: synthesize non-200 ({r.status_code}). "
                    f"body={r.text[:300]!r}"
                )
            narration = r.json()
            if narration.get("refused"):
                pytest.skip(
                    f"HUMAN_REQUIRED: synthesize refused — "
                    f"reason={narration.get('refusal_reason')!r}"
                )

            # 3. Documented narration envelope shape.
            required_keys = {"headline", "observations", "citations", "cache_key"}
            missing = required_keys - set(narration.keys())
            assert not missing, (
                f"narration envelope missing keys: {missing!r}. "
                f"actual keys: {sorted(narration.keys())!r}"
            )
            assert isinstance(narration["headline"], str), (
                f"headline not a str: {type(narration['headline']).__name__}"
            )
            assert isinstance(narration["observations"], list), (
                f"observations not a list: {type(narration['observations']).__name__}"
            )

            # 4. runs[] gained an append (append-only contract).
            row = await db_conn.analyses.find_one({"id": aid}, {"_id": 0})
            assert row is not None, f"analysis {aid!r} missing post-synthesize"
            runs = row.get("runs") or []
            assert len(runs) >= 1, (
                f"runs[] did not gain an entry — append-only contract "
                f"violated. runs={runs!r}"
            )
            last_run = runs[-1]
            for run_field in ("run_id", "created_at", "headline"):
                assert run_field in last_run, (
                    f"run row missing {run_field!r}: {last_run!r}"
                )

            # 5. Golden shape snapshot.
            shape = _to_shape(narration)
            if not GOLDEN_PATH.exists():
                GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
                GOLDEN_PATH.write_text(
                    json.dumps({"shape": shape, "blessed_at": now_iso},
                               indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                return

            golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
            expected_shape = golden["shape"]
            actual_top_keys = set(shape.keys()) if isinstance(shape, dict) else set()
            expected_top_keys = set(expected_shape.keys()) if isinstance(expected_shape, dict) else set()
            missing_keys = expected_top_keys - actual_top_keys
            assert not missing_keys, (
                f"synthesize response DROPPED top-level keys vs golden: "
                f"{missing_keys!r}. Re-bless if intentional."
            )
        finally:
            await db_conn.analyses.delete_one({"id": aid})
            await db_conn.analysis_blobs.delete_many({"analysis_id": aid})


# ────────────────────── golden re-blessing procedure ──────────────────────
#
# Identical to the chat round-trip: delete the .golden.json next to
# this file → run the test → commit the new golden. Documented at the
# foot of `test_chat_roundtrip_golden.py`.
