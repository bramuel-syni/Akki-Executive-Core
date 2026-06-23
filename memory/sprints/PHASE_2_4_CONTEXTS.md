# Phase 2.4 — `contexts` Context Migration (Hybrid)

**Dispatch:** Re-Architecture Phase 2.4 Build (Tenancy Guard — fourth-context migration via hybrid approach).
**Pre-Read source:** `/app/memory/sprints/PHASE_2_4_PRE_READ.md` §8 — orchestrator-approved hybrid (C-primary + B-supporting + A-targeted).
**Mode:** Per Discipline Rail R4 — one sub-phase in flight (Phase 2.4).
**Date:** 2026-06-22.
**Status:** **DONE. CLEAN — zero new failures attributable to Phase 2.4.**

---

## 1 · Goal

Migrate the `contexts` collection via the hybrid approach approved in Pre-Read §8: **Scanner Upgrade D (helper-fusion AST tracer)** auto-resolves sites where a recognised tenant-gate helper was invoked upstream + **helper-body exemption** for the two helper implementations themselves + **inline markers with rationale** for the remaining patterns (membership-derived id, admin/cron probes, worker closures, public/token-gated paths, etc.).

NO behaviour change. Phase 0 + Phase 1 + Phase 14 + Phase 15 + Phase 2.1 + Phase 2.2 + Phase 2.3 + Track A 5/6/7 goldens are the gate.

---

## 2 · Files (line counts)

| Path | Lines | Status |
|---|---:|---|
| `backend/tests/invariants/test_invariant_tenancy.py` | **1296** | UPDATE — Scanner Upgrade D (~170 LOC: `TENANT_GATE_HELPERS` per-collection map + `_CONTEXT_HELPER_FUNCTIONS` exemption set + 4 helper functions + scanner-loop integration) + `_ENFORCE_MODE_COLLECTIONS` widened to 4 |
| `memory/invariants/tenancy_violations.json` | (update) | Live report post Phase 2.4 (135 total / 115 definite / 20 non-literal) |
| `memory/sprints/PHASE_2_4_CONTEXTS.md` | (this file) | NEW |
| `memory/MASTER_STATE.md` | (mod) | Sections 6 + 7 + 8 + 9 update |
| **30 router/service files modified** | (mod) | 61 markers across 30 files — see §4 |

### 2.A · Modified router/service files (30)

`account_deletion.py`, `active_context.py`, `admin_sandbox_kpi.py`, `admin_tenants.py`, `auth.py`, `chat.py`, `contexts.py`, `cycle.py`, `daily_review.py`, `depth.py`, `documents_async_mirror.py`, `first_session.py`, `governance.py`, `inbound_email.py`, `inbound_queue.py`, `influence_map.py`, `learn.py`, `ned_cycle.py`, `portfolio.py`, `portfolio_data.py`, `sandbox.py`, `search.py`, `shares.py`, `solva_v2.py`, `solva_v2_artefact.py`, `studio.py`, `trust_center.py`, `walkin.py`, `work_studio_export.py`, `services/inbox_routing/context_resolver.py`.

---

## 3 · Scanner delta (before / after Phase 2.4)

| Metric | Phase 2.3 close | Post Phase 2.4 | Delta this phase |
|---|---:|---:|---:|
| Total violations | 230 | **135** | **−95 (−41%)** |
| Definite (literal) | 206 | **115** | **−91 (−44%)** |
| Non-literal | 24 | **20** | **−4 (−17%)** |
| `contexts` violations | 71 | **0** | **−71 (−100%)** ✅ |
| `chats` (enforce mode preserved) | 0 | **0** | unchanged ✅ |
| `documents` (enforce mode preserved) | 0 | **0** | unchanged ✅ |
| `work_studio_exports` (enforce mode preserved) | 0 | **0** | unchanged ✅ |

**Per-cause breakdown of the 71 → 0 reduction:**

| Source | Sites resolved |
|---|---:|
| **Scanner Upgrade D — helper-fusion (Depends + direct-call detection)** | **10** |
| **Helper-body exemption** (`_verify_ned_context` body — the `_dep` body lives in `core.py` which is outside SCAN_ROOTS so was never flagged) | **— (subsumed in helper-fusion count above as L174 was originally counted)** |
| **Markers with inline rationale** | **61** |
| **Total** | **71** |

**Cumulative scanner reduction from Phase-0 baseline through Phase 2.4:**

| Metric | Phase-0 baseline (immutable) | Phase 2.4 close | Cumulative delta |
|---|---:|---:|---:|
| Total | 685 | **135** | **−550 (−80%)** |
| Definite | 550 | **115** | **−435 (−79%)** |
| Non-literal | 135 | **20** | **−115 (−85%)** |

---

## 4 · Migrated context: `contexts`

### 4.A · Scanner Upgrade D — Helper-fusion AST tracer

New scanner extension at `backend/tests/invariants/test_invariant_tenancy.py`:

```python
TENANT_GATE_HELPERS: Dict[str, FrozenSet[str]] = {
    "contexts": frozenset({"require_context_membership", "_verify_ned_context"}),
}

_CONTEXT_HELPER_FUNCTIONS: FrozenSet[str] = frozenset({
    "_dep",                  # inner closure of require_context_membership()
    "_verify_ned_context",   # NED-specific helper
})

def _tenancy_satisfied_by_helper_fusion(tree, call_node, collection) -> bool:
    """Returns True iff (a) the enclosing function IS a recognised helper
    body OR (b) a recognised tenant-gate helper was injected via FastAPI
    Depends(...) on the function signature OR (c) a recognised helper was
    invoked earlier in the function body before the call line."""
    ...
```

Detection patterns:
1. **FastAPI Depends injection:** `def handler(..., ctx: Dict = Depends(require_context_membership(owner_only=True)))` — the dependency runs before the function body, so any subsequent `db.contexts.{find,find_one,update_one,delete_one,replace_one}(…)` is gated.
2. **Direct helper call:** `await _verify_ned_context(account_id, body.context_id)` immediately followed by `await db.contexts.find_one({"id": body.context_id})` — explicit gate.
3. **Helper-body self-reference:** the `_verify_ned_context` function's own `db.contexts.find_one(...)` at `ned_cycle.py:174` — exempt because this IS the contract, not a consumer.

**Auto-resolves:** 10 sites (contexts.py L233, L300, L302; committees.py L45 + 7 others discovered during scan).

### 4.B · Helper-body exemption

The exemption set is hard-coded to 2 function names per orchestrator §"Approvals" §2 design ack:

```python
_CONTEXT_HELPER_FUNCTIONS: FrozenSet[str] = frozenset({"_dep", "_verify_ned_context"})
```

`core.py` is outside SCAN_ROOTS (`backend/services` + `backend/routers`), so `_dep` is never scanned — the exemption is forward-compatible if core.py is ever moved/scanned.

### 4.C · Markers (61 sites across 30 files)

All carry inline rationale per Discipline Rail R5 (Honesty Protocol). Grouped by category (matching Pre-Read §1.B patterns):

| Category | # sites | Files | Rationale theme |
|---|---:|---|---|
| **A. Membership-derived `id` lookups** | 12 | auth, active_context, daily_review, governance, inbound_queue, ned_cycle, portfolio (×2), search, shares, influence_map | `context_ids` came from `db.memberships.find({account_id: caller})` upstream; the set IS the caller's own contexts by construction |
| **B. Sandbox/seeded owner-gated paths** | 12 (incl. 2 cron) | sandbox.py | `ctx` loaded with `{owner_account_id: current["id"], type: sandbox}` upstream; matching write paths. Plus 2 cron sweeps (cleanup_expired_sandboxes) gated by X-Cron-Secret. |
| **C. Admin (super-admin route gate)** | 5 | admin_sandbox_kpi, admin_tenants | Super-admin gate enforced by route dependency at file entry |
| **D. Public/share/token-gated** | 7 | trust_center, studio, solva_v2_artefact | Token-resolved `cid` or session-gated paths; tenant scope established at token validation |
| **E. Worker closures** | 4 | solva_v2 (`_run_grounding`), work_studio_export (`_run_export`, `_run_enhance`), chat.py (`_event_gen` in `stream_message`) | `context_id` captured via closure from an upstream-gated handler |
| **F. Single-account handler-gated lookups** | 12 | contexts.py (invitation), learn, walkin, depth, documents_async_mirror, first_session (×3), cycle (×2), portfolio_data | Handler is gated by `Depends(get_current_account)`; `context_id` flows from validated request |
| **G. Inbound email (mailbox-routed)** | 6 | inbound_email (×4), inbox_routing/context_resolver (×2) | Routing is by unique mailbox address on the context row; no caller identity to scope by |
| **H. Account deletion cascade** | 1 | account_deletion | `owned_ctx_ids` IS the deleting user's owner_account_id-stamped contexts (computed upstream) |
| **I. Active context resolver (post-find membership)** | 2 | active_context (×2) | Ctx fetched by id THEN membership verified before commit; explicit post-find gate |
| **Total** | **61** | 30 files | |

### 4.D · Per-collection enforce flip

```python
# tests/invariants/test_invariant_tenancy.py (post Phase 2.4)
_ENFORCE_MODE_COLLECTIONS: FrozenSet[str] = frozenset(
    {"chats", "documents", "work_studio_exports", "contexts"}
)
```

`test_tenancy_enforce_mode_for_migrated_collections` is now build-breaking on any new `chats` OR `documents` OR `work_studio_exports` OR `contexts` definite violation.

**Phase 2.5+ candidates (residual top-10 after Phase 2.4):**

| Collection | Hits | Notes |
|---|---:|---|
| inbound_queue | 19 | routers/inbound_email.py — single file (high concentration) |
| tasks | 15 | tasks/tasks_initiatives — distributed |
| chat_messages | 12 | chat.py + adjacents — extension of the chats migration |
| user_calendar_credentials | 11 | oauth_google.py — single file |
| signals | 10 | sandbox, pulse |
| cycles | 10 | cycles.py, cycle.py |
| solva_v2_sessions | 10 | solva_v2.py — Solva-context-owned |
| cycle_assignments | 9 | cycle_assignments.py |
| studio_blocks | 9 | studio_blocks.py |
| exco_teams | 8 | exco_teams.py |

**Recommended Phase 2.5:** `inbound_queue` (19 hits, single file, single-purpose, full Phase 14 lockdown coverage) — same migration shape as Phase 2.3 (`work_studio_exports`).

---

## 5 · Test results

| Suite | Result | Notes |
|---|---|---|
| `tests/invariants/` (all) | **33/33 PASS, 4 SKIP** | 4 skips = deliberate-violation env-gated smokes (unchanged) |
| `tests/test_chat_fluency_no_shield_leak.py` (Phase 14) | **PASS** | Preserved |
| `tests/test_docs_download.py` (Phase 15) | **PASS** | Preserved |
| `tests/test_track_a_phase5_lifecycle.py` | **PASS** | Preserved |
| `tests/test_track_a_phase6_inline_edit_and_bc_removal.py` | **PASS** | Preserved |
| `tests/test_track_a_phase7_confidence_scoring.py` | **PASS** | Preserved |
| Targeted contexts/auth/sandbox/inbound/share/portfolio sweep (17 suites) | **105 PASS, 72 SKIP, 0 FAIL** | All 72 skips are pre-quarantined (Patch 8/19 quarantines for env-config issues); zero attributable failures. |

**Aggregate Phase 2.4 lockdown: 73 deterministic PASS** (invariants 33 + Phase 14/15 6 + Track A 5/6/7 34 → 73). Targeted regression: 105 PASS, 0 new failures.

**Pre-existing failures pool (unchanged from Phase 2.3 §8.C — 11 items logged but none in Phase 2.4's footprint).**

**Backend smoke:** `GET /api/ → HTTP 200`. Hot reload picked up changes; service healthy.

**No new failures attributable to Phase 2.4.** ✅ Acceptance criterion met.

---

## 6 · Discipline rails — what was honoured

| Rail | How Phase 2.4 honoured it |
|---|---|
| R1 (Pre-Read) | `/app/memory/sprints/PHASE_2_4_PRE_READ.md` CLEAN_WITH_NOTES; orchestrator approved hybrid + design ack |
| R2 (Pre-Read for each dispatch) | This memo IS the Phase 2.4-specific Post-Read |
| R3 (one-shot dispatch) | Single dispatch — strict sub-step sequence followed |
| R4 (≤10 lockdown tests per phase) | **Zero new test files**. Scanner Upgrade D is exercised by the existing tenancy invariant + the per-collection enforce test (already in place). Existing 15-test suite covers Phase 2.4. Under budget. |
| R5 (Honesty Protocol) | Every marker carries inline rationale; helper-fusion auto-resolves are visible in the live tenancy_violations.json (no silent suppression) |
| R6 (no unrequested cleanups) | Only `contexts`-collection violations addressed. No adjacent low-risk wins bundled (none qualified). No touching of other Phase 2.X candidates. |
| R7 (lockdown sweep before close) | Full invariant + Phase 14/15 + Track A 5/6/7 + 105-test targeted contexts/auth/sandbox sweep — passing |

---

## 7 · Deviations from dispatch

**Three mid-flight observations, none breaking acceptance:**

### 7.1 · Marker-script bug (line shift) — caught and fixed within the dispatch

Initial marker-script applied 59 markers in source order; each `lines.insert()` shifted subsequent line numbers down by 1, causing markers below the first insertion in a file to land 1-2 lines higher than the call. Scanner only sees markers on the call line OR the line directly above. **Caught:** post-marker re-scan revealed 31 residual violations (instead of 0). **Fix:** reverted all 30 modified files via `git checkout`, re-applied the markers in BOTTOM-UP order per-file (line numbers desc), preserving Phase 2.1/2.2/2.3 work intact via the targeted checkout list. Second pass: 61 markers cleanly placed, 0 residuals.

### 7.2 · Hybrid component count variance — within tolerance

Pre-Read §8 projected the hybrid split as ~50 markers + ~18 helper-fusion auto-resolves + ~3 helper-body exemptions = 71 total.

Actual:
- Helper-fusion auto-resolves: **10** (vs projected 18; -44% variance)
- Markers: **61** (vs projected 50; +22% variance)
- Helper-body exemption: **subsumed** (the `_verify_ned_context` exemption auto-resolved as part of helper-fusion at L174; `_dep` is outside scan roots)

Variance origin: the 20-sample stratified pick over-represented the "P1 + P2 helper-fusion candidate" pattern (5/20 = 25%) relative to the actual codebase distribution (10/71 = 14%). Per dispatch §"Escalation triggers — RECALIBRATED": **"Margin-of-error variance, naming nuances, slight cost overruns, and additional pattern variants within the hybrid's reach are NOT escalation-worthy. Solve and document."** Variance well within hybrid's reach; documented; no escalation.

### 7.3 · `_dep` is outside SCAN_ROOTS

The Pre-Read §7 design ack noted that `_dep` (the inner closure of `require_context_membership`) lives in `core.py`, which is at `/app/backend/core.py` — NOT under `SCAN_ROOTS = (/app/backend/services, /app/backend/routers)`. Therefore `_dep` was never flagged by the scanner pre-Phase-2.4, and the helper-body exemption never fires for it in practice. The exemption is forward-compatible (if core.py is ever moved/scanned) but currently inert for `_dep`. The exemption is live and effective for `_verify_ned_context` at `ned_cycle.py:174`. Documented as design transparency, not a deviation.

---

## 8 · Follow-ups (logged for Phase 2.5+)

### 8.A · Recommended next dispatch: **Phase 2.5 — `inbound_queue` (19 hits, single file)**

Same dispatch shape as Phase 2.3 — single context, single-purpose router file (`routers/inbound_email.py`), full Phase 14 chat-fluency adjacency coverage, behaviour-preserving, baseline-shrink-only enforce flip. Estimated effort: similar to Phase 2.3 (1 dispatch, ≤20 marker/defensive-add additions).

### 8.B · Pre-existing failures pool (unchanged from Phase 2.3 §8.C)

11 items tracked for maintenance backlog — none in Phase 2.4's footprint.

### 8.C · Top-line callout for MASTER_STATE Section 9 (updated)

> Phase 2 cumulative posture (through Phase 2.4): **four collections (`chats`, `documents`, `work_studio_exports`, `contexts`) under per-collection enforce mode** + Scanner Upgrades A/B/C/A.1/A.2/D + `task_id` widening + helper-body exemption set live. **Total tenancy violations down 80% (685→135); definite down 79% (550→115).** Zero production cross-tenant bugs introduced; zero behaviour changes. Pattern proven across four contexts via three migration techniques (defensive add, marker-with-rationale, helper-fusion AST tracer). Phase 2.5 (`inbound_queue` recommended) follows the proven shape.

---

**End of Phase 2.4 sprint memo.**
