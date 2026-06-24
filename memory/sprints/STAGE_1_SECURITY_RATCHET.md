# Stage 1 — Security Ratchet (P2.1 + P2.2 + P2.4)

**Date:** 2026-06-24
**Dispatch:** AKKI Full Runway, Stage 1 — "Close security (IDOR + ratchet)".
**Status:** CLOSED. Three commits land locally; all 9 new invariant tests GREEN; FE caller analysis SHOWN; security claim SHOWN.
**Type:** One IDOR/BOLA fix + three build-breaking invariants. Product-code change limited to a 2-token edit (`Depends` swap + import swap) on the audited file. Zero changes to product behaviour for legitimate callers.

## Headline result

| Item | Commit | Result |
|---|---|---|
| **P2.1** Tenancy patch on `strategic_goal_evolution.py` | `adbecd3f` | IDOR closed; non-member call → 403; victim title NOT in response body |
| **P2.2-A** Hard ratchet on `{context_id}` route membership gate | `5cbd948f` | 21 audit-derived exceptions allowlisted; build fails on the silent-omission class |
| **P2.2-B** Audited allowlist for tenancy escape hatches | `5cbd948f` (same) | 12 `untenanted=True` callsites + 179 `# tenancy:allow-no-account-id` markers enumerated with justifications |
| **P2.4** `thinklab` engine/surface name guard | `280b4549` | backend at 0 hits; hard ratchet, no allowlist |

**Verification (collected output):**
```
$ pytest backend/tests/test_monitor_drawer_progress_timeline.py -v
8 passed, 1 failed (the 1 is pre-existing server.py source-text drift,
                    unrelated to P2.1 — proven by stash + re-run).

$ pytest backend/tests/invariants/test_context_route_membership_gate.py \
         backend/tests/invariants/test_tenancy_escape_hatch_allowlist.py \
         backend/tests/invariants/test_thinklab_uilabel_only.py -v
9 passed, 21 warnings in 9.59s
```

## P2.1 — IDOR patch (full evidence)

### FE Caller Analysis (precondition, SHOWN not asserted)

The dispatch required: *"the behaviour-change claim — 'frontend already operates under an active context, no UI regression' — must be SHOWN, not asserted."*

Trace per `memory/audit/P2_sge_tenancy_audit.md` (full memo). Headline:

**Endpoint inventory:** single endpoint `GET /api/contexts/{context_id}/strategic-goals/{goal_id}/evolution`.

**Runtime FE caller:** `StrategicGoalsPanel.jsx:554` (the only one — `schemas.gen.ts:13504` is auto-generated type, not a caller).

**`contextId` provenance:**
- `Monitor.jsx:73` → `const cid = activeContext?.id;` from `useAuth()`
- `AuthContext.jsx:61-85::fetchAuthoritativeContexts` fetches from `/api/me/contexts`
- `backend/routers/active_context.py::list_my_contexts` filters by `db.memberships.find({"account_id": current["id"], "status": "active"})`
- This is **the same query** the new `require_context_membership` dep runs.
- Boot guard at `AuthContext.jsx:109-122` clears stale `activeContextId` not in the membership list

**Verdict:** legitimate FE callers see no change (200 OK → 200 OK). Only attackers see a change (200 OK → 403).

### Patch

```diff
diff --git a/backend/routers/strategic_goal_evolution.py
@@ -51,7 +51,7 @@
-from core import db, get_current_account
+from core import db, require_context_membership
@@ -82,7 +82,7 @@ async def goal_evolution(
     context_id: str,
     goal_id: str,
-    current: Dict[str, Any] = Depends(get_current_account),
+    ctx: Dict[str, Any] = Depends(require_context_membership()),
 ) -> Dict[str, Any]:
```

2 single-token edits. No filter changes (all 4 DB-call filters were already `context_id`-scoped, matching sibling-router convention).

### Security claim verified

`test_evolution_endpoint_blocks_cross_tenant_access` (new) authenticates as an attacker account with no membership in victim's context, calls the endpoint, asserts:
- Response status `== 403` (was 200 pre-patch).
- Victim's goal title `"CONFIDENTIAL board KPI"` NOT in response body.
- Victim's document title `"Secret board capital plan Q3"` NOT in response body.

Test passes. The CVE-class IDOR/BOLA is closed.

### Tests

Existing tests updated to seed `db.contexts` + `db.memberships` for the fake account (needed because the new dep does its own DB lookups). Two positive tests + one new security test = 3 P2.1-related tests. All pass.

### Disclosed pre-existing failure

`test_evolution_router_registered_in_server` fails pre- and post-patch identically (verified via `git stash`). The test asserts `"app.include_router(strategic_goal_evolution_router.router)" in server.py`, but a prior refactor moved router-mounting to `akki_app.py:187`. Out of P2.1 scope; logged under §9 as a follow-up.

## P2.2 — Hard ratchet on `{context_id}` membership + audited tenancy escapes

### Invariant A: `test_context_route_membership_gate.py` (HARD RATCHET)

Scans `backend/` for every FastAPI route whose URL path contains `{context_id}`. Each MUST have either:
- `Depends(require_context_membership(...))` from `core.py:249`, OR
- `Depends(require_role(...))` from `services/rbac.py:127`, OR
- An audit-reviewed entry in `context_route_membership_allowlist.yml` with both `gate_mechanism` and `justification` fields.

**Initial population**: 270 `{context_id}` routes total; 249 use a canonical factory dep; 21 use audited inline gates (the allowlist YAML). Categories:

| Category | Count | Mechanism | Files |
|---|---|---|---|
| Superadmin bypass | 2 | `Depends(_require_superadmin)` | `admin_tenants.py` |
| Tiered report access | 7 | `_resolve_report_access(...)` inline | `cycle.py` |
| Worker-stamp pattern ⚠ | 4 | `job_queue` stamps `account_id` | `documents_async_mirror.py` |
| NED inline check | 1 | `_verify_ned_context(...)` | `ned_cycle.py` |
| Sandbox owner-only | 7 | `{owner_account_id: current.id, type: sandbox}` filter | `sandbox.py` |
| **Total** | **21** | | |

⚠ The 4 `documents_async_mirror.py` entries carry a `Subtle:` note in their justifications — the input route doesn't pre-gate before queueing. Logged for §9 follow-up.

### Invariant B: `test_tenancy_escape_hatch_allowlist.py` (AUDITED ALLOWLIST)

Two scanners on product code (excludes `tests/` and `contracts/`):
- **AST**: every callsite passing `untenanted=True` kwarg — 12 callsites.
- **Regex**: every line matching `# tenancy:allow-no-account-id` — 179 markers.

Both populations mechanically derived in `tenancy_escape_allowlist.yml`. Each entry has `file`, `line`, and `justification`. Stale entries (no matching callsite) fail the build. New callsites without an entry fail the build.

Per the user's framing: *"the 16 `untenanted=True` callsites and 24+ markers get their own explicit, audit-derived allowlists — documented, reasoned exceptions, the opposite of the silent omission you caught."*

### Tests output

```
$ pytest backend/tests/invariants/test_context_route_membership_gate.py \
         backend/tests/invariants/test_tenancy_escape_hatch_allowlist.py -v

test_context_route_membership_gate.py::test_allowlist_is_well_formed         PASSED
test_context_route_membership_gate.py::test_no_allowlist_entry_is_orphaned   PASSED
test_context_route_membership_gate.py::test_every_context_id_route_is_gated_or_allowlisted PASSED
test_tenancy_escape_hatch_allowlist.py::test_allowlist_yaml_is_well_formed   PASSED
test_tenancy_escape_hatch_allowlist.py::test_every_untenanted_kwarg_callsite_is_allowlisted PASSED
test_tenancy_escape_hatch_allowlist.py::test_no_orphaned_untenanted_entries  PASSED
test_tenancy_escape_hatch_allowlist.py::test_every_tenancy_allow_marker_is_allowlisted PASSED
test_tenancy_escape_hatch_allowlist.py::test_no_orphaned_tenancy_allow_marker_entries PASSED

8 passed in 9.80s
```

## P2.4 — `thinklab` UI-label-only invariant

The architectural lock per `SPRINT_PLAN.md:99`: *"ThinkLab is UI label only; internal names stay solva (build-breaking invariant)."*

`test_thinklab_uilabel_only.py` case-insensitively scans `backend/*.py` for `thinklab`. Today: 0 hits. The invariant locks this state in. The first `thinklab` symbol that lands in backend code (a route name, a class, a collection, a logger channel, etc.) fails the build, forcing rename to `solva` or a domain-appropriate term.

Frontend deliberately NOT scanned — the surface IS called ThinkLab, FE labels are expected.

```
$ pytest backend/tests/invariants/test_thinklab_uilabel_only.py -v
test_thinklab_uilabel_only.py::test_backend_has_zero_thinklab_references     PASSED
1 passed
```

## Files touched in Stage 1

### Product code (only allowed edit: P2.1's 2-token patch)
- `backend/routers/strategic_goal_evolution.py` (4-line diff: 1 import edit, 1 dep edit)

### Test code (security-claim verification)
- `backend/tests/test_monitor_drawer_progress_timeline.py` (added membership seeds + new cross-tenant 403 test)

### Invariants (new) — `backend/tests/invariants/`
- `test_context_route_membership_gate.py`
- `test_tenancy_escape_hatch_allowlist.py`
- `test_thinklab_uilabel_only.py`
- `context_route_membership_allowlist.yml` (21 entries)
- `tenancy_escape_allowlist.yml` (191 entries)

### Maintenance (this memo + DEV_PIPELINE.md)
- `memory/DEV_PIPELINE.md` (§1 + §2 + §4 + §9 updates)
- `memory/audit/P2_sge_tenancy_audit.md` (FE analysis + post-patch verification appended)
- `memory/sprints/STAGE_1_SECURITY_RATCHET.md` (this file)
- `.github/workflows/pipeline-log-sync.yml` (KNOWN_MAPPINGS extended with `STAGE_1/2/3/4/5`)

## Commit ledger (local-only; user push)

```
$ git log --oneline origin/main..HEAD
280b4549 ci(P2.4): backend-zero thinklab invariant (UI-label-only on FE)
5cbd948f ci(P2.2): hard ratchet on {context_id} membership + audit-derived allowlist for tenancy escapes
adbecd3f fix(P2.1): require_context_membership on strategic_goal_evolution routes (CVE-class IDOR fix)
50e41ab2 auto-commit for 24648c76-829e-4303-ba1a-f6f57669a0ec (unrelated, prior)
9b8dbc7a ci(P1): close-out memo + DEV_PIPELINE §1/§2/§4/§9 updates
f944f365 ci(P1.5): extend gitleaks allowlist for sprint/audit memos and product review
9a3c6c97 ci(P1.3): annotate spaCy github-release lines for requirements-guard
8b6b7fc7 ci(P1.1): commit yarn.lock for deterministic installs
```

The Stage 1 close-out (memo + DEV_PIPELINE + KNOWN_MAPPINGS) lands as a **4th commit** on top of these.

## §9 follow-up flags (logged but not actioned in this stage)

1. **`documents_async_mirror.py` worker-stamp pattern (4 routes)** — input routes don't pre-gate membership before queueing. Worker re-validates, but a non-member could still trigger LLM compute. Operational-DoS risk only (no data leak). Audit-follow-up.
2. **`test_evolution_router_registered_in_server` pre-existing failure** — asserts router-mount in `server.py` but the mount moved to `akki_app.py:187` in a prior refactor. Source-text drift, not behaviour.

## Stop-and-report

✅ **No STOP conditions tripped.** All four Stage 1 items GREEN. Immediately rolling into Stage 2 (Clean history + green board) per dispatch.
