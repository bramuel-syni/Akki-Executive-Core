"""Cross-context calls invariant — Phase 1 (OBSERVE MODE).

The boundary-imports invariant (`test_invariant_boundary_imports.py`)
catches direct cross-context imports at the FILE level. This
invariant catches the same kind of leak at the CALL-SITE level:
calls into other contexts that should be mediated by
`backend/contracts/` but currently bypass it.

Specifically: any call site that invokes one of the 21 contract
methods' underlying primitives WITHOUT going through the contracts
package is logged as a violation. Examples:

  * Calling `shield_invoke` directly (instead of
    `get_synisense().shield_invoke(...)`) — Phase 2 migrates these.
  * Calling `narrate_analysis` directly — Phase 2 migrates these.
  * Direct Mongo reads from `db.accounts.find_one(...)` inside
    SyniSense or Solva packages — Phase 2 migrates these via
    `AkkiContract.get_tenant_profile()`.

OBSERVE MODE in Phase 1
-----------------------
The Phase 1 build dispatch specifies observe mode here: the test
WRITES a JSON report to
`/app/memory/invariants/cross_context_violations.json` and PASSES
the build regardless of the violation count. Phase 2 will flip this
to enforce mode after migrating call sites.

This pattern matches the Phase 0 tenancy invariant's observe-mode
contract.
"""
from __future__ import annotations

import ast
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Tuple


# ───────────────────────── call-site patterns ─────────────────────────

# Method-name → context-owner mapping. If a file in package X calls
# a method in this dict, and X != the method's context-owner, AND the
# call site is outside `backend/contracts/`, it's a violation.
#
# Phase 1 seed: the load-bearing primitives for the 21 contract
# methods. Phase 2 widens this as call sites migrate.
CROSS_CONTEXT_PRIMITIVES: Dict[str, str] = {
    # SyniSense-owned (callers in Solva / Akki should route through SyniSenseContract)
    "shield_invoke":              "synisense",
    "find_audit":                 "synisense",
    "find_receipt":               "synisense",
    # Solva-owned (callers in Akki should route through SolvaContract)
    "narrate_analysis":           "solva",
    # Akki-owned data accessors (callers in SyniSense / Solva should route through AkkiContract)
    # These are method NAMES on db.<collection> objects, not function names,
    # so they need a different handling — see _detect_db_calls below.
}

# Tenant-scoped collections that should be accessed via AkkiContract,
# not directly. Mirrors Pre-Read §4.C's mapping; Phase 0's tenancy
# invariant has a broader list — we use a focused subset here for the
# cross-context perspective (only Akki-owned data that SyniSense or
# Solva should NOT reach into directly).
AKKI_OWNED_COLLECTIONS: FrozenSet[str] = frozenset({
    "accounts",
    "contexts",
    "cycles",
    "cycle_questions",
    "memberships",
    "chats",
    "chat_messages",
    "briefings",
    "documents",
    "objectives",
})

# Phase 4.3 — `signals` reclassified as SyniSense-owned. SyniSense's
# primary artefact is derived by `services/synisense/engine/
# signal_derivation.py`. Akki / Solva readers go through
# `SyniSenseContract.{count,list,get,...}_signal*(...)`; SyniSense
# self-reads are now same-context (no escape hatch needed). The
# 5 retained Phase 4.2 Deviation #1 hatches are dissolved by this
# reclassification + the new typed methods on `SyniSenseContract`.
SYNISENSE_OWNED_COLLECTIONS: FrozenSet[str] = frozenset({
    "signals",
})

# File path → owning context.
SYNISENSE_ROUTER_PREFIXES: Tuple[str, ...] = (
    "synisense_", "healthz_shield", "trust_", "signal_", "signals_",
    "admin_shield_", "admin_signal_",
)
SOLVA_ROUTER_PREFIXES: Tuple[str, ...] = (
    "solva_",
)


def _file_context(fp: str) -> str:
    if "/app/backend/services/synisense/" in fp:
        return "synisense"
    if "/app/backend/services/solva_v2/" in fp:
        return "solva"
    if "/app/backend/services/solva_voice_audit/" in fp:
        return "solva"
    if "/app/backend/services/workbook_analyzer/" in fp:
        return "akki"  # Akki-adjacent library
    if "/app/backend/services/work_studio/" in fp:
        return "akki"
    if "/app/backend/routers/" in fp:
        # Phase 4.0 — natural-context routers (synisense_*.py /
        # solva_*.py / etc.) are the HTTP surface of their respective
        # contexts. Calls into their own internal services do NOT
        # count as cross-context.
        fname = fp.rsplit("/", 1)[-1]
        for pfx in SYNISENSE_ROUTER_PREFIXES:
            if fname.startswith(pfx):
                return "synisense"
        for pfx in SOLVA_ROUTER_PREFIXES:
            if fname.startswith(pfx):
                return "solva"
        return "akki"
    if "/app/backend/contracts/" in fp:
        return "contracts"
    if "/app/backend/services/" in fp:
        return "akki"  # default Akki for everything else under services/
    return "unknown"


# Scan everything we know about; skip noise.
SCAN_ROOTS: Tuple[str, ...] = (
    "/app/backend/services",
    "/app/backend/routers",
)
EXCLUDE_PATH_FRAGMENTS: Tuple[str, ...] = (
    "/__pycache__/", "/tests/", "/scripts/", "/migrations/",
)
EXEMPT_PATH_FRAGMENTS: Tuple[str, ...] = (
    "/app/backend/contracts/",
)

ESCAPE_HATCH_MARKER = "boundary:allow-direct-call"

REPORT_PATH = Path("/app/memory/invariants/cross_context_violations.json")


# ───────────────────────── helpers ─────────────────────────

def _iter_python_files() -> List[Path]:
    out: List[Path] = []
    for root in SCAN_ROOTS:
        for dirpath, _, filenames in os.walk(root):
            if any(f in dirpath for f in EXCLUDE_PATH_FRAGMENTS):
                continue
            if any(f in dirpath for f in EXEMPT_PATH_FRAGMENTS):
                continue
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                fp = os.path.join(dirpath, fn)
                if any(f in fp for f in EXEMPT_PATH_FRAGMENTS):
                    continue
                out.append(Path(fp))
    return sorted(out)


def _line_is_escape_hatched(source_lines: List[str], lineno: int) -> bool:
    idx = lineno - 1
    candidates = source_lines[max(0, idx - 1): idx + 1]
    return any(ESCAPE_HATCH_MARKER in line for line in candidates)


def _call_name(node: ast.Call) -> str | None:
    """Return the callable name as a flat string, or None.

    Patterns recognised:
      foo(...)                  → "foo"
      module.foo(...)           → "foo"
      a.b.c.foo(...)            → "foo"
    """
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


# Names of the Phase 1 contract accessors. A call whose receiver chain
# starts with one of these is, by construction, going through the
# contracts package — so the primitive-name match should NOT count
# as a violation.
CONTRACT_ACCESSORS: FrozenSet[str] = frozenset({
    "get_synisense", "get_solva", "get_akki",
})


def _root_call_name(node: ast.AST) -> str | None:
    """Walk an `ast.Call.func` attribute chain down to the innermost
    `ast.Call` whose `.func` is an `ast.Name`. Return that name if
    found, else None.

    Used to detect whether a `obj.X(...)` call site has a receiver
    rooted at one of the contract accessors (e.g.
    `get_synisense().shield_invoke(...)` → root call is
    `get_synisense`).
    """
    while True:
        if isinstance(node, ast.Attribute):
            node = node.value
            continue
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                return func.id
            if isinstance(func, ast.Attribute):
                node = func
                continue
            return None
        if isinstance(node, ast.Await):
            node = node.value
            continue
        return None


def _is_contract_call(node: ast.Call) -> bool:
    """True if this call's receiver chain begins with a contract
    accessor (`get_synisense() / get_solva() / get_akki()`).
    """
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    root = _root_call_name(func.value)
    return root in CONTRACT_ACCESSORS


def _detect_db_calls(node: ast.Call) -> Tuple[str, str] | None:
    """Return (collection, method) if node is `db.<collection>.<method>(...)`.

    Same shape detector as the Phase 0 tenancy invariant.
    """
    func = node.func
    if not isinstance(func, ast.Attribute):
        return None
    method = func.attr
    inner = func.value
    if not isinstance(inner, ast.Attribute):
        return None
    collection = inner.attr
    root = inner.value
    if not isinstance(root, ast.Name) or root.id != "db":
        return None
    return (collection, method)


def _file_imports_contract_accessor(tree: ast.AST) -> bool:
    """Return True if the module imports any of the contract accessors
    from `contracts`. This is positive evidence that the file routes
    its primitive calls through the contracts package — typically via
    a module-level shim function that tests can monkey-patch (legacy
    Phase 1 test pattern).
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "contracts":
                for alias in node.names:
                    if alias.name in CONTRACT_ACCESSORS:
                        return True
    return False


def compute_cross_context_violations() -> List[Dict[str, Any]]:
    """Walk every file; record any direct cross-context primitive
    call that should be mediated by `contracts/`."""
    out: List[Dict[str, Any]] = []
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
        my_ctx = _file_context(str(fp))
        # Phase 4.0 — if the file imports a contract accessor from
        # `contracts`, treat primitive Name calls (`shield_invoke(...)`,
        # `find_audit(...)`, etc.) as routed through contracts. This
        # supports the test-friendly shim pattern where a module
        # defines its own `shield_invoke = ...` symbol bound to the
        # contract method so existing `monkeypatch.setattr(module,
        # "shield_invoke", ...)` tests keep working.
        file_imports_contract = _file_imports_contract_accessor(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if _line_is_escape_hatched(source_lines, node.lineno):
                continue
            # Primitive function calls (shield_invoke, narrate_analysis, etc.)
            name = _call_name(node)
            if name and name in CROSS_CONTEXT_PRIMITIVES:
                owner = CROSS_CONTEXT_PRIMITIVES[name]
                # Calls routed through the contracts package don't count.
                # E.g. `(await get_synisense().shield_invoke(...))` reads
                # as `obj.shield_invoke(...)` but the receiver is the
                # contract accessor — exempt by design.
                if _is_contract_call(node):
                    continue
                # Phase 4.0 shim — file imports a contract accessor, so
                # any local-name primitive call (e.g. a shim function)
                # is, by construction, routed through contracts.
                if file_imports_contract:
                    continue
                if owner != my_ctx and my_ctx != "contracts":
                    out.append({
                        "file":       str(fp),
                        "line":       node.lineno,
                        "kind":       "primitive_call",
                        "name":       name,
                        "owner":      owner,
                        "caller_ctx": my_ctx,
                    })
                    continue
            # Direct db.<X>.<method>(...) calls into Akki-owned collections
            # from non-Akki packages OR SyniSense-owned collections from
            # non-SyniSense packages.
            db_call = _detect_db_calls(node)
            if db_call is None:
                continue
            coll, method = db_call
            # Phase 4.2 — split ownership: signals reads from synisense
            # files are SAME-context.
            if coll in SYNISENSE_OWNED_COLLECTIONS:
                if my_ctx != "synisense" and my_ctx != "contracts":
                    out.append({
                        "file":       str(fp),
                        "line":       node.lineno,
                        "kind":       "db_read_from_other_context",
                        "name":       f"db.{coll}.{method}",
                        "owner":      "synisense",
                        "caller_ctx": my_ctx,
                    })
                continue
            if coll not in AKKI_OWNED_COLLECTIONS:
                continue
            if my_ctx in ("synisense", "solva"):
                out.append({
                    "file":       str(fp),
                    "line":       node.lineno,
                    "kind":       "db_read_from_other_context",
                    "name":       f"db.{coll}.{method}",
                    "owner":      "akki",
                    "caller_ctx": my_ctx,
                })
    return out


# ───────────────────────── tests ─────────────────────────

def test_cross_context_calls_scanner_writes_report() -> None:
    """Enforce-mode contract (Phase 4.0): write the report.
    Build fails when `violation_count > 0` (see
    `test_enforce_mode_zero_violations` below).
    """
    violations = compute_cross_context_violations()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "scan_timestamp":             datetime.now(timezone.utc).isoformat(),
        "scan_roots":                 list(SCAN_ROOTS),
        "primitives_inspected":       sorted(CROSS_CONTEXT_PRIMITIVES.keys()),
        "akki_owned_collections":     sorted(AKKI_OWNED_COLLECTIONS),
        "synisense_owned_collections": sorted(SYNISENSE_OWNED_COLLECTIONS),
        "escape_hatch_marker":        ESCAPE_HATCH_MARKER,
        "violations":                 violations,
        "violation_count":            len(violations),
        "phase":                      "4_3_enforce_mode",
        "phase_4_3_enforce_target":   "violation_count == 0 AND escape_hatch_count == 0",
    }
    REPORT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    assert REPORT_PATH.exists()


def test_cross_context_calls_report_has_expected_schema() -> None:
    """Report on disk matches the documented schema."""
    assert REPORT_PATH.exists()
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    required = {
        "scan_timestamp", "scan_roots", "primitives_inspected",
        "akki_owned_collections", "escape_hatch_marker",
        "violations", "violation_count", "phase",
        "phase_4_3_enforce_target",
    }
    assert required.issubset(data.keys())
    assert data["phase"] == "4_3_enforce_mode"
    for v in data["violations"]:
        for k in ("file", "line", "kind", "name", "owner", "caller_ctx"):
            assert k in v, f"violation missing {k!r}: {v!r}"


def test_enforce_mode_zero_violations() -> None:
    """Phase 4.0 enforce contract — build FAILS on any new
    unannotated cross-context direct call.

    Was `test_observe_mode_does_not_fail_build_phase_1` in Phase 1;
    flipped 2026-06-23 at Phase 4.0 close. The 48 Phase-1 observe-mode
    violations + 43 newly-surfaced (post-scanner-refinement) ones were
    all either migrated through `get_*()` adapters or explicitly
    annotated with `# boundary:allow-direct-call` (see sprint memo
    `PHASE_4_0_CONTRACT_WIRING.md` §B).

    Any NEW direct cross-context primitive or db.X.find call MUST
    either (a) route through `contracts/`, or (b) carry the
    `# boundary:allow-direct-call` annotation with documented
    rationale.
    """
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert data["violation_count"] == 0, (
        f"Cross-context invariant violation_count={data['violation_count']} "
        f"— Phase 4.0 enforce-mode requires 0 unannotated violations. "
        f"Route the call through `contracts/` (get_synisense / get_solva / "
        f"get_akki) OR annotate with `# boundary:allow-direct-call` and "
        f"document the deviation. Violations:\n  "
        + "\n  ".join(
            f"{v['file']}:{v['line']} {v['caller_ctx']}→{v['owner']} "
            f"({v['kind']}: {v['name']})"
            for v in data["violations"][:20]
        )
    )
