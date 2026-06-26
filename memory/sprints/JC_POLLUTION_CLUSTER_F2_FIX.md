**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (sub-sprint F.2 dispatched per user direction 2026-06-26 · scope: 3 M1 polluter files (security_headers + cookie_hardening + health_composite) · HARD STOP at proving-slice close)

# Sprint JC_POLLUTION_CLUSTER_F2_FIX — mechanical sync→async conversion on 3 M1 polluters

**Status**: SHIPPED (test-file-only patches landed) · proving slice **12/12 GREEN** · regression-check ladder GREEN · HARD STOP at slice close
**Date**: 2026-06-26
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_E_FIX.md` (mechanical pattern proven 9/9 GREEN); `sprints/P5_7_FIX_SCOPE_CLUSTER_F.md` (14-file survey + 6-sub-sprint grouping)

---

## §0 — Outcome at a glance

| File | Sync tests | Conversions | Post-fix isolation |
|---|---:|---|---|
| `tests/test_phase_p2_b1_security_headers.py` | 5 | 4 async-converted + 1 stays sync (pure subprocess.run, no asyncio) | 5/5 PASS |
| `tests/test_phase_p3_2_cookie_hardening.py` | 2 | 2 async-converted (drops inner `_do()` closures) | 2/2 PASS |
| `tests/test_phase_p2_d2_health_composite.py` | 4 | 3 async-converted + 1 stays sync (pure-Python `_overall` unit test) | 4/4 PASS |
| **Totals** | **11** | **9 async-converted + 2 stay sync** | **11/11 PASS** |

**Net**: Cluster-F.2 closes the wrong-loop-binding leak at source for 3 of the 14 Cluster-F polluters. The remaining 11 Cluster-F polluters need their own sub-sprints (F.1, F.3, F.4, F.5, F.6). Per the §2.3 measurement procedure that drove A+D's evidence: this slice's Rows 4-6 paired each F.2 file with the autosave file (the original B.2 polluted target) and all 3 closed pairwise — confirming the mechanical fix shape transfers cleanly from Cluster-E's 1-file proof to Cluster-F.2's 3-file scale-up.

**Honest accounting on FTT IDs**: this sub-sprint does NOT directly close FTT-024..026 (those are the autosave file's 3 IDs). The autosave file still has 11 unconverted Cluster-F polluters in its broad-suite predecessor set. **FTT-024..026 will close after the final Cluster-F sub-sprint (F.6) ships** — at that point all 14 polluters are converted and autosave's pollution surface is empty.

---

## §1 — Patches applied (test-file-only, locked-area cleared)

### §1.1 — `tests/test_phase_p2_b1_security_headers.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 30-31 pre-fix)
- Converted 4 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_b1_baseline_headers_on_json_response`
  - `test_b1_hsts_set_on_https_forwarded`
  - `test_b1_hsts_absent_on_plain_http`
  - `test_b1_csp_present_on_json_too`
- Each test's `_run(_get(...))` became `await _get(...)`
- `test_b1_html_shell_headers_via_live_probe` **stayed sync** — it uses only `subprocess.run(curl)` and never touches asyncio. Documented in its docstring.
- Updated module docstring to cite Cluster-F.2 (2026-06-26) + root cause

### §1.2 — `tests/test_phase_p3_2_cookie_hardening.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 25-26 pre-fix)
- Converted 2 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_p3_2_login_cookie_attributes`
  - `test_p3_2_csrf_cookie_samesite_lax`
- Both tests had an inner `async def _do(): ... ; _run(_do())` pattern. Inlined the `_do()` body directly into the test function (drops the closure).
- Updated module docstring

### §1.3 — `tests/test_phase_p2_d2_health_composite.py`

- Removed `import asyncio` (unused post-conversion)
- Removed `_run` helper (lines 21-22 pre-fix)
- Converted 3 sync tests to `@pytest.mark.asyncio + async def`:
  - `test_d2_composite_shape`
  - `test_d2_caches_for_30_seconds`
  - `test_d2_no_auth_required`
- `test_d2_overall_rolls_up_fail_if_any_fails` **stayed sync** — it only exercises the pure-Python `_overall` helper function, no asyncio surface. Documented in its docstring.
- Updated module docstring

### §1.4 — Locked-area re-confirmation

| Area | Touched? |
|---|---|
| Shield surfaces | NO |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| Product code (`server.py`, `core.py`, `contracts/`) | NO |

Cleared. All 3 files are pure test-side. Only test bodies + helpers + module docstrings touched.

---

## §2 — Proving slice results (`backend/scripts/jc_pollution_cluster_f2_proving_slice.py`)

```
============================================================================
P5.7-Cluster-F.2 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
============================================================================
  Row  1  GREEN  tests/test_phase_p2_b1_security_headers.py in isolation post-fix (5 passed)
            5 passed, 21 warnings in 4.49s
  Row  2  GREEN  tests/test_phase_p3_2_cookie_hardening.py in isolation post-fix (2 passed)
            2 passed, 21 warnings in 4.89s
  Row  3  GREEN  tests/test_phase_p2_d2_health_composite.py in isolation post-fix (4 passed)
            4 passed, 21 warnings in 4.21s
  Row  4  GREEN  security_headers + autosave (B.2 polluter pair, post-fix)
            8 passed, 21 warnings in 5.12s
  Row  5  GREEN  cookie_hardening + autosave (B.2 polluter pair, post-fix)
            5 passed, 21 warnings in 5.47s
  Row  6  GREEN  health_composite + autosave (B.2 polluter pair, post-fix)
            7 passed, 21 warnings in 4.98s
  Row  7  GREEN  Combined F.2 (all 3 files together) — 11 PASS expected
            11 passed, 21 warnings in 5.06s
  Row  8  GREEN  Combined F.2 + autosave — 14 PASS expected
            14 passed, 21 warnings in 5.80s
  Row  9  GREEN  security_headers + bounce_webhook (A+D defensive)
            10 passed, 21 warnings in 4.49s
  Row 10  GREEN  cookie_hardening + p5_10 (Cluster-E defensive)
            7 passed, 21 warnings in 4.84s
  Row 11  GREEN  log scan: zero 'Future attached to a different loop'
            occurrences=0 in Row 8's full stdout
  Row 12  GREEN  source-assertion: no _run / get_event_loop.run_until_complete
            all 3 files clean
============================================================================
RESULT  12/12 GREEN
============================================================================
```

**Key signals**:
- **Rows 4-6**: each F.2 file paired with autosave (the B.2 polluted target) → all PASS post-conversion. Confirms the wrong-loop-binding is closed for these 3 specific polluter→polluted pairs.
- **Row 8**: combined F.2 + autosave = 14/14 PASS. The pollution scope previously reported for these 3 polluters is now empty.
- **Row 9-10**: defensive checks confirm A+D's (bounce_webhook) and Cluster-E's (p5_10) closures aren't regressed.
- **Row 11**: zero `Future attached to a different loop` occurrences — the canonical Cluster-E signature is silenced for all 3 F.2 polluters.
- **Row 12**: source-assertion confirms no `_run` helper or `asyncio.get_event_loop().run_until_complete` line remains in any of the 3 files. Durability check for future regressions.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **88 pass / 7 pre-existing failures** unchanged | Same `.....................Fsss.................................FF...F...` pattern as post-B.1 state. NOT regressions from F.2. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchet at `31e1d9769f632472` | yes | **MATCH** — live re-verified, 636 paths |
| JC-TM email path smoke | yes | **N/A** | No SendGrid/email-path code touched. (The bounce_webhook polluted file STILL has its `_run` helper — not in F.2 scope; will close in F.4.) |
| Convergent + divergent pptx renders | yes | **N/A** | No pptx render code touched. |
| Cluster's own proving slice | yes (12/12) | **12/12 GREEN** |

---

## §4 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_phase_p2_b1_security_headers.py` | MOD | Helper drop + 4 sync→async + import refresh + docstring (≈25 LOC delta) |
| `tests/test_phase_p3_2_cookie_hardening.py` | MOD | Helper drop + 2 sync→async + inlining of `_do()` closures + docstring (≈22 LOC delta) |
| `tests/test_phase_p2_d2_health_composite.py` | MOD | Helper drop + 3 sync→async + import refresh + docstring (≈18 LOC delta) |
| `backend/scripts/jc_pollution_cluster_f2_proving_slice.py` | NEW | 12-row proving slice |
| `memory/sprints/JC_POLLUTION_CLUSTER_F2_FIX.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row for JC-POLLUTION-CLUSTER-F2-FIX |

**Files NOT touched**: any product code, any other test file, any fixture file, any invariant file. Zero touches to Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer · contracts module · core.py · server.py.

---

## §5 — Discipline notes

- **Scope honoured**: only the 3 F.2 files in `tests/` modified.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 12/12 GREEN** — HARD STOP at slice close.
- **Locked-area check** done before and after — clear.
- **No production code changes** — entirely test-side mechanical conversion.
- **Pattern uniformity confirmed**: the same Cluster-E mechanical conversion applied 3× without per-file customization. Validates the F.1..F.5 sub-sprints can follow the same pattern.
- **Sync-test preservation where appropriate**: 2 of the 11 sync tests stay sync (one uses only `subprocess.run`, one is a pure-Python unit test). These have no asyncio surface to convert. Pattern: convert only tests that use `_run` / asyncio.
- **Discovered structural insight**: the cookie_hardening test had an inner `async def _do(): ...` closure that wrapped the actual body; the conversion inlined it directly into the test function (drops the closure overhead). Same pattern will apply to other M1 polluters that have inner async closures (need per-file inspection in subsequent sub-sprints).

---

## §6 — User-direction surface (next dispatch)

Per the Cluster-F memo's 6-sub-sprint plan + this sprint's validation that the mechanical pattern scales:

- **F.1** (next, recommended) — admin-mutation pair (password_change + admin_force_reset) — 8 sync tests
- F.4 — SendGrid surfaces (bounce_webhook + waitlist_reminder) — 13 sync tests
- F.5 — largest test-count group (microsoft_pkce + inbox_migration + admin_button_and_badge) — 18 sync tests
- F.3 — CSRF/session lifecycle (csrf + session_timeout + session_reauth) — 16 sync tests; medium risk
- F.6 — M2 outlier (synisense_security) — 3 sync tests + Shield-adjacency

Each its own dispatch with own proving slice + HARD STOP. After all 6 sub-sprints close, FTT-024..026 (the autosave file's 3 IDs) auto-close because the autosave file's polluter set will be empty.

Standing rules unchanged across remaining sub-sprints.
