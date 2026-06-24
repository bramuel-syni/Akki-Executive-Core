#!/usr/bin/env python3
"""Phase 5.2 Part A — FE raw-axios codemod.

Migrates `import { api[, ...others] } from '<X>/api'` to
`import api from '<X>/api/apiV2'` (+ a separate named import for any
sibling names), across every FE file under `/app/frontend/src/`.

Pattern matched (line-anchored):
    import { ...names... } from "<dots>/api";
    import { ...names... } from "@/lib/api";

Where `api` appears in `...names...`. The names list is split into
`api` (default-imported from apiV2) and the rest (kept as named-import
from the original module).

NOT in scope:
  - `src/lib/api.js` (the raw client itself).
  - `src/lib/api/*.js` (the wrapper internals).
  - Files that don't import `api` from `lib/api` (no-op).

Run with `--dry-run` to preview. Default mode applies edits and prints
the count of files touched.

Safety:
  * Idempotent — running twice produces no further changes.
  * Comment-preserving — only the import line is rewritten.
  * Quote-preserving — re-uses the file's own quote style.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path("/app/frontend/src")
EXTS = {".js", ".jsx", ".ts", ".tsx"}

# Skip — wrapper internals + the raw client + tests that mock the api
# object + archived sources.
SKIP = {
    Path("/app/frontend/src/lib/api.js"),
    Path("/app/frontend/src/lib/api/apiV2.js"),
    Path("/app/frontend/src/lib/api/validatedCall.js"),
    Path("/app/frontend/src/lib/api/endpointSchemas.js"),
    Path("/app/frontend/src/lib/api/resolveOperation.js"),
    Path("/app/frontend/src/lib/api/schemas.gen.ts"),
    # The unit tests under __tests__ that mock `api` for assertions on
    # the wrapper's underlying client. They MUST import the raw
    # `{ api }` to call `mockReset()` on its `.get` / `.post` etc.
    Path("/app/frontend/src/__tests__/apiV2.test.js"),
    Path("/app/frontend/src/__tests__/validatedCall.deliberateDrift.test.js"),
}

# Directories whose contents are skipped wholesale.
SKIP_DIRS = (
    "/app/frontend/src/_archived/",
)

# Matches:  import { ...names... } from "...api";
# Captures: names list + the source-module-path-without-trailing-slash.
# The source path must end with `/api` (relative) or `@/lib/api`.
_IMPORT_RE = re.compile(
    r"""^(?P<indent>\s*)import\s*\{\s*(?P<names>[^}]+?)\s*\}\s*from\s*(?P<quote>['"])(?P<src>(?:\.{1,2}/)*(?:lib/)?api|@/lib/api)(?P=quote)\s*;?\s*$""",
    re.MULTILINE,
)


def _split_names(names_raw: str) -> List[str]:
    """Parse the imported names list. Strips whitespace, drops empties."""
    return [n.strip() for n in names_raw.split(",") if n.strip()]


def _rewrite_path_to_apiv2(src: str) -> str:
    """`../lib/api` → `../lib/api/apiV2`. `@/lib/api` → `@/lib/api/apiV2`. etc."""
    return f"{src}/apiV2"


def _rewrite(content: str) -> Tuple[str, int]:
    """Return (rewritten content, edits count)."""
    edits = 0

    def _sub(m: re.Match) -> str:
        nonlocal edits
        names = _split_names(m.group("names"))
        if "api" not in names:
            return m.group(0)
        others = [n for n in names if n != "api"]
        indent = m.group("indent")
        quote = m.group("quote")
        src = m.group("src")
        apiv2_src = _rewrite_path_to_apiv2(src)

        lines = [f"{indent}import api from {quote}{apiv2_src}{quote};"]
        if others:
            lines.append(f"{indent}import {{ {', '.join(others)} }} from {quote}{src}{quote};")
        edits += 1
        return "\n".join(lines)

    new = _IMPORT_RE.sub(_sub, content)
    return new, edits


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Preview only.")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    files_touched: List[Path] = []
    total_edits = 0

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in EXTS:
            continue
        if path in SKIP:
            continue
        if any(str(path).startswith(d) for d in SKIP_DIRS):
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "api" not in original:
            continue
        new, n = _rewrite(original)
        if n == 0 or new == original:
            continue
        files_touched.append(path)
        total_edits += n
        if args.verbose:
            print(f"  {path.relative_to(ROOT)}: {n} edit(s)")
        if not args.dry_run:
            path.write_text(new, encoding="utf-8")

    mode = "DRY-RUN" if args.dry_run else "APPLIED"
    print(f"\n[{mode}] {len(files_touched)} files; {total_edits} import-line rewrites.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
