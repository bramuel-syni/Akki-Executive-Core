"""JC-WAVE3 · axios → shared client migration — sub-sprint 1 proving slice.

Scope: 4 sandbox/v2 files that previously each created their own
`axios.create(...)` instance with duplicate base-URL + cookies +
CSRF handling. Migrated to use the shared `lib/api::api` client
which already owns those concerns.

Per user direction at AUTONOMOUS BACKLOG RUN (2026-06-26):
  • "axios → apiV2 migration (314 sites) — break into ≤50-site
    sub-sprints, each with its own proving slice. Defer batches
    if you find non-trivial migrations (anything beyond
    mechanical search-and-replace + auth header normalization)."

This sub-sprint moves 11 call sites (well under the 50 ceiling)
across 4 files — purely mechanical. The remaining ~300 call sites
either already use the shared `lib/api::api` client (so are
already migrated by definition) or are spread across many small
surfaces that need their own sub-sprint scoping pass.

Run from the repo root:
    cd /app/backend && python scripts/jc_wave3_axios_migration_subsprint_1_slice.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ART_DIR = Path("/app/memory/jc_artifacts/wave3/axios_migration_subsprint_1")
ART_DIR.mkdir(parents=True, exist_ok=True)


MIGRATED_FILES = [
    "/app/frontend/src/components/sandbox/v2/Step4CycleSnapshot.jsx",
    "/app/frontend/src/components/sandbox/v2/ClosingStep.jsx",
    "/app/frontend/src/components/sandbox/v2/Step1SolvaWrapper.jsx",
    "/app/frontend/src/components/sandbox/v2/Step3StudioWrapper.jsx",
]

# Regexes — comments are stripped before matching so the JC-WAVE3
# breadcrumb comment doesn't false-positive "axios.create".
_COMMENT_RX = re.compile(r"^\s*//", re.MULTILINE)


def _read_code(path: str) -> str:
    """Read the file with comments stripped (line-comments only —
    block comments not used in the JSX files in scope)."""
    text = Path(path).read_text()
    lines = [ln for ln in text.splitlines() if not _COMMENT_RX.match(ln)]
    return "\n".join(lines)


def row_a_no_import_axios() -> Dict[str, Any]:
    """Row A — None of the 4 files import `axios` directly anymore."""
    bad = []
    for f in MIGRATED_FILES:
        code = _read_code(f)
        if re.search(r"^\s*import\s+axios\s+from\s+['\"]axios['\"]", code, re.MULTILINE):
            bad.append(f)
    return {"row": "A", "subject": "No direct axios import in migrated files",
            "bad": bad, "PASS": not bad}


def row_b_no_axios_create() -> Dict[str, Any]:
    """Row B — None of the 4 files call `axios.create(...)`."""
    bad = []
    for f in MIGRATED_FILES:
        code = _read_code(f)
        if "axios.create" in code:
            bad.append(f)
    return {"row": "B", "subject": "No local axios.create in migrated files",
            "bad": bad, "PASS": not bad}


def row_c_imports_shared_api() -> Dict[str, Any]:
    """Row C — All 4 files import `api` from `@/lib/api`."""
    bad = []
    for f in MIGRATED_FILES:
        code = _read_code(f)
        # accept either `import { api } from "@/lib/api"` or
        # `import { api, … } from "@/lib/api"`
        if not re.search(r"import\s*\{[^}]*\bapi\b[^}]*\}\s+from\s+['\"]@/lib/api['\"]", code):
            bad.append(f)
    return {"row": "C", "subject": "All 4 files import `api` from @/lib/api",
            "bad": bad, "PASS": not bad}


def row_d_paths_have_api_prefix() -> Dict[str, Any]:
    """Row D — Every `api.{get,post,put,delete,patch}(…)` call in the
    4 files uses a path that starts with `/` (not absolute URL,
    not env-var concatenation)."""
    bad = []
    rx = re.compile(r"api\.(get|post|put|delete|patch)\(\s*[`'\"]([^`'\")\s,]+)")
    for f in MIGRATED_FILES:
        code = _read_code(f)
        for m in rx.finditer(code):
            method, path = m.group(1), m.group(2)
            if not path.startswith("/"):
                bad.append({"file": f, "method": method, "path": path[:60]})
    return {"row": "D", "subject": "Every api.* call uses a leading-slash relative path",
            "bad": bad, "PASS": not bad}


def row_e_sandbox_v2_paths_explicit() -> Dict[str, Any]:
    """Row E — In files whose prior local axios had `baseURL: ${API}/api/sandbox/v2`,
    every migrated path must now start with `/sandbox/v2/`. Files
    that previously had `baseURL: ${API}/api` (Step1SolvaWrapper)
    keep their paths unchanged (already relative to /api)."""
    needs_prefix = {
        "/app/frontend/src/components/sandbox/v2/Step4CycleSnapshot.jsx": "/sandbox/v2/",
        "/app/frontend/src/components/sandbox/v2/ClosingStep.jsx":        "/sandbox/v2/",
        "/app/frontend/src/components/sandbox/v2/Step3StudioWrapper.jsx": "/sandbox/v2/",
    }
    rx = re.compile(r"api\.(get|post|put|delete|patch)\(`([^`]*)`")
    bad = []
    for f, prefix in needs_prefix.items():
        code = _read_code(f)
        for m in rx.finditer(code):
            path = m.group(2)
            if not path.startswith(prefix):
                bad.append({"file": f, "method": m.group(1), "path": path[:80]})
    return {"row": "E", "subject": "Sandbox-v2-baseURL files prefix paths with /sandbox/v2/",
            "bad": bad, "PASS": not bad}


def row_f_step1_paths_unchanged() -> Dict[str, Any]:
    """Row F — Step1SolvaWrapper's paths (already relative to /api)
    don't need /sandbox/v2 prefix on the /solva/v2 calls."""
    code = _read_code("/app/frontend/src/components/sandbox/v2/Step1SolvaWrapper.jsx")
    rx = re.compile(r"api\.(get|post)\(`([^`]*)`")
    paths = [m.group(2) for m in rx.finditer(code)]
    expected_starts = ("/sandbox/v2/", "/solva/v2/")
    bad = [p for p in paths if not p.startswith(expected_starts)]
    return {"row": "F", "subject": "Step1SolvaWrapper paths stay /sandbox/v2 or /solva/v2",
            "paths": paths, "bad": bad, "PASS": not bad}


def main():
    print("=" * 70)
    print("JC-WAVE3 axios migration sub-sprint 1 — proving slice")
    print("=" * 70)
    t0 = time.time()
    rows = [
        row_a_no_import_axios,
        row_b_no_axios_create,
        row_c_imports_shared_api,
        row_d_paths_have_api_prefix,
        row_e_sandbox_v2_paths_explicit,
        row_f_step1_paths_unchanged,
    ]
    results = []
    for fn in rows:
        try:
            r = fn()
        except Exception as exc:  # noqa: BLE001
            r = {"row": fn.__name__, "exception": f"{type(exc).__name__}: {exc}", "PASS": False}
        results.append(r)
        verdict = "✓ PASS" if r.get("PASS") else "✗ FAIL"
        print(f"  Row {r.get('row')}: {verdict}")
        if not r.get("PASS"):
            print(f"     {json.dumps({k: v for k, v in r.items() if k != 'PASS'}, default=str)[:400]}")
    n_pass = sum(1 for r in results if r.get("PASS"))
    n_total = len(results)
    print()
    print("=" * 70)
    print(f"RESULT: {n_pass}/{n_total} GREEN")
    print(f"Total elapsed: {round(time.time() - t0, 2)}s")
    print("=" * 70)
    out_path = ART_DIR / f"slice_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps({
        "ran_at":   datetime.now(timezone.utc).isoformat(),
        "n_pass":   n_pass, "n_total": n_total,
        "all_green": n_pass == n_total,
        "results":  results,
        "migrated_files": MIGRATED_FILES,
    }, default=str, indent=2))
    print(f"Evidence → {out_path}")
    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    sys.exit(main())
