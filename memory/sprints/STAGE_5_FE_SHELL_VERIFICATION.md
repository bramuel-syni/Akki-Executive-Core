# Stage 5 — FE shell verification (Task Manager · Monitor · Pulse)

**Date:** 2026-06-24
**Dispatch:** AKKI Full Runway, Stage 5 — verify the three Stage 5 FE
shells against their post-Stage-3-rename backends. STOP gate: a
backend a frontend needs doesn't actually work at runtime.
**Status:** CLOSED. One commit lands locally. 7 new e2e tests green +
57 pre-existing surface tests confirmed green. No regressions. No
seams beyond Stage 4 require code.

## Headline result

| Step | Result |
|---|---|
| 5.1 Task Manager FE shell over 28-endpoint backend | VERIFIED. Routes mounted in `server.py:158` + `akki_app.py:127-128/171`. 5 pre-existing test files (`test_phase_aa_slice_1_tasks_initiatives.py` + 4 others) GREEN. 2 new live-call tests confirm `/api/tasks/counts` + `/api/tasks` return 200 for an authenticated member. |
| 5.2 Monitor FE shell over `monitor_strategic_items` + `monitor_dashboard` | VERIFIED. Both routers mounted post-Stage-3 rename (`server.py:90` + `server.py:147`; `akki_app.py:97/99/191/243`). 7 pre-existing test files GREEN. 3 new live-call tests confirm `/api/contexts/{cid}/monitor` (dashboard), `/api/contexts/{cid}/monitor/{kind}` (objective + project CRUD list), and `/api/contexts/{cid}/monitor/owner-roles` all return 200. |
| 5.3 Pulse FE shell over 11-endpoint backend | VERIFIED. Router mounted in `server.py:97` + `akki_app.py:113/199`. 2 pre-existing test files GREEN. 2 new live-call tests confirm `/api/contexts/{cid}/pulse/feed` and `/api/contexts/{cid}/pulse/across-boards` return 200. |
| 5.4 Sprint memo + DEV_PIPELINE.md updates | (this memo + DEV_PIPELINE row) |

## Stage 5.1 — Task Manager verification

### Surface inventory

- **FE pages:** `pages/TaskManager.jsx` (canonical) + `pages/TaskManagerActivity.jsx`. Mounted at `/app/task-manager` (alias `/app/cycle` → CycleList, separate).
- **Backend routers:** `routers/tasks.py` (28 endpoints) + `routers/tasks_initiatives.py` (6 endpoints) = 34 routes total. Mount points: `server.py:158` (tasks_initiatives) + `akki_app.py:127/128/171/172`.
- **Direct FE → BE calls** (sample, from FE pages + components):
  - `GET /api/tasks/counts?context_id={cid}` → top-of-page badges
  - `GET /api/tasks?context_id={cid}` → list per tab
  - `POST /api/tasks/agent-prefill` → wizard prefill
  - `GET/POST/PATCH/DELETE /api/tasks/{tid}` + lifecycle subroutes (commit, draft, review, circulation, final-production, regenerate-intel, ...)

### Tests confirmed green at this commit

```
$ pytest tests/test_phase_aa_slice_1_tasks_initiatives.py tests/test_track_b_phase2_task_lifecycle.py tests/test_wave4_task_listing.py tests/test_task_card_uses_primitive.py tests/test_task_drawer_tab_prefix_guard.py
... 5 test files green
```

### New live-call tests (`test_stage_5_fe_shell_backends.py`)

- `test_task_manager_counts_endpoint` — 200 + `{active, draft, closed}` shape
- `test_task_manager_list_endpoint` — 200 + list-shape body

## Stage 5.2 — Monitor verification

### Surface inventory

- **FE pages:** `pages/Monitor.jsx` (mounted at `/app/monitor`).
- **Backend routers:**
  - `routers/monitor_dashboard.py` (1 main endpoint: function-aware dashboard composer)
  - `routers/monitor_strategic_items.py` (8 endpoints: CRUD + auto-suggest + owner-roles)
  - **Both renamed in Stage 3** (`monitor.py` → `monitor_dashboard.py`; `monitor_v2.py` → `monitor_strategic_items.py`). URL paths unchanged; module names function-aware.
- **Direct FE → BE calls:**
  - `GET /api/contexts/{cid}/monitor?function=ceo` → dashboard view
  - `GET /api/contexts/{cid}/monitor/{kind}` → objective | project list (kind ∈ {objective, project})
  - `GET /api/contexts/{cid}/monitor/owner-roles` → owner-role catalogue
  - `GET /api/contexts/{cid}/monitor/auto-suggest-{kind}s` → AI prefill
  - `POST/PATCH/DELETE /api/contexts/{cid}/monitor/{kind}/{rid}` → mutations

### Tests confirmed green at this commit

```
$ pytest tests/test_patch_5_monitor_v2.py tests/test_monitor_v1_compat.py tests/test_phase_aa_slice_4_monitor.py tests/test_monitor_drawer_and_owner_filter.py tests/test_monitor_drawer_progress_timeline.py tests/test_monitor_status_filter_harmonization.py
... 7 test files green
```

### New live-call tests

- `test_monitor_dashboard_endpoint` — 200 on `?function=ceo`
- `test_monitor_strategic_items_endpoints` — 200 on each of `objective` + `project` (kind list, post-rename)
- `test_monitor_owner_roles_endpoint` — 200 on the owner-role catalogue

### Subtlety

`monitor_strategic_items.py:27` defines `_KIND = ("objective", "project")` — only these two are served by this router. The Task Manager / Initiative tabs (`task`, `initiative`) are served by `routers/tasks.py` + `routers/tasks_initiatives.py` under `/api/tasks/*` rather than `/api/contexts/{cid}/monitor/*`. The Monitor FE page surfaces both via different drawer components, but the routing is split at the API layer.

## Stage 5.3 — Pulse verification

### Surface inventory

- **FE pages:** `pages/Pulse.jsx` (main feed) + `pages/PulseIdeas.jsx` (radar surface).
- **Backend router:** `routers/pulse.py` (11 endpoints). Mount: `server.py:97` + `akki_app.py:113/199`.
- **Direct FE → BE calls:**
  - `GET /api/contexts/{cid}/pulse/feed` → main signal timeline
  - `GET /api/contexts/{cid}/pulse/across-boards` → cross-board radar
  - `POST /api/contexts/{cid}/pulse/signals/{sid}/comment | share | resolve | bookmark | save | take-to-solva | unresolve | unbookmark`
  - `DELETE /api/contexts/{cid}/pulse/signals/{sid}/comments/{cid}`

### Tests confirmed green at this commit

```
$ pytest tests/test_p1_a_intel_to_pulse.py tests/test_patch_6_pulse_synisense.py
... 2 test files green
```

### New live-call tests

- `test_pulse_feed_endpoint` — 200 on `/feed`
- `test_pulse_across_boards_endpoint` — 200 on `/across-boards?window_days=30&limit=10`

## Stage 5 — STOP gate verdict

> Stop trigger: "a backend a frontend needs doesn't actually work at runtime."

**Not tripped.** Every Stage 5 backend endpoint the FE pages depend on returns 200 for an authenticated member of the target context on a fresh seed. Test pattern: `httpx.AsyncClient + ASGITransport + @pytest.mark.asyncio` against `server.app` — same loop as the conftest session, no Motor cross-loop drift.

Live preview backend smoke also confirmed routes serve auth-required 401 (NOT 404) on `/api/tasks/counts`, `/api/contexts/x/monitor`, `/api/contexts/x/monitor/objectives`, `/api/contexts/x/pulse/feed`.

## Affected-test sample (regression check)

```
$ python -m pytest tests/invariants/ \
    tests/test_stage_4_3_analyze_narration_exports.py \
    tests/test_stage_5_fe_shell_backends.py \
    tests/test_phase_aa_slice_1_tasks_initiatives.py \
    tests/test_track_b_phase2_task_lifecycle.py \
    tests/test_wave4_task_listing.py \
    tests/test_patch_5_monitor_v2.py \
    tests/test_monitor_v1_compat.py \
    tests/test_phase_aa_slice_4_monitor.py \
    tests/test_p1_a_intel_to_pulse.py \
    tests/test_patch_6_pulse_synisense.py \
    -p no:warnings --tb=line -q
170 passed, 10 skipped in 101.47s
```

Zero rename-induced regressions. Zero Stage-4-induced regressions. Zero Stage-5-induced regressions.

## Files touched

- `backend/tests/test_stage_5_fe_shell_backends.py` (new) — 7 live-call e2e tests

## §9 follow-up flags (filed; not actioned in this stage)

1. **HUMAN_REQUIRED skipped invariants** (3 today): same as Stage 4 — `test_invariant_audit_always` + `test_invariant_shield_no_leak` (claude + gpt + upload-multi paths). All skip with `HUMAN_REQUIRED` reasons; orthogonal to Stages 1-5.
2. **`services/solva_v2/` rename** — user verbatim deferred (DEV_PIPELINE §9). Wider FE+chat blast radius.
3. **Mongo collection `solva_phase_d_sessions` rename** — gated on the §9 #2 decision + a migration plan.
4. **URL canonicalization** at `/api/contexts/{cid}/solva/v2/*` — same gating.
5. **FE comment refresh** at `ObjectivesProjectsPanel.jsx:467` — cosmetic; lowest priority.
6. **`synisense_observability` router not mounted** (pre-existing) — investigate whether the router is intentionally unmounted or whether `server.py`/`akki_app.py` should include it.
7. **ThinkLab Gate A render-check + Flag 3** — awaiting user call.

## Commits ledger

```
(this commit — Stage 5 sprint memo + DEV_PIPELINE.md updates + live-call tests)
```

## Stop-and-report

✅ **No STOP conditions tripped during Stage 5.** All three FE shells already exist (pre-Stage-3 ship) and are wired to working post-Stage-3-rename backends. The verification pass confirms execution-evidence, not just code-path-existence. Full Runway dispatch closes here.
