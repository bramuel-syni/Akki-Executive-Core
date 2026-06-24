"""Phase 5.2 Part A — invariant: no raw-axios `api.X()` outside the wrapper.

After Phase 3.2 (hot-path migration of 283 sites) and Phase 5.2 Part A
(cold-path migration of the remaining ~155 files via the
`/app/scripts/codemod_raw_axios_to_apiv2.py` codemod), every FE module
that does HTTP MUST route through `lib/api/apiV2.js` — which validates
responses against the codegenned zod schemas and surfaces drift loudly.

This invariant runs on every default pytest invocation and fails the
build if any new FE source file is introduced that imports the raw
`{ api }` named export from `lib/api`.

Allowed exceptions (documented whitelist — must NOT grow without
deliberate review):
  1. The wrapper itself (`src/lib/api/apiV2.js`, `validatedCall.js`).
  2. The raw client (`src/lib/api.js`).
  3. Wrapper-internal helpers (`endpointSchemas.js`, `resolveOperation.js`).
  4. The two `__tests__/` files that mock `api` for unit tests on the
     wrapper. Those tests MUST import the raw `{ api }` to call
     `mockReset()` on its `.get` / `.post` methods.
  5. `_archived/` — dead code retained for historical reference; will
     be removed in a future cleanup sprint.

Adding ANY new file to the whitelist requires explicit justification
(documented here AND in the sprint memo). The default answer is "no" —
new HTTP call sites MUST go through `apiV2`.

The invariant grep matches the IMPORT line specifically:
    import { api[, ...] } from "<dots>/api"
    import { api[, ...] } from "@/lib/api"

This is the correct anchor — a local variable named `api` that's the
default-imported `apiV2` (e.g. `import api from "@/lib/api/apiV2"`)
is fine; only the named-import of the raw `api` is banned.
"""
from __future__ import annotations

import re
from pathlib import Path


FRONTEND_SRC = Path("/app/frontend/src")

# Whitelist — exact paths only. These files are intentionally allowed
# to import `{ api }` from `lib/api`. See module docstring.
_WHITELIST = {
    # Wrapper internals
    "lib/api.js",
    "lib/api/apiV2.js",
    "lib/api/validatedCall.js",
    "lib/api/endpointSchemas.js",
    "lib/api/resolveOperation.js",
    "lib/api/schemas.gen.ts",
    # Unit tests that mock `api` to assert on the wrapper's underlying
    # client. They cannot use `apiV2` because they mock the underlying
    # axios instance directly.
    "__tests__/apiV2.test.js",
    "__tests__/validatedCall.deliberateDrift.test.js",
    # Archived sources — out-of-scope dead code retained for historical
    # reference. Will be removed in a future cleanup sprint.
    "_archived/Home1.jsx",
    "_archived/Home2.jsx",
    "_archived/e4_doc_routes/components/reading/ReadingTopBar.jsx",
    "_archived/e4_doc_routes/hooks/useDocumentParagraphs.js",
    "_archived/e4_doc_routes/pages/ReadingView.jsx",
}

# Matches `import { ..., api, ... } from "...api"` or
# `import { api, ... } from "@/lib/api"`. The `(?:lib/)?api` segment
# ensures the source module is exactly `lib/api` (not e.g. `lib/api/apiV2`).
_RAW_API_IMPORT_RE = re.compile(
    r"""^\s*import\s*\{\s*[^}]*?\bapi\b[^}]*?\s*\}\s*from\s*['"](?:\.{1,2}/)*(?:lib/)?api['"]\s*;?\s*$""",
    re.MULTILINE,
)

# Also catches `import api from "@/lib/api"` (default-import the wrong
# module). The raw `lib/api.js` does NOT have a default export; this
# pattern would only trigger if someone wrote a buggy import — but
# better to catch it.
_RAW_API_DEFAULT_IMPORT_RE = re.compile(
    r"""^\s*import\s+api\s+from\s+['"](?:\.{1,2}/)*(?:lib/)?api['"]\s*;?\s*$""",
    re.MULTILINE,
)


def _is_whitelisted(relpath: Path) -> bool:
    return relpath.as_posix() in _WHITELIST


def _scan_for_raw_api_imports() -> list[str]:
    """Walk `frontend/src/` and return the list of relative paths that
    contain a raw-api import outside the whitelist."""
    violations: list[str] = []
    for path in FRONTEND_SRC.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".js", ".jsx", ".ts", ".tsx"}:
            continue
        relpath = path.relative_to(FRONTEND_SRC)
        if _is_whitelisted(relpath):
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if _RAW_API_IMPORT_RE.search(body) or _RAW_API_DEFAULT_IMPORT_RE.search(body):
            violations.append(relpath.as_posix())
    return sorted(violations)


def test_no_raw_api_imports_outside_whitelist() -> None:
    """No new files may import the raw `{ api }` from `lib/api`.

    The codemod at `/app/scripts/codemod_raw_axios_to_apiv2.py`
    handles the migration mechanically. If you've added a new file
    that needs HTTP, import the default from `lib/api/apiV2` instead:

        import api from "@/lib/api/apiV2";

    `apiV2` is a drop-in replacement for the raw `api` (same
    `get / post / put / patch / delete` shape) but validates every
    response against the codegenned zod schemas and surfaces drift.

    If you genuinely need the raw client (e.g. you're writing a unit
    test that mocks `api`), document the reason here AND in the
    sprint memo, then add the path to `_WHITELIST` above.
    """
    violations = _scan_for_raw_api_imports()
    assert not violations, (
        f"Phase 5.2 Part A invariant — {len(violations)} FE file(s) import "
        f"the raw `{{ api }}` from `lib/api` outside the documented whitelist:\n  "
        + "\n  ".join(violations)
        + "\n\nRemediation: change the import to:\n"
        + "    import api from \"@/lib/api/apiV2\";\n"
        + "or, if the file legitimately needs the raw client, add its "
        + "relative path to `_WHITELIST` in this test file AND document "
        + "the reason in the sprint memo.\n\nThe codemod at "
        + "`/app/scripts/codemod_raw_axios_to_apiv2.py` performs the "
        + "migration mechanically."
    )


def test_whitelist_entries_all_resolve() -> None:
    """Every whitelisted path must exist — otherwise the whitelist is
    stale and the invariant has effectively no coverage on that entry."""
    missing = [
        w for w in sorted(_WHITELIST)
        if not (FRONTEND_SRC / w).exists()
    ]
    assert not missing, (
        f"Phase 5.2 Part A invariant — {len(missing)} whitelist entry(ies) "
        f"point to non-existent files. Either restore the file or remove the "
        f"entry from `_WHITELIST`:\n  " + "\n  ".join(missing)
    )
