# Codemod Convention

This directory holds **idempotent code-transformation scripts** that
perform mechanical migrations across the codebase — the kind of change
that would otherwise require N>50 manual file edits and which is
expressible in pattern-match terms.

The Phase 5.2 raw-axios → apiV2 migration (codemod 001) executed 155
mechanical file rewrites in a single idempotent pass, saving literal
weeks of manual labour. The pattern is now a rail.

---

## 1. When to use a codemod

A codemod is the RIGHT tool when ALL of the following are true:

| Criterion | Concrete heuristic |
|---|---|
| Mechanical | The change is a pattern-match-and-substitute; no human judgement per call site. |
| Repeated | The transformation applies to many files. Threshold: **N > 50**. Below that, manual edits with a search-replace + grep verification are fine. |
| Pattern-expressible | The rule can be written as a regex / AST match / scoped grep. If you have to reason case-by-case, it's not a codemod — it's a refactor. |
| Non-destructive | The script preserves git history, doesn't reformat untouched code, doesn't delete unrelated content. |
| Verifiable | Every codemod ships with a build-breaking invariant test that locks the post-state and prevents drift. |

If any of these don't hold, use a manual refactor instead. The
overhead of writing + reviewing a codemod isn't worth it under 50
sites.

---

## 2. Idempotency rule (non-negotiable)

**Every codemod must be safely re-runnable.**

The contract:
- Run the codemod once → it applies the transformation.
- Run the codemod a second time → it's a no-op (0 files touched).

How to verify:
```bash
$ python /app/scripts/codemods/NNN_short_description.py
[APPLIED] X files; Y line rewrites.
$ python /app/scripts/codemods/NNN_short_description.py
[APPLIED] 0 files; 0 line rewrites.    # ← must be zero
```

The idempotency check is the cheapest assertion that the codemod's
match pattern matches its OWN output. If the second run produces
edits, the pattern is over-eager and risks corrupting subsequent
calls.

Implement idempotency by ensuring the match pattern excludes the
post-transformation shape. Example from codemod 001:
- Match: `import { api[, ...] } from "<dots>/api"` (the legacy form).
- Replace: `import api from "<dots>/api/apiV2"` (the new form).
- The match pattern uses `(?:lib/)?api['"]` which does NOT match
  `(?:lib/)?api/apiV2['"]` — so the new form is not re-matched.

---

## 3. Naming convention

Filename format: `NNN_short_description.py`

- `NNN` — 3-digit zero-padded incrementing counter (`001`, `002`, …).
  Establishes ordering history; the order is meaningful (later codemods
  may assume earlier ones have run).
- `short_description` — `snake_case` verb_object phrase.
  - GOOD: `001_raw_axios_to_apiv2`, `002_dict_any_to_pydantic_model`,
    `003_print_to_logger_info`.
  - BAD: `axios_migration`, `narrow_routes`, `fix_logging`.

Numbers are assigned at land-time, not at write-time. Two codemods in
flight at the same time take the next two available numbers in
land-order.

---

## 4. Required structure

Every codemod file:

```python
#!/usr/bin/env python3
"""Phase X.Y — short description.

Long docstring covering:
  - Purpose (1-2 sentences).
  - Scope (which files match, which don't).
  - Idempotency proof (the pattern that excludes post-state).
  - Whitelist (paths skipped by design, with reasons).
  - How to run (dry-run + apply commands).
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path("/app/<area>")
EXTS = {".js", ".jsx", ".ts", ".tsx"}    # or .py, .md, etc.

SKIP = { ... }       # explicit file paths
SKIP_DIRS = (...,)   # directory prefixes

_PATTERN_RE = re.compile(r"...", re.MULTILINE)

def _rewrite(content: str) -> Tuple[str, int]:
    """Return (rewritten_content, edits_count)."""
    ...

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    files_touched, total_edits = [], 0
    for path in sorted(ROOT.rglob("*")):
        # iterate, skip, rewrite, count
        ...

    mode = "DRY-RUN" if args.dry_run else "APPLIED"
    print(f"\n[{mode}] {len(files_touched)} files; {total_edits} rewrites.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

CLI contract:
- `--dry-run` — preview only; no file writes.
- `--verbose` / `-v` — print every touched file.
- Default (no flags) — apply edits.
- Exit code: `0` on success (including 0-files-touched); non-zero on
  unexpected error.
- Final line MUST be `[APPLIED]` or `[DRY-RUN]` + counts. CI scrapes
  this line.

---

## 5. Verification rule (the lock)

**Every codemod ships with at least one build-breaking invariant
test.**

Why: without a lock, the codebase can drift back to the pre-codemod
shape as new code lands. The invariant test runs on every default
pytest invocation and fails the build if the pattern re-appears.

Location: `/app/backend/tests/invariants/test_invariant_<lock_name>.py`.

Example pairings:
| Codemod | Invariant test | What it locks |
|---|---|---|
| `001_raw_axios_to_apiv2.py` | `test_invariant_no_raw_axios.py` | No new file imports `{ api }` from `lib/api` outside whitelist. |
| (future) `002_dict_any_to_pydantic_model.py` | `test_invariant_polymorphic_response_ratchet.py` (already exists) | `Optional[Dict[str, Any]]` route count only goes DOWN, never up. |

The invariant MUST include:
1. A scanner function (`_scan_for_<thing>()`) that returns the current
   violation set.
2. A test function with a clear remediation message pointing to the
   codemod path.
3. A whitelist (if any) with each entry justified inline + a sibling
   test that asserts whitelist entries resolve to real files (no
   stale entries).

---

## 6. Non-destructive convention

Codemods must NOT:
- Reformat untouched code (no auto-formatter passes inside the codemod).
- Delete files (split into a separate `cleanup_<thing>.py` script if
  deletion is needed — clearly named and separately reviewed).
- Touch areas outside the documented scope. A codemod that "happens
  to also fix" something unrelated is a code review nightmare.
- Modify generated files (e.g. `schemas.gen.ts`, slice JSONs).
- Edit `_archived/`, `node_modules/`, build outputs, etc.

Preserve git blame as much as the transformation allows. For
import-line rewrites, this is automatic (only the import line moves);
for AST-scale transformations, accept that blame will shift and
document the migration in the commit message.

---

## Candidate Future Codemods

Pre-screened mechanical migrations that match the rules above. Pick
one when its parent dispatch lands. **Numbers are assigned at land
time.**

### `NNN_dict_any_to_pydantic_model.py` (Phase 5.4 candidate)

- **Scope**: 49 FastAPI handlers in `backend/routers/` still declared
  with `response_model=Optional[Dict[str, Any]]` (baselined in
  `test_invariant_polymorphic_response_ratchet.py`).
- **Pattern**: AST-match the FastAPI route decorator + the line
  carrying the `# phase-3.0:narrow-in-3.1` marker; consult a
  per-route mapping table (`{ "GET /api/chats/{id}": "ChatDetailResponse", ... }`);
  replace `response_model=Optional[Dict[str, Any]]` with
  `response_model=Optional[<MappedModel>]` and drop the marker.
- **Pre-req**: per-route Pydantic model authored in
  `contracts/responses.py` BEFORE the codemod runs.
- **Verification lock**: the existing ratchet invariant (the codemod
  decrements `_BASELINE_POLY_ROUTE_COUNT` after running).
- **Per-batch diff-harness**: required (the dispatch's "wire-byte
  equivalence" rail). The codemod itself doesn't run the harness;
  it's a separate sibling step in the dispatch.

### `NNN_print_to_logger_info.py` (only if applicable — verify first)

- **Scope**: `print(...)` calls in `backend/` outside `scripts/` and
  test files. Verify with a grep before scoping — if the count is
  low (<50), skip the codemod and just inline-fix.
- **Pattern**: line-match `print(<args>)` → `logger.info(<args>)`,
  adding `import logging; logger = logging.getLogger(__name__)` at
  module top if missing.
- **Caveat**: NOT mechanical for multi-line print, `print(file=...)`,
  or print used for stdout emission to subprocesses. Likely a hybrid
  codemod-with-warnings pass; needs careful scope.
- **Verification lock**: would need a new
  `test_invariant_no_print_in_backend.py` invariant.

### `NNN_archived_dead_code_removal.py` (cleanup candidate, low priority)

- **Scope**: `/app/frontend/src/_archived/` — 5 files still
  whitelisted in `test_invariant_no_raw_axios.py` and any other
  archived directories.
- **Pattern**: delete files in `_archived/`; verify they're not
  referenced anywhere in `src/` (outside `_archived/` itself).
- **Pre-req**: grep `_archived` in `src/` to confirm zero external
  references.
- **Verification lock**: refresh the codemod 001 invariant's
  `_WHITELIST` set (remove the 5 archived entries).

### `NNN_emergent_envvar_to_typed_settings.py` (Phase 6 candidate, gated)

- **Scope**: ~80 `os.environ.get("AKKI_*")` call sites in
  `backend/`.
- **Pattern**: replace inline `os.environ.get("AKKI_X", default)`
  with a centralized `settings.AKKI_X` import from a Pydantic
  `BaseSettings` class.
- **Pre-req**: the typed settings module must land first.
- **Verification lock**: a new invariant banning new
  `os.environ.get` calls in router/service modules.

---

## Running a codemod

```bash
# Preview (no writes)
python /app/scripts/codemods/NNN_short_description.py --dry-run

# Verbose preview
python /app/scripts/codemods/NNN_short_description.py --dry-run -v

# Apply
python /app/scripts/codemods/NNN_short_description.py

# Verify idempotency (re-run must produce 0 changes)
python /app/scripts/codemods/NNN_short_description.py

# Run the locking invariant
cd /app/backend && python -m pytest tests/invariants/test_invariant_<lock_name>.py -v
```

---

## Filing a new codemod (checklist)

Before opening the PR:

- [ ] N > 50 files affected? (else: manual refactor).
- [ ] Pattern expressible as regex / AST match?
- [ ] Idempotency: second run is a no-op?
- [ ] Dry-run mode works and reports correct counts?
- [ ] Skip list documented inline (paths + reasons)?
- [ ] Build-breaking invariant test lands in the same PR?
- [ ] Invariant test references THIS codemod by path in its docstring?
- [ ] This README's "Candidate Future Codemods" entry (if any) crossed
      off?
- [ ] Sprint memo includes the codemod + invariant + dry-run output
      + idempotency-proof?

---

## History

| # | Date | Codemod | Files touched | Invariant lock |
|---|---|---|---|---|
| 001 | 2026-06-24 | `001_raw_axios_to_apiv2.py` | 155 FE files | `test_invariant_no_raw_axios.py` |
