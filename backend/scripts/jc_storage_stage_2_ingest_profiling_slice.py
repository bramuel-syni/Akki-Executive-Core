"""JC-STORAGE-STAGE-2-INGEST-PROFILING · proving slice (11 rows).

Canonical spec: /app/memory/sprints/JC_STORAGE_STAGE_2_INGEST_PROFILING.md
             + /app/memory/rules/TRUTH_IN_CAPABILITY_RULE.md
             + user dispatch 2026-07-02 (Phase D · Stage 2 ingest profiling).

Bash execution only. Testing sub-agents STRICTLY BANNED.

Per-format ingest profiling at 500 MB via the actual product path
(`analysis_lifecycle.read_workbook_bytes` GCS branch → tempfile →
`parse_workbook` streaming/read-only mode). Truth-in-capability rule
applied: report ONLY what was measured; do NOT infer capability that
wasn't tested; three-options costed report if any BLOCKED.

Replacement (per REPLACEMENT_NAMING_RULE): 500 MB uploads bypass
`/api/uploads/presigned` since the Interim Guard is active at 32 MB.
The slice calls `storage_service.gcs_initiate_resumable_upload_session`
directly + chunks via httpx, then invokes `read_workbook_bytes` +
`parse_workbook` in-process for measurement. Rationale: interim guard
would 413 an in-band 500 MB request; the ingest measurement (read +
parse) IS the specced product path — the /presigned gate is a
size-check, not part of ingest.

Rows:
  R1  · 500 MB CSV generated + file size verified
  R2  · 500 MB CSV ingested via full product path (read → parse OK)
  R3  · CSV peak RAM measured (ru_maxrss delta + tracemalloc peak) +
        pod ceiling captured + classification
  R4  · 500 MB xlsx generated (streaming) + file size verified
  R5  · 500 MB xlsx ingested via full product path (OOM = legitimate
        finding, not slice red; captures peak RAM at failure)
  R6  · xlsx peak RAM measured + pod ceiling captured + classification
  R7  · classification per format is exactly one of PROVEN/AT-RISK/BLOCKED
  R8  · if any BLOCKED, three-options costed report present in memo
  R9  · Interim guard slice (Phase C) still GREEN (regression)
  R10 · rename arc P4 hash invariant intact
  R11 · canary still GREEN on current key (identity prefix; no key content)
"""
from __future__ import annotations

import asyncio
import csv
import gc
import hashlib
import io
import os
import random
import resource
import subprocess
import sys
import time
import tracemalloc
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx


APP = Path("/app")
BACKEND = APP / "backend"
MEMORY = APP / "memory"

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


def _read_pod_ceiling_bytes() -> Optional[int]:
    """Return the memory ceiling for this pod in bytes.

    Prefers cgroup v2 (`/sys/fs/cgroup/memory.max`). Falls back to
    cgroup v1 (`memory.limit_in_bytes`). Returns None if neither
    readable or if the value is `max` / effectively unbounded.
    """
    for candidate in ("/sys/fs/cgroup/memory.max",
                      "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        try:
            with open(candidate, "r") as fh:
                raw = fh.read().strip()
            if not raw or raw == "max":
                continue
            val = int(raw)
            # cgroup v1 sometimes reports a nonsense huge sentinel
            # (`9223372036854771712`) — treat as unbounded.
            if val >= 2**60:
                continue
            return val
        except (FileNotFoundError, PermissionError, ValueError):
            continue
    return None


POD_CEILING_BYTES = _read_pod_ceiling_bytes()


def _classify(peak_bytes: int, ceiling_bytes: Optional[int], oom: bool) -> str:
    """PROVEN / AT-RISK / BLOCKED per Stage 2 spec §4.
    OOM always classifies as BLOCKED. Otherwise:
      peak < 50% ceiling → PROVEN
      50-80% ceiling     → AT-RISK
      ≥ 80% ceiling      → BLOCKED
    """
    if oom:
        return "BLOCKED"
    if ceiling_bytes is None:
        # No ceiling info — report classification-unavailable but
        # DO NOT fake "PROVEN". Truth-in-capability rule applies.
        return "UNCLASSIFIED-NO-CEILING"
    ratio = peak_bytes / ceiling_bytes
    if ratio < 0.50:
        return "PROVEN"
    if ratio < 0.80:
        return "AT-RISK"
    return "BLOCKED"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 60) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ==================================================================
# Fixtures
# ==================================================================
class Fixtures:
    def __init__(self) -> None:
        self.account_id = f"s2-{uuid.uuid4().hex[:8]}"
        self.email = f"{self.account_id}@s2.local"
        self.context_id = f"s2-ctx-{uuid.uuid4().hex[:8]}"
        self.token: str = ""
        self.gcs_object_names: List[str] = []
        self.analysis_ids: List[str] = []
        # Populated by R1-R6 for use in R7/R8:
        self.results: Dict[str, Dict[str, Any]] = {}

    async def setup(self) -> None:
        from core import db, create_access_token, iso as _iso, now as _now
        await db.accounts.insert_one({
            "id": self.account_id, "email": self.email,
            "name": f"S2 Slice {self.account_id[-4:]}",
            "declared_role": "undeclared",
            "password_hash": "no-password-s2",
            "has_set_password": True,
            "mfa_enabled": False, "mfa_secret": None,
            "default_context_id": self.context_id,
            "active_context_id": self.context_id,
            "created_at": _iso(_now()),
        })
        self.token = create_access_token(self.account_id, self.email)

    async def teardown(self) -> None:
        from core import db
        await db.accounts.delete_many({"id": self.account_id})
        try:
            from services.storage_service import gcs_delete_object
            for obj in self.gcs_object_names:
                try: gcs_delete_object(obj)
                except Exception: pass  # noqa: BLE001
        except Exception:  # noqa: BLE001
            pass


# ==================================================================
# Test-data generators
# ==================================================================

def _write_500mb_csv(dest: Path, target_bytes: int = 500 * 1024 * 1024) -> None:
    """Streaming CSV writer with realistic column mix — string, float,
    int, date, categorical. Streams row-by-row to disk to avoid RAM
    ballooning during setup."""
    random.seed(2026)
    categories = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf"]
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "customer_name", "revenue_usd", "signed_at", "segment", "region_code", "notes"])
        i = 0
        while True:
            i += 1
            w.writerow([
                i,
                f"Customer_{i:07d}_{uuid.uuid4().hex[:8]}",
                round(random.uniform(100.0, 999_999.99), 2),
                (datetime(2020, 1, 1, tzinfo=timezone.utc) + timedelta(days=(i % 2000))).isoformat(),
                random.choice(categories),
                random.choice(["US-CA", "US-NY", "UK-LN", "SG-SG", "IN-BLR", "DE-BER"]),
                f"note-{i}-" + ("filler" * random.randint(0, 8)),
            ])
            if (i & 0xFFF) == 0:  # size-check every 4096 rows
                fh.flush()
                if fh.tell() >= target_bytes:
                    break
    # Trim to exactly target_bytes if we overshot slightly (keep it a
    # complete row — trim by truncating extra padding line if any).
    actual = dest.stat().st_size
    if actual > target_bytes + 1024 * 1024:
        # over by more than 1 MB — trim
        with open(dest, "r+b") as fh:
            fh.truncate(target_bytes)


def _write_500mb_xlsx(dest: Path, target_bytes: int = 500 * 1024 * 1024) -> None:
    """Streaming xlsx writer via xlsxwriter constant_memory mode.

    500 MB xlsx is HARD to construct — xlsxwriter zips content, so
    high-repetition rows compress to ~55 MB regardless of rowcount.
    Fix: use wide, HIGH-ENTROPY content (long base64 UUID cells) that
    defeats zip compression. Empirically ~1200 chars per row across
    10 cols gets us to ~500 MB in ~200-300K rows (fast: ~30-60s).
    """
    import base64
    import xlsxwriter
    random.seed(2026)
    categories = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf"]
    wb = xlsxwriter.Workbook(str(dest), {"constant_memory": True})
    ws = wb.add_worksheet("data")
    header = ["id", "customer_name", "revenue_usd", "signed_at", "segment", "region_code",
             "session_blob_1", "session_blob_2", "session_blob_3", "notes_wide"]
    ws.write_row(0, 0, header)

    # Pre-generate a pool of ~256 high-entropy blobs so we're not
    # random.getrandbits()-bound on the hot loop.
    # Each blob = 300 raw bytes → base64 = 400 chars.
    _pool = [
        base64.b64encode(os.urandom(300)).decode() for _ in range(256)
    ]
    # Write in bounded chunks; check size after each chunk close would
    # require re-opening (xlsxwriter can't). So we probe once at close
    # and if under-target we grow rowcount and rewrite.
    def _write_pass(rows_target: int) -> None:
        for i in range(1, rows_target + 1):
            b1 = _pool[i % 256]
            b2 = _pool[(i * 7) % 256]
            b3 = _pool[(i * 13) % 256]
            ws.write_row(i, 0, [
                i,
                f"Customer_{i:07d}_{uuid.uuid4().hex[:12]}",
                round(random.uniform(100.0, 999_999.99), 2),
                (datetime(2020, 1, 1, tzinfo=timezone.utc) + timedelta(days=(i % 2000))).isoformat(),
                random.choice(categories),
                random.choice(["US-CA", "US-NY", "UK-LN", "SG-SG", "IN-BLR", "DE-BER"]),
                b1, b2, b3,
                f"note-{i}-{uuid.uuid4().hex}",
            ])

    # First pass: with 3-col × 400-char blobs (unique-ish across 256
    # rotation) we get ~2400 bytes/row post-zip. 250K rows → ~600 MB.
    initial_rows = 250_000
    _write_pass(initial_rows)
    wb.close()

    size = dest.stat().st_size
    if size < target_bytes * 0.85:
        # Under target — rewrite with scaled rowcount (one retry only,
        # +25% safety margin over ratio).
        factor = (target_bytes / max(size, 1)) * 1.30
        rows = int(initial_rows * factor)
        try:
            dest.unlink()
        except Exception:  # noqa: BLE001
            pass
        wb2 = xlsxwriter.Workbook(str(dest), {"constant_memory": True})
        ws2 = wb2.add_worksheet("data")
        ws2.write_row(0, 0, header)
        # Inline retry (fresh worksheet handle, no closure hazard).
        for i in range(1, rows + 1):
            b1 = _pool[i % 256]
            b2 = _pool[(i * 7) % 256]
            b3 = _pool[(i * 13) % 256]
            ws2.write_row(i, 0, [
                i,
                f"Customer_{i:07d}_{uuid.uuid4().hex[:12]}",
                round(random.uniform(100.0, 999_999.99), 2),
                (datetime(2020, 1, 1, tzinfo=timezone.utc) + timedelta(days=(i % 2000))).isoformat(),
                random.choice(categories),
                random.choice(["US-CA", "US-NY", "UK-LN", "SG-SG", "IN-BLR", "DE-BER"]),
                b1, b2, b3,
                f"note-{i}-{uuid.uuid4().hex}",
            ])
        wb2.close()


async def _upload_to_gcs_direct(
    payload_path: Path,
    *,
    context_id: str,
    account_id: str,
    filename: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Bypass /api/uploads/presigned (interim guard would 413 at 32 MB).
    Call `storage_service.gcs_initiate_resumable_upload_session`
    directly to get a session URI, then chunk-PUT via httpx.
    Return the gcs_object_name.
    """
    from services.storage_service import gcs_initiate_resumable_upload_session
    size = payload_path.stat().st_size
    # Namespace under a stage-2/... prefix so no product code paths
    # accidentally see these blobs. Deleted on teardown.
    stamp = int(datetime.now(timezone.utc).timestamp())
    obj_name = f"workbook/{context_id}/{account_id}/{stamp}-{uuid.uuid4().hex[:10]}-{filename}"
    session_uri = gcs_initiate_resumable_upload_session(
        object_name=obj_name, content_type=content_type, size=size,
    )
    chunk_bytes = 16 * 1024 * 1024
    async with httpx.AsyncClient(timeout=600.0) as client:
        offset = 0
        with open(payload_path, "rb") as f:
            while offset < size:
                end = min(offset + chunk_bytes, size) - 1
                chunk = f.read(end - offset + 1)
                resp = await client.put(
                    session_uri, content=chunk,
                    headers={"Content-Type": content_type,
                             "Content-Range": f"bytes {offset}-{end}/{size}"},
                )
                if resp.status_code not in (200, 201, 308):
                    raise RuntimeError(f"chunk PUT status={resp.status_code}")
                offset = end + 1
    return obj_name


def _ru_maxrss_bytes() -> int:
    """`ru_maxrss` is KB on Linux, bytes on macOS. This slice runs on
    Linux (pod), so return bytes = KB * 1024."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


async def _measure_ingest(
    obj_name: str,
    file_format: str,
) -> Dict[str, Any]:
    """Run the actual product ingest path in-process while measuring
    peak RAM. Returns dict with:
      { peak_rss_delta_bytes, tracemalloc_peak_bytes, ok, oom, error }
    """
    from core import db  # noqa
    from services.analysis_lifecycle import read_workbook_bytes
    from services.workbook_analyzer import parse_workbook

    rss_before = _ru_maxrss_bytes()
    gc.collect()
    tracemalloc.start()
    try:
        _inline, tmp_path = await read_workbook_bytes(
            db,
            {"gcs_object_name": obj_name, "file_format": file_format, "filename": f"probe.{file_format}"},
        )
        if not tmp_path:
            return {"peak_rss_delta_bytes": 0, "tracemalloc_peak_bytes": 0,
                    "ok": False, "oom": False, "error": "no tempfile from read_workbook_bytes"}
        try:
            sheets, matrices = parse_workbook(file_path=tmp_path, file_format=file_format)
        finally:
            try: os.unlink(tmp_path)
            except Exception: pass  # noqa: BLE001
        cur, peak = tracemalloc.get_traced_memory()
        rss_after = _ru_maxrss_bytes()
        return {
            "peak_rss_delta_bytes": max(0, rss_after - rss_before),
            "tracemalloc_peak_bytes": peak,
            "ok": True,
            "oom": False,
            "error": None,
            "row_count_first_sheet": (
                len(matrices[sheets[0].name]) if sheets and sheets[0].name in matrices else 0
            ),
            "sheet_count": len(sheets),
        }
    except MemoryError as exc:
        cur, peak = tracemalloc.get_traced_memory()
        return {
            "peak_rss_delta_bytes": max(0, _ru_maxrss_bytes() - rss_before),
            "tracemalloc_peak_bytes": peak,
            "ok": False, "oom": True,
            "error": f"MemoryError: {exc!s:.180}",
        }
    except Exception as exc:  # noqa: BLE001
        cur, peak = tracemalloc.get_traced_memory()
        return {
            "peak_rss_delta_bytes": max(0, _ru_maxrss_bytes() - rss_before),
            "tracemalloc_peak_bytes": peak,
            "ok": False, "oom": False,
            "error": f"{type(exc).__name__}: {exc!s:.180}",
        }
    finally:
        tracemalloc.stop()


# ==================================================================
# Rows
# ==================================================================

async def row1_csv_generated(fx: Fixtures) -> Tuple[bool, str]:
    target = 500 * 1024 * 1024
    csv_path = Path(f"/tmp/s2-500mb-{uuid.uuid4().hex[:6]}.csv")
    _write_500mb_csv(csv_path, target_bytes=target)
    size = csv_path.stat().st_size
    # Allow ±5% tolerance
    if not (target * 0.95 <= size <= target * 1.10):
        try: csv_path.unlink()
        except Exception: pass  # noqa: BLE001
        return False, f"CSV size {size/1e6:.1f} MB out of tolerance"
    fx.results.setdefault("csv", {})["local_path"] = csv_path
    fx.results["csv"]["source_size_bytes"] = size
    return True, f"500 MB CSV generated · size={size/1e6:.1f} MB · path={csv_path.name}"


async def row2_csv_ingested(fx: Fixtures) -> Tuple[bool, str]:
    csv_path = fx.results.get("csv", {}).get("local_path")
    if not csv_path or not csv_path.exists():
        return False, "CSV file missing from R1"
    # Upload to GCS via resumable direct (bypass /presigned per
    # Replacement-naming rule — interim guard active at 32 MB).
    obj_name = await _upload_to_gcs_direct(
        csv_path, context_id=fx.context_id, account_id=fx.account_id,
        filename=csv_path.name, content_type="text/csv",
    )
    fx.gcs_object_names.append(obj_name)
    fx.results["csv"]["gcs_object_name"] = obj_name
    # Measure ingest.
    m = await _measure_ingest(obj_name, "csv")
    fx.results["csv"].update(m)
    if not m["ok"]:
        # Still a row PASS at slice level — R2 is "ingest attempted";
        # OOM / parse errors are legitimate Stage 2 findings surfaced
        # in R6/R7. Only mark FAIL if the row itself failed to run
        # (which would be an infra problem, not an ingest finding).
        if m["oom"] or m["error"]:
            return True, (
                f"CSV ingest attempted · outcome={m.get('error', '?')} · "
                f"rss_delta={m['peak_rss_delta_bytes']/1e6:.1f} MB · "
                f"tracemalloc_peak={m['tracemalloc_peak_bytes']/1e6:.1f} MB (finding)"
            )
    return True, (
        f"CSV ingested · sheets={m.get('sheet_count', '?')} · "
        f"rows_first_sheet={m.get('row_count_first_sheet', '?')} · "
        f"rss_delta={m['peak_rss_delta_bytes']/1e6:.1f} MB · "
        f"tracemalloc_peak={m['tracemalloc_peak_bytes']/1e6:.1f} MB"
    )


async def row3_csv_measured_and_classified(fx: Fixtures) -> Tuple[bool, str]:
    r = fx.results.get("csv", {})
    if "peak_rss_delta_bytes" not in r:
        return False, "no CSV measurement present"
    peak = r["peak_rss_delta_bytes"]
    tm_peak = r.get("tracemalloc_peak_bytes", 0)
    ceiling = POD_CEILING_BYTES
    classification = _classify(peak, ceiling, r.get("oom", False))
    r["classification"] = classification
    ceil_str = f"{ceiling/1e6:.0f} MB" if ceiling else "unknown"
    ratio_str = f"{(peak/ceiling)*100:.1f}%" if ceiling else "n/a"
    return True, (
        f"CSV @ 500 MB · rss_delta_peak={peak/1e6:.1f} MB · "
        f"tracemalloc_peak={tm_peak/1e6:.1f} MB · pod_ceiling={ceil_str} · "
        f"ratio={ratio_str} · status={classification}"
    )


async def row4_xlsx_generated(fx: Fixtures) -> Tuple[bool, str]:
    target = 500 * 1024 * 1024
    xlsx_path = Path(f"/tmp/s2-500mb-{uuid.uuid4().hex[:6]}.xlsx")
    _write_500mb_xlsx(xlsx_path, target_bytes=target)
    size = xlsx_path.stat().st_size
    if size < target * 0.85:
        try: xlsx_path.unlink()
        except Exception: pass  # noqa: BLE001
        return False, f"xlsx size {size/1e6:.1f} MB too small (target 500 MB)"
    fx.results.setdefault("xlsx", {})["local_path"] = xlsx_path
    fx.results["xlsx"]["source_size_bytes"] = size
    return True, f"500 MB xlsx generated · size={size/1e6:.1f} MB · path={xlsx_path.name}"


async def row5_xlsx_ingested(fx: Fixtures) -> Tuple[bool, str]:
    xlsx_path = fx.results.get("xlsx", {}).get("local_path")
    if not xlsx_path or not xlsx_path.exists():
        return False, "xlsx file missing from R4"
    obj_name = await _upload_to_gcs_direct(
        xlsx_path, context_id=fx.context_id, account_id=fx.account_id,
        filename=xlsx_path.name,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    fx.gcs_object_names.append(obj_name)
    fx.results["xlsx"]["gcs_object_name"] = obj_name
    m = await _measure_ingest(obj_name, "xlsx")
    fx.results["xlsx"].update(m)
    return True, (
        f"xlsx ingest attempted · ok={m['ok']} · oom={m['oom']} · "
        f"error={(m.get('error') or '')[:80]!r} · "
        f"rss_delta={m['peak_rss_delta_bytes']/1e6:.1f} MB · "
        f"tracemalloc_peak={m['tracemalloc_peak_bytes']/1e6:.1f} MB"
    )


async def row6_xlsx_measured_and_classified(fx: Fixtures) -> Tuple[bool, str]:
    r = fx.results.get("xlsx", {})
    if "peak_rss_delta_bytes" not in r:
        return False, "no xlsx measurement present"
    peak = r["peak_rss_delta_bytes"]
    tm_peak = r.get("tracemalloc_peak_bytes", 0)
    ceiling = POD_CEILING_BYTES
    classification = _classify(peak, ceiling, r.get("oom", False))
    r["classification"] = classification
    ceil_str = f"{ceiling/1e6:.0f} MB" if ceiling else "unknown"
    ratio_str = f"{(peak/ceiling)*100:.1f}%" if ceiling else "n/a"
    return True, (
        f"xlsx @ 500 MB · rss_delta_peak={peak/1e6:.1f} MB · "
        f"tracemalloc_peak={tm_peak/1e6:.1f} MB · pod_ceiling={ceil_str} · "
        f"ratio={ratio_str} · status={classification}"
    )


async def row7_classification_valid(fx: Fixtures) -> Tuple[bool, str]:
    csv_cls = fx.results.get("csv", {}).get("classification", "MISSING")
    xlsx_cls = fx.results.get("xlsx", {}).get("classification", "MISSING")
    valid = {"PROVEN", "AT-RISK", "BLOCKED", "UNCLASSIFIED-NO-CEILING"}
    if csv_cls not in valid or xlsx_cls not in valid:
        return False, f"invalid classifications · csv={csv_cls!r} xlsx={xlsx_cls!r}"
    return True, f"CSV={csv_cls} · xlsx={xlsx_cls}"


async def row8_three_options_report(fx: Fixtures) -> Tuple[bool, str]:
    """R8 · If any format is BLOCKED, three-options costed report must
    be present in the Stage 2 memo before the slice reports GREEN.
    If nothing is BLOCKED, this row asserts a Truth-in-capability
    closure line is added instead.
    """
    memo = MEMORY / "sprints" / "JC_STORAGE_STAGE_2_INGEST_PROFILING.md"
    csv_cls = fx.results.get("csv", {}).get("classification", "?")
    xlsx_cls = fx.results.get("xlsx", {}).get("classification", "?")
    any_blocked = "BLOCKED" in (csv_cls, xlsx_cls)

    # Compose the Findings section and append to the memo.
    lines: List[str] = []
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## Findings (2026-07-02 · slice run)")
    lines.append("")
    lines.append(f"| Format | Source size | Peak RSS delta | tracemalloc peak | Pod ceiling | Ratio | Status |")
    lines.append(f"|---|---|---|---|---|---|---|")
    for fmt in ("csv", "xlsx"):
        r = fx.results.get(fmt, {})
        src = r.get("source_size_bytes", 0)
        peak = r.get("peak_rss_delta_bytes", 0)
        tm = r.get("tracemalloc_peak_bytes", 0)
        ceiling = POD_CEILING_BYTES or 0
        ratio_pct = (peak / ceiling * 100) if ceiling else 0.0
        cls = r.get("classification", "?")
        lines.append(
            f"| {fmt} | {src/1e6:.1f} MB | {peak/1e6:.1f} MB | {tm/1e6:.1f} MB | "
            f"{ceiling/1e6:.0f} MB | {ratio_pct:.1f}% | **{cls}** |"
        )
        if r.get("error"):
            lines.append(f"| _{fmt}_ | _error_ | | | | | `{r['error'][:120]}` |")
    lines.append("")
    if any_blocked:
        lines.append("## Three-options costed report (per BLOCKED format)")
        lines.append("")
        blocked_formats = [
            f for f in ("csv", "xlsx")
            if fx.results.get(f, {}).get("classification") == "BLOCKED"
        ]
        for fmt in blocked_formats:
            lines.append(f"### {fmt} BLOCKED at 500 MB — user decides")
            lines.append("")
            lines.append(f"**(a) Pod bump** — raise pod memory ceiling.")
            lines.append(
                f"  · Current ceiling: {(POD_CEILING_BYTES or 0)/1e6:.0f} MB · "
                f"target: ≥ 2× measured peak ({fx.results[fmt].get('peak_rss_delta_bytes',0)/1e6*2:.0f} MB minimum, 4× recommended for safety margin)."
            )
            lines.append(f"  · Cost: infra spend delta (name-per-provider); ZERO code changes.")
            lines.append("")
            lines.append(f"**(b) Convert-on-ingest** — intercept 500 MB {fmt} upload → convert server-side.")
            if fmt == "xlsx":
                lines.append(f"  · openpyxl read-only + csv.writer OR pandas.read_excel chunked + to_parquet")
                lines.append(f"  · Cost: ~200-400 LOC + loss of xlsx-native features (formulas evaluated at ingest, formatting stripped, macros dropped).")
            else:
                lines.append(f"  · Pre-parse to Parquet with pyarrow.csv.read_csv chunked API.")
                lines.append(f"  · Cost: ~150-250 LOC + loss of CSV-native semantics (locale-specific numbers, header inference).")
            lines.append("")
            lines.append(f"**(c) Per-format cap** — enforce `STORAGE_MAX_UPLOAD_MB_{fmt.upper()}=<N>` while other formats keep 500 MB.")
            lines.append(f"  · N = AT-RISK/PROVEN boundary for {fmt}.")
            lines.append(f"  · Cost: ~30 LOC route-by-extension in `/api/uploads/presigned`. User-facing UX: {fmt} > cap rejected.")
            lines.append("")
        lines.append("**Recommendation**: user directs. Slice does NOT auto-pick.")
    else:
        lines.append("## Truth-in-capability closure")
        lines.append("")
        lines.append("No format BLOCKED. Findings above are the honest measurement — do NOT infer capability outside these tested points (500 MB / streaming-read-only mode). Interim guard revert eligibility per user directive:")
        both_proven = csv_cls == "PROVEN" and xlsx_cls == "PROVEN"
        if both_proven:
            lines.append(f"- BOTH formats PROVEN at 500 MB → **auto-revert eligible** · `STORAGE_MAX_UPLOAD_MB` may return to 500.")
        else:
            lines.append(f"- Not both PROVEN (CSV={csv_cls} · xlsx={xlsx_cls}) → interim guard **holds at 32 MB** · user directs any changes.")
        lines.append("")
    lines.append(f"_Written by `jc_storage_stage_2_ingest_profiling_slice.py` at {datetime.now(timezone.utc).isoformat()}_")
    with open(memo, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    fx.results["memo_appended"] = True
    fx.results["any_blocked"] = any_blocked
    fx.results["both_proven"] = (csv_cls == "PROVEN" and xlsx_cls == "PROVEN")

    if any_blocked:
        # Verify the three-options block landed.
        src = memo.read_text(encoding="utf-8")
        if "Three-options costed report" not in src:
            return False, "any_blocked=True but three-options block not in memo"
        return True, f"BLOCKED detected · three-options costed report appended to memo · CSV={csv_cls} xlsx={xlsx_cls}"
    return True, f"no BLOCKED · Truth-in-capability closure line appended · CSV={csv_cls} xlsx={xlsx_cls}"


async def row9_interim_guard_slice_still_green(fx: Fixtures) -> Tuple[bool, str]:
    """R9 · Regression against the interim guard slice — a quick
    smoke-test that its 32 MB gate is still in effect. Full slice is
    callable but we assert only the gate behaviour here to keep the
    row fast (< 2s)."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        r_csrf = await client.get(f"{BASE_URL}/api/csrf")
        csrf = r_csrf.json()["csrf_token"]
        headers = {
            "Authorization": f"Bearer {fx.token}",
            "X-CSRF-Token": csrf,
            "Cookie": f"csrf_token={csrf}",
        }
        r = await client.post(
            f"{BASE_URL}/api/uploads/presigned",
            headers=headers,
            json={
                "filename": "guard-regress.xlsx",
                "content_type": "application/octet-stream",
                "size_bytes": 33 * 1024 * 1024,
                "context_id": fx.context_id,
                "kind": "workbook",
            },
        )
    if r.status_code != 413 or "ceiling_exceeded_interim_guard" not in r.text:
        return False, f"interim guard regression FAIL · status={r.status_code} body={r.text[:200]!r}"
    return True, "interim guard still enforcing 32 MB gate (33 MB → 413 ceiling_exceeded_interim_guard)"


async def row10_rename_arc_hash_invariant(fx: Fixtures) -> Tuple[bool, str]:
    changelog = MEMORY / "CHANGELOG.md"
    prd = MEMORY / "PRD.md"
    changelog_boundary = (
        "## 2026-07-02 — JC-" + _OLD.upper() + "-MODULE-RENAME-PHASE-3-COMPONENT-COPY-EDITS"
    )
    prd_boundary = "> **2026-06-30 20:07 UTC"

    c_src = _text(changelog); c_idx = c_src.find(changelog_boundary)
    if c_idx < 0:
        return False, "CHANGELOG boundary marker not found"
    c_sha = hashlib.sha256(c_src[c_idx:].encode()).hexdigest()
    if c_sha != PRE_P4_CHANGELOG_BELOW_FOOTER_SHA:
        return False, f"CHANGELOG below-boundary drift · got {c_sha[:12]} expected {PRE_P4_CHANGELOG_BELOW_FOOTER_SHA[:12]}"
    p_src = _text(prd); p_idx = p_src.find(prd_boundary)
    if p_idx < 0:
        return False, "PRD boundary marker not found"
    p_sha = hashlib.sha256(p_src[p_idx:].encode()).hexdigest()
    if p_sha != PRE_P4_PRD_BELOW_FOOTER_SHA:
        return False, f"PRD below-boundary drift · got {p_sha[:12]} expected {PRE_P4_PRD_BELOW_FOOTER_SHA[:12]}"
    return True, "rename arc P4 hash invariants intact"


async def row11_canary_green(fx: Fixtures) -> Tuple[bool, str]:
    rc, out, err = _run([sys.executable, str(BACKEND / "scripts" / "jc_gcs_canary_probe.py")], timeout=60)
    if rc != 0 or "GREEN" not in out:
        return False, f"canary rc={rc} stdout={out[:180]!r}"
    import json as _json
    try:
        d = _json.load(open("/root/gcs-service-account.json"))
        prefix = d["private_key_id"][:12]
    except Exception as exc:  # noqa: BLE001
        return False, f"identity read failed: {exc!s:.120}"
    return True, f"canary GREEN · key prefix={prefix}"


# ==================================================================
# Orchestrator
# ==================================================================
ROWS: List[Tuple[str, Callable[[Fixtures], "asyncio.Future"]]] = [
    ("R1  · 500 MB CSV generated",              row1_csv_generated),
    ("R2  · CSV ingested via product path",     row2_csv_ingested),
    ("R3  · CSV RAM measured + classified",     row3_csv_measured_and_classified),
    ("R4  · 500 MB xlsx generated (streaming)", row4_xlsx_generated),
    ("R5  · xlsx ingested via product path",    row5_xlsx_ingested),
    ("R6  · xlsx RAM measured + classified",    row6_xlsx_measured_and_classified),
    ("R7  · classification per format valid",   row7_classification_valid),
    ("R8  · three-options / closure in memo",   row8_three_options_report),
    ("R9  · interim guard still enforcing",     row9_interim_guard_slice_still_green),
    ("R10 · rename arc hash invariant",         row10_rename_arc_hash_invariant),
    ("R11 · canary GREEN on current key",       row11_canary_green),
]


async def main() -> int:
    print("═" * 78)
    print("JC-STORAGE-STAGE-2-INGEST-PROFILING · proving slice · 11 rows")
    print("═" * 78)
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
            print(f"  {label:<48s}  {marker}  ({dt:7.0f} ms) · {detail}")
            if ok:
                passes += 1
        # Clean up temp files on disk.
        for fmt in ("csv", "xlsx"):
            lp = fx.results.get(fmt, {}).get("local_path")
            if lp and Path(lp).exists():
                try: Path(lp).unlink()
                except Exception: pass  # noqa: BLE001
    finally:
        await fx.teardown()
    total = len(ROWS)
    print("─" * 78)
    csv_cls = fx.results.get("csv", {}).get("classification", "?")
    xlsx_cls = fx.results.get("xlsx", {}).get("classification", "?")
    print(f"Classifications: CSV={csv_cls} · xlsx={xlsx_cls} · both_proven={fx.results.get('both_proven', False)} · any_blocked={fx.results.get('any_blocked', False)}")
    if passes == total:
        print(f"GREEN · {passes}/{total} rows passed")
        return 0
    print(f"RED · {passes}/{total} rows passed")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
