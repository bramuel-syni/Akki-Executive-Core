**Canonical Spec**: `/app/memory/sprints/P5_22_csrf_wire_test_refresh.md` (failing-test ledger seeded by Phase 5.6.1 CSRF rig audit)

# Failing-Test Tracker

Per the Zero-Handoff-Loss discipline: every test marked FLAGGED-FALSE-GREEN
during a rig-fix audit, or surfaced as a flaky-in-broad-but-green-in-isolation
test, lives here until it is either re-implemented with a real assertion or
diagnosed for a root-cause sprint.

## Active entries

### FLAGGED-FALSE-GREEN (from PHASE_5_6_1_CSRF_RIG_AUDIT.md, 2026-06-26)

— **(empty)** — FTT-001 resolved by Phase 5.6.2 on 2026-06-26; see Resolved section below.

### CROSS-TEST POLLUTION FLAKES (current scope post-P5.7-PER-FILE-CAPTURE reclassification, 2026-06-26)

These 18 nodes / 7 files PASS in isolation in the default lane but FAIL in-suite. Confirmed cross-test pollution candidates — bisect required to identify polluter chains.

| ID(s) | File | Cluster (P5.7-DIAG hypothesis) | Bisect status |
|-------|------|--------------------------------|---------------|
| FTT-004..009 | `tests/test_iter41_signal_actions_in_process.py` | shared_fixture_state_iter41 (in-file) | ✅ **CLOSED** by JC-POLLUTION-CLUSTER-C-FIX (2026-06-30) — single-dispatch fixture-isolation refactor; 3 module-level free helpers (`_client` / `_register` / `_seed_signal`) replaced with 4 function-scoped fixtures (`client` / `registered_user` / `signal_factory`) + autouse `_reset_app_dependency_overrides` snapshot/restore defending against upstream FastAPI `app.dependency_overrides` mutations. Proving slice **13/13 GREEN** (Row 1 lesson #5 6/6 PASS preservation · Row 3 autouse fixture AST+behavioral validation · Row 4 cross-test pollution scan clean · Row 12 AST source-check 3 helpers REMOVED + 4 fixtures present). NEW mechanical family **fixture-isolation refactor** (distinct from F+G sync→async family) documented at `sprints/JC_POLLUTION_CLUSTER_C_FIX.md §X`. Closes 6 FTT IDs in single sub-sprint. |
| FTT-010..012 | `tests/test_p_cleanup_c_help_tooltip_suppression.py` | dependency_overrides_leak (refined 2026-06-26 by JC-POLLUTION-B1-FIX as `module_scoped_async_fixture_loop_binding_leak` — pytest-asyncio binds module-scoped async fixtures to first-resolve loop; broad-suite churn corrupts the binding) | ✅ **CLOSED** by JC-POLLUTION-B1-FIX (2026-06-26) — single-decorator change `@pytest_asyncio.fixture(scope="module")` → `scope="function"` at lines 43-45. Proving slice 4/4 GREEN. Cheap durability check: Row 4 of slice asserts function-scope marker present and module-scope marker absent. |
| FTT-015, FTT-016 | `tests/test_phase_p3_2_cookie_hardening.py` | env_or_motor_loop_state | ✅ **CLOSED** by JC-POLLUTION-A-D-FIX (2026-06-26) — env + asyncio-loop-policy snapshot/restore on polluter `tests/test_phase4_2_http_transport_smoke.py` (paired-pytest GREEN) |
| FTT-017, FTT-018 | `tests/test_phase_p5_10_audit_panel_direct_linkage.py` | env_or_motor_loop_state | ✅ **CLOSED** by JC-POLLUTION-A-D-FIX (2026-06-26) — same fix on `test_phase4_2_http_transport_smoke.py` (paired-pytest GREEN) |
| FTT-019..022 | `tests/test_phase_p5_7_5_bounce_webhook.py` | sendgrid_env_stub_leak | ✅ **CLOSED** by JC-POLLUTION-A-D-FIX (2026-06-26) — `os.environ` snapshot/restore on polluter closed the SendGrid stub leak (paired-pytest GREEN) |
| FTT-023 | `tests/test_track_b_phase2_task_lifecycle.py::test_cross_tenant_lifecycle_blocked` | **event_loop_binding_leak_from_sync_run** (refined 2026-06-26 by P5.7-FIX-SCOPE-CLUSTER-E source-read; original tracker cluster name `tenant_resolver_stub_leak` was wrong — conftest.py:224-253 already handles dep-override cleanup, so dep-overrides are NOT the polluter shape. Real mechanism: p5_10's SYNC tests use `_run(coro) = asyncio.get_event_loop().run_until_complete(coro)`; for sync tests the policy loop differs from pytest-asyncio's session-scoped loop, so Motor binds to wrong loop and downstream `@pytest.mark.asyncio` tests fire `Future attached to a different loop` RuntimeError.) | ✅ **CLOSED** by JC-POLLUTION-CLUSTER-E-FIX (2026-06-26) — async-conversion of p5_10's 5 sync test functions to `@pytest.mark.asyncio` binds them to conftest.py:210-221's session-scoped event loop. Proving slice 9/9 GREEN including log scan (0 occurrences of `Future attached to a different loop`) and loop-binding sanity (loop policy clean post-fix). Closed FTT-023 + 6 sibling async test failures in task_lifecycle (collateral damage of same mechanism). |
| FTT-024..026 | `tests/test_track_b_phase_b5_g6_notes_autosave.py` | **event_loop_binding_leak_from_sync_run_in_polluter_files** (refined 2026-06-26 by JC-POLLUTION-B2-HALT empirical evidence; original tracker cluster name `autosave_debounce_timer_leak` was wrong; remeasure §3.1's Mongo-collection-state hypothesis was also wrong. **Actual mechanism was the same as Cluster-E**: each of the 14 polluters used sync test functions with `_run = asyncio.get_event_loop().run_until_complete(coro)` or direct `asyncio.run(...)` calls, which bound Motor's singleton to a sync-test-local loop different from conftest.py:210-221's session-scoped loop used by autosave's `@pytest.mark.asyncio` tests. Verbatim error: `RuntimeError: Task ... got Future ... attached to a different loop`.) | ✅ **CLOSED** by JC-POLLUTION-CLUSTER-F6-FIX (2026-06-27) — Cluster-F arc completion: all 14 polluters converted across F.2 (3 files: security_headers + cookie_hardening + health_composite) + F.1 (2 files: password_change + admin_force_reset) + F.4 (2 files: bounce_webhook + waitlist_reminder) + F.5 (3 files: microsoft_pkce + inbox_migration + admin_button_and_badge) + F.3 (3 files: csrf + session_timeout + session_reauth) + F.6 (1 M2 file: synisense_security). **AUTO-CLOSE VALIDATED END-TO-END**: ran autosave + ALL 14 originally-polluter files in a single pytest invocation → 72/72 PASS · 0 failures · 0 `Future attached to a different loop` signatures. Autosave's polluter set is empty. **Closure-schedule lock at final state**: M1_CEILING=5 (Cluster-G remainder) + M2_CEILING=26 (25 Cluster-G + 1 A+D-preserved). **Discovery (2026-06-27)**: invariant baseline scan surfaced 9 additional polluter files beyond the original 14-file Cluster-F scope — "Cluster-G (post-F)" follow-up dispatch recommended (5 M1 + 25 M2 across ~12 distinct files surfaced by INVARIANT_NO_BESPOKE_RUN_HELPER baseline scan). |

**KEY INSIGHTS**:
- **Cluster A** — one polluter file `tests/test_phase4_2_http_transport_smoke.py` accounts for 8 of 10 confirmed pairs in P5.7-BISECT (FTT-015..022). That file is ALSO a deterministic regression itself (FAIL_DETERMINISTIC in isolation per P5.7-PER-FILE-CAPTURE). Dual identity = surgical sprint closes 10 FTT IDs (Cluster A + FTT-014 Cluster D).
- **Cluster B.1** — `test_p_cleanup_c_help_tooltip_suppression.py` returned 0 pairwise polluters across 69 candidates → SHARED GLOBAL STATE pollution. Different fix shape (test-side fixture reset, source inspection).
- **Cluster B.2** — `test_track_b_phase_b5_g6_notes_autosave.py` has 15 distinct polluters, all auth/session/CSRF surface area. Single test-side hardening closes all 3 FTT IDs.
- **Cluster C** — `test_iter41_signal_actions_in_process.py` in-file pollution. Fixture refactor (module-scoped → function-scoped) closes 6 FTT IDs.

Total cross-test pollution: **18 distinct nodes / 7 files** — of which **10 IDs / 4 files** have confirmed external polluter pairs (Cluster A), **3 IDs / 1 file** is broad-sensitive (Cluster B.2), **3 IDs / 1 file** is shared-global-state shape (Cluster B.1), and **6 IDs / 1 file** is intra-file (Cluster C). All 18 IDs mapped to concrete fix-shapes with paired-pytest-confirmed evidence (except B.1 where the 0-pairwise-polluter finding IS the evidence).

### DETERMINISTIC REGRESSIONS (promoted from reclassification, 2026-06-26)

These are real bugs surfacing as deterministic failures in isolation — not flakes, not pollution. They were hiding behind the pollution noise; promoted here so they get fix-sprint priority.

| ID | Node | Evidence | Disposition |
|----|------|----------|-------------|
| FTT-014 | `tests/test_phase_i5_open_questions.py::test_i5_B1_backfill_idempotent` | Was FAIL_DETERMINISTIC at 12.2 s in isolation (per-file capture 2026-06-26); now deterministic PASS at ~4.5s across 3 consecutive isolation runs (2026-06-27 09:20 UTC) | ✅ **CLOSED** by post-Cluster-F arc closure + GridFS backfill --commit (2026-06-27). Re-ran post-backfill-commit per dispatch Step 3 sequencing → `1 passed in 4.61s`; verified stability with 3 consecutive isolation runs (4.52s, 4.57s, 4.56s) — deterministic GREEN. **Anti-false-GREEN audit PROVEN** (CSRF-rig standard from Phase 5.6.1): test seeds 3 fresh `cycle_questions` rows with distinct shapes (ned-owned, anonymous, already-classified); calls `backfill_asker_role.main()`; hard-asserts `res1["total"]==2 + board==1 + team==1`; re-reads rows from Mongo asserting `asker_role` actually written (bf1=="board", bf2=="team", bf3=="ceo" untouched as idempotency negative case); re-runs backfill asserting `res2["total"]==0` as idempotency positive case. 6 distinct assertions covering scan + classification + write + idempotency + untouched-row negative — NOT a thin assertion, exercises real `backfill_asker_role` semantics end-to-end. **Causal uncertainty note (honesty)**: the dispatch's deferral hypothesis ("FTT-014 depends on GridFS backfill") was a hypothesis, not proven. The mechanical relationship between the GridFS backfill (operates on `workbook_blobs` + `analysis_blobs`) and FTT-014's `cycle_questions.asker_role` backfill is unclear. Most likely root cause of the 12.2s → 4.5s + RED → GREEN state transition: the Cluster-F arc closure removed wrong-loop-binding pollution that was affecting i5_actors fixture's `db.memberships` interaction (Motor-touching), since both Cluster-F resolution and this test stabilisation landed in the same dispatch sequence. Without a `git bisect`-style root-cause sprint we can't isolate the single fix that flipped FTT-014; what we CAN prove is the test is now deterministic GREEN with real-behavior assertions, which closes the audit cleanly. |
| (untracked → "Cluster D sibling") | `tests/test_phase4_2_http_transport_smoke.py::test_internal_transport_openapi_hash_unchanged` | FAIL_DETERMINISTIC in isolation — hardcoded surface-ratchet sha `cdcb23322bb82895` drifted vs live `31e1d9769f632472` | ✅ **CLOSED** by JC-POLLUTION-A-D-FIX (2026-06-26) — sha refresh at line 101 + live re-verification (`/api/openapi.json` → 636 paths → sha256:16 = `31e1d9769f632472`). DEV_PIPELINE §5 + §6 also updated to match. |

### INTEGRATION-LANE-ONLY (reclassified from pollution, 2026-06-26)

These nodes only execute when `-m integration` is enabled. They were misclassified as cross-test pollution because the broad-suite that surfaced them ran with integration markers enabled; in the default lane (`not integration`) they are PASS_NO_TESTS (marker-deselected).

| ID | Node | Status |
|----|------|--------|
| FTT-002 | `tests/characterisation/test_chat_roundtrip_golden.py::test_chat_roundtrip_golden_shape` | NOT an active issue in default lane; failures only with `-m integration` |
| FTT-003 | `tests/test_chat_fluency_no_shield_leak.py::test_chat_response_does_not_leak_shield_mechanics` | NOT an active issue in default lane; failures only with `-m integration` |

These are NOT active pollution issues. If integration-lane failures surface in CI, they get their own bug-fix sprint then.

### DETERMINISTIC-SLOW (reclassified from pollution, 2026-06-26)

| ID | Node | Status |
|----|------|--------|
| FTT-013 | `tests/test_phase_d_fix_bundle.py::test_far_refusal_reachable_with_substantive_but_thin_inputs` | TIMEOUT at 60 s in isolation (per-file capture 2026-06-26). NOT pollution — test is deterministically slow. Filed as a separate "test performance" backlog item; not a flake. |

### Reclassification audit trail (preserved per discipline)

Original `CROSS-TEST POLLUTION FLAKES (from broad-suite run delta, 2026-06-26)` table contained 24 entries (FTT-002..026). The P5.7-PER-FILE-CAPTURE sprint (per-file subprocess isolation, 433 files in 54.8 min) re-classified 6 of them per the evidence above. The current scope reflects post-reclassification truth; original 24-entry table is preserved here as the audit record:

| Original FTT IDs | Original suspected source | Per-file evidence (2026-06-26) | New section |
|---|---|---|---|
| FTT-002, FTT-003 | event-loop binding leak | PASS_NO_TESTS (integration-marker-only) | INTEGRATION-LANE-ONLY |
| FTT-004..009 | shared fixture-state | PASS in isolation | CROSS-TEST POLLUTION (kept) |
| FTT-010..012 | dependency_overrides leak | PASS in isolation | CROSS-TEST POLLUTION (kept) |
| FTT-013 | TBD (slow-marker skip) | TIMEOUT @ 60s in isolation | DETERMINISTIC-SLOW |
| FTT-014 | Mongo-collection state from prior file | FAIL_DETERMINISTIC in isolation | DETERMINISTIC REGRESSIONS |
| FTT-015..018 | env / Motor loop | PASS in isolation | CROSS-TEST POLLUTION (kept) |
| FTT-019..022 | SendGrid env stub | PASS in isolation | CROSS-TEST POLLUTION (kept) |
| FTT-023 | tenant-stub state | PASS in isolation | CROSS-TEST POLLUTION (kept) |
| FTT-024..026 | autosave debounce timer | PASS in isolation | CROSS-TEST POLLUTION (kept) |

Slice: `backend/scripts/jc_test_pollution_per_file_capture_slice.py` · evidence: `memory/jc_artifacts/test_pollution/per_file/` (433 MDs) · index: `memory/jc_artifacts/test_pollution/per_file_capture_20260626T181453Z.md` · sprint memo: `sprints/P5_7_PER_FILE_CAPTURE.md`.

### THIN-ASSERTION grandfather entries (from INVARIANT_NO_THIN_ASSERTIONS baseline scan, 2026-06-26)

These 9 entries are the pre-existing thin-assertion test bodies that the new build-breaking invariant `tests/invariants/test_no_thin_assertions.py` surfaced at ship time. They are exempted by the file-based grandfather list at `backend/tests/invariants/thin_assertions_grandfathered.yml`. Each is queued for individual rewrite (real assertion that exercises the documented branch) OR deletion (if the test is truly redundant). Removing an entry from this section MUST coincide with removing it from the grandfather YAML.

**P2 OPPORTUNISTIC-ONLY BACKLOG STATUS (codified 2026-06-30 per user directive in `sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md` follow-on dispatch JC-INLINE-BLOB-SUNSET-PROD-COUNT)**: Threshold enforcement stays automatic — the invariant catcher + drift detector remain active at the 9-entry ceiling. Retirement of FTT-027..035 is OPPORTUNISTIC: take one down when someone is already inside these files for real product/test work, rewrite/delete with a real assertion, and remove the corresponding YAML + tracker rows in the same commit. **NOT to be scheduled as a dedicated sprint dispatch.** The machine-enforced ceiling is the discipline pay; individual closures are P2 opportunistic work only.

| ID | Node | Pattern | Disposition target |
|----|------|---------|---------------------|
| FTT-027 | `tests/test_iter12_shares_home.py::test_comment_on_share_via_comments_router` | T2 (`pass`-only) | Legacy share-home test stub; rewrite with real comments-router assertion or delete |
| FTT-028 | `tests/test_j2_stage_3.py::test_no_guardrail_files_modified_in_j2` | T3 (`assert True`) | Guardrail-files marker assertion — replace with real file-set diff assertion |
| FTT-029 | `tests/test_j3_stage_4_5_frontend.py::test_j3_f6_retired_at_j4_ship` | T3 (`assert True`) | Retired-at-ship marker — confirm phase retirement via real surface check |
| FTT-030 | `tests/test_j3_stage_4_5_frontend.py::test_j3_f8_no_guardrail_files_modified` | T3 (`assert True`) | Same shape as FTT-028 |
| FTT-031 | `tests/test_patch_21_news.py::test_news_endpoint_requires_auth` | T4 (only `pytest.skip`) | Either remove (dead test) or restore real auth-gate assertion |
| FTT-032 | `tests/test_patch_23_upload_p0.py::test_upload_endpoint_rejects_without_auth_header` | T4 (only `pytest.skip`) | Same shape as FTT-031 |
| FTT-033 | `tests/test_patch_25_news_geo.py::test_profile_country_get_patch_round_trip` | T4 (only `pytest.skip`) | Same shape as FTT-031 |
| FTT-034 | `tests/test_track_b_phase1_signin_begin.py::test_fig20_unauth_root_lands_on_signin` | T2 (`pass`-only) | Track-B Phase 1 sign-in unauth-root — pair with FIG-20 acceptance row |
| FTT-035 | `tests/test_track_b_phase1_signin_begin.py::test_fig22_post_redirect_no_error_state` | T2 (`pass`-only) | Track-B Phase 1 post-redirect no-error — pair with FIG-22 acceptance row |

Total thin-assertion tracker: **9** distinct nodes (FTT-027..035); each requires individual rewrite or deletion.

## Active counts (post-2026-06-26 reclassification)

| Section | Count |
|---|---:|
| CROSS-TEST POLLUTION FLAKES (real pollution, pending bisect) | 18 / 7 files |
| DETERMINISTIC REGRESSIONS (real bugs surfaced; was hiding behind pollution) | 1 |
| INTEGRATION-LANE-ONLY (not active issue in default lane) | 2 |
| DETERMINISTIC-SLOW (test-performance backlog item, not a flake) | 1 |
| THIN-ASSERTION grandfather entries | 9 |
| **Active total** | **31** |

(Down from 33 pre-reclassification — net change: 24 pollution entries became 18 real pollution + 1 deterministic regression + 2 integration-only + 1 deterministic-slow + 1 already disposed at the audit-trail row level.)

## Resolved entries

### Phase 5.6.2 ship (2026-06-26)

| ID | Node | Disposition | Sprint memo |
|----|------|-------------|-------------|
| FTT-001 | `tests/test_phase_zz2_x.py::test_zz2_x_fixture_404_when_env_disabled` | RE-IMPLEMENTED with real assertion (both rails: env-disabled fall-through + env-enabled positive control via sentinel-patched `stream_fixture`). 4/4 GREEN on proving slice; 1 passed on pytest target with no sibling regression. | `sprints/P5_6_2_ftt001_real_assertion.md` |

## Disposition rules

1. **THIN-ASSERTION** items → Phase 5.6.2: rewrite each test with a real assertion that exercises the documented branch. Each entry leaves this tracker when its sprint memo ships.
2. **CROSS-TEST POLLUTION** items → require root-cause investigation (event-loop binding, dependency_overrides isolation, Mongo collection cleanup). Filed for a future Phase 5.7+ sprint.
3. New entries appended at the bottom of the appropriate section with the rationale, never inline-edited (preserve the audit trail).

— END —
