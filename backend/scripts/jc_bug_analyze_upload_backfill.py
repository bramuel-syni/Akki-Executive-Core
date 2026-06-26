"""JC-WS · BUG-ANL-UPLOAD-GRIDFS — Inline-blob → GridFS backfill.

Source of truth: `/app/memory/JC_WS_CANONICAL_SPEC.md` (Analyze
submodule under JC-WS; storage backend swap only).
Design memo: `/app/memory/jc_artifacts/bugs/analyze_upload_20260626.md`
Section 4 · Backfill plan.

WHAT IT DOES
============
Walks `workbook_blobs` and `analysis_blobs`, finds rows with
`data_b64` set AND no `gridfs_id`. For each row:
  1. base64-decodes the inline payload
  2. streams it into the GridFS `fs` bucket
  3. updates the row: $set gridfs_id, $unset data_b64

Per-row atomic. Idempotent. Resumable on interrupt.

WHY YOU MIGHT RUN IT
====================
The new code path writes ONLY to GridFS, but legacy rows still
carry `data_b64`. The dual-read helper (`read_workbook_bytes`)
handles both transparently — backfill is NOT required for the
new code to work. Run only if you want to consolidate storage,
e.g. before sunset of the inline path (P2 backlog item).

HOW TO RUN
==========
Defaults to DRY-RUN (counts only, no writes):

    cd /app/backend && python scripts/jc_bug_analyze_upload_backfill.py

Commit (writes GridFS chunks + flips rows):

    cd /app/backend && python scripts/jc_bug_analyze_upload_backfill.py --commit

Scope to one collection:

    --collection workbook_blobs     (or analysis_blobs)

Scope to one analysis:

    --analysis-id ana-abc123def456

The script connects to the same `MONGO_URL` the backend uses
(read from /app/backend/.env). For production, the operator sets
MONGO_URL to the Atlas URI in their shell before running.

INVARIANTS
==========
  • Per-row atomicity: write GridFS first, then update the row.
    On failure mid-row, the row stays inline (no half-state).
  • Idempotent: rows already carrying gridfs_id are skipped.
  • No silent loss: if the inline base64 fails to decode, the
    row is logged and SKIPPED. It stays inline until manually
    inspected.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import io
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")

from core import db  # noqa: E402
from services.analysis_lifecycle import upload_to_gridfs  # noqa: E402


VALID_COLLECTIONS = ("workbook_blobs", "analysis_blobs")


async def migrate_collection(
    *,
    collection: str,
    commit: bool = False,
    only_analysis_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Walk the given collection; migrate inline rows to GridFS.

    Returns: dict with keys
      `scanned`         total docs visited
      `eligible`        rows carrying `data_b64` AND no `gridfs_id`
      `migrated`        rows successfully flipped (or DRY-RUN count)
      `skipped_decode`  rows whose base64 wouldn't decode (LOGGED)
      `skipped_gridfs`  rows already on GridFS (idempotent skip)
      `errors`          rows where the write failed (DETAILS in log)
      `commit`          echo of the commit flag
    """
    if collection not in VALID_COLLECTIONS:
        raise ValueError(f"unsupported collection: {collection}; valid={VALID_COLLECTIONS}")

    coll = db[collection]
    query: Dict[str, Any] = {}
    if only_analysis_id:
        query["analysis_id"] = only_analysis_id

    cursor = coll.find(query, {"_id": 1, "analysis_id": 1, "source_id": 1,
                                "filename": 1, "file_format": 1,
                                "account_id": 1, "context_id": 1,
                                "data_b64": 1, "gridfs_id": 1, "created_at": 1})

    stats = {
        "scanned": 0, "eligible": 0, "migrated": 0,
        "skipped_decode": 0, "skipped_gridfs": 0, "errors": 0,
        "commit": commit, "collection": collection,
    }

    async for row in cursor:
        stats["scanned"] += 1

        if row.get("gridfs_id"):
            # Already migrated — no inline payload to copy. Idempotent.
            stats["skipped_gridfs"] += 1
            continue

        if not row.get("data_b64"):
            # Neither field — orphaned row, skip silently. Manual.
            continue

        stats["eligible"] += 1

        try:
            raw = base64.b64decode(row["data_b64"])
        except Exception as exc:  # noqa: BLE001
            stats["skipped_decode"] += 1
            print(
                f"[backfill] skipped (base64 decode failed): "
                f"_id={row['_id']} analysis_id={row.get('analysis_id')} "
                f"err={type(exc).__name__}: {exc!s:.200}"
            )
            continue

        if not commit:
            stats["migrated"] += 1  # DRY-RUN: counted as eligible.
            continue

        # Per-row atomic write: GridFS first, then $set gridfs_id /
        # $unset data_b64 in one Mongo update.
        kind = "workbook_blob" if collection == "workbook_blobs" else "analysis_blob"
        metadata = {
            "kind":         kind,
            "analysis_id":  row.get("analysis_id"),
            "source_id":    row.get("source_id"),
            "account_id":   row.get("account_id"),
            "context_id":   row.get("context_id"),
            "filename":     row.get("filename"),
            "file_format":  row.get("file_format"),
            "backfilled_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            file_id = await upload_to_gridfs(
                db,
                source=io.BytesIO(raw),
                filename=row.get("filename") or "backfilled",
                metadata=metadata,
            )
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            print(
                f"[backfill] ERROR (GridFS write failed): "
                f"_id={row['_id']} analysis_id={row.get('analysis_id')} "
                f"err={type(exc).__name__}: {exc!s:.200}"
            )
            continue

        # Atomic flip — only if the row still carries data_b64 AND no
        # gridfs_id (defends against concurrent backfill runs).
        result = await coll.update_one(
            {"_id": row["_id"], "data_b64": {"$exists": True}, "gridfs_id": {"$exists": False}},
            {"$set": {"gridfs_id": file_id}, "$unset": {"data_b64": ""}},
        )
        if result.modified_count == 1:
            stats["migrated"] += 1
        else:
            # Race condition (another runner migrated between find +
            # update) — delete the orphan GridFS file we just wrote
            # so storage doesn't double up.
            from services.analysis_lifecycle import delete_gridfs_file
            await delete_gridfs_file(db, file_id)
            stats["skipped_gridfs"] += 1

    return stats


async def main():
    parser = argparse.ArgumentParser(
        description="Inline-blob → GridFS backfill for analyze upload migration.",
    )
    parser.add_argument(
        "--collection", choices=VALID_COLLECTIONS + ("both",), default="both",
        help="Which collection to migrate (default: both).",
    )
    parser.add_argument(
        "--commit", action="store_true",
        help="Actually perform the writes. DEFAULT IS DRY-RUN (counts only).",
    )
    parser.add_argument(
        "--analysis-id", default=None,
        help="Scope to one analysis_id (testing / one-off recoveries).",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("JC-WS · BUG-ANL-UPLOAD-GRIDFS — inline → GridFS backfill")
    print("=" * 70)
    if not args.commit:
        print("MODE: DRY-RUN — pass --commit to perform writes.")
    else:
        print("MODE: COMMIT — writes will land in Mongo + GridFS.")
    print(f"Collection: {args.collection}")
    if args.analysis_id:
        print(f"Scoped to analysis_id: {args.analysis_id}")
    print()

    collections_to_run = (
        list(VALID_COLLECTIONS) if args.collection == "both" else [args.collection]
    )

    grand_summary = {}
    for coll in collections_to_run:
        print(f"--- {coll} ---")
        summary = await migrate_collection(
            collection=coll, commit=args.commit,
            only_analysis_id=args.analysis_id,
        )
        grand_summary[coll] = summary
        for k, v in summary.items():
            print(f"  {k}: {v}")
        print()

    print("=" * 70)
    if not args.commit:
        eligible_total = sum(s["eligible"] for s in grand_summary.values())
        if eligible_total > 0:
            print(f"DRY-RUN complete — {eligible_total} row(s) eligible.")
            print("Re-run with --commit to perform the migration.")
        else:
            print("DRY-RUN complete — no eligible rows found. Nothing to migrate.")
    else:
        migrated = sum(s["migrated"] for s in grand_summary.values())
        errors = sum(s["errors"] for s in grand_summary.values())
        print(f"COMMIT complete — migrated={migrated} · errors={errors}")
        if errors > 0:
            print("⚠️  Some rows failed to migrate. See per-row error log above.")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
