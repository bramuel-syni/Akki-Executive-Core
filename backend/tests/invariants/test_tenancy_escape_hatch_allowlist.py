"""AUDIT_P2.2 — Invariant B: explicit audit-derived allowlist for tenancy
escape hatches (`untenanted=True` kwarg + `# tenancy:allow-no-account-id`
line markers).

The codebase has two existing escape mechanisms for cases where a DB
call is intentionally cross-tenant or row-id-targeted:

  1. `untenanted=True` kwarg on contract-adapter calls (12 callsites in
     product code, defined at `backend/contracts/akki.py:259/287/342` and
     `backend/contracts/synisense.py:89` with full justifications).

  2. `# tenancy:allow-no-account-id` line-marker on direct `db.<col>.find/
     update/...` calls where the call site's tenancy guarantee is
     established by an upstream context-id-gated read or by a cron-level
     cross-tenant operational task.

Both mechanisms are LEGITIMATE — but the user's AUDIT_P2.2 dispatch
required them to be EXPLICITLY audited rather than silently accepted at
scale. This invariant maintains `tenancy_escape_allowlist.yml` as the
single audit-trail register: every existing callsite is enumerated,
each with a justification. Any NEW escape that's not on the list fails
the build.

The contrast with Invariant A (`test_context_route_membership_gate.py`):
  Invariant A: hard ratchet on missing membership gate (silent omission).
  Invariant B: explicit allowlist on documented escapes (auditable).

Per the user's words in the P2.2 dispatch:
  "the 16 untenanted=True callsites and 24+ markers get their own
   explicit, audit-derived allowlists — that's right, because those are
   documented, reasoned exceptions, the opposite of the silent omission
   you caught."
"""
from __future__ import annotations

import ast
import pathlib
import re
from typing import Dict, List, Set, Tuple

import pytest
import yaml


REPO = pathlib.Path(__file__).resolve().parents[3]
BACKEND = REPO / "backend"
ALLOWLIST_FILE = REPO / "backend" / "tests" / "invariants" / "tenancy_escape_allowlist.yml"

MARKER_REGEX = re.compile(r"#.*?tenancy:allow-no-account-id")


def _iter_product_files() -> List[pathlib.Path]:
    """Product code only: skip tests + contract definitions (where the
    `untenanted` kwarg is DEFINED, not used)."""
    out: List[pathlib.Path] = []
    for f in sorted(BACKEND.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        if "/tests/" in str(f):
            continue
        if "/contracts/" in str(f):
            continue
        out.append(f)
    return out


def _scan_untenanted_kwarg_callsites() -> Set[Tuple[str, int]]:
    found: Set[Tuple[str, int]] = set()
    for f in _iter_product_files():
        try:
            src = f.read_text(encoding="utf-8")
            tree = ast.parse(src, str(f))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for kw in (node.keywords or []):
                if (
                    kw.arg == "untenanted"
                    and isinstance(kw.value, ast.Constant)
                    and kw.value.value is True
                ):
                    found.add((str(f.relative_to(REPO)), node.lineno))
                    break
    return found


def _scan_tenancy_allow_markers() -> Set[Tuple[str, int]]:
    """All callsites flagged with `# tenancy:allow-no-account-id`. Skips
    tests; products are auditable. Skip lines inside this scanner file
    itself (where the regex string is defined) and skip lines under
    `/tests/invariants/` so the contract-snapshot fixtures and the
    invariant scanner code don't self-flag."""
    found: Set[Tuple[str, int]] = set()
    for f in BACKEND.rglob("*.py"):
        if "__pycache__" in f.parts:
            continue
        if "/tests/" in str(f):
            continue
        try:
            src = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for ln, line in enumerate(src.splitlines(), start=1):
            if MARKER_REGEX.search(line):
                found.add((str(f.relative_to(REPO)), ln))
    return found


def _load_allowlist() -> Tuple[Set[Tuple[str, int]], Set[Tuple[str, int]]]:
    """Return (untenanted_kwarg_set, marker_set) of (file, line) tuples."""
    if not ALLOWLIST_FILE.exists():
        raise FileNotFoundError(
            f"AUDIT_P2.2 allowlist file not found at {ALLOWLIST_FILE}."
        )
    data = yaml.safe_load(ALLOWLIST_FILE.read_text(encoding="utf-8")) or {}
    u: Set[Tuple[str, int]] = set()
    m: Set[Tuple[str, int]] = set()
    for e in (data.get("untenanted_true_callsites") or []):
        u.add((e["file"], int(e["line"])))
        if not e.get("justification"):
            raise AssertionError(
                f"untenanted_true_callsites entry at {e.get('file')}:{e.get('line')} "
                "MUST have a non-empty 'justification' field."
            )
    for e in (data.get("tenancy_allow_no_account_id_markers") or []):
        m.add((e["file"], int(e["line"])))
        if not e.get("justification"):
            raise AssertionError(
                f"tenancy_allow_no_account_id_markers entry at "
                f"{e.get('file')}:{e.get('line')} MUST have a non-empty "
                "'justification' field."
            )
    return u, m


# ────────────────────────────────────────────────────────────────────────
# Tests
# ────────────────────────────────────────────────────────────────────────


def test_allowlist_yaml_is_well_formed():
    """The allowlist YAML must parse and every entry must have a
    justification. This is the foundation of the audit trail."""
    u, m = _load_allowlist()
    assert len(u) + len(m) >= 1, "allowlist seems empty; check the file"


def test_every_untenanted_kwarg_callsite_is_allowlisted():
    """Any product-code callsite passing `untenanted=True` MUST be in
    the explicit allowlist (with a justification). New escapes need
    audit review."""
    allowed_u, _ = _load_allowlist()
    actual = _scan_untenanted_kwarg_callsites()
    new_unaudited = actual - allowed_u
    assert not new_unaudited, (
        f"{len(new_unaudited)} `untenanted=True` callsite(s) are not in the "
        f"audit-derived allowlist `tenancy_escape_allowlist.yml`. Each new "
        f"escape requires an audit-reviewed entry with a justification.\n\n"
        f"New unaudited callsites:\n" +
        "\n".join(f"  {f}:{l}" for f, l in sorted(new_unaudited))
    )


def test_no_orphaned_untenanted_entries():
    """Every allowlist entry must correspond to a real callsite. Stale
    entries are a maintenance hazard."""
    allowed_u, _ = _load_allowlist()
    actual = _scan_untenanted_kwarg_callsites()
    orphaned = allowed_u - actual
    assert not orphaned, (
        f"{len(orphaned)} stale `untenanted=True` allowlist entries (no "
        f"matching callsite). Remove from `tenancy_escape_allowlist.yml`:\n" +
        "\n".join(f"  {f}:{l}" for f, l in sorted(orphaned))
    )


def test_every_tenancy_allow_marker_is_allowlisted():
    """Any product-code `# tenancy:allow-no-account-id` line marker MUST
    be in the explicit allowlist with a justification."""
    _, allowed_m = _load_allowlist()
    actual = _scan_tenancy_allow_markers()
    new_unaudited = actual - allowed_m
    assert not new_unaudited, (
        f"{len(new_unaudited)} `# tenancy:allow-no-account-id` marker line(s) "
        f"are not in the audit-derived allowlist "
        f"`tenancy_escape_allowlist.yml`. Each new marker requires an "
        f"audit-reviewed entry.\n\n"
        f"New unaudited markers:\n" +
        "\n".join(f"  {f}:{l}" for f, l in sorted(new_unaudited))
    )


def test_no_orphaned_tenancy_allow_marker_entries():
    """Every marker allowlist entry must correspond to a real marker
    line. Stale entries are a maintenance hazard."""
    _, allowed_m = _load_allowlist()
    actual = _scan_tenancy_allow_markers()
    orphaned = allowed_m - actual
    assert not orphaned, (
        f"{len(orphaned)} stale `# tenancy:allow-no-account-id` allowlist "
        f"entries (no matching marker line in product code). Remove from "
        f"`tenancy_escape_allowlist.yml`:\n" +
        "\n".join(f"  {f}:{l}" for f, l in sorted(orphaned))
    )
