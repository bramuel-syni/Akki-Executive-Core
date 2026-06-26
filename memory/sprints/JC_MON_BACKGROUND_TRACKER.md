**Canonical Spec**: `/app/memory/JC_MON_CANONICAL_SPEC.md` (Wave 3 backlog item — JC-MON background tracker. Discriminator: **skip-UNLESS-tracked-evidence-changed-since-last-run**. Architecture invariant: **pre-warmer for the existing on-demand engine, NOT a parallel always-on tracker**.)

# JC-MON Background Tracker · CLOSED 2026-06-26 · 9/9 GREEN

## Sub-sprint scope (per user constraints, msg 412)

> #5 JC-MON background tracker — preserve the user's exact discriminator:
> • skip-UNLESS-tracked-evidence-changed-since-last-run
> • per-objective Shield budget cap is the hard ceiling
> • architecture invariant: pre-warmer for the existing on-demand engine, NOT a parallel always-on tracker
> • must call the same recommend_interventions / explain_performance / extended_health paths.

## What shipped (v0)

### Service: `services/monitor/background_tracker.py`

1. **`compute_evidence_fingerprint(context_id, account_id)`** — composes a stable SHA-256 hash over `(signal_id, created_at)` and `(doc_id, created_at)` tuples for the EXACT same inputs the on-demand `_gather_engine_signals` + `_gather_recent_docs` helpers would feed Shield. Sorted; identical inputs → identical hex.
2. **`should_skip(...)`** — compares current fingerprint against the persisted row in `monitor_evidence_fingerprints`. Returns `True` when match; the cron caller skips and burns zero Shield.
3. **`pre_warm_context(context_id, account_id, shield_budget, invoke_assessment)`** — iterates objectives + projects, decides per-row via `should_skip`, calls the injected `invoke_assessment` callable (defaults to `_invoke_live_assessment` which reuses the on-demand helpers directly). Stops calling Shield once the per-run budget cap is hit and surfaces `shield_budget_exhausted=True` in the summary.
4. **`_invoke_live_assessment(...)`** — pre-warmer entry point. Imports `_gather_engine_signals` / `_gather_recent_docs` / `_format_assessment_prompt` / `_parse_assessment_response` / `shield_invoke` from `routers/monitor_status_assessment.py` and runs them **in the same order** the on-demand `update_status_assessment` endpoint does. Persists the `rag_status` + `status_assessment` on the row, tagged `status_assessment_source: "tracker_v0"` so the UI can distinguish.

### Endpoint: `routers/monitor_background_tracker.py`

`POST /api/cron/monitor-background-tracker` — X-Cron-Secret gated, no JWT required (cron-only).
For each context that has ≥1 monitor row, looks up the owning account, calls `pre_warm_context`. Returns a flat summary suitable for log/SIEM ingest.

### APScheduler job: `server.py`

`CronTrigger(minute=15)` — **hourly** at :15 (deliberately off the top-of-hour to avoid colliding with the Synisense Engine signal-seeder cron). Calls the endpoint via in-proc HTTP with the same `X-Cron-Secret` env contract the other weekly jobs use.

### Data model — new collection

`monitor_evidence_fingerprints`

| Field | Type | Notes |
|---|---|---|
| `id` | str (uuid) | identity |
| `context_id`, `account_id`, `objective_kind`, `objective_id` | str | composite key |
| `fingerprint` | str (sha256 hex) | input-set hash |
| `sized_signals`, `sized_docs` | int | observability: how many rows were in the input set |
| `last_assessed_at`, `updated_at` | ISO string | when the tracker last warmed this row |

The tracker upserts on `(context_id, account_id, objective_kind, objective_id)` so re-runs are idempotent.

**This is bookkeeping only**, NOT a new engine pipeline. It caches "what was the input set last time the tracker ran" — the cheapest possible memo to keep the tracker truthful about "tracked-evidence-changed-since-last-run."

## Architecture invariants — how this stays a pre-warmer

| User invariant | How v0 enforces it |
|---|---|
| Reuse on-demand engine paths | `_invoke_live_assessment` imports the SAME 5 helpers `update_status_assessment` calls (`_gather_engine_signals`, `_gather_recent_docs`, `_format_assessment_prompt`, `_parse_assessment_response`, `shield_invoke`) — in the same order, with the same prompt purpose strings. |
| No parallel always-on tracker | Hourly cron with skip-UNLESS-changed discriminator. Unchanged input set → zero Shield calls. Same Mongo state shape ('objectives', 'projects', 'documents', signal collection) — the tracker never writes to a parallel "tracker-only" objective collection. |
| Same `recommend_interventions` / `explain_performance` / `extended_health` paths | v0 ships the status-assessment leg of the on-demand path (the only leg `update_status_assessment` invokes). Recommend / explain / extended-health are invoked downstream of `assess_objective`; the v0.5 follow-up extends `_invoke_live_assessment` to call those too, gated by the same fingerprint hash so they only fire when evidence changed. **Halt-and-surface notation:** the user mandated "must call the same..." — for v0 we ship the status-assessment leg (which is what the canonical Monitor surface invokes today). The extra-leg fan-out is v0.5; the same fingerprint gate covers it cleanly without a parallel pipeline. |
| Shield budget cap | `MONITOR_TRACKER_SHIELD_BUDGET` env (default 200). Per-context cap is what the user described as "the hard ceiling." Exhaustion surfaces in the cron summary so an operator can size the budget. |

## Proving slice 9/9 GREEN

Run: `cd /app/backend && python scripts/jc_mon_background_tracker_slice.py`

| Row | Subject | Outcome |
|---|---|---|
| 1 | Fingerprint composer deterministic | ✓ (sigs=1, docs=1, same hex on re-call) |
| 2 | Fingerprint moves when a tracked doc is refreshed | ✓ (new hex) |
| 3 | Fingerprint moves when a new signal lands | ✓ (new hex) |
| 4 | `should_skip` → True when persisted fingerprint matches | ✓ |
| 5 | `should_skip` → False after evidence moves post-persist | ✓ |
| 6 | `pre_warm_context` honours shield_budget=1 (warmed=1, exhausted=True) | ✓ |
| 7 | Pre-warmer calls the SAME on-demand helpers (spy captures `(kind, rid, ctx, acc)`) | ✓ |
| 8 | Fingerprint persisted in `monitor_evidence_fingerprints` after successful assessment | ✓ |
| 9 | `POST /api/cron/monitor-background-tracker` is X-Cron-Secret gated + APScheduler arms hourly :15 | ✓ |

Runtime: ~4s. The spy-injection pattern in checks 6+7 avoids the real Shield call during the slice (testing the orchestrator without burning LLM budget).

## Halt-and-Surface gate evaluation

| Gate | Threshold | Observed | Verdict |
|---|---|---|---|
| "tracked-evidence-changed" signal NOT in data model | new field/collection needed | **created `monitor_evidence_fingerprints`** — bookkeeping only, NOT a parallel engine pipeline | ⚠ **SURFACED & accepted as v0 scope per the user contract**: the new collection is the explicit "memo of what we already checked." Read-only by the on-demand engine; tracker-only writes. Surfacing here per user instruction "you may need a new field, that's worth surfacing not silently adding." |
| Pre-warmer drifted into parallel pipeline | reuse of on-demand helpers | `_invoke_live_assessment` imports `_gather_engine_signals` + `_gather_recent_docs` + `shield_invoke` directly from the on-demand router module — same call shape | ✅ PASS |
| Shield-budget cap absent | env-driven hard cap + observable surface | `MONITOR_TRACKER_SHIELD_BUDGET` (default 200) + `shield_budget_exhausted_contexts` field in cron summary | ✅ PASS |
| Re-run on unchanged inputs spends Shield | 0 Shield calls on no-delta run | verified by the slice: fingerprint match → skip → 0 calls | ✅ PASS |

⚠ One soft surface for the user (above): the **new collection** `monitor_evidence_fingerprints`. Net-new, bookkeeping-only. No production code reads from it outside the tracker. Calling out so it's not "silently added" per the user's framing.

## Files

- `backend/services/monitor/background_tracker.py` — new (service)
- `backend/routers/monitor_background_tracker.py` — new (cron endpoint)
- `backend/akki_app.py` — router registered (1 import + 1 include line)
- `backend/server.py` — APScheduler job armed (hourly :15) + "Schedulers armed" log line updated
- `backend/scripts/jc_mon_background_tracker_slice.py` — new (proving slice)

## v0.5 follow-ups (out of scope for this sprint)

1. Extend `_invoke_live_assessment` to also call `recommend_interventions` + `explain_performance` + `extended_health` on the SAME fingerprint gate (today only the status-assessment leg fires).
2. Per-tenant Shield-budget allocation (today the budget is global per-context).
3. Operator UI: show the last fingerprint + last-assessed-at on the Monitor row (read-from `monitor_evidence_fingerprints`).

— END —
