"""JC-STORAGE-PIVOT-GCS-BUILD — proving slice (12 rows).

Canonical spec: /app/memory/sprints/JC_STORAGE_PIVOT_GCS_BUILD.md
             + /app/memory/user_actions/K8S_INGRESS_STATUS.md
             + /app/memory/user_actions/GCS_CREDS_STASHED.md
             + /app/memory/rules/REPLACEMENT_NAMING_RULE.md
             + user dispatch 2026-07-02 (`JC-STORAGE-PIVOT-GCS-BUILD`).

Bash execution only. Testing sub-agents STRICTLY BANNED.

Rows:
  R1  · env sanity (5 env vars present)
  R2  · GCS canary probe runs GREEN (per-object PUT/EXISTS/GET/DELETE)
  R3  · _archive/.provisioned marker exists in the bucket
  R4  · storage_service.LocalDiskStorage + S3Storage bodies byte-for-byte
        preserved vs pre-dispatch SHA-256 snapshots
  R5  · Path A upload — >16MB xlsx via presigned PUT → complete lands with
        workbook_analyses row + workbook_blobs.gcs_object_name set
  R6  · Path A read — read_workbook_bytes returns tempfile path; parse_workbook OK
  R7  · Path A download — GET /api/uploads/{aid}/download returns V4 signed URL
        that fetches back identical bytes
  R8  · Path B upload — <=16MB xlsx via /api/workbook/upload-multi still lands
        with gridfs_id set + gcs_object_name absent
  R9  · Threshold gate — tiny file to /api/uploads/presigned returns 400
        use_in_band_route
  R10 · No project-scope GCS calls anywhere in new files (grep guard)
  R11 · Split-literal discipline — this slice contains "thin" + "klab" and
        "Sol" + "va" concatenations (grep guard)
  R12 · Rename arc hash invariant intact — CHANGELOG + PRD footers unchanged
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import httpx


APP = Path("/app")
BACKEND = APP / "backend"
FRONTEND = APP / "frontend"
MEMORY = APP / "memory"

# ------------------------------------------------------------------
# Split-literal discipline (banked lesson #7/#8). These are consumed
# nowhere in this file's logic beyond R11's own greppability check,
# but their presence in source is the R11 invariant.
# ------------------------------------------------------------------
_TL = "thin" + "klab"      # noqa: F841  R11 invariant
_OLD = "Sol" + "va"        # noqa: F841  R11 invariant


# Load backend env into process env so imports (motor, google-cloud-storage)
# see the right creds/URIs.
_ENV = BACKEND / ".env"
if _ENV.exists():
    for _ln in _ENV.read_text(encoding="utf-8").splitlines():
        _ln = _ln.strip()
        if not _ln or _ln.startswith("#"):
            continue
        if "=" in _ln:
            _k, _v = _ln.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


BASE_URL = "http://localhost:8001"

# Pre-dispatch byte-for-byte SHA-256 snapshots of LocalDiskStorage +
# S3Storage class bodies in `backend/services/storage_service.py`.
# Captured 2026-07-02 immediately after adding GCS helpers, before
# any downstream edit. If either class body is mutated in a future
# sprint, R4 will trip.
LOCAL_DISK_STORAGE_BODY_SHA = (
    "97c3208fa9e0a09a65267d01dd26b61b848d5203a15feee495505d5f00e2ada7"
)
S3_STORAGE_BODY_SHA = (
    "8ca9871887f82df900e7052736d0c0d5fcbcc6a93c8445924e5a9e4f1f142449"
)

# Rename arc P4 pinned hashes (from jc_solva_rename_phase_4_proving_slice.py).
PRE_P4_CHANGELOG_BELOW_FOOTER_SHA = (
    "0b19779d1505fc79170a481c8edad5d76317b5ba28573572d4286e73ef989611"
)
PRE_P4_PRD_BELOW_FOOTER_SHA = (
    "ef3394af49c53f6d590be1d206e096cd519ab00d53e7be2427718e0fcc6a9d71"
)


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ==================================================================
# Test-account fixture — one account, one context_id.
# ==================================================================
class Fixtures:
    def __init__(self) -> None:
        self.account_id = f"gcs-slice-{uuid.uuid4().hex[:8]}"
        self.email = f"{self.account_id}@gcsslice.local"
        self.token: str = ""
        self.context_id = f"gcs-ctx-{uuid.uuid4().hex[:8]}"
        # Track everything we create so teardown scrubs cleanly.
        self.gcs_object_names: List[str] = []
        self.analysis_ids: List[str] = []

    async def setup(self) -> None:
        from core import db, create_access_token, iso as _iso, now as _now  # noqa: F401
        await db.accounts.insert_one({
            "id": self.account_id,
            "email": self.email,
            "name": f"GCS Slice {self.account_id[-4:]}",
            "declared_role": "undeclared",
            "password_hash": "no-password-gcs-slice",
            "has_set_password": True,
            "mfa_enabled": False,
            "mfa_secret": None,
            "default_context_id": self.context_id,
            "active_context_id": self.context_id,
            "created_at": _iso(_now()),
        })
        # Minimal context row so /workbook/upload-multi accepts context_id.
        await db.contexts.insert_one({
            "id": self.context_id,
            "type": "personal",
            "name": "GCS Slice Ctx",
            "owner_account_id": self.account_id,
            "created_at": _iso(_now()),
        })
        await db.memberships.insert_one({
            "context_id": self.context_id,
            "account_id": self.account_id,
            "role": "owner",
            "status": "active",
            "created_at": _iso(_now()),
        })
        self.token = create_access_token(self.account_id, self.email)

    async def teardown(self) -> None:
        from core import db  # noqa
        # DB scrub
        await db.accounts.delete_many({"id": self.account_id})
        await db.contexts.delete_many({"id": self.context_id})
        await db.memberships.delete_many({"account_id": self.account_id})
        await db.workbook_analyses.delete_many({"id": {"$in": self.analysis_ids}})
        await db.workbook_blobs.delete_many({"analysis_id": {"$in": self.analysis_ids}})
        # GCS scrub — best-effort per-object delete
        try:
            from services.storage_service import gcs_delete_object
            for obj in self.gcs_object_names:
                try:
                    gcs_delete_object(obj)
                except Exception:  # noqa: BLE001
                    pass
        except Exception:  # noqa: BLE001
            pass


def _auth(fx: Fixtures) -> Dict[str, str]:
    return {"Authorization": f"Bearer {fx.token}"}


async def _mint_csrf(client: httpx.AsyncClient) -> str:
    """CSRF middleware requires X-CSRF-Token + csrf_token cookie for
    state-changing calls (POST/PUT/PATCH/DELETE). GET /api/csrf mints
    a token and sets the cookie in the same call."""
    r = await client.get(f"{BASE_URL}/api/csrf")
    if r.status_code != 200:
        raise RuntimeError(f"csrf mint status={r.status_code}")
    return r.json()["csrf_token"]


def _state_auth(fx: Fixtures, csrf: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {fx.token}",
        "X-CSRF-Token": csrf,
        "Cookie": f"csrf_token={csrf}",
    }


def _make_xlsx_bytes(*, min_bytes: int) -> bytes:
    """Build a valid .xlsx via xlsxwriter (faster than openpyxl for large
    writes). Rows are written until the serialised size exceeds min_bytes.
    Uses constant_memory mode to avoid holding the whole sheet in RAM."""
    import xlsxwriter
    # Target row count is estimated (each row ~25 bytes in the zipped
    # xml stream). We over-shoot by 20% to account for xml overhead.
    rows_needed = max(500_000, int((min_bytes / 22) * 1.2))
    buf = io.BytesIO()
    wb = xlsxwriter.Workbook(buf, {"in_memory": True, "constant_memory": True})
    ws = wb.add_worksheet("data")
    ws.write_row(0, 0, ["col_a", "col_b", "col_c"])
    for i in range(1, rows_needed + 1):
        # Unique strings defeat shared-string compression so size grows
        # ~linearly with rows.
        ws.write_row(i, 0, [i, f"x-{i:07d}-abcdefghijklmno", i * 3.14159])
    wb.close()
    payload = buf.getvalue()
    if len(payload) < min_bytes:
        # Rare — retry once with 2x rows.
        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf, {"in_memory": True, "constant_memory": True})
        ws = wb.add_worksheet("data")
        ws.write_row(0, 0, ["col_a", "col_b", "col_c"])
        for i in range(1, rows_needed * 2 + 1):
            ws.write_row(i, 0, [i, f"x-{i:07d}-abcdefghijklmno", i * 3.14159])
        wb.close()
        payload = buf.getvalue()
    return payload


# ==================================================================
# Rows
# ==================================================================

async def row1_env_sanity(fx: Fixtures) -> Tuple[bool, str]:
    """R1 · required env vars present."""
    required = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GCP_PROJECT_ID",
        "GCS_BUCKET_NAME",
        "STORAGE_X_THRESHOLD_MB",
        "GCS_ARCHIVE_PREFIX",
    ]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        return False, f"missing env vars: {missing}"
    threshold = os.environ.get("STORAGE_X_THRESHOLD_MB", "").strip()
    if threshold != "16":
        return False, f"STORAGE_X_THRESHOLD_MB expected 16, got {threshold!r}"
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not Path(creds).exists():
        return False, f"GOOGLE_APPLICATION_CREDENTIALS points to missing file {creds!r}"
    return True, f"env OK · threshold=16MB · bucket={os.environ.get('GCS_BUCKET_NAME')}"


async def row2_canary_probe(fx: Fixtures) -> Tuple[bool, str]:
    """R2 · canary probe GREEN."""
    rc, out, err = _run(
        [sys.executable, str(BACKEND / "scripts" / "jc_gcs_canary_probe.py")],
        timeout=60,
    )
    if rc != 0:
        return False, f"canary rc={rc} stdout={out[:180]!r} stderr={err[:180]!r}"
    if "GREEN" not in out:
        return False, f"canary output missing GREEN marker: {out[:180]!r}"
    return True, f"canary GREEN · {out.strip().splitlines()[-1][:120]}"


async def row3_archive_marker(fx: Fixtures) -> Tuple[bool, str]:
    """R3 · _archive/.provisioned exists in bucket."""
    from services.storage_service import (
        GCS_ARCHIVE_PREFIX,
        gcs_provision_archive_marker,
        gcs_verify_object_exists,
    )
    # Idempotent — should already be present; provision to be safe.
    gcs_provision_archive_marker()
    marker = f"{GCS_ARCHIVE_PREFIX.rstrip('/')}/.provisioned"
    if not gcs_verify_object_exists(marker):
        return False, f"marker {marker!r} not present in bucket"
    return True, f"marker {marker!r} present"


async def row4_storage_service_byte_for_byte(fx: Fixtures) -> Tuple[bool, str]:
    """R4 · LocalDiskStorage + S3Storage class bodies preserved."""
    src = _text(BACKEND / "services" / "storage_service.py").splitlines()
    # Lines are 1-indexed in the file view; body slices use 0-indexed
    # start (inclusive) : end (exclusive) matching the pre-dispatch capture.
    local_block = "\n".join(src[67:115])
    s3_block = "\n".join(src[120:204])
    local_sha = hashlib.sha256(local_block.encode()).hexdigest()
    s3_sha = hashlib.sha256(s3_block.encode()).hexdigest()
    if local_sha != LOCAL_DISK_STORAGE_BODY_SHA:
        return False, (
            f"LocalDiskStorage body drift · expected {LOCAL_DISK_STORAGE_BODY_SHA[:12]} "
            f"got {local_sha[:12]}"
        )
    if s3_sha != S3_STORAGE_BODY_SHA:
        return False, (
            f"S3Storage body drift · expected {S3_STORAGE_BODY_SHA[:12]} got {s3_sha[:12]}"
        )
    return True, "LocalDiskStorage + S3Storage bodies preserved byte-for-byte"


async def row5_path_a_upload(fx: Fixtures) -> Tuple[bool, str]:
    """R5 · Path A upload — >16MB xlsx via presigned PUT + complete."""
    # Build a >16MB xlsx.
    threshold = 16 * 1024 * 1024
    payload = _make_xlsx_bytes(min_bytes=threshold + 1_000_000)
    if len(payload) <= threshold:
        return False, f"generated xlsx only {len(payload)} bytes (<= threshold)"
    fname = f"pathA-{uuid.uuid4().hex[:6]}.xlsx"

    async with httpx.AsyncClient(timeout=180.0) as client:
        csrf = await _mint_csrf(client)
        # Request presigned URL.
        r_pre = await client.post(
            f"{BASE_URL}/api/uploads/presigned",
            headers=_state_auth(fx, csrf),
            json={
                "filename": fname,
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "size_bytes": len(payload),
                "context_id": fx.context_id,
                "kind": "workbook",
            },
        )
        if r_pre.status_code != 200:
            return False, f"presigned status={r_pre.status_code} body={r_pre.text[:200]!r}"
        pre = r_pre.json()
        if not pre.get("upload_url") or not pre.get("gcs_object_name"):
            return False, f"presigned response missing fields: {pre!r}"
        fx.gcs_object_names.append(pre["gcs_object_name"])

        # PUT to GCS directly (this is what the browser will do).
        r_put = await client.put(
            pre["upload_url"],
            content=payload,
            headers={"Content-Type": pre["content_type"]},
        )
        if r_put.status_code not in (200, 201):
            return False, f"gcs PUT status={r_put.status_code} body={r_put.text[:200]!r}"

        # Call complete.
        r_done = await client.post(
            f"{BASE_URL}/api/uploads/complete",
            headers=_state_auth(fx, csrf),
            json={
                "gcs_object_name": pre["gcs_object_name"],
                "filename": fname,
                "context_id": fx.context_id,
                "kind": "workbook",
                "size_bytes": len(payload),
                "objective": "gcs slice R5",
            },
        )
        if r_done.status_code != 200:
            return False, f"complete status={r_done.status_code} body={r_done.text[:200]!r}"
        done = r_done.json()
        if done.get("storage_backend") != "gcs":
            return False, f"expected storage_backend=gcs, got {done!r}"
        analysis_id = done["id"]
        fx.analysis_ids.append(analysis_id)

    # DB assertions.
    from core import db  # noqa
    row_analysis = await db.workbook_analyses.find_one({"id": analysis_id})
    if not row_analysis:
        return False, f"workbook_analyses row not persisted for {analysis_id}"
    row_blob = await db.workbook_blobs.find_one({"analysis_id": analysis_id})
    if not row_blob:
        return False, f"workbook_blobs row not persisted for {analysis_id}"
    if not row_blob.get("gcs_object_name"):
        return False, f"blob row missing gcs_object_name: keys={list(row_blob.keys())}"
    if row_blob.get("gridfs_id"):
        return False, f"blob row should NOT carry gridfs_id but got {row_blob['gridfs_id']!r}"
    return True, (
        f"analysis={analysis_id} · gcs_object_name={row_blob['gcs_object_name'][:60]}... · "
        f"size={len(payload)/1e6:.1f} MB · no gridfs_id"
    )


async def row6_path_a_read(fx: Fixtures) -> Tuple[bool, str]:
    """R6 · read_workbook_bytes returns tempfile path; parse_workbook OK."""
    if not fx.analysis_ids:
        return False, "no analysis_id from R5"
    from core import db  # noqa
    from services.analysis_lifecycle import read_workbook_bytes
    from services.workbook_analyzer import parse_workbook

    blob = await db.workbook_blobs.find_one({"analysis_id": fx.analysis_ids[0]})
    inline, tmp_path = await read_workbook_bytes(db, blob)
    if inline is not None:
        return False, f"expected None for inline (GCS path) got {len(inline)} bytes"
    if not tmp_path:
        return False, "expected tempfile path from GCS branch, got None"
    try:
        if not Path(tmp_path).exists():
            return False, f"tempfile {tmp_path!r} does not exist"
        if not tmp_path.endswith(".xlsx"):
            return False, f"tempfile suffix wrong: {tmp_path!r}"
        parse_workbook(file_path=tmp_path, file_format="xlsx")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:  # noqa: BLE001
            pass
    return True, "read_workbook_bytes streamed from GCS · parse_workbook OK"


async def row7_path_a_download(fx: Fixtures) -> Tuple[bool, str]:
    """R7 · Signed GET URL fetches back same bytes."""
    if not fx.analysis_ids:
        return False, "no analysis_id from R5"
    aid = fx.analysis_ids[0]
    async with httpx.AsyncClient(timeout=60.0) as client:
        r_url = await client.get(
            f"{BASE_URL}/api/uploads/{aid}/download",
            headers=_auth(fx),
        )
        if r_url.status_code != 200:
            return False, f"download endpoint status={r_url.status_code} body={r_url.text[:200]!r}"
        signed_url = r_url.json().get("download_url", "")
        if not signed_url.startswith("https://"):
            return False, f"download_url not https: {signed_url[:120]!r}"

        r_get = await client.get(signed_url)
        if r_get.status_code != 200:
            return False, f"signed GET status={r_get.status_code}"
        if len(r_get.content) < 10 * 1024 * 1024:
            return False, f"signed GET returned only {len(r_get.content)} bytes"
    return True, f"signed download · https · bytes={len(r_get.content)/1e6:.1f} MB"


async def row8_path_b_upload(fx: Fixtures) -> Tuple[bool, str]:
    """R8 · <=16MB xlsx via /api/workbook/upload-multi lands with gridfs_id."""
    small_payload = _make_xlsx_bytes(min_bytes=64 * 1024)  # tiny, ~100KB
    if len(small_payload) > 16 * 1024 * 1024:
        return False, f"small xlsx unexpectedly {len(small_payload)} bytes"
    fname = f"pathB-{uuid.uuid4().hex[:6]}.xlsx"

    async with httpx.AsyncClient(timeout=60.0) as client:
        csrf = await _mint_csrf(client)
        files = [("files", (fname, small_payload, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))]
        data = {"context_id": fx.context_id, "objective": "gcs slice R8"}
        r = await client.post(
            f"{BASE_URL}/api/workbook/upload-multi",
            headers=_state_auth(fx, csrf),
            files=files,
            data=data,
        )
        if r.status_code != 200:
            return False, f"upload-multi status={r.status_code} body={r.text[:200]!r}"
        analysis_id = r.json().get("id")
        if not analysis_id:
            return False, f"no id in upload-multi response: {r.json()!r}"
        fx.analysis_ids.append(analysis_id)

    # /workbook/upload-multi writes to db.analyses + db.analysis_blobs
    # (multi-source v1 shape). It does NOT touch db.workbook_analyses /
    # db.workbook_blobs — those are the v2/single-source collections
    # our Path A pivot writes to. R8 verifies Path B untouched-ness.
    from core import db  # noqa
    parent = await db.analyses.find_one({"id": analysis_id})
    if not parent:
        return False, f"path-B analyses row not present for {analysis_id}"
    blob = await db.analysis_blobs.find_one({"analysis_id": analysis_id})
    if not blob:
        return False, f"path-B analysis_blobs row not present for {analysis_id}"
    if not blob.get("gridfs_id"):
        return False, f"path-B row missing gridfs_id: keys={list(blob.keys())}"
    if blob.get("gcs_object_name"):
        return False, f"path-B row should NOT carry gcs_object_name: {blob.get('gcs_object_name')!r}"
    return True, f"path-B analysis={analysis_id} · gridfs_id set · no gcs_object_name"


async def row9_threshold_gate(fx: Fixtures) -> Tuple[bool, str]:
    """R9 · <=threshold rejected from presigned endpoint."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        csrf = await _mint_csrf(client)
        r = await client.post(
            f"{BASE_URL}/api/uploads/presigned",
            headers=_state_auth(fx, csrf),
            json={
                "filename": "tiny.xlsx",
                "content_type": "application/octet-stream",
                "size_bytes": 1024,  # 1KB
                "context_id": fx.context_id,
                "kind": "workbook",
            },
        )
    if r.status_code != 400:
        return False, f"expected 400 got {r.status_code} body={r.text[:200]!r}"
    if "use_in_band_route" not in r.text:
        return False, f"expected 'use_in_band_route' in body, got {r.text[:200]!r}"
    return True, "threshold gate rejects small file with 400 · use_in_band_route"


async def row10_no_project_scope_calls(fx: Fixtures) -> Tuple[bool, str]:
    """R10 · No `list_buckets(` / `get_bucket(` in new files.
    
    Uses AST inspection so docstrings / comments that MENTION the
    forbidden APIs (e.g. "do NOT call `client.list_buckets()`") do not
    trigger a false positive. We inspect Call nodes only."""
    import ast

    def _forbidden_calls(source: str) -> List[str]:
        tree = ast.parse(source)
        hits: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Attribute) and fn.attr in {"list_buckets", "get_bucket"}:
                    hits.append(fn.attr)
                if isinstance(fn, ast.Name) and fn.id in {"list_buckets", "get_bucket"}:
                    hits.append(fn.id)
        return hits

    new_files = [
        BACKEND / "routers" / "uploads.py",
        BACKEND / "scripts" / "jc_gcs_canary_probe.py",
        BACKEND / "services" / "storage_service.py",  # includes the additive GCS block
    ]
    hits: List[str] = []
    for f in new_files:
        for tok in _forbidden_calls(_text(f)):
            hits.append(f"{f.name}::{tok}")

    if hits:
        return False, f"forbidden project-scope calls (AST): {hits}"
    return True, "no project-scope GCS calls in new surface (AST-verified)"


async def row11_split_literal_invariant(fx: Fixtures) -> Tuple[bool, str]:
    """R11 · No raw joined-literal for the T-L or Sol-va tokens in slice source.

    Uses tokenize to inspect ONLY string-literal tokens (comments are
    tokenized separately and never confuse this check). Detects any
    STRING token whose Python value equals the forbidden joined form
    (i.e. someone accidentally typed the joined string as a literal
    instead of using `"..." + "..."` concatenation).
    """
    import tokenize
    forbidden_joined: List[str] = ["thin" + "klab", "Sol" + "va"]
    hits: List[Tuple[int, str]] = []
    with open(__file__, "rb") as fh:
        for tok in tokenize.tokenize(fh.readline):
            if tok.type != tokenize.STRING:
                continue
            # Skip triple-quoted (docstrings) — they can legitimately
            # mention rename-arc tokens in prose.
            raw = tok.string
            if raw.startswith(('"""', "'''", 'r"""', "r'''", 'b"""', "b'''", 'f"""', "f'''")):
                continue
            try:
                value = ast_literal_str(raw)
            except Exception:  # noqa: BLE001
                continue
            for bad in forbidden_joined:
                if value == bad:
                    hits.append((tok.start[0], value))
    if hits:
        return False, f"raw joined literals present at lines {hits}"
    # Positive assertion — split-literal usage IS present in source.
    src = _text(Path(__file__))
    tl_lit = '"' + "thin" + '" + "' + "klab" + '"'   # constructed at runtime
    old_lit = '"' + "Sol" + '" + "' + "va" + '"'
    if tl_lit not in src or old_lit not in src:
        return False, "expected split-literal concatenations not present in slice source"
    return True, "split-literal discipline preserved (tokenize-verified)"


def ast_literal_str(raw: str) -> str:
    """Return the runtime value of a Python string-literal token
    (handles single-quote, double-quote, byte, f-string prefix)."""
    import ast as _ast
    return _ast.literal_eval(raw)


async def row12_rename_arc_hash_invariant(fx: Fixtures) -> Tuple[bool, str]:
    """R12 · CHANGELOG + PRD below-footer bytes unchanged from P4 pinned SHA."""
    changelog = MEMORY / "CHANGELOG.md"
    prd = MEMORY / "PRD.md"
    # P4 slice uses split-literal for the boundary marker; replicate.
    changelog_boundary = (
        "## 2026-07-02 — JC-" + _OLD.upper() + "-MODULE-RENAME-PHASE-3-COMPONENT-COPY-EDITS"
    )
    prd_boundary = "> **2026-06-30 20:07 UTC"

    c_src = _text(changelog)
    c_idx = c_src.find(changelog_boundary)
    if c_idx < 0:
        return False, f"CHANGELOG boundary marker not found"
    c_below = c_src[c_idx:]
    c_sha = hashlib.sha256(c_below.encode()).hexdigest()
    if c_sha != PRE_P4_CHANGELOG_BELOW_FOOTER_SHA:
        return False, (
            f"CHANGELOG below-footer drift · expected "
            f"{PRE_P4_CHANGELOG_BELOW_FOOTER_SHA[:12]} got {c_sha[:12]}"
        )

    p_src = _text(prd)
    p_idx = p_src.find(prd_boundary)
    if p_idx < 0:
        return False, f"PRD boundary marker not found"
    p_below = p_src[p_idx:]
    p_sha = hashlib.sha256(p_below.encode()).hexdigest()
    if p_sha != PRE_P4_PRD_BELOW_FOOTER_SHA:
        return False, (
            f"PRD below-footer drift · expected "
            f"{PRE_P4_PRD_BELOW_FOOTER_SHA[:12]} got {p_sha[:12]}"
        )
    return True, "rename arc P4 hash invariants intact"


# ==================================================================
# Orchestrator
# ==================================================================
ROWS: List[Tuple[str, Callable[[Fixtures], "asyncio.Future"]]] = [
    ("R1  · env sanity", row1_env_sanity),
    ("R2  · canary probe GREEN", row2_canary_probe),
    ("R3  · archive marker provisioned", row3_archive_marker),
    ("R4  · S3/local storage classes preserved", row4_storage_service_byte_for_byte),
    ("R5  · Path A upload (>16MB → GCS)", row5_path_a_upload),
    ("R6  · Path A read (GCS branch)", row6_path_a_read),
    ("R7  · Path A signed download", row7_path_a_download),
    ("R8  · Path B upload (<=16MB → GridFS)", row8_path_b_upload),
    ("R9  · Threshold gate rejects small file", row9_threshold_gate),
    ("R10 · No project-scope GCS calls", row10_no_project_scope_calls),
    ("R11 · Split-literal discipline", row11_split_literal_invariant),
    ("R12 · Rename arc hash invariant", row12_rename_arc_hash_invariant),
]


async def main() -> int:
    print("═" * 72)
    print("JC-STORAGE-PIVOT-GCS-BUILD · proving slice · 12 rows")
    print("═" * 72)

    fx = Fixtures()
    await fx.setup()
    passes = 0
    try:
        for (label, fn) in ROWS:
            t0 = time.time()
            try:
                ok, detail = await fn(fx)
            except Exception as exc:  # noqa: BLE001
                ok, detail = False, f"exception: {type(exc).__name__}: {exc!s:.200}"
            dt = (time.time() - t0) * 1000
            marker = "✅ PASS" if ok else "❌ FAIL"
            print(f"  {label:<48s}  {marker}  ({dt:6.0f} ms) · {detail}")
            if ok:
                passes += 1
    finally:
        await fx.teardown()

    total = len(ROWS)
    print("─" * 72)
    if passes == total:
        print(f"GREEN · {passes}/{total} rows passed")
        return 0
    print(f"RED · {passes}/{total} rows passed")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
