"""JC-STORAGE-PIVOT-GCS-BUILD (2026-07-02) — >16MB presigned upload flow.

Canonical spec: /app/memory/sprints/JC_STORAGE_PIVOT_GCS_BUILD.md
             + /app/memory/user_actions/K8S_INGRESS_STATUS.md §2
             + /app/memory/user_actions/GCS_CREDS_STASHED.md
             + /app/memory/rules/REPLACEMENT_NAMING_RULE.md

Bypasses the k8s ingress `proxy-body-size` limit for files > 16 MB by
having the browser PUT directly to GCS via a V4 signed URL. Files
≤ 16 MB continue to route through the existing GridFS in-band paths
(no change here).

Endpoints (all under `/api/uploads`):
  POST /presigned    → issue a V4 signed PUT URL for a large upload
  POST /complete     → verify the object exists in GCS, parse it,
                       persist workbook_analyses + workbook_blobs rows
                       with `gcs_object_name` in place of `gridfs_id`
  GET  /{artefact_id}/download → V4 signed GET URL for a GCS-backed
                       artefact; legacy GridFS artefacts fall through

All new code uses ONLY per-object GCS methods — no `list_buckets()`,
no `get_bucket(name)`. The bound SA is bucket-object scoped and would
403 on project-level calls.
"""
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core import db, get_current_account
from services.analysis_lifecycle import read_workbook_bytes
from services.storage_service import (
    GCS_BUCKET_NAME,
    STORAGE_MAX_UPLOAD_BYTES,
    STORAGE_MAX_UPLOAD_MB,
    STORAGE_X_THRESHOLD_BYTES,
    STORAGE_X_THRESHOLD_MB,
    gcs_generate_presigned_download_url,
    gcs_get_object_size,
    gcs_initiate_resumable_upload_session,
    gcs_verify_object_exists,
)
from services.workbook_analyzer import parse_workbook
from models.analysis import Analysis, AnalysisRefreshEntry, AnalysisSource


log = logging.getLogger("uploads.gcs_pivot")

router = APIRouter(prefix="/api/uploads", tags=["uploads-gcs-pivot"])


ACCEPT_EXT_WORKBOOK = {".xlsx", ".csv"}
KindLiteral = Literal["workbook"]


# ═══════════════════════════════════════════════════════════════════════
# Request / response models
# ═══════════════════════════════════════════════════════════════════════

class PresignedRequest(BaseModel):
    filename: str = Field(..., min_length=1)
    content_type: Optional[str] = None
    size_bytes: int = Field(..., ge=1)
    context_id: str = Field(..., min_length=1)
    kind: KindLiteral = "workbook"
    origin: Optional[str] = None


class PresignedResponse(BaseModel):
    """Stage 1B response shape · resumable-default for the >16 MB band.
    
    Fields:
        gcs_object_name: bucket-scoped object path to be written.
        upload_session_uri: URL to PUT chunks to via `Content-Range` headers.
        method: always `RESUMABLE` for this endpoint (single-PUT DEPRECATED).
        expires_at: nominal session validity (~7 days per GCS default).
        content_type: Content-Type to send on chunk PUTs.
        max_upload_mb: informational — the truth-in-capability ceiling.
    """
    gcs_object_name: str
    upload_session_uri: str
    method: Literal["RESUMABLE"] = "RESUMABLE"
    expires_at: str
    content_type: str
    max_upload_mb: int


class CompleteRequest(BaseModel):
    gcs_object_name: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    context_id: str = Field(..., min_length=1)
    kind: KindLiteral = "workbook"
    size_bytes: int = Field(..., ge=1)
    objective: Optional[str] = None
    title: Optional[str] = None


class CompleteResponse(BaseModel):
    id: str
    kind: KindLiteral
    status: str
    storage_backend: Literal["gcs"] = "gcs"
    gcs_object_name: str


class DownloadResponse(BaseModel):
    download_url: str
    expires_at: str
    method: Literal["GET"] = "GET"


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _expires_iso(seconds: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=int(seconds))).isoformat()


def _validate_ext(filename: str, kind: str) -> str:
    fname = filename or ""
    ext = ("." + fname.rsplit(".", 1)[-1].lower()) if "." in fname else ""
    if kind == "workbook":
        if ext not in ACCEPT_EXT_WORKBOOK:
            raise HTTPException(415, f"workbook_format_unsupported: {ext}")
        return "xlsx" if ext == ".xlsx" else "csv"
    raise HTTPException(400, f"unknown_kind: {kind}")


def _build_gcs_object_name(*, account_id: str, context_id: str, filename: str, kind: str) -> str:
    """Namespaced object key: `{kind}/{context_id}/{account_id}/{ts}-{rand}-{fname}`.
    No PII — filename is included as-is but treated as opaque bytes downstream."""
    # sanitise filename to safe URL chars (very light — GCS accepts most)
    safe_fname = "".join(
        c if (c.isalnum() or c in "._-") else "-" for c in (filename or "unnamed")
    )[:180] or "unnamed"
    stamp = int(datetime.now(timezone.utc).timestamp())
    return f"{kind}/{context_id}/{account_id}/{stamp}-{uuid.uuid4().hex[:10]}-{safe_fname}"


# ═══════════════════════════════════════════════════════════════════════
# POST /api/uploads/presigned
# ═══════════════════════════════════════════════════════════════════════

@router.post("/presigned", response_model=PresignedResponse)
async def uploads_presigned(
    body: PresignedRequest,
    current: Dict[str, Any] = Depends(get_current_account),
):
    """Stage 1B refactor 2026-07-02 · content-length dispatch:
    
      ≤ 16 MB      → 400 use_in_band_route (client must use `/api/workbook/upload-multi`)
      16 - 500 MB  → 200 with resumable session URI (method: RESUMABLE)
      > 500 MB     → 413 ceiling_exceeded
    
    Single-PUT V4 signed URLs are DEPRECATED for the >16 MB range (see
    `gcs_generate_presigned_upload_url` docstring). This endpoint is the
    single unified entry point for GCS uploads above the 16 MB gate.
    """
    if not GCS_BUCKET_NAME:
        raise HTTPException(500, "gcs_bucket_not_configured")
    if body.size_bytes <= STORAGE_X_THRESHOLD_BYTES:
        # ≤16 MB · must use existing in-band GridFS flow.
        raise HTTPException(
            status_code=400,
            detail={
                "error": "use_in_band_route",
                "reason": f"files <= {STORAGE_X_THRESHOLD_MB} MB must use the existing in-band upload route",
                "threshold_mb": STORAGE_X_THRESHOLD_MB,
            },
        )
    if body.size_bytes > STORAGE_MAX_UPLOAD_BYTES:
        # >ceiling · Truth-in-capability ceiling enforcement.
        # Interim guard 2026-07-02 (`JC-STORAGE-INTERIM-GUARD`):
        # ceiling temporarily lowered to 32 MB pending Stage 2
        # per-format ingest profiling. Error code carries the
        # `_interim_guard` suffix + a `note` naming the gap so
        # frontends can surface honest guidance to end-users.
        raise HTTPException(
            status_code=413,
            detail={
                "error": "ceiling_exceeded_interim_guard",
                "reason": f"files > {STORAGE_MAX_UPLOAD_MB} MB are rejected",
                "max_mb": STORAGE_MAX_UPLOAD_MB,
                "note": (
                    "Temporary ceiling pending per-format ingest profiling (Stage 2). "
                    "Transport up to 500MB proven via GCS resumable; per-format ingest "
                    "capacity not yet measured at that scale."
                ),
            },
        )

    _validate_ext(body.filename, body.kind)

    object_name = _build_gcs_object_name(
        account_id=current["id"],
        context_id=body.context_id,
        filename=body.filename,
        kind=body.kind,
    )
    content_type = body.content_type or "application/octet-stream"
    session_uri = gcs_initiate_resumable_upload_session(
        object_name=object_name,
        content_type=content_type,
        size=body.size_bytes,
        origin=body.origin,
    )
    # GCS session URIs are valid ~1 week per GCS default; we mark
    # expiry at +7 days as an honest approximation for clients.
    return PresignedResponse(
        gcs_object_name=object_name,
        upload_session_uri=session_uri,
        expires_at=_expires_iso(7 * 24 * 3600),
        content_type=content_type,
        max_upload_mb=STORAGE_MAX_UPLOAD_MB,
    )


# ═══════════════════════════════════════════════════════════════════════
# POST /api/uploads/complete
# ═══════════════════════════════════════════════════════════════════════

@router.post("/complete", response_model=CompleteResponse)
async def uploads_complete(
    body: CompleteRequest,
    current: Dict[str, Any] = Depends(get_current_account),
):
    if not GCS_BUCKET_NAME:
        raise HTTPException(500, "gcs_bucket_not_configured")

    # Ownership check on the object name — reject anything not scoped
    # to this account under the current context.
    account_id = current["id"]
    expected_prefix = f"{body.kind}/{body.context_id}/{account_id}/"
    if not body.gcs_object_name.startswith(expected_prefix):
        raise HTTPException(
            status_code=403,
            detail={"error": "object_name_scope_mismatch"},
        )

    if not gcs_verify_object_exists(body.gcs_object_name):
        raise HTTPException(404, "gcs_object_not_found")

    fmt = _validate_ext(body.filename, body.kind)

    if body.kind == "workbook":
        return await _complete_workbook(
            body=body, current=current, fmt=fmt,
        )
    # Unreachable — kind literal is constrained.
    raise HTTPException(400, "unsupported_kind")


async def _complete_workbook(
    *,
    body: CompleteRequest,
    current: Dict[str, Any],
    fmt: str,
) -> CompleteResponse:
    """Parse-validate the GCS-hosted workbook + persist analysis + blob rows."""
    # Reuse read_workbook_bytes's third branch by giving it a synthetic
    # blob_row. This streams from GCS to a tempfile and returns the path.
    _inline, tmp_path = await read_workbook_bytes(
        db,
        {"gcs_object_name": body.gcs_object_name, "file_format": fmt, "filename": body.filename},
    )
    try:
        if not tmp_path:
            raise HTTPException(500, "gcs_download_returned_no_tempfile")
        try:
            parse_workbook(file_path=tmp_path, file_format=fmt)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(422, f"workbook_parse_failed: {exc!s:.200}")
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:  # noqa: BLE001
                pass

    # Persist analysis row + blob row. Blob row carries `gcs_object_name`
    # in place of `gridfs_id` — that's the field `read_workbook_bytes`
    # now dispatches on for the third branch.
    account_id = current["id"]
    context_id = body.context_id
    analysis_id = "ana-" + uuid.uuid4().hex[:12]
    source_id = "src-" + uuid.uuid4().hex[:12]

    display_title = (body.title or "").strip() or body.filename

    analysis = Analysis(
        id=analysis_id,
        account_id=account_id,
        context_id=context_id,
        title=display_title,
        objective=(body.objective or ""),
        sources=[AnalysisSource(
            source_id=source_id,
            filename=body.filename,
            file_format=fmt,  # type: ignore[arg-type]
            file_size_bytes=body.size_bytes,
        )],
        refresh_history=[AnalysisRefreshEntry(
            refresh_id="rf-" + uuid.uuid4().hex[:12],
            triggered_by="upload",
            note="Initial upload via GCS presigned flow (>16 MB)",
        )],
    )
    await db.workbook_analyses.insert_one(analysis.model_dump())  # tenancy:allow-no-account-id — model.dump() insert: analysis carries account_id+context_id fields stamped at Analysis(...) constructor above; non-literal scanner cannot resolve through model.dump()

    await db.workbook_blobs.insert_one({
        "analysis_id":     analysis_id,
        "source_id":       source_id,
        "account_id":      account_id,
        "context_id":      context_id,
        "filename":        body.filename,
        "file_format":     fmt,
        "gcs_object_name": body.gcs_object_name,
        "size_bytes":      body.size_bytes,
        "created_at":      _now_iso(),
    })

    return CompleteResponse(
        id=analysis_id,
        kind="workbook",
        status="parsed",
        gcs_object_name=body.gcs_object_name,
    )


# ═══════════════════════════════════════════════════════════════════════
# GET /api/uploads/{artefact_id}/download
# ═══════════════════════════════════════════════════════════════════════

@router.get("/{artefact_id}/download", response_model=DownloadResponse)
async def uploads_download(
    artefact_id: str,
    current: Dict[str, Any] = Depends(get_current_account),
):
    """Return a V4 signed GET URL for a GCS-backed artefact.
    Legacy GridFS artefacts return 404 here (they use their own
    download route)."""
    if not GCS_BUCKET_NAME:
        raise HTTPException(500, "gcs_bucket_not_configured")

    # Currently only workbook artefacts land through this router.
    # Look up the analysis row + blob row (account_id-scoped).
    analysis = await db.workbook_analyses.find_one(
        {"id": artefact_id, "account_id": current["id"]},
        {"_id": 0, "id": 1, "sources": 1},
    )
    if not analysis:
        raise HTTPException(404, "artefact_not_found")

    blob = await db.workbook_blobs.find_one(
        {"analysis_id": artefact_id, "account_id": current["id"], "gcs_object_name": {"$exists": True}},
        {"_id": 0, "gcs_object_name": 1, "filename": 1},
    )
    if not blob:
        # Fall-through — this endpoint is GCS-only. Legacy GridFS artefacts
        # download via their existing route.
        raise HTTPException(404, "not_gcs_backed")

    ttl = 300  # 5 minutes
    url = gcs_generate_presigned_download_url(
        object_name=blob["gcs_object_name"],
        ttl_seconds=ttl,
        response_disposition=f'attachment; filename="{blob.get("filename") or "download"}"',
    )
    return DownloadResponse(
        download_url=url,
        expires_at=_expires_iso(ttl),
    )
