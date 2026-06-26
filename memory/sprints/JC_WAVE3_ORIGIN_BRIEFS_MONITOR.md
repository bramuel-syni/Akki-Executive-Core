**Canonical Spec**: `/app/memory/DEV_PIPELINE.md` (Journey 3a — Origin-triggered Briefs entered the canonical model via the JC-WS Phase 3 spec revision: brief actions live on the origin surface — Solva / Monitor / Task Manager — not as a Work Studio picker entry. Build each when its module is built.)

# Wave 3 · Origin-triggered Briefs · Monitor (first surface) · CLOSED 2026-06-26 · 9/9 GREEN

## Sub-sprint scope (per user contract)

User direction at AUTONOMOUS BACKLOG RUN (msg 412):
> "Origin-triggered Briefs — surface ordering authority retained. You have authority to pick the first surface based on coverage-gap analysis. Ship the pattern on first surface, then fan out to remaining surfaces in subsequent sub-sprints."

This sub-sprint ships the **pattern**:
1. Backend schema accepts `origin_kind` + `origin_id` on `POST /work-studio/export/{kind}`.
2. Backend persists these on the export row + audit row.
3. Frontend "Brief this" affordance on the chosen origin surface posts the originating-context payload.
4. Pattern is fan-outable — Solva / Task Manager will reuse the same schema in subsequent sub-sprints.

## Coverage-gap analysis → first surface

| Module | Recent activity | Existing brief affordance? | Coverage-gap rank |
|---|---|---|---|
| Solva | Heavy (Bottom Line landed in DOCX/PPTX/XLSX exports per Stage 4.3) | **partial** — narration carries into Work Studio exports | LOW |
| **Monitor** | Heavy (just shipped GP perspectives, Spread-heatmap, Auto-tune candidates) | **NONE** | **HIGHEST** |
| Task Manager | Has its own compile pipeline (board-pack 5 sections) | Different shape (compile ≠ brief) | MEDIUM |

**Conclusion: Monitor / Strategic Goals is the first surface.** Three fresh deliverables that beg for executive briefing (GP perspectives, Spread-heatmap deltas, Auto-tune candidates) and zero existing brief affordances.

## Diff applied

| File | Change |
|---|---|
| `backend/routers/work_studio_export.py` | `ExportRequestIn` accepts `origin_kind` (enum: `monitor_objective` / `monitor_signal` / `solva_session` / `task_manager_task`) + `origin_id` (str, ≤128 chars). Row insertion writes both fields (None when omitted). Audit metadata includes both when present. **Fixed a latent bug along the way**: the existing `write_audit(...target_id=export_id...)` call passed an unknown kwarg → silently failed inside `try/except`. Now uses the canonical positional shape `(context_id, account_id, action, resource_type, resource_id, metadata)`. |
| `frontend/src/components/monitor/StrategicGoalsPanel.jsx` | New `BriefThisGoalButton` rendered inside `GoalDetailDrawer` next to the existing "Update Goal" button (NED users excluded). Synthesises `description / objective / scope` from goal data (title, status, score, probability, target, target_date, rationale). POSTs to existing `/work-studio/export/brief` route with `origin_kind=monitor_objective` + `origin_id=<goal.id>` stamped. Surfaces a sonner toast with an "Open" action that deep-links to the brief artefact in Work Studio (UX kept light for v0; an inline preview drawer is a follow-up). |

## Why the in-drawer button + toast (vs. a redirect to Work Studio)

Per the canonical spec: *"output delivered back AT the origin surface (not in Work Studio)"*. For v0 the click stays in-drawer (no navigation), the brief runs in the background, and the deep link is offered explicitly via the toast action. v1 follow-up: mount an inline preview that pops the brief artefact in a side panel anchored to the GoalDetailDrawer.

## Proving slice 9/9 GREEN

Run: `cd /app/backend && python scripts/jc_wave3_origin_briefs_monitor_slice.py`

| Row | Subject | Outcome |
|---|---|---|
| 1 | `ExportRequestIn` schema accepts `origin_kind` + `origin_id` | ✓ |
| 2 | Schema rejects unknown `origin_kind` values | ✓ |
| 3 | Brief export starts successfully against the live in-proc app | ✓ (status=200 + export_id) |
| 4 | `origin_kind` + `origin_id` persisted on `work_studio_exports` row | ✓ |
| 5 | `origin_kind` + `origin_id` written to `audit_log` row metadata | ✓ (fixes pre-existing silent-failure bug) |
| 6 | Legacy in-Studio flow (no origin fields) — row carries None defaults | ✓ |
| 7 | Monitor FE component uses shared `api` client, no direct axios import | ✓ |
| 8 | FE stamps `origin_kind=monitor_objective` + `origin_id=goal.id` on the payload | ✓ |
| 9 | FE pre-fills payload from goal data (title in description, "Brief the board" in objective) | ✓ |

Runtime: ~4s (thin-input refusal shortcut avoids the 60-second LLM round-trip during slice).

## Fan-out plan (next sub-sprints, when their modules are next worked)

| Origin | Trigger surface | origin_kind | Notes |
|---|---|---|---|
| Solva v2 session detail | next to "Export deck" CTA | `solva_session` | Use session.objective + session.summary as auto-prefill |
| Task Manager task drawer | "Compile" tab → "Brief this task" affordance | `task_manager_task` | Use task.title + readiness intelligence as auto-prefill |
| Monitor signal card | per-card kebab menu → "Brief this signal" | `monitor_signal` | Use signal.headline + recent trend data as auto-prefill |

Same schema, same audit shape. Net-new is purely the FE affordance + module-specific auto-prefill builder.

## Files

- `backend/routers/work_studio_export.py` — schema + persistence + audit (latent bug fixed)
- `frontend/src/components/monitor/StrategicGoalsPanel.jsx` — `BriefThisGoalButton` + drawer insertion
- `backend/scripts/jc_wave3_origin_briefs_monitor_slice.py` — new

— END —
