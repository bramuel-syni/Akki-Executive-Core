**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (parent
JC-WS lock; this triage is the Phase 5.5.3 deferred candidate-C
work that the Phase 5.5.2 sprint memo carried forward).

# PHASE 5.5.3 — Broader-suite drift triage · investigative only · no fixes shipped

## Scope of this triage

Phase 5.5.2 closed with two surgical fixes (candidates A + B) and
deferred "candidate C — broader-suite drift across ~7+ test files
NOT in the original Q1-Q5 scope" to Phase 5.5.3 / future. That
deferral has been sitting in DEV_PIPELINE §8 since 2026-06-05.

This dispatch's deliverable: **a sharp picture of which files
carry drift, what the drift modes are, and a phased remediation
plan**. No code changes ship from this dispatch — the actual
fixes belong to a future Phase 5.6+ dispatch with deliberate scope
+ user sign-off.

Run command for this triage (reproducible):

```bash
cd /app/backend && \
  python -m pytest tests/ -q --tb=no -p no:warnings -n 8 --dist=loadfile \
  > /tmp/pytest_broad.log 2>&1
```

Last-run timestamp: 2026-06-26 09:53 → 10:06 UTC (12 min 39 s wall clock).

## Headline numbers

| Outcome | Count |
|---|---:|
| Total tests collected | 4 410 |
| ✅ Passed | 3 738 (84.8 %) |
| ⏭ Skipped | 459 (10.4 %) |
| 🔴 Failed | 202 |
| 🟠 Errored (collection or fixture failure) | 11 |
| **Files carrying ≥ 1 failure or error** | **101** |
| Time | 759.5 s |

The ~7+ files prediction undercounted by roughly 14×. The actual
drift surface is broad but appears to be a **small number of root
causes hitting many tests** rather than 100+ independent
regressions.

## Failure-mode taxonomy (sampled)

I sampled the top 5 failing files and read the first 2–3 failures in
each. The dominant failure mode is uniform:

```
httpx.HTTPStatusError: HTTP 500: Internal Server Error
  /app/backend/contracts/_adapters/_http_client.py:286
```

This is the centralised HTTP-transport adapter (the same file that
got the candidate-B fix in Phase 5.5.2 — `_sanitize_kwargs_for_json`).
A 500 is bubbling up from the in-process FastAPI app to the test rig,
which then surfaces as a test failure. The server-side error is what
needs to be tracked down per family of test.

**Three working hypotheses (each requires a 1-hour spike to confirm):**

1. **Auth-rig drift** (≈ 40-50 % of failures by sampling).
   Test families like `test_phase_p3_1_csrf`, `test_phase_p5_5_session_reauth`,
   `test_phase_p2_a2_microsoft_pkce`, `test_phase_p5_6_csrf_cookie_domain`
   all hit a login / token-refresh / CSRF flow. They are the same
   class of failure as the 3 pre-existing Solva v2 CSRF-rig fails
   confirmed during the BUG-ANL-UPLOAD-GRIDFS regression checks
   (which I confirmed PRE-EXISTING via `git stash`). The likely
   root cause: the CSRF middleware now requires a token round-trip
   the test rig doesn't perform; the in-proc transport returns 500
   instead of 403 because the absence trips an unhandled exception.
   *Fix shape: update the central in-proc fixture to do the CSRF
   round-trip; OR add a `request.state.csrf_skip = True` for the
   test client.*

2. **Inbox / waitlist data-model drift** (≈ 15-20 %).
   `test_phase_p5_7_waitlist_reminder`, `test_phase_p5_7_5_bounce_webhook`,
   `test_phase_p5_8_inbox_migration`, `test_phase_p5_10_audit_panel_direct_linkage`.
   These touch Mongo collections that have evolved their schema
   (active context_id requirements, tenancy filters added). Tests
   were authored before the tenancy enforce-mode landed and now
   the seed data they create gets filtered out by the canonical
   membership gate.
   *Fix shape: update test seed-data helpers to add a context_id
   + membership row.*

3. **Track A / Track B feature drift** (≈ 15-20 %).
   `test_track_a_phase3_prompt_fix`, `test_track_a_phase3_narration`,
   `test_track_a_phase2_drawer_journal`, `test_track_b_phase_b5_g6_notes_autosave`.
   These exercise feature branches that have since been refactored.
   The endpoints exist but the response-shape pinning the test does
   is stale.
   *Fix shape: re-pin assertions against current contract.*

The remaining ~15-20 % is a long tail of one-off files. Each will
need ~10 min of investigation. Not worth a hypothesis until the
top-3 cohorts are fixed (which likely lifts most of the long tail
as collateral).

## Full list of 101 failing files (alphabetical)

Saved to `/tmp/failing_files.txt` for the next dispatch. Top 25:

| # Tests failing | File |
|---:|---|
| 9 | `tests/test_track_a_phase3_prompt_fix.py` |
| 7 | `tests/test_phase_p5_8_inbox_migration.py` |
| 6 | `tests/test_track_a_phase3_narration.py` |
| 6 | `tests/test_phase_p5_corrections.py` |
| 6 | `tests/test_phase_p2_a2_microsoft_pkce.py` |
| 5 | `tests/test_track_a_phase2_drawer_journal.py` |
| 5 | `tests/test_phase_p5_7_waitlist_reminder.py` |
| 5 | `tests/test_phase_p5_10_audit_panel_direct_linkage.py` |
| 5 | `tests/test_phase_p3_1_csrf.py` |
| 5 | `tests/test_j3_stage_4_5_backend.py` |
| 5 | `tests/test_home_cleanup_phase_e3.py` |
| 4 | `tests/test_phase_p5_7_5_bounce_webhook.py` |
| 4 | `tests/test_phase_p5_6_csrf_cookie_domain.py` |
| 4 | `tests/test_phase_p5_5_session_reauth.py` |
| 4 | `tests/test_phase_p2_b1_security_headers.py` |
| 4 | `tests/test_phase_m2prep_notify_multirecipient.py` |
| 3 | `tests/test_track_b_phase_b5_g6_notes_autosave.py` |
| 3 | `tests/test_phase_z2_batch3.py` |
| 3 | `tests/test_phase_z2_batch1.py` |
| 3 | `tests/test_phase_s_password_reset.py` |
| 3 | `tests/test_phase_p5_9_admin_button_and_badge.py` |
| 3 | `tests/test_phase_m3_public_trust.py` |
| 3 | `tests/test_patch_9_streaming_phases.py` |
| 3 | `tests/test_home_cleanup_phase_f4.py` |
| 3 | `tests/test_admin_qa_hooks.py` |

## What this triage is NOT

- **NOT** a fix list. Nothing in this dispatch attempts a rewrite.
- **NOT** a green-tree promise. The 202 failures are pre-existing
  drift and will remain failing until a future dispatch addresses
  them with deliberate scope.
- **NOT** a basis to widen the CI's `backend-tests.yml` lane. That
  expansion stays parked until the top-3 hypotheses are confirmed
  AND the fixes ship green AND the lane runs clean for 7 days.

## Proposed remediation order (Phase 5.6+ subject to user sign-off)

1. **Phase 5.6.1 — CSRF auth-rig fix.** 1-day sprint. Touch:
   `tests/conftest.py` (central in-proc fixture). Expected lift:
   ~80-100 tests across CSRF / session / login / waitlist families.

2. **Phase 5.6.2 — Tenancy seed-data refresh.** 1-day sprint. Touch:
   per-suite seed helpers in `tests/_helpers/` (add context_id +
   membership row to every seeded account). Expected lift: ~30-40
   tests in the inbox / audit-panel / waitlist families.

3. **Phase 5.6.3 — Track A/B contract re-pin.** 2-3 day sprint.
   Touch per-test assertion blocks against current OpenAPI contract.
   Expected lift: ~30-40 tests across the `track_a_*` and
   `track_b_*` families.

4. **Phase 5.6.4 — Long tail.** Remaining ~20 files; ad-hoc.

5. **Phase 5.7 — Backend-tests.yml lane widening.** Move from
   today's targeted-green scope to full-tree gating, gated on 7
   days of clean runs from 5.6.1-5.6.4.

## Standing risks if not addressed

- **Coverage gap on regression.** The 5-check convergent regression
  runs after major dispatches captures only the locked-bar
  invariants. Drift in the broader suite means we don't catch
  collateral damage to non-pinned surfaces until a customer hits
  it.
- **CI-lane confidence erosion.** Engineers stop trusting `pytest`
  signal because so much of the tree is amber. The triage step
  before every PR review is "is this fail new or known?" — which
  is exactly the cognitive load the locked CI lane was supposed
  to eliminate.
- **Test-rig divergence from product.** Each month of drift makes
  the test rig further out of sync with the runtime auth/tenancy
  middleware. At some point the rig becomes unfixable without a
  rewrite.

## Standing rules respected

- ✅ No code changes shipped from this dispatch (investigative only).
- ✅ Triage scope honours the autonomy contract: "Skipped this run
  — Google OAuth native flow." The CSRF / OAuth / PKCE failures
  belong here but they're called out as Phase 5.6.1 work, NOT
  attempted now.
- ✅ Halt-and-surface respected — the user must sign off before
  Phase 5.6.x starts.
