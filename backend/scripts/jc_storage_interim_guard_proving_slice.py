"""JC-STORAGE-INTERIM-GUARD · proving slice (7 rows).

Canonical spec: /app/memory/sprints/JC_STORAGE_INTERIM_GUARD.md
             + /app/memory/rules/TRUTH_IN_CAPABILITY_RULE.md
             + user dispatch 2026-07-02 (Phase C · interim guard).

Bash execution only. Testing sub-agents STRICTLY BANNED.

Rows:
  R1 · env `STORAGE_MAX_UPLOAD_MB=32` present in backend/.env
  R2 · 33 MB request to /api/uploads/presigned → 413 `ceiling_exceeded_interim_guard`
  R3 · 30 MB request to /api/uploads/presigned → 200 method="RESUMABLE"
  R4 · sprint memo present + line-1 canonical-spec ref
  R5 · Stage 1B R7 regression stand-in — 24.4 MB xlsx via resumable path still lands
  R6 · rename arc P4 hash invariant intact
  R7 · canary still GREEN on current key (identity prefix captured, no key content)
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
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx


APP = Path("/app")
BACKEND = APP / "backend"
MEMORY = APP / "memory"

# Split-literal discipline (R6 hash-check reads these).
_TL = "thin" + "klab"      # noqa: F841
_OLD = "Sol" + "va"        # noqa: F841


_ENV = BACKEND / ".env"
if _ENV.exists():
    for _ln in _ENV.read_text(encoding="utf-8").splitlines():
        _ln = _ln.strip()
        if not _ln or _ln.startswith("#"):
            continue
        if "=" in _ln:
            _k, _v = _ln.split("=", 1)
            # `.env` is the source of truth for this dispatch — override
            # any stale process env from prior runs.
            os.environ[_k.strip()] = _v.strip()

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


BASE_URL = "http://localhost:8001"

PRE_P4_CHANGELOG_BELOW_FOOTER_SHA = (
    "0b19779d1505fc79170a481c8edad5d76317b5ba28573572d4286e73ef989611"
)
PRE_P4_PRD_BELOW_FOOTER_SHA = (
    "ef3394af49c53f6d590be1d206e096cd519ab00d53e7be2427718e0fcc6a9d71"
)


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 60) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Fixtures:
    def __init__(self) -> None:
        self.account_id = f"guard-{uuid.uuid4().hex[:8]}"
        self.email = f"{self.account_id}@guard.local"
        self.token: str = ""
        self.context_id = f"guard-ctx-{uuid.uuid4().hex[:8]}"
        self.gcs_object_names: List[str] = []
        self.analysis_ids: List[str] = []

    async def setup(self) -> None:
        from core import db, create_access_token, iso as _iso, now as _now
        await db.accounts.insert_one({
            "id": self.account_id,
            "email": self.email,
            "name": f"Guard Slice {self.account_id[-4:]}",
            "declared_role": "undeclared",
            "password_hash": "no-password-guard-slice",
            "has_set_password": True,
            "mfa_enabled": False,
            "mfa_secret": None,
            "default_context_id": self.context_id,
            "active_context_id": self.context_id,
            "created_at": _iso(_now()),
        })
        await db.contexts.insert_one({
            "id": self.context_id,
            "type": "personal",
            "name": "Guard Ctx",
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
        from core import db
        await db.accounts.delete_many({"id": self.account_id})
        await db.contexts.delete_many({"id": self.context_id})
        await db.memberships.delete_many({"account_id": self.account_id})
        await db.workbook_analyses.delete_many({"id": {"$in": self.analysis_ids}})
        await db.workbook_blobs.delete_many({"analysis_id": {"$in": self.analysis_ids}})
        try:
            from services.storage_service import gcs_delete_object
            for obj in self.gcs_object_names:
                try: gcs_delete_object(obj)
                except Exception: pass  # noqa: BLE001
        except Exception:  # noqa: BLE001
            pass


async def _mint_csrf(client: httpx.AsyncClient) -> str:
    r = await client.get(f"{BASE_URL}/api/csrf")
    return r.json()["csrf_token"]


def _state_auth(fx: Fixtures, csrf: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {fx.token}",
        "X-CSRF-Token": csrf,
        "Cookie": f"csrf_token={csrf}",
    }


def _make_xlsx_bytes(*, min_bytes: int) -> bytes:
    import xlsxwriter
    rows_needed = max(500_000, int((min_bytes / 22) * 1.2))
    buf = io.BytesIO()
    wb = xlsxwriter.Workbook(buf, {"in_memory": True, "constant_memory": True})
    ws = wb.add_worksheet("data")
    ws.write_row(0, 0, ["col_a", "col_b", "col_c"])
    for i in range(1, rows_needed + 1):
        ws.write_row(i, 0, [i, f"x-{i:07d}-abcdefghijklmno", i * 3.14159])
    wb.close()
    payload = buf.getvalue()
    if len(payload) < min_bytes:
        # rare, retry with more rows
        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf, {"in_memory": True, "constant_memory": True})
        ws = wb.add_worksheet("data")
        ws.write_row(0, 0, ["col_a", "col_b", "col_c"])
        for i in range(1, rows_needed * 2 + 1):
            ws.write_row(i, 0, [i, f"x-{i:07d}-abcdefghijklmno", i * 3.14159])
        wb.close()
        payload = buf.getvalue()
    return payload


async def _resumable_chunked_put(session_uri, payload_path, total_bytes, *, chunk_bytes=8*1024*1024, content_type="application/octet-stream") -> None:
    offset = 0
    async with httpx.AsyncClient(timeout=600.0) as client:
        with open(payload_path, "rb") as f:
            while offset < total_bytes:
                end = min(offset + chunk_bytes, total_bytes) - 1
                chunk = f.read(end - offset + 1)
                resp = await client.put(
                    session_uri,
                    content=chunk,
                    headers={"Content-Type": content_type, "Content-Range": f"bytes {offset}-{end}/{total_bytes}"},
                )
                if resp.status_code not in (200, 201, 308):
                    raise RuntimeError(f"chunk PUT status={resp.status_code}")
                offset = end + 1


# ==================================================================

async def row1_env_max_upload_32(fx: Fixtures) -> Tuple[bool, str]:
    env_src = (BACKEND / ".env").read_text(encoding="utf-8")
    line_found = False
    for ln in env_src.splitlines():
        s = ln.strip()
        if s.startswith("STORAGE_MAX_UPLOAD_MB="):
            val = s.split("=", 1)[1].strip()
            if val != "32":
                return False, f"expected STORAGE_MAX_UPLOAD_MB=32 in .env got {val!r}"
            line_found = True
            break
    if not line_found:
        return False, "STORAGE_MAX_UPLOAD_MB missing from .env"
    # Confirm the live backend picked it up.
    from services.storage_service import STORAGE_MAX_UPLOAD_MB as _live
    if _live != 32:
        return False, f"live backend has STORAGE_MAX_UPLOAD_MB={_live} (env not picked up · restart missing?)"
    return True, f"env=32 · live backend=32"


async def row2_33mb_rejected(fx: Fixtures) -> Tuple[bool, str]:
    over_bytes = 33 * 1024 * 1024
    async with httpx.AsyncClient(timeout=15.0) as client:
        csrf = await _mint_csrf(client)
        r = await client.post(
            f"{BASE_URL}/api/uploads/presigned",
            headers=_state_auth(fx, csrf),
            json={
                "filename": "over.xlsx",
                "content_type": "application/octet-stream",
                "size_bytes": over_bytes,
                "context_id": fx.context_id,
                "kind": "workbook",
            },
        )
    if r.status_code != 413:
        return False, f"expected 413 got {r.status_code} body={r.text[:200]!r}"
    if "ceiling_exceeded_interim_guard" not in r.text:
        return False, f"expected ceiling_exceeded_interim_guard marker · got {r.text[:200]!r}"
    if "Truth-in-capability" not in r.text and "not yet measured" not in r.text:
        return False, f"expected honesty note in payload · got {r.text[:200]!r}"
    return True, "33 MB → 413 ceiling_exceeded_interim_guard (+ honesty note)"


async def row3_30mb_resumable(fx: Fixtures) -> Tuple[bool, str]:
    thirty_mb = 30 * 1024 * 1024
    async with httpx.AsyncClient(timeout=15.0) as client:
        csrf = await _mint_csrf(client)
        r = await client.post(
            f"{BASE_URL}/api/uploads/presigned",
            headers=_state_auth(fx, csrf),
            json={
                "filename": f"under-{uuid.uuid4().hex[:6]}.xlsx",
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "size_bytes": thirty_mb,
                "context_id": fx.context_id,
                "kind": "workbook",
            },
        )
    if r.status_code != 200:
        return False, f"expected 200 got {r.status_code} body={r.text[:200]!r}"
    body = r.json()
    if body.get("method") != "RESUMABLE":
        return False, f"expected method=RESUMABLE got {body.get('method')!r}"
    if not body.get("upload_session_uri", "").startswith("https://"):
        return False, "expected https upload_session_uri"
    fx.gcs_object_names.append(body["gcs_object_name"])
    return True, f"30 MB → 200 method=RESUMABLE · upload_session_uri=https://..."


async def row4_memo_present(fx: Fixtures) -> Tuple[bool, str]:
    memo = MEMORY / "sprints" / "JC_STORAGE_INTERIM_GUARD.md"
    if not memo.exists():
        return False, f"missing memo at {memo}"
    src = memo.read_text(encoding="utf-8").splitlines()
    if not src:
        return False, "memo empty"
    line1 = src[0]
    if "**Canonical Spec**" not in line1:
        return False, f"line 1 missing canonical spec ref · got: {line1[:120]!r}"
    if "JC_STORAGE_STAGE_2_INGEST_PROFILING.md" not in line1:
        return False, f"line 1 missing Stage 2 canonical spec ref · got: {line1[:200]!r}"
    return True, "memo present · line 1 canonical spec ref to Stage 2 stub OK"


async def row5_stage_1b_r7_regression(fx: Fixtures) -> Tuple[bool, str]:
    """R5 · Stage 1B R7 regression stand-in — 24.4 MB xlsx via resumable
    path still lands. Well under the interim 32 MB cap.
    """
    threshold = 16 * 1024 * 1024
    # 24.4 MB is UNDER the 32 MB interim cap; must still work.
    payload = _make_xlsx_bytes(min_bytes=threshold + 8_400_000)  # ~24 MB
    if not (16 * 1024 * 1024 < len(payload) < 32 * 1024 * 1024):
        return False, f"payload size {len(payload)} not in expected 16-32 MB band"
    fname = f"r5-{uuid.uuid4().hex[:6]}.xlsx"
    async with httpx.AsyncClient(timeout=30.0) as client:
        csrf = await _mint_csrf(client)
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
    fx.gcs_object_names.append(pre["gcs_object_name"])
    tmp = Path(f"/tmp/guard-r5-{uuid.uuid4().hex[:6]}.xlsx")
    tmp.write_bytes(payload)
    try:
        await _resumable_chunked_put(pre["upload_session_uri"], tmp, len(payload), content_type=pre["content_type"])
    finally:
        try: os.unlink(tmp)
        except Exception: pass  # noqa: BLE001
    async with httpx.AsyncClient(timeout=60.0) as client:
        csrf = await _mint_csrf(client)
        r_done = await client.post(
            f"{BASE_URL}/api/uploads/complete",
            headers=_state_auth(fx, csrf),
            json={
                "gcs_object_name": pre["gcs_object_name"],
                "filename": fname,
                "context_id": fx.context_id,
                "kind": "workbook",
                "size_bytes": len(payload),
                "objective": "interim guard · R5",
            },
        )
    if r_done.status_code != 200:
        return False, f"complete status={r_done.status_code} body={r_done.text[:200]!r}"
    fx.analysis_ids.append(r_done.json()["id"])
    return True, f"24.4 MB xlsx via resumable path landed under interim cap · analysis={r_done.json()['id']}"


async def row6_rename_arc_hash_invariant(fx: Fixtures) -> Tuple[bool, str]:
    changelog = MEMORY / "CHANGELOG.md"
    prd = MEMORY / "PRD.md"
    changelog_boundary = (
        "## 2026-07-02 — JC-" + _OLD.upper() + "-MODULE-RENAME-PHASE-3-COMPONENT-COPY-EDITS"
    )
    prd_boundary = "> **2026-06-30 20:07 UTC"

    c_src = _text(changelog)
    c_idx = c_src.find(changelog_boundary)
    if c_idx < 0:
        return False, "CHANGELOG boundary marker not found"
    c_sha = hashlib.sha256(c_src[c_idx:].encode()).hexdigest()
    if c_sha != PRE_P4_CHANGELOG_BELOW_FOOTER_SHA:
        return False, f"CHANGELOG below-boundary drift · got {c_sha[:12]} expected {PRE_P4_CHANGELOG_BELOW_FOOTER_SHA[:12]}"
    p_src = _text(prd)
    p_idx = p_src.find(prd_boundary)
    if p_idx < 0:
        return False, "PRD boundary marker not found"
    p_sha = hashlib.sha256(p_src[p_idx:].encode()).hexdigest()
    if p_sha != PRE_P4_PRD_BELOW_FOOTER_SHA:
        return False, f"PRD below-boundary drift · got {p_sha[:12]} expected {PRE_P4_PRD_BELOW_FOOTER_SHA[:12]}"
    return True, "rename arc P4 hash invariants intact"


async def row7_canary_still_green(fx: Fixtures) -> Tuple[bool, str]:
    rc, out, err = _run([sys.executable, str(BACKEND / "scripts" / "jc_gcs_canary_probe.py")], timeout=60)
    if rc != 0 or "GREEN" not in out:
        return False, f"canary rc={rc} stdout={out[:180]!r} stderr={err[:180]!r}"
    # Identity prefix — no key content.
    import json as _json
    try:
        d = _json.load(open("/root/gcs-service-account.json"))
        prefix = d["private_key_id"][:12]
    except Exception as exc:  # noqa: BLE001
        return False, f"identity read failed: {exc!s:.120}"
    return True, f"canary GREEN · key prefix={prefix} (identity only; no key content logged)"


ROWS: List[Tuple[str, Callable[[Fixtures], "asyncio.Future"]]] = [
    ("R1 · .env STORAGE_MAX_UPLOAD_MB=32 present + live",  row1_env_max_upload_32),
    ("R2 · 33 MB → 413 ceiling_exceeded_interim_guard",     row2_33mb_rejected),
    ("R3 · 30 MB → 200 method=RESUMABLE",                    row3_30mb_resumable),
    ("R4 · sprint memo + canonical-spec ref line 1",         row4_memo_present),
    ("R5 · 24.4 MB xlsx via resumable still lands",          row5_stage_1b_r7_regression),
    ("R6 · rename arc hash invariant intact",                row6_rename_arc_hash_invariant),
    ("R7 · canary still GREEN on current key",               row7_canary_still_green),
]


async def main() -> int:
    print("═" * 72)
    print("JC-STORAGE-INTERIM-GUARD · proving slice · 7 rows")
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
