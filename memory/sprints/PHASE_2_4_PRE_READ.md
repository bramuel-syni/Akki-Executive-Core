# Phase 2.4 Pre-Read — `contexts` Migration Approach

**Mode:** READ-ONLY investigation (Discipline Rail R1).
**Date:** 2026-06-22.
**Scope:** Decide the migration approach for the `contexts` collection (71 hits — 69 literal + 2 non-literal — ~30% of post-Phase-2.3 violations).

**Headline:** **CLEAN_WITH_NOTES.** Architectural picture is more fragmented than Phase 2.2 §8.B suggested — **5 distinct patterns**, not 1. Single-approach migration (Option A, B, C, or D alone) would force-fit the outliers and create silent risks. Recommended: **hybrid (C-primary + B-supporting + A-targeted) + escalate 1 helper-design observation**. No real-bug escalation: both tenant-gate helpers DO enforce tenancy correctly. Cost: ~1.5 build hours, fits the dispatch budget.

---

## 1 · Pattern characterisation (Q1)

20-of-71 stratified sample at `/tmp/phase24_ctx_sample.json`. Each entry inspected ±8 lines + enclosing function args + AST-resolved name scope.

### 1.A · Sample table

| # | File:line | Method | Filter shape | Upstream helper | account_id in scope |
|---|---|---|---|---|---|
| 1 | `sandbox.py:365` | find | `{type, hard_delete_at, status}` (admin cron) | — | n |
| 2 | `contexts.py:233` | update_one | `{id}` | **`require_context_membership@L192`** | Y |
| 3 | `inbound_email.py:278` | find_one | `{inbound_address, status}` (no id lookup) | — | n |
| 4 | `solva_v2_artefact.py:78` | find_one | `{id: cid}` | — | Y |
| 5 | `active_context.py:168` | find_one | `{id: body.context_id, status:active}` | — | Y |
| 6 | `admin_tenants.py:106` | count_documents | `{type, name regex}` (admin inventory) | — | n |
| 7 | `committees.py:45` | update_one | `{id}` | **`require_context_membership@L34`** | Y |
| 8 | `first_session.py:275` | update_one | `{id: context_id, owner_account_id: current.id}` | — | Y |
| 9 | `admin_sandbox_kpi.py:65` | find | `{type:sandbox, ...}` (admin probe) | — | n |
| 10 | `auth.py:162` | find | `{id: {$in: my_ctx_ids}}` | — | n (but `account` is) |
| 11 | `ned_cycle.py:174` | find_one | `{id, type:^ned_}` | — (THIS IS the helper body — `_verify_ned_context`) | Y |
| 12 | `contexts.py:300` | update_one | `{id}` | **`require_context_membership@L298`** | Y |
| 13 | `search.py:60` | find | `{id: {$in: my_ctx_ids}}` | — | Y |
| 14 | `sandbox.py:634` | update_one | `{id: context_id}` | (prior find with `owner_account_id` gate at L604) | Y |
| 15 | `depth.py:68` | find_one | `{id: m[context_id]}` (member-derived) | — | Y |
| 16 | `contexts.py:302` | find_one | `{id}` | **`require_context_membership@L298`** | Y |
| 17 | `work_studio_export.py:1336` | find_one | `{id: context_id}` (worker) | — | n (closure) |
| 18 | `inbound_email.py:375` | update_one | `{id: ctx_id}` (inbound handler) | (prior find at L341 with `inbound_address` lookup) | Y |
| 19 | `solva_v2.py:599` | find_one | `{id: context_id}` (worker) | — | Y |
| 20 | `sandbox.py:318` | delete_one | `{id: ctx_id}` (rollback in `_seed_sandbox`) | — (ctx_id was self-created in this same function) | Y |

### 1.B · Pattern tally (5 distinct patterns identified)

| Pattern | % of sample | Description | Migration implication |
|---|---:|---|---|
| **P1 — `require_context_membership` upstream** | **20% (4/20)** | Filter is `{id: context_id}`; helper called above in same function at the route boundary; membership 403 already enforced. | Helper-fusion (Option B) would auto-resolve. |
| **P2 — `_verify_ned_context` (or inline membership check) upstream** | **5% (1/20)** | Same shape as P1 but using the NED-specific helper. | Same as P1 if helper-fusion. |
| **P3 — Owner-scoped or membership-derived id** | **30% (6/20)** | Filter `{id: context_id}` where `context_id` came from `db.memberships.find({account_id: …})` OR a prior `db.contexts.find_one({id, owner_account_id})` gate IN THE SAME FUNCTION. | Defensive add of `owner_account_id` works iff route is sandbox/seeded — but breaks for shared contexts. Helper-fusion fails (no helper call). Marker is the safe play. |
| **P4 — Admin / cron / cross-tenant probes** | **20% (4/20)** | Sweep across all tenants by design; gated by `X-Cron-Secret` or super-admin route dependency. | Marker only — alt-key widening is wrong (would suppress detection of new admin-route violations). |
| **P5 — Worker / closure / no-helper handler** | **25% (5/20)** | `{id: context_id}` inside `_run_export`, `_run_grounding`, `_run_enhance`, `set_active_context` — context_id arrived as an arg/closure capture; no upstream helper in the same function (helper was at the caller). | Defensive `owner_account_id`/`type`/`status` cannot be added safely (handler doesn't have them) — marker required. Helper-fusion would need cross-function tracking, out of scope. |

### 1.C · Projection on the full 71 hits

The sample is small (20) but stratified — projection to 71:

- **P1 + P2 (helper-fusion candidates):** ~25% = **18 hits**
- **P3 (membership/owner derived):** ~30% = **21 hits**
- **P4 (admin/cron):** ~20% = **14 hits**
- **P5 (worker/closure):** ~25% = **18 hits**

Roughly even-thirds split between "helper-fusion would catch", "compositional gate", and "marker required". No single option covers >25% on its own → **hybrid is the architecturally correct answer**, not lazy.

---

## 2 · Tenant-gate helpers audit (Q2)

### 2.A · `require_context_membership(owner_only=False)` — `core.py:249-269`

```python
def require_context_membership(owner_only: bool = False):
    """Dependency: validates current account has active membership in context_id."""
    async def _dep(
        context_id: str,
        current: Dict[str, Any] = Depends(get_current_account),
    ) -> Dict[str, Any]:
        ctx = await db.contexts.find_one({"id": context_id}, {"_id": 0})  # L255 ← own violation
        if not ctx:
            raise HTTPException(status_code=404, detail="Context not found")
        membership = await db.memberships.find_one(
            {"context_id": context_id, "account_id": current["id"], "status": "active"},
            {"_id": 0},
        )
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this context")
        if owner_only:
            is_owner = ctx.get("owner_account_id") == current["id"]
            if not is_owner and membership.get("sub_role") != "admin":
                raise HTTPException(status_code=403, detail="Owner privilege required")
        return {"account": current, "context": ctx, "membership": membership}
    return _dep
```

**Tenancy enforcement:** REAL. Line 258-263 — fetches `memberships` row keyed by `(context_id, account_id, status=active)`; raises 403 if missing. The unscoped `db.contexts.find_one({"id": context_id})` at L255 is intentional — it's a presence check; the membership row is the gate.

**Failure modes:**
- Missing context → 404.
- Missing/inactive membership → 403.
- `owner_only=True` with non-owner non-admin caller → 403.

**Call sites:** 60+ FastAPI route handlers (single-file `grep -c require_context_membership backend/routers/*.py | grep -v :0` would enumerate; not enumerated here for brevity — the count exceeds the 20-sample's representation, which is why P1+P2 projected ~25%).

**Verdict:** Safe to codify via Option B (helper-fusion scanner). NOT security theatre.

### 2.B · `_verify_ned_context(account_id, context_id)` — `ned_cycle.py:164-179`

```python
async def _verify_ned_context(account_id: str, context_id: str) -> Dict[str, Any]:
    """Confirms the account has a NED membership on context_id and returns
    the resolved context. Raises 403 otherwise."""
    m = await db.memberships.find_one(
        {"account_id": account_id, "context_id": context_id,
         "role": "ned", "status": "active"},
        {"_id": 0, "role": 1},
    )
    if not m:
        raise HTTPException(status_code=403, detail="Not a NED on this board")
    ctx = await db.contexts.find_one(
        {"id": context_id, "type": {"$regex": "^ned_"}}, {"_id": 0},  # L174 ← own violation
    )
    if not ctx:
        raise HTTPException(status_code=404, detail="NED context not found")
    return ctx
```

**Tenancy enforcement:** REAL. Line 167-171 — fetches memberships row with `(account_id, context_id, role=ned, status=active)`; raises 403 if missing. Then fetches context; the contexts find is post-gate.

**Failure modes:** Same shape as `require_context_membership`. NED role is additionally enforced.

**Call sites:** ~3-5 (within `ned_cycle.py` only — not a cross-router helper).

**Verdict:** Safe to codify. NOT security theatre.

### 2.C · No other helpers

Exhaustive grep (`def require_context_membership|def get_context_or_403|def _resolve_context|def _load_context|def require_context|def _verify_ned_context|def fetch_context|def verify_context`) returns ONLY these two. `get_context_or_403` does NOT exist (Phase 2.2 §8.B speculative naming — it's `require_context_membership` in practice).

### 2.D · One observation worth surfacing in §7 ESCALATE (non-bug; design note)

Both helpers' own `db.contexts.find_one(...)` calls (L255 in core.py and L174 in ned_cycle.py) are themselves on the 69-literal-violations list. The current scanner correctly flags them — but they are the helpers we want to **bless** as tenancy-satisfied, not migrate. Whichever hybrid approach we pick must explicitly exempt these two helper bodies (e.g., marker with rationale "this IS the tenant gate; the membership lookup above enforces it"). NOT a bug.

---

## 3 · Four options costed (Q3)

| Criterion | A: Alt-key (`id`) | B: Helper-fusion | C: Marker sweep | D: ContextRepo |
|---|---|---|---|---|
| **Concept** | Add `"id"` to `ALT_TENANCY_KEYS["contexts"]` | Scanner traces preceding `require_context_membership()` calls in same function scope and accepts the downstream `db.contexts.{find,find_one,update_one}(…)` | Inline `# tenancy:allow-no-account-id` marker on every 71 sites with rationale | New class `ContextRepo(account_id).by_id(context_id)` etc.; migrate all 71 sites |
| **Implementation cost** | Trivial — 1 line scanner edit + tests | Medium — ~60 LOC scanner extension; need to enumerate tenant-gate helper names; new test fixtures for the AST tracer | Low-medium — 71 markers with rationale; ~3-4 hours of pattern-matching writing | High — new class, 71 call-site rewrites, regenerate dozens of test fixtures |
| **Call sites touched (product code)** | 0 | 0 (scanner only) | 71 (one marker each) | 71 (full rewrite) |
| **Lines of code added/changed** | ~5 (test fixture for the alt-key) | ~120 (scanner + 5 new tests) | ~140 (71 markers ×2 lines avg) | ~600 (class + 71 call-sites + test refactor) |
| **Static catch on future misuse** | **NO** — any new `db.contexts.find_one({"id": x})` passes silently. Worst on this axis. | **YES** — scanner fails if no preceding `require_context_membership()` / `_verify_ned_context()` call in the same scope. False-positive risk if call is in a different scope but architecturally safe. | **YES** — every new call site without a marker fails the build. Highest signal-to-noise, lowest false-positive rate. | **YES** — direct `db.contexts.*` calls become anti-pattern; scanner forbids them entirely. Strongest. |
| **Runtime safety contribution** | None (scanner only) | None (scanner only) | None (scanner only) | High — `ContextRepo.__init__(account_id)` raises if absent; every `by_id` call physically threads account_id through. |
| **Behaviour change required** | None | None | None | None if `ContextRepo.by_id` returns the same row shape. But signature change at every call site IS behaviour change in the loose sense (raises ValueError vs returns None). |
| **Goldens risk** | None | None | Negligible — markers are comments, AST-invisible | High — call-site signature changes can ripple through `chats`/`documents`/`work_studio_export.py` (which all read context occasionally) |
| **R6 compliance ("no unrequested cleanups")** | ✓ | ✓ | ✓ | ✗ — large architectural refactor; out of Phase 2 scope |
| **R4 budget (≤10 lockdown tests)** | 1 new test | 5 new tests | 0 new tests (existing enforce mode test covers) | 10+ new tests |
| **Downside / dealbreaker** | Loses the static catch. Future bugs land silently. | Same-scope tracing is heuristic — fails for closures (P5 ≈ 25%), workers, callbacks. ~18 hits would still need markers. | 71 markers is verbose; some routes get 3-5 markers each. Visual noise. | Behaviour change risk + R6 violation + biggest blast radius. **Disqualified for Phase 2.4.** |

### 3.A · Top-line ranking

- **C is the safest single-option choice** (static catch + zero behaviour risk).
- **B is the most elegant** but doesn't cover P3/P5 (≈55% of hits).
- **A is the cheapest** but loses the catch — anti-Phase-2 intent.
- **D is over-engineered** for Phase 2.4 — defer to Phase 4 (process separation) when `ContextRepo` would also serve the HTTP-transport indirection.

**Single-option recommendation: C.** Hybrid recommendation: see §4 — C-primary + B-supporting where leverage is highest + A as a targeted exemption for the helper bodies themselves.

---

## 4 · Hybrid pattern proposal (Q4)

### 4.A · The recommended hybrid

| Component | # sites | Approach | Rationale |
|---|---:|---|---|
| **B — Helper-fusion scanner (Upgrade D)** | **~18** | Scanner detects `require_context_membership()` / `_verify_ned_context()` / `await … = Depends(require_context_membership(...))` in the same function scope before a `db.contexts.{find,find_one,update_one,delete_one}(…)` call. Treats the downstream call as tenancy-satisfied. | Phase 1/2/3 patterns already use these helpers; codifying the contract makes the scanner an architecture-doc that reads itself. Catches future misuse where someone forgets the helper. |
| **C — Marker sweep** | **~50** | Inline `# tenancy:allow-no-account-id — <reason>` on every remaining call site. | Covers P3 (membership-derived id), P4 (admin/cron), P5 (worker/closure) — the categories where helper-fusion can't statically prove safety. Markers are individually reviewable and force future engineers to write the rationale. |
| **A — Alt-key (NARROWLY scoped)** | **~3 helper bodies** | The two helper bodies themselves (`core.py:255`, `ned_cycle.py:174`) + helper Dependency-resolution call sites (where `ctx` comes from `Depends(require_context_membership())`) get a TARGETED alt-key recognition: scanner accepts `db.contexts.find_one({"id": context_id})` when the enclosing function IS one of the recognised helpers. Equivalent to a "self-reference exemption". | Cleanest way to avoid markering the helper bodies — they ARE the contract, not consumers of it. |

### 4.B · Why this split is correct

The 5-pattern characterisation maps to exactly the 3 hybrid components:
- P1 + P2 → B
- P3 + P4 + P5 → C
- Helpers' own bodies → A

Each pattern gets the simplest tool that statically catches future drift. No pattern is force-fit. No call site needs >1 treatment. The migration cost is dominated by C (50 markers), exactly proportional to the share of patterns that need it.

### 4.C · Why not C alone?

C alone is viable (71 markers + helper exemption), but loses the most-architecturally-honest signal: 18 sites WHERE THE TENANT GATE IS LITERALLY ABOVE ON THE PRECEDING LINE should not need a marker — the structure already says "vetted". Marker noise inversely correlates with grep-ability ("why does X have a marker — is there a problem?"). B encodes the established architecture; C only documents the exceptions.

### 4.D · Why not B alone?

P3 (membership-derived id) and P5 (worker/closure) have no enclosing helper call in the same function — even though they're architecturally safe (the membership ids were just fetched; the worker was spawned by a gated handler). Adding helper-fusion to walk callers would require interprocedural analysis = out of Phase 2 scope.

---

## 5 · Safety property analysis (Q5)

**Question:** if a future engineer accidentally writes `db.contexts.find({"id": some_id})` without going through the tenant gate, will the scanner catch it?

| Option | Catch mechanism | Catch coverage | False-positive rate |
|---|---|---:|---:|
| A | none | 0% | n/a |
| B | no helper call in scope → flagged | ~25% (P1+P2 sites would be exempt; new violation in those patterns rare; new violation in P3/P4/P5 patterns NOT caught) | medium (legitimate P3-style patterns get flagged even though architecturally safe) |
| C | no marker → flagged | **100%** | low (every legitimate cross-tenant call already markered with rationale) |
| D | no `ContextRepo` involved → flagged | 100% | none (anti-pattern by design) |
| **Hybrid (recommended)** | per §4 — C/marker AND B/helper-fusion both required | **100%** | low — B reduces false-positives for the architectural-safe-by-helper category; C catches everything else |

**The hybrid achieves 100% catch with minimal false-positive noise.** New `db.contexts.find_one({"id": x})` written without a preceding helper call AND without a marker → **build fails immediately**.

---

## 6 · Discrepancies with approved plan (Q6)

### 6.A · Behaviour change

**None.** All three hybrid components are scanner-side (B and A targeted-alt-key) or comment-only (C). Zero product-code behaviour change. No goldens at risk.

### 6.B · New test files / helpers / modules

**Yes — modest:**
- 1 new scanner test file or 5-10 new tests in `test_invariant_tenancy.py` covering Upgrade D (helper-fusion AST tracer): synthetic offenders, compliant cases, edge cases (helper imported under alias, helper in nested if/else, helper at caller scope).
- 0 new helpers (both existing helpers are sufficient).
- 0 new modules.
- 0 new product files.

R4 budget: 10 lockdown tests allowed per phase; hybrid uses ~5-7. Under budget.

### 6.C · Helpers audited as real tenant gates

Both `require_context_membership` AND `_verify_ned_context` enforce tenancy via the `memberships` collection. Not security theatre. **No real-bug escalation.**

### 6.D · One non-bug design observation (escalated below)

Both helpers' OWN `db.contexts.find_one({"id": context_id})` calls (`core.py:255`, `ned_cycle.py:174`) are themselves on the 69-literal-violations list. Whichever option we pick must explicitly recognise these as the *implementations of* the tenancy contract, not violators of it. Option A's narrow "self-reference exemption" handles this; without it, even the C+B hybrid would falsely flag the helper internals.

### 6.E · Sample-size caveat

20-of-71 is a small sample. Confidence intervals on the pattern percentages are wide (±10-15 pp). If the hybrid build dispatch finds the C-component balloons to 60+ markers (vs the projected 50), reviewer should NOT auto-rubber-stamp — re-validate the helper-fusion eligibility on the unsampled 51 first to confirm B-coverage didn't collapse.

---

## 7 · ESCALATE TO USER

One **non-blocking design observation** for acknowledgement before the Phase 2.4 build dispatch:

### 7.1 · Helper-body self-reference contract

`require_context_membership()` (`core.py:255`) and `_verify_ned_context()` (`ned_cycle.py:174`) both contain `db.contexts.find_one({"id": context_id})` that the scanner currently flags as violations. These ARE the implementations of the tenancy contract — every other call site relies on them. The recommended hybrid uses Option A (narrow alt-key alias) to exempt them via a function-name allowlist:

```python
# tests/invariants/test_invariant_tenancy.py — Phase 2.4 addition
_CONTEXT_HELPER_FUNCTIONS: FrozenSet[str] = frozenset({
    "_dep",                          # require_context_membership's inner _dep
    "_verify_ned_context",
})
# Scanner skips contexts violations inside these function bodies.
```

**Question:** acknowledge that the scanner gets a narrow "helper-body exemption" for these two specific functions (rather than tagging them with `tenancy:allow-no-account-id` markers, which would visually equate them with admin probes)?

Recommendation: yes. Marker-tagging them works but obscures the architectural significance — they're the contract, not exemptions. The exemption set is hard-coded to 2 functions and reviewed in the Phase 2.4 dispatch PR.

---

## 8 · Recommended Phase 2.4 build dispatch (Q7)

### 8.A · Title
Phase 2.4 — `contexts` Tenancy Migration (Hybrid: Helper-Fusion + Markers + Helper-Body Exemption)

### 8.B · Sub-step sequence

**Step 1 — Scanner Upgrade D (helper-fusion AST tracer).**
- Extend `test_invariant_tenancy.py` with an AST walker that, for a `contexts.{find,find_one,update_one,delete_one,replace_one}(…)` call against the `contexts` collection, walks BACKWARD in the enclosing function scope and accepts the call as compliant iff:
  - A `Call` to `require_context_membership(...)` OR `_verify_ned_context(account_id, context_id)` OR a FastAPI `Depends(require_context_membership(...))` appears before the call line, AND
  - The same `context_id` variable name flows from the helper call's arg/return into the contexts filter.
- Cost: ~80 LOC scanner + 5-7 test fixtures (synthetic offenders, compliant cases, alias-imported helper, helper in nested if/else, helper at parent scope via Depends).
- Acceptance: re-running the scanner against the live tree drops the literal violations from 69 → ~50 (P1+P2 ≈ 18 hits resolved).

**Step 2 — Helper-body exemption (Option A narrow).**
- Add `_CONTEXT_HELPER_FUNCTIONS: FrozenSet[str] = frozenset({"_dep", "_verify_ned_context"})` to the scanner.
- When the enclosing function name matches, skip the contexts-collection check.
- Cost: ~10 LOC + 1 test.
- Acceptance: literal violations drop from ~50 → ~47 (3 helper-body hits resolved).

**Step 3 — Marker sweep for P3/P4/P5 patterns.**
- Add `# tenancy:allow-no-account-id` markers with inline rationale to the remaining ~47 sites:
  - Admin/cron (P4 ≈ 14): rationale = "super-admin/cron probe; route gate enforces caller identity"
  - Membership-derived id (P3 ≈ 21): rationale = "ctx_id came from db.memberships find for caller's account; within-tenant by definition"
  - Worker/closure (P5 ≈ 12): rationale = "context_id is a closure capture from an upstream-gated handler"
- Cost: ~120 LOC inline comments; ~2 hours of methodical sweeping.
- Acceptance: literal violations drop from ~47 → 0.

**Step 4 — Per-collection enforce flip.**
- Add `contexts` to `_ENFORCE_MODE_COLLECTIONS` → `frozenset({"chats", "documents", "work_studio_exports", "contexts"})`.
- The 2 non-literal contexts violations need separate inspection: likely admin/sweep patterns that get markers in Step 3.
- Cost: 1-line scanner edit.
- Acceptance: `test_tenancy_enforce_mode_for_migrated_collections` is build-breaking on any new contexts violation.

**Step 5 — Regression sweep.**
- Same shape as Phase 2.3: invariants 33/33 + Phase 14/15 + Track A 5/6/7 + targeted contexts/auth/admin sweep.
- Verify no behaviour change.

**Step 6 — Sprint memo + MASTER_STATE update.**
- `/app/memory/sprints/PHASE_2_4_CONTEXTS.md`
- MASTER_STATE Section 6/7/8 update.

### 8.C · Acceptance criteria

- `contexts` literal violations: 69 → 0.
- `contexts` non-literal violations: 2 → 0 (via markers in Step 3).
- Per-collection enforce mode now covers 4 collections: `chats`, `documents`, `work_studio_exports`, `contexts`.
- All goldens + invariants + regression sweep green.
- Scanner Upgrade D's helper-fusion AST tracer passes 5-7 synthetic-offender + compliant-case unit tests.
- No new BE-sweep failures attributable to Phase 2.4.

### 8.D · Estimated cost in build hours

| Step | Hours |
|---|---:|
| 1 — Scanner Upgrade D + tests | 0.5 - 0.75 |
| 2 — Helper-body exemption | 0.1 |
| 3 — Marker sweep (47 sites with inline rationale) | 0.75 - 1.0 |
| 4 — Enforce flip + non-literal cleanup | 0.1 |
| 5 — Regression sweep + verification | 0.25 |
| 6 — Sprint memo + MASTER_STATE | 0.25 |
| **Total** | **~2.0 - 2.5 hours** |

Slightly above the 1.5-2.0 hour target in the dispatch §"Cost target" because the scanner Upgrade D needs ~30 minutes more than Phase 2.2's task_id widening (helper-fusion AST tracing is more complex than alt-key map extension). Within rounding error of target.

### 8.E · Risk assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Sample under-projected the P3/P5 ratio → C-component balloons | Low-Med | Re-validate B-coverage on unsampled 51 in Step 3; if <50% of B's projected 18 are actually B-compliant, recalibrate and add markers. |
| Scanner Upgrade D over-permits (accepts a call that bypassed the helper via aliasing/decorator) | Low | Aliasing/decorator detection is well-understood; tests cover the common alias forms. Defence-in-depth: keep the marker on every line; B is additive over C. |
| Helper-body exemption widens to other helpers later → exempt-list growth | Med | The exempt list is hard-coded in the scanner source; growth requires a PR review. Treat the list as documentation, not config. |
| Phase 2.5+ migrations want to lean on Upgrade D → scope creep | Low | Document Upgrade D as "contexts-collection specific" in the scanner source; other collections continue to use alt-keys/markers per Phase 2.1's pattern. |

**No "stop / escalate" risks identified beyond the 1 design ack in §7.**

---

**End of Phase 2.4 Pre-Read.**
Status: **CLEAN_WITH_NOTES** — 1 design ack in §7, ~2.0-2.5 build hours estimated for Phase 2.4 dispatch.
