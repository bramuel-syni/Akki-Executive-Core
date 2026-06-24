# Stage 3 — Function-Based Renames (Option C)

**Date:** 2026-06-24
**Dispatch:** AKKI Full Runway, Stage 3 — "Canonicalize the two half-migrations" via Option C (rename, not delete) per user direction.
**Status:** CLOSED. 4 commits land locally. 12 invariant tests GREEN. Backend health verified.

## Headline result

| Step | Commit | Result |
|---|---|---|
| 3.1 Inventory pass + STOP-and-surface | `2063f12a` | Identified 4 architectural options for the user to choose between |
| 3.2 Rename `services/solva` → `services/solva_voice_audit` | `7fcdb587` | 24 files moved, ~50 import callsites updated |
| 3.3 Rename `monitor.py` + `monitor_v2.py` → function-based names | `95ae06ba` | 2 files moved, 13 callsites updated |
| 3.4 Build-breaking invariant locking the new names | `f8a91624` | 3 sub-tests; pre-Stage-4 GREEN |

## Naming decisions (capability-based, per user direction)

| Old path | New path | 1-line rationale |
|---|---|---|
| `backend/services/solva/` | `backend/services/solva_voice_audit/` | Captures the two distinctive capabilities vs the parallel `services/solva_v2/` — namely (1) the voice tier with single-voice invariant (`voice/question_bank.py` + `voice/synthesis_renderer.py` + `voice/refusal_voice.py` + `voice/invariants.py`) and (2) the audit-panel timeline endpoint that backs `AuditPanel.jsx` + `AttachDocumentModal.jsx`. |
| `backend/routers/monitor.py` | `backend/routers/monitor_dashboard.py` | This file is the **function-aware dashboard composer**. Single endpoint `GET /contexts/{cid}/monitor` returns the CEO/CFO/COO/Commercial/NED "what to pay attention to" view composed from signals/checklists/reports. Used by `pages/Monitor.jsx:110` for the top dashboard payload. |
| `backend/routers/monitor_v2.py` | `backend/routers/monitor_strategic_items.py` | This file is the **strategic-items CRUD** (objectives/projects/tasks/initiatives + auto-suggest + owner-roles). Entirely different feature from `monitor.py`. The `_v2` suffix was misleading. Used by `ObjectivesProjectsPanel.jsx`. |

## Explicitly out of dispatch scope

| Item | Reason | Filed where |
|---|---|---|
| `backend/services/solva_v2/` rename | User verbatim: "leave the path as-is for now. The name is misleading but the rename has a wider blast radius (4 FE files import from it, plus chat surface, plus export pipeline)." | DEV_PIPELINE.md §9 follow-up |
| Mongo collection `solva_phase_d_sessions` rename | Stored data identifier, not a code path. Requires migration if renamed. | DEV_PIPELINE.md §9 follow-up |
| Routes at `/api/contexts/{cid}/solva/v2/*` URL canonicalization | FE backward-compat. URL renames break the published client. | DEV_PIPELINE.md §9 follow-up |
| FE comment fixup at `ObjectivesProjectsPanel.jsx:467` (references the old backend file name in a code comment, not an import) | Cosmetic; no functional impact. | DEV_PIPELINE.md §9 follow-up |

## Step 3.2 — Solva rename evidence

```
$ git mv backend/services/solva backend/services/solva_voice_audit
$ # sed pass on all backend/ .py files:
$ find backend -name '*.py' -not -path '*/__pycache__/*' -print0 | xargs -0 sed -i \
    -e 's|from services\.solva import|from services.solva_voice_audit import|g' \
    -e 's|from services\.solva\.|from services.solva_voice_audit.|g' \
    -e 's|import services\.solva\b|import services.solva_voice_audit|g'
$ grep -rn 'from services.solva import\|from services.solva\.' backend/  # POST: empty
```

24 files renamed via `git mv`. 50+ import callsites updated across:
- `backend/routers/solva_phase_d.py` (8 top-level imports + several inline imports)
- `backend/routers/solva_telemetry_admin.py` (1)
- `backend/routers/chat.py` (1, line 750 — `record_handoff` inline import)
- `backend/tests/test_phase_d_solva_pipeline.py` (~20 imports)
- `backend/tests/test_phase_d_audit_correction.py`, `test_phase_d_fix_bundle.py`, `test_phase_e_polish.py`, `test_solva_v2_identity_audit.py`, `test_invariant_cross_context_calls.py`

Backend restarted cleanly post-rename — `Application startup complete` in supervisor logs. Curl `/api/health` returned HTTP 200.

## Step 3.3 — Monitor renames evidence

```
$ git mv backend/routers/monitor.py backend/routers/monitor_dashboard.py
$ git mv backend/routers/monitor_v2.py backend/routers/monitor_strategic_items.py
$ # sed pass updated:
$ #   from routers import monitor as <X>           ->  from routers import monitor_dashboard as <X>
$ #   from routers import monitor_v2 as <X>        ->  from routers import monitor_strategic_items as <X>
$ #   from routers.monitor_v2 import <X>           ->  from routers.monitor_strategic_items import <X>
$ # Plus variable-name updates in akki_app.py + server.py for consistency.
```

13 callsites updated: 4 in `akki_app.py` (L97/99/191/243), 2 in `server.py` (L90/147), 4 in `test_aa_followup_5_owner_role_retrofit.py`, 1 in `test_j4_stage_6_backend.py`, 1 in `test_phase_p5_14_2_compact_landings.py`, plus internal variable-name updates for consistency.

## Step 3.4 — Build-breaking invariant evidence

`backend/tests/invariants/test_no_legacy_solva_monitor_names.py`:

```python
LEGACY_IMPORTS_RE = re.compile(
    r"^\s*(?:"
    r"from\s+services\.solva\b(?!_)"          # bare `solva`
    r"|from\s+services\.solva\."
    r"|import\s+services\.solva\b(?!_)"
    r"|from\s+routers\s+import\s+monitor\s+as\b"  # bare monitor
    r"|from\s+routers\s+import\s+monitor_v2\b"
    r"|from\s+routers\.monitor\s+import\b"
    r"|from\s+routers\.monitor_v2\b"
    r")"
)

GRANDFATHERED_V_SUFFIX_STEMS = frozenset({
    "solva_v2",  # out of dispatch scope per user verbatim direction
})
```

Three sub-tests:
1. `test_no_legacy_solva_monitor_imports` — scans `backend/` for legacy import strings; fails on any hit.
2. `test_no_new_v_suffixes_under_solva_or_monitor` — scans `services/solva*` + `routers/monitor*` trees for `_vN` suffixed paths; fails on any hit except `solva_v2`.
3. `test_canonical_paths_exist` — smoke check that the renamed paths exist.

Results:
```
pytest backend/tests/invariants/test_no_legacy_solva_monitor_names.py -v
test_no_legacy_solva_monitor_imports                  PASSED
test_no_new_v_suffixes_under_solva_or_monitor         PASSED
test_canonical_paths_exist                            PASSED
3 passed in 1.5s

pytest backend/tests/invariants/ -v                   # all 4 invariant groups
12 passed in 9.69s
```

## Affected-test sample (regression check)

```
$ pytest tests/test_phase_d_solva_pipeline.py tests/test_phase_d_audit_correction.py \
         tests/test_phase_d_fix_bundle.py tests/test_phase_e_polish.py \
         tests/test_solva_v2_identity_audit.py tests/test_aa_followup_5_owner_role_retrofit.py \
         tests/test_j4_stage_6_backend.py tests/test_phase_p5_14_2_compact_landings.py \
         tests/invariants/test_invariant_cross_context_calls.py
7 failed, 110 passed, 21 warnings in 215.39s
```

**All 7 failures are pre-existing and unrelated to the rename:**

| Test | Failure mode | Cause |
|---|---|---|
| `test_phase_d_solva_pipeline.py::test_full_session_round_trip_audit_ids_grow` | `httpcore.ReadTimeout` | Synisense HTTP unreachable from this pod (env) |
| `test_phase_d_solva_pipeline.py::test_session_get_returns_next_question_when_resumed` | `httpcore.ReadTimeout` | Same |
| `test_phase_d_fix_bundle.py::test_refusal_gate_fires_on_persistently_thin_evidence` | `httpcore.ReadTimeout` | Same |
| `test_phase_d_fix_bundle.py::test_single_voice_synthesis_no_far_vocabulary_well_framed` | `httpcore.ReadTimeout` | Same |
| `test_phase_d_fix_bundle.py::test_single_voice_refusal_rendering_no_far_vocabulary` | `httpcore.ReadTimeout` | Same |
| `test_phase_d_fix_bundle.py::test_far_refusal_reachable_with_substantive_but_thin_inputs` | `httpcore.ReadTimeout` | Same |
| `test_phase_e_polish.py::test_phase_e_routers_registered` | Asserts `/api/admin/synisense/observability` mounted | Router file exists at `routers/synisense_observability.py` but is NOT include()d in `server.py` or `akki_app.py`. Pre-existing; orthogonal to Stage 3. |

Zero rename-induced regressions.

## FE verification

```
$ grep -rn 'routers/monitor\|routers.monitor\|services.solva\|services/solva' \
    frontend/src | grep -v 'solva_v2'
frontend/src/components/monitor/ObjectivesProjectsPanel.jsx:467: \
    // Mirrors the backend `CANONICAL_OWNER_ROLES` in `routers/monitor_v2.py`.
```

ONE comment reference (not an import). FE clients call URLs, not Python module names, so this comment is cosmetic. Filed in §9 follow-up to refresh the reference text.

## Mongo data note

The `solva_phase_d_sessions` Mongo collection name is UNCHANGED. The rename was code-paths-only. Live tenant data is unaffected. If a future dispatch renames the collection (e.g. `solva_voice_audit_sessions`), it will need:
1. A migration script that reads from the old name, writes to the new.
2. A backward-compat read shim during cutover.
3. Production rollout window.

Not in scope for this dispatch.

## Commits ledger

```
f8a91624 ci(Stage 3): build-breaking invariant blocking legacy solva/monitor names
95ae06ba chore(Stage 3): rename monitor.py/monitor_v2.py to function-based names
7fcdb587 chore(Stage 3): rename services/solva to services/solva_voice_audit (function-based)
2063f12a audit(Stage 3.1): canonicalization inventory + STOP
```

(Plus this memo + DEV_PIPELINE.md updates → final Stage 3 commit.)

## §9 follow-up flags (filed but not actioned in this stage)

1. **`services/solva_v2/` rename** — user explicit punt; revisit when blast radius is mapped (FE clients + chat + export pipeline imports).
2. **Mongo collection `solva_phase_d_sessions` rename** — gated on the §9 #1 decision + a migration plan.
3. **URL canonicalization** at `/api/contexts/{cid}/solva/v2/*` — same gating.
4. **FE comment refresh** at `ObjectivesProjectsPanel.jsx:467` — cosmetic; lowest priority.
5. **`synisense_observability` router not mounted** (pre-existing, surfaced by `test_phase_e_routers_registered`) — investigate whether the router is intentionally unmounted or whether `server.py`/`akki_app.py` should include it.

## Stop-and-report

✅ **No STOP conditions tripped during Stage 3.2/3.3/3.4.** Stage 3.1 STOPPED-and-surfaced; user resolved via Option C; rest of Stage 3 executed cleanly. Stage 4 (Work Studio) starts next, per dispatch's no-pause discipline.
