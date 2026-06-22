"""Boundary-imports invariant — Phase 1.

Cross-context imports are FORBIDDEN at the file level. The contract
package (`backend/contracts/`) is the ONLY allowed bridge between
contexts. The pass-through adapters in `backend/contracts/_adapters/`
are exempt from this rule by design — they wrap the underlying
services.

Per the Phase 1 build dispatch:
  - SyniSense (`backend/services/synisense/`) MUST NOT import from
    `solva_v2/`, `workbook_analyzer/`, `work_studio/`, or
    `backend/routers/`.
  - Solva (`backend/services/solva_v2/`) MUST NOT import from
    `synisense/`, `workbook_analyzer/`, `work_studio/`, or routers.
  - Akki routers MAY import from `contracts/` for cross-context calls
    (and the existing direct service imports are allowed in Phase 1
    via the baseline — Phase 2 migrates them).

Baseline-driven enforcement
---------------------------
The Pre-Read §5.B confirmed that current code has existing cross-
context imports (notably `services/solva_v2/analyze_narration.py`
importing `shield_invoke` directly). Migrating these in Phase 1
would break the behaviour-preservation guarantee. Instead:

  * First run computes the current set of cross-context imports and
    writes them to `/app/memory/invariants/boundary_imports.baseline.json`.
  * Every subsequent run computes the current set and compares against
    the baseline. NEW violations (not in baseline) FAIL the build.
  * Phase 2 dispatch migrates baseline entries to use the contract
    surface, shrinking the baseline JSON as it goes.
  * Phase 2's final move flips this to "baseline must be empty".

This pattern (build-breaking on growth, but preserving existing
state) is the only way to enforce the boundary without forcing
behaviour change in Phase 1.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Set, Tuple


# ───────────────────────── context definitions ─────────────────────────

# Each context maps a path prefix to the list of forbidden import
# path prefixes for files inside that context.
#
# `routers/` is treated as Akki (orchestration). The rule is asymmetric:
# routers CAN import from synisense / solva (because that's the orchestration
# pattern in flight today). What they SHOULD do is import via `contracts/`.
# The observe-mode `test_invariant_cross_context_calls.py` records the
# router-side migration backlog separately.
CONTEXT_RULES: Dict[str, FrozenSet[str]] = {
    # SyniSense files cannot reach into other contexts.
    "/app/backend/services/synisense/": frozenset({
        "services.solva_v2",
        "services.workbook_analyzer",
        "services.work_studio",
        "routers.",
    }),
    # Solva files cannot reach into SyniSense, Work Studio, or routers.
    # They can still reach workbook_analyzer because Solva v2 narration
    # legitimately reads the parsed-workbook output structure (it's an
    # adjacency, not a context leak per the Pre-Read §1.C taxonomy).
    "/app/backend/services/solva_v2/": frozenset({
        "services.synisense",
        "services.work_studio",
        "routers.",
    }),
    # Workbook analyzer and Work Studio are Akki-adjacent libraries; they
    # may not reach into the other reasoning/governance contexts.
    "/app/backend/services/workbook_analyzer/": frozenset({
        "services.synisense",
        "services.solva_v2",
        "services.work_studio",
        "routers.",
    }),
    "/app/backend/services/work_studio/": frozenset({
        "services.solva_v2",
        "services.workbook_analyzer",
        "routers.",
    }),
    # NOTE: routers/ is NOT in this dict. Routers are Akki's orchestration
    # surface and are allowed to import from synisense/solva directly in
    # Phase 1. Phase 2 migrates these to use `contracts/`. The observe-mode
    # cross_context_calls invariant tracks the migration backlog.
}

# Roots to scan. We scan every file that has a CONTEXT_RULES entry
# (i.e. the keys above act as both rules and scan roots for this test).
SCAN_ROOTS: Tuple[str, ...] = tuple(CONTEXT_RULES.keys())

# Files / dirs to exclude.
EXCLUDE_PATH_FRAGMENTS: Tuple[str, ...] = (
    "/__pycache__/",
    "/tests/",
    "/scripts/",
    "/migrations/",
)

# The contracts package is EXEMPT — it's the bridge layer by design.
# The pass-through adapters in `_adapters/` legitimately import across
# boundaries to wrap the underlying services.
EXEMPT_PATH_FRAGMENTS: Tuple[str, ...] = (
    "/app/backend/contracts/",
)

# Per-line escape hatch (for unavoidable legitimate exceptions).
ESCAPE_HATCH_MARKER = "boundary:allow-cross-context-import"

# Output paths.
BASELINE_PATH = Path("/app/memory/invariants/boundary_imports.baseline.json")
REPORT_PATH = Path("/app/memory/invariants/boundary_imports_current.json")


# ───────────────────────── helpers ─────────────────────────

def _file_in_context(file_path: str) -> str | None:
    """Return the context-prefix this file belongs to, or None if none."""
    for ctx_prefix in CONTEXT_RULES:
        if file_path.startswith(ctx_prefix):
            return ctx_prefix
    return None


def _iter_python_files() -> List[Path]:
    out: List[Path] = []
    for root in SCAN_ROOTS:
        for dirpath, _, filenames in os.walk(root):
            if any(frag in dirpath for frag in EXCLUDE_PATH_FRAGMENTS):
                continue
            if any(frag in dirpath for frag in EXEMPT_PATH_FRAGMENTS):
                continue
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                fp = os.path.join(dirpath, fn)
                if any(frag in fp for frag in EXEMPT_PATH_FRAGMENTS):
                    continue
                out.append(Path(fp))
    return sorted(out)


def _imports_in_file(tree: ast.AST) -> List[Tuple[str, int]]:
    """Return list of (imported_module, lineno) pairs."""
    out: List[Tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level == 0 and module:
                out.append((module, node.lineno))
            # Relative imports (level > 0) are intra-package by
            # construction and cannot cross context boundaries.
    return out


def _violates_rule(imported_module: str, forbidden: FrozenSet[str]) -> bool:
    """True if `imported_module` matches any forbidden prefix."""
    for f in forbidden:
        if imported_module == f.rstrip("."):
            return True
        if imported_module.startswith(f if f.endswith(".") else f + "."):
            return True
    return False


def _line_is_escape_hatched(source_lines: List[str], lineno: int) -> bool:
    idx = lineno - 1
    candidates = source_lines[max(0, idx - 1): idx + 1]
    return any(ESCAPE_HATCH_MARKER in line for line in candidates)


def compute_cross_context_violations() -> List[Dict[str, Any]]:
    """Walk every file under SCAN_ROOTS, return all cross-context
    import violations as a list of dicts. Each dict carries
    {file, line, imported, context_prefix}.
    """
    violations: List[Dict[str, Any]] = []
    for fp in _iter_python_files():
        try:
            source = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        source_lines = source.splitlines()
        try:
            tree = ast.parse(source, filename=str(fp))
        except SyntaxError:
            continue
        ctx = _file_in_context(str(fp))
        if ctx is None:
            continue
        forbidden = CONTEXT_RULES[ctx]
        for imp_mod, lineno in _imports_in_file(tree):
            if not _violates_rule(imp_mod, forbidden):
                continue
            if _line_is_escape_hatched(source_lines, lineno):
                continue
            violations.append({
                "file":           str(fp),
                "line":           lineno,
                "imported":       imp_mod,
                "context_prefix": ctx,
            })
    return violations


def _normalise_for_compare(v: Dict[str, Any]) -> Tuple[str, str]:
    """Order-independent comparison key. We compare on file+imported,
    not line — line numbers shift trivially as code grows."""
    return (v["file"], v["imported"])


# ───────────────────────── tests ─────────────────────────

def test_boundary_imports_baseline_exists_or_is_recorded() -> None:
    """First run records the baseline; subsequent runs read it."""
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    current = compute_cross_context_violations()
    REPORT_PATH.write_text(
        json.dumps({"violations": current, "count": len(current)},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if not BASELINE_PATH.exists():
        BASELINE_PATH.write_text(
            json.dumps({
                "baseline_recorded_phase": "1",
                "violations":              current,
                "count":                   len(current),
                "rationale": (
                    "Phase 1 ships the contract surface and PASS-THROUGH "
                    "adapters; behaviour-preservation forbids migrating "
                    "existing cross-context imports in this phase. The "
                    "baseline captures the current state; Phase 2 "
                    "migrates entries and shrinks this file."
                ),
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    assert BASELINE_PATH.exists()


def test_no_new_cross_context_violations_beyond_baseline() -> None:
    """The build fails if the current cross-context import set has
    grown beyond the recorded baseline."""
    assert BASELINE_PATH.exists(), (
        "boundary baseline missing — run "
        "`test_boundary_imports_baseline_exists_or_is_recorded` first"
    )
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    baseline_keys = {tuple(b["__key__"]) if "__key__" in b else _normalise_for_compare(b)
                     for b in baseline.get("violations", [])}

    current = compute_cross_context_violations()
    current_keys = {_normalise_for_compare(v) for v in current}

    new_violations = current_keys - baseline_keys
    assert not new_violations, (
        f"Phase 1 boundary-imports invariant — {len(new_violations)} NEW "
        f"cross-context import(s) introduced beyond the recorded baseline. "
        f"Either add `{ESCAPE_HATCH_MARKER}` on the line if legitimate, "
        f"OR route the call through the contracts package. NEW: "
        f"{sorted(new_violations)!r}"
    )


def test_baseline_shrinks_or_holds_phase_1() -> None:
    """The current violation set must be a SUBSET of the baseline.
    A Phase-1 migration that removes a baseline entry without
    updating the baseline JSON is harmless; the test passes.
    """
    assert BASELINE_PATH.exists()
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    baseline_keys = {_normalise_for_compare(b) for b in baseline.get("violations", [])}
    current = compute_cross_context_violations()
    current_keys = {_normalise_for_compare(v) for v in current}
    # current ⊆ baseline must always hold (we may shrink but not grow).
    extra = current_keys - baseline_keys
    assert not extra, (
        f"Phase 1 baseline drift — current has entries not in baseline: "
        f"{sorted(extra)!r}"
    )


# ─── Scanner self-tests (regression catch) ─────────────────────────────

def test_scanner_finds_synthetic_import_violation() -> None:
    """Sanity check: scanner correctly flags a synthetic offender."""
    synth = (
        "from services.solva_v2.analyze_narration import narrate_analysis\n"
        "import services.work_studio.confidence_scorer\n"
    )
    tree = ast.parse(synth)
    imports = _imports_in_file(tree)
    assert any(
        i[0].startswith("services.solva_v2") for i in imports
    ), "scanner missed solva_v2 import"
    forbidden = CONTEXT_RULES["/app/backend/services/synisense/"]
    assert _violates_rule("services.solva_v2.analyze_narration", forbidden)
    assert _violates_rule("services.work_studio.confidence_scorer", forbidden)


def test_scanner_does_not_flag_intra_package_imports() -> None:
    """Sanity check: intra-package imports are not flagged."""
    synth = (
        "from services.synisense.shield.client import invoke\n"
        "from services.synisense.shield import canonical\n"
    )
    tree = ast.parse(synth)
    forbidden = CONTEXT_RULES["/app/backend/services/synisense/"]
    for imp_mod, _ in _imports_in_file(tree):
        assert not _violates_rule(imp_mod, forbidden), (
            f"intra-SyniSense import {imp_mod!r} wrongly flagged"
        )
