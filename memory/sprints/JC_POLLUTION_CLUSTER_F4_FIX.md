**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (sub-sprint F.4 dispatched per user direction 2026-06-27 · scope: 2 M1 polluter files (bounce_webhook + waitlist_reminder) — SendGrid surfaces · HARD STOP at proving-slice close · no chain into F.5 · closure-schedule lock end-to-end validated by NEW Row 11 against bespoke-run invariant)

# Sprint JC_POLLUTION_CLUSTER_F4_FIX — mechanical sync→async conversion on the SendGrid surfaces pair

**Status**: SHIPPED (test-file-only patches landed) · proving slice **11/11 GREEN** stable across 2 consecutive runs · regression-check ladder GREEN · HARD STOP at slice close · closure-schedule lock validated
**Date**: 2026-06-27
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_F1_FIX.md` (10/10 GREEN — F.1 admin-mutation pair); `sprints/JC_POLLUTION_CLUSTER_F2_FIX.md` (12/12 GREEN — F.2 3-file scale-up); `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (closure-schedule lock shipped as Step 4.5)
**Parallel sibling**: `sprints/INVARIANT_POLLUTER_INVENTORY.md` (READ-ONLY observability slice — shipped same dispatch, no scope collision)

---

## §0 — Outcome at a glance

| File | Sync tests | Conversions | Post-fix isolation |
|---|---:|---|---|
| `tests/test_phase_p5_7_5_bounce_webhook.py` | 5 | 4 async-converted + 1 stays sync (`_classify` pure-Python helper) | 5/5 PASS |
| `tests/test_phase_p5_7_waitlist_reminder.py` | 8 | 5 async-converted + 3 stay sync (DECLINE_BODY format · render_*_html · _self_check word-count) | 8/8 PASS |
| **Totals** | **13** | **9 async-converted + 4 stay sync** | **13/13 PASS** |

**Net**: Cluster-F.4 closes wrong-loop-binding at source for 2 more of 14 Cluster-F polluters. **7 of 14 polluters converted** across F.2 + F.1 + F.4. 7 remain across F.3 (csrf + session_timeout + session_reauth) · F.5 (microsoft_pkce + inbox_migration + admin_button_and_badge) · F.6 (synisense_security M2 outlier).

**Closure-schedule lock validated end-to-end** (NEW vs F.1/F.2 slices): Row 11 confirms the bespoke-run invariant PASSES after the YAML edits — `m1_entries:` lost 2 entries for the F.4 files, `M1_CEILING` ratcheted 13 → 11, the drift detector did not fire, the count-ceiling did not fire, the catcher confirms both F.4 files no longer carry the M1 pattern. The closure-schedule lock works.

**Sync-test preservation honoured per Cluster-F.2 heuristic**:
- bounce_webhook's `test_p5_7_5_classify_buckets_correctly` — calls only the pure-Python `_classify(...)` helper; no asyncio surface.
- waitlist_reminder's `test_p5_7_6_send_decline_with_waitlist_url_switches_body` — only Python format-string contract on DECLINE_BODY / DECLINE_BODY_WITH_WAITLIST.
- waitlist_reminder's `test_p5_7_html_escapes_first_name_and_magic_link` — only HTML rendering via render_*_html; no asyncio.
- waitlist_reminder's `test_p5_7_self_check_passes` — only word-counting on `_self_check()` output.

4 of 13 tests preserved sync; 9 converted. Pattern uniformity continues.

---

## §1 — Patches applied (test-file-only, locked-area cleared)

### §1.1 — `tests/test_phase_p5_7_5_bounce_webhook.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 21-22 pre-fix per scope memo §0)
- Converted 4 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_p5_7_5_bounce_event_writes_failed_bucket_on_application_row`
  - `test_p5_7_5_delivered_event_writes_delivered_bucket`
  - `test_p5_7_5_unknown_recipient_does_not_create_row`
  - `test_p5_7_5_invalid_body_returns_400`
- Each test's inner `_do()` async closure inlined directly into the test body; the `_run(_do())` invocation replaced by direct `async with AsyncClient(...) as ac: ...` block.
- `test_p5_7_5_classify_buckets_correctly` STAYS SYNC — pure-Python helper call, documented in its docstring.
- Updated module docstring to cite Cluster-F.4 (2026-06-27) + root cause.

### §1.2 — `tests/test_phase_p5_7_waitlist_reminder.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 36-37 pre-fix per scope memo §0)
- Converted 5 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_p5_7_6_waitlist_accepts_valid_email`
  - `test_p5_7_6_waitlist_idempotent_on_repeat_email`
  - `test_p5_7_6_waitlist_rejects_malformed_email`
  - `test_p5_7_6_waitlist_correlates_source_application_id`
  - `test_p5_7_4_reminder_sweep_idempotent` (calls `run_expiry_reminder_sweep()` — natively async)
- Each `_run(_do())` invocation replaced by inlining the `_do()` body; reminder-sweep test directly awaits the imported async function.
- 3 tests STAY SYNC (documented in their docstrings as pure-Python contracts with no asyncio surface).
- Updated module docstring.

### §1.3 — Closure-schedule lock edits

- `tests/invariants/bespoke_run_helper_grandfathered.yml` — 2 `m1_entries:` rows DELETED (one for bounce_webhook, one for waitlist_reminder)
- `tests/invariants/test_no_bespoke_run_helper.py` — `M1_CEILING` ratcheted from `13` → `11` to reflect the new baseline post-F.4 closure
- Module docstring + module comment updated to cite the F.4 closure

### §1.4 — Locked-area re-confirmation

| Area | Touched? |
|---|---|
| Shield surfaces | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| SendGrid SEND code path (`services/sendgrid_*.py` etc.) | NO (the converted tests exercise webhook INGESTION + waitlist endpoint + HTML rendering + word-count contracts; the send code is NOT touched) |
| Product code | NO |

Cleared. All edits are test-side or invariant-side (the invariant edit is the closure-schedule lock; no fix-authority change).

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_f4_proving_slice.py`)

```
============================================================================
P5.7-Cluster-F.4 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
============================================================================
  Row  1  GREEN  tests/test_phase_p5_7_5_bounce_webhook.py in isolation post-fix (5 passed)
            5 passed, 21 warnings in 4.39s
  Row  2  GREEN  tests/test_phase_p5_7_waitlist_reminder.py in isolation post-fix (8 passed)
            8 passed, 21 warnings in 4.20s
  Row  3  GREEN  bounce_webhook + autosave (B.2 polluter pair, post-fix)
            8 passed, 21 warnings in 4.94s
  Row  4  GREEN  waitlist_reminder + autosave (B.2 polluter pair, post-fix)
            11 passed, 21 warnings in 5.14s
  Row  5  GREEN  Combined F.4 (bounce + waitlist together) — 13 PASS expected
            13 passed, 21 warnings in 4.41s
  Row  6  GREEN  Combined F.4 + autosave — 16 PASS expected
            16 passed, 21 warnings in 5.44s
  Row  7  GREEN  bounce_webhook + phase4_2 (A+D defensive)
            13 passed, 21 warnings in 5.29s
  Row  8  GREEN  waitlist_reminder + p5_10 (Cluster-E defensive)
            13 passed, 21 warnings in 4.38s
  Row  9  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 6's full stdout
  Row 10  GREEN  source-assertion: no _run / get_event_loop.run_until_complete
            both F.4 files clean
  Row 11  GREEN  bespoke-run invariant PASSES (F.4 entries removed, files clean)
            3 passed, 21 warnings in 5.87s
============================================================================
RESULT  11/11 GREEN
============================================================================
```

**Key signals**:
- **Rows 3-4**: each F.4 file paired with autosave (the B.2 polluted target) → all PASS. Confirms the wrong-loop-binding is closed for these 2 specific polluter→polluted pairs.
- **Row 6**: combined F.4 + autosave = 16/16 PASS. The pollution scope previously reported for these 2 polluters is now empty.
- **Rows 7-8**: defensive checks confirm A+D's (phase4_2) and Cluster-E's (p5_10) closures aren't regressed.
- **Row 9**: zero `Future attached to a different loop` occurrences — canonical signature silenced.
- **Row 10**: source-assertion confirms no `_run` helper or `asyncio.get_event_loop().run_until_complete` line remains.
- **Row 11 (NEW)**: bespoke-run invariant runs after the YAML edits — catcher + drift detector + count-ceiling ALL PASS (3 tests). End-to-end validation of the closure-schedule lock: removing the YAML entries + ratcheting the ceiling didn't break the invariant; the invariant correctly recognizes the converted files no longer carry the M1 pattern.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **92 pass / 7 pre-existing failures** unchanged | Same pattern as post-Step 4+4.5 state. NOT regressions from F.4. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via `test_phase4_4_dual_mount_smoke.py` 37/37 PASS — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` in lockstep |
| JC-TM email path smoke | yes | **N/A** | The converted tests exercise webhook INGESTION + waitlist endpoint + HTML rendering + word-count contracts; the SendGrid SEND code path is NOT touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Cluster's own proving slice | yes (11/11) | **11/11 GREEN** stable across 2 runs |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_phase_p5_7_5_bounce_webhook.py` | MOD | Helper drop + 4 sync→async + inlined `_do` closures + docstring (≈30 LOC delta) |
| `tests/test_phase_p5_7_waitlist_reminder.py` | MOD | Helper drop + 5 sync→async + inlined `_do` closures + docstring (≈40 LOC delta) |
| `tests/invariants/bespoke_run_helper_grandfathered.yml` | MOD | 2 `m1_entries:` rows DELETED for the converted files |
| `tests/invariants/test_no_bespoke_run_helper.py` | MOD | `M1_CEILING` 13 → 11 (ratchet-down lock) + module docstring/comment update |
| `backend/scripts/jc_pollution_cluster_f4_proving_slice.py` | NEW | 11-row proving slice with NEW Row 11 (closure-schedule-lock end-to-end validation) |
| `memory/sprints/JC_POLLUTION_CLUSTER_F4_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added |
| `memory/jc_artifacts/FAILING_TEST_TRACKER.md` | UPDATED | FTT-024..026 entry: 5/14 → 7/14 polluters converted; mentions closure-schedule lock + Cluster-G discovery |

**Files NOT touched**: any product code, any other test file, any other invariant file (thin-assertions is untouched in this sprint), any fixture file, any pptx/schema file.

---

## §5 — Discipline notes

- **Scope honoured**: only the 2 F.4 files + invariant lock edits.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 11/11 GREEN stable across 2 consecutive runs** — HARD STOP at slice close.
- **Locked-area check** done before and after — clear.
- **No production code changes** — entirely test-side + invariant lock.
- **Pattern uniformity**: same mechanical conversion applied 3rd time without per-file customization.
- **Sync-test preservation continues** to honour the Cluster-F.2 heuristic (4 of 13 tests stay sync; only async-touching tests convert).
- **Closure-schedule lock works**: ratcheting M1_CEILING down from 13 → 11 + removing YAML entries + invariant still PASSES = lock is genuine.
- **Discovery findings unchanged**: the Cluster-G (post-F) bucket from the 2026-06-27 invariant baseline scan remains unchanged at 5 M1 + 7 M2 files (Cluster-F.4 didn't surface anything new beyond what was already in scope).

---

## §6 — User-direction surface (HARD STOP)

Per the original dispatch directive: **HARD STOP & surface to user — no chaining into F.5**.

Cluster-F sub-sprint progress:
- ✅ F.2 (security_headers + cookie_hardening + health_composite) — 3 files closed
- ✅ F.1 (password_change + admin_force_reset) — 2 files closed
- ✅ F.4 (bounce_webhook + waitlist_reminder) — 2 files closed
- ⏳ F.5 (microsoft_pkce + inbox_migration + admin_button_and_badge) — 3 files pending
- ⏳ F.3 (csrf + session_timeout + session_reauth) — 3 files pending; medium risk per scope memo §1.1
- ⏳ F.6 (synisense_security) — 1 M2 outlier file pending; HALT-and-surface pre-armed per scope memo §6 for Shield-adjacency

7 of 14 polluters converted. 7 remain across 3 sub-sprints.

Awaiting next dispatch from user. Standing rules unchanged.
