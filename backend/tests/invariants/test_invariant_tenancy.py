"""Tenancy invariant — OBSERVE MODE (Phase 0).

Static AST walk over backend/services/ and backend/routers/. Finds
every direct call of the shape

    db.<collection>.<method>(<filter_arg>, ...)

For tenant-scoped collections (allow-list below), records a violation
when the filter Dict literal does not contain an `account_id` key.

Phase 0 contract (observe mode):
  - Violations are SERIALISED to
    `/app/memory/invariants/tenancy_violations.json`.
  - This test asserts the JSON file exists + has the expected schema.
  - The test does NOT fail the build when violation_count > 0.
  - Phase 2 will flip this to enforce mode by adding an assertion
    that violation_count == 0 (or against a regression baseline).

The scanner only sees the DIRECT pattern `db.X.Y(...)`. Variable
indirection (`coll = db.chats; coll.find(...)`), function-returning-
collection helpers, and aggregate-pipeline first-stage $match are
out of scope for Phase 0. The static analysis is a smoke / drift
detector, not a soundness oracle.

The set of "mutating-or-reading" methods we inspect:
  find · find_one · count_documents · distinct
  find_one_and_update · find_one_and_delete · find_one_and_replace
  update_one · update_many · delete_one · delete_many · replace_one

Inserts are scanned in a separate pass: when `insert_one({...})` /
`insert_many([{...}, ...])` is called against a tenant-scoped
collection, the document literal MUST contain `account_id`. Same
observe-mode contract.

Scope notes
-----------
- Test FILES (anything under backend/tests/) are EXCLUDED. Tests
  legitimately seed/inspect rows with custom filters and exempt the
  guarantee.
- Files under backend/scripts/ and backend/migrations/ are EXCLUDED.
  Maintenance scripts run with explicit elevated privilege.
- Lines containing the marker comment `# tenancy:allow-no-account-id`
  are EXCLUDED to give code reviewers a safety valve when a global
  cross-tenant probe is legitimate (admin-only routes, scheduler
  bookkeeping, etc.).

The allow-list of tenant-scoped collections is the canonical Phase 0
seed; Phase 1 Pre-Read will widen / confirm it. New collections SHOULD
be added here as they're introduced.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pytest


# ───────────────────────── allow-list ─────────────────────────
# Phase 0 seed. TODO(Phase 1 Pre-Read): widen / tighten this list
# with the full tenant-scoped catalogue once the data-ownership
# matrix is written (Phase 1.B). The current list is the obvious
# hot-path collections.
#
# NOT included on purpose:
#   - `accounts`     — the row IS the tenant (queries by `id` /
#                      `email` ARE the tenant scope). Including it
#                      yields false positives on every primary-key
#                      lookup.
#   - `memberships`  — link table (account_id, context_id). Both
#                      filter shapes are legitimate; can't be
#                      statically classified by Phase 0's scanner.
#   - shared / admin / cron-scoped collections (e.g. `news_articles`,
#                      `news_sources`, `_migrations`, `synisense_audit_log`,
#                      `synisense_trust_receipts`, `scheduler_locks`,
#                      `audit_invariant_violations`, `solva_engine_runs`)
#                      — not tenant-scoped by design.
TENANT_SCOPED_COLLECTIONS: frozenset = frozenset({
    "analyses",
    "analysis_blobs",
    "briefings",
    "chats",
    "chat_attachments",
    "chat_messages",
    "comments",
    "compilations",
    "contexts",
    "context_assignments",
    "cycles",
    "cycle_assignments",
    "cycle_questions",
    "cycle_responses",
    "decks",
    "document_engagement",
    "document_shares",
    "documents",
    "events",
    "exco_teams",
    "feedback",
    "highlights",
    "ideas_audit_log",
    "ideas_digests",
    "inbound_queue",
    "influence_maps",
    "monitor_status",
    "ned_assignments",
    "pulse_ideas",
    "questions",
    "shared_links",
    "signal_actions",
    "signal_events",
    "signals",
    "solva_v2_sessions",
    "strategic_goals",
    "studio_blocks",
    "studio_documents",
    "tasks",
    "tasks_initiatives",
    "team_catalogue",
    "user_calendar_credentials",
    "user_recent_views",
    "work_studio_exports",
    "work_studio_phase_c_exports",
    "workbook_analyses",
    "workbook_blobs",
})

# Methods that take a `filter` as the first positional argument.
FILTER_METHODS: frozenset = frozenset({
    "find", "find_one", "count_documents", "distinct",
    "find_one_and_update", "find_one_and_delete", "find_one_and_replace",
    "update_one", "update_many",
    "delete_one", "delete_many",
    "replace_one",
})

# Methods that take a DOCUMENT (or list of documents) as the first
# positional argument. The document literal MUST contain account_id.
INSERT_METHODS: frozenset = frozenset({"insert_one", "insert_many"})

# Roots to scan. Tests + scripts + migrations excluded.
SCAN_ROOTS: Tuple[str, ...] = (
    "/app/backend/services",
    "/app/backend/routers",
)

# Files / dirs to exclude even within scan roots.
EXCLUDE_PATH_FRAGMENTS: Tuple[str, ...] = (
    "/__pycache__/",
    "/tests/",
    "/scripts/",
    "/migrations/",
)

# Single-line marker that EXEMPTS a specific source line. Reviewers
# use this when a global cross-tenant query is legitimate.
ESCAPE_HATCH_MARKER = "tenancy:allow-no-account-id"

# Output report path.
REPORT_PATH = Path("/app/memory/invariants/tenancy_violations.json")


# ───────────────────────── helpers ─────────────────────────

def _iter_python_files() -> List[Path]:
    out: List[Path] = []
    for root in SCAN_ROOTS:
        for dirpath, _, filenames in os.walk(root):
            if any(frag in dirpath for frag in EXCLUDE_PATH_FRAGMENTS):
                continue
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                fp = os.path.join(dirpath, fn)
                if any(frag in fp for frag in EXCLUDE_PATH_FRAGMENTS):
                    continue
                out.append(Path(fp))
    return sorted(out)


def _extract_db_call(node: ast.Call) -> Optional[Tuple[str, str]]:
    """If node is `db.<collection>.<method>(...)`, return
    (collection, method). Otherwise return None.
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


def _dict_has_account_id_key(node: ast.AST) -> Optional[bool]:
    """Return True if node is a Dict literal containing an
    `account_id` key, False if it's a Dict without that key, None
    if node is not a Dict literal (we can't statically tell).
    """
    if not isinstance(node, ast.Dict):
        return None
    for k in node.keys:
        if isinstance(k, ast.Constant) and k.value == "account_id":
            return True
        if isinstance(k, ast.Str) and k.s == "account_id":  # py<3.12 hold-over
            return True
    return False


def _list_first_dict_has_account_id_key(node: ast.AST) -> Optional[bool]:
    """For insert_many([{...}, ...]): inspect the first list element."""
    if not isinstance(node, ast.List) or not node.elts:
        return None
    return _dict_has_account_id_key(node.elts[0])


def _line_is_escape_hatched(source_lines: List[str], lineno: int) -> bool:
    """Returns True if the marker comment appears on the call line
    OR on the line directly above (developer convenience).
    """
    idx = lineno - 1
    candidates = source_lines[max(0, idx - 1): idx + 1]
    return any(ESCAPE_HATCH_MARKER in line for line in candidates)


def scan_repo_for_tenancy_violations() -> Dict[str, Any]:
    """Walk every .py file under SCAN_ROOTS. Return a violations
    report dict with shape:

        {
          "scan_timestamp": "...",
          "scan_roots": [...],
          "files_scanned": <int>,
          "tenant_scoped_collections": [...],
          "violations": [
              {"file": "...", "line": N, "collection": "...",
               "method": "...", "kind": "filter"|"insert"|"non_literal"},
              ...
          ],
          "violation_count": <int>,
        }
    """
    from datetime import datetime, timezone
    violations: List[Dict[str, Any]] = []
    files_scanned = 0

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
        files_scanned += 1

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            db_call = _extract_db_call(node)
            if db_call is None:
                continue
            collection, method = db_call
            if collection not in TENANT_SCOPED_COLLECTIONS:
                continue
            if _line_is_escape_hatched(source_lines, node.lineno):
                continue

            first_arg = node.args[0] if node.args else None
            if first_arg is None:
                # No filter/document supplied — e.g. `db.X.find()` returns a cursor over the
                # whole collection. Definite violation.
                violations.append({
                    "file":       str(fp),
                    "line":       node.lineno,
                    "collection": collection,
                    "method":     method,
                    "kind":       "no_args",
                })
                continue

            if method in FILTER_METHODS:
                has = _dict_has_account_id_key(first_arg)
                if has is True:
                    continue
                if has is False:
                    violations.append({
                        "file":       str(fp),
                        "line":       node.lineno,
                        "collection": collection,
                        "method":     method,
                        "kind":       "filter",
                    })
                    continue
                # `has is None` → first arg is not a Dict literal
                # (variable, function call, etc.) — record as
                # `non_literal` (can't statically tell). These DO
                # NOT count against the Phase-2-enforcement
                # baseline; reviewers can manually verify.
                violations.append({
                    "file":       str(fp),
                    "line":       node.lineno,
                    "collection": collection,
                    "method":     method,
                    "kind":       "non_literal",
                })
                continue

            if method in INSERT_METHODS:
                # insert_one(doc) → check doc.
                # insert_many([d1, d2, ...]) → check first list elt.
                if method == "insert_one":
                    has = _dict_has_account_id_key(first_arg)
                else:
                    has = _list_first_dict_has_account_id_key(first_arg)
                if has is True:
                    continue
                if has is False:
                    violations.append({
                        "file":       str(fp),
                        "line":       node.lineno,
                        "collection": collection,
                        "method":     method,
                        "kind":       "insert",
                    })
                    continue
                violations.append({
                    "file":       str(fp),
                    "line":       node.lineno,
                    "collection": collection,
                    "method":     method,
                    "kind":       "non_literal",
                })
                continue

    return {
        "scan_timestamp":              datetime.now(timezone.utc).isoformat(),
        "scan_roots":                  list(SCAN_ROOTS),
        "files_scanned":               files_scanned,
        "tenant_scoped_collections":   sorted(TENANT_SCOPED_COLLECTIONS),
        "filter_methods_inspected":    sorted(FILTER_METHODS),
        "insert_methods_inspected":    sorted(INSERT_METHODS),
        "escape_hatch_marker":         ESCAPE_HATCH_MARKER,
        "violations":                  violations,
        "violation_count":             len(violations),
        "definite_violation_count":    sum(
            1 for v in violations if v["kind"] != "non_literal"
        ),
        "phase":                       "0_observe_mode",
        "phase_2_enforce_target":      "definite_violation_count == 0",
    }


# ───────────────────────── tests ─────────────────────────

def test_tenancy_scan_runs_and_writes_report() -> None:
    """The scanner runs, walks files, and writes the JSON report."""
    report = scan_repo_for_tenancy_violations()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    assert REPORT_PATH.exists()
    assert report["files_scanned"] > 0, (
        f"scanner walked zero files — SCAN_ROOTS may be misconfigured: "
        f"{SCAN_ROOTS!r}"
    )


def test_tenancy_report_has_expected_schema() -> None:
    """Report on disk matches the documented schema."""
    assert REPORT_PATH.exists(), (
        f"report not yet written — run "
        f"test_tenancy_scan_runs_and_writes_report first or "
        f"unconditionally in the sweep"
    )
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    required_top_keys = {
        "scan_timestamp", "scan_roots", "files_scanned",
        "tenant_scoped_collections", "filter_methods_inspected",
        "insert_methods_inspected", "escape_hatch_marker",
        "violations", "violation_count", "definite_violation_count",
        "phase", "phase_2_enforce_target",
    }
    missing = required_top_keys - set(data.keys())
    assert not missing, f"report missing keys: {missing!r}"

    assert data["phase"] == "0_observe_mode"
    assert isinstance(data["violations"], list)
    assert data["violation_count"] == len(data["violations"])
    assert data["definite_violation_count"] == sum(
        1 for v in data["violations"] if v.get("kind") != "non_literal"
    )

    for v in data["violations"]:
        for key in ("file", "line", "collection", "method", "kind"):
            assert key in v, f"violation missing {key!r}: {v!r}"
        assert v["collection"] in TENANT_SCOPED_COLLECTIONS
        assert v["kind"] in {"filter", "insert", "no_args", "non_literal"}


def test_tenancy_observe_mode_does_not_fail_build() -> None:
    """Phase 0 contract — violation_count > 0 is REPORTED but NOT
    a build failure. This test exists to document the contract.
    Phase 2 dispatch will replace this with an enforce-mode assertion.
    """
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    # Just log; do not assert == 0.
    if data["definite_violation_count"] > 0:
        print(
            f"[tenancy observe mode] "
            f"definite_violation_count={data['definite_violation_count']} "
            f"non_literal={data['violation_count'] - data['definite_violation_count']} "
            f"— violations recorded in {REPORT_PATH}"
        )
    assert True  # observe mode never fails


# ─── Schema-shape tests on the scanner internals (catches drift) ───

def test_scanner_detects_synthetic_violation_in_filter_dict() -> None:
    """Synthetic offender → scanner must flag it.

    Proves the scanner has teeth. Synthetic source goes through the
    real `ast.parse` + `_extract_db_call` + `_dict_has_account_id_key`
    chain.
    """
    source = (
        "async def offender(uid: str):\n"
        "    return await db.chats.find_one({'id': uid})\n"
    )
    tree = ast.parse(source)
    found_call: Optional[ast.Call] = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            db_call = _extract_db_call(n)
            if db_call == ("chats", "find_one"):
                found_call = n
                break
    assert found_call is not None, (
        "scanner did not recognise db.chats.find_one(...) shape"
    )
    has = _dict_has_account_id_key(found_call.args[0])
    assert has is False, (
        f"scanner mis-classified synthetic offender as compliant: "
        f"has={has!r}"
    )


def test_scanner_accepts_compliant_filter() -> None:
    """Compliant call must NOT be flagged."""
    source = (
        "async def ok(uid: str, acc: str):\n"
        "    return await db.chats.find_one({'id': uid, 'account_id': acc})\n"
    )
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            db_call = _extract_db_call(n)
            if db_call == ("chats", "find_one"):
                has = _dict_has_account_id_key(n.args[0])
                assert has is True, (
                    f"scanner mis-classified compliant filter: has={has!r}"
                )
                return
    pytest.fail("scanner did not recognise compliant db.chats.find_one(...)")


def test_scanner_handles_escape_hatch_marker() -> None:
    """A line carrying the marker comment is excluded."""
    source = (
        "async def superadmin_all_chats():\n"
        "    # tenancy:allow-no-account-id — superadmin observability\n"
        "    return await db.chats.find()\n"
    )
    source_lines = source.splitlines()
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("chats", "find"):
            assert _line_is_escape_hatched(source_lines, n.lineno) is True, (
                "escape-hatch marker on the preceding line should exempt the call"
            )
            return
    pytest.fail("scanner did not find the find() call")
