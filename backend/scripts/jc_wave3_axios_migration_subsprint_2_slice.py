#!/usr/bin/env python3
"""JC-WAVE3 axios migration sub-sprint 2 — proving slice.

Canonical Spec : /app/memory/JC_WS_CANONICAL_SPEC.md (parent JC-WS lock).
Sprint memo    : /app/memory/sprints/JC_WAVE3_AXIOS_SUBSPRINT_2.md

Six checks (Halt-and-Surface if any FAIL):

1. No direct `from "axios"` import remains in ANY app source file
   except `src/lib/api.js` (the shared client) — across all of
   `src/`.

2. Each of the 7 migrated files imports `api` (or `apiV2` for the
   one site that was already on the schema-validated wrapper).

3. No file uses `${API}/api/...` template strings on calls that
   shipped axios → api. Confirms the path-prefix rewrite.

4. The api client interceptor in `lib/api.js` is intact (CSRF +
   Bearer + X-Active-Context all still set).

5. No `useAuthHeaders` hook remains anywhere — every consumer must
   now defer to the shared api client interceptor for auth.

6. No leftover ad-hoc `axios.get(.../csrf)` priming calls. The api
   client handles the double-submit transparently.

Exit codes:
  0 → all GREEN
  1 → at least one FAIL
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FRONTEND = REPO / "frontend" / "src"

MIGRATED_FILES = [
    "pages/TrustCenter.jsx",
    "pages/WelcomePage.jsx",
    "pages/SharedArtefact.jsx",
    "website/pages/Waitlist.jsx",
    "website/pages/Cohort.jsx",
    "website/components/PublicVelocityTile.jsx",
    "components/chat/GovernanceSignals.jsx",
]

RESULTS: list[tuple[str, bool, str]] = []


def _record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    flag = "GREEN" if ok else "RED"
    print(f"  [{flag}] {name}: {detail}")


# ─── 1 ─ no `from "axios"` outside lib/api.js ────────────────────────
print("\n[1] No direct axios imports outside src/lib/api.js")
axios_imports: list[str] = []
for path in FRONTEND.rglob("*.jsx"):
    if "_archived" in str(path) or "__tests__" in str(path):
        continue
    text = path.read_text()
    if re.search(r'from\s+["\']axios["\']', text):
        axios_imports.append(str(path.relative_to(REPO)))
for path in FRONTEND.rglob("*.js"):
    if "_archived" in str(path) or "__tests__" in str(path):
        continue
    if path.name == "api.js" and path.parent.name == "lib":
        continue  # the wrapper itself is allowed
    text = path.read_text()
    if re.search(r'from\s+["\']axios["\']', text):
        axios_imports.append(str(path.relative_to(REPO)))
ok = len(axios_imports) == 0
_record(
    "no_direct_axios_outside_wrapper",
    ok,
    f"offenders={axios_imports if axios_imports else 'none'}",
)


# ─── 2 ─ each migrated file imports `api` (or apiV2) ─────────────────
print("\n[2] Migrated files import the shared client")
import_ok = []
import_bad = []
for rel in MIGRATED_FILES:
    full = FRONTEND / rel
    text = full.read_text()
    if re.search(r'import\s+\{\s*api(\s*,|\s*\})', text) or re.search(
        r'import\s+api\s+from\s+["\']@/lib/api/apiV2["\']', text
    ):
        import_ok.append(rel)
    else:
        import_bad.append(rel)
ok = len(import_bad) == 0
_record(
    "all_files_import_api_client",
    ok,
    f"missing_import={import_bad if import_bad else 'none'}",
)


# ─── 3 ─ no `${API}/api/...` template literals on migrated paths ─────
print("\n[3] No ${API}/api/ template literals remain in migrated files")
template_bad: list[str] = []
for rel in MIGRATED_FILES:
    full = FRONTEND / rel
    text = full.read_text()
    matches = re.findall(r'\$\{API\}\s*/\s*api/', text)
    if matches:
        template_bad.append(f"{rel} ({len(matches)} occurrences)")
ok = len(template_bad) == 0
_record(
    "no_api_template_literals",
    ok,
    f"offenders={template_bad if template_bad else 'none'}",
)


# ─── 4 ─ lib/api.js interceptor intact ───────────────────────────────
print("\n[4] lib/api.js interceptor stack is intact")
api_text = (FRONTEND / "lib" / "api.js").read_text()
required = [
    'NON_IDEMPOTENT',          # CSRF interceptor preamble
    'X-CSRF-Token',            # CSRF header
    'akki_access_token',       # Bearer source
    'X-Active-Context',        # context header
    'csrf_token_missing',      # 403 retry handler
]
missing_pieces = [p for p in required if p not in api_text]
ok = not missing_pieces
_record(
    "api_client_interceptors_intact",
    ok,
    f"missing={missing_pieces if missing_pieces else 'all_required_present'}",
)


# ─── 5 ─ no useAuthHeaders hook anywhere ─────────────────────────────
print("\n[5] No useAuthHeaders hook leftover anywhere in src/")
ua_offenders: list[str] = []
for path in FRONTEND.rglob("*.jsx"):
    if "_archived" in str(path) or "__tests__" in str(path):
        continue
    text = path.read_text()
    # Allow the audit-comment reference in TrustCenter.jsx
    if re.search(r'\bfunction\s+useAuthHeaders\b', text) or re.search(
        r'\buseAuthHeaders\(\)', text
    ):
        ua_offenders.append(str(path.relative_to(REPO)))
ok = len(ua_offenders) == 0
_record(
    "no_useAuthHeaders_hook",
    ok,
    f"offenders={ua_offenders if ua_offenders else 'none'}",
)


# ─── 6 ─ no ad-hoc /api/csrf priming axios calls anywhere ────────────
print("\n[6] No ad-hoc /api/csrf priming axios calls anywhere in src/")
csrf_priming: list[str] = []
for path in list(FRONTEND.rglob("*.jsx")) + list(FRONTEND.rglob("*.js")):
    if "_archived" in str(path) or "__tests__" in str(path):
        continue
    if path.name == "api.js" and path.parent.name == "lib":
        continue  # the wrapper itself does prime via internal axios.get
    text = path.read_text()
    # Strip JS line comments + block comments before scanning so we
    # don't flag historical documentation that references the OLD
    # pattern (e.g. "// the legacy axios.get(/api/csrf) priming step").
    stripped = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
    # Look for axios.get with /api/csrf or /csrf in the URL
    if re.search(r'axios\.get\([^)]*[/\']csrf', stripped):
        csrf_priming.append(str(path.relative_to(REPO)))
ok = len(csrf_priming) == 0
_record(
    "no_adhoc_csrf_priming",
    ok,
    f"offenders={csrf_priming if csrf_priming else 'none'}",
)


# ─── Summary ───────────────────────────────────────────────────────
green = sum(1 for _, ok, _ in RESULTS if ok)
red = len(RESULTS) - green
print(f"\n=== SUMMARY: {green}/{len(RESULTS)} GREEN ===")
if red:
    print("FAILED checks:")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  - {name}: {detail}")
    sys.exit(1)

print("ALL CHECKS GREEN — Wave 3 axios sub-sprint 2 verified.")
sys.exit(0)
