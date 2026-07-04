"""Phase 10 / Item B — S3-compatible object storage.

Two backends:

  * :class:`LocalDiskStorage` — preserves pre-Phase-10 behaviour. Used
    in tests and in dev environments without MinIO. Writes under
    ``UPLOADS_DIR`` (default ``/app/backend/uploads``).
  * :class:`S3Storage` — boto3 client against any S3-compatible
    endpoint (AWS S3, MinIO, Cloudflare R2, Backblaze B2). Server-side
    encryption AES256 enforced on every ``PUT``.

Backend is selected by ``STORAGE_BACKEND={local|s3}``.
Default in this env: ``s3`` (so MinIO is exercised by default).

Public interface:

  put(key, content, content_type, metadata) -> {key, size, etag}
  get_bytes(key) -> bytes
  get_presigned_url(key, ttl_seconds=300, response_content_disposition=None) -> str
  delete(key) -> bool
  head(key) -> {exists, size, etag, content_type, last_modified}

``key`` convention: ``{context_id}/{doc_id}/{sanitised_filename}``. No
PII in the key or in object metadata.
"""
from __future__ import annotations

import io
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("akki.storage")


STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "s3").strip().lower()
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "http://127.0.0.1:9000")
S3_REGION = os.environ.get("S3_REGION", "eu-west-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "akki-uploads")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "")
S3_FORCE_PATH_STYLE = os.environ.get("S3_FORCE_PATH_STYLE", "true").lower() in ("1", "true", "yes")
LOCAL_UPLOADS_DIR = Path(os.environ.get("UPLOADS_DIR", "/app/backend/uploads"))


_SANE_NAME_RE = re.compile(r"[^A-Za-z0-9._\-]+")


def _sanitise(name: str) -> str:
    """Collapse non-alphanumeric to '-' and cap length."""
    name = (name or "file").strip()
    name = _SANE_NAME_RE.sub("-", name)
    return name[:180] or "file"


def make_key(context_id: str, doc_id: str, filename: str) -> str:
    """Canonical storage key. Used by every upload path."""
    return f"{context_id}/{doc_id}/{_sanitise(filename)}"


# ---------------------------------------------------------------------------
# Backend: local disk
# ---------------------------------------------------------------------------
class LocalDiskStorage:
    backend = "local"

    def __init__(self, root: Path = LOCAL_UPLOADS_DIR):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _p(self, key: str) -> Path:
        return self.root / key

    def put(self, key: str, content: bytes, content_type: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        path = self._p(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {"key": key, "size": len(content), "etag": None}

    def get_bytes(self, key: str) -> bytes:
        path = self._p(key)
        if not path.exists():
            raise FileNotFoundError(key)
        return path.read_bytes()

    def get_presigned_url(self, key: str, ttl_seconds: int = 300,
                          response_content_disposition: Optional[str] = None) -> str:
        # Local backend: synthesise an in-app download URL. Callers that
        # rely on a real presigned URL (e.g. the Studio image block on a
        # production deploy) will be on the S3 backend.
        return f"/api/storage/local/{key}"

    def delete(self, key: str) -> bool:
        path = self._p(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def head(self, key: str) -> Dict[str, Any]:
        path = self._p(key)
        if not path.exists():
            return {"exists": False}
        st = path.stat()
        return {
            "exists": True,
            "size": st.st_size,
            "etag": None,
            "content_type": None,
            "last_modified": st.st_mtime,
        }


# ---------------------------------------------------------------------------
# Backend: S3 / MinIO
# ---------------------------------------------------------------------------
class S3Storage:
    backend = "s3"

    def __init__(self):
        import boto3
        from botocore.client import Config
        if not S3_ACCESS_KEY or not S3_SECRET_KEY:
            raise RuntimeError(
                "STORAGE_BACKEND=s3 requires S3_ACCESS_KEY and S3_SECRET_KEY"
            )
        self.bucket = S3_BUCKET
        self.client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path" if S3_FORCE_PATH_STYLE else "virtual"},
            ),
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.client.create_bucket(Bucket=self.bucket)
                logger.info("created bucket %s", self.bucket)
            except Exception as e:  # noqa: BLE001
                logger.warning("could not create bucket %s: %s", self.bucket, e)

    def put(self, key: str, content: bytes, content_type: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        extra: Dict[str, Any] = {
            "ServerSideEncryption": "AES256",
        }
        if content_type:
            extra["ContentType"] = content_type
        if metadata:
            # Strip any PII-shaped values defensively — S3 metadata is
            # header-scoped and we don't want surprise leakage.
            extra["Metadata"] = {
                str(k)[:80]: str(v)[:240] for k, v in metadata.items() if k and v is not None
            }
        resp = self.client.put_object(
            Bucket=self.bucket, Key=key, Body=content, **extra,
        )
        return {"key": key, "size": len(content), "etag": (resp.get("ETag") or "").strip('"')}

    def get_bytes(self, key: str) -> bytes:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=key)
        except self.client.exceptions.NoSuchKey as e:
            raise FileNotFoundError(key) from e
        return obj["Body"].read()

    def get_presigned_url(self, key: str, ttl_seconds: int = 300,
                          response_content_disposition: Optional[str] = None) -> str:
        params: Dict[str, Any] = {"Bucket": self.bucket, "Key": key}
        if response_content_disposition:
            params["ResponseContentDisposition"] = response_content_disposition
        return self.client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=int(ttl_seconds),
        )

    def delete(self, key: str) -> bool:
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return True

    def head(self, key: str) -> Dict[str, Any]:
        try:
            r = self.client.head_object(Bucket=self.bucket, Key=key)
        except Exception:
            return {"exists": False}
        return {
            "exists": True,
            "size": r.get("ContentLength"),
            "etag": (r.get("ETag") or "").strip('"'),
            "content_type": r.get("ContentType"),
            "last_modified": r.get("LastModified").isoformat() if r.get("LastModified") else None,
        }


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------
_BACKEND: Any = None


def get_storage():
    global _BACKEND
    if _BACKEND is not None:
        return _BACKEND
    if STORAGE_BACKEND == "local":
        _BACKEND = LocalDiskStorage()
    else:
        _BACKEND = S3Storage()
    logger.info("storage backend initialised: %s", _BACKEND.backend)
    return _BACKEND


# ---------------------------------------------------------------------------
# Back-compat shim — `documents_service.save_to_storage` used to return
# a local-disk relative path. The S3 backend returns the object key.
# The DB column stored that string either way, so nothing else needs to
# change; but we provide thin wrappers so the existing call sites read
# naturally.
# ---------------------------------------------------------------------------
def save(context_id: str, doc_id: str, filename: str, data: bytes,
         content_type: Optional[str] = None) -> str:
    key = make_key(context_id, doc_id, filename)
    result = get_storage().put(key, data, content_type=content_type)
    return result["key"]


def read(key: str) -> bytes:
    # Back-compat: old local-disk keys were relative paths. Try them.
    try:
        return get_storage().get_bytes(key)
    except FileNotFoundError:
        # Fallback for pre-Phase-10 local disk keys — only when running
        # the s3 backend with legacy rows still pointing at the disk.
        legacy = LOCAL_UPLOADS_DIR / key
        if legacy.exists():
            return legacy.read_bytes()
        raise


def delete(key: str) -> bool:
    try:
        return get_storage().delete(key)
    except FileNotFoundError:
        return False



# ═══════════════════════════════════════════════════════════════════════
# JC-STORAGE-PIVOT-GCS-BUILD (2026-07-02) — additive GCS helpers.
# ═══════════════════════════════════════════════════════════════════════
#
# Purpose: browser-direct-to-GCS uploads for files > STORAGE_X_THRESHOLD_MB
# to bypass the k8s ingress `proxy-body-size` limit.
#
# Design constraints (see /app/memory/user_actions/GCS_CREDS_STASHED.md
# and /app/memory/rules/REPLACEMENT_NAMING_RULE.md):
#   * The bound SA is **bucket-object scoped** — no project-scope calls.
#     Do NOT call `client.list_buckets()`, `client.get_bucket(name)`, or
#     any other API that requires project-level permissions. Use direct
#     `client.bucket(name)` (returns a handle without an API call) plus
#     per-object methods (`bucket.blob(x).upload_from_string()`,
#     `.exists()`, `.download_as_bytes()`, `.delete()`, `.generate_signed_url()`).
#   * V4 signing is used for all presigned URLs.
#   * These helpers are ADDITIVE — the S3/MinIO/LocalDiskStorage backend
#     above is untouched and remains the default for the pre-existing
#     upload paths. Only the new `/api/uploads/*` router uses these.
# ═══════════════════════════════════════════════════════════════════════

from datetime import timedelta as _timedelta

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "").strip()
GCS_ARCHIVE_PREFIX = os.environ.get("GCS_ARCHIVE_PREFIX", "_archive/")
STORAGE_X_THRESHOLD_MB = int(os.environ.get("STORAGE_X_THRESHOLD_MB", "16") or "16")
STORAGE_X_THRESHOLD_BYTES = STORAGE_X_THRESHOLD_MB * 1024 * 1024
STORAGE_MAX_UPLOAD_MB = int(os.environ.get("STORAGE_MAX_UPLOAD_MB", "500") or "500")
STORAGE_MAX_UPLOAD_BYTES = STORAGE_MAX_UPLOAD_MB * 1024 * 1024
STORAGE_RESUMABLE_THRESHOLD_MB = int(os.environ.get("STORAGE_RESUMABLE_THRESHOLD_MB", "100") or "100")
STORAGE_RESUMABLE_THRESHOLD_BYTES = STORAGE_RESUMABLE_THRESHOLD_MB * 1024 * 1024
STORAGE_PRESIGNED_TTL_SECONDS = int(os.environ.get("STORAGE_PRESIGNED_TTL_SECONDS", "3600") or "3600")

_GCS_CLIENT = None  # module-level cache; storage.Client() calls no APIs on construct


def gcs_client():
    """Cached GCS client. Constructor does NOT make an API call."""
    global _GCS_CLIENT
    if _GCS_CLIENT is not None:
        return _GCS_CLIENT
    from google.cloud import storage as _gcs_storage
    _GCS_CLIENT = _gcs_storage.Client()
    return _GCS_CLIENT


def _gcs_bucket():
    """Direct bucket handle. `client.bucket(name)` is a local operation
    (no API call), safe for a bucket-object-scoped SA. NEVER swap this
    for `client.get_bucket(name)` — that requires `storage.buckets.get`
    which this SA lacks (403)."""
    if not GCS_BUCKET_NAME:
        raise RuntimeError("GCS_BUCKET_NAME env var not set")
    return gcs_client().bucket(GCS_BUCKET_NAME)


def gcs_generate_presigned_upload_url(
    object_name: str,
    content_type: str = "application/octet-stream",
    ttl_seconds: int = 900,
) -> str:
    """Return a V4 signed PUT URL for `object_name`. Default TTL 15 min."""
    blob = _gcs_bucket().blob(object_name)
    return blob.generate_signed_url(
        version="v4",
        expiration=_timedelta(seconds=int(ttl_seconds)),
        method="PUT",
        content_type=content_type,
    )


def gcs_generate_presigned_download_url(
    object_name: str,
    ttl_seconds: int = 300,
    response_disposition: Optional[str] = None,
) -> str:
    """Return a V4 signed GET URL for `object_name`. Default TTL 5 min."""
    blob = _gcs_bucket().blob(object_name)
    kwargs: Dict[str, Any] = dict(
        version="v4",
        expiration=_timedelta(seconds=int(ttl_seconds)),
        method="GET",
    )
    if response_disposition:
        kwargs["response_disposition"] = response_disposition
    return blob.generate_signed_url(**kwargs)


def gcs_verify_object_exists(object_name: str) -> bool:
    """Per-object existence check via `bucket.blob(name).exists()`.
    Safe for a bucket-object-scoped SA."""
    try:
        return bool(_gcs_bucket().blob(object_name).exists())
    except Exception as exc:  # noqa: BLE001
        logger.warning("gcs_verify_object_exists failed for %s: %s", object_name, exc)
        return False


def gcs_provision_archive_marker() -> bool:
    """Idempotently upload the archive-prefix marker. Confirms the SA
    holds write permission on the target prefix without creating any
    user-facing artefact."""
    marker_name = f"{GCS_ARCHIVE_PREFIX.rstrip('/')}/.provisioned"
    blob = _gcs_bucket().blob(marker_name)
    if blob.exists():
        return True
    blob.upload_from_string(
        b"jc-storage-pivot-gcs-build provisioned",
        content_type="text/plain",
    )
    return True


def gcs_download_to_tempfile(object_name: str, suffix: str = ".bin") -> str:
    """Stream-download `object_name` to a NamedTemporaryFile and return
    the path. Caller MUST `os.unlink()` after use."""
    import tempfile as _tempfile
    blob = _gcs_bucket().blob(object_name)
    with _tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tf:
        blob.download_to_file(tf)
        path = tf.name
    return path


def gcs_delete_object(object_name: str) -> bool:
    """Delete a single object; returns False if it does not exist."""
    blob = _gcs_bucket().blob(object_name)
    if not blob.exists():
        return False
    blob.delete()
    return True


def gcs_create_resumable_upload_session(
    object_name: str,
    content_type: str = "application/octet-stream",
    size: Optional[int] = None,
    origin: Optional[str] = None,
) -> str:
    """Initiate a GCS resumable upload session and return the session URI.

    The returned URI is a signed URL the browser (or any HTTP client) can
    PUT chunks to using `Content-Range: bytes {start}-{end}/{total}` headers.
    Session URIs are valid for ~1 week per GCS default. Chunks may be as
    small as 256 KiB (except final) and as large as the full remaining
    payload.

    Requires the SA to have `storage.objects.create` on the bucket — which
    our bound SA has. This method uses per-object `blob.create_resumable_upload_session`
    ONLY; no project-scope calls.

    Args:
        object_name: GCS blob path.
        content_type: Content-Type for the eventual object.
        size: Total upload size in bytes (highly recommended; GCS pre-allocates).
        origin: Frontend origin for CORS on the resumable session (e.g.
            'https://akki.syni.ai'). If unset, no Origin header is sent.
    """
    blob = _gcs_bucket().blob(object_name)
    kwargs: Dict[str, Any] = {"content_type": content_type}
    if size is not None:
        kwargs["size"] = int(size)
    if origin:
        kwargs["origin"] = origin
    return blob.create_resumable_upload_session(**kwargs)


def gcs_get_object_size(object_name: str) -> Optional[int]:
    """Return the size in bytes for an existing blob, or None if absent."""
    blob = _gcs_bucket().blob(object_name)
    blob.reload()  # refreshes metadata from GCS (per-object; no project call)
    return int(blob.size) if blob.size is not None else None
