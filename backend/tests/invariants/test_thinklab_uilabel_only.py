"""AUDIT_P2.4 — Invariant: `thinklab` must NEVER appear in backend
PRODUCTION code except in the single allowlisted user-visible-label
constants file. Meta-code (tests + proving-slice scripts) is exempt.

The engine is Solva v2. The UI module rendered over it is ThinkLab.
There is ZERO reason for backend PRODUCTION modules, routes, classes,
collection names, import paths, configuration keys, log channels, or
any other server-side construct to contain the literal `thinklab`
(case-insensitive).

**Allowlist (multi-layer):**

1. **Single-file constants exception** — `backend/services/module_labels.py`.
   The BE analog of the FE `frontend/src/lib/moduleLabels.js` constants
   file. Carries the user-visible module label strings AND PDF template
   filenames that the Solva engine needs. Added 2026-07-02 by
   `JC-SOLVA-MODULE-RENAME-PHASE-1-ROUTES-AND-NAV` per Case 6 override.
   Extended 2026-07-02 by `JC-SOLVA-MODULE-RENAME-PHASE-2-FILE-TREE`
   with template filename constants.

2. **Meta-code directories** — `backend/tests/**/*.py` +
   `backend/scripts/**/*.py`. Test files legitimately grep-assert
   against FE state (file paths, filenames, component names) as part
   of their invariant checks. Proving-slice scripts legitimately
   reference the new tokens to verify Phase-2 renames. Neither
   category is production surface code — they are meta-code that
   validates production surface state. Added 2026-07-02 by
   `JC-SOLVA-MODULE-RENAME-PHASE-2-FILE-TREE` per Option (a)
   Category-A+B fold-in.

Every backend `.py` file OUTSIDE `backend/services/module_labels.py`
AND OUTSIDE `backend/tests/**/*.py` AND OUTSIDE
`backend/scripts/**/*.py` continues to hard-ratchet at zero `thinklab`
matches. The invariant remains the true gate for PRODUCTION code.

Frontend usage (UI labels, route copy, i18n strings, etc.) is
INTENTIONALLY ALLOWED — the surface IS called ThinkLab. This invariant
deliberately does not scan `frontend/`.
"""
from __future__ import annotations

import pathlib
import re
from typing import List, Tuple

import pytest


REPO = pathlib.Path(__file__).resolve().parents[3]
BACKEND = REPO / "backend"

# Case-insensitive match: thinklab, ThinkLab, THINKLAB, etc.
THINKLAB_REGEX = re.compile(r"thinklab", re.IGNORECASE)


# Layer 1 — single-file constants allowlist (basename match).
_ALLOWLIST_FILENAMES = frozenset({
    "module_labels.py",  # backend/services/module_labels.py — Phase 1/2
})

# Layer 2 — meta-code directory allowlist (path-prefix match). Applied
# to path relative to REPO — e.g. "backend/tests/foo.py" allowlisted
# under "backend/tests".
_ALLOWLIST_DIR_PREFIXES = (
    "backend/tests",
    "backend/scripts",
)


def _scan_backend_for_thinklab() -> List[Tuple[str, int, str]]:
    """Return (file_relpath, line_no, snippet) for every line in backend/
    that mentions `thinklab` case-insensitively. Skips:

    * `__pycache__/` dirs
    * this invariant file itself (regex literal would self-trigger)
    * the single-file allowlist entry (`_ALLOWLIST_FILENAMES`)
    * meta-code directories (`_ALLOWLIST_DIR_PREFIXES`)
    """
    hits: List[Tuple[str, int, str]] = []
    for f in sorted(BACKEND.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        # Skip this invariant file itself (the regex literal would self-trigger).
        if f.name == "test_thinklab_uilabel_only.py":
            continue
        # Single-file allowlist for the user-visible-label constants file.
        if f.name in _ALLOWLIST_FILENAMES:
            continue
        # Meta-code directory allowlist.
        rel = f.relative_to(REPO).as_posix()
        if any(rel.startswith(prefix + "/") for prefix in _ALLOWLIST_DIR_PREFIXES):
            continue
        try:
            src = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for ln, line in enumerate(src.splitlines(), start=1):
            if THINKLAB_REGEX.search(line):
                hits.append((str(f.relative_to(REPO)), ln, line.strip()[:140]))
    return hits


def test_backend_has_zero_thinklab_references():
    """HARD RATCHET on production BE code. The engine is Solva v2.
    ThinkLab is a UI surface. Backend PRODUCTION code MUST NOT contain
    the literal `thinklab` (any casing).

    Exempt:
      * `backend/services/module_labels.py` (single-file constants)
      * `backend/tests/**/*.py` (meta-code — grep-assertion tests)
      * `backend/scripts/**/*.py` (meta-code — proving-slice scripts)

    If this fails: the offender is production BE code that has adopted
    the module name. Fix by (a) renaming the symbol to use `solva` (the
    engine name) or a domain-appropriate term, OR (b) routing through
    `services.module_labels` if it MUST emit a user-visible label.
    """
    hits = _scan_backend_for_thinklab()
    assert not hits, (
        f"AUDIT_P2.4 HARD RATCHET violated: {len(hits)} occurrence(s) of "
        f"`thinklab` (case-insensitive) found in backend/ PRODUCTION code. "
        f"The engine is Solva v2; ThinkLab is a UI surface only. Backend "
        f"production modules, routes, classes, collection names, "
        f"configuration keys, and log channels MUST NOT contain "
        f"`thinklab`. If the callsite legitimately needs a user-visible "
        f"module label, import from `services.module_labels`.\n\n"
        f"Offending lines:\n" +
        "\n".join(f"  {f}:{ln}  {snip}" for f, ln, snip in hits)
    )
