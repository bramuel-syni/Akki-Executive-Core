"""Tenancy invariant — Phase 2.1 ENFORCE MODE (per-collection).

Phase 0 shipped this in observe mode. Phase 1 left it observe. Phase 2.1
upgrades the AST walker (Upgrades A + B + C, see §7 of the Phase 2
Pre-Read) and flips ONE collection (`chats`) to enforce mode. Subsequent
Phase 2.x dispatches widen `_ENFORCE_MODE_COLLECTIONS`.

Phase 2.1 upgrades layered on top of the original strict walker:
  - **Upgrade A — multi-line dict literal tracking.**
    When the first arg to a tenant-scoped method is a `Name`, walk
    backward in the same function scope; if the most recent assignment
    of that name is a `Dict` literal, re-classify against the literal.
    Also follows simple `if/else` and post-assignment `subscript`
    additions (`d["account_id"] = x`).

  - **Upgrade B — alternative tenancy key per-collection map.**
    Different collections legitimately use different tenancy keys
    (`owner_account_id` on `contexts`, `assignee_account_id` on
    `cycle_questions`, etc.). The scanner accepts ANY recognised
    tenancy key for that collection. Default fallback (collection not
    in the map) still requires `account_id`.

  - **Upgrade C — `tenant_filter()` / `tenant_doc()` helper call
    recognition.** When the first arg to a tenant-scoped method is a
    `Call` to `tenant_filter` / `tenant_doc` (imported from
    `helpers.tenancy` or aliased), the scanner inspects the helper
    call's `account_id` kwarg + the helper's first positional arg
    (the `extra` dict). The helper guarantees `account_id` is mixed
    in.

Phase 0 contract preserved:
  - Violations SERIALISED to `/app/memory/invariants/tenancy_violations.json`.
  - Schema unchanged. Existing tests still PASS.
  - The `tenancy:allow-no-account-id` marker still exempts a call.

Enforce-mode contract (Phase 2.1+):
  - `_ENFORCE_MODE_COLLECTIONS` is the live list of collections under
    enforce mode. Any violation against these collections fails the
    build. Other collections stay observe.
  - `_ENFORCE_MODE_COLLECTIONS` SHRINKS as Phase 2.2, 2.3, ... migrate
    further contexts — each migration adds the next collection.

Scope notes (UNCHANGED from Phase 0):
  - Test files (anything under backend/tests/) are EXCLUDED.
  - Files under backend/scripts/ and backend/migrations/ are EXCLUDED.
  - Lines carrying `# tenancy:allow-no-account-id` are EXCLUDED.

The set of "mutating-or-reading" methods we inspect:
  find · find_one · count_documents · distinct
  find_one_and_update · find_one_and_delete · find_one_and_replace
  update_one · update_many · delete_one · delete_many · replace_one

Inserts are scanned in a separate pass: when `insert_one({...})` /
`insert_many([{...}, ...])` is called against a tenant-scoped
collection, the document literal MUST contain a recognised tenancy
key. Same observe-mode contract.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

import pytest


# ───────────────────────── allow-list ─────────────────────────
# Phase 0 seed + Phase 2.1 sweep. Collections appearing here MUST
# carry a recognised tenancy key on every filter / insert dict.
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

# ───────────────────────── Phase 2.1 Upgrade B ─────────────────────────
# Alternative tenancy keys recognised per-collection. Sourced from the
# 20-violation sample in PHASE_2_PRE_READ.md §2.B + targeted source
# inspection. Each entry is annotated with the rationale (the code path
# that enforces tenant isolation when the alternative key is present).
#
# Collections NOT in this map fall back to `{"account_id"}` (strict).
ALT_TENANCY_KEYS: Dict[str, FrozenSet[str]] = {
    # contexts: the row IS the tenant. `owner_account_id` field stamps
    # the creating account (routers/contexts.py:264 + sandbox seeds).
    # `id` lookups are tenant-implicit (id is a UUID + the route gates
    # access via require_context_membership).
    "contexts": frozenset({"account_id", "owner_account_id"}),
    # cycles: scoped to `context_id` (membership-gated) + the demo-
    # visibility list `seed_marker_visible_for` (G22, see
    # routers/cycles.py:303). `context_id` alone is sufficient because
    # the route gate requires membership in that context.
    "cycles": frozenset({"account_id", "context_id", "seed_marker_visible_for"}),
    # cycle_questions: scoped to `context_id` (membership-gated) or
    # `assignee_account_id` (Q4Y P0 — per-user assigned questions).
    "cycle_questions": frozenset({
        "account_id", "context_id", "assignee_account_id",
    }),
    # questions: same pattern as cycle_questions — context-scoped via
    # membership gate + per-user assignment.
    "questions": frozenset({
        "account_id", "context_id", "assignee_account_id",
    }),
    # documents: scoped to `context_id` (membership-gated) + the
    # `uploaded_by` field for legacy single-user lookups. Phase 2.2
    # adds `task_id` — documents linked to a task inherit the task's
    # tenancy (tasks are account_id-scoped; the task lookup gates
    # the document access upstream).
    "documents": frozenset({"account_id", "context_id", "uploaded_by", "task_id"}),
    # compilations: scoped to `context_id` (membership-gated) + the
    # `created_by` field on the rec (routers/compilations.py:116).
    "compilations": frozenset({"account_id", "context_id", "created_by"}),
    # studio_blocks: parent artefact is context-scoped; rows carry
    # `context_id` for collation under the work studio composer.
    "studio_blocks": frozenset({"account_id", "context_id"}),
    # cycle_assignments: scoped by `context_id` (cycle is context-bound)
    # OR `assignee_account_id`.
    "cycle_assignments": frozenset({
        "account_id", "context_id", "assignee_account_id",
    }),
    # decks / studio_documents / signal_actions / signal_events /
    # signals / briefings / events / influence_maps / monitor_status /
    # pulse_ideas / strategic_goals: all context-scoped through their
    # owning context + the route's membership gate.
    "decks": frozenset({"account_id", "context_id"}),
    "studio_documents": frozenset({"account_id", "context_id"}),
    "signal_actions": frozenset({"account_id", "context_id"}),
    "signal_events": frozenset({"account_id", "context_id"}),
    "signals": frozenset({"account_id", "context_id"}),
    "briefings": frozenset({"account_id", "context_id"}),
    "events": frozenset({"account_id", "context_id"}),
    "influence_maps": frozenset({"account_id", "context_id"}),
    "monitor_status": frozenset({"account_id", "context_id"}),
    "pulse_ideas": frozenset({"account_id", "context_id"}),
    "strategic_goals": frozenset({"account_id", "context_id"}),
    # work_studio_exports + workbook_analyses + workbook_blobs +
    # analyses + analysis_blobs: context-scoped, route-gated.
    "work_studio_exports": frozenset({"account_id", "context_id"}),
    "work_studio_phase_c_exports": frozenset({"account_id", "context_id"}),
    "workbook_analyses": frozenset({"account_id", "context_id"}),
    "workbook_blobs": frozenset({"account_id", "context_id"}),
    "analyses": frozenset({"account_id", "context_id"}),
    "analysis_blobs": frozenset({"account_id", "context_id"}),
    # tasks / tasks_initiatives: account_id is the canonical key
    # (routers/tasks.py:207); `owner_id` is a contributor reference,
    # NOT tenant scope. Phase 2.5 adds `task_id` for contributor-token-
    # gated paths that look up the row by `{"id": task_id}` after
    # _resolve_contributor_token validated the token.
    "tasks": frozenset({"account_id", "context_id", "task_id"}),
    # chat_messages: scoped by `chat_id` (parent chat row is
    # account_id-gated; messages inherit the parent's tenancy). Phase 2.5
    # widens to recognise the chat_id-keyed lookups in trust_center,
    # work_studio_from_source, work_studio_phase_c, and the backfill
    # services.
    "chat_messages": frozenset({"account_id", "chat_id"}),
    # user_calendar_credentials: scoped by `user_id` (alias for
    # account_id on this collection — see routers/account_deletion.py:182
    # `delete_many({"user_id": account_id})`). Phase 2.5 alt-key widening.
    "user_calendar_credentials": frozenset({"account_id", "user_id"}),
    # cycle_assignments: NED-keyed via `ned_id` (the assignee), or
    # gated by the parent brief (`brief_id`) which is itself
    # context_id-gated. Phase 2.5 adds both keys.
    "cycle_assignments": frozenset({
        "account_id", "context_id", "assignee_account_id",
        "ned_id", "brief_id",
    }),
    # studio_blocks: scoped by `artefact_id` (the parent artefact row
    # is context_id-gated via `_resolve_artefact` upstream). Phase 2.5
    # adds `artefact_id` to the alt-keys for static recognition + uses
    # the `_resolve_artefact` helper-fusion (TENANT_GATE_HELPERS below).
    "studio_blocks": frozenset({"account_id", "context_id", "artefact_id"}),
    # team_catalogue: context-scoped via membership (route is
    # `/contexts/{context_id}/team-catalogue/{member_id}`). Phase 2.5
    # adds `member_id` (the row's own primary key — gated by the
    # context-membership upstream).
    "team_catalogue": frozenset({"account_id", "context_id", "member_id"}),
    "tasks_initiatives": frozenset({"account_id", "context_id"}),
    # exco_teams: context-scoped via membership. Phase 2.5 adds
    # `team_id` (the row's own primary key — handlers are at
    # `/contexts/{context_id}/exco-teams/{team_id}`).
    "exco_teams": frozenset({"account_id", "context_id", "team_id"}),
    # ideas_audit_log + ideas_digests: account-scoped or context-scoped.
    "ideas_audit_log": frozenset({"account_id", "context_id"}),
    "ideas_digests": frozenset({"account_id", "context_id"}),
    # document_engagement / document_shares / shared_links / highlights:
    # owning-document is context-scoped; rows reference doc_id +
    # context_id.
    "document_engagement": frozenset({"account_id", "context_id"}),
    "document_shares": frozenset({"account_id", "context_id"}),
    "shared_links": frozenset({"account_id", "context_id"}),
    "highlights": frozenset({"account_id", "context_id"}),
    # comments + feedback: context-scoped or per-user.
    "comments": frozenset({"account_id", "context_id"}),
    "feedback": frozenset({"account_id", "context_id"}),
    # cycle_responses + context_assignments + ned_assignments: scoped
    # via context_id.
    "cycle_responses": frozenset({"account_id", "context_id"}),
    "context_assignments": frozenset({"account_id", "context_id"}),
    "ned_assignments": frozenset({"account_id", "context_id"}),
    # solva_v2_sessions: account_id canonical (routers/solva_v2.py:1070).
    # inbound_queue: account_id canonical, but row is also stamped with
    # `context_id` on every inbound write (routers/inbound_email.py
    # produces `{context_id, account_id}` payloads via the mailbox
    # router; routers/inbound_queue.py reads gate on
    # `Depends(require_context_membership())`). Phase 2.5a widens to
    # accept `context_id` as a recognised key.
    "inbound_queue": frozenset({"account_id", "context_id"}),
    # chat_attachments: account_id canonical (parent chat is account-
    # gated; attachments inherit). Phase 2.5a adds `chat_id` for the
    # parent-chat-gated lookups.
    "chat_attachments": frozenset({"account_id", "chat_id"}),
    # user_recent_views: account_id canonical.
}


def _allowed_keys_for(collection: str) -> FrozenSet[str]:
    """Return the set of recognised tenancy keys for the given
    collection. Defaults to {"account_id"} for collections not
    explicitly mapped — strict mode."""
    return ALT_TENANCY_KEYS.get(collection, frozenset({"account_id"}))


# ───────────────────────── Phase 2.4 Upgrade D — helper-fusion ──────────
# For collections where the tenancy contract is enforced by a tenant-vetted
# helper (rather than by a key-on-the-filter literal), the scanner accepts
# a `db.<collection>.<method>(...)` call as compliant iff a matching helper
# call appears earlier in the same function scope OR the function is
# decorated with a FastAPI `Depends(helper_factory(...))` dependency.
#
# Recognised helpers per collection (Phase 2.4 Pre-Read §2 audit confirmed
# both helpers enforce tenancy via memberships-collection lookup + raise
# 403 on miss).
TENANT_GATE_HELPERS: Dict[str, FrozenSet[str]] = {
    "contexts": frozenset({
        # core.py:249 — `require_context_membership(owner_only=False)`
        # returns a FastAPI Dependency `_dep` that verifies
        # (account_id, context_id, status=active) in memberships before
        # returning {account, context, membership}. Used via
        # `ctx = Depends(require_context_membership())` in handler signatures.
        "require_context_membership",
        # ned_cycle.py:164 — `_verify_ned_context(account_id, context_id)`
        # verifies (account_id, context_id, role=ned, status=active) in
        # memberships and returns the resolved context row.
        "_verify_ned_context",
    }),
    "studio_blocks": frozenset({
        # routers/studio_blocks.py:444 — `_resolve_artefact(kind, aid,
        # account)` finds the parent artefact row by id, verifies
        # `context_id`, then verifies `(account_id, context_id,
        # status=active)` in memberships; raises 403 on miss. Every
        # `db.studio_blocks.<method>` call inside `studio_blocks.py`
        # handlers happens AFTER this resolver succeeds, so the
        # `artefact_id` (or parent-artefact-derived `context_id`) on the
        # filter is already proven to belong to the caller. Same shape
        # as the `contexts` helper-fusion contract; the alt-key
        # `artefact_id` ALSO resolves these statically — the helper
        # fusion is the architectural ground truth, alt-key is the
        # belt-and-braces.
        "_resolve_artefact",
    }),
}

# Functions whose OWN body implements one of the helpers above. Their
# `db.contexts.find_one({"id": context_id})` calls ARE the tenancy
# contract — they're not consumers of it. The scanner skips checks
# inside these specific function bodies (per the collection they gate).
#
# Hard-coded set; growth requires a PR-reviewed scanner edit (treated as
# documentation, not config — per Phase 2.4 Pre-Read §7 design ack).
_CONTEXT_HELPER_FUNCTIONS: FrozenSet[str] = frozenset({
    "_dep",                  # inner closure of require_context_membership()
    "_verify_ned_context",   # the NED helper itself
    "_resolve_artefact",     # studio_blocks artefact resolver (Phase 2.5a)
})


# ───────────────────────── Phase 2.1 enforce-mode list ─────────────────
# Collections currently under enforce mode. Adding a collection here
# means any violation against that collection FAILS the build.
# SHRINKS DOWNWARD as Phase 2.2, 2.3, ... migrate further contexts.
#
# Phase 2.1 ships with `chats` first per dispatch directive — highest-
# traffic surface, full Phase 0 + Phase 14 lockdown coverage.
# Phase 2.2 adds `documents` — second-context per Pre-Read §5.A.2
# verbatim recommendation; 32→0 via task_id alt-key widening + 23
# markers.
# Phase 2.3 adds `work_studio_exports` — third-context per Phase 2.2 §8.A
# recommendation; 24→0 via 20 defensive context_id adds + 4 markers.
# Phase 2.4 adds `contexts` — fourth-context per Phase 2.4 Pre-Read §8
# hybrid (Upgrade D helper-fusion + helper-body exemption + markers).
# Phase 2.5a adds 7 more: `inbound_queue`, `tasks`, `chat_messages`,
# `user_calendar_credentials`, `signals`, `cycles`, `solva_v2_sessions`.
_ENFORCE_MODE_COLLECTIONS: FrozenSet[str] = frozenset({
    "chats",
    "documents",
    "work_studio_exports",
    "contexts",
    # Phase 2.5a additions (all 7 reached 0 via alt-key widening + markers).
    "inbound_queue",
    "tasks",
    "chat_messages",
    "user_calendar_credentials",
    "signals",
    "cycles",
    "solva_v2_sessions",
})


# ───────────────────────── Phase 2.5a — cross-tenant whitelist ─────────
# Collections that legitimately store rows WITHOUT a per-tenant key
# because they exist at a global/system layer (pre-account, audit-only,
# webhook log, telemetry, cron-state, etc.). These collections are
# considered OUT-OF-SCOPE for the tenancy scanner by design — adding
# `account_id` would be semantically wrong (the row predates / spans /
# audits accounts).
#
# Invariant enforced by `test_cross_tenant_whitelist_disjoint_from_scoped`:
#   `_CROSS_TENANT_COLLECTIONS & TENANT_SCOPED_COLLECTIONS == ∅`
#
# This list is a formal paper trail per Phase 2.5a brief — it does NOT
# control scanner behaviour today (anything outside `TENANT_SCOPED_COLLECTIONS`
# is already not checked). It exists so a future agent reviewing
# "why is collection X unchecked?" gets an immediate, dated rationale
# rather than relying on the absence of a declaration. Growth requires
# explicit per-entry rationale.
_CROSS_TENANT_COLLECTIONS: FrozenSet[str] = frozenset({
    # ── Identity / pre-account ─────────────────────────────────────
    "accounts",                  # The accounts collection itself; queried by id/email/cohort.
    "memberships",               # The (account_id, context_id) JOIN; cross by definition.
    "context_members",           # Legacy alias for memberships in some paths.
    "invitations",               # Pre-account: an invite has no account_id yet.
    "revoked_jtis",              # JWT revocation list; queried by jti globally.
    "oauth_pkce_verifiers",      # Pre-account OAuth state; queried by state key.
    "login_attempts",            # Brute-force gate; queried by email/IP, pre-auth.
    # ── Cohort onboarding (pre-account) ─────────────────────────────
    "cohorts",
    "cohort_applications",
    "cohort_application_audit",
    "cohort_copy_overrides",
    "cohort_email_events",
    "cohort_invites",
    "cohort_magic_links",
    "cohort_special_asks",
    "cohort_waitlist",
    # ── Early-access / interest forms (pre-account) ─────────────────
    "early_access_applications",
    "early_access_optins",
    "early_access_registrations",
    "enterprise_interest",
    "billing_launch_interest",
    # ── System audit / telemetry / cron-state ──────────────────────
    "audit_log",                 # System audit; rows tagged with `account_id` opportunistically but not as a tenancy gate.
    "audit_invariant_violations",
    "auth_events",
    "chat_audit_log",
    "feature_events",
    "telemetry_events",
    "scheduler_runs",
    "model_fallback_log",
    "llm_deep_usage",
    "llm_retry_log",
    "extraction_failures",
    "extractions_log",
    "backfill_jobs",
    "backfill_log",
    "async_jobs",
    # ── Synisense Shield audit (cross-tenant by Shield contract) ────
    "synisense_audit_log",
    "synisense_runs",
    "synisense_shield_maps",
    "synisense_trust_receipts",
    # ── External webhook logs ───────────────────────────────────────
    "stripe_events",
    "stripe_dead_letter",
    "inbound_queue_raw",          # Raw email payload mirror; carries context_id but the inbound_queue normalised row is the tenant-scoped surface.
    "inbox_routing_log",
    # ── Public content ─────────────────────────────────────────────
    "blog_posts",
    "blog_subscribers",
    "news_items",
})


# Invariant: cross-tenant whitelist MUST be disjoint from the
# tenant-scoped allow-list. Adding the same collection to both is a
# contradiction. (Test: `test_cross_tenant_whitelist_disjoint_from_scoped`.)
_CROSS_TENANT_OVERLAP: FrozenSet[str] = _CROSS_TENANT_COLLECTIONS & TENANT_SCOPED_COLLECTIONS


# Methods that take a `filter` as the first positional argument.
FILTER_METHODS: frozenset = frozenset({
    "find", "find_one", "count_documents", "distinct",
    "find_one_and_update", "find_one_and_delete", "find_one_and_replace",
    "update_one", "update_many",
    "delete_one", "delete_many",
    "replace_one",
})

# Methods that take a DOCUMENT (or list of documents) as the first
# positional argument. The document literal MUST contain a recognised
# tenancy key.
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


def _dict_has_any_recognised_key(
    node: ast.AST, allowed: FrozenSet[str],
) -> Optional[bool]:
    """Return True if node is a Dict literal containing ANY key from
    `allowed`, False if it's a Dict without any of them, None if node
    is not a Dict literal (we can't statically tell).

    Note: dict spreads `{**other, ...}` are represented as a key of
    None in the ast.Dict. This function does NOT follow the spread
    by itself — see `_dict_or_spread_has_recognised_key()` for the
    scanner-level extension that resolves spreads against the
    enclosing function scope.
    """
    if not isinstance(node, ast.Dict):
        return None
    for k in node.keys:
        if isinstance(k, ast.Constant) and k.value in allowed:
            return True
        if isinstance(k, ast.Str) and k.s in allowed:  # py<3.12 hold-over
            return True
    return False


def _dict_or_spread_has_recognised_key(
    node: ast.AST,
    allowed: FrozenSet[str],
    tree: ast.AST,
    call_node: ast.Call,
) -> Optional[bool]:
    """Phase 2.1 Upgrade A.2 — spread-aware dict scanning.

    Handles `{**other, "k": v}` shape: if `other` is a Name we can
    resolve in the enclosing function scope, union its keys with the
    literal's own keys and check the union against `allowed`.
    Returns:
      True  — any source carries an allowed key.
      False — definitively no allowed key across literal + spreads.
      None  — first-arg is not a Dict literal (caller falls through
              to the existing Name-resolution path).
    """
    if not isinstance(node, ast.Dict):
        return None

    # Collect literal keys.
    own_keys: Set[str] = set()
    spread_sources: List[str] = []
    for k, v in zip(node.keys, node.values):
        if k is None:
            # Spread: `**other`. Capture the source if it's a Name.
            if isinstance(v, ast.Name):
                spread_sources.append(v.id)
            elif isinstance(v, ast.Dict):
                # Nested literal in spread — recurse.
                nested = _dict_or_spread_has_recognised_key(
                    v, allowed, tree, call_node,
                )
                if nested is True:
                    return True
            continue
        if isinstance(k, ast.Constant) and isinstance(k.value, str):
            own_keys.add(k.value)
        elif isinstance(k, ast.Str):
            own_keys.add(k.s)

    if own_keys & allowed:
        return True

    if not spread_sources:
        return False

    # Spread sources present — resolve each via the function scope.
    enc = _enclosing_function(tree, call_node)
    if enc is None:
        return False

    for src in spread_sources:
        _, src_keys = _resolve_name_to_dict_keys(enc, src, call_node.lineno)
        if src_keys & allowed:
            return True

    return False


def _list_first_dict_has_any_recognised_key(
    node: ast.AST, allowed: FrozenSet[str],
) -> Optional[bool]:
    """For insert_many([{...}, ...]): inspect the first list element."""
    if not isinstance(node, ast.List) or not node.elts:
        return None
    return _dict_has_any_recognised_key(node.elts[0], allowed)


def _line_is_escape_hatched(source_lines: List[str], lineno: int) -> bool:
    """Returns True if the marker comment appears on the call line
    OR on the line directly above (developer convenience).
    """
    idx = lineno - 1
    candidates = source_lines[max(0, idx - 1): idx + 1]
    return any(ESCAPE_HATCH_MARKER in line for line in candidates)


# ───────────────────────── Phase 2.1 Upgrade A — multi-line dict tracking ──

def _enclosing_function(
    tree: ast.AST, target: ast.Call,
) -> Optional[ast.AST]:
    """Return the FunctionDef / AsyncFunctionDef that lexically contains
    `target`, or None if it's at module scope. Naive single-pass walk;
    fine for our scanner-call counts."""
    found: List[ast.AST] = []

    class _Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: List[ast.AST] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
            self.stack.append(node)
            self.generic_visit(node)
            self.stack.pop()

        def visit_AsyncFunctionDef(  # noqa: N802
            self, node: ast.AsyncFunctionDef,
        ) -> None:
            self.stack.append(node)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
            if node is target and self.stack:
                found.append(self.stack[-1])
            self.generic_visit(node)

    _Visitor().visit(tree)
    return found[0] if found else None


def _resolve_name_to_dict_keys(
    func_node: ast.AST, name: str, before_lineno: int,
) -> Tuple[Optional[ast.Dict], Set[str]]:
    """Walk the function body forward; collect dict-literal assignment
    state + subsequent `d["key"] = ...` subscript assignments for the
    given Name, up to (but not including) `before_lineno`.

    Returns (last_dict_literal_node, set_of_known_keys). The
    last_dict_literal_node is the most recent `name = {...}` (or None
    if not seen as a dict literal). The set_of_known_keys includes
    keys from that literal PLUS any subsequent `name["key"] = ...`
    statements lexically before `before_lineno`.

    Handles:
      - `name = {...}`           (Assign with Dict value)
      - `name["k"] = ...`        (subscript assignment after init)
      - `name.update({...})`     (limited — only inline Dict args)
      - `name = dict(other, k=v)` / `dict(...)` calls — best-effort:
        we treat `dict(other_name, ...)` as "inherit other_name's keys
        plus the kwargs", capped to the current function's other_name
        tracking.

    Limitations (recorded; observe-mode acceptable):
      - Cross-function dict construction (helper returns dict).
      - Conditional `if user: name["account_id"] = ...` — we conservatively
        UNION keys across branches even though they may not always fire.
      - Dict comprehension assignments.
    """
    keys: Set[str] = set()
    last_lit: Optional[ast.Dict] = None

    for stmt in ast.walk(func_node):
        # Filter to statements lexically before the use.
        if not hasattr(stmt, "lineno") or stmt.lineno >= before_lineno:
            continue

        # Phase 2.1 Upgrade A fix — handle annotated assignments
        # `name: T = {...}` (ast.AnnAssign) in addition to plain
        # `name = {...}` (ast.Assign). The two AST shapes are
        # semantically identical for our purposes; we treat AnnAssign
        # as a single-target Assign by synthesising the target list.
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value is not None:
            if stmt.target.id == name:
                if isinstance(stmt.value, ast.Dict):
                    last_lit = stmt.value
                    keys = set()
                    for k in stmt.value.keys:
                        if isinstance(k, ast.Constant) and isinstance(
                            k.value, str,
                        ):
                            keys.add(k.value)
                        elif isinstance(k, ast.Str):
                            keys.add(k.s)
                else:
                    keys = set()
                    last_lit = None

        # `name = {...}` (initial or replacement assignment)
        if isinstance(stmt, ast.Assign):
            for tgt in stmt.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    if isinstance(stmt.value, ast.Dict):
                        last_lit = stmt.value
                        # Reset keys to ONLY this literal's keys; the
                        # name was just rebound to a new dict.
                        keys = set()
                        for k in stmt.value.keys:
                            if isinstance(k, ast.Constant) and isinstance(
                                k.value, str,
                            ):
                                keys.add(k.value)
                            elif isinstance(k, ast.Str):
                                keys.add(k.s)
                    elif isinstance(stmt.value, ast.Call):
                        # `name = dict(other, k=v)` — track kwargs.
                        if (
                            isinstance(stmt.value.func, ast.Name)
                            and stmt.value.func.id == "dict"
                        ):
                            new_keys: Set[str] = set()
                            for kw in stmt.value.keywords:
                                if kw.arg is not None:
                                    new_keys.add(kw.arg)
                            # The positional arg may be a `Name` that
                            # itself is a dict variable — recurse.
                            for pos in stmt.value.args:
                                if isinstance(pos, ast.Name):
                                    _, src_keys = _resolve_name_to_dict_keys(
                                        func_node, pos.id, stmt.lineno,
                                    )
                                    new_keys |= src_keys
                                elif isinstance(pos, ast.Dict):
                                    for k in pos.keys:
                                        if isinstance(k, ast.Constant) and isinstance(
                                            k.value, str,
                                        ):
                                            new_keys.add(k.value)
                                        elif isinstance(k, ast.Str):
                                            new_keys.add(k.s)
                            keys = new_keys
                            last_lit = None  # synthesised, not a literal
                        else:
                            # Some other call returning a dict — opaque.
                            keys = set()
                            last_lit = None
                    else:
                        # Variable assigned from another expression we
                        # can't statically tell — opaque.
                        keys = set()
                        last_lit = None

        # `name["k"] = ...` (subscript assignment)
        elif isinstance(stmt, ast.Assign):
            # Handled above already.
            pass

        # The walk above covers most cases. Now handle subscript
        # assignments specifically — they're a separate Assign node
        # where the target is a Subscript.
        if isinstance(stmt, ast.Assign):
            for tgt in stmt.targets:
                if (
                    isinstance(tgt, ast.Subscript)
                    and isinstance(tgt.value, ast.Name)
                    and tgt.value.id == name
                ):
                    sl = tgt.slice
                    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                        keys.add(sl.value)
                    elif isinstance(sl, ast.Str):
                        keys.add(sl.s)

    return last_lit, keys


# ───────────────────────── Phase 2.1 Upgrade C — helper-call recognition ──

_TENANCY_HELPERS = frozenset({"tenant_filter", "tenant_doc"})


def _is_tenancy_helper_call(node: ast.AST) -> Optional[ast.Call]:
    """Return the Call node if `node` is a call to tenant_filter() /
    tenant_doc(), else None."""
    if not isinstance(node, ast.Call):
        return None
    fn = node.func
    if isinstance(fn, ast.Name) and fn.id in _TENANCY_HELPERS:
        return node
    if isinstance(fn, ast.Attribute) and fn.attr in _TENANCY_HELPERS:
        return node
    return None


def _helper_call_supplies_account_id(call: ast.Call) -> bool:
    """A `tenant_filter()` / `tenant_doc()` call is compliant iff it
    passes `account_id=...` as a keyword argument. The helper itself
    raises ValueError on falsy, so we only need to verify it's
    present in the call surface."""
    for kw in call.keywords:
        if kw.arg == "account_id":
            return True
    return False


# ───────────────────────── Phase 2.4 Upgrade D — helper-fusion ──────────

def _function_has_dependency_on_helper(
    func_node: ast.AST, helper_names: FrozenSet[str],
) -> bool:
    """Phase 2.4 Upgrade D — FastAPI dependency detection.

    Returns True if `func_node` has any positional or keyword-only argument
    whose default value is `Depends(<helper>(...))` for any helper in
    `helper_names`. The dependency is resolved BEFORE the function body
    runs, so the tenancy gate is established for the entire function
    scope.

    Recognises both shapes:
      - `Depends(require_context_membership())`           — bare factory
      - `Depends(require_context_membership(owner_only=True))` — factory call
    """
    if not isinstance(func_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    defaults = list(func_node.args.defaults) + list(
        func_node.args.kw_defaults or []
    )
    for d in defaults:
        if not isinstance(d, ast.Call):
            continue
        # Depends(...) wrapper
        fn = d.func
        if isinstance(fn, ast.Name) and fn.id == "Depends":
            pass
        elif isinstance(fn, ast.Attribute) and fn.attr == "Depends":
            pass
        else:
            continue
        # Inspect the argument inside Depends(...)
        if not d.args:
            continue
        inner = d.args[0]
        # Pattern A: Depends(helper) — bare reference
        if isinstance(inner, ast.Name) and inner.id in helper_names:
            return True
        if isinstance(inner, ast.Attribute) and inner.attr in helper_names:
            return True
        # Pattern B: Depends(helper(...)) — factory invocation
        if isinstance(inner, ast.Call):
            ifn = inner.func
            if isinstance(ifn, ast.Name) and ifn.id in helper_names:
                return True
            if isinstance(ifn, ast.Attribute) and ifn.attr in helper_names:
                return True
    return False


def _function_calls_helper_before(
    func_node: ast.AST, helper_names: FrozenSet[str], before_lineno: int,
) -> bool:
    """Phase 2.4 Upgrade D — direct-call detection.

    Returns True if any `Call` node to one of `helper_names` exists in
    the function body BEFORE `before_lineno`. Covers the
    `await _verify_ned_context(aid, ctx_id)` pattern where the helper
    is invoked explicitly inside the function body (rather than via
    FastAPI dependency injection).
    """
    if not isinstance(func_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    for n in ast.walk(func_node):
        if not isinstance(n, ast.Call):
            continue
        if getattr(n, "lineno", 0) >= before_lineno:
            continue
        fn = n.func
        if isinstance(fn, ast.Name) and fn.id in helper_names:
            return True
        if isinstance(fn, ast.Attribute) and fn.attr in helper_names:
            return True
    return False


def _is_helper_body(func_node: ast.AST) -> bool:
    """Phase 2.4 helper-body exemption.

    Returns True if `func_node` is one of the recognised tenant-gate
    helper implementations. Their `db.contexts.find_one(...)` calls
    ARE the tenancy contract — not consumers of it.
    """
    if not isinstance(func_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    return func_node.name in _CONTEXT_HELPER_FUNCTIONS


def _tenancy_satisfied_by_helper_fusion(
    tree: ast.AST,
    call_node: ast.Call,
    collection: str,
) -> bool:
    """Phase 2.4 Upgrade D entry point.

    Returns True if the contexts-collection call is tenancy-satisfied
    by helper-fusion: either (a) the enclosing function IS a recognised
    helper body (exemption), or (b) a recognised tenant-gate helper was
    invoked earlier in the function's lexical scope OR injected as a
    FastAPI dependency.
    """
    helpers = TENANT_GATE_HELPERS.get(collection)
    if not helpers:
        return False
    enc = _enclosing_function(tree, call_node)
    if enc is None:
        return False
    # (a) helper-body exemption
    if _is_helper_body(enc):
        return True
    # (b1) FastAPI Depends(...) on a recognised helper
    if _function_has_dependency_on_helper(enc, helpers):
        return True
    # (b2) direct call to a recognised helper before our line
    if _function_calls_helper_before(enc, helpers, call_node.lineno):
        return True
    return False


# ───────────────────────── core scanner ─────────────────────────

def scan_repo_for_tenancy_violations() -> Dict[str, Any]:
    """Walk every .py file under SCAN_ROOTS. Return a violations
    report dict.
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

            # Phase 2.4 Upgrade D — helper-fusion check (currently only
            # consulted for `contexts`; per-collection map in
            # TENANT_GATE_HELPERS). Treat the call as compliant if a
            # tenant-vetted helper was injected (Depends) or invoked
            # earlier in the same function — OR if the call is INSIDE
            # the helper body itself (exemption).
            if _tenancy_satisfied_by_helper_fusion(tree, node, collection):
                continue

            allowed = _allowed_keys_for(collection)

            first_arg = node.args[0] if node.args else None
            if first_arg is None:
                violations.append({
                    "file":       str(fp),
                    "line":       node.lineno,
                    "collection": collection,
                    "method":     method,
                    "kind":       "no_args",
                })
                continue

            # Phase 2.1 Upgrade C — helper call recognition.
            helper = _is_tenancy_helper_call(first_arg)
            if helper is not None:
                if _helper_call_supplies_account_id(helper):
                    continue
                violations.append({
                    "file":       str(fp),
                    "line":       node.lineno,
                    "collection": collection,
                    "method":     method,
                    "kind":       "helper_no_account_id",
                })
                continue

            if method in FILTER_METHODS:
                # Phase 2.1 Upgrade A.2 — spread-aware check first.
                # Covers `{**chat_filter, "title": rx}` shape where
                # the literal alone has no allowed key but the spread
                # source is a resolvable Name carrying account_id.
                has = _dict_or_spread_has_recognised_key(
                    first_arg, allowed, tree, node,
                )
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
                # `has is None` → first arg is not a Dict literal.
                # Phase 2.1 Upgrade A — try multi-line dict tracking.
                if isinstance(first_arg, ast.Name):
                    enc = _enclosing_function(tree, node)
                    if enc is not None:
                        _, known_keys = _resolve_name_to_dict_keys(
                            enc, first_arg.id, node.lineno,
                        )
                        if known_keys & allowed:
                            continue  # compliant via Upgrade A
                # Could not resolve statically — record as non_literal.
                violations.append({
                    "file":       str(fp),
                    "line":       node.lineno,
                    "collection": collection,
                    "method":     method,
                    "kind":       "non_literal",
                })
                continue

            if method in INSERT_METHODS:
                if method == "insert_one":
                    has = _dict_has_any_recognised_key(first_arg, allowed)
                else:
                    has = _list_first_dict_has_any_recognised_key(first_arg, allowed)
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
                # `has is None` — Upgrade A for insert_one taking a Name.
                if method == "insert_one" and isinstance(first_arg, ast.Name):
                    enc = _enclosing_function(tree, node)
                    if enc is not None:
                        _, known_keys = _resolve_name_to_dict_keys(
                            enc, first_arg.id, node.lineno,
                        )
                        if known_keys & allowed:
                            continue
                # insert_one(rec.copy()) / insert_one(dict(rec)) — peek
                # one level into the Call.
                if (
                    method == "insert_one"
                    and isinstance(first_arg, ast.Call)
                ):
                    inner = first_arg.func
                    target_name: Optional[str] = None
                    if (
                        isinstance(inner, ast.Attribute)
                        and inner.attr == "copy"
                        and isinstance(inner.value, ast.Name)
                    ):
                        target_name = inner.value.id
                    elif (
                        isinstance(inner, ast.Name)
                        and inner.id == "dict"
                        and first_arg.args
                        and isinstance(first_arg.args[0], ast.Name)
                    ):
                        target_name = first_arg.args[0].id
                    if target_name is not None:
                        enc = _enclosing_function(tree, node)
                        if enc is not None:
                            _, known_keys = _resolve_name_to_dict_keys(
                                enc, target_name, node.lineno,
                            )
                            if known_keys & allowed:
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
        "alt_tenancy_keys":            {
            k: sorted(v) for k, v in ALT_TENANCY_KEYS.items()
        },
        "enforce_mode_collections":    sorted(_ENFORCE_MODE_COLLECTIONS),
        "filter_methods_inspected":    sorted(FILTER_METHODS),
        "insert_methods_inspected":    sorted(INSERT_METHODS),
        "escape_hatch_marker":         ESCAPE_HATCH_MARKER,
        "violations":                  violations,
        "violation_count":             len(violations),
        "definite_violation_count":    sum(
            1 for v in violations if v["kind"] != "non_literal"
        ),
        "phase":                       "2.1_per_collection_enforce",
        "phase_2_enforce_target":      "definite_violation_count == 0 for enforce_mode_collections",
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
    assert report["files_scanned"] > 0


def test_tenancy_report_has_expected_schema() -> None:
    """Report on disk matches the documented schema."""
    assert REPORT_PATH.exists()
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    required_top_keys = {
        "scan_timestamp", "scan_roots", "files_scanned",
        "tenant_scoped_collections", "alt_tenancy_keys",
        "enforce_mode_collections",
        "filter_methods_inspected",
        "insert_methods_inspected", "escape_hatch_marker",
        "violations", "violation_count", "definite_violation_count",
        "phase", "phase_2_enforce_target",
    }
    missing = required_top_keys - set(data.keys())
    assert not missing, f"report missing keys: {missing!r}"

    assert data["phase"] == "2.1_per_collection_enforce"
    assert isinstance(data["violations"], list)
    assert data["violation_count"] == len(data["violations"])
    assert data["definite_violation_count"] == sum(
        1 for v in data["violations"] if v.get("kind") != "non_literal"
    )

    for v in data["violations"]:
        for key in ("file", "line", "collection", "method", "kind"):
            assert key in v, f"violation missing {key!r}: {v!r}"
        assert v["collection"] in TENANT_SCOPED_COLLECTIONS
        assert v["kind"] in {
            "filter", "insert", "no_args", "non_literal",
            "helper_no_account_id",
        }


# ───── Phase 2.1 ENFORCE MODE — per-collection ─────

def test_tenancy_enforce_mode_for_migrated_collections() -> None:
    """Phase 2.1 ENFORCE — collections listed in
    `_ENFORCE_MODE_COLLECTIONS` MUST have zero definite violations.
    Other collections stay observe; their violations remain recorded
    but do NOT fail the build.

    Phase 2.2+ widens `_ENFORCE_MODE_COLLECTIONS` and re-runs this
    test against the next migrated context. The list shrinks ZERO and
    grows monotonically as Phase 2 progresses.
    """
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    enforce = set(_ENFORCE_MODE_COLLECTIONS)
    bad = [
        v for v in data["violations"]
        if v["collection"] in enforce and v["kind"] != "non_literal"
    ]
    assert not bad, (
        f"tenancy ENFORCE-mode violations for collections "
        f"{sorted(enforce)}: {len(bad)} hits. "
        f"First 5: {bad[:5]!r}"
    )


def test_tenancy_observe_mode_records_other_collections() -> None:
    """Collections NOT in `_ENFORCE_MODE_COLLECTIONS` stay observe —
    their violations are reported but do NOT fail the build. This
    test documents the contract and verifies the report's metadata."""
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert data["enforce_mode_collections"] == sorted(_ENFORCE_MODE_COLLECTIONS)
    enforce = set(_ENFORCE_MODE_COLLECTIONS)
    other_definite = [
        v for v in data["violations"]
        if v["collection"] not in enforce and v["kind"] != "non_literal"
    ]
    # Just log; do not assert == 0.
    if other_definite:
        print(
            f"[tenancy observe mode] "
            f"{len(other_definite)} definite violations across "
            f"{len({v['collection'] for v in other_definite})} non-enforced "
            f"collections — violations recorded in {REPORT_PATH}"
        )
    assert True  # observe mode never fails


# ─── Scanner self-tests (Phase 0 strict-mode coverage) ───

def test_scanner_detects_synthetic_violation_in_filter_dict() -> None:
    """Synthetic offender → scanner must flag it."""
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
    assert found_call is not None
    has = _dict_has_any_recognised_key(
        found_call.args[0], _allowed_keys_for("chats"),
    )
    assert has is False, (
        f"scanner mis-classified synthetic offender as compliant: has={has!r}"
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
                has = _dict_has_any_recognised_key(
                    n.args[0], _allowed_keys_for("chats"),
                )
                assert has is True
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
            assert _line_is_escape_hatched(source_lines, n.lineno) is True
            return
    pytest.fail("scanner did not find the find() call")


# ─── Phase 2.1 Upgrade A — multi-line dict tracking ───

def test_upgrade_a_accepts_compliant_dict_assigned_then_passed() -> None:
    """A dict literal carrying account_id assigned to a variable
    THEN passed to the db call is compliant under Upgrade A."""
    source = (
        "async def ok(uid: str, acc: str):\n"
        "    q = {'id': uid, 'account_id': acc}\n"
        "    return await db.chats.find_one(q)\n"
    )
    tree = ast.parse(source)
    target_call: Optional[ast.Call] = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("chats", "find_one"):
            target_call = n
            break
    assert target_call is not None
    enc = _enclosing_function(tree, target_call)
    assert enc is not None
    _, keys = _resolve_name_to_dict_keys(enc, "q", target_call.lineno)
    assert "account_id" in keys, (
        f"Upgrade A failed to track account_id across assign-then-call: "
        f"keys={keys!r}"
    )


def test_upgrade_a_accepts_subscript_added_after_assign() -> None:
    """A dict assigned then mutated via `q['account_id'] = ...` is
    compliant under Upgrade A."""
    source = (
        "async def ok(uid: str, acc: str):\n"
        "    q = {'id': uid}\n"
        "    q['account_id'] = acc\n"
        "    return await db.chats.find_one(q)\n"
    )
    tree = ast.parse(source)
    target_call: Optional[ast.Call] = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("chats", "find_one"):
            target_call = n
            break
    assert target_call is not None
    enc = _enclosing_function(tree, target_call)
    assert enc is not None
    _, keys = _resolve_name_to_dict_keys(enc, "q", target_call.lineno)
    assert "account_id" in keys


def test_upgrade_a_flags_dict_without_account_id_even_with_subscript() -> None:
    """A dict assigned + subscript-added with an UNRELATED key is
    still a violation under Upgrade A."""
    source = (
        "async def offender(uid: str):\n"
        "    q = {'id': uid}\n"
        "    q['status'] = 'open'\n"
        "    return await db.chats.find_one(q)\n"
    )
    tree = ast.parse(source)
    target_call: Optional[ast.Call] = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("chats", "find_one"):
            target_call = n
            break
    assert target_call is not None
    enc = _enclosing_function(tree, target_call)
    assert enc is not None
    _, keys = _resolve_name_to_dict_keys(enc, "q", target_call.lineno)
    assert keys & _allowed_keys_for("chats") == set(), (
        f"Upgrade A leaked: keys={keys!r} should not intersect "
        f"{_allowed_keys_for('chats')!r}"
    )


# ─── Phase 2.1 Upgrade B — alternative tenancy keys ───

def test_upgrade_b_recognises_owner_account_id_on_contexts() -> None:
    """contexts.insert_one with owner_account_id is compliant via
    Upgrade B (the row IS the tenant; `owner_account_id` is canonical
    on contexts.insert)."""
    source = (
        "async def ok(acc: str):\n"
        "    return await db.contexts.insert_one("
        "{'id': 'x', 'name': 'y', 'owner_account_id': acc})\n"
    )
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("contexts", "insert_one"):
            has = _dict_has_any_recognised_key(
                n.args[0], _allowed_keys_for("contexts"),
            )
            assert has is True, (
                f"Upgrade B failed for contexts/owner_account_id: has={has!r}"
            )
            return
    pytest.fail("test setup failed")


def test_upgrade_b_recognises_context_id_on_cycles() -> None:
    """cycles.find with context_id is compliant via Upgrade B
    (context_id is membership-gated; route-level guard enforces scope)."""
    source = (
        "async def ok(ctx: str):\n"
        "    return await db.cycles.find({'context_id': ctx})\n"
    )
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("cycles", "find"):
            has = _dict_has_any_recognised_key(
                n.args[0], _allowed_keys_for("cycles"),
            )
            assert has is True


def test_upgrade_b_strict_default_for_unmapped_collection() -> None:
    """A collection NOT in ALT_TENANCY_KEYS defaults to strict
    `{account_id}` only — context_id alone is NOT enough."""
    # `chats` is in ALT_TENANCY_KEYS? No — chats is NOT mapped, so it
    # falls back to {"account_id"} only.
    assert _allowed_keys_for("chats") == frozenset({"account_id"})
    source = (
        "async def offender(uid: str):\n"
        "    return await db.chats.find_one({'id': uid, 'context_id': 'x'})\n"
    )
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("chats", "find_one"):
            has = _dict_has_any_recognised_key(
                n.args[0], _allowed_keys_for("chats"),
            )
            assert has is False, (
                f"Upgrade B over-widened: chats accepting context_id when "
                f"it shouldn't"
            )


# ─── Phase 2.1 Upgrade C — tenant_filter() / tenant_doc() recognition ───

def test_upgrade_c_recognises_tenant_filter_with_account_id_kwarg() -> None:
    """A db call wrapped in tenant_filter(extra, account_id=...) is
    compliant via Upgrade C."""
    source = (
        "from helpers.tenancy import tenant_filter\n"
        "async def ok(uid: str, acc: str):\n"
        "    return await db.chats.find_one("
        "tenant_filter({'id': uid}, account_id=acc))\n"
    )
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("chats", "find_one"):
            helper = _is_tenancy_helper_call(n.args[0])
            assert helper is not None, "Upgrade C did not detect tenant_filter()"
            assert _helper_call_supplies_account_id(helper) is True, (
                "Upgrade C missed the account_id kwarg"
            )
            return
    pytest.fail("test setup failed")


def test_upgrade_c_rejects_tenant_filter_without_account_id_kwarg() -> None:
    """tenant_filter(extra) WITHOUT the account_id kwarg is non-
    compliant (the helper's runtime ValueError catches it, but
    static-side we still flag it)."""
    source = (
        "from helpers.tenancy import tenant_filter\n"
        "async def offender(uid: str):\n"
        "    return await db.chats.find_one(tenant_filter({'id': uid}))\n"
    )
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _extract_db_call(n) == ("chats", "find_one"):
            helper = _is_tenancy_helper_call(n.args[0])
            assert helper is not None
            assert _helper_call_supplies_account_id(helper) is False
            return
    pytest.fail("test setup failed")



# ─── Phase 2.5a Upgrade — cross-tenant whitelist disjointness ─────────

def test_cross_tenant_whitelist_disjoint_from_scoped() -> None:
    """`_CROSS_TENANT_COLLECTIONS` MUST be disjoint from
    `TENANT_SCOPED_COLLECTIONS`. A collection cannot simultaneously be
    a tenant-scoped collection AND a legitimate cross-tenant
    collection. Build-breaking on overlap.

    Phase 2.5a creates this whitelist as a formal paper trail for
    collections legitimately out-of-scope for the scanner. The
    invariant prevents accidental contradictions during future
    growth.
    """
    overlap = _CROSS_TENANT_COLLECTIONS & TENANT_SCOPED_COLLECTIONS
    assert overlap == frozenset(), (
        f"Cross-tenant whitelist overlaps tenant-scoped allow-list: "
        f"{sorted(overlap)!r}. Either remove from "
        f"_CROSS_TENANT_COLLECTIONS or remove from "
        f"TENANT_SCOPED_COLLECTIONS — these are mutually exclusive."
    )
