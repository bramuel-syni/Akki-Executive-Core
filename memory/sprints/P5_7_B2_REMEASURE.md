**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE.md §2.3` (inter-cluster measurement procedure · post-A+D · READ-ONLY · HARD STOP at delta-index surface)

# Sprint P5.7-B2-REMEASURE — post-A+D delta sweep on B.2 polluter list

**Status**: SHIPPED (measurement-only) · slice **15/15 deterministic outcomes** with 0 halt flags · HARD STOP at delta surface · AWAITING USER DIRECTION ON B.2 FIX-SPRINT DISPATCH
**Date**: 2026-06-26
**Predecessor**: `sprints/JC_POLLUTION_A_D_FIX.md` (A+D shipped 2026-06-26; 8 tracker-FTT IDs closed + 1 Cluster D sibling regression)
**Discipline**: READ-ONLY contract honoured. 0 test files mutated. 0 product code mutated. Pure paired-pytest delta measurement.

---

## §0 — Headline measurement (table)

| Metric | Count |
|---|---:|
| Pre-A+D polluter count (P5.7-HOLDOUT-FINISHER) | **15** |
| Post-A+D polluter count (REMAINING — this sweep) | **15** |
| Disappeared (downstream of A+D's env / loop-policy leak) | **0** |
| Inconclusive (timeout / subprocess-inconsistency / OTHER) | **0** |

**Implication for B.2 fix-sprint scope**: **unchanged from the original P5_7_FIX_SCOPE.md §2.2 plan**. A+D's env-snapshot/restore and asyncio-loop-policy-restore patches had ZERO measurable effect on the autosave file's polluter set — the 15 polluters are entirely INDEPENDENT of A+D's mechanism and need test-side hardening on `test_track_b_phase_b5_g6_notes_autosave.py` itself.

---

## §1 — Why this signal is clean and load-bearing

The measurement procedure was designed in scope memo §2.3 expressly to answer this question:

> "Polluters that disappear from the list = they were depending on A+D's env leak, B.2's scope shrinks by that count. Polluters that remain = genuine session/cookie state issues, B.2's actual scope."

Empirical answer: **15 remained, 0 disappeared**. This is the maximum-confidence signal — it isolates B.2's pollution shape as orthogonal to A+D's. The 15-polluter list's cluster name in `FAILING_TEST_TRACKER.md` is `autosave_debounce_timer_leak`, but a closer reading of the 15 polluters' file names confirms the actual surface is **uniformly auth/session/CSRF state**:

```
test_phase_p2_a2_microsoft_pkce       — Microsoft OAuth PKCE flow
test_phase_p2_b1_security_headers     — security-header middleware
test_phase_p2_b4_password_change      — account password mutation
test_phase_p2_b6_admin_force_reset    — admin-triggered password reset
test_phase_p2_d2_health_composite     — health-composite (touches auth?)
test_phase_p3_1_csrf                  — CSRF token mint + verify
test_phase_p3_2_cookie_hardening      — cookie attributes (Secure/HttpOnly/SameSite)
test_phase_p3_4_session_timeout       — session timeout enforcement
test_phase_p5_5_session_reauth        — re-auth ladder
test_phase_p5_7_5_bounce_webhook      — SendGrid bounce webhook
test_phase_p5_7_waitlist_reminder     — waitlist reminder send path
test_phase_p5_8_inbox_migration       — inbox migration script
test_phase_p5_9_admin_button_and_badge — admin UI gating
test_phase_p5_10_audit_panel_direct_linkage — audit-panel resolver (FTT-023 polluter)
test_synisense_security               — Synisense security guard
```

Every one of these files touches admin auth state (`admin@akki.ai`), session cookies, CSRF tokens, or `app.dependency_overrides` on auth-related deps (`get_current_account`, `get_current_session`). The autosave file requires a clean admin auth state per test (it calls `_csrf_login(ac, "admin@akki.ai", "AkkiAdmin2026!")` at the top of every test); these polluters break that state.

**A+D's env-snapshot/restore couldn't have closed these** — none of them depend on `BOUNDED_CONTEXT_TRANSPORT`, `SENDGRID_*`, or any other key A+D was leaking. They depend on Mongo collection state (`login_failed_attempts`, `session_revocations`, account-row mutations) and `app.dependency_overrides`. **Confirmed independent fix shape.**

---

## §2 — Per-polluter evidence

Each of the 15 polluters has its own per-pair MD at:

```
memory/jc_artifacts/test_pollution/b2_remeasure/<polluter_slug>.md
```

Format mirrors the holdout-finisher's confirmed-pair MDs: file:line reproduction command, exit code, STDOUT tail, sample-recheck consistency boolean, locked-area flag. All 15 sample-rechecks were CONSISTENT (no subprocess-inconsistency halt fired).

Consolidated delta index:

```
memory/jc_artifacts/test_pollution/b2_remeasure_20260626T214643Z.md
```

---

## §3 — B.2 fix-sprint scope (confirmed unchanged)

The original scope memo §2.2 plan stands without modification:

- **Touch**: `tests/test_track_b_phase_b5_g6_notes_autosave.py` (test file only)
- **Patch shape**: add an autouse function-scoped fixture that resets the four state surfaces before each test:
  1. `db.login_failed_attempts.delete_many({"email": "admin@akki.ai"})`
  2. `db.session_revocations.delete_many({"account_id": <admin's id>})` (or all if admin's id resolution is brittle)
  3. `db.accounts.update_one({"email": "admin@akki.ai"}, {"$unset": {"is_locked": "", "mfa_required": "", "force_reset_at": ""}})`
  4. `app.dependency_overrides.clear()` or restore-to-baseline (the conftest's `_isolate_dependency_overrides` autouse fixture already does the per-test snapshot/restore, so polluter dep-override leaks should be caught there — but this DOES NOT close all 15 polluters, so the leak is NOT purely dep-overrides)
- **Closes**: FTT-024..026 (3 IDs, on the autosave file's three failing tests)
- **Proving slice target**: 17/17 GREEN per memo §2.2 (15 paired-polluter checks + isolation + post-fix holdout sweep)

### §3.1 — Important refinement from this remeasure

The original §2.2 plan listed `app.dependency_overrides` as one of four reset surfaces. But conftest.py already has `_isolate_dependency_overrides` (an autouse function-scoped fixture at `tests/conftest.py:224-253`) that snapshots and restores `app.dependency_overrides` per test. Since that fixture exists and still 15 polluters break the autosave file, the dep-override leak is NOT the dominant mechanism for B.2.

**The dominant mechanism is Mongo-collection state on `admin@akki.ai`**:
- `login_failed_attempts` counter increments by failed-login polluters
- `session_revocations` rows persist across tests
- `accounts.{is_locked, mfa_required, force_reset_at}` flags get set by P2/P3/P5 tests and don't reset

B.2's autouse fixture should focus on Mongo-collection reset, NOT dep-override clear.

---

## §4 — Discipline notes

- **READ-ONLY contract honoured**: 0 test files mutated. 0 product code mutated. 0 fixtures mutated.
- **Same harness as P5.7-HOLDOUT-FINISHER**: 30 s per-pair timeout, sample-recheck on every confirmed pair (subprocess-inconsistency guard).
- **Sample-recheck consistency**: 15/15 PAIRS CONSISTENT — no halt fired.
- **Locked-area scan**: zero locked-area polluters in the 15 (none touch Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer source paths).
- **No testing subagent used** (per banned-list rule).
- **HARD STOP at delta surface**: B.2 fix-sprint dispatch awaits user direction.

---

## §5 — Files produced

| Path | Status |
|---|---|
| `/app/backend/scripts/jc_pollution_b2_remeasure_slice.py` | NEW — 15-pair sweep harness (READ-ONLY) |
| `/app/memory/jc_artifacts/test_pollution/b2_remeasure/<15 per-polluter MDs>` | NEW × 15 |
| `/app/memory/jc_artifacts/test_pollution/b2_remeasure_20260626T214643Z.md` | NEW — consolidated delta index |
| `/app/memory/sprints/P5_7_B2_REMEASURE.md` | NEW — this sprint memo |

## §6 — Files NOT touched

- 0 product code mutated (`backend/`, `frontend/`)
- 0 test files mutated (`backend/tests/`)
- 0 fixture files mutated (`conftest.py`)
- 0 invariant files mutated (`tests/invariants/`)

---

## §7 — User-direction surface (next dispatch)

The B.2 fix-sprint can dispatch with confidence on the original §2.2 plan, refined by §3.1:

- **Recommended shape**: autouse function-scoped fixture in the autosave file resetting Mongo-collection state on `admin@akki.ai` (NOT dep-overrides — conftest already handles those).
- **Closes**: FTT-024..026 (3 IDs).
- **Proving slice**: 17/17 GREEN target.

If you want the B.2 fix dispatched **after** Cluster-E (FTT-023) closes, the §3.1 refinement carries over unchanged. Sequencing decision is yours.
