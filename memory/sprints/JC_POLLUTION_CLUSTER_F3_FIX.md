**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (Cluster-F sub-sprint F.3 dispatched 2026-06-27 · advance-scan memo `P5_7_FIX_SCOPE_CLUSTER_F3_ADVANCE.md §5` verdict LOW-risk · scope locked to 3 M1 polluter files · HARD STOP at proving-slice close · no chain into F.6 · closure-schedule lock end-to-end validated by Row 13 against bespoke-run invariant)

# Sprint JC_POLLUTION_CLUSTER_F3_FIX — mechanical sync→async conversion on the CSRF + session-middleware sub-sprint

**Status**: SHIPPED (test-file-only patches landed) · proving slice **13/13 GREEN** stable across 2 consecutive runs · regression-check ladder GREEN · HARD STOP at slice close · closure-schedule lock validated
**Date**: 2026-06-27
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_F3_ADVANCE.md` (immediate predecessor — READ-ONLY advance scan that reclassified F.3 medium → LOW risk); `sprints/JC_POLLUTION_CLUSTER_F5_FIX.md` (13/13 GREEN — F.5 3-file largest test-count group); `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (closure-schedule lock)

---

## §0 — Outcome at a glance

| File | Sync tests | Conversions | Post-fix isolation |
|---|---:|---|---|
| `tests/test_phase_p3_1_csrf.py` | 7 | 5 async-converted + 2 stay sync (`test_p3_1_webhook_allowlisted` `_ALLOWLIST_PREFIXES` membership + `test_p3_1_verify_round_trip` pure mint+verify) | 7/7 PASS |
| `tests/test_phase_p3_4_session_timeout.py` | 5 | 5 async-converted + 0 sync | 5/5 PASS |
| `tests/test_phase_p5_5_session_reauth.py` | 4 | 4 async-converted + 0 sync | 4/4 PASS |
| **Totals** | **16** | **14 async-converted + 2 stay sync** | **16/16 PASS** |

**Net**: Cluster-F.3 closes wrong-loop-binding at source for 3 more of 14 Cluster-F polluters. **13 of 14 polluters converted** across F.2 + F.1 + F.4 + F.5 + F.3. Only F.6 (1 M2 file: synisense_security with 2 sites · Shield-adjacency HALT pre-armed) remains in active Cluster-F scope.

**Advance-scan LOW-risk verdict honoured under conversion**: every timing-sensitive assertion across all 3 files (forged JWT `iat=-13h/-31min/-65min`, pre-set `last_activity_at=-35min` via pymongo) injected state pre-HTTP-call with zero real wall-clock dependencies; the conversion did not introduce any timing destabilization. The scope memo's original "medium risk" tag was conservative; advance scan's "LOW" verdict was correct.

---

## §1 — Patches applied (test-file-only, locked-area cleared)

### §1.1 — `tests/test_phase_p3_1_csrf.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 21-22 pre-fix)
- Kept `_client()` factory function (still returns an unawaited `AsyncClient` for `async with` use)
- Converted 5 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_p3_1_csrf_mint_endpoint_returns_token_and_sets_cookie`
  - `test_p3_1_post_without_csrf_returns_403_missing` (env-mutation try/finally preserved — see note)
  - `test_p3_1_post_with_mismatched_csrf_returns_403_invalid` (env-mutation try/finally preserved)
  - `test_p3_1_post_with_matched_csrf_passes` (env-mutation try/finally preserved)
  - `test_p3_1_get_requests_bypass_csrf`
- Inner `_do()` async closures inlined directly into the test body; the `_run(_do())` invocation replaced by direct `async with _client() as ac: ...` block.
- 3 of the 5 async-convert tests carry `os.environ` mutation for `CSRF_TEST_BYPASS_HEADER` to disable the autouse bypass; the try/finally pattern (save old → set "0" → run → restore old) is preserved verbatim and now wraps the async block instead of `_run(_do())`.
- `test_p3_1_webhook_allowlisted` STAYS SYNC — only imports `_ALLOWLIST_PREFIXES` + asserts membership. Pure-Python helper test.
- `test_p3_1_verify_round_trip` STAYS SYNC — only calls pure-Python `mint_csrf_token()` / `verify_csrf_token()`. No asyncio surface.

### §1.2 — `tests/test_phase_p3_4_session_timeout.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 25-26 pre-fix)
- Converted 5 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_p3_4_absolute_timeout_rejects_after_12h`
  - `test_p3_4_idle_timeout_rejects_after_30m_inactive`
  - `test_p3_4_fresh_session_passes`
  - `test_p3_4_silent_refresh_emits_x_token_refreshed_header`
  - `test_p3_4_public_routes_bypass_session_timeout`
- Inner `_do()` closures inlined; `_make_account()` + `_forge_token()` helpers stay sync (they don't touch asyncio).

### §1.3 — `tests/test_phase_p5_5_session_reauth.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 46-47 pre-fix)
- Converted 4 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_p5_5_login_bypasses_session_timeout_middleware`
  - `test_p5_5_login_refreshes_last_activity_at` (the test with the 2-min wall-clock tolerance — verified safe under async; tolerance is 120× any plausible event-loop scheduling jitter)
  - `test_p5_5_login_wrong_password_still_returns_401_not_timeout`
  - `test_p5_5_csrf_endpoint_bypasses_idle_timeout`
- Inner `_login_then_probe()` closure (test #2) inlined as 2 sequential `await ac.post(...)` + `await ac.get(...)` in same async block.

### §1.4 — Closure-schedule lock edits (F.5-slip lesson applied)

Per the F.5 mid-flight YAML-edit slip recorded in `JC_POLLUTION_CLUSTER_F5_FIX.md §1.5`, applied a SINGLE BATCHED `mcp_search_replace` removing all 3 F.3 entries at once (vs F.5's 2 sequential calls). The match `old_str` captured the full 5-entry block from csrf → mfa → session_timeout → cohort_funnel → session_reauth; the `new_str` retained only the 2 Cluster-G (post-F) interleaved entries (mfa + cohort_funnel). Single atomic edit, no risk of mid-flight slip.

Post-edit `yaml.safe_load` verify confirmed exact state BEFORE running the slice:
- M1 count: 5 (matches new `M1_CEILING`)
- M2 count: 28 (unchanged)
- All 5 remaining M1 entries are `Cluster-G (post-F)` (rate_limits, mfa, cohort_funnel, csrf_cookie_domain, corrections)
- 0 stale entries · 0 new ungrandfathered sites

`M1_CEILING` ratcheted from `8` → `5` in `test_no_bespoke_run_helper.py` to reflect the new baseline post-F.3 closure (trajectory: 13 → 11 (F.4) → 8 (F.5) → 5 (F.3); next ratchet: F.6 closes 0 M1 + 2 M2 → M1_CEILING stays at 5 post-F.6 because F.6 is M2-only; M2_CEILING ratchets 28 → 26 post-F.6).

### §1.5 — F.3-ADVANCE-slip lesson applied

Per the F.3-ADVANCE-scan discipline slip recorded in `P5_7_FIX_SCOPE_CLUSTER_F3_ADVANCE.md` close-surface, applied the DEV_PIPELINE.md §9 row update BEFORE authoring this memo. Verified line addition pre-memo via grep. Discipline standing rule "DEV_PIPELINE.md updated before sprint memo" honoured in F.3 fix sprint.

### §1.6 — Locked-area re-confirmation (advance-scan §4 already verified clean)

| Area | Touched? |
|---|---|
| Shield surfaces | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| CSRF middleware (`services/csrf` mint+verify pure functions) | NO — test-side import only |
| Session middleware (`core` JWT_SECRET, JWT_ALGO, create_access_token) | NO — test-side import only |
| OAuth provider live endpoints | NO |
| Product code | NO |

Cleared. All edits are test-side or invariant-side (the invariant edit is the closure-schedule lock).

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_f3_proving_slice.py`)

```
============================================================================
P5.7-Cluster-F.3 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
============================================================================
  Row  1  GREEN  tests/test_phase_p3_1_csrf.py in isolation post-fix (7 passed)
            7 passed, 23 warnings in 4.33s
  Row  2  GREEN  tests/test_phase_p3_4_session_timeout.py in isolation post-fix (5 passed)
            5 passed, 21 warnings in 5.27s
  Row  3  GREEN  tests/test_phase_p5_5_session_reauth.py in isolation post-fix (4 passed)
            4 passed, 21 warnings in 5.56s
  Row  4  GREEN  csrf + autosave (B.2 polluter pair, post-fix)
            10 passed, 23 warnings in 5.23s
  Row  5  GREEN  session_timeout + autosave (B.2 polluter pair, post-fix)
            8 passed, 21 warnings in 5.84s
  Row  6  GREEN  session_reauth + autosave (B.2 polluter pair, post-fix)
            7 passed, 21 warnings in 6.38s
  Row  7  GREEN  Combined F.3 (all 3 files) — 16 PASS expected
            16 passed, 23 warnings in 6.51s
  Row  8  GREEN  Combined F.3 + autosave — 19 PASS expected
            19 passed, 23 warnings in 7.47s
  Row  9  GREEN  csrf + phase4_2 (A+D defensive)
            15 passed, 23 warnings in 5.19s
  Row 10  GREEN  session_timeout + p5_10 (Cluster-E defensive)
            10 passed, 21 warnings in 5.47s
  Row 11  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 8's full stdout
  Row 12  GREEN  source-assertion: no _run / get_event_loop.run_until_complete
            all 3 F.3 files clean
  Row 13  GREEN  bespoke-run invariant PASSES (F.3 entries removed + M1_CEILING=5)
            3 passed, 21 warnings in 6.43s
============================================================================
RESULT  13/13 GREEN
============================================================================
```

**Key signals**:
- **Rows 4-6**: each F.3 file paired with autosave (the B.2 polluted target) → all PASS. 3 more polluter→polluted pairs closed.
- **Row 8**: combined F.3 + autosave = 19/19 PASS (16 F.3 + 3 autosave). The pollution scope for these 3 polluters is now empty.
- **Rows 9-10**: defensive checks confirm A+D's and Cluster-E's closures aren't regressed.
- **Row 11**: zero `Future attached to a different loop` occurrences — canonical signature silenced.
- **Row 12**: source-assertion confirms no `_run` / `get_event_loop.run_until_complete` remains in any of the 3 files.
- **Row 13**: closure-schedule lock validated end-to-end — invariant catcher + drift detector + count-ceiling ALL PASS (3 tests) after YAML edits + M1_CEILING ratchet 8→5.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **92 pass / 7 pre-existing failures** unchanged | Same pattern as post-F.5 state. NOT regressions from F.3. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via `test_phase4_4_dual_mount_smoke.py` 37/37 PASS — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` in lockstep |
| JC-TM email path smoke | yes | **N/A** | No SendGrid send code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Cluster's own proving slice | yes (13/13) | **13/13 GREEN** stable across 2 runs |
| Inventory slice sibling re-run | yes | **3/3 GREEN** · M1=5/5 ceiling, M2=28/28 ceiling, zero drift |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_phase_p3_1_csrf.py` | MOD | Helper drop + 5 sync→async + env-mutation try/finally preserved + 2 sync preserved + docstring (≈25 LOC delta) |
| `tests/test_phase_p3_4_session_timeout.py` | MOD | Helper drop + 5 sync→async + inlined `_do` closures + docstring (≈20 LOC delta) |
| `tests/test_phase_p5_5_session_reauth.py` | MOD | Helper drop + 4 sync→async + inlined `_login_then_probe` closure + docstring (≈35 LOC delta) |
| `tests/invariants/bespoke_run_helper_grandfathered.yml` | MOD | 3 `m1_entries:` rows DELETED in SINGLE BATCHED edit (F.5-slip lesson applied) |
| `tests/invariants/test_no_bespoke_run_helper.py` | MOD | `M1_CEILING` 8 → 5 + module docstring/comment update |
| `backend/scripts/jc_pollution_cluster_f3_proving_slice.py` | NEW | 13-row proving slice with Row 13 closure-schedule-lock end-to-end validation |
| `memory/sprints/JC_POLLUTION_CLUSTER_F3_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added BEFORE memo authored (F.3-ADVANCE-slip lesson applied) |
| `memory/jc_artifacts/FAILING_TEST_TRACKER.md` | UPDATED | FTT-024..026 entry: 10/14 → 13/14 polluters converted; ceiling trajectory updated |

**Files NOT touched**: any product code, any other test file, any other invariant file, any fixture file.

---

## §5 — Discipline notes

- **Scope honoured**: only the 3 F.3 files + invariant lock edits.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 13/13 GREEN stable across 2 consecutive runs** — HARD STOP at slice close.
- **Locked-area check** done before + after — clear.
- **No production code changes** — entirely test-side + invariant lock.
- **Pattern uniformity confirmed at 5 sub-sprints**: same Cluster-E mechanical conversion applied 5× without per-file customization (F.2, F.1, F.4, F.5, F.3 — total 13 polluter files closed via this exact pattern).
- **Sync-test preservation continues** to honour the Cluster-F.2 heuristic (2 of 16 tests stay sync; only async-touching tests convert).
- **Two prior discipline-slip lessons applied successfully**:
  - **F.5 slip lesson** (mid-flight YAML edit): used SINGLE batched search_replace + `yaml.safe_load` verify-before-slice — no slip occurred this sprint.
  - **F.3-ADVANCE slip lesson** (memo-before-DEV_PIPELINE): updated `DEV_PIPELINE.md §9` row BEFORE authoring this memo — verified pre-memo via grep.

---

## §6 — User-direction surface (HARD STOP)

Per the original dispatch directive: **HARD STOP & surface to user — no chaining into F.6**.

Cluster-F sub-sprint progress:
- ✅ F.2 (security_headers + cookie_hardening + health_composite) — 3 files closed
- ✅ F.1 (password_change + admin_force_reset) — 2 files closed
- ✅ F.4 (bounce_webhook + waitlist_reminder) — 2 files closed
- ✅ F.5 (microsoft_pkce + inbox_migration + admin_button_and_badge) — 3 files closed
- ✅ F.3 (csrf + session_timeout + session_reauth) — 3 files closed
- ⏳ F.6 (synisense_security) — 1 M2 outlier file pending; **HALT-and-surface pre-armed** per scope memo §6 for Shield-adjacency; user-confirmed TWO-DISPATCH approach (advance scan → fix sprint)

**13 of 14 polluters converted. 1 file remains.**

When F.6 closes (the final Cluster-F sub-sprint), the autosave file's pollution surface will be empty → FTT-024..026 auto-close. Then Cluster-G dispatch (5 M1 + 25 M2 + 1 A+D-preserved across ~12 distinct files surfaced by INVARIANT_NO_BESPOKE_RUN_HELPER baseline scan).

Awaiting next dispatch from user. Standing rules unchanged.

---

## §7 — Time-gate status at slice close

`Sat Jun 27 08:46:26 UTC 2026` at memo authoring. Steps 2 + 3 pre-auth window opens at `Sat Jun 27 09:12:00 UTC` — **~26 minutes from this surface**. Did NOT auto-fire during this dispatch (the window had not yet crossed at any check during F.3 execution). The user's standing pre-authorization remains active for the next work cycle.
