**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (sub-sprint F.5 dispatched per user direction 2026-06-27 · scope: 3 M1 polluter files (microsoft_pkce + inbox_migration + admin_button_and_badge) — largest test-count group · HARD STOP at proving-slice close · no chain into F.3 · closure-schedule lock end-to-end validated by Row 13 against bespoke-run invariant)

# Sprint JC_POLLUTION_CLUSTER_F5_FIX — mechanical sync→async conversion on the largest Cluster-F sub-sprint

**Status**: SHIPPED (test-file-only patches landed) · proving slice **13/13 GREEN** stable across 2 consecutive runs · regression-check ladder GREEN · HARD STOP at slice close · closure-schedule lock validated
**Date**: 2026-06-27
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_F4_FIX.md` (11/11 GREEN — F.4 SendGrid pair); `sprints/JC_POLLUTION_CLUSTER_F1_FIX.md` (10/10 GREEN — F.1 admin-mutation pair); `sprints/JC_POLLUTION_CLUSTER_F2_FIX.md` (12/12 GREEN — F.2 3-file scale-up); `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (closure-schedule lock)

---

## §0 — Outcome at a glance

| File | Sync tests | Conversions | Post-fix isolation |
|---|---:|---|---|
| `tests/test_phase_p2_a2_microsoft_pkce.py` | 7 | 6 async-converted + 1 stays sync (pure-function `_ms_pkce_verifier`/`_ms_pkce_challenge` round-trip) | 7/7 PASS |
| `tests/test_phase_p5_8_inbox_migration.py` | 7 | 7 async-converted + 0 sync | 7/7 PASS (1 may skip without SENDGRID_INBOUND_AUTH env) |
| `tests/test_phase_p5_9_admin_button_and_badge.py` | 4 | 3 async-converted + 1 stays sync (pure-dict-mutation cache-bust contract) | 4/4 PASS |
| **Totals** | **18** | **16 async-converted + 2 stay sync** | **18/18 PASS** |

**Net**: Cluster-F.5 closes wrong-loop-binding at source for 3 more of 14 Cluster-F polluters. **10 of 14 polluters converted** across F.2 + F.1 + F.4 + F.5. 4 remain across F.3 (csrf + session_timeout + session_reauth) + F.6 (synisense_security M2 outlier).

**Filename verification (per F.1 audit-trail discipline)**: user dispatch referenced `test_phase_p4_3_microsoft_pkce.py` / `test_phase_p2_c1_inbox_migration.py` / `test_phase_p2_c2_admin_button_and_badge.py` as approximate filenames with explicit "(or similar — verify exact filename on disk)" hint. The actual on-disk filenames are `test_phase_p2_a2_microsoft_pkce.py` / `test_phase_p5_8_inbox_migration.py` / `test_phase_p5_9_admin_button_and_badge.py` per scope memo §0. Documented for the audit trail.

**Largest sub-sprint by test count (18)** validates the mechanical pattern scales without per-file customization. Same Cluster-E shape applied 3×.

---

## §1 — Patches applied (test-file-only, locked-area cleared)

### §1.1 — `tests/test_phase_p2_a2_microsoft_pkce.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 72-74 pre-fix)
- Kept the existing `_async_get(...)` helper as `async def` (it was already async; just removed its `_run` callers)
- Kept the existing autouse `_clean_pkce_collection` fixture (sync; cleans `oauth_pkce_verifiers` collection per test — no asyncio touch)
- Converted 6 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_a2_start_returns_code_challenge_S256` (parametrized)
  - `test_a2_start_response_shape_unchanged`
  - `test_a2_probe_returns_minimal_shape`
  - `test_a2_pkce_verifier_persisted_in_mongo`
  - `test_a2_exchange_code_sends_code_verifier`
  - `test_a2_callback_rejects_when_verifier_missing`
- Each test's `_run(_async_get(...))` became `await _async_get(...)`; `_run(ao._ms_exchange_code(...))` became `await ao._ms_exchange_code(...)`.
- `test_a2_pkce_verifier_helpers_round_trip` STAYS SYNC — only calls pure-Python `_ms_pkce_verifier(...)` + `_ms_pkce_challenge(...)`; no asyncio. Documented in docstring.

### §1.2 — `tests/test_phase_p5_8_inbox_migration.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 40-41 pre-fix)
- Converted 7 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_p5_8_1_sendgrid_inbound_rejects_no_auth`
  - `test_p5_8_1_sendgrid_inbound_rejects_wrong_auth` (still uses `pytest.skip` when env missing)
  - `test_p5_8_1_inbound_provider_flag_disables_sendgrid` (preserves `os.environ` mutation inside try/finally)
  - `test_p5_8_2_capture_for_admin_inbox_writes_row`
  - `test_p5_8_2_list_requires_admin`
  - `test_p5_8_2_detail_404_when_missing`
  - `test_p5_8_2_capture_caps_body_at_64kb_text`
- Inner `_do()` closures inlined directly; `await capture_for_admin_inbox(...)` in place of `_run(_do())`.

### §1.3 — `tests/test_phase_p5_9_admin_button_and_badge.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 23-24 pre-fix)
- Converted 3 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_p5_9_2_unread_count_requires_super_admin`
  - `test_p5_9_2_capture_updates_count_after_cache_bust`
  - `test_p5_9_2_endpoint_route_registered`
- `test_p5_9_2_cache_busted_when_status_flips_to_read` STAYS SYNC — only mutates `_unread_count_cache` dict + does direct pymongo writes; no HTTP, no async function calls. Documented in docstring.

### §1.4 — Closure-schedule lock edits

- `tests/invariants/bespoke_run_helper_grandfathered.yml` — 3 `m1_entries:` rows DELETED (microsoft_pkce + inbox_migration + admin_button_and_badge)
- `tests/invariants/test_no_bespoke_run_helper.py` — `M1_CEILING` ratcheted from `11` → `8` to reflect the new baseline post-F.5 closure (trajectory: 13 → 11 (F.4) → 8 (F.5); next ratchet 8 → 5 expected after F.3 closes 3 more M1 files)

### §1.5 — Mid-flight YAML-edit slip + self-correction (discipline note)

During the YAML edits an incorrect `mcp_search_replace` `new_str` briefly re-added the already-converted F.4 entries (`bounce_webhook` + `waitlist_reminder`) while removing the F.5 entries. YAML went 11 → 10 instead of the intended 11 → 8 (3-entry removal + 0 additions). Caught the slip immediately by re-querying YAML state post-edit BEFORE running the proving slice; surgical follow-up `mcp_search_replace` removed the 2 re-added entries; final state matches the intended 11 → 8 trajectory.

**Standing lesson**: sequential `mcp_search_replace` calls on the same file can race with copy-paste of `new_str` blocks. Future sprints should either (a) batch all YAML edits into one tool call, or (b) verify-after-each-edit with a `yaml.safe_load` check before proceeding. The drift detector would have caught the re-added entries at proving-slice time (Row 13's invariant run would have failed because the F.4 files no longer carry the M1 pattern), but it's better to catch slips at edit time than at slice time. Lesson banked.

### §1.6 — Locked-area re-confirmation

| Area | Touched? |
|---|---|
| Shield surfaces | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| SendGrid SEND code path | NO (the converted tests exercise INGESTION + endpoint contracts; the send code is NOT touched) |
| OAuth provider live endpoints (Microsoft) | NO (the converted tests use `unittest.mock.patch` to neutralize live MS calls — pattern unchanged from pre-conversion) |
| Product code | NO |

Cleared. All edits are test-side or invariant-side (the invariant edit is the closure-schedule lock).

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_f5_proving_slice.py`)

```
============================================================================
P5.7-Cluster-F.5 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
============================================================================
  Row  1  GREEN  tests/test_phase_p2_a2_microsoft_pkce.py in isolation post-fix
            7 passed, 21 warnings in 4.29s
  Row  2  GREEN  tests/test_phase_p5_8_inbox_migration.py in isolation post-fix
            7 passed, 21 warnings in 4.28s
  Row  3  GREEN  tests/test_phase_p5_9_admin_button_and_badge.py in isolation post-fix
            4 passed, 21 warnings in 4.28s
  Row  4  GREEN  microsoft_pkce + autosave (B.2 polluter pair, post-fix)
            10 passed, 21 warnings in 5.06s
  Row  5  GREEN  inbox_migration + autosave (B.2 polluter pair, post-fix)
            10 passed, 21 warnings in 5.22s
  Row  6  GREEN  admin_button_and_badge + autosave (B.2 polluter pair, post-fix)
            7 passed, 21 warnings in 5.08s
  Row  7  GREEN  Combined F.5 (all 3 files together) — 18 PASS expected
            18 passed, 21 warnings in 4.56s
  Row  8  GREEN  Combined F.5 + autosave — 21 PASS expected
            21 passed, 21 warnings in 5.94s
  Row  9  GREEN  microsoft_pkce + phase4_2 (A+D defensive)
            15 passed, 21 warnings in 5.41s
  Row 10  GREEN  inbox_migration + p5_10 (Cluster-E defensive)
            12 passed, 21 warnings in 4.54s
  Row 11  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 8's full stdout
  Row 12  GREEN  source-assertion: no _run / get_event_loop.run_until_complete
            all 3 F.5 files clean
  Row 13  GREEN  bespoke-run invariant PASSES (F.5 entries removed + M1_CEILING=8)
            3 passed, 21 warnings in 5.86s
============================================================================
RESULT  13/13 GREEN
============================================================================
```

**Key signals**:
- **Rows 4-6**: each F.5 file paired with autosave (the B.2 polluted target) → all PASS. 3 more polluter→polluted pairs closed.
- **Row 8**: combined F.5 + autosave = 21/21 PASS (18 F.5 + 3 autosave). The pollution scope for these 3 polluters is now empty.
- **Rows 9-10**: defensive checks confirm A+D's (phase4_2) and Cluster-E's (p5_10) closures aren't regressed.
- **Row 11**: zero `Future attached to a different loop` occurrences — canonical signature silenced.
- **Row 12**: source-assertion confirms no `_run` / `get_event_loop.run_until_complete` remains in any of the 3 files.
- **Row 13 (closure-schedule lock validation)**: bespoke-run invariant runs after YAML edits + ceiling ratchet — catcher + drift detector + count-ceiling ALL PASS (3 tests). End-to-end validation: removing the YAML entries + ratcheting M1_CEILING 11→8 didn't break the invariant; the invariant correctly recognizes the converted files no longer carry the M1 pattern.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **92 pass / 7 pre-existing failures** unchanged | Same pattern as post-F.4 state. NOT regressions from F.5. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via `test_phase4_4_dual_mount_smoke.py` 37/37 PASS — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` in lockstep |
| JC-TM email path smoke | yes | **N/A** | The converted tests exercise OAuth PKCE + inbound webhook auth + admin inbox capture + unread-count badge contracts; no SendGrid SEND code touched. |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Cluster's own proving slice | yes (13/13) | **13/13 GREEN** stable across 2 runs |
| Inventory slice sibling re-run | yes | **3/3 GREEN** · M1=8/8 ceiling, M2=28/28 ceiling, zero drift |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_phase_p2_a2_microsoft_pkce.py` | MOD | Helper drop + 6 sync→async + 1 sync preserved + docstring (≈25 LOC delta) |
| `tests/test_phase_p5_8_inbox_migration.py` | MOD | Helper drop + 7 sync→async + inlined `_do` closures + docstring (≈40 LOC delta) |
| `tests/test_phase_p5_9_admin_button_and_badge.py` | MOD | Helper drop + 3 sync→async + 1 sync preserved + docstring (≈18 LOC delta) |
| `tests/invariants/bespoke_run_helper_grandfathered.yml` | MOD | 3 `m1_entries:` rows DELETED (post-slip-correction final state 11 → 8) |
| `tests/invariants/test_no_bespoke_run_helper.py` | MOD | `M1_CEILING` 11 → 8 + module docstring/comment update |
| `backend/scripts/jc_pollution_cluster_f5_proving_slice.py` | NEW | 13-row proving slice with Row 13 closure-schedule-lock end-to-end validation |
| `memory/sprints/JC_POLLUTION_CLUSTER_F5_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added |
| `memory/jc_artifacts/FAILING_TEST_TRACKER.md` | UPDATED | FTT-024..026 entry: 7/14 → 10/14 polluters converted; updated ceiling trajectory |

**Files NOT touched**: any product code, any other test file, any other invariant file, any fixture file.

---

## §5 — Discipline notes

- **Scope honoured**: only the 3 F.5 files + invariant lock edits.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 13/13 GREEN stable across 2 consecutive runs** — HARD STOP at slice close.
- **Locked-area check** done before and after — clear.
- **No production code changes** — entirely test-side + invariant lock.
- **Pattern uniformity confirmed at the largest sub-sprint scale**: same Cluster-E mechanical conversion applied 4th time without per-file customization.
- **Sync-test preservation continues** to honour the Cluster-F.2 heuristic (2 of 18 tests stay sync; only async-touching tests convert).
- **Filename-verification audit-trail discipline applied** (F.1 lesson) — user's approximate filenames documented + corrected.
- **Mid-flight YAML-edit slip surfaced + corrected** (§1.5) — banked as standing lesson for future sprints.

---

## §6 — User-direction surface (HARD STOP)

Per the original dispatch directive: **HARD STOP & surface to user — no chaining into F.3**.

Cluster-F sub-sprint progress:
- ✅ F.2 (security_headers + cookie_hardening + health_composite) — 3 files closed
- ✅ F.1 (password_change + admin_force_reset) — 2 files closed
- ✅ F.4 (bounce_webhook + waitlist_reminder) — 2 files closed
- ✅ F.5 (microsoft_pkce + inbox_migration + admin_button_and_badge) — 3 files closed
- ⏳ F.3 (csrf + session_timeout + session_reauth) — 3 files pending; medium risk per scope memo §1.1
- ⏳ F.6 (synisense_security) — 1 M2 outlier file pending; HALT-and-surface pre-armed per scope memo §6 for Shield-adjacency

**10 of 14 polluters converted. 4 remain across 2 sub-sprints.**

After F.6 closes (the final Cluster-F sub-sprint), the autosave file's pollution surface will be empty → FTT-024..026 auto-close.

After that: Cluster-G READ-ONLY scope memo dispatch (5 M1 + 7 M2 files discovered by the 2026-06-27 invariant baseline scan; see `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md §3`).

Awaiting next dispatch from user. Standing rules unchanged.
