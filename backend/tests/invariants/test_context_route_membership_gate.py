"""AUDIT_P2.2 — Invariant A: every `{context_id}` route must be membership-gated.

This is the HARD RATCHET that AUDIT_P2.1 introduced.

Background (verbatim from the P2.1 audit memo):
    `strategic_goal_evolution.py` declared a route with `{context_id}` in the
    path but used only `Depends(get_current_account)` — authn-only, no
    membership check. Any authenticated caller could pass any victim
    tenant's `context_id`/`goal_id` and receive 200 OK with cross-tenant
    data (board doc titles, audit log, etc.). The existing
    `test_invariant_tenancy.py` did not catch this because it validates
    query FILTERS have a tenant key, not whether the HANDLER itself has a
    membership gate.

The invariant:
    Every route declared in `backend/routers/*.py` (and elsewhere in
    `backend/`) whose URL path contains the literal `{context_id}` MUST
    have one of the following gates:

    (a) `Depends(require_context_membership(...))` from `core.py`     — canonical
    (b) `Depends(require_role(...))`               from `services.rbac` — canonical
    (c) An entry in `context_route_membership_allowlist.yml`            — audited exception

Anything else fails the invariant. No allowlist file modifications can be
"silent" — the YAML file IS the audit trail and EVERY entry there has a
`gate_mechanism` + `justification` field that PR reviewers must defend.
"""
from __future__ import annotations

import ast
import pathlib
from typing import Dict, List, Optional, Set, Tuple

import pytest
import yaml


REPO = pathlib.Path(__file__).resolve().parents[3]
BACKEND = REPO / "backend"
ALLOWLIST_FILE = REPO / "backend" / "tests" / "invariants" / "context_route_membership_allowlist.yml"

# Canonical factory deps that are accepted without an allowlist entry.
# Adding to this set is itself a deliberate audit-level change.
CANONICAL_FACTORY_DEPS: Set[str] = {
    "require_context_membership",  # core.py:249
    "require_role",                # services/rbac.py:127
}

# HTTP-verb decorator method names on the router-style decorators.
HTTP_VERBS: Set[str] = {"get", "post", "put", "patch", "delete"}


def _iter_python_files() -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    for f in sorted(BACKEND.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        if "/tests/" in str(f):
            continue
        files.append(f)
    return files


def _is_route_decorator(deco: ast.AST) -> Optional[Tuple[str, str]]:
    """If `deco` is a `@router.<verb>("...")` / `@app.<verb>("...")` call
    decorator with a literal string path, return `(verb, path)`. Else None."""
    if not isinstance(deco, ast.Call):
        return None
    if not (isinstance(deco.func, ast.Attribute) and deco.func.attr in HTTP_VERBS):
        return None
    if not deco.args:
        return None
    arg0 = deco.args[0]
    if not (isinstance(arg0, ast.Constant) and isinstance(arg0.value, str)):
        return None
    return deco.func.attr.upper(), arg0.value


def _depends_canonical_factory(default_node: ast.AST) -> bool:
    """Return True iff `default_node` is `Depends(<F>(...))` where `<F>` is a
    canonical factory (`require_context_membership` or `require_role`)."""
    if not isinstance(default_node, ast.Call):
        return False
    func = default_node.func
    func_name = func.attr if isinstance(func, ast.Attribute) else (
        func.id if isinstance(func, ast.Name) else None
    )
    if func_name != "Depends":
        return False
    if not default_node.args:
        return False
    inner = default_node.args[0]
    if not isinstance(inner, ast.Call):
        return False
    inner_func = inner.func
    inner_name = inner_func.attr if isinstance(inner_func, ast.Attribute) else (
        inner_func.id if isinstance(inner_func, ast.Name) else None
    )
    return inner_name in CANONICAL_FACTORY_DEPS


def _signature_has_canonical_gate(node: ast.AST) -> bool:
    """True iff any param's default is `Depends(<canonical_factory>(...))`."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    defaults: List[ast.AST] = list(node.args.defaults)
    defaults += [d for d in node.args.kw_defaults if d is not None]
    return any(_depends_canonical_factory(d) for d in defaults)


def _enumerate_context_id_routes() -> List[Dict[str, object]]:
    """Walk every backend `.py` file and return one dict per route whose
    path contains `{context_id}`. Each dict has `file`, `line`, `verb`,
    `path`, `handler`, `has_canonical_gate`."""
    found: List[Dict[str, object]] = []
    for f in _iter_python_files():
        try:
            src = f.read_text(encoding="utf-8")
            tree = ast.parse(src, str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for deco in node.decorator_list:
                meta = _is_route_decorator(deco)
                if meta is None:
                    continue
                verb, path = meta
                if "{context_id}" not in path:
                    continue
                found.append({
                    "file": str(f.relative_to(REPO)),
                    "line": node.lineno,
                    "verb": verb,
                    "path": path,
                    "handler": node.name,
                    "has_canonical_gate": _signature_has_canonical_gate(node),
                })
    return found


def _load_allowlist() -> Set[Tuple[str, int]]:
    """Return the set of (file_relpath, line) tuples in the allowlist."""
    if not ALLOWLIST_FILE.exists():
        raise FileNotFoundError(
            f"AUDIT_P2.2 allowlist file not found at {ALLOWLIST_FILE}. "
            "Create it (with the AUDIT_P2.2 schema) before adding routes "
            "that bypass the canonical membership-gate factories."
        )
    data = yaml.safe_load(ALLOWLIST_FILE.read_text(encoding="utf-8")) or {}
    entries = data.get("entries") or []
    out: Set[Tuple[str, int]] = set()
    for e in entries:
        f = e.get("file")
        ln = e.get("line")
        if not f or ln is None:
            raise AssertionError(
                f"Malformed allowlist entry (missing file or line): {e}"
            )
        if not (e.get("gate_mechanism") and e.get("justification")):
            raise AssertionError(
                f"Allowlist entry at {f}:{ln} MUST have non-empty "
                "'gate_mechanism' and 'justification' fields. Audit decisions "
                "require explicit rationale."
            )
        out.add((f, int(ln)))
    return out


# ────────────────────────────────────────────────────────────────────────
# Tests
# ────────────────────────────────────────────────────────────────────────


def test_allowlist_is_well_formed():
    """The allowlist YAML must parse and every entry must have the
    required fields. This is the foundation of the audit trail."""
    allowed = _load_allowlist()
    assert len(allowed) >= 1, "allowlist seems empty; check the file"


def test_no_allowlist_entry_is_orphaned():
    """Every allowlist entry must correspond to a real route in the
    codebase. Stale entries are a maintenance hazard."""
    allowed = _load_allowlist()
    routes = _enumerate_context_id_routes()
    route_keys = {(r["file"], r["line"]) for r in routes}
    orphaned = [a for a in allowed if a not in route_keys]
    assert not orphaned, (
        f"Orphaned allowlist entries (no matching {{context_id}} route): "
        f"{orphaned}. Remove the stale entries from "
        "context_route_membership_allowlist.yml."
    )


def test_every_context_id_route_is_gated_or_allowlisted():
    """THE HARD RATCHET. Every route with {context_id} must EITHER use a
    canonical factory dep OR have an explicit, justified entry in the
    audit-derived allowlist YAML."""
    allowed = _load_allowlist()
    routes = _enumerate_context_id_routes()
    violations: List[str] = []
    for r in routes:
        if r["has_canonical_gate"]:
            continue  # canonical factory dep present
        if (r["file"], r["line"]) in allowed:
            continue  # audited exception
        violations.append(
            f"  {r['file']}:{r['line']}  {r['verb']:<6} {r['path']:<70} -> {r['handler']}"
        )
    assert not violations, (
        f"AUDIT_P2.2 HARD RATCHET violated: {len(violations)} route(s) with "
        f"{{context_id}} in the path lack BOTH a canonical factory dep "
        f"(`require_context_membership` / `require_role`) AND an allowlist "
        f"entry in `context_route_membership_allowlist.yml`. This is the exact "
        f"silent-omission class that AUDIT_P2.1 caught in "
        f"`strategic_goal_evolution.py`.\n\n"
        f"Either (a) add `Depends(require_context_membership())` (or "
        f"`require_role(...)`) to the handler signature, OR (b) add an "
        f"audit-reviewed entry with `gate_mechanism` + `justification` to "
        f"the allowlist YAML.\n\n"
        f"Violating routes:\n" + "\n".join(violations)
    )
