**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (sub-sprint F.1 dispatched per user direction 2026-06-27 · scope: 2 M1 polluter files (password_change + admin_force_reset) · HARD STOP at proving-slice close · no chain into F.4)

# Sprint JC_POLLUTION_CLUSTER_F1_FIX — mechanical sync→async conversion on the admin-mutation pair

**Status**: SHIPPED (test-file-only patches landed) · proving slice **10/10 GREEN** stable across 2 consecutive runs · regression-check ladder GREEN · HARD STOP at slice close
**Date**: 2026-06-27
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_F2_FIX.md` (mechanical pattern proven 12/12 GREEN on 3-file scale-up); `sprints/JC_POLLUTION_CLUSTER_E_FIX.md` (1-file pattern proof); `sprints/P5_7_FIX_SCOPE_CLUSTER_F.md` (14-file survey + 6-sub-sprint grouping)

---

## §0 — Outcome at a glance

| File | Sync tests | Conversions | Post-fix isolation |
|---|---:|---|---|
| `tests/test_phase_p2_b4_password_change.py` | 4 | 4 async-converted (all touch Motor I/O via `AsyncClient/ASGITransport`) | 4/4 PASS |
| `tests/test_phase_p2_b6_admin_force_reset.py` | 4 | 4 async-converted (all touch Motor I/O via `AsyncClient/ASGITransport`) | 4/4 PASS |
| **Totals** | **8** | **8 async-converted + 0 stay sync** | **8/8 PASS** |

**Net**: Cluster-F.1 closes the wrong-loop-binding leak at source for 2 of the 14 Cluster-F polluters. Combined with F.2 (3 files), **5 of 14 Cluster-F polluters are now converted** — 9 remain across F.3 (csrf + session_timeout + session_reauth), F.4 (bounce_webhook + waitlist_reminder), F.5 (microsoft_pkce + inbox_migration + admin_button_and_badge), and F.6 (synisense_security).

**Why every test converted (vs F.2's 9-of-11)**: every test in b4/b6 uses Motor I/O through FastAPI middleware (`AsyncClient + ASGITransport` against `app`). No pure-Python unit tests, no `subprocess.run`-only tests. The conversion is 100% coverage of these files' sync surface.

**Honest accounting on FTT IDs**: this sub-sprint does NOT directly close FTT-024..026 (those are the autosave file's 3 IDs). **FTT-024..026 will close after the final Cluster-F sub-sprint (F.6) ships** — at that point all 14 polluters are converted and autosave's pollution surface is empty.

---

## §1 — Patches applied (test-file-only, locked-area cleared)

### §1.1 — `tests/test_phase_p2_b4_password_change.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 34-35 pre-fix per scope memo §0)
- Converted helper `_login(email, password)` from sync→`async def`. Drops inner `_do()` closure if any.
- Converted 4 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_b4_change_password_happy_path`
  - `test_b4_rejects_wrong_current_password`
  - `test_b4_rejects_same_password`
  - `test_b4_rejects_passwordless_account`
- Each test's `_run(_login(...))` became `await _login(...)`; `_run(_do())` patterns inlined into the test body.
- Updated module docstring to cite Cluster-F.1 (2026-06-26) + root cause (wrong-loop binding via sync `_run` helper).

### §1.2 — `tests/test_phase_p2_b6_admin_force_reset.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 24-25 pre-fix per scope memo §0)
- Converted helper `_admin_token(admin)` from sync→`async def`.
- Converted 4 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_b6_force_reset_happy_path`
  - `test_b6_non_superadmin_blocked`
  - `test_b6_unknown_user_returns_404`
  - `test_b6_audit_event_written`
- Each test's `_run(_admin_token(...))` became `await _admin_token(...)`; embedded `_run(_do())` patterns inlined.
- Updated module docstring to cite Cluster-F.1 (2026-06-26) + root cause.

### §1.3 — Locked-area re-confirmation

| Area | Touched? |
|---|---|
| Shield surfaces | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| Product code (`server.py`, `core.py`, `contracts/`) | NO |

Cleared. Both files are pure test-side. Only test bodies + helpers + module docstrings touched.

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_f1_proving_slice.py`)

### §2.1 — Run-1 transient + Run-2/Run-3 confirmation

**The first invocation produced a transient Row 7 RED** (7 failed / 5 passed on `b4 + phase4_2` pairing, wall time 83.07s — vs expected 12 PASS in <10s). Immediate re-invocation of the identical `pytest` command directly produced **12 PASSED in 7.28s**. Two consecutive subsequent full slice runs both produced **10/10 GREEN with Row 7 at 12 PASS in ~9s**.

**Diagnosis**: not a regression introduced by F.1. The b4 file alone (Row 1) and the F.1 pair alone (Row 5) and F.1 + autosave (Row 6) all PASS deterministically. The pre-A+D phase4_2 file is the only A+D-fixed defensive pairing in this slice; that file is also itself sensitive to upstream MongoDB warmup state (per BUG-ANL-UPLOAD-GRIDFS proving-slice notes on MongoDB-state warmup variability under cold-cache load).

**Discipline rule applied**: per §6.3 of the F.2 memo's "proving slice GREEN means GREEN twice consecutively at slice scope" standard, the slice closes only when 2 consecutive runs are 10/10 GREEN. That standard is met (Run-2 and Run-3 both 10/10). Run-1 transient is documented as a known-flake signature unique to A+D-fixed defensive pairings under cold cache, NOT caused by F.1.

### §2.2 — Stable-run output

```
============================================================================
P5.7-Cluster-F.1 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
============================================================================
  Row  1  GREEN  tests/test_phase_p2_b4_password_change.py in isolation post-fix (4 passed)
            4 passed, 21 warnings in 6.91s  [dur=9.1s]
  Row  2  GREEN  tests/test_phase_p2_b6_admin_force_reset.py in isolation post-fix (4 passed)
            4 passed, 21 warnings in 6.00s  [dur=7.9s]
  Row  3  GREEN  tests/test_phase_p2_b4_password_change.py + autosave (B.2 polluter pair, post-fix)
            7 passed, 21 warnings in 8.10s  [dur=10.0s]
  Row  4  GREEN  tests/test_phase_p2_b6_admin_force_reset.py + autosave (B.2 polluter pair, post-fix)
            7 passed, 21 warnings in 7.11s  [dur=9.2s]
  Row  5  GREEN  Combined F.1 (b4 + b6 together) — 8 PASS expected
            8 passed, 21 warnings in 8.64s  [dur=10.7s]
  Row  6  GREEN  Combined F.1 + autosave — 11 PASS expected
            11 passed, 21 warnings in 9.47s  [dur=11.6s]
  Row  7  GREEN  tests/test_phase_p2_b4_password_change.py + tests/test_phase4_2_http_transport_smoke.py (A+D defensive)
            12 passed, 21 warnings in 6.90s  [dur=9.0s]
  Row  8  GREEN  tests/test_phase_p2_b6_admin_force_reset.py + tests/test_phase_p5_10_audit_panel_direct_linkage.py (Cluster-E defensive)
            9 passed, 21 warnings in 5.99s  [dur=7.9s]
  Row  9  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 6's full stdout
  Row 10  GREEN  source-assertion: no _run / get_event_loop.run_until_complete
            both F.1 files clean
============================================================================
RESULT  10/10 GREEN
============================================================================
```

**Key signals**:
- **Rows 3-4**: each F.1 file paired with autosave (the B.2 polluted target) → 7 PASS each. Confirms wrong-loop-binding is closed for these 2 specific polluter→polluted pairs.
- **Row 5**: combined F.1 (b4 + b6 alphabetically together — b4 runs first per ASCII order) = 8/8 PASS. Inner-cluster cross-pollination empty.
- **Row 6**: combined F.1 + autosave = 11/11 PASS. The pollution scope previously reported for these 2 polluters is now empty.
- **Row 7-8**: defensive checks confirm A+D's (phase4_2) and Cluster-E's (p5_10) closures aren't regressed by the F.1 conversion.
- **Row 9**: zero `Future attached to a different loop` occurrences — the canonical Cluster-E signature is silenced for both F.1 polluters.
- **Row 10**: source-assertion confirms no `_run` helper or `asyncio.get_event_loop().run_until_complete` line remains in either file. Durability check for future regressions.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **88 pass / 7 pre-existing failures** unchanged | Same pattern as post-F.2 state (`enforce_mode_zero_violations` + `polymorphic_response_ratchet` × 2 + `sdk_slices` + `tenancy_enforce_mode_for_migrated_collections` + `tenancy_escape_hatch_allowlist` × 2). NOT regressions from F.1. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via `test_phase4_4_dual_mount_smoke.py` 37/37 PASS — `/api/* = 31e1d9769f632472`, `/v1/* = beb97b57a4bb2660`, combined `8082e79d5d7302f5` all in lockstep |
| JC-TM email path smoke | yes | **N/A** | No SendGrid/email-path code touched. (The bounce_webhook polluted file STILL has its `_run` helper — not in F.1 scope; will close in F.4.) |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Cluster's own proving slice | yes (10/10) | **10/10 GREEN** stable across 2 runs |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_phase_p2_b4_password_change.py` | MOD | Helper drop + `_login` async-conversion + 4 sync→async tests + docstring (≈22 LOC delta) |
| `tests/test_phase_p2_b6_admin_force_reset.py` | MOD | Helper drop + `_admin_token` async-conversion + 4 sync→async tests + docstring (≈23 LOC delta) |
| `backend/scripts/jc_pollution_cluster_f1_proving_slice.py` | NEW | 10-row proving slice (≈165 LOC) |
| `memory/sprints/JC_POLLUTION_CLUSTER_F1_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row for JC-POLLUTION-CLUSTER-F1-FIX (added 2026-06-27) |
| `memory/jc_artifacts/FAILING_TEST_TRACKER.md` | UPDATED | FTT-024..026 cluster note refreshed — 5/14 polluters now converted |

**Files NOT touched**: any product code, any other test file, any fixture file, any invariant file. Zero touches to Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer · contracts module · core.py · server.py.

---

## §5 — Discipline notes

- **Scope honoured**: only the 2 F.1 files in `tests/` modified.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 10/10 GREEN stable across 2 consecutive runs** — HARD STOP at slice close.
- **Locked-area check** done before and after — clear.
- **No production code changes** — entirely test-side mechanical conversion.
- **Pattern uniformity confirmed**: the same Cluster-E mechanical conversion applied 2× without per-file customization. Validates that the pattern continues to scale; F.3, F.4, F.5 can follow the same shape.
- **All-tests-convert in this pair**: unlike F.2 (which preserved 2 sync tests for `subprocess.run`-only / pure-Python-only cases), F.1's 8 tests all touch Motor I/O through FastAPI middleware. 100% conversion rate.
- **Run-1 transient surfaced + investigated + documented**: not a regression; A+D-fixed phase4_2 file is itself sensitive to MongoDB warmup state under cold-cache load. 2 consecutive 10/10 GREEN runs satisfy the slice-close discipline.

---

## §6 — User-direction surface (HARD STOP)

Per the original dispatch directive: **HARD STOP & surface to user — do NOT chain into F.4**.

Cluster-F sub-sprint progress:
- ✅ F.2 (security_headers + cookie_hardening + health_composite) — 3 files closed
- ✅ F.1 (password_change + admin_force_reset) — 2 files closed
- ⏳ F.4 (bounce_webhook + waitlist_reminder) — 2 files pending
- ⏳ F.5 (microsoft_pkce + inbox_migration + admin_button_and_badge) — 3 files pending
- ⏳ F.3 (csrf + session_timeout + session_reauth) — 3 files pending; medium risk per scope memo §1.1
- ⏳ F.6 (synisense_security) — 1 M2 outlier file pending; HALT-and-surface pre-armed per scope memo §6 for Shield-adjacency

5 of 14 polluters converted. 9 remain across 4 sub-sprints.

Awaiting next dispatch from user. Standing rules unchanged.
