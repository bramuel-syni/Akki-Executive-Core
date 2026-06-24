"""STAGE 3 — Build-breaking invariant for legacy Solva/Monitor names.

After the AKKI Full Runway Stage 3 rename pass (Option C — rename, not
delete), the new canonical names are:

  - `services/solva_voice_audit/` (was `services/solva/`)
  - `routers/monitor_dashboard.py` (was `routers/monitor.py`)
  - `routers/monitor_strategic_items.py` (was `routers/monitor_v2.py`)

These names describe FUNCTION, not version or phase. This invariant
locks them in:

  (a) No code in `backend/` may import the legacy names
      (`services.solva`, `routers.monitor` bare, `routers.monitor_v2`).
  (b) No NEW file or directory created under the `services/solva*` or
      `routers/monitor*` family may carry a `_v\\d+` suffix. Future
      variants MUST be named by capability, not version.

Per the user's verbatim direction:
  'name by function, kill every v1/v2 implication. Don't replace a
   misleading name with a half-misleading one.'

Known grandfathered exception:
  - `services/solva_v2/` is explicitly OUT OF SCOPE for this dispatch
    per the user's verbatim direction: 'For services/solva_v2/: leave
    the path as-is for now. The name is misleading but the rename has
    a wider blast radius (4 FE files import from it, plus chat surface,
    plus export pipeline). NOTE the rename as a follow-up under
    DEV_PIPELINE.md §9, but do NOT execute it in this dispatch.'
    The scanner allowlists the literal `solva_v2` stem; any NEW `_vN`
    suffix elsewhere fails the build.

No general allowlist. This is the third hard ratchet on the codebase
(after the context-membership and engine/surface-name guards).
"""
from __future__ import annotations

import ast
import pathlib
import re
from typing import List, Tuple

import pytest


REPO = pathlib.Path(__file__).resolve().parents[3]
BACKEND = REPO / "backend"

# Legacy import patterns (post-Stage-3 forbidden).
LEGACY_IMPORTS_RE = re.compile(
    r"^\s*(?:"
    # `from services.solva import ...` (bare `solva`, NOT solva_v2 / solva_voice_audit)
    r"from\s+services\.solva\b(?!_)"
    r"|"
    # `from services.solva.X import ...`
    r"from\s+services\.solva\."
    r"|"
    # `import services.solva` (bare, not followed by `_v2` / `_voice_audit`)
    r"import\s+services\.solva\b(?!_)"
    r"|"
    # `from routers import monitor as ...` (bare monitor — old name)
    r"from\s+routers\s+import\s+monitor\s+as\b"
    r"|"
    # `from routers import monitor_v2 as ...`
    r"from\s+routers\s+import\s+monitor_v2\b"
    r"|"
    # `from routers.monitor import ...` (bare module path)
    r"from\s+routers\.monitor\s+import\b"
    r"|"
    # `from routers.monitor_v2 import ...` / `from routers.monitor_v2.X import ...`
    r"from\s+routers\.monitor_v2\b"
    r")"
)

# Known grandfathered `_vN` stems we explicitly allow per the user's
# direction. Adding to this set is an audit-level change — only
# `solva_v2` for now (the user's verbatim out-of-scope note).
GRANDFATHERED_V_SUFFIX_STEMS = frozenset({
    "solva_v2",
})


def _iter_backend_py_files() -> List[pathlib.Path]:
    out: List[pathlib.Path] = []
    for f in sorted(BACKEND.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        # Skip the invariant file itself (it documents the legacy strings
        # in its docstring/regex which would self-trigger).
        if f.name == "test_no_legacy_solva_monitor_names.py":
            continue
        out.append(f)
    return out


def _scan_legacy_imports() -> List[Tuple[str, int, str]]:
    hits: List[Tuple[str, int, str]] = []
    for f in _iter_backend_py_files():
        try:
            src = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for ln, line in enumerate(src.splitlines(), start=1):
            if LEGACY_IMPORTS_RE.search(line):
                hits.append((str(f.relative_to(REPO)), ln, line.strip()[:200]))
    return hits


def _scan_versioned_paths() -> List[Tuple[str, str]]:
    """Return (relpath, suffix_match) for any file/dir under
    `services/solva*` or `routers/monitor*` carrying a `_v\\d+` suffix,
    EXCLUDING the known grandfathered exceptions
    (`GRANDFATHERED_V_SUFFIX_STEMS`)."""
    targets = [
        BACKEND / "services",
        BACKEND / "routers",
    ]
    hits: List[Tuple[str, str]] = []
    for t in targets:
        if not t.exists():
            continue
        for p in t.rglob("*"):
            if "__pycache__" in p.parts:
                continue
            rel = p.relative_to(REPO).as_posix()
            if not (
                rel.startswith("backend/services/solva")
                or rel.startswith("backend/routers/monitor")
            ):
                continue
            stem = p.stem if p.is_file() else p.name
            if stem in GRANDFATHERED_V_SUFFIX_STEMS:
                continue
            if re.search(r"_v\d+(?:_\d+)*$", stem):
                hits.append((rel, stem))
    return hits


# ────────────────────────────────────────────────────────────────────────
# Tests
# ────────────────────────────────────────────────────────────────────────


def test_no_legacy_solva_monitor_imports():
    """HARD RATCHET. No code in backend/ may import the legacy names.
    Use the post-Stage-3 canonical names:

      services.solva           -> services.solva_voice_audit
      routers.monitor          -> routers.monitor_dashboard
      routers.monitor_v2       -> routers.monitor_strategic_items
    """
    hits = _scan_legacy_imports()
    assert not hits, (
        f"AKKI Full Runway Stage 3 invariant violated: {len(hits)} legacy "
        f"import(s) found. Use the function-based canonical names "
        f"introduced in commits 7fcdb587 + 95ae06ba.\n\n"
        f"Offending lines:\n" +
        "\n".join(f"  {f}:{ln}  {snip}" for f, ln, snip in hits)
    )


def test_no_new_v_suffixes_under_solva_or_monitor():
    """HARD RATCHET. No new file or directory under `services/solva*`
    or `routers/monitor*` may carry a `_v\\d+` (or `_v\\d+_\\d+`) suffix.

    Per the user's framing: 'name by function, kill every v1/v2
    implication; don't replace a misleading name with a half-misleading
    one'. Future variants MUST describe capability."""
    hits = _scan_versioned_paths()
    assert not hits, (
        f"AKKI Full Runway Stage 3 invariant violated: {len(hits)} file(s) "
        f"or directories under services/solva* or routers/monitor* carry "
        f"a forbidden _vN suffix. Name by function instead.\n\n"
        f"Offending paths:\n" +
        "\n".join(f"  {p}  (stem: {s})" for p, s in hits)
    )


def test_canonical_paths_exist():
    """Smoke check: the renamed canonical paths exist after the Stage 3
    pass. Cheap protection against a future revert that drops the new
    names without removing this invariant."""
    expected = [
        BACKEND / "services" / "solva_voice_audit" / "__init__.py",
        BACKEND / "routers" / "monitor_dashboard.py",
        BACKEND / "routers" / "monitor_strategic_items.py",
    ]
    missing = [p for p in expected if not p.exists()]
    assert not missing, (
        f"Stage 3 canonical paths missing: {[str(p) for p in missing]}. "
        "If this invariant fires, the rename was reverted — restore the "
        "function-based names per commits 7fcdb587 + 95ae06ba."
    )
