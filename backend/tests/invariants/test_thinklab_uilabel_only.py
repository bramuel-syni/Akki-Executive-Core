"""AUDIT_P2.4 — Invariant: `thinklab` must NEVER appear in backend code
except in the single allowlisted user-visible-label constants file.

The engine is Solva v2. The UI module rendered over it is ThinkLab.
There is ZERO reason for backend modules, routes, classes, collection
names, import paths, configuration keys, log channels, or any other
server-side construct to contain the literal `thinklab` (case-
insensitive).

**Allowlist (single-file exception):**
* `backend/services/module_labels.py` — the BE analog of the FE
  `frontend/src/lib/moduleLabels.js` constants file. Carries the
  user-visible module label strings that PDF/PPTX renderers +
  jinja template fallbacks need. Added 2026-07-02 by
  `JC-SOLVA-MODULE-RENAME-PHASE-1-ROUTES-AND-NAV` per Case 6 override.
  Every other BE `.py` file continues to hard-ratchet at zero
  `thinklab` matches — the invariant remains a HARD gate.

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


# Single-file allowlist. Analog of how ESLint whitelists a single
# constants file. Every other BE `.py` file continues to hard-ratchet.
_ALLOWLIST_FILENAMES = frozenset({
    "module_labels.py",  # backend/services/module_labels.py — Phase 1
})


def _scan_backend_for_thinklab() -> List[Tuple[str, int, str]]:
    """Return (file_relpath, line_no, snippet) for every line in backend/
    that mentions `thinklab` case-insensitively. Skips __pycache__ and
    the single-file allowlist entry (see `_ALLOWLIST_FILENAMES`)."""
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
        try:
            src = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for ln, line in enumerate(src.splitlines(), start=1):
            if THINKLAB_REGEX.search(line):
                hits.append((str(f.relative_to(REPO)), ln, line.strip()[:140]))
    return hits


def test_backend_has_zero_thinklab_references():
    """HARD RATCHET. The engine is Solva v2. ThinkLab is a UI surface.
    Backend code MUST NOT contain the literal `thinklab` (any casing).

    If this fails: rename the backend symbol to use `solva` (the engine
    name) or a domain-appropriate term. ThinkLab is FE-only.
    """
    hits = _scan_backend_for_thinklab()
    assert not hits, (
        f"AUDIT_P2.4 HARD RATCHET violated: {len(hits)} occurrence(s) of "
        f"`thinklab` (case-insensitive) found in backend/ code. The engine "
        f"is Solva v2; ThinkLab is a UI surface only. Backend modules, "
        f"routes, classes, collection names, configuration keys, and log "
        f"channels MUST NOT contain `thinklab`.\n\n"
        f"Offending lines:\n" +
        "\n".join(f"  {f}:{ln}  {snip}" for f, ln, snip in hits)
    )
