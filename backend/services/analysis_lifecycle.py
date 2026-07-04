"""Track A Phase 1 (2026-06-03) — Analysis lifecycle service.

Helpers for the new `Analysis` entity (see `models.analysis`).
Phase 1 covers:
  • Create an Analysis row from a multi-file upload payload.
  • Session-close hook: delete blobs in `analysis_blobs`, mark the
    Analysis sources `blob_purged=True`, and append a
    "session-close" entry to `refresh_history`.

Phase 2 will add the read-side adapter for the UI; Phase 3 will
populate `observations[]` via Solva v2 narration; Phase 4 will
add the multi-version semantics. None of those land in Phase 1.

BUG-ANL-UPLOAD-GRIDFS (2026-06-26) — GridFS migration.
  • Upload path: NEW writes stream into the `fs` GridFS bucket via
    `upload_to_gridfs(...)`. The metadata row (`analysis_blobs` /
    `workbook_blobs`) carries `gridfs_id` instead of `data_b64`.
  • Read path: NEW helper `read_workbook_bytes(blob_row)` dual-reads —
    GridFS-first via `download_to_tempfile`, falls back to
    `data_b64` for LEGACY rows that pre-date the migration. Returns
    `(bytes, None)` for legacy inline blobs and `(None, path)` for
    GridFS-backed blobs. Caller passes the non-None side to
    `parse_workbook(blob=…)` or `parse_workbook(file_path=…)` and
    MUST `os.unlink` the tempfile when done.
  • Delete path: `delete_analysis_blobs(...)` deletes the GridFS
    chunks for any blob carrying `gridfs_id`, then removes the
    metadata rows. Idempotent on re-run.

Memory contract (load-bearing): the GridFS path never materialises
the full file in memory. Uploads stream FastAPI's
SpooledTemporaryFile straight into Motor's `upload_from_stream`
(255 KB chunks); reads stream chunks straight into a
NamedTemporaryFile on disk. Peak RAM at 500 MB upload ≈ a few MB
of Motor buffering, NOT the ~1.2 GB peak the inline-base64 path
required.
"""
from __future__ import annotations

import base64
import os
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from models.analysis import (
    Analysis,
    AnalysisRefreshEntry,
    AnalysisSource,
)


# ──────────────────────────────────────────────────────────────────
# GridFS bucket — singleton per process. Re-use the application's
# Motor client (`db.client`) so connection pooling is shared with
# the rest of the backend.
# ──────────────────────────────────────────────────────────────────
GRIDFS_BUCKET_NAME = "fs"
_BUCKET_CACHE: Dict[int, AsyncIOMotorGridFSBucket] = {}


def _bucket(db) -> AsyncIOMotorGridFSBucket:
    """Return a cached `AsyncIOMotorGridFSBucket` for the db. Tied to
    the db's id so a swap in tests (different db) builds a fresh
    bucket."""
    key = id(db)
    if key not in _BUCKET_CACHE:
        _BUCKET_CACHE[key] = AsyncIOMotorGridFSBucket(db, bucket_name=GRIDFS_BUCKET_NAME)
    return _BUCKET_CACHE[key]


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


# ──────────────────────────────────────────────────────────────────
# JC-WS · BUG-ANL-UPLOAD-GRIDFS (2026-06-26) — GridFS helpers.
# ──────────────────────────────────────────────────────────────────


async def upload_to_gridfs(db, *, source, filename: str, metadata: Dict[str, Any]) -> str:
    """Stream a file-like `source` into the GridFS bucket and return
    the file_id as a string.

    `source` MUST expose `.read(N)` — typically `UploadFile.file`
    (FastAPI's `SpooledTemporaryFile`) or any opened binary file.
    Motor reads the source in 255 KB chunks; the full payload is
    never held in memory.

    `metadata` is the document-level metadata copied onto `fs.files`
    (tenancy-scoped: account_id + context_id + kind + analysis_id
    + filename + file_format).
    """
    # Ensure the source is at position 0 — FastAPI sometimes leaves
    # the spooled file at EOF after content-length reads.
    try:
        source.seek(0)
    except Exception:  # noqa: BLE001 — best-effort; some sources are not seekable
        pass
    file_id = await _bucket(db).upload_from_stream(
        filename, source, metadata=dict(metadata or {}),
    )
    return str(file_id)


async def download_to_tempfile(db, file_id: str, *, suffix: str = ".gridfs") -> str:
    """Stream a GridFS file by id into a `NamedTemporaryFile`; return
    the absolute path. Caller MUST `os.unlink` the path when done.

    Memory contract: chunks stream to disk; peak RAM ≈ Motor buffer
    (a few hundred KB). Disk holds the full file.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        await _bucket(db).download_to_stream(ObjectId(file_id), tmp)
    finally:
        tmp.close()
    return tmp.name


async def delete_gridfs_file(db, file_id: str) -> bool:
    """Delete a GridFS file by id. Returns True on success, False on
    not-found (idempotent — caller can re-run safely)."""
    from gridfs.errors import NoFile
    try:
        await _bucket(db).delete(ObjectId(file_id))
        return True
    except NoFile:
        return False


async def read_workbook_bytes(db, blob_row: Dict[str, Any]) -> Tuple[Optional[bytes], Optional[str]]:
    """Dual-read for any inline-or-GridFS-stored workbook blob.

    Returns `(bytes, None)` for LEGACY rows carrying `data_b64`.
    Returns `(None, tempfile_path)` for GridFS-backed rows carrying
    `gridfs_id` — caller MUST `os.unlink(tempfile_path)` after use.

    Raises if the row carries neither field.

    Suffix selection: the tempfile created for GridFS reads carries
    the proper extension (`.xlsx` / `.csv` / `.bin`) so downstream
    consumers like openpyxl (which extension-checks before opening)
    accept the file. Falls back to `.gridfs` for unrecognised
    formats.
    """
    gridfs_id = blob_row.get("gridfs_id")
    if gridfs_id:
        fmt = (blob_row.get("file_format") or "").lower()
        suffix = {
            "xlsx": ".xlsx",
            "csv":  ".csv",
        }.get(fmt, ".gridfs")
        path = await download_to_tempfile(db, gridfs_id, suffix=suffix)
        return None, path
    # JC-STORAGE-PIVOT-GCS-BUILD (2026-07-02) — additive third branch.
    # Path A workbooks (uploaded via /api/uploads/complete) carry
    # `gcs_object_name` in place of `gridfs_id`. Stream-download from
    # GCS to a tempfile with the correct extension so downstream
    # openpyxl / csv parsers accept it.
    gcs_object_name = blob_row.get("gcs_object_name")
    if gcs_object_name:
        fmt = (blob_row.get("file_format") or "").lower()
        suffix = {
            "xlsx": ".xlsx",
            "csv":  ".csv",
        }.get(fmt, ".gcs")
        from services.storage_service import gcs_download_to_tempfile
        path = gcs_download_to_tempfile(gcs_object_name, suffix=suffix)
        return None, path
    legacy_b64 = blob_row.get("data_b64")
    if legacy_b64:
        return base64.b64decode(legacy_b64), None
    raise RuntimeError(
        f"blob row carries neither gridfs_id nor gcs_object_name nor data_b64 "
        f"(analysis_id={blob_row.get('analysis_id')}, "
        f"source_id={blob_row.get('source_id')})"
    )


# ──────────────────────────────────────────────────────────────────
# Analysis row construction.
# ──────────────────────────────────────────────────────────────────


def build_analysis_metadata(
    *,
    account_id: str,
    context_id: str,
    title: str,
    files: List[Tuple[str, int, str, str]],
    objective: str = "",
) -> Tuple[Analysis, List[Dict[str, Any]]]:
    """JC-WS · BUG-ANL-UPLOAD-GRIDFS (2026-06-26) — GridFS-aware
    constructor.

    `files`: list of `(filename, size_bytes, file_format, gridfs_id)`.
    The GridFS upload MUST have already happened upstream; this
    function only assembles the `Analysis` row + the metadata
    rows that go into `analysis_blobs`.

    Returns: (Analysis instance, list of analysis_blobs documents
    each carrying `gridfs_id` instead of `data_b64`).
    """
    if not files:
        raise ValueError("at_least_one_file_required")
    if not context_id:
        raise ValueError("context_id_required")

    analysis_id = _new_id("ana")
    sources: List[AnalysisSource] = []
    blob_docs: List[Dict[str, Any]] = []
    for (fname, size_bytes, fmt, gridfs_id) in files:
        source_id = _new_id("src")
        sources.append(AnalysisSource(
            source_id=source_id,
            filename=fname,
            file_format=fmt,  # type: ignore[arg-type]
            file_size_bytes=size_bytes,
        ))
        blob_docs.append({
            "analysis_id": analysis_id,
            "source_id":   source_id,
            "account_id":  account_id,
            "context_id":  context_id,
            "filename":    fname,
            "file_format": fmt,
            "gridfs_id":   gridfs_id,
            "created_at":  _iso_now(),
        })

    analysis = Analysis(
        id=analysis_id,
        account_id=account_id,
        context_id=context_id,
        title=title,
        objective=objective,
        sources=sources,
        refresh_history=[
            AnalysisRefreshEntry(
                refresh_id=_new_id("rf"),
                triggered_by="upload",
                note=f"Initial upload of {len(sources)} file(s)",
            ),
        ],
    )
    return analysis, blob_docs


def build_analysis_from_uploads(
    *,
    account_id: str,
    context_id: str,
    title: str,
    files: List[Tuple[str, bytes, str]],
    objective: str = "",
) -> Tuple[Analysis, List[Dict[str, Any]]]:
    """LEGACY signature retained for backwards-compatibility.

    BUG-ANL-UPLOAD-GRIDFS (2026-06-26) — this entry point is NO LONGER
    used by the production upload path (the multi-file handler now
    calls `build_analysis_metadata(...)` after streaming each upload
    to GridFS). It is kept for unit tests / characterisation tests
    that still pass raw bytes through this constructor; those tests
    exercise the LEGACY inline-base64 path so the dual-read helper
    can be exercised against synthesised legacy rows.

    `files`: list of `(filename, raw_bytes, file_format)`.

    Returns: (Analysis instance, list of analysis_blobs documents
    each carrying `data_b64` — LEGACY shape for test scaffolds).
    """
    if not files:
        raise ValueError("at_least_one_file_required")
    if not context_id:
        raise ValueError("context_id_required")

    analysis_id = _new_id("ana")
    sources: List[AnalysisSource] = []
    blob_docs: List[Dict[str, Any]] = []
    for (fname, raw, fmt) in files:
        source_id = _new_id("src")
        sources.append(AnalysisSource(
            source_id=source_id,
            filename=fname,
            file_format=fmt,  # type: ignore[arg-type]
            file_size_bytes=len(raw),
        ))
        blob_docs.append({
            "analysis_id": analysis_id,
            "source_id":   source_id,
            "account_id":  account_id,
            "context_id":  context_id,
            "filename":    fname,
            "file_format": fmt,
            "data_b64":    base64.b64encode(raw).decode("ascii"),
            "created_at":  _iso_now(),
        })

    analysis = Analysis(
        id=analysis_id,
        account_id=account_id,
        context_id=context_id,
        title=title,
        objective=objective,
        sources=sources,
        refresh_history=[
            AnalysisRefreshEntry(
                refresh_id=_new_id("rf"),
                triggered_by="upload",
                note=f"Initial upload of {len(sources)} file(s)",
            ),
        ],
    )
    return analysis, blob_docs


# ──────────────────────────────────────────────────────────────────
# Session-close lifecycle hook.
# ──────────────────────────────────────────────────────────────────


async def delete_analysis_blobs(db, *, analysis_id: str, account_id: str) -> Dict[str, int]:
    """BUG-ANL-UPLOAD-GRIDFS (2026-06-26) — Delete all blobs for an
    Analysis from BOTH GridFS (chunks for any blob carrying
    `gridfs_id`) AND the `analysis_blobs` metadata collection.

    Returns: {"blobs_deleted": N, "gridfs_files_deleted": M,
              "gridfs_files_missing": K}
    Idempotent on re-run.
    """
    # Step 1: gather the GridFS file_ids before we drop the metadata.
    cursor = db.analysis_blobs.find(
        {"analysis_id": analysis_id, "account_id": account_id},
        {"_id": 0, "gridfs_id": 1},
    )
    gridfs_ids: List[str] = []
    async for row in cursor:
        fid = row.get("gridfs_id")
        if fid:
            gridfs_ids.append(fid)

    # Step 2: delete GridFS chunks (best-effort — missing files are
    # treated as already-cleaned).
    gridfs_deleted = 0
    gridfs_missing = 0
    for fid in gridfs_ids:
        ok = await delete_gridfs_file(db, fid)
        if ok:
            gridfs_deleted += 1
        else:
            gridfs_missing += 1

    # Step 3: drop the metadata rows.
    del_result = await db.analysis_blobs.delete_many({
        "analysis_id": analysis_id,
        "account_id":  account_id,
    })

    return {
        "blobs_deleted":         del_result.deleted_count,
        "gridfs_files_deleted":  gridfs_deleted,
        "gridfs_files_missing":  gridfs_missing,
    }


async def session_close(db, *, analysis_id: str, account_id: str, context_id: str) -> Dict[str, Any]:
    """Delete blobs in `analysis_blobs` scoped to this Analysis,
    mark sources `blob_purged=True`, append a session-close
    refresh-history row. Idempotent on re-run.

    Returns the touched Analysis row (sanitized; no _id).
    Returns None if the analysis doesn't exist or belongs to
    another tenant.

    BUG-ANL-UPLOAD-GRIDFS (2026-06-26) — now also drops GridFS
    chunks via `delete_analysis_blobs(...)` for any blob carrying
    `gridfs_id`. Legacy inline rows continue to drop via the
    `analysis_blobs.delete_many(...)` step inside the helper.
    """
    row = await db.analyses.find_one(
        {"id": analysis_id, "account_id": account_id, "context_id": context_id},
        {"_id": 0},
    )
    if not row:
        return None

    # Delete blobs (GridFS + metadata) scoped to this analysis.
    del_summary = await delete_analysis_blobs(
        db, analysis_id=analysis_id, account_id=account_id,
    )
    purged_count = del_summary["blobs_deleted"]

    # Mark sources purged + append refresh-history row.
    refresh_id = _new_id("rf")
    refresh_row = {
        "refresh_id":  refresh_id,
        "ran_at":       _iso_now(),
        "triggered_by": "session-close",
        "note":         (
            f"Purged {purged_count} blob(s) "
            f"(gridfs={del_summary['gridfs_files_deleted']}, "
            f"missing={del_summary['gridfs_files_missing']})"
        ),
    }
    await db.analyses.update_one(
        {"id": analysis_id, "account_id": account_id, "context_id": context_id},
        {
            "$set": {
                "updated_at": _iso_now(),
                "sources.$[].blob_purged": True,
                "status": "purged",
            },
            "$push": {"refresh_history": refresh_row},
        },
    )
    fresh = await db.analyses.find_one(
        {"id": analysis_id, "account_id": account_id, "context_id": context_id},
        {"_id": 0},
    )
    return fresh


__all__ = [
    # New (GridFS migration).
    "GRIDFS_BUCKET_NAME",
    "upload_to_gridfs",
    "download_to_tempfile",
    "delete_gridfs_file",
    "read_workbook_bytes",
    "build_analysis_metadata",
    "delete_analysis_blobs",
    # Retained (legacy + lifecycle).
    "build_analysis_from_uploads",
    "session_close",
]
