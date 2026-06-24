"""AUDIT_P2.4 — Invariant: `thinklab` must NEVER appear in backend code.

The engine is Solva v2. ThinkLab is a *UI surface* over it. There is
ZERO reason for backend modules, routes, classes, collection names,
import paths, configuration keys, log channels, or any other server-
side construct to contain the literal `thinklab` (case-insensitive).

This invariant is a HARD RATCHET with no allowlist. The current
codebase ships at zero `thinklab` references in `backend/` (verified
via case-insensitive recursive grep on 2026-06-24). This test locks
that state in. The first `thinklab` symbol that appears in backend
code fails the build.

Frontend usage (UI labels, route copy, i18n strings, etc.) is
INTENTIONALLY ALLOWED — the surface IS called ThinkLab. This invariant
deliberately does not scan `frontend/`.

Per the dispatch (Stage 1, item 4):
  "Add the one-line `thinklab` UI-label-only invariant (backend
   contains zero `thinklab` references; build-breaking)."
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


def _scan_backend_for_thinklab() -> List[Tuple[str, int, str]]:
    """Return (file_relpath, line_no, snippet) for every line in backend/
    that mentions `thinklab` case-insensitively. Skips __pycache__ and
    test fixtures dirs (no tests today reference thinklab; if they ever
    do, that's actually OK since tests can document the rename and shouldn't
    fail the invariant — but at present, the invariant scans ALL backend
    Python files for a hard ratchet)."""
    hits: List[Tuple[str, int, str]] = []
    for f in sorted(BACKEND.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        # Skip this invariant file itself (the regex literal would self-trigger).
        if f.name == "test_thinklab_uilabel_only.py":
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
