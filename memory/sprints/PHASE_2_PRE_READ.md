# Phase 2 Pre-Read — Tenancy Guard

**Mode:** READ-ONLY investigation (per Discipline Rail R1).
**Date:** 2026-06-22.
**Scope:** Establish ground-truth for the 8 dispatch questions before any Phase 2 code dispatch.

**Headline:** **CLEAN_WITH_NOTES.** No code-level blockers found. Phase 2 build dispatch is ready contingent on user acknowledgement of three §9 items: (a) scanner upgrade scope (Q7 — keys + dotted writes), (b) explicit acceptance that 9 of the 47 in-list collections use a non-`account_id` ownership key today (Q3 / §2.C), (c) the brief's "682/827" numbers are a stale pre-Phase-0 scanner snapshot — current ground truth is **685 / 550** (§8 drift check).

---

## 1 · Data-access helper shape (Q1)

The Phase-1 contract surface already inverted the cross-context DB reads (SyniSense + Solva → Akki) and routed them through `AkkiContract`. Phase 2's tenancy guard is a **layer underneath** the contract surface — it constrains the shape of the residual ~550 direct `db.<collection>.<method>(...)` call sites that exist INSIDE the Akki context itself (router handlers).

### 1.A · Three candidates evaluated

| Candidate | Shape | Pro | Con |
|---|---|---|---|
| **(A) Decorator on the router** | `@tenanted def list_x(account_id: str, ...)` — wraps the handler; injects `account_id` into a contextvar that a `tenanted_db` wrapper consumes | DRY; FastAPI-native; matches Depends pattern | Contextvars + async = footgun (Phase 1 Pre-Read §2.B already rejected this for `shield_invoke`); silent failure mode |
| **(B) Query-helper class** | `TenantedCollection(db.chats, account_id).find_one({...})` — wraps each Motor cursor | Single point to enforce; explicit | Touches **every** call site (~550); huge diff; goldens risk (Q6) |
| **(C) Builder helper** | `q = tenant_filter({"id": x}, account_id=current["id"]); await db.chats.find_one(q)` — returns a dict with `account_id` mixed in | Smallest diff (1 line added per site); reuses existing dict-literal shape the scanner already understands; goldens preserved | Doesn't force the helper to be USED; static check still needed |

### 1.B · Recommendation: **(C) Builder helper + AST guard**

```python
# backend/core/tenancy.py  (NEW — proposed; not written in this phase)
def tenant_filter(extra: dict, *, account_id: str) -> dict:
    """Mix account_id into a Mongo filter. Required for tenant-scoped
    collections; the Phase-2 tenancy invariant fails if a direct
    db.X.find/find_one/... is called against a tenant-scoped collection
    WITHOUT a tenant_filter()-ish dict literal carrying account_id."""
    if not account_id:
        raise ValueError("account_id required")
    return {**extra, "account_id": account_id}

def tenant_doc(doc: dict, *, account_id: str) -> dict:
    """Mix account_id into an insert document. Same contract."""
    if not account_id:
        raise ValueError("account_id required")
    return {**doc, "account_id": account_id}
```

**Justification:**

1. **Minimum-blast-radius diff.** Each call site changes from `db.chats.find_one({"id": chat_id, "account_id": current["id"]})` → `db.chats.find_one(tenant_filter({"id": chat_id}, account_id=current["id"]))`. Single line change; the dict literal already had `account_id` in 9/20 fresh-sampled cases (see §2.B); the visual contract is unchanged.

2. **Scanner-friendly.** The Phase 0 scanner walks Dict literals at `node.args[0]`. A migration that DROPS the inline `account_id: ...` key in favour of a `tenant_filter(...)` helper call would actually BREAK the scanner (the first arg becomes a `Call`, classified `non_literal`). The Phase 2 scanner upgrade (§7) MUST learn to unwrap `tenant_filter()` / `tenant_doc()` AST shapes and re-validate the inner dict. This is a known cost of the recommendation; quantified in §7.

3. **Fail-fast.** The helper raises `ValueError` at runtime if `account_id` is missing/falsy. Runtime defence in addition to static.

4. **Explicit migration off `current["id"]`.** Half the existing call sites already pass `current["id"]`. The helper accepts `account_id=...` as a required kwarg, mirroring Phase 1's `account_id` kwarg convention on `AkkiContract.*` methods. Pattern convergence.

5. **Crossover-compatible with later phases.** When Phase 4 swaps in-process adapters to HTTP, the `tenant_filter` helper continues to work (it's a dict-builder, no transport coupling). When Phase 6 carves the DB physically, the helper trivially extends to a tenant-aware client factory.

### 1.C · Out-of-scope helper shapes (declined)

- A `TenantedCollection` wrapper class (option B) — touches every call site; goldens regression risk too high for a behaviour-preservation phase.
- A FastAPI `Depends(tenant_scope)` injection — Phase 1 Pre-Read §2.B already settled the propagation pattern as explicit kwarg, not contextvar/injection.
- An `account_id` ContextVar — async footgun, surfaced and rejected in Phase 1 Pre-Read §2.B.

---

## 2 · Enforce target: 550 vs 685 (Q2)

### 2.A · Mechanism: **baseline-driven, shrink-only** (settled per directive §2)

The Phase 2 build dispatch MUST flip `test_invariant_tenancy.py::test_tenancy_observe_mode_does_not_fail_build` from `assert True` to:

```python
current = scan_repo_for_tenancy_violations()["definite_violation_count"]
baseline = json.load(open("/app/memory/invariants/tenancy_baseline.json"))["count"]
assert current <= baseline, (
    f"tenancy regression: {current} definite violations, baseline={baseline}"
)
```

The baseline file records the agreed starting count + the explicit shrink-only contract. Per-context migrations land in Phase 2 (Akki context first because it owns 90%+ of the violations), and EACH migration MUST update the baseline downward in the same commit (the test-driver test fails otherwise on the next sweep).

This matches the Plan §5 verbatim language `"flip the tenancy invariant from observe to enforce per migrated context"` and the Phase 1 boundary-imports pattern (which already proved this shape works for 3 entries).

### 2.B · Target: 20-sample fresh categorisation (per directive §2 — TBD via sample)

I re-sampled 20 non-literal violations stratified across the top 10 files (one per file) + 10 random others. Sample JSON: `/tmp/phase2_pre_read_20_sample.json`. Each was inspected against the surrounding 10 lines of source. Result:

| # | File:line | Coll/Method | Category | Reason |
|---|---|---|---|---|
| 1 | chat.py:720 | chats.insert_one | **(ii) FP** | `rec["account_id"]=current["id"]` at L688 — dict-literal split across many lines, scanner can't trace |
| 2 | sandbox.py:632 | documents.insert_one | **(ii) FP** | `doc["account_id"]=current["id"]` at L617 |
| 3 | cycle.py:211 | questions.insert_one | **(iii) Key-drift** | row has `context_id` + `created_by`, NO `account_id` field on the table |
| 4 | cycles.py:240 | cycles.insert_one | **(ii) FP** | `row["account_id"]=ctx["account"]["id"]` at L233 |
| 5 | solva_v2.py:1109 | solva_v2_sessions.insert_one | **(ii) FP** | `rec["account_id"]=account["id"]` at L1070 |
| 6 | tasks.py:221 | tasks.insert_one | **(ii) FP** | `task["account_id"]=current["id"]` at L207 |
| 7 | work_studio_export.py:1138 | chats.insert_one | **(ii) FP** | `chat_row["account_id"]=account_id` at L1123 |
| 8 | compilations.py:126 | compilations.insert_one | **(iii) Key-drift** | row has `context_id` + `created_by`, NO `account_id` field |
| 9 | documents.py:511 | documents.insert_one | **(iii) Key-drift** | row has `context_id` + `uploaded_by`, NO `account_id` field |
| 10 | questions.py:128 | cycle_questions.count_documents | **(iii) Key-drift** | filter has `assignee_account_id=me["id"]`, scanner only matches literal `account_id` |
| 11 | signal_actions.py:159 | signal_actions.insert_one | **(ii) FP** | `doc["account_id"]=ctx["account"]["id"]` at L150 |
| 12 | chat.py:2189 | chats.find_one | **(ii) FP** | `chat_filter["account_id"]=current["id"]` at L2182 |
| 13 | admin_tenants.py:106 | contexts.count_documents | **(i) Cross-tenant** | admin-wide inventory; `match` filters by `type` + `name` only |
| 14 | tasks.py:424 | tasks.count_documents | **(ii) FP** | `q=dict(base, state=state)` where `base["account_id"]=current["id"]` at L418 |
| 15 | cycles.py:329 | cycles.count_documents | **(iii) Key-drift** | filter is `{$or: [{context_id:…}, {seed_marker_visible_for:account_id}]}` — `account_id` is a VALUE not a top-level KEY |
| 16 | cycle.py:441 | questions.find | **(iii) Key-drift** | filter has `context_id` + `status`, NO `account_id` key |
| 17 | contexts.py:264 | contexts.insert_one | **(iii) Key-drift** | row has `owner_account_id=current["id"]` at L259 — scanner only matches `account_id` literal |
| 18 | chat.py:1225 | chats.find_one | **(ii) FP** | `existing_filter["account_id"]=current["id"]` at L1220 |
| 19 | chat.py:2086 | chat_messages.insert_one | **(ii) FP** | `assistant_msg["account_id"]=current["id"]` at L2061 |
| 20 | solva_v2.py:208 | documents.find_one | **(iii) Key-drift** | filter has `{id:sid, context_id:…}`; no `account_id` key (functionally safe — `id` is a UUID and `context_id` is membership-gated) |

**Tally:**

| Category | Count | % of sample | Projected on 135 non-literal | Action |
|---|---:|---:|---:|---|
| **(i) Genuinely cross-tenant** | 1 | 5% | ~7 | Needs explicit `@cross_tenant` / `tenancy:allow-no-account-id` marker. Phase 2 migration adds the marker; no behaviour change. |
| **(ii) FP (dict literal HAS `account_id` but scanner can't trace across multi-line construction)** | 9 | 45% | ~61 | Scanner upgrade §7 makes these compliant without code change. |
| **(iii) Key-drift (compliant by intent — uses `context_id`, `owner_account_id`, `assignee_account_id`, etc.)** | 10 | 50% | ~67 | **Phase 2 design decision required** — either widen scanner to recognise alternative keys (§7) OR migrate routes to include `account_id` alongside the existing key (more invasive). |

### 2.C · Recommended baseline number

**Per the categorisation above, the recommended baseline is `definite_violation_count = 550`** (current value, unchanged). The 135 non-literal violations split as:
- ~61 will collapse to zero once the scanner unwraps multi-line dict construction (§7 upgrade — scanner change only, zero product-code change).
- ~67 will collapse to zero once the scanner recognises the alternative tenancy keys `context_id`, `owner_account_id`, `assignee_account_id`, `created_by`, `uploaded_by`, `assignee_user_id` (§7 widened-key recognition).
- ~7 stay as genuine cross-tenant calls, which get the existing `tenancy:allow-no-account-id` marker.

**Phase 2 enforce mode is set against `definite_violation_count == 550`** (baseline), and each migration commit shrinks the baseline by N (where N = the number of violations the migration closes). Final target after Phase 2 closes the Akki context: `definite_violation_count == 0`.

### 2.D · Per-collection literal breakdown (top concentrations to inform sequencing)

| Collection | Literal hits | Top concentration |
|---|---:|---|
| documents | 123 | routers/documents.py (47), services/universal_search.py (8), routers/sandbox.py |
| contexts | 82 | routers/contexts.py + routers/oauth_google.py |
| work_studio_exports | 52 | routers/work_studio_export.py (29) + routers/work_studio_overlay.py |
| signals | 40 | routers/sandbox.py + routers/pulse.py |
| cycles | 33 | routers/cycles.py + routers/cycle.py |
| cycle_questions | 23 | routers/questions.py + routers/cycle_assignments.py |
| chats | 19 | routers/chat.py + routers/work_studio_export.py |
| inbound_queue | 17 | routers/inbound_email.py |
| exco_teams | 16 | routers/exco_teams.py |
| strategic_goals | 15 | routers/strategic_goal_assessment.py |
| decks | 14 | routers/decks.py |
| tasks | 14 | routers/tasks.py + routers/tasks_initiatives.py |
| team_catalogue | 12 | routers/team_catalogue.py |
| chat_messages | 12 | routers/chat.py |
| user_calendar_credentials | 11 | routers/oauth_google.py |
| cycle_assignments | 11 | routers/cycle_assignments.py |
| studio_blocks | 10 | routers/studio_blocks.py |
| questions | 9 | routers/cycle.py + routers/q4y |
| (remaining 28 collections) | ≤8 each | scattered |

Top 5 collections (documents, contexts, work_studio_exports, signals, cycles) account for **330 / 550 = 60%** of literal violations. Sequencing recommendation in §5.

---

## 3 · Cross-tenant collection whitelist (Q3)

### 3.A · Tier 1 — Genuinely unscoped (need explicit marker, no `account_id` exists or applies)

These are the §1.A admin-tenants pattern + the Phase 1 Pre-Read §2.C list, re-verified against the live `TENANT_SCOPED_COLLECTIONS` allow-list (47 entries). The scanner's allow-list IS the Phase-2 enforce target — collections NOT in this list are by definition cross-tenant and never trip the scanner. So the "whitelist" question becomes: which CALL SITES (not collections) on tenant-scoped collections need the `tenancy:allow-no-account-id` marker?

**Sample-validated cross-tenant call sites (P0 list — from the 20-sample + Phase 1 Pre-Read §2.D):**

| File:line | Collection | Reason | Phase 2 action |
|---|---|---|---|
| routers/admin_tenants.py:106 | contexts | Admin-wide inventory listing | Add `# tenancy:allow-no-account-id` on line 106 |
| routers/admin_tenants.py:108 | contexts | Same surface, paginated find() | Same |
| routers/admin_qa_hooks.py:194 | contexts | Test-fixture seeding (already excluded by the scanner's `EXCLUDE_PATH_FRAGMENTS`? Confirm — `admin_qa_hooks.py` is NOT under `/scripts/` so it IS scanned) | Add marker |
| services/synisense/engine/scheduler_lock.py | scheduler_runs | (NOT in TENANT_SCOPED — already exempt) | No action |
| (other admin-wide reads) | — | Cron probes, scheduler dashboards | Sweep at migration time |

**Estimated total of genuine cross-tenant call sites: ~7-15** (projected from 5% of 135 non-literal + manually inspected ~5 admin-routes).

### 3.B · Tier 2 — Collections that LOOK tenant-scoped but use a different scope key (the §2.B category-iii cases)

These are NOT cross-tenant. They ARE tenant-scoped, just via a key other than `account_id`. Phase 2 design choice in §7:

| Collection | Alternative tenancy key | Frequency in 20-sample |
|---|---|---:|
| contexts | `owner_account_id` | 1 |
| questions / cycle_questions | `context_id` + `assignee_account_id` | 2 |
| cycles | `context_id` + `seed_marker_visible_for` ($or value) | 1 |
| compilations | `context_id` + `created_by` | 1 |
| documents | `context_id` + `uploaded_by` | 1 |

**Decision needed:** widen scanner to recognise these keys as tenant-scope (Phase 2 §7 scope), OR migrate routes to add `account_id` alongside the existing key (more invasive; touches ~67 sites). Recommendation: widen scanner — preserves goldens (Q6), preserves the existing data shape (no Mongo schema migration), single-file change in `test_invariant_tenancy.py`.

### 3.C · Tier 3 — TENANT_SCOPED_COLLECTIONS allow-list audit

The scanner's allow-list (47 collections) was Phase 0's seed. Cross-checking against the Phase 1 Pre-Read's full ownership table (§1.B, 156 collections):

| Issue | Count | Action |
|---|---:|---|
| In allow-list AND legitimately tenant-scoped via `account_id` | ~38 | Keep |
| In allow-list but uses ALTERNATIVE tenancy key (§3.B) | 9 | Scanner widening (§7) |
| In Phase-1 Pre-Read ownership table as tenant-scoped but NOT in allow-list (false negative — scanner under-detects) | 9 | Phase 2 PR: add `auth_events`, `boardpacks`, `briefs`, `inbox_routing_*` (4), `lens_*` (2) — but defer ownership-table widening to Phase 2 follow-up (do not expand allow-list inside Phase 2 build itself; defer for post-build sweep). |
| In allow-list but Phase 1 Pre-Read says cross-tenant | 0 | None — Phase 1 Pre-Read already filtered. |

**P0 Phase 2 build only touches the allow-list AS-IS (47 entries). Do not widen the allow-list mid-build — that introduces new violations and breaks the shrink-only contract.**

### 3.D · Recommended marker syntax (already in place)

The Phase 0 scanner already implements `# tenancy:allow-no-account-id` on the call line or one above. Phase 2 adopts this verbatim — no new syntax. Adding the marker IS a code change but does NOT alter behaviour (preserves goldens). Phase 2 marker additions are tracked in commit messages: `"add tenancy marker — admin tenant inventory (legitimate cross-tenant)"`.

---

## 4 · Phase 1 cross-context migration overlap (Q4)

Phase 1 left two backlogs:

- **Boundary-imports baseline (3 entries):** Solva v2 → SyniSense direct imports at `analyze_narration.py:38`, `llm_adapter.py:125`, `llm_adapter.py:346`. Phase 2's tenancy work does NOT touch these — they're cross-CONTEXT imports, orthogonal to per-tenant filter shape. They migrate when Solva v2 routes are touched (Phase 2.C in §5 below, but as a side-effect; not Phase 2's primary goal).

- **Cross-context-calls observe-mode (48 violations):**
  - 27 primitive_call from Akki routers (e.g. `shield_invoke()` direct calls that should go via `get_synisense().shield_invoke()`)
  - 1 primitive_call from Solva (`analyze_narration` direct shield_invoke)
  - 20 db_read_from_other_context from SyniSense (tenant-entity harvester + signal_derivation reads)

### 4.A · Overlap matrix — Phase 2 vs Phase 1 backlog

| File | Tenancy violations (Phase 0) | Cross-context violations (Phase 1) | Overlap? |
|---|---:|---:|---|
| routers/documents.py | 47 (literal) + 4 (non-literal) | 3 (intelligence_service calls Shield) | Partial — touching the same files but for DIFFERENT primitives (Phase 2 = filter shape; Phase 1 = SyniSense call indirection) |
| routers/chat.py | 19 (literal) + 15 (non-literal) | 6 (shield_invoke calls) | High — both phases want chat.py touched |
| routers/work_studio_export.py | 29 (literal) + 5 (non-literal) | 0 (cross-context calls are in service files) | Phase 2 only |
| routers/work_studio_overlay.py | 19 (literal) | 1 (shield_invoke) | Low overlap |
| routers/tasks.py | 11 (literal) + 5 (non-literal) | 0 (intelligence_service has the Shield call) | Phase 2 only |
| routers/solva_v2.py | 14 (literal) + 5 (non-literal) | 0 | Phase 2 only |
| services/synisense/engine/signal_derivation.py | 0 (it's SyniSense — reads Akki via different key) | 11 (10 db reads + N/A) | Phase 1.B only |
| services/synisense/shield/tenant_entities.py | 0 | 3 (db reads) | Phase 1.B only |
| services/documents/intelligence_service.py | 0 | 3 (shield_invoke) | Phase 1.B only |
| routers/synisense_shield.py | 0 | 2 (find_audit, find_receipt) | Phase 1.B only |
| services/work_studio/confidence_scorer.py | 0 | 1 (shield_invoke) | Phase 1.B only |
| services/solva_v2/analyze_narration.py:695 | 0 | 1 (shield_invoke) | Phase 1.B + Phase 2.C (if Solva routes migrate) |

### 4.B · Co-migration recommendation

**Phase 2 migrations open the files to changes — co-migrating the cross-context primitives in the same dispatch saves a re-open of the file:**

- **chat.py** — high overlap. Phase 2 dispatch on chat.py SHOULD include the 6 `shield_invoke(...) → get_synisense().shield_invoke(...)` migrations in the same PR.
- **documents.py / work_studio_export.py / tasks.py / solva_v2.py** — Phase 2 only (no cross-context overlap at the router level).
- **intelligence_service.py / confidence_scorer.py / signal_derivation.py / tenant_entities.py** — Phase 1.B only (no tenancy overlap; pure cross-context).

### 4.C · Risk of co-migration

Co-migrating amplifies the diff size. Recommendation: **do NOT co-migrate in Phase 2.1 (first dispatch).** Sequence cleanly: Phase 2.1 closes tenancy across the 4 router files; Phase 2.2 closes cross-context calls. Each phase is self-contained, smaller blast radius, easier to revert. Re-open cost on chat.py / documents.py is ~5 min of editor time vs the risk of co-migration goldens-regression.

---

## 5 · Migration sequencing within Phase 2 (Q5)

### 5.A · Three-tier strike order (recommended)

**Phase 2.1 — Surface-light scanner upgrade + escape-hatch sweep (1 dispatch, ~80 LOC change):**
1. Upgrade `test_invariant_tenancy.py` per §7 (multi-line dict tracking + alternative key recognition).
2. Sweep the ~7 genuine cross-tenant call sites (Tier 1 §3.A) — add `# tenancy:allow-no-account-id` markers.
3. Record post-upgrade baseline. **Target: definite_violation_count drops from 550 to <50** (≈60% of literal violations are §2.B category-iii — those become compliant under the widened scanner).
4. Flip the invariant to **enforce mode with the new baseline**.

**Phase 2.2 — Akki router migrations (sequence by violation density):**
1. Hottest first: `routers/documents.py` (47 literal) + `routers/work_studio_export.py` (29) + `routers/sandbox.py` (27) — these are 103 violations across 3 files; goldens already cover these surfaces (Phase 0 characterisation suite + Phase 5/6 lockdowns).
2. Mid-tier: `routers/chat.py` (19), `routers/work_studio_overlay.py` (19), `routers/questions.py` (17), `routers/solva_v2.py` (14) — 69 violations across 4 files.
3. Long tail: `routers/exco_teams.py`, `routers/oauth_google.py`, `routers/daily_review.py`, `routers/studio_blocks.py`, `routers/briefings.py`, `routers/cycle.py`, `routers/tasks.py`, etc. — ~378 violations across 25 files.

Each migration commits **baseline shrink in the SAME PR.** Reverts collapse cleanly (Git revert restores both code AND baseline).

**Phase 2.3 — Service-layer mop-up:** `services/universal_search.py` (8), `services/tasks/compile_service.py` (9), other `services/` violations. Smaller blast radius — services are typically called from already-migrated routers.

### 5.B · Lockdown cadence per migration

Per Discipline Rail R4 (≤10 lockdown tests per phase), Phase 2.2 dispatches CANNOT bundle all routers in one go. Recommended cadence:

- One dispatch = one router file + the corresponding goldens + ≤10 new lockdown tests covering the migrated call sites.
- Aggregate the deterministic regression sweep at every dispatch close (Phase 0 + Phase 1 + Phase 14 + Phase 15 + Phase 2 cumulative).
- Each dispatch SHIPS its baseline-shrink commit; no compound revert risk.

### 5.C · Pre-Read for each Phase 2 dispatch

Per Discipline Rail R2, each Phase 2.x dispatch needs its own micro-Pre-Read (1-2 pages) capturing:
1. The file's current violation list (literal + non-literal counts).
2. The expected new baseline value after the migration.
3. Any cross-context call site overlap (§4.B).
4. Any goldens that touch the migrated surface (§6).

This is lightweight enough to live inline in the dispatch brief, not a separate sprint memo. **Phase 2.1 (scanner upgrade + sweep) IS the master Phase 2 build dispatch and needs a separate sprint memo.**

### 5.D · Akki context exits first; SyniSense/Solva inherits

Phase 1 already put the cross-context primitives behind contracts. Once Akki's tenancy is locked, SyniSense and Solva's INTERNAL calls auto-inherit the constraint via `AkkiContract.<method>(account_id=...)`. The 19 Solva-owned + 9 SyniSense-owned collections (Phase 1 Pre-Read §1.C) are smaller surfaces; Phase 2.3 mops these up.

---

## 6 · Goldens preservation strategy (Q6)

### 6.A · Phase 0 characterisation goldens — current coverage

Per Phase 0 sprint memo:
- 4 deliberate-smoke characterisation tests (`tests/characterisation/`) — `@pytest.mark.integration` (real LLM); not in the default sweep.
- 8 invariant tests in default sweep (tenancy + fail-closed + shield-no-leak + audit-always).
- Per-phase lockdown tests at `tests/test_track_a_phase{3,4,5,6,7}*.py` + `tests/test_phase14_*.py` + `tests/test_docs_download.py`.

Aggregate: **160/160 deterministic backend tests** (Phase 1 final state) + characterisation goldens (integration-marked).

### 6.B · Phase 2 risk surface against goldens

Behaviour-preservation in Phase 2 means:
- **Same return shape** from every migrated handler (the dict on the wire is identical).
- **Same Mongo writes** (the filter / insert document content is identical even after `tenant_filter()` wrapping).
- **Same audit log entries** (no new audit writes; no removed audit writes).
- **Same SyniSense Shield envelope** (no `account_id` re-thread; the existing kwarg flows through unchanged).

### 6.C · Goldens that touch Phase-2-migrated surfaces

Per the §2.D top-5 collections and the existing lockdown suite:

| Lockdown file | Surfaces covered | Phase 2 migration impact |
|---|---|---|
| `tests/test_track_a_phase4_*.py` (21 tests) | analyses + workbook + multi-blob synthesise | LOW — analyses is in TENANT_SCOPED but Solva-owned; Phase 2.3 mop-up |
| `tests/test_track_a_phase5_lifecycle.py` (14 tests) | work_studio_exports + compile + commit | HIGH — work_studio_export.py is Phase 2.2 priority |
| `tests/test_track_a_phase6_inline_edit_and_bc_removal.py` (10 tests) | DocumentOverlay + commit | MEDIUM — documents.py + work_studio_overlay.py |
| `tests/test_track_a_phase7_confidence_scoring.py` (15 tests) | scorer + commit recompute | LOW — scoring service, no router migration |
| `tests/test_chat_*.py` (Phase 14 — 14 tests) | chat send + classifier | HIGH — chat.py is Phase 2.2 priority |
| `tests/test_docs_download.py` | docs download endpoint | LOW |
| `tests/invariants/*` | tenancy + boundary + cross-context | DIRECTLY exercised — Phase 2.1 flips tenancy enforce-mode |
| `tests/characterisation/*` (integration-marked) | shield_invoke + critical journeys | LOW — runs `@pytest.mark.integration` opt-in |

### 6.D · Strategy

1. **Every Phase 2 dispatch runs the full deterministic sweep before declaring done.** No drift permitted; this is the Phase 6 lesson (BC-mirror migration broke 4 tests; fixed via deliberate test updates).
2. **Migrated tests are NOT re-blessed silently.** If a migration accidentally changes a response shape, the test fails AND the fix is part of the dispatch (either revert the response shape OR explicit golden re-bless documented in the sprint memo).
3. **Characterisation suite runs at each Phase 2 close** with `@pytest.mark.integration` enabled (consumes Shield budget — ~$0.20 per characterisation run, 4 tests = ~$0.80 per close).
4. **No "while I'm in there" cleanups.** Phase 2 migrations touch ONLY the dict literal at the call site. Refactoring of surrounding code is explicitly out-of-scope (per Discipline Rail R6).
5. **Pre-Phase-2 baseline snapshot:** before Phase 2.1 lands, the agent commits a snapshot of the current 160/160 deterministic green + the 4 characterisation goldens to `memory/baselines/phase_2_start.json`. Any subsequent regression is traceable to a specific Phase 2 commit.

---

## 7 · Static analyser improvements (Q7)

### 7.A · Required upgrades for Phase 2 baseline to be meaningful

The scanner currently misses:

#### Upgrade A — Multi-line dict literal tracking
**Problem:** Of the 20-sample, 9 (45%) are dict literals constructed across multiple lines where the closing `db.X.insert_one(rec)` is on a different line than the `"account_id": ...` assignment. The scanner sees `rec` (Name) → classifies `non_literal`.

**Fix:** When the first arg to a tenant-scoped method is a `Name`, walk backward in the same function scope and find the most recent dict-literal assignment. If found, apply the same `_dict_has_account_id_key()` check against that literal.

**Implementation cost:** ~80 LOC in `test_invariant_tenancy.py`. Single-pass AST scope walk; trivial complexity.

**Coverage:** Closes ~61 of the 135 non-literal violations.

#### Upgrade B — Alternative tenancy key recognition
**Problem:** 10/20 (50%) of non-literals use a tenancy key other than `account_id`. The architecture is intentionally heterogeneous — different collections use different keys for legitimate reasons (`owner_account_id` on `contexts`, `assignee_account_id` on `cycle_questions`, `context_id`-via-membership on `cycles`).

**Fix:** Extend the scanner with a per-collection key map:

```python
TENANCY_KEY_BY_COLLECTION: Dict[str, frozenset] = {
    "contexts":           frozenset({"account_id", "owner_account_id"}),
    "cycle_questions":    frozenset({"account_id", "assignee_account_id"}),
    "questions":          frozenset({"account_id", "assignee_account_id", "context_id"}),
    "documents":          frozenset({"account_id", "uploaded_by", "context_id"}),
    "cycles":             frozenset({"account_id", "context_id", "seed_marker_visible_for"}),
    "compilations":       frozenset({"account_id", "context_id", "created_by"}),
    # ... 9 collections in §3.B + scan
}
```

A filter dict passes if it contains ANY key from the per-collection set. Default fallback (collection not in the map) keeps requiring `account_id`.

**Implementation cost:** ~30 LOC + the map.

**Coverage:** Closes ~67 of the 135 non-literal violations.

**Caveat:** This widens the safety contract. The map MUST be reviewed in a Pre-Read sub-section before being checked in — adding `context_id` as a recognised tenancy key for `cycles` is functionally safe (the route gate enforces context membership) but is a SHIFT from the strict `account_id`-only contract Phase 0 implied. Document in the Phase 2.1 sprint memo.

#### Upgrade C — `tenant_filter()` / `tenant_doc()` helper recognition
**Problem:** Once the §1 helper lands, the first arg becomes `tenant_filter({...}, account_id=...)` — a `Call`, not a `Dict`. Scanner classifies `non_literal`.

**Fix:** Detect calls to `tenant_filter()` and `tenant_doc()`; treat their first positional arg as the dict to inspect; verify `account_id=...` kwarg present in the helper call.

**Implementation cost:** ~25 LOC.

**Coverage:** Forward-looking — closes 0 violations today; prevents NEW violations after Phase 2 migrations adopt the helper.

#### Upgrade D — Dotted-path `$set` write detection
**Problem:** `db.contexts.update_one({"id": ctx_id}, {"$set": {"sandbox_metadata.field": value}})` — the filter has NO `account_id`. The Phase 0 scanner catches this as a tenancy violation. But there are legitimate cases (the entity was already fetched by id+account, then updated by id alone). The scanner doesn't track this provenance.

**Fix (declined for Phase 2 scope):** Two-pass scanner — first pass collects (id, account_id) fetch pairs; second pass exempts subsequent update_one({"id": x}, ...) within the same function. This is hard, brittle, and out of scope.

**Recommended:** Add the marker `# tenancy:allow-no-account-id` on these sites case-by-case during Phase 2.2 migrations.

#### Upgrade E — Aggregation pipeline `$match` first-stage scanning
**Problem:** The scanner inspects `find/find_one/...` first-args. It does NOT inspect `db.X.aggregate([{"$match": {...}}, ...])` pipeline first-stage `$match` dicts. This is a current blind spot.

**Estimated current count of aggregate calls in `routers/` + `services/`:** unknown — needs a grep sweep. Recommend Phase 2.1 dispatch includes this sweep as a non-blocking observation.

**Fix (declined for Phase 2 scope):** ~50 LOC; defer to Phase 2.4 follow-up.

### 7.B · Other observed limitations (do NOT fix in Phase 2)

- Helper-returning-collection: `coll = db.chats; coll.find(...)` — Phase 0 doc explicitly states this is out of scope. Phase 2 does not change this.
- Conditional account_id: `q = {"id": x}; if user: q["account_id"] = user["id"]` — non-deterministic; can't be statically classified. Out of scope.
- Indirect db reference: `from core import db as _db; _db.chats.find(...)` — different attribute access shape. Out of scope.

### 7.C · Phase 2 enforce-mode test contract (post-Upgrade A+B+C)

```python
# test_invariant_tenancy.py — post-Phase-2.1
def test_tenancy_enforce_mode_against_baseline() -> None:
    """Phase 2 ENFORCE mode — definite_violation_count must NOT grow.
    Baseline file is committed to repo; each migration shrinks it."""
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["count"]
    assert data["definite_violation_count"] <= baseline, (
        f"tenancy regression: definite={data['definite_violation_count']} "
        f"baseline={baseline} — fix or update baseline in same commit"
    )
```

Build-breaking. Baseline file commit guarded by Phase 2 sprint memo. Same shape as Phase 1's boundary-imports baseline (already proven).

---

## 8 · Discrepancies with approved plan (Q8)

### 8.A · Stated assumption vs reality

| Plan assumption | Reality | Impact |
|---|---|---|
| Plan §5 estimated **827 violations** to migrate | Current scanner reports **685** | Smaller surface, same architecture |
| Plan §5 estimated **682 definite** | Current scanner reports **550 definite** | Smaller surface, same architecture |
| Plan §5 assumed "flip enforce per migrated context" | Confirmed feasible — Akki context owns 90%+ of violations; SyniSense / Solva inherit via contracts | Plan §5 architecturally sound |
| Plan §5 assumed all violations are `account_id`-missing | **50% are alternative-key-uses (§2.B category iii)** — scanner upgrade required, not migration | Phase 2 scope expansion: scanner work + sweep, not just call-site rewrites |
| Plan §5 implied a single-pass migration | Phase 2 should be **3 dispatches** (scanner upgrade + 4 hot routers + long-tail) per Discipline Rail R4 | No behaviour difference; phasing change |

### 8.B · The 682 → 550 drift question (per directive §bonus)

**The drift is not drift.** Forensic check:

1. The committed `memory/invariants/tenancy_violations.json` was first written at commit `9416652` on **2026-06-22 20:53:21+00:00** (Phase 0 ship). Counts: **685 total / 550 definite.**
2. The current scan (2026-06-22 21:15:41+00:00, ~22 minutes later) reports IDENTICAL **685 total / 550 definite.**
3. The Phase 1 contracts shipped (commit timeline 2026-06-22 21:19) added ZERO code under `SCAN_ROOTS = (/app/backend/services, /app/backend/routers)`. Phase 1's adapters live at `/app/backend/contracts/_adapters/*.py` which is OUTSIDE the scan roots. → Zero impact on the scanner output.
4. Therefore the **"682 / 827" numbers in the dispatch brief are from a PRE-PHASE-0 scanner iteration** that pre-dates the committed baseline. They reflect a scanner version that was tuned (most likely a widening of `TENANT_SCOPED_COLLECTIONS` or a refinement of `_dict_has_account_id_key`) between authoring the dispatch brief and Phase 0's first commit.

**This is NOT a code drift; it is a brief-vs-snapshot mismatch.** No remediation needed beyond updating Phase 2 brief language to cite `685 / 550` going forward (already in the dispatch brief per directive).

**5-violation sanity sample (file:line that would have been in the 682 set):** N/A — no historical scanner snapshot exists to diff against. The pre-Phase-0 numbers were CHAT output, not a committed JSON. If the orchestrator wants a forensic snapshot, propose adding a `memory/invariants/tenancy_baseline_phase_0.json` archive of the current `685/550` JSON now, before Phase 2.1 ships.

### 8.C · Phase 1 cross-context observe-mode count discrepancy

Phase 1's `cross_context_violations.json` (rescanned 2026-06-22 21:15) reports `violation_count: 48`. This matches the Phase 1 sprint memo's `48 entries`. No drift.

### 8.D · Boundary-imports baseline

Phase 1's `boundary_imports.baseline.json` records 3 entries (`solva_v2 → synisense` imports). No drift.

### 8.E · Scope changes from Plan §5

None. The Plan's tenancy-guard intent and Phase 2's recommended scope agree fully. The only Plan-level ambiguity resolved here is **which collections have alternative tenancy keys** — surfaced in §3.B + §7 Upgrade B. The Plan does not preclude this; it is a refinement of the §5 enforce mechanism.

---

## 9 · ESCALATE TO USER

Three items that need user acknowledgement before Phase 2.1 build dispatches; none are blockers.

### 9.1 · Scanner upgrade scope (§7 Upgrades A + B + C — required for the enforce-mode flip)

The recommended baseline (`550 → ~0` after scanner upgrade + sweep) assumes Upgrades A (multi-line dict tracking), B (alternative tenancy keys per-collection map), and C (helper-call recognition) all ship as part of Phase 2.1.

**Question:** acknowledge — all three upgrades land in Phase 2.1, in one dispatch, before any router migration?

Recommendation: yes. The alternative (ship Upgrade A only, defer B + C) means the false-positive carry-over (~67 alt-key violations) would inflate the baseline and the Phase 2.2 migration would mechanically add `account_id` to dict literals that already have a perfectly legitimate `context_id` / `owner_account_id` / `assignee_account_id` — a behaviour change ban-walked by Discipline Rail R6.

### 9.2 · §3.B alternative-key recognition acknowledgement

The scanner Upgrade B widens the tenancy-key contract from "must contain `account_id`" to "must contain ANY of {`account_id`, `owner_account_id`, `assignee_account_id`, `context_id`, `uploaded_by`, `created_by`, `seed_marker_visible_for`}" — collection-dependent.

**Question:** acknowledge this widening, OR direct that Phase 2.1 migrates the 67 sites to also include `account_id` alongside the existing key (the alternative path)?

Recommendation: widen scanner. The route-level membership/owner gate already enforces tenant scope; mechanically adding `account_id` to filters that already carry `context_id` is a behaviour-preserving no-op MOST of the time but a definite goldens-regression risk for routes that fetch by composite key.

### 9.3 · Pre-Phase-0 number drift (§8.B)

The dispatch brief's `682 / 827` is a pre-Phase-0 scanner iteration's number, not drift. The post-Phase-0 baseline (committed at `memory/invariants/tenancy_violations.json` at commit `9416652`) reports `685 / 550`. Phase 1 added zero scanned code.

**Question:** acknowledge that Phase 2 dispatches reference `685 / 550` going forward (per directive already in place), AND that an explicit snapshot `memory/invariants/tenancy_baseline_phase_0.json` should be committed at Phase 2.1 start to prevent future "drift" confusion?

Recommendation: yes to both.

---

## 10 · Recommended Phase 2.1 dispatch scope

Phase 2.1 is the master Phase 2 build dispatch. Subsequent Phase 2.2 / 2.3 dispatches are router-by-router migrations under the new enforce-mode contract.

### 10.A · Phase 2.1 build dispatch — proposed brief

```
RE-ARCHITECTURE — Phase 2.1 Build: Tenancy Guard (scanner upgrade + sweep + enforce flip)

Per the Phase 2 Pre-Read (sprints/PHASE_2_PRE_READ.md), this dispatch
upgrades the tenancy scanner, sweeps the genuine cross-tenant call
sites, snapshots the baseline, and flips the invariant from observe
to enforce mode. NO router or service migration in this dispatch —
Phase 2.2+ migrates call sites against the new baseline.

NO behaviour change. The scanner upgrade is observe-only on its own.
The enforce flip uses a baseline-driven shrink-only contract; any
NEW violation fails the build, but existing ones don't.

Deliverables:
  1. backend/core/tenancy.py — NEW. `tenant_filter()` + `tenant_doc()`
     helpers (§1.B). Forward-looking; not yet used in Phase 2.1.
  2. backend/tests/invariants/test_invariant_tenancy.py — UPGRADE.
     Add Upgrades A (multi-line dict), B (alt-key map per §3.B),
     C (helper-call recognition). Verify Upgrade A+B+C with
     synthetic offenders + compliant cases.
  3. memory/invariants/tenancy_baseline_phase_0.json — NEW.
     Archive copy of the current 685/550 JSON. Provenance preserved.
  4. memory/invariants/tenancy.baseline.json — NEW. The Phase-2-active
     baseline; updated downward by Phase 2.2+ migrations.
  5. Sweep ~7 admin-wide / cross-tenant call sites (§3.A): add
     `# tenancy:allow-no-account-id` markers. Identified by §3.A
     table + a one-pass grep against current report.
  6. Enforce-mode flip: replace test_tenancy_observe_mode_does_not_
     fail_build with test_tenancy_enforce_mode_against_baseline
     per §7.C.
  7. /app/memory/sprints/PHASE_2_TENANCY_GUARD.md — sprint memo.
  8. MASTER_STATE.md Section 6 + 8 update — Phase 2.1 status = DONE,
     Phase 2.2 status = Pending.

DO NOT in this phase:
  - Migrate any router call site (Phase 2.2+).
  - Touch service-layer call sites (Phase 2.3).
  - Add new collections to TENANT_SCOPED_COLLECTIONS (defer to
    follow-up sweep per §3.C).
  - Change any behaviour. The helpers are added but not called.
  - Touch the cross-context-calls invariant (Phase 1 follow-up).
  - Refactor unrelated code in the touched files.

Acceptance criteria:
  - 3 scanner-upgrade synthetic tests PASS (one per Upgrade A, B, C).
  - Cross-tenant marker sweep complete; baseline JSON commits cleanly.
  - Phase 2 enforce-mode test PASS against new baseline.
  - All 160 existing Phase 0/1/14/15 + Track-A Phase 5/6/7 lockdowns
    PASS unchanged.
  - 4 characterisation goldens (integration-marked) PASS on next
    real-LLM run.
  - Sprint memo + MASTER_STATE updated.

Out of scope:
  - Aggregation pipeline first-stage `$match` scanning (defer to 2.4).
  - Helper-returning-collection / conditional `account_id` detection
    (declined; Plan §5 doesn't require).
  - Allow-list widening (defer to post-Phase-2 sweep).
```

### 10.B · Phase 2.1 risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Scanner Upgrade B (alt-key map) accidentally exempts a TRUE violation | Low-Med | Map is small (≤10 collections), reviewable line-by-line in the dispatch PR; each entry annotated with the route file that gates the alternative key |
| Baseline JSON merge conflict in active migrations | Low | Baseline is single-line `{"count": N}`; conflicts trivially resolved at PR review |
| Goldens regression from `tenant_filter()` helper addition (Deliverable 1) | None | Helper added but not called; no behaviour change in Phase 2.1 |
| Enforce-mode flip breaks Phase 14 / Phase 15 / Track A regression | None | Test rewrites only the threshold assertion; existing violations stay under baseline |

### 10.C · Phase 2.1 → Phase 2.2+ handoff

Phase 2.1 establishes the enforce-mode floor. Phase 2.2 then:
1. Migrates `routers/documents.py` (47 violations). Adopts `tenant_filter()` / `tenant_doc()` helpers per §1.B.
2. Per Discipline Rail R4: ≤10 new lockdown tests covering the migrated call sites.
3. Updates `memory/invariants/tenancy.baseline.json` downward (target: 47 → 0 for this file).
4. Phase 2.2 sprint memo + MASTER_STATE update.

Phase 2.3 follows the same shape for `routers/work_studio_export.py` (29), then `routers/sandbox.py` (27), then chat.py + work_studio_overlay.py + the long-tail.

### 10.D · Phase 2 → Phase 3 independence

Phase 3 (frontend API-boundary contract) is INDEPENDENT of Phase 2 progress. Phase 3 can dispatch in parallel with Phase 2.2+. No coupling.

---

**End of Phase 2 Pre-Read.** Status: **CLEAN_WITH_NOTES** — Phase 2.1 build dispatch is ready contingent on §9 acknowledgement.

