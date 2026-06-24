#!/usr/bin/env python3
"""Phase 5.4 — codemod 002: narrow `Optional[Dict[str, Any]]` response
models to named Pydantic models per a per-batch mapping table.

Operates on FastAPI router decorators in `/app/backend/routers/*.py`.
For each line matching:

    @router.<verb>("<path>", response_model=Optional[Dict[str, Any]])  # phase-3.0:narrow-in-3.1

This codemod consults the per-batch `MAPPING` table at the top of the
file. If the route is in the table, the decorator is rewritten to:

    @router.<verb>("<path>", response_model=Optional[<MappedModel>])  # Phase 5.4 narrowed

Including auto-detection of whether `<MappedModel>` is already
imported from `contracts.responses` in the target file. (Adding new
imports is OUT OF SCOPE for the codemod — the dispatch's discipline
rail "non-destructive" forbids cross-cutting imports. The author of
each batch is responsible for adding the `from contracts.responses
import X` line BEFORE running the codemod. The codemod will fail
loudly if the named model is missing from the file.)

Scope: ONLY rewrites lines that match the dispatch's exact decorator
shape. Lines using `response_model=Dict[str, Any]` (without `Optional`),
or response_model=Optional[<other>], are untouched.

Idempotency: the post-state decorator (`# Phase 5.4 narrowed`) does
NOT match the codemod's regex (which requires `Dict[str, Any]` in the
response_model value). Re-running this codemod against an already-
narrowed file produces 0 changes.

Batch 1 (Phase 5.4 close) — applied 2026-06-24:
  GET    /chats/{chat_id}            -> ChatResponse
  PATCH  /chats/{chat_id}            -> ChatResponse
  POST   /tasks/{tid}/commission     -> TaskResponse
  POST   /tasks/{tid}/close          -> TaskResponse
  GET    /tasks/counts               -> TaskCountsResponse
  GET    /tasks/{task_id}            -> TaskResponse
  PATCH  /tasks/{task_id}            -> TaskResponse

This batch was applied manually + the codemod was built second to
LOCK the convention. Re-running it against the post-state codebase is
a 0-change idempotency check. Future batches (5.5+) drop into the
MAPPING and the codemod handles the mechanical replace.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


ROUTERS_DIR = Path("/app/backend/routers")
EXT = ".py"

# Per-route mapping table. KEY: ("<verb_upper>", "<path>"). VALUE:
# the named Pydantic model. The model MUST be imported from
# `contracts.responses` by the target router file BEFORE the codemod
# runs (the codemod fails loudly if it isn't).
#
# Batch 1 (Phase 5.4 — applied 2026-06-24):
MAPPING: Dict[Tuple[str, str], str] = {
    ("GET",    "/chats/{chat_id}"):                         "ChatResponse",
    ("PATCH",  "/chats/{chat_id}"):                         "ChatResponse",
    ("POST",   "/tasks/{tid}/commission"):                  "TaskResponse",
    ("POST",   "/tasks/{tid}/close"):                       "TaskResponse",
    ("GET",    "/tasks/counts"):                            "TaskCountsResponse",
    ("GET",    "/tasks/{task_id}"):                         "TaskResponse",
    ("PATCH",  "/tasks/{task_id}"):                         "TaskResponse",
}

# Matches `@<varname>.<verb>("<path>", response_model=Optional[Dict[str, Any]])`
# with optional sibling args after `response_model=...` (the codemod
# preserves them). Trailing `# phase-3.0:narrow-in-3.1` marker
# tolerated and dropped.
_DECORATOR_RE = re.compile(
    r"""^(?P<indent>\s*)@(?P<varname>\w+)\.(?P<verb>get|post|put|patch|delete)\("""
    r"""(?P<quote>['"])(?P<path>[^'"]+)(?P=quote),\s*"""
    r"""response_model\s*=\s*Optional\s*\[\s*Dict\s*\[\s*str\s*,\s*Any\s*\]\s*\]"""
    r"""(?P<extra>[^)]*)\)"""
    r"""(?:\s*#\s*phase-3\.0:narrow-in-3\.1)?\s*$""",
    re.MULTILINE,
)


def _rewrite(content: str, file_label: str) -> Tuple[str, int, List[str]]:
    """Return (rewritten content, edits count, missing-import list)."""
    edits = 0
    missing: List[str] = []
    # Cache the file's import set — we can't add new imports here.
    imported_names: set[str] = set()
    # Matches single-line OR multi-line `from contracts.responses import (...)`
    # Captures the inner names list (possibly spanning newlines).
    import_re = re.compile(
        r"^from\s+contracts\.responses\s+import\s*(?:\(\s*([^)]+)\)|([^\n]+))",
        re.MULTILINE,
    )
    for m in import_re.finditer(content):
        inner = m.group(1) or m.group(2) or ""
        for name in inner.replace(",", " ").split():
            imported_names.add(name.strip())

    def _sub(m: re.Match) -> str:
        nonlocal edits
        verb = m.group("verb").upper()
        path = m.group("path")
        key = (verb, path)
        if key not in MAPPING:
            return m.group(0)
        model = MAPPING[key]
        if model not in imported_names:
            missing.append(
                f"{file_label}: route `{verb} {path}` maps to `{model}` "
                f"but `{model}` is not imported from `contracts.responses`. "
                f"Add the import to the file BEFORE running this codemod."
            )
            return m.group(0)
        indent = m.group("indent")
        varname = m.group("varname")
        verb_lower = m.group("verb")
        quote = m.group("quote")
        extra = m.group("extra")
        edits += 1
        return (
            f"{indent}@{varname}.{verb_lower}({quote}{path}{quote}, "
            f"response_model=Optional[{model}]{extra})  # Phase 5.4 narrowed"
        )

    new = _DECORATOR_RE.sub(_sub, content)
    return new, edits, missing


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    files_touched: List[Path] = []
    total_edits = 0
    all_missing: List[str] = []

    for path in sorted(ROUTERS_DIR.rglob(f"*{EXT}")):
        if not path.is_file():
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        # Fast pre-filter — skip files without the target pattern at
        # all (no `Dict[str, Any]` in any response_model).
        if "Dict[str, Any]" not in original:
            continue
        label = path.relative_to(ROUTERS_DIR.parent).as_posix()
        new, n, missing = _rewrite(original, label)
        all_missing.extend(missing)
        if n == 0 or new == original:
            continue
        files_touched.append(path)
        total_edits += n
        if args.verbose:
            print(f"  {label}: {n} rewrite(s)")
        if not args.dry_run:
            path.write_text(new, encoding="utf-8")

    if all_missing:
        print("\n[MISSING-IMPORTS]", file=sys.stderr)
        for line in all_missing:
            print(f"  {line}", file=sys.stderr)
        print(
            "\nThe codemod is non-destructive — it will not add imports. "
            "Add the listed imports manually then re-run.",
            file=sys.stderr,
        )

    mode = "DRY-RUN" if args.dry_run else "APPLIED"
    print(f"\n[{mode}] {len(files_touched)} files; {total_edits} decorator rewrites.")
    if all_missing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
