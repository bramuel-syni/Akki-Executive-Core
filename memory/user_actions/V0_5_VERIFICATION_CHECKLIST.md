**Canonical Spec**: `/app/memory/sprints/JC_WAVE3_ORIGIN_BRIEFS_MONITOR.md` + `/app/memory/sprints/JC_WAVE3_ORIGIN_BRIEFS_SOLVA_TM_FANOUT.md` (Origin-triggered Briefs Monitor first surface + Solva/TM fan-out; both CLOSED 2026-06-26) + `/app/memory/sprints/OWNER_DIGEST_V05.md` (Owner Digest v0.5 CLOSED 2026-06-26 · 12/12 GREEN) + `/app/memory/sprints/JC_MON_BACKGROUND_TRACKER.md` (JC-MON background tracker v0 CLOSED 2026-06-26 · 9/9 GREEN; user shorthand "Tracker v0.5") + user directive on user-verification pending.

# V0.5 verification checklist — 3 components, 3 flows

3 shipped components awaiting your verification. Each has a URL/route, test data setup, step-by-step actions, expected results, red flags, ~30-45 min per component.

**Test credentials** (from `/app/memory/test_credentials.md`):
- `admin@akki.ai` / `<redacted:ADMIN_SEED_PASSWORD>` — superadmin, owns Syni.ai HQ, carries `solva_v2_poc=true` + `solva_v2=true` feature flags
- `juliusaopio@gmail.com` / `Julius@Akki!2026-Exec` — rich substrate (5 contexts × 6 committees × 14 docs) — recommended for briefings/tracker
- `bramuel@syni.ai` / `Bramuel2026!` — NED test account (3 NED contexts + 1 exec)

---

## Component 1 — Origin-triggered Briefs (Wave 3)

### 1.1 What shipped

Two sprints closed 2026-06-26:
- **Monitor first-surface**: `POST /work-studio/export/{kind}` accepts `origin_kind` + `origin_id`. FE has "Brief this" affordance on Strategic Goals + Signals surfaces.
- **Solva + Task Manager fan-out**: Same `origin_kind` enum extended to `solva_session` + `task_manager_task`. "Brief this" button on `SolvaArtefact.jsx` handoff bar + Task Manager task detail view.

### 1.2 What changed vs v0

- **v0** (before Wave 3): Briefs existed as a Work Studio picker entry. User navigated Work Studio, picked "brief", chose a kind, pasted context manually.
- **v0.5 (Wave 3)**: Briefs live on the ORIGIN surface. User is looking at a signal / session / task, clicks "Brief this", context auto-prefills from the origin.

### 1.3 Step-by-step verification (all 3 surfaces)

#### Monitor surface

1. Log in as `juliusaopio@gmail.com` / `Julius@Akki!2026-Exec` at `https://akki.syni.ai/app/login`
2. Navigate to `/app/monitor` (Strategic Goals dashboard)
3. Click a strategic objective card
4. Look for "Brief this" button/link near the objective title
5. Click it → should open a Brief modal or navigate to `/app/work-studio/brief/new` with prefilled context
6. Confirm the prefilled context includes: objective name, current rag_status, recent signals list, GP perspectives if any
7. Submit the brief; expect it to render + save to Doc Journal

#### Solva surface

1. Same account. Navigate to `/app/solva/v2-poc` (or `/app/solva/session/<any-existing-sid>`)
2. Open a completed Solva session (Julius's account has multiple)
3. Look for "Brief this session" button in the handoff bar (adjacent to "Continue in Chat" / "Use as input" / "Take to Cycle")
4. Click it → same modal/flow, prefilled from session evidence
5. Note: refused sessions should NOT show the "Brief this" button (per the sprint memo)

#### Task Manager surface

1. Same account. Navigate to `/app/task-manager` (or the module's route)
2. Open a task with sub-tasks
3. Look for "Brief this" affordance on the task detail view (3 mentions in the sprint memo suggest button + comment + helper)
4. Click it → same modal/flow, prefilled from task metadata + sub-tasks

### 1.4 Expected outcomes

- All 3 surfaces show the "Brief this" affordance
- Prefill is contextually accurate (matches what you were looking at)
- All 3 route to the SAME endpoint `/work-studio/export/brief` (verifiable via Network tab)
- No parallel brief endpoint per surface (confirmed in sprint memo Coupling-debt table)

### 1.5 Red flags to watch for

- "Brief this" button MISSING on any surface → sub-sprint incomplete
- Prefill drops material context (e.g., signal timeline missing on Monitor origin) → context builder bug
- Different endpoints per surface (e.g., `/api/monitor/brief` vs `/api/solva/brief`) → coupling-debt regression
- 500/422 errors on submit → schema mismatch (likely `origin_kind` enum drift)

### 1.6 Time estimate: ~30 min

---

## Component 2 — Owner Digest v0.5

### 2.1 What shipped

Per `sprints/OWNER_DIGEST_V05.md`, three additive pieces on top of v0:
- **Per-context TZ resolver**: `resolve_owner_tz(account_id)` reads `accounts.preferences.tz` (fallbacks `preferences.timezone` → top-level `timezone` → `UTC`)
- **SendGrid delivery**: real send vs v0's deterministic-body-only mode. Uses existing `services.cohort_email._send_via_sendgrid`. Honours `COHORT_NOTIFY_DISABLED=1` kill switch.
- **Reply-handler**: replies to `digest+<digest_id>@<SENDGRID_INBOUND_DOMAIN>` route into Doc Journal accept rail. Uses `reply_alias_for(digest_id)` + `extract_digest_id_from_alias(alias)` helpers.

### 2.2 What changed vs v0

- **v0**: deterministic body composed + skip-if-no-delta + hash gate, but NO actual email delivery. Body sat in `owner_digests` collection unsent.
- **v0.5**: same deterministic composer + skip gate + hash gate PLUS actual SendGrid delivery PLUS reply routing.
- **Cron change**: `CronTrigger(day_of_week="mon", hour=9, minute=0)` (single weekly UTC fire) → `CronTrigger(minute=5)` (hourly :05). TZ gate now inside the endpoint, not on the trigger.

### 2.3 Step-by-step verification

#### 2.3.1 Set a timezone on the test account

1. Log in as `juliusaopio@gmail.com` / `Julius@Akki!2026-Exec`
2. Navigate to profile/preferences (or use the API directly)
3. Set `accounts.preferences.tz = "America/New_York"` (or your preferred non-UTC zone)
4. Verify persisted via `GET /api/accounts/me` → check the `preferences.tz` field

#### 2.3.2 Trigger the cron manually (bypass the hourly wait)

```bash
# From your terminal or via a curl to the prod cron endpoint
API_URL="https://akki.syni.ai"
CRON_SECRET="<from your platform secrets>"

curl -s -X POST "$API_URL/api/cron/owner-digest" \
  -H "X-Cron-Secret: $CRON_SECRET" \
  -H "Content-Type: application/json"
```

Response should include per-context outcomes (delivered / skipped_no_delta / skipped_outside_target_hour / skipped_kill_switch).

#### 2.3.3 Check the delivery + reply-alias

1. Look at the email inbox for the owner's registered email
2. Confirm the digest arrived (may take a minute for SendGrid)
3. Check the Reply-To header on the email — should look like `digest+<digest_id>@<SENDGRID_INBOUND_DOMAIN>` where `<digest_id>` is a UUID
4. Reply to the email with an accept-signal (e.g., "accept #<objective_id>" or the accept-rail shape from Doc Journal)
5. Verify in Doc Journal that the accept was routed correctly (check `/api/doc-journal/entries` for a new entry with `source: "owner_digest_reply"`)

### 2.4 Expected outcomes

- Cron fires hourly at :05 (verifiable via APScheduler logs)
- ONLY the current-target-hour-in-target-tz contexts fire (e.g., 09:00 America/New_York = 13:00 UTC → only fires at 13:05 UTC cron)
- Deterministic body: same inputs → same output (test by running twice; second call should skip on hash match)
- Email delivered via SendGrid with correct Reply-To alias
- Reply → Doc Journal accept-rail entry created

### 2.5 Red flags to watch for

- Cron fires but 0 emails sent → check `COHORT_NOTIFY_DISABLED` env var (should be unset or 0 for prod)
- Emails sent to wrong tz (e.g., 09:00 UTC when owner is in NY) → TZ resolver bug
- Reply-To alias missing or malformed → alias builder regression
- Reply arrives but doesn't route to Doc Journal → reply-handler regression
- Same digest sent twice (no hash skip) → skip-if-no-delta broken

### 2.6 Time estimate: ~45 min (including waiting for email delivery)

---

## Component 3 — JC-MON Background Tracker (user shorthand "Tracker v0.5")

### 3.1 What shipped

Per `sprints/JC_MON_BACKGROUND_TRACKER.md`:
- **Pre-warmer cron** at `CronTrigger(minute=15)` — hourly at :15 (deliberately off top-of-hour to avoid collision with Synisense Engine signal-seeder cron)
- **Endpoint**: `POST /api/cron/monitor-background-tracker` (X-Cron-Secret gated, no JWT)
- **Discriminator**: `skip-UNLESS-tracked-evidence-changed-since-last-run` via `compute_evidence_fingerprint(context_id, account_id)` returning SHA-256 over `(signal_id, created_at)` + `(doc_id, created_at)` tuples
- **Budget**: per-objective Shield budget cap; stops calling Shield once per-run cap hit; surfaces `shield_budget_exhausted=True` in summary
- **Architecture invariant**: pre-warmer for on-demand engine, NOT parallel always-on tracker. Uses SAME `recommend_interventions` / `explain_performance` / `extended_health` code paths as on-demand.

### 3.2 What changed vs v0

- **v0**: no background tracking. Monitor status assessments happened on-demand only (user opens Monitor → status computed live → user waits).
- **v0.5**: pre-warmer runs hourly. When user opens Monitor, most statuses are already computed. Skip discriminator avoids wasted Shield budget on unchanged evidence.

### 3.3 Step-by-step verification

#### 3.3.1 Seed some evidence change

1. Log in as `juliusaopio@gmail.com` (rich substrate — 5 contexts)
2. Navigate to a strategic objective in Monitor
3. Trigger evidence change: add a signal (via Signal Engine or admin API), or upload a doc via Workbook Analyzer
4. Note the timestamp

#### 3.3.2 Trigger the tracker cron manually

```bash
API_URL="https://akki.syni.ai"
CRON_SECRET="<from platform secrets>"

curl -s -X POST "$API_URL/api/cron/monitor-background-tracker" \
  -H "X-Cron-Secret: $CRON_SECRET" \
  -H "Content-Type: application/json"
```

Response should include per-context outcomes with fingerprint fields.

#### 3.3.3 Verify pre-warming happened

1. Refresh the Monitor page for the objective you seeded evidence into
2. The status assessment should be already-computed (`status_assessment_source: "tracker_v0"` on the row)
3. Check the DB via `GET /api/monitor/objectives/<id>/status` — should show a `rag_status` + `status_assessment` populated
4. UI should render fast (no live-Shield-call wait)

#### 3.3.4 Verify the skip discriminator

1. Trigger the tracker cron AGAIN immediately (no evidence change between calls)
2. Response should show `skipped=<count>` incremented (evidence fingerprint unchanged → skip)
3. Shield budget consumed on the second call should be ~0

#### 3.3.5 Verify budget cap

- Set the per-objective Shield budget cap intentionally low (test-env only; ask ops if unsure how)
- Trigger the cron on an account with many objectives
- Verify the summary surfaces `shield_budget_exhausted=True` when the cap is hit

### 3.4 Expected outcomes

- Cron fires hourly at :15 (verifiable via APScheduler logs)
- Uses SAME code paths as on-demand (`_gather_engine_signals` + `_gather_recent_docs` + `_format_assessment_prompt` + `_parse_assessment_response` + `shield_invoke`) — verifiable by grep of `routers/monitor_background_tracker.py` import list
- Skip-if-unchanged-evidence works (2nd immediate call skips)
- Budget cap fires when hit
- Row is tagged `status_assessment_source: "tracker_v0"` (distinguishable from on-demand which is tagged `"live"`)

### 3.5 Red flags to watch for

- Cron fires but calls Shield every time regardless of evidence change → fingerprint bug
- Rows not tagged `tracker_v0` → source-tagging regression
- Shield budget exhausted but keeps calling → budget cap bug
- Parallel always-on architecture (e.g., a websocket or long-poll always running) → architecture invariant violated
- Different code path from on-demand (grep for `recommend_interventions` etc. in the tracker file — should match on-demand) → drift

### 3.6 Time estimate: ~30 min

---

## Summary

| Component | Route/URL | Time | Test acct |
|---|---|---:|---|
| Origin-triggered Briefs (Wave 3) | Monitor + Solva + TM UI · `POST /work-studio/export/brief` | ~30 min | `juliusaopio@gmail.com` |
| Owner Digest v0.5 | `POST /api/cron/owner-digest` + inbox check | ~45 min | `juliusaopio@gmail.com` |
| Background Tracker v0.5 | `POST /api/cron/monitor-background-tracker` + UI check | ~30 min | `juliusaopio@gmail.com` |
| **Total** | | **~1h 45min** | |

---

## Where to record verification results

Same shape as LLM sign-off (per `LLM_REFRESH_SIGNOFF_CHECKLIST.md §Part C`):

1. **DEV_PIPELINE §9 verification row** — user adds a new row:
   ```
   | V0.5-USER-VERIFICATION-{ORIGIN-BRIEFS | OWNER-DIGEST | BG-TRACKER} — <PASS / PASS-with-note / FAIL> — <timestamp>
   | 2026-XX-XX (user marked verification · flow ran end-to-end · findings: <one-line summary>)
   | Free-form note field. Any red flags caught, minor issues, etc.
   | Cross-refs: V0_5_VERIFICATION_CHECKLIST.md + originating sprint memo
   ```

2. **On any FAIL**: user adds a note + tags `HALT`; agent auto-detects and opens a bug-fix sub-sprint.

---

## Cross-references

- Origin-Briefs Monitor: `sprints/JC_WAVE3_ORIGIN_BRIEFS_MONITOR.md`
- Origin-Briefs Solva/TM fan-out: `sprints/JC_WAVE3_ORIGIN_BRIEFS_SOLVA_TM_FANOUT.md`
- Owner Digest v0.5: `sprints/OWNER_DIGEST_V05.md`
- Background Tracker v0.5: `sprints/JC_MON_BACKGROUND_TRACKER.md`
- Predecessor Owner Digest v0: `sprints/OWNER_DIGEST_V0.md`
- Test credentials: `memory/test_credentials.md`
- Canonical spec for Monitor: `memory/JC_MON_CANONICAL_SPEC.md`
