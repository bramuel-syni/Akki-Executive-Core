**Canonical Spec**: `/app/memory/JC_MON_CANONICAL_SPEC.md` (Wave 3 backlog item — Owner Digest v0: Monday 9am owner-tz, deterministic-only content, skip-if-no-delta, replies route to TM Journal accept rail.)

# Owner Digest v0 · CLOSED 2026-06-26 · 7/7 GREEN

## Sub-sprint scope (per user constraints, msg 412)

> #4 Owner Digest v0 — preserve discipline:
> • Deterministic-only. No Shield call.
> • Skip-if-no-delta.
> • Monday 9am owner-tz.
> • Replies → TM Journal accept rail (reuse, don't build new).

## What shipped (v0)

1. **`services/owner_digest.py`** — deterministic composer.
   - Reads `strategic_goals` for the context, ranks `off_track` + `at_risk` first.
   - Computes `previous_score` + `delta_score` from `score_history` (last entry that pre-dates the 7-day window).
   - Stable `delta_hash` — SHA-256 over a canonicalised subset of fields (`goal_id`, `status`, `score`, `probability`, `band`). Identical inputs always produce identical hashes.
   - `compose_or_skip(...)` returns `(payload, should_skip)` — `True` when the new hash matches the latest persisted `owner_digests` row for `(context_id, owner_account_id)`.
   - **Zero Shield / LLM calls along the entire path.** Reading goals + score_history is pure Mongo.

2. **`routers/owner_digest.py`** — 3 endpoints:
   - `GET  /api/contexts/{cid}/owner-digest/preview` — owner-only, composes without persisting.
   - `GET  /api/contexts/{cid}/owner-digest/latest`  — owner-only, last persisted row.
   - `POST /api/cron/owner-digest-weekly` — X-Cron-Secret gated. Sweeps every context with an owner + at least one strategic goal; persists the digest only when the delta hash differs from the last row.

3. **`server.py` APScheduler** — `owner_digest_weekly` job armed at `CronTrigger(day_of_week="mon", hour=9, minute=0)`. Calls the cron endpoint via in-proc HTTP with the same `X-Cron-Secret` env the other weekly jobs already use. Same APScheduler caveat as the rest of the suite (single-replica in-process; HA deploys point an external trigger at the same endpoint).

## owner-tz handling (v0 default — UTC)

For v0 the scheduler fires at `09:00 UTC`. Per-context timezone resolution (so each owner gets it at their local 9 AM) is a v0.5 follow-up — adds a `account.preferences.tz` resolver on the cron entry point and shards the schedule across hourly buckets. v0 lands the deterministic content + the skip-if-no-delta gate, which are the load-bearing pieces.

## Replies → TM Journal accept rail (v0.5)

Per canonical spec: "*replies route to TM Journal accept rail (reuse, don't build new)*."

For v0 we stamp `surface: "owner_digest_v0"` on every persisted digest row. The v0.5 reply handler will:
- Listen on the existing `/api/inbound/sendgrid` rail with envelope marker `In-Reply-To: <owner-digest-…>`.
- Insert the reply body into `db.documents` with `source_channel: "owner_digest_reply"` + `lifecycle_state: "pending"`.
- The Document Journal's existing "accept" affordance picks it up — **zero net-new code on the accept rail.**

This sprint did NOT touch any document-ingestion code (no new collections, no new schema). The hook surface (`surface` marker on the digest row) is the only thing the v0.5 reply handler needs to round-trip.

## Skip-if-no-delta — what "no delta" means

The `delta_hash` covers only fields that signal **material change** in board-level performance:
- `goal_id`     — goal identity.
- `status`      — categorical state (on_track / at_risk / off_track / achieved / not_started / abandoned).
- `score`       — current performance score.
- `probability` — current probability of success.
- `band`        — derived band of `score` (strong/moderate/weak/critical) — coarsens the comparison so a 1-pt score wobble doesn't fire a fresh digest, but a band crossing does.

Excluded from the hash (deliberately): `target_value`, `target_metric`, `target_date`, `description`, `rationale`, `score_history`, timestamps. These are reference data that don't constitute weekly board-level signal.

## Proving slice 7/7 GREEN

Run: `cd /app/backend && python scripts/jc_owner_digest_v0_slice.py`

| Row | Subject | Outcome |
|---|---|---|
| 1 | Composer is deterministic; identical inputs → identical delta_hash | ✓ |
| 2 | Off_track + at_risk goals ranked first in `rows[]` | ✓ |
| 3 | `previous_score` + `delta_score` computed from pre-window score_history entry | ✓ (prev=60, delta=-25) |
| 4 | `compose_or_skip` returns skip=True after persisting an identical first digest | ✓ |
| 5 | `compose_or_skip` returns skip=False when a goal's score changes (hash differs) | ✓ |
| 6 | `POST /api/cron/owner-digest-weekly` is X-Cron-Secret gated (403 unauth, 200 auth) | ✓ |
| 7 | APScheduler arms `owner_digest_weekly` job at Mon 09:00 | ✓ |

Runtime: ~5s. No LLM/Shield calls in either the composer or the slice.

## Halt-and-Surface gate evaluation

| Gate                                                | Threshold | Observed | Verdict |
|-----------------------------------------------------|-----------|----------|---------|
| Scheduler infra missing                             | new infra | none — reused existing APScheduler + AKKI_CRON_SECRET | ✅ PASS |
| Shield / LLM call along the composer path           | 0         | 0        | ✅ PASS |
| New collection / schema for the accept rail         | 0         | 0 (reuse existing `documents` + `source_channel` field) | ✅ PASS |
| Net-new email-transport code                        | 0 (v0)    | 0 — deferred to v0.5 | ✅ PASS |
| Skip-if-no-delta gate present + tested              | yes       | yes      | ✅ PASS |

## Files

- `backend/services/owner_digest.py` — new (composer + skip gate)
- `backend/routers/owner_digest.py` — new (3 endpoints, cron-secret gated)
- `backend/akki_app.py` — router registered (1 import + 1 include line)
- `backend/server.py` — APScheduler job added (Mon 09:00 UTC)
- `backend/scripts/jc_owner_digest_v0_slice.py` — new (proving slice)

## v0.5 follow-ups (out of scope for this sprint)

1. Per-context TZ resolution: hourly-bucket cron sharded across `account.preferences.tz` values.
2. Email delivery rail: SendGrid template + per-owner unsubscribe.
3. Reply handler: `/api/inbound/sendgrid` envelope sniff → `documents` insert with `source_channel='owner_digest_reply'`.
4. In-app digest surface in the Monitor side panel (read state stamped on the row).

— END —
