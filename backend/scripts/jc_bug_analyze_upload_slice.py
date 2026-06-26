"""JC-WS · BUG-ANL-UPLOAD-GRIDFS — Phase 3 proving slice.

Source of truth: `/app/memory/JC_WS_CANONICAL_SPEC.md` (Analyze
submodule under JC-WS; the storage-backend swap honours the spec
rule "Reuse the existing engines — do not rebuild" by changing
ONLY the persistence backend under the workbook_analyzer).

Design memo: `/app/memory/jc_artifacts/bugs/analyze_upload_20260626.md`
(Section 9 · Proving slice scope — 10 acceptance rows A–J).

USER REINFORCEMENTS (2026-06-26):
  • Keep multi-file row F in the slice (Analyze drawer surface).
  • Run all 5 regression checks downstream (slice is the upload
    proof; regression is the locked invariants check that ships
    alongside this slice's GREEN report).

10 acceptance rows:

  Row  Subject                                                Expected
  ───  ───────────────────────────────────────────────────────────────
   A   5 MB CSV `/upload`                                     200, GridFS-backed
   A2  1 MB synthetic XLSX `/upload`                          200, GridFS-backed (regression on xlsx)
   B   50 MB CSV `/upload`                                    200 (the band that broke pre-migration)
   C   250 MB CSV `/upload`                                   200 (user's stated minimum)
   D   500 MB CSV `/upload`                                   200 (ceiling)
   E   600 MB CSV `/upload`                                   413 clean rejection
   F   Multi-file `/upload-multi` (two ~250 MB CSVs)          200; each blob GridFS-backed
   G   Round-trip 10 MB blob: write → read_workbook_bytes     byte-identical
   H   Legacy inline `data_b64` row → read_workbook_bytes     byte-identical (dual-read confirmed)
   I   Backfill: 2 inline + 1 GridFS row → --commit → idemp.  all GridFS; rerun = no-op
   J   Lifecycle delete: GridFS chunks + metadata gone        no orphan fs.chunks rows

Memory peak observation (load-bearing safety property):
  Track RSS before and after the 500 MB upload (Row D). Target
  peak delta ≤ ~250 MB (Motor streaming + openpyxl row-iter), NOT
  the old ~1.2 GB inline-base64 peak.

Run from the repo root:
    cd /app/backend && python scripts/jc_bug_analyze_upload_slice.py

Artefacts → `/app/memory/jc_artifacts/bugs/analyze_upload_slice_evidence/`
(JSON summary + memory observation + per-row outcomes).
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import shutil
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")

import psutil  # noqa: E402
from bson import ObjectId  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from starlette.datastructures import UploadFile as StarletteUploadFile  # noqa: E402

from core import db  # noqa: E402
from routers.workbook_analysis import (  # noqa: E402
    upload_workbook,
    upload_workbook_multi,
)
from services.analysis_lifecycle import (  # noqa: E402
    delete_gridfs_file,
    download_to_tempfile,
    read_workbook_bytes,
    session_close,
    upload_to_gridfs,
)
import openpyxl  # noqa: E402


ART_DIR = Path("/app/memory/jc_artifacts/bugs/analyze_upload_slice_evidence")
ART_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR = Path(tempfile.mkdtemp(prefix="jc_anl_slice_"))

MB = 1024 * 1024


# ──────────────────────────────────────────────────────────────────
# File generators (high-throughput, low-RAM).
# ──────────────────────────────────────────────────────────────────


def gen_csv(path: Path, target_bytes: int) -> int:
    """Generate a CSV file ≥ target_bytes. Chunked block writes:
    build one 4 KB line block once, write enough times to clear the
    target. Returns actual file size on disk."""
    header = b"row_idx,col_b,col_c,col_d,col_e\n"
    # 35-byte deterministic row. 128 rows ≈ 4.5 KB block.
    block_rows = 128
    block = b"".join(
        f"{i},val_b_{i:08d},val_c_{i:08d},val_d_{i:08d},val_e_{i:08d}\n".encode()
        for i in range(block_rows)
    )
    block_size = len(block)
    n_blocks = (target_bytes - len(header)) // block_size + 1
    with open(path, "wb") as f:
        f.write(header)
        for _ in range(n_blocks):
            f.write(block)
    return path.stat().st_size


def gen_xlsx(path: Path, n_rows: int = 1000) -> int:
    """Generate a small synthetic XLSX file via openpyxl (used only
    for the row-A2 xlsx regression check; large XLSX is impractical
    via openpyxl due to write-side compression overhead — large files
    are exercised via CSV which has identical handler behaviour)."""
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet(title="Sheet1")
    ws.append(["Month", "Revenue", "Cost", "Net"])
    for i in range(n_rows):
        ws.append([f"2024-{(i % 12) + 1:02d}", 1000 + i, 600 + i, 400 + i // 2])
    wb.save(str(path))
    return path.stat().st_size


# ──────────────────────────────────────────────────────────────────
# Mocked starlette UploadFile (size-aware, file-backed).
# ──────────────────────────────────────────────────────────────────


def make_upload_file(path: Path) -> StarletteUploadFile:
    """Wrap a local file path as an UploadFile so router handlers
    accept it. We pass an open binary file as `file=` and the actual
    size on disk as `size=` (mirrors what FastAPI sets from
    content-length)."""
    fp = open(path, "rb")
    size = os.fstat(fp.fileno()).st_size
    # Starlette ≥ 0.27 accepts (file, *, size, filename, headers).
    return StarletteUploadFile(
        file=fp, size=size, filename=path.name,
    )


# ──────────────────────────────────────────────────────────────────
# Fixtures.
# ──────────────────────────────────────────────────────────────────


async def _resolve_fixture_account_and_context() -> Tuple[Dict[str, Any], str]:
    """Find a real account + context to scope writes under. Prefers
    the admin account in the seed data; falls back to any existing
    account if not present. Returns (account_row, context_id)."""
    candidates: List[Dict[str, Any]] = []
    async for row in db.accounts.find(
        {"email": {"$in": ["admin@akki.ai", "admin@mara-heritage.test"]}},
        {"_id": 0}, limit=2,
    ):
        candidates.append(row)
    if not candidates:
        async for row in db.accounts.find({}, {"_id": 0}, limit=1):
            candidates.append(row)
    if not candidates:
        raise RuntimeError("no accounts in DB — cannot mint slice fixture")
    acct = candidates[0]

    # Pick the account's first context (membership row).
    mem = await db.memberships.find_one(
        {"account_id": acct["id"], "status": "active"}, {"_id": 0},
    )
    if not mem:
        # Fallback: any context the account ever touched.
        ctx_row = await db.contexts.find_one({}, {"_id": 0})
        if not ctx_row:
            raise RuntimeError("no contexts in DB — cannot scope slice writes")
        return acct, ctx_row["id"]
    return acct, mem["context_id"]


# ──────────────────────────────────────────────────────────────────
# Row runners.
# ──────────────────────────────────────────────────────────────────


def rss_mb() -> float:
    """Current process RSS in MB."""
    return psutil.Process(os.getpid()).memory_info().rss / MB


async def _verify_gridfs_backed(analysis_id: str, *, collection: str) -> Dict[str, Any]:
    """Verify the inserted blob row carries `gridfs_id` and NOT
    `data_b64`. Returns observation dict for the evidence file."""
    if collection == "workbook_blobs":
        row = await db.workbook_blobs.find_one({"analysis_id": analysis_id}, {"_id": 0})
    else:
        row = await db.analysis_blobs.find_one({"analysis_id": analysis_id}, {"_id": 0})
    if not row:
        return {"ok": False, "reason": "blob_row_missing"}
    has_gridfs = bool(row.get("gridfs_id"))
    has_legacy = bool(row.get("data_b64"))
    return {
        "ok":         has_gridfs and not has_legacy,
        "gridfs_id":  row.get("gridfs_id"),
        "has_data_b64": has_legacy,
    }


async def row_a_5mb_csv(account: Dict[str, Any]) -> Dict[str, Any]:
    """Row A — 5 MB CSV via /upload."""
    path = TMP_DIR / "row_a_5mb.csv"
    size = gen_csv(path, 5 * MB)
    rss_before = rss_mb()
    uf = make_upload_file(path)
    try:
        resp = await upload_workbook(file=uf, current=account)
    finally:
        uf.file.close()
    rss_after = rss_mb()
    aid = resp["id"]
    verify = await _verify_gridfs_backed(aid, collection="workbook_blobs")
    return {
        "row": "A", "subject": "5 MB CSV via /upload",
        "file_size_bytes": size,
        "rss_mb_delta": round(rss_after - rss_before, 2),
        "rss_mb_peak": round(rss_after, 2),
        "analysis_id": aid,
        "status": resp.get("status"),
        "verify": verify,
        "PASS": resp.get("status") == "parsed" and verify["ok"],
    }


async def row_a2_xlsx(account: Dict[str, Any]) -> Dict[str, Any]:
    """Row A2 — Small XLSX via /upload (xlsx-format regression)."""
    path = TMP_DIR / "row_a2_xlsx.xlsx"
    size = gen_xlsx(path, n_rows=10_000)
    rss_before = rss_mb()
    uf = make_upload_file(path)
    try:
        resp = await upload_workbook(file=uf, current=account)
    finally:
        uf.file.close()
    rss_after = rss_mb()
    aid = resp["id"]
    verify = await _verify_gridfs_backed(aid, collection="workbook_blobs")
    return {
        "row": "A2", "subject": "Synthetic XLSX via /upload",
        "file_size_bytes": size,
        "rss_mb_delta": round(rss_after - rss_before, 2),
        "rss_mb_peak": round(rss_after, 2),
        "analysis_id": aid,
        "status": resp.get("status"),
        "verify": verify,
        "PASS": resp.get("status") == "parsed" and verify["ok"],
    }


async def row_b_50mb_csv(account: Dict[str, Any]) -> Dict[str, Any]:
    path = TMP_DIR / "row_b_50mb.csv"
    size = gen_csv(path, 50 * MB)
    rss_before = rss_mb()
    uf = make_upload_file(path)
    try:
        resp = await upload_workbook(file=uf, current=account)
    finally:
        uf.file.close()
    rss_after = rss_mb()
    aid = resp["id"]
    verify = await _verify_gridfs_backed(aid, collection="workbook_blobs")
    return {
        "row": "B", "subject": "50 MB CSV via /upload",
        "file_size_bytes": size,
        "rss_mb_delta": round(rss_after - rss_before, 2),
        "rss_mb_peak": round(rss_after, 2),
        "analysis_id": aid,
        "status": resp.get("status"),
        "verify": verify,
        "PASS": resp.get("status") == "parsed" and verify["ok"],
    }


async def row_c_250mb_csv(account: Dict[str, Any]) -> Dict[str, Any]:
    path = TMP_DIR / "row_c_250mb.csv"
    size = gen_csv(path, 250 * MB)
    rss_before = rss_mb()
    uf = make_upload_file(path)
    try:
        resp = await upload_workbook(file=uf, current=account)
    finally:
        uf.file.close()
    rss_after = rss_mb()
    aid = resp["id"]
    verify = await _verify_gridfs_backed(aid, collection="workbook_blobs")
    return {
        "row": "C", "subject": "250 MB CSV via /upload",
        "file_size_bytes": size,
        "rss_mb_delta": round(rss_after - rss_before, 2),
        "rss_mb_peak": round(rss_after, 2),
        "analysis_id": aid,
        "status": resp.get("status"),
        "verify": verify,
        "PASS": resp.get("status") == "parsed" and verify["ok"],
    }


async def row_d_500mb_csv(account: Dict[str, Any]) -> Dict[str, Any]:
    """Row D — 500 MB CSV (ceiling). Memory peak observation lives
    here (the load-bearing safety property)."""
    path = TMP_DIR / "row_d_500mb.csv"
    # Target ~498 MB so we're safely under MAX_BYTES (500 MB exact).
    size = gen_csv(path, 498 * MB)
    rss_before = rss_mb()
    rss_peak = rss_before

    async def _track_peak():
        nonlocal rss_peak
        while True:
            v = rss_mb()
            if v > rss_peak:
                rss_peak = v
            await asyncio.sleep(0.1)

    tracker = asyncio.create_task(_track_peak())
    try:
        uf = make_upload_file(path)
        try:
            resp = await upload_workbook(file=uf, current=account)
        finally:
            uf.file.close()
    finally:
        tracker.cancel()
        try:
            await tracker
        except asyncio.CancelledError:
            pass
    rss_after = rss_mb()
    aid = resp["id"]
    verify = await _verify_gridfs_backed(aid, collection="workbook_blobs")
    return {
        "row": "D", "subject": "500 MB CSV via /upload (ceiling)",
        "file_size_bytes": size,
        "rss_mb_before": round(rss_before, 2),
        "rss_mb_peak":   round(rss_peak, 2),
        "rss_mb_after":  round(rss_after, 2),
        "rss_mb_delta":  round(rss_peak - rss_before, 2),
        "analysis_id":   aid,
        "status":        resp.get("status"),
        "verify":        verify,
        "PASS": resp.get("status") == "parsed" and verify["ok"],
    }


async def row_e_600mb_csv(account: Dict[str, Any]) -> Dict[str, Any]:
    """Row E — 600 MB CSV → expect 413 clean rejection."""
    path = TMP_DIR / "row_e_600mb.csv"
    size = gen_csv(path, 600 * MB)
    uf = make_upload_file(path)
    raised = None
    try:
        await upload_workbook(file=uf, current=account)
    except HTTPException as e:
        raised = e
    finally:
        uf.file.close()
    is_413 = raised is not None and raised.status_code == 413
    has_clean_msg = (
        raised is not None
        and "workbook_over_500mb_ceiling" in str(raised.detail)
        and ".csv" in str(raised.detail).lower()
    )
    return {
        "row": "E", "subject": "600 MB CSV via /upload (over-ceiling)",
        "file_size_bytes": size,
        "status_code": raised.status_code if raised else None,
        "detail": str(raised.detail) if raised else None,
        "PASS": is_413 and has_clean_msg,
    }


async def row_f_multi_two_250mb(account: Dict[str, Any], context_id: str) -> Dict[str, Any]:
    """Row F — multi-file upload of two ~250 MB CSVs."""
    p1 = TMP_DIR / "row_f_first.csv"
    p2 = TMP_DIR / "row_f_second.csv"
    s1 = gen_csv(p1, 250 * MB)
    s2 = gen_csv(p2, 250 * MB)
    rss_before = rss_mb()
    uf1 = make_upload_file(p1)
    uf2 = make_upload_file(p2)
    try:
        resp = await upload_workbook_multi(
            files=[uf1, uf2],
            title="row_f_multi",
            context_id=context_id,
            objective="row F multi-file proof",
            current=account,
        )
    finally:
        uf1.file.close()
        uf2.file.close()
    rss_after = rss_mb()
    aid = resp["id"]
    blob_rows = await db.analysis_blobs.find(
        {"analysis_id": aid}, {"_id": 0, "gridfs_id": 1, "data_b64": 1, "filename": 1},
    ).to_list(length=None)
    all_gridfs = all(bool(b.get("gridfs_id")) for b in blob_rows)
    no_legacy = all(not bool(b.get("data_b64")) for b in blob_rows)
    return {
        "row": "F", "subject": "Multi-file 2× ~250 MB CSVs via /upload-multi",
        "file_sizes": [s1, s2],
        "rss_mb_delta": round(rss_after - rss_before, 2),
        "analysis_id": aid,
        "n_sources": len(resp.get("sources") or []),
        "n_blob_rows": len(blob_rows),
        "all_gridfs_backed": all_gridfs,
        "no_legacy_data_b64": no_legacy,
        "PASS": len(blob_rows) == 2 and all_gridfs and no_legacy,
    }


async def row_g_round_trip(account: Dict[str, Any]) -> Dict[str, Any]:
    """Row G — round-trip byte-equality on a 10 MB synthetic payload
    through GridFS write → read_workbook_bytes → byte-equality."""
    payload = os.urandom(10 * MB)
    src_path = TMP_DIR / "row_g_payload.bin"
    with open(src_path, "wb") as f:
        f.write(payload)
    with open(src_path, "rb") as f:
        gridfs_id = await upload_to_gridfs(
            db, source=f, filename="row_g_payload.bin",
            metadata={
                "kind": "workbook_blob",
                "account_id": account["id"],
                "filename": "row_g_payload.bin",
                "file_format": "bin",
                "analysis_id": "ana-row-g-synthetic",
            },
        )
    # Read back via the dual-read helper.
    blob_row = {"gridfs_id": gridfs_id, "filename": "row_g_payload.bin", "file_format": "bin"}
    inline_bytes, tmp_path = await read_workbook_bytes(db, blob_row)
    try:
        if tmp_path:
            with open(tmp_path, "rb") as f:
                round_trip = f.read()
        else:
            round_trip = inline_bytes or b""
    finally:
        if tmp_path:
            os.unlink(tmp_path)
    byte_equal = (round_trip == payload)
    await delete_gridfs_file(db, gridfs_id)
    return {
        "row": "G", "subject": "Round-trip byte-equality on 10 MB blob",
        "payload_bytes": len(payload),
        "roundtrip_bytes": len(round_trip),
        "byte_equal": byte_equal,
        "PASS": byte_equal,
    }


async def row_h_legacy_dual_read(account: Dict[str, Any]) -> Dict[str, Any]:
    """Row H — Synthesize a legacy `data_b64` row and prove the
    dual-read helper returns identical bytes."""
    payload = b"abc,def\n" + os.urandom(2 * MB)
    b64 = base64.b64encode(payload).decode("ascii")
    legacy_row = {
        "analysis_id":  "ana-row-h-legacy",
        "source_id":    "src-row-h",
        "account_id":   account["id"],
        "filename":     "row_h_legacy.csv",
        "file_format":  "csv",
        "data_b64":     b64,
        "created_at":   datetime.now(timezone.utc).isoformat(),
    }
    inline_bytes, tmp_path = await read_workbook_bytes(db, legacy_row)
    same = (inline_bytes == payload) and (tmp_path is None)
    return {
        "row": "H", "subject": "Legacy inline data_b64 row → dual-read",
        "payload_bytes": len(payload),
        "decoded_bytes": len(inline_bytes or b""),
        "tmp_path_used": tmp_path is not None,
        "byte_equal":   same,
        "PASS":         same,
    }


async def row_i_backfill(account: Dict[str, Any]) -> Dict[str, Any]:
    """Row I — seed 2 inline rows + 1 GridFS row in a sandboxed
    test collection, run the backfill script with --commit, verify
    all 3 end up as GridFS rows. Rerun = no-op."""
    # Use a sandboxed analysis_id so we don't touch production data.
    sandbox_aid = "ana-row-i-" + uuid.uuid4().hex[:8]
    # Seed 2 inline rows.
    payload1 = b"col_a,col_b\n1,2\n3,4\n" + os.urandom(1 * MB)
    payload2 = b"col_x,col_y\n5,6\n7,8\n" + os.urandom(1 * MB)
    inline_rows = [
        {
            "analysis_id":  sandbox_aid,
            "source_id":    "src-i-1",
            "account_id":   account["id"],
            "context_id":   "ctx-row-i",
            "filename":     "row_i_legacy_1.csv",
            "file_format":  "csv",
            "data_b64":     base64.b64encode(payload1).decode("ascii"),
            "created_at":   datetime.now(timezone.utc).isoformat(),
        },
        {
            "analysis_id":  sandbox_aid,
            "source_id":    "src-i-2",
            "account_id":   account["id"],
            "context_id":   "ctx-row-i",
            "filename":     "row_i_legacy_2.csv",
            "file_format":  "csv",
            "data_b64":     base64.b64encode(payload2).decode("ascii"),
            "created_at":   datetime.now(timezone.utc).isoformat(),
        },
    ]
    # Seed 1 GridFS row.
    payload3 = b"col_p,col_q\n9,10\n" + os.urandom(1 * MB)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as t:
        t.write(payload3)
        t_path = t.name
    try:
        with open(t_path, "rb") as f:
            gridfs_id3 = await upload_to_gridfs(
                db, source=f, filename="row_i_gridfs.csv",
                metadata={"kind": "analysis_blob", "analysis_id": sandbox_aid,
                          "account_id": account["id"], "filename": "row_i_gridfs.csv",
                          "file_format": "csv"},
            )
    finally:
        os.unlink(t_path)
    gridfs_row = {
        "analysis_id":  sandbox_aid,
        "source_id":    "src-i-3",
        "account_id":   account["id"],
        "context_id":   "ctx-row-i",
        "filename":     "row_i_gridfs.csv",
        "file_format":  "csv",
        "gridfs_id":    gridfs_id3,
        "created_at":   datetime.now(timezone.utc).isoformat(),
    }
    await db.analysis_blobs.insert_many(inline_rows + [gridfs_row])

    # Invoke the backfill script with --commit on this sandbox aid.
    from scripts.jc_bug_analyze_upload_backfill import migrate_collection
    summary_first = await migrate_collection(
        collection="analysis_blobs", commit=True, only_analysis_id=sandbox_aid,
    )
    # Rerun → should be no-op.
    summary_second = await migrate_collection(
        collection="analysis_blobs", commit=True, only_analysis_id=sandbox_aid,
    )

    # Verify all 3 rows now have gridfs_id and no data_b64.
    after_rows = await db.analysis_blobs.find(
        {"analysis_id": sandbox_aid}, {"_id": 0},
    ).to_list(length=None)
    all_gridfs = all(bool(r.get("gridfs_id")) for r in after_rows)
    no_inline = all(not r.get("data_b64") for r in after_rows)

    # Cleanup the sandbox.
    cleanup_gridfs_ids = [r["gridfs_id"] for r in after_rows if r.get("gridfs_id")]
    for fid in cleanup_gridfs_ids:
        await delete_gridfs_file(db, fid)
    await db.analysis_blobs.delete_many({"analysis_id": sandbox_aid})

    return {
        "row": "I", "subject": "Backfill: 2 inline + 1 GridFS → all GridFS; rerun no-op",
        "first_run":    summary_first,
        "second_run":   summary_second,
        "n_rows_after": len(after_rows),
        "all_gridfs":   all_gridfs,
        "no_data_b64":  no_inline,
        "second_was_noop": summary_second.get("migrated") == 0,
        "PASS": (
            len(after_rows) == 3
            and all_gridfs and no_inline
            and summary_first.get("migrated") == 2
            and summary_second.get("migrated") == 0
        ),
    }


async def row_j_lifecycle_delete(account: Dict[str, Any], context_id: str) -> Dict[str, Any]:
    """Row J — full lifecycle: upload multi → session_close →
    verify both `analysis_blobs` rows AND `fs.chunks` rows are
    gone (no orphans)."""
    p1 = TMP_DIR / "row_j_lifecycle.csv"
    gen_csv(p1, 3 * MB)
    uf = make_upload_file(p1)
    try:
        resp = await upload_workbook_multi(
            files=[uf], title="row_j_lifecycle",
            context_id=context_id, objective="row J lifecycle",
            current=account,
        )
    finally:
        uf.file.close()
    aid = resp["id"]
    # Capture the gridfs_ids before close.
    blobs_before = await db.analysis_blobs.find(
        {"analysis_id": aid}, {"_id": 0, "gridfs_id": 1},
    ).to_list(length=None)
    gridfs_ids = [b["gridfs_id"] for b in blobs_before if b.get("gridfs_id")]

    # Run session_close.
    closed = await session_close(
        db, analysis_id=aid, account_id=account["id"], context_id=context_id,
    )

    # Verify metadata rows gone.
    blobs_after = await db.analysis_blobs.find(
        {"analysis_id": aid}, {"_id": 0},
    ).to_list(length=None)
    # Verify fs.chunks gone for each gridfs_id.
    chunks_left = 0
    files_left = 0
    for fid in gridfs_ids:
        chunks = await db["fs.chunks"].count_documents({"files_id": ObjectId(fid)})
        files = await db["fs.files"].count_documents({"_id": ObjectId(fid)})
        chunks_left += chunks
        files_left += files

    # Cleanup the parent analyses row.
    await db.analyses.delete_one({"id": aid})

    return {
        "row": "J", "subject": "Lifecycle delete → no orphan fs.chunks",
        "analysis_id":      aid,
        "gridfs_ids_seen":  gridfs_ids,
        "metadata_rows_after_close": len(blobs_after),
        "fs_chunks_left":   chunks_left,
        "fs_files_left":    files_left,
        "session_close_returned_purged": (closed or {}).get("status") == "purged",
        "PASS": (
            len(blobs_after) == 0
            and chunks_left == 0
            and files_left == 0
            and (closed or {}).get("status") == "purged"
        ),
    }


# ──────────────────────────────────────────────────────────────────
# Cleanup created analyses (best-effort).
# ──────────────────────────────────────────────────────────────────


async def _cleanup_test_analyses(account_id: str, ids: List[str]) -> None:
    """Drop the test-created workbook_analyses, workbook_blobs +
    associated GridFS files. Best-effort — failures swallowed so a
    cleanup hiccup doesn't fail an otherwise green slice."""
    for aid in ids:
        try:
            blob = await db.workbook_blobs.find_one({"analysis_id": aid}, {"_id": 0})
            if blob and blob.get("gridfs_id"):
                await delete_gridfs_file(db, blob["gridfs_id"])
            await db.workbook_blobs.delete_many({"analysis_id": aid})
            await db.workbook_analyses.delete_many({"id": aid, "account_id": account_id})
        except Exception:  # noqa: BLE001
            pass


# ──────────────────────────────────────────────────────────────────
# Main entrypoint.
# ──────────────────────────────────────────────────────────────────


async def main():
    print("=" * 70)
    print("JC-WS · BUG-ANL-UPLOAD-GRIDFS — Phase 3 proving slice")
    print("=" * 70)
    print(f"Tempdir: {TMP_DIR}")
    print(f"Artefacts → {ART_DIR}")
    print()

    t0 = time.time()
    account, context_id = await _resolve_fixture_account_and_context()
    # Patch the active_context_id field that handlers read.
    account = dict(account)
    account.setdefault("active_context_id", context_id)
    print(f"Fixture account: {account.get('email')} ({account['id'][:8]}…)")
    print(f"Fixture context: {context_id[:8]}…")
    print()

    results: List[Dict[str, Any]] = []
    created_analysis_ids: List[str] = []

    rows = [
        ("A",  row_a_5mb_csv,        {"account": account}),
        ("A2", row_a2_xlsx,          {"account": account}),
        ("B",  row_b_50mb_csv,       {"account": account}),
        ("C",  row_c_250mb_csv,      {"account": account}),
        ("D",  row_d_500mb_csv,      {"account": account}),
        ("E",  row_e_600mb_csv,      {"account": account}),
        ("F",  row_f_multi_two_250mb,{"account": account, "context_id": context_id}),
        ("G",  row_g_round_trip,     {"account": account}),
        ("H",  row_h_legacy_dual_read, {"account": account}),
        ("I",  row_i_backfill,       {"account": account}),
        ("J",  row_j_lifecycle_delete, {"account": account, "context_id": context_id}),
    ]
    for tag, fn, kwargs in rows:
        print(f"--- Row {tag} ---")
        t_row = time.time()
        try:
            res = await fn(**kwargs)
        except Exception as exc:  # noqa: BLE001
            res = {
                "row": tag, "subject": fn.__doc__ or "",
                "exception": f"{type(exc).__name__}: {exc!s:.300}",
                "PASS": False,
            }
        res["elapsed_s"] = round(time.time() - t_row, 2)
        results.append(res)
        if res.get("analysis_id"):
            created_analysis_ids.append(res["analysis_id"])
        verdict = "✓ PASS" if res.get("PASS") else "✗ FAIL"
        print(f"  {verdict} ({res['elapsed_s']}s)")
        print(f"  {json.dumps({k: v for k, v in res.items() if k != 'PASS'}, default=str, indent=2)[:400]}")
        print()

    # Cleanup transient test data.
    await _cleanup_test_analyses(account["id"], created_analysis_ids)
    shutil.rmtree(TMP_DIR, ignore_errors=True)

    n_pass = sum(1 for r in results if r.get("PASS"))
    n_total = len(results)
    print("=" * 70)
    print(f"RESULT: {n_pass}/{n_total} GREEN")
    print(f"Total elapsed: {round(time.time() - t0, 1)}s")
    print("=" * 70)

    out_path = ART_DIR / f"slice_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    summary = {
        "ran_at":     datetime.now(timezone.utc).isoformat(),
        "n_pass":     n_pass,
        "n_total":    n_total,
        "all_green":  n_pass == n_total,
        "results":    results,
    }
    out_path.write_text(json.dumps(summary, default=str, indent=2))
    print(f"Evidence written → {out_path}")

    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    rc = asyncio.run(main())
    sys.exit(rc)
