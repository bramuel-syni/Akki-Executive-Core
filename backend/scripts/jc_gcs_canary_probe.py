"""jc_gcs_canary_probe.py — SA + bucket + write/read/delete round-trip.

Canonical spec: /app/memory/sprints/JC_STORAGE_PIVOT_GCS_BUILD.md
             + /app/memory/rules/REPLACEMENT_NAMING_RULE.md
             + /app/memory/user_actions/GCS_CREDS_STASHED.md §"Notes for storage build"

Runs a per-object canary against `GCS_BUCKET_NAME` (default: the stashed
env var). Uses ONLY per-object methods — NO `client.list_buckets()`, NO
`client.get_bucket(name)`. Both return 403 for the current SA (documented
in GCS_CREDS_STASHED.md line 9 + REPLACEMENT_NAMING_RULE.md line 15).

Usage:
    python /app/backend/scripts/jc_gcs_canary_probe.py

Exit code:
    0 → GREEN (all 4 ops succeeded)
    1 → RED (one or more ops failed; details on stderr)
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Ensure backend env is loaded (script may run outside FastAPI process).
try:
    from dotenv import load_dotenv
    load_dotenv("/app/backend/.env")
except Exception:  # noqa: BLE001
    pass

try:
    from google.cloud import storage
except Exception as exc:  # noqa: BLE001
    print(f"[canary] RED · google-cloud-storage import failed: {exc}", file=sys.stderr)
    sys.exit(1)


BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "").strip()
CREDS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()


def _fail(msg: str) -> None:
    print(f"[canary] RED · {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not BUCKET_NAME:
        _fail("GCS_BUCKET_NAME env var not set")
    if not CREDS_PATH or not Path(CREDS_PATH).exists():
        _fail(f"GOOGLE_APPLICATION_CREDENTIALS not set or missing: {CREDS_PATH!r}")

    canary_name = f"_canary/probe-{int(time.time())}-{os.getpid()}.txt"
    payload = f"canary-{time.time_ns()}".encode()

    # Direct bucket handle — client.bucket() does NOT call GCS API.
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # 1) PUT
    blob = bucket.blob(canary_name)
    try:
        blob.upload_from_string(payload, content_type="text/plain")
    except Exception as exc:  # noqa: BLE001
        _fail(f"upload_from_string failed: {exc}")

    # 2) EXISTS
    try:
        exists = bucket.blob(canary_name).exists()
    except Exception as exc:  # noqa: BLE001
        _fail(f"exists() failed: {exc}")
    if not exists:
        _fail(f"blob {canary_name!r} not found immediately after PUT")

    # 3) GET
    try:
        got = bucket.blob(canary_name).download_as_bytes()
    except Exception as exc:  # noqa: BLE001
        _fail(f"download_as_bytes failed: {exc}")
    if got != payload:
        _fail(f"round-trip mismatch: got={got!r} expected={payload!r}")

    # 4) DELETE
    try:
        bucket.blob(canary_name).delete()
    except Exception as exc:  # noqa: BLE001
        _fail(f"delete failed: {exc}")

    # confirm delete
    try:
        still = bucket.blob(canary_name).exists()
    except Exception as exc:  # noqa: BLE001
        _fail(f"post-delete exists() failed: {exc}")
    if still:
        _fail(f"blob {canary_name!r} still exists after delete")

    print(f"[canary] GREEN · bucket={BUCKET_NAME} object={canary_name} ops=PUT/EXISTS/GET/DELETE")


if __name__ == "__main__":
    main()
