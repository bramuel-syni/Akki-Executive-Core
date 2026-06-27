**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (Cluster-F sub-sprint F.3 = csrf + session_timeout + session_reauth — 3 M1 polluter files; scope memo §1.1 tagged "medium risk per CSRF middleware coverage; needs careful proving slice for token round-trips"; this advance scan memo source-reads the 3 files to verify or refine the risk classification before dispatching the mechanical conversion · READ-ONLY · no test/product/fixture mutations · HARD STOP at memo surface)

# Sprint P5.7-FIX-SCOPE-CLUSTER-F3-ADVANCE — F.3 structural-shape advance scan

**Status**: SHIPPED (memo only) · READ-ONLY · HARD STOP at memo surface · AWAITING USER F.3 FIX-SPRINT DISPATCH
**Date**: 2026-06-27
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (original scope memo's "medium risk" assignment for F.3); `sprints/JC_POLLUTION_CLUSTER_F5_FIX.md` (most recent Cluster-F sub-sprint, validates mechanical pattern at 3-file scale)
**Discipline**: READ-ONLY contract honoured · 0 LOC mutated · pure source-read + risk-classification output

---

## §0 — Filename verification (per F.1/F.5 audit-trail discipline)

User dispatch referenced `test_phase_p3_5_session_reauth.py`. Actual on-disk filename is `test_phase_p5_5_session_reauth.py` (the session-reauth sprint shipped in Phase P5.5, not P3.5). Per scope memo §0 the three F.3 files are:

| User reference | Actual on disk | Verified |
|---|---|:---:|
| `test_phase_p3_1_csrf.py` | `tests/test_phase_p3_1_csrf.py` | ✅ exact |
| `test_phase_p3_4_session_timeout.py` | `tests/test_phase_p3_4_session_timeout.py` | ✅ exact |
| `test_phase_p3_5_session_reauth.py` | `tests/test_phase_p5_5_session_reauth.py` | ⚠️ filename correction (user `p3_5` → actual `p5_5`) |

Documented per Cluster-F.1 / F.5 audit-trail standing rule. Same shape as F.5's `p4_3` / `p2_c1` / `p2_c2` corrections.

---

## §1 — Per-file evidence table

### §1.1 — `tests/test_phase_p3_1_csrf.py` — 7 sync tests / 162 LOC

| # | Test | LOC | Async surface? | Notes |
|---:|---|---:|:---:|---|
| 1 | `test_p3_1_csrf_mint_endpoint_returns_token_and_sets_cookie` | 30-42 | YES | `_run(_do())` with `_client()` async ctx manager; HTTP GET /api/csrf |
| 2 | `test_p3_1_post_without_csrf_returns_403_missing` | 45-70 | YES | `_run(_do())` + `os.environ` mutation in try/finally (CSRF_TEST_BYPASS_HEADER) |
| 3 | `test_p3_1_post_with_mismatched_csrf_returns_403_invalid` | 73-103 | YES | `_run(_do())` + same env-mutation pattern |
| 4 | `test_p3_1_post_with_matched_csrf_passes` | 106-135 | YES | `_run(_do())` + same env-mutation pattern; CSRF token round-trip in same async block |
| 5 | `test_p3_1_get_requests_bypass_csrf` | 138-144 | YES | `_run(_do())` simple HTTP GET |
| 6 | `test_p3_1_webhook_allowlisted` | 147-151 | NO | Pure-Python: only imports `_ALLOWLIST_PREFIXES` + asserts membership — **STAYS SYNC** per Cluster-F.2 heuristic |
| 7 | `test_p3_1_verify_round_trip` | 154-161 | NO | Pure-Python: only `mint_csrf_token()` + `verify_csrf_token()` calls — **STAYS SYNC** per heuristic |

**Helper at lines 21-22**: `def _run(coro): return asyncio.get_event_loop().run_until_complete(coro)` — exact M1 pattern.
**Conversion plan**: 5 async + 2 sync. env-mutation try/finally pattern (3 tests) preserved verbatim.

### §1.2 — `tests/test_phase_p3_4_session_timeout.py` — 5 sync tests / 141 LOC

| # | Test | LOC | Async surface? | Notes |
|---:|---|---:|:---:|---|
| 1 | `test_p3_4_absolute_timeout_rejects_after_12h` | 62-72 | YES | `_run(_do())`; forges JWT with `iat=-13h` |
| 2 | `test_p3_4_idle_timeout_rejects_after_30m_inactive` | 75-91 | YES | `_run(_do())`; pre-sets `last_activity_at` 31min ago via pymongo |
| 3 | `test_p3_4_fresh_session_passes` | 94-109 | YES | `_run(_do())`; forges fresh JWT |
| 4 | `test_p3_4_silent_refresh_emits_x_token_refreshed_header` | 112-131 | YES | `_run(_do())`; forges JWT with `iat=-65min` + fresh `last_activity_at` |
| 5 | `test_p3_4_public_routes_bypass_session_timeout` | 134-140 | YES | `_run(_do())` simple HTTP GET |

**Helper at lines 25-26**: exact M1 pattern.
**Conversion plan**: 5 async + 0 sync.

### §1.3 — `tests/test_phase_p5_5_session_reauth.py` — 4 sync tests / 210 LOC

| # | Test | LOC | Async surface? | Notes |
|---:|---|---:|:---:|---|
| 1 | `test_p5_5_login_bypasses_session_timeout_middleware` | 73-107 | YES | `_run(_do())` POST /api/auth/login with stale Bearer + Cookie |
| 2 | `test_p5_5_login_refreshes_last_activity_at` | 110-160 | YES | `_run(_login_then_probe())` — two sequential awaits in same async block (login + protected probe) |
| 3 | `test_p5_5_login_wrong_password_still_returns_401_not_timeout` | 163-192 | YES | `_run(_do())` POST /api/auth/login wrong password |
| 4 | `test_p5_5_csrf_endpoint_bypasses_idle_timeout` | 195-209 | YES | `_run(_do())` GET /api/csrf |

**Helper at lines 46-47**: exact M1 pattern.
**Conversion plan**: 4 async + 0 sync.

### §1.4 — Totals

| | Sync tests | Async-convert | Stay sync | LOC total |
|---|---:|---:|---:|---:|
| csrf | 7 | 5 | 2 | 162 |
| session_timeout | 5 | 5 | 0 | 141 |
| session_reauth | 4 | 4 | 0 | 210 |
| **F.3 total** | **16** | **14** | **2** | **513** |

Matches scope memo §0 (16 sync tests, ~510 LOC). Pattern continues from F.5: 14/16 async-conversion rate; 2 sync-preservation cases both in csrf file (pure-Python helper tests).

---

## §2 — Timing-sensitivity audit

This is the load-bearing section per user dispatch — the "medium risk" tag from scope memo §1.1 hinges on whether any F.3 test asserts on real wall-clock timing that could destabilize under `@pytest.mark.asyncio` semantics.

### §2.1 — Time-relative assertions, classified

| Test | Assertion class | Wall-clock dependency? | Risk under async |
|---|---|:---:|:---:|
| csrf:test_p3_1_csrf_mint_endpoint_returns_token_and_sets_cookie | Token shape (`tok and "." in tok`) | NO | low |
| csrf:test_p3_1_post_without_csrf_returns_403_missing | Status code + detail.code | NO | low |
| csrf:test_p3_1_post_with_mismatched_csrf_returns_403_invalid | Same shape, mint-then-tamper | NO | low (round-trip is in-same-async-block; no time gap) |
| csrf:test_p3_1_post_with_matched_csrf_passes | Status code != 403 | NO | low |
| csrf:test_p3_1_get_requests_bypass_csrf | Status code | NO | low |
| csrf:test_p3_1_verify_round_trip | Pure-fn round-trip | NO | low (stays sync) |
| csrf:test_p3_1_webhook_allowlisted | Set membership | NO | low (stays sync) |
| timeout:test_p3_4_absolute_timeout_rejects_after_12h | 401 + `session_absolute_timeout` | **NO (injected via JWT `iat=-13h`)** | low |
| timeout:test_p3_4_idle_timeout_rejects_after_30m_inactive | 401 + `session_idle_timeout` | **NO (injected via pymongo `last_activity_at = -31min`)** | low |
| timeout:test_p3_4_fresh_session_passes | Status 200/404 | NO | low |
| timeout:test_p3_4_silent_refresh_emits_x_token_refreshed_header | Header `X-Token-Refreshed: 1` | **NO (injected via JWT `iat=-65min` + pymongo fresh `last_activity_at`)** | low |
| timeout:test_p3_4_public_routes_bypass_session_timeout | Status 200 | NO | low |
| reauth:test_p5_5_login_bypasses_session_timeout_middleware | Status 200 + body shape | **NO (account seeded with `last_activity_at = -35min` via pymongo)** | low |
| reauth:test_p5_5_login_refreshes_last_activity_at | `(now - post_ts) < timedelta(minutes=2)` AFTER login | **YES — real wall-clock subtraction** | low (tolerance is 2 MINUTES on a test that runs in ~1s; tolerance >> async event-loop scheduling jitter) |
| reauth:test_p5_5_login_wrong_password_still_returns_401_not_timeout | Status 401 + detail.code != session_idle_timeout | NO | low |
| reauth:test_p5_5_csrf_endpoint_bypasses_idle_timeout | Status 200 + token | NO | low |

### §2.2 — Critical finding — every "time-sensitive" test injects time via DB state or forged JWT

The scope memo §1.1 "medium risk" tag was assigned on the apparent surface area of CSRF middleware + session middleware. Source-read reveals: **every time-sensitive assertion in all 3 files relies on INJECTED state** (JWT `iat` claims forged at mint time, `last_activity_at` written to Mongo before the HTTP call). NONE of the 16 tests:
- Call `time.sleep(...)` or `await asyncio.sleep(...)` mid-body
- Use `freezegun` patches
- Assert on duration between two real-time captures (the one exception — reauth test 2 — has a 2-minute tolerance that's 100× larger than any plausible async scheduling jitter)
- Have any test-body interleaving that would change semantics under async (each `_run(_do())` is a single atomic block; the conversion replaces it with `async def test_x()` + inlined `_do()` body, preserving the same in-order sequence)

**Verdict**: the "medium risk" tag was conservative on surface-area grounds, but the actual test-body shapes are all LOW risk under mechanical conversion. Same shape as F.1/F.2/F.4/F.5.

### §2.3 — Round-trip audit

Three CSRF token round-trips exist in csrf.py (tests 3, 4):
- Test 3: GET /api/csrf → cookie+header → POST /api/cohort/applications with TAMPERED `X-CSRF-Token`
- Test 4: GET /api/csrf → cookie+header → POST /api/cohort/applications with MATCHED token+cookie

Both round-trips occur within a SINGLE `async with _client() as ac:` block. The conversion makes this trivially safe: `async def test_x(): async with _client() as ac: r1 = await ac.get(...); r2 = await ac.post(...)`. The token is captured in a Python local variable between the two requests; no time gap, no interleaving with other tests, no async race.

CSRF token TTL: the `mint_csrf_token()` + `verify_csrf_token()` helpers (in `services/csrf`) appear to be HMAC-based without explicit TTL (test 7 verifies a freshly-minted token; the tampered-HMAC variant fails as expected). No time-based assertion on the verify side. Round-trip is safe.

---

## §3 — State-reset audit

| File | Tests touching admin state? | Mongo collections written | Before-each reset needed? |
|---|---|---|---|
| csrf | NO — uses anonymous /api/cohort/applications POST + /api/csrf | `cohort_applications` (3 tests post; cohort dedupes by email_lc — unique random emails per test prevent collisions) | NO — random UUID-suffix emails are already collision-free |
| session_timeout | YES — each test seeds a fresh account via `_make_account(prefix)` with random UUID-suffix email | `accounts` (5 tests, 1 row each), `accounts.last_activity_at` writes (2 tests) | NO — random emails are unique; accounts created in test are not deleted, but they don't interfere with each other |
| session_reauth | YES — same `_make_account(prefix)` pattern with random emails | `accounts` (4 tests, 1 row each) + `last_activity_at` writes | NO — same isolation |

**Verdict**: NONE of the 16 tests need a before-each Mongo reset fixture. Each test seeds its own UUID-suffixed account/email; collisions are statistically impossible. No autouse fixture additions required during F.3 conversion.

This matches F.1's pattern (which also uses UUID-suffixed accounts) and F.5's pattern (which kept the existing autouse `_clean_pkce_collection` fixture as-is).

---

## §4 — Locked-area scan across 3 files

Per the user's standing HALT condition "If any file reveals coupling to Shield / WS Generate Doc UI / Track-2 schema / Monitor pre-warmer in its production-code touches → HALT":

| File | Shield? | WS Doc UI? | Track-2? | Monitor pre-warmer? | OAuth providers? |
|---|:---:|:---:|:---:|:---:|:---:|
| csrf | NO | NO | NO | NO | NO |
| session_timeout | NO | NO | NO | NO | NO |
| session_reauth | NO | NO | NO | NO | NO |

**Imports per file**:
- csrf: `services.csrf` (mint + verify pure functions) — TEST-SIDE only
- session_timeout: `core` (JWT_SECRET, JWT_ALGO) — TEST-SIDE only, no mutation
- session_reauth: `core` (create_access_token) — TEST-SIDE only, no mutation

All 3 files are pure test-side. The conversion touches ONLY test bodies + module docstrings + the `_run` helper deletion. Zero production touches required.

---

## §5 — Risk classification

| File | Scope-memo tag | Advance-scan verdict | Rationale |
|---|---|---|---|
| csrf | medium | **LOW** | CSRF round-trips are in-same-async-block; pure-fn tests stay sync; env-mutation try/finally preserved verbatim |
| session_timeout | medium | **LOW** | All timeout assertions use injected state (JWT `iat` or pymongo `last_activity_at`); no real wall-clock waits |
| session_reauth | medium | **LOW** | Same injected-state pattern; 1 wall-clock assertion has a 2-min tolerance dwarfing any async jitter |

**Overall F.3 verdict**: LOW risk. The scope memo's "medium risk" was a conservative tag based on surface-area review; source-read reveals all 16 tests are mechanically convertible without special handling.

**Recommendation**: dispatch F.3 as a single sub-sprint (NOT split into F.3a/b/c). Apply the same mechanical pattern as F.1/F.2/F.4/F.5. No special test-shape modifications needed.

---

## §6 — Proving slice design recommendation

Standard ≥13-row shape per Cluster-F.5 (which set the pattern at 3-file scale):

| Row | Check |
|---|---|
| 1 | csrf in isolation post-fix → 7/7 PASS |
| 2 | session_timeout in isolation post-fix → 5/5 PASS |
| 3 | session_reauth in isolation post-fix → 4/4 PASS |
| 4 | csrf + autosave (B.2 polluter pair) → all PASS |
| 5 | session_timeout + autosave → all PASS |
| 6 | session_reauth + autosave → all PASS |
| 7 | Combined F.3 (all 3 files) → 16 PASS expected |
| 8 | Combined F.3 + autosave → 19 PASS expected |
| 9 | csrf + phase4_2 (A+D defensive) → all PASS |
| 10 | session_timeout + p5_10 (Cluster-E defensive) → all PASS |
| 11 | Log scan: zero `Future attached to a different loop` across paired Row 8's full stdout |
| 12 | Source-assertion: no F.3 file contains `_run` helper or `asyncio.get_event_loop().run_until_complete` |
| 13 | Bespoke-run invariant PASSES with M1_CEILING=5 (closure-schedule lock validated; 8 → 5 ratchet) |

**No additional rows recommended beyond the standard 13-row shape**. The CSRF round-trip integrity is already covered by `test_p3_1_verify_round_trip` (which stays sync — pure Python). Adding an explicit "CSRF token replay timing" row would be testing F.3's preserved behavior twice; not value-add.

---

## §7 — Closure-schedule lock update post-F.3

When F.3 ships, the trajectory continues:
- Remove 3 m1_entries from `bespoke_run_helper_grandfathered.yml`: csrf, session_timeout, session_reauth
- Ratchet `M1_CEILING` from `8` → `5` in `test_no_bespoke_run_helper.py`
- Post-F.3 state: 5 M1 entries remaining (5 in Cluster-G post-F bucket: rate_limits, mfa, cohort_funnel, csrf_cookie_domain, corrections); 0 in F.3/F.4/F.5 buckets; 0 in F.6 M1 bucket
- M2_CEILING stays at 28 (F.3 has no M2 sites)

After F.3, only F.6 remains in active Cluster-F scope (1 M2 outlier in synisense_security — Shield-adjacency HALT pre-armed).

---

## §8 — HALT conditions reviewed (pre-armed for the F.3 fix sprint)

Per user dispatch:

1. ✅ **Filename mismatch** — verified, documented in §0 (1 correction: user's `p3_5_session_reauth` → actual `p5_5_session_reauth`)
2. ✅ **Shield coupling** — none found across 3 files (§4)
3. ✅ **Locked-area coupling** — none found across 3 files (§4)
4. ✅ **Fix-shape entirely different from M1 mechanical pattern** — none surfaced; all 3 files have the canonical M1 `_run` helper at module level
5. ✅ **Timing-sensitive test** — none with real wall-clock dependency that could break under async (§2)
6. ✅ **State-machine tests changing semantics under async** — none surfaced; all round-trips are in-same-async-block

NO HALT conditions tripped. F.3 fix sprint is dispatch-ready.

---

## §9 — Discipline notes

- **Scope honoured**: READ-ONLY contract — 0 LOC mutated across the repo.
- **No testing subagent used** (per banned-list rule).
- **Locked-area scan clean** (§4).
- **Filename audit-trail discipline applied** (§0) — 1 correction documented (p3_5 → p5_5).
- **Risk classification refined** (§5) — scope memo's "medium" → advance scan's "LOW" with rationale.
- **No structural insight that wasn't already in the scope memo** — confirms the scope memo §0 evidence table was accurate at the file-line level; the only new finding is the timing-sensitivity audit which the scope memo didn't perform.

---

## §10 — User-direction surface (HARD STOP per dispatch)

Advance scan complete. F.3 fix sprint is **dispatch-ready** with the following parameters:

- **Files**: csrf + session_timeout + session_reauth (3 files; LOW risk)
- **Conversion count**: 14 async + 2 sync (matches F.5 ratio at scale; pattern uniform)
- **Proving slice**: standard 13-row shape (NO additions needed beyond the standard)
- **Closure-schedule lock**: remove 3 entries from YAML, ratchet M1_CEILING 8 → 5
- **Locked-area**: clear
- **HALT conditions**: 6/6 pre-armed conditions clean

When user dispatches the F.3 fix sprint, I'll apply the mechanical conversion as described in §1, ship the 13-row slice as described in §6, and update the closure-schedule lock as described in §7. Standing rules unchanged.

Awaiting next dispatch from user.
