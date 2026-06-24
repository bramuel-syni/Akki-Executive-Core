# Phase AUDIT_P2.1 — Tenancy Audit on `strategic_goal_evolution.py`

**Date:** 2026-06-24
**Status:** 🔴 **STOP GATE TRIPPED.** Audit found a real UNTENANTED handler. No product code touched per dispatch's strict no-silent-patch rule. Awaiting explicit user approval before patching.
**File audited:** `backend/routers/strategic_goal_evolution.py` (207 LOC, 1 endpoint, 4 DB read sites).
**Verdict:** **UNTENANTED** at the *handler* layer. Query filters DO carry `context_id` (collection-scoped), but the handler is missing the canonical `require_context_membership()` dep that validates the caller has an active membership in that `context_id`. As shipped, **any authenticated account can read any other tenant's strategic goal + linked documents + extractions log + audit log by passing the victim's `context_id`/`goal_id` in the URL.**

## Headline counts

| Class | Count | Rows |
|---|---|---|
| SAFE | 0 | — |
| SUSPECT | 0 | — |
| **UNTENANTED** | **4** | L89, L125, L151, L176 — all DB reads in the file |

## Endpoint inventory

Single endpoint:

```
GET /api/contexts/{context_id}/strategic-goals/{goal_id}/evolution
```

Signature (lines 82-86):

```python
@router.get("/{context_id}/strategic-goals/{goal_id}/evolution")
async def goal_evolution(
    context_id: str,
    goal_id: str,
    current: Dict[str, Any] = Depends(get_current_account),
) -> Dict[str, Any]:
```

The `current` payload from `get_current_account` is **never consulted** anywhere in the handler. It only authenticates the caller — it does not authorize them against `context_id`.

## Per-DB-call table

| # | Line | Op | Collection | Filter (verbatim) | tenant key in filter | handler-level membership gate | Risk |
|---|---|---|---|---|---|---|---|
| 1 | 89 | `find_one` | `strategic_goals` | `{"id": goal_id, "context_id": context_id}` | ✅ `context_id` | ❌ none | **UNTENANTED** |
| 2 | 125 | `find` (cursor) | `documents` | `{"context_id": context_id, "linked_objective_id": goal_id, "deleted_at": {"$exists": False}}` | ✅ `context_id` | ❌ none | **UNTENANTED** |
| 3 | 151 | `find` (cursor) | `extractions_log` | `{"document_id": {"$in": doc_ids}, "context_id": context_id}` | ✅ `context_id` | ❌ none | **UNTENANTED** |
| 4 | 176 | `find` (cursor) | `audit_log` | `{"context_id": context_id, "subject_type": "strategic_goal", "subject_id": goal_id, "action": {"$in": ["strategic_goal.updated", "strategic_goal.assessed"]}}` | ✅ `context_id` | ❌ none | **UNTENANTED** |

All 4 calls scope by the URL-supplied `context_id`. None of them verify the caller has access to that `context_id`. The `current` account identity is unused.

## Why "filter has context_id" is NOT sufficient (the gap)

`context_id` is a *resource identifier*, not a *tenant key*. Without a membership check at the handler boundary, a filter like `{"context_id": context_id}` will happily return rows for **any** `context_id` the caller passes — because the database has no way to know whether `current` is allowed to see that context.

The codebase's canonical tenancy model (per `core.py:249-269`):

```python
def require_context_membership(owner_only: bool = False):
    """Dependency: validates current account has active membership in context_id."""
    async def _dep(
        context_id: str,
        current: Dict[str, Any] = Depends(get_current_account),
    ) -> Dict[str, Any]:
        ctx = await db.contexts.find_one({"id": context_id}, {"_id": 0})
        if not ctx:
            raise HTTPException(status_code=404, detail="Context not found")
        membership = await db.memberships.find_one(
            {"context_id": context_id, "account_id": current["id"], "status": "active"},
            {"_id": 0},
        )
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this context")
        # ... owner_only check ...
        return {"account": current, "context": ctx, "membership": membership}
    return _dep
```

This dep is the canonical "context-scoped" tenant boundary. Every sibling router on the same URL family uses it.

## Side-by-side: sibling `strategic_goals.py` vs. audited `strategic_goal_evolution.py`

Both files own routes under `/api/contexts/{context_id}/strategic-goals/...`. They MUST share a tenant boundary by construction.

### Sibling (`backend/routers/strategic_goals.py`) — TENANT-GATED

```python
# L135-148
@router.get("/contexts/{context_id}/strategic-goals")
async def list_goals(
    context_id: str,
    department: Optional[str] = None,
    ctx: Dict[str, Any] = Depends(require_context_membership()),   # ✅ MEMBERSHIP-GATED
):
    q: Dict[str, Any] = {"context_id": context_id}
    if department:
        q["department"] = department
    goals = await db.strategic_goals.find(q, {"_id": 0}).to_list(200)
    ...

# L184-188
@router.patch("/contexts/{context_id}/strategic-goals/{goal_id}")
async def update_goal(
    context_id: str, goal_id: str, body: GoalPatch,
    ctx: Dict[str, Any] = Depends(require_context_membership()),   # ✅ MEMBERSHIP-GATED
):
    ...

# L226-230 — delete_goal: also membership-gated. Same pattern.
# L241-245 — extract_from_document: also membership-gated. Same pattern.
```

All 5 endpoints in the sibling router go through `Depends(require_context_membership())`. Every DB call below them inherits a verified `account_id ↔ context_id` membership tie.

### Audited file (`backend/routers/strategic_goal_evolution.py`) — **NOT** TENANT-GATED

```python
# L81-86
@router.get("/{context_id}/strategic-goals/{goal_id}/evolution")
async def goal_evolution(
    context_id: str,
    goal_id: str,
    current: Dict[str, Any] = Depends(get_current_account),   # ❌ AUTHN-ONLY, no membership check
) -> Dict[str, Any]:
    ...
```

The single endpoint uses `get_current_account` only. No `require_context_membership`. The 4 downstream DB reads inherit no membership tie — they're filter-scoped by a URL parameter the caller controls.

## Threat model + reproduction

**Step 1.** Tenant A creates a strategic goal in their context `ctx_A`. Goal id `g_secret`. Context owner uploads sensitive board document `d_priv` linked to the goal. AKKI runs LLM extractions and writes audit-log rows.

**Step 2.** Attacker authenticates as a Tenant B account (e.g. trial account). Attacker has a valid JWT, but **no membership** in `ctx_A`.

**Step 3.** Attacker calls:
```
GET /api/contexts/ctx_A/strategic-goals/g_secret/evolution
Authorization: Bearer <attacker's own JWT>
```

**Step 4.** The handler:
- `Depends(get_current_account)` → succeeds (attacker has a valid JWT, returns the attacker's own `current`).
- L89 `db.strategic_goals.find_one({"id": "g_secret", "context_id": "ctx_A"})` → returns Tenant A's goal.
- L125 `db.documents.find({"context_id": "ctx_A", "linked_objective_id": "g_secret", ...})` → returns Tenant A's `d_priv` with title.
- L151 `db.extractions_log.find({"document_id": {"$in": [d_priv]}, "context_id": "ctx_A"})` → returns Tenant A's LLM extraction history.
- L176 `db.audit_log.find({"context_id": "ctx_A", "subject_type": "strategic_goal", "subject_id": "g_secret", ...})` → returns Tenant A's goal-status mutation history.

**Step 5.** Response shape (verbatim from L202-206):
```json
{
  "goal_id": "g_secret",
  "context_id": "ctx_A",
  "events": [
    {"kind": "doc_upload",        "trigger": "New strategy uploaded: <Tenant A board pack title>", "doc_id": "d_priv", "doc_title": "<sensitive title>"},
    {"kind": "score_delta",       "trigger": "Performance moved 45% → 72%", ...},
    {"kind": "ai_reassessment",   "trigger": "AKKI re-evaluated this goal (12 signals, 1 failed)", ...},
    {"kind": "status_change",     "trigger": "Status changed to at_risk", ...}
  ]
}
```

**Information disclosed cross-tenant:**
- Goal id existence + title (echoed via `goal_id` field, plus trigger lines reference goal events).
- Linked document titles (cross-tenant doc title leak).
- LLM extraction run cadence + failure counts (operational telemetry leak).
- Goal status mutation history with timestamps.

**Severity:** HIGH (IDOR/BOLA — Broken Object-Level Authorization, OWASP API1:2023). Cross-tenant data exfiltration via a single authenticated GET, no special privilege needed.

**Mitigating factors:**
- Attacker needs valid `context_id` AND `goal_id` to enumerate, but `context_id` is a UUID (low brute-force surface) — however, `context_id` leaks via several other endpoints (e.g., any shared link, any `X-Active-Context` log line, any error reflected back, any analytics).
- Modifications/writes are not possible via this endpoint (read-only). The companion sibling router has writes; those ARE membership-gated.

## Why the existing `test_invariant_tenancy.py` doesn't catch this

The existing invariant scanner at `backend/tests/invariants/test_invariant_tenancy.py` (~63KB) operates in two passes:

1. **Filter-pass:** AST-scans every `db.<col>.find/find_one/update/...` call and asserts the *filter dict* contains a recognized tenant key. For `strategic_goals`, both `account_id` AND `context_id` are recognized (L181: `frozenset({"account_id", "context_id"})`). All 4 calls in the audited file PASS this pass — they all carry `context_id`.

2. **Helper-fusion pass:** Recognizes `Depends(require_context_membership())` (L281-286, L812-813) as fulfilling the tenancy contract for handlers that don't carry `account_id` in their queries. The scanner extends scope so a `context_id`-only filter is acceptable IF the handler has the membership dep.

The audited file:
- ✅ Passes filter-pass (all queries have `context_id`).
- ❌ Fails the *intent* of helper-fusion (handler has no membership dep) — **but the scanner doesn't REQUIRE the dep when `context_id` alone is in the recognized-keys set for the collection**. The dep is rewarded if present, not required when absent.

This is the exact gap P2 was designed to close. The scanner correctly enforces the data-layer contract (filter has tenant key); it does NOT enforce the auth-layer contract (handler has membership gate when filter is `context_id`-only).

## Recommended fix (NOT APPLIED — awaiting user approval)

Single-line change:

```diff
- from core import db, get_current_account
+ from core import db, require_context_membership

  @router.get("/{context_id}/strategic-goals/{goal_id}/evolution")
  async def goal_evolution(
      context_id: str,
      goal_id: str,
-     current: Dict[str, Any] = Depends(get_current_account),
+     ctx: Dict[str, Any] = Depends(require_context_membership()),
  ) -> Dict[str, Any]:
```

The 4 DB-call filters are correct as-is — they already carry `context_id`, which is the standard scope on this URL family (matches the sibling router's `list_goals`/`update_goal`/`delete_goal`/etc.). No filter changes needed.

**Behaviour-change risk: LOW.**
- Before: any authenticated caller passing valid `context_id`/`goal_id` gets the events feed.
- After: same caller, but only if they have an active membership in `context_id`. Non-member callers (today: 200 OK with cross-tenant data) become 403 Forbidden (correct — they shouldn't have seen the data).
- 404 path (line 92-93: goal-not-found) still works; the dep returns 404 *before* reaching the goal-existence check now, which is arguably more correct (avoid existence-leak for unknown contexts).

**Regression surface:**
- Any frontend code that calls this endpoint without an active context. The endpoint is called by `Day16Banner.jsx` and `GoalDrawer.tsx` per a brief frontend search (will confirm if user authorizes). Both should already operate under an active context (otherwise the surrounding UI would not have surfaced this drawer).

## Escape-hatch inventory (for P2.2 — pending P2.1 unblock)

For completeness, the codebase already uses two escape-hatch mechanisms. Enumerated here so P2.2's invariant can derive its allowlist from real callsites, not from guesses:

### Mechanism 1: `untenanted=True` kwarg on contract-adapter calls (16 callsites)

```
backend/routers/solva_v2.py:258            untenanted=True,
backend/routers/solva_v2.py:2017           untenanted=True,
backend/routers/solva_v2.py:2037           untenanted=True,
backend/routers/comments.py:82             untenanted=True,
backend/routers/cycle.py:1743              untenanted=True,
backend/routers/lens.py:94                 untenanted=True,
backend/routers/synisense_metrics.py:213   untenanted=True,
backend/routers/trust_center.py:84         untenanted=True,
backend/routers/trust_center.py:740        untenanted=True,
backend/routers/shares.py:63               untenanted=True,
backend/routers/studio_blocks.py:477       untenanted=True,
backend/routers/pulse.py:554               untenanted=True,  # has inline justification
backend/tests/test_phase4_2_http_transport_smoke.py:227   untenanted=True,  # test file, expected
```

Defining contract definitions (the adapter signatures that ACCEPT this kwarg):
```
backend/contracts/_adapters/akki.py:580         (db.chats.find_one  pass-through)
backend/contracts/_adapters/synisense.py:180    (db.signals  pass-through)
backend/contracts/akki.py:259                   (documents.find_one)
backend/contracts/akki.py:287                   (chats.find_one)
backend/contracts/akki.py:342                   (chats.find versatile)
backend/contracts/synisense.py:89               (signals.find_one)
```

Each contract docstring carries an inline justification ("Trust Center / synisense_metrics public mirror", "Solva v2 evidence-card resolver fetches by document id alone, then verifies via membership downstream", etc.). P2.2 allowlist must include all 13 product-code callsites with these justifications.

### Mechanism 2: `# tenancy:allow-no-account-id` line-comment marker (≥24 callsites)

Used at the call-site of a `db.<col>.find/update/...` to mark "this query is intentionally not tenant-keyed because the prior line-level evidence establishes the tenancy guarantee." Verbatim ESCAPE_HATCH_MARKER per the tenancy invariant scanner (L456).

Sample callsites with their inline justifications (representative subset):
- `routers/chat.py:1434` — "retention sweep is a cross-tenant operational task (cron); each row is then processed under its own account_id"
- `routers/chat.py:1550` — "`d` was loaded from this chat's grounding doc set via context_id-gated path; update is a write-back of paragraphs cache"
- `routers/sandbox.py:281` — "`seeds["documents"]` built by build_seed_payload(owner_account_id=...) which stamps account_id on every row; scanner can't trace into the builder"
- `routers/strategic_goals.py:222` — "row-id-targeted readback after L218-219 validated write with context_id"
- `routers/solva_v2.py:219` — "seed resolver: question fetched by id THEN explicit context_id cross-check at L223"
- (See `grep -rn 'tenancy:allow-no-account-id' backend/` for the full set — at least 24 callsites enumerated in P2.1 evidence gathering.)

This marker is already enforced/recognized by `test_invariant_tenancy.py::ESCAPE_HATCH_MARKER` (L456). P2.2's new invariant should NOT re-enforce this — it should focus on the `untenanted=True` kwarg lane plus any *additional* escape patterns derived from the audit.

### Missing escape mechanism: handler-level "no membership gate" (the AUDIT_P2.1 finding class)

Currently undetected. There's no allowlist convention for "handler intentionally uses `get_current_account` without `require_context_membership` even though the URL path includes `{context_id}`". The audited file is in this class.

Recommended P2.2 follow-up:
- Add a third escape mechanism: a function-level comment marker like `# tenancy:allow-no-membership-gate — <justification>` for genuine cases (e.g., public read endpoints), OR
- Mandate that all routes with `{context_id}` in the path MUST use `require_context_membership()` (no allowlist, strict ratchet), with the audited file being the first repair.

The user should choose between these two postures before P2.2 ships.

## What the user MUST decide before P2 unblocks

1. **Repair?** Apply the one-import + one-line dep swap on `strategic_goal_evolution.py` (recommended). The change is mechanical and matches sibling-router conventions verbatim. Diff ≤ 5 lines.
2. **OR Whitelist?** Document the file as "intentional public/relaxed access". This would require a NEW escape-hatch marker (no current convention covers this), and the threat model section above suggests it would be the wrong call (sensitive cross-tenant data leak).
3. **OR Other?** Some alternative gating (e.g., a custom dep for read-only-from-membership-or-public-share) — needs design.

Repair (option 1) is recommended. Awaiting explicit "OK to patch" from user before touching product code.

## Files touched in this audit pass

- Created: `memory/audit/P2_sge_tenancy_audit.md` (this file).
- **NO** product code changes.
- **NO** test code changes.

## Stop-and-report

🔴 **STOP GATE TRIPPED** per dispatch's strict no-silent-patch rule.

> *"if any UNTENANTED row is found, STOP P2.1, surface the audit table, and wait for explicit user approval before patching. No silent edits to product code."*

P2.2/P2.3/P2.4 are blocked behind this decision since they depend on resolving the canonical-pattern question (whether `require_context_membership` is the canonical gate, or whether a new escape-hatch marker for "no-membership-gate" is being introduced).

Awaiting user direction.
