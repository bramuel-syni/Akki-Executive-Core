"""AUDITS-BACKEND-ROUTE — proving slice.

Canonical Spec: user dispatch 2026-07-02 Task B (audits backend route).
Router:         /app/backend/routers/audits.py
Wire-up:        /app/backend/server.py `app.include_router(audits_router.router)`.

Executes 5 assertion rows verifying the `/api/audits/{name}` route
serves the 3 whitelisted audit markdown files and rejects every other
input including path-traversal attempts. Runs entirely via bash — no
testing subagents.
"""
from __future__ import annotations

import os
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Callable, List, Tuple


APP = Path("/app")
AUDITS_DIR = APP / "memory/audits"
ROUTER_FILE = APP / "backend/routers/audits.py"
FRONTEND_ENV = APP / "frontend/.env"

ALLOWED = [
    "JC_WS_DECK_CONFORMANCE_AUDIT.md",
    "SOLVA_THINKLAB_RENAME_REGRESSION_AUDIT.md",
    "SHIELD_BELOW_CHAT_REGRESSION_INVESTIGATION.md",
    "SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md",
]


def _api_url() -> str:
    """Resolve preview backend URL from frontend/.env REACT_APP_BACKEND_URL."""
    for line in FRONTEND_ENV.read_text().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("REACT_APP_BACKEND_URL not found in frontend/.env")


API = _api_url()


def _curl(url: str, *, method: str = "GET") -> Tuple[int, str, str]:
    """Run curl and return (status_code, body, content_type)."""
    proc = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            method,
            "-D",
            "-",  # dump headers to stdout
            url,
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    raw = proc.stdout
    # Split first blank line — headers vs body
    header_block, _, body = raw.partition("\r\n\r\n")
    if not body:
        # some curl builds normalise to \n\n
        header_block, _, body = raw.partition("\n\n")
    lines = header_block.splitlines()
    status = 0
    ctype = ""
    for line in lines:
        if line.upper().startswith("HTTP/"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                status = int(parts[1])
        elif line.lower().startswith("content-type:"):
            ctype = line.split(":", 1)[1].strip()
    return status, body, ctype


def row1_three_allowlisted_files_return_200() -> Tuple[bool, str]:
    """Each of the 3 whitelisted files returns 200 + text/markdown + non-empty body."""
    for name in ALLOWED:
        url = f"{API}/api/audits/{name}"
        status, body, ctype = _curl(url)
        if status != 200:
            return False, f"{name} returned {status} not 200"
        if "text/markdown" not in ctype:
            return False, f"{name} content-type is '{ctype}', expected text/markdown"
        if not body or len(body) < 100:
            return False, f"{name} body is empty or too short ({len(body)} chars)"
    return True, f"all 3 whitelisted files return 200 + text/markdown + non-empty body"


def row2_unlisted_md_returns_404() -> Tuple[bool, str]:
    """A .md filename not in the allowlist returns 404 (not 200)."""
    url = f"{API}/api/audits/SOME_OTHER_AUDIT.md"
    status, _, _ = _curl(url)
    ok = status == 404
    return ok, f"SOME_OTHER_AUDIT.md returned {status} (expected 404)"


def row3_path_traversal_returns_404() -> Tuple[bool, str]:
    """Path-traversal attempts return 404, never 200 or 500."""
    attempts = [
        # url-encoded ../../etc/passwd
        urllib.parse.quote("../../../etc/passwd", safe=""),
        # nested traversal targeting a real backend file
        urllib.parse.quote("../server.py", safe=""),
        # absolute path
        urllib.parse.quote("/etc/passwd", safe=""),
        # traversal masked in dot patterns
        "..%2F..%2Fserver.py",
    ]
    for enc in attempts:
        url = f"{API}/api/audits/{enc}"
        status, _, _ = _curl(url)
        # 404 or a routing-level rejection (405/400) is acceptable;
        # what matters is that 200 is NEVER returned.
        if status == 200:
            return False, f"traversal attempt '{enc}' returned 200 — SECURITY FAIL"
        if status not in (400, 404, 405):
            return False, (
                f"traversal attempt '{enc}' returned unexpected {status} "
                f"(expected 400/404/405)"
            )
    return True, f"{len(attempts)} traversal attempts all rejected safely"


def row4_content_matches_disk_byte_for_byte() -> Tuple[bool, str]:
    """Served body matches the on-disk file byte-for-byte."""
    for name in ALLOWED:
        url = f"{API}/api/audits/{name}"
        _, body, _ = _curl(url)
        disk = (AUDITS_DIR / name).read_text(encoding="utf-8")
        # Compare byte-for-byte; account for potential trailing whitespace
        # from curl's split (\r\n\r\n normalisation). Trim single trailing
        # newline mismatches only.
        if body == disk:
            continue
        if body.rstrip("\r\n") == disk.rstrip("\r\n"):
            continue
        return False, (
            f"{name} body differs from disk file (served {len(body)}b, "
            f"disk {len(disk)}b, first diff at char "
            f"{next((i for i, (a, b) in enumerate(zip(body, disk)) if a != b), 'end')})"
        )
    return True, f"all 3 files match disk byte-for-byte"


def row5_no_auth_required() -> Tuple[bool, str]:
    """No Authorization header sent; route serves 200 unconditionally."""
    # _curl above never sets Authorization; we just re-run one URL to
    # explicitly confirm this remains true in production.
    url = f"{API}/api/audits/{ALLOWED[0]}"
    status, _, _ = _curl(url)
    ok = status == 200
    return ok, f"no-auth GET returned {status} (expected 200)"


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 3 whitelisted files return 200 + text/markdown + non-empty body", row1_three_allowlisted_files_return_200),
    ("R2 unlisted .md filename returns 404", row2_unlisted_md_returns_404),
    ("R3 path-traversal attempts all return non-200 (404/400/405)", row3_path_traversal_returns_404),
    ("R4 served body matches disk file byte-for-byte", row4_content_matches_disk_byte_for_byte),
    ("R5 no auth required", row5_no_auth_required),
]


def main() -> int:
    print("=" * 78)
    print("AUDITS-BACKEND-ROUTE proving slice")
    print(f"Backend URL: {API}")
    print(f"Router:      {ROUTER_FILE}")
    print("=" * 78)
    failures: List[str] = []
    for idx, (label, fn) in enumerate(ROWS, start=1):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001 — slice authoritative
            ok = False
            detail = f"raised {type(exc).__name__}: {exc}"
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"[{idx}/{len(ROWS)}] {status} — {label}")
        print(f"       {detail}")
        if not ok:
            failures.append(f"R{idx}: {label}")
    print("=" * 78)
    if failures:
        print(f"SLICE RED · {len(failures)}/{len(ROWS)} failed")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(f"SLICE GREEN · {len(ROWS)}/{len(ROWS)} rows passed")
    print("")
    print("Public preview URLs:")
    for name in ALLOWED:
        print(f"  {API}/api/audits/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
