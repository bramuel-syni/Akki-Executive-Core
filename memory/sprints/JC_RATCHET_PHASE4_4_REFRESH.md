**Canonical Spec**: `/app/memory/sprints/JC_POLLUTION_B1_FIX.md §5` (parked side-finding surfaced during B.1 slice authoring: `test_phase4_4_dual_mount_smoke.py::test_{api,v1,combined}_slice_hash_pinned` carry stale ratchet shas) · ratchet-refresh sprint dispatched in parallel with Cluster-F.2 · HARD STOP at proving-slice close

# Sprint JC_RATCHET_PHASE4_4_REFRESH — surface-ratchet sha refresh on phase4_4 smoke

**Status**: SHIPPED (test-file-only patch landed) · proving slice **4/4 GREEN** · HARD STOP at slice close
**Date**: 2026-06-26
**Predecessor**: `sprints/JC_POLLUTION_B1_FIX.md §5` (parked side-finding)

---

## §0 — Outcome at a glance

| Test | Pre-fix sha | Post-fix sha (live) | Status |
|---|---|---|---|
| `test_api_slice_hash_pinned` | `9aa905f6d951f2a8` (stale) | `31e1d9769f632472` (live, 636 paths) | **GREEN** |
| `test_v1_slice_hash_pinned` | `6ce751ef812f6816` (stale) | `beb97b57a4bb2660` (live, 634 paths) | **GREEN** |
| `test_combined_hash_pinned` | `4f050f7e95b8dd10` (stale) | `8082e79d5d7302f5` (live, 1270 paths) | **GREEN** |
| `test_dual_mount_count_invariant` (implicit — depends on path counts) | api=632 / v1=630 | api=636 / v1=634 (delta still 2 = `EXPECTED_EXCLUDED_COUNT`) | **GREEN** |

**Net**: 3 deterministic regressions in `test_phase4_4_dual_mount_smoke.py` closed by refreshing 3 sha constants + 2 path-count constants. Same shape as A+D's Cluster-D sibling regression on phase4_2 (a one-line stale-sha fix; here it's 5 constants on a single file).

---

## §1 — Patches applied (test-file-only, locked-area cleared)

**File touched**: `tests/test_phase4_4_dual_mount_smoke.py` (single test file; 5 constant updates).

### §1.1 — Constant refreshes (lines 52-54 + 79 + 94)

```python
# Pre-fix:
EXPECTED_API_SHA = "9aa905f6d951f2a8"
EXPECTED_V1_SHA = "6ce751ef812f6816"
EXPECTED_COMBINED_SHA = "4f050f7e95b8dd10"
assert len(api_paths) == 632   # line 79
assert len(v1_paths) == 630    # line 94
```

```python
# Post-fix:
EXPECTED_API_SHA = "31e1d9769f632472"  # rolled forward at JC-RATCHET-PHASE4_4-REFRESH (2026-06-26)
EXPECTED_V1_SHA = "beb97b57a4bb2660"   # rolled forward at JC-RATCHET-PHASE4_4-REFRESH (2026-06-26)
EXPECTED_COMBINED_SHA = "8082e79d5d7302f5"  # rolled forward at JC-RATCHET-PHASE4_4-REFRESH (2026-06-26)
assert len(api_paths) == 636   # line 79
assert len(v1_paths) == 634    # line 94
```

**Pre-flight verification** (preflight block of proving slice):
```
/api/* sha = 31e1d9769f632472 (paths=636) — matches new EXPECTED
/v1/*  sha = beb97b57a4bb2660 (paths=634) — matches new EXPECTED
combined sha = 8082e79d5d7302f5 (paths=1270) — matches new EXPECTED
```

**Path-count invariant preserved**: `EXPECTED_EXCLUDED_COUNT = 2` still holds because `api_paths (636) - v1_paths (634) = 2` (same excluded set: `/api/healthz/clamav` + `/api/healthz/shield`).

### §1.2 — Locked-area re-confirmation

| Area | Touched? |
|---|---|
| Shield surfaces | NO (test exercises Shield paths in byte-identity smoke, but FIX only touches constants) |
| WS Generate Doc UI | NO |
| Track-2 schema | NO |
| Monitor pre-warmer | NO |
| Product code | NO |

Cleared. 5 constants updated; zero behavioural code changed.

---

## §2 — Proving slice results (`backend/scripts/jc_ratchet_phase4_4_proving_slice.py`)

```
============================================================================
JC-RATCHET-PHASE4_4-REFRESH Proving Slice
============================================================================
  preflight: /api/* sha = 31e1d9769f632472 (paths=636)
  preflight: /v1/*  sha = beb97b57a4bb2660 (paths=634)
  preflight: combined = 8082e79d5d7302f5 (paths=1270)

  Row  1  GREEN  test_api_slice_hash_pinned PASSES
            1 passed, 21 warnings in 5.06s
  Row  2  GREEN  test_v1_slice_hash_pinned PASSES
            1 passed, 21 warnings in 5.13s
  Row  3  GREEN  test_combined_hash_pinned PASSES
            1 passed, 21 warnings in 5.16s
  Row  4  GREEN  All 37 tests in target file PASS in isolation
            37 passed, 21 warnings in 5.60s
============================================================================
RESULT  4/4 GREEN
============================================================================
```

**Pre-flight check**: live `/api/openapi.json` re-verification confirms all 3 hardcoded EXPECTED constants match live values BEFORE running pytest. This guarantees the test sha constants aren't drifting again between authoring and execution.

**Row 4 nuance**: `test_phase4_4_dual_mount_smoke.py` has 37 tests total (3 sha-pinned + 1 v1-context-namespace + 1 dual-mount-count-invariant + 31 byte-identity parametrize cases + 2 wrong-context negative tests). Pre-fix: 34/37 PASS, 3 RED on sha pins. Post-fix: 37/37 PASS.

---

## §3 — Side-effects on DEV_PIPELINE §5

Per discipline, DEV_PIPELINE.md §5 (surface ratchet table) is updated to reflect the live values:

```diff
-| API: public path-list ratchet | `/api/* = 31e1d9769f632472` · `/v1/* = 6ce751ef812f6816` · combined `4f050f7e95b8dd10` |
+| API: public path-list ratchet | `/api/* = 31e1d9769f632472` · `/v1/* = beb97b57a4bb2660` · combined `8082e79d5d7302f5` |
```

The `/api/*` sha was already at `31e1d9769f632472` (rolled forward by A+D). This refresh adds the `/v1/*` and combined-sha live-truth alignment that A+D didn't cover (A+D only rolled `/api/*` because that was its sibling-test's hardcoded constant).

---

## §4 — Regression-check ladder

| Check | Required | Result |
|---|---|---|
| Invariant suite | yes | **88 pass / 7 pre-existing failures** unchanged. Same pattern as post-Cluster-F.2 state. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** — no render path touched |
| 450/450 Solva v2 schema+validator | yes | **N/A** — no schema/validator file touched |
| Surface ratchet at `31e1d9769f632472` | yes | **MATCH** — pre-flight re-verified plus this sprint also updates `/v1/*` and combined ratchets in DEV_PIPELINE §5 |
| JC-TM email path smoke | yes | **N/A** |
| Convergent + divergent pptx renders | yes | **N/A** |
| Cluster's own proving slice (4/4) | yes | **4/4 GREEN** |

---

## §5 — Files produced / modified

| Path | Status | Why |
|---|---|---|
| `tests/test_phase4_4_dual_mount_smoke.py` | MOD | 5 constants updated (3 shas + 2 path counts); zero behavioural change |
| `backend/scripts/jc_ratchet_phase4_4_proving_slice.py` | NEW | 4-row proving slice with live-truth pre-flight check |
| `memory/sprints/JC_RATCHET_PHASE4_4_REFRESH.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §5 ratchet table refreshed (`/v1/*` + combined to live values); §9 row for this sprint |

---

## §6 — Discipline notes

- **Test-file-only scope honoured**: 5 hardcoded constants updated in one file.
- **No testing subagent used** (per banned-list rule).
- **Live-truth pre-flight built into the proving slice**: any future re-run of `jc_ratchet_phase4_4_proving_slice.py` would fail the pre-flight if the live ratchet drifts again — making the slice self-detecting for future surface ships that add routes without updating the constants.
- **Locked-area check** done before and after — clear.
- **No production code changes** — pure ratchet-pin refresh.
- **Pattern documented for re-use**: any future "stale ratchet sha" finding in another test file (there may be more — DEV_PIPELINE notes that several test files have hardcoded shas) follows this same shape: live re-verify + constant update + slice with pre-flight.

---

## §7 — User-direction surface (next dispatch)

The B.1 sprint memo §5 surfaced this as a parked side-finding. Now closed.

No follow-up dispatch required for this finding. The original sequence resumes:
- **F.1** (next, recommended Cluster-F sub-sprint)
- F.4 → F.5 → F.3 → F.6 in sequence
- Cluster C dispatch after Cluster-F closes

Standing rules unchanged.
