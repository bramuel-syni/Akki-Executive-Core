**Canonical Spec**: `/app/memory/sprints/INVARIANT_NO_THIN_ASSERTIONS.md §6` (grandfather YAML 9-entry baseline + 10-entry HALT threshold cited in ship-memo footer — but only as a one-shot check at ship time, NOT as a continuous build-time enforcement; this memo audits-and-fixes that gap, shipped as Step 4 of the 2026-06-27 batch)

# Sprint INVARIANT_GRANDFATHER_CEILING — continuous enforcement of the thin-assertion grandfather ceiling

**Status**: SHIPPED · proving slice rows B1 + B2 GREEN (10/10 batch) · regression-check ladder GREEN
**Date**: 2026-06-27
**Predecessor**: `sprints/INVARIANT_NO_THIN_ASSERTIONS.md` (the invariant being audited and amended)

---

## §0 — Audit finding

Per Step 4 directive, audited `tests/invariants/test_no_thin_assertions.py` for grandfather-count ceiling enforcement.

**Pre-fix state**:
- `_load_grandfather()` reads the YAML and returns the set of grandfathered entries.
- `test_no_thin_assertions_in_tests()` skips ANY entry that matches the YAML (regardless of count).
- `test_grandfather_list_does_not_drift()` checks for STALE entries (entries in YAML but no longer present as a live thin-assertion).
- The original sprint memo `sprints/INVARIANT_NO_THIN_ASSERTIONS.md` documented a "10-finding HALT threshold" but that was a **one-shot baseline check at ship time**, NOT a continuous enforcement.

**Verdict**: ❌ **No continuous count-ceiling enforcement existed.** A new test with a thin-assertion + a new YAML entry would silently grow the count past 10 with no one watching. User's concern (Step 4 directive) was correct.

---

## §1 — Fix applied

### §1.1 — Added `test_grandfather_count_below_ceiling()` function in `test_no_thin_assertions.py`

```python
GRANDFATHER_CEILING = 10

def test_grandfather_count_below_ceiling():
    """Hard ceiling: thin-assertion grandfather YAML cannot quietly
    grow past the ship-time HALT threshold of 10 entries.
    ..."""
    if yaml is None:
        pytest.skip(...)
    grandfathered = _load_grandfather()
    if len(grandfathered) > GRANDFATHER_CEILING:
        pytest.fail(...)
```

**Net delta**: +42 LOC. One new test function. No change to the existing two functions.

**Ceiling rationale**: `GRANDFATHER_CEILING = 10` matches the ship-time HALT threshold from the original sprint memo. Current YAML has 9 entries (FTT-027..035) → baseline passes with 1 slot of headroom. Trajectory: as FTT-027..035 close (each test rewritten with a real assertion), the count drops; ceiling stays at 10. Never grows.

---

## §2 — Proving slice (`backend/scripts/jc_invariant_bespoke_run_helper_slice.py` rows B1-B2)

This slice ships in batch with the Step 4.5 invariant (`INVARIANT_NO_BESPOKE_RUN_HELPER.md`) — both invariants share one slice for audit-trail consolidation.

```
  Row  9  GREEN  thin-assertion count-ceiling PASSES (9 ≤ 10)
            1 passed, 21 warnings in 3.78s
  Row 10  GREEN  thin-assertion ceiling probe: lower ceiling to 8 → FAILS
            1 failed, 21 warnings in 3.79s
```

**Row B1 (Row 9)**: invariant PASSES at the seeded baseline (9 ≤ 10).
**Row B2 (Row 10)**: temporarily bump ceiling DOWN to 8 (below current YAML count of 9). Expected outcome: invariant FAILS with the clear pointer to the three resolution options. Cleanup restores ceiling to 10 → invariant back to PASS. End-to-end NEGATIVE probe successful.

---

## §3 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite `tests/invariants/*` | yes | **92 pass / 7 pre-existing failures** | +1 new test (`test_grandfather_count_below_ceiling`) added; +3 from companion bespoke-run invariant. Total +4 PASS. SAME 7 pre-existing failures unchanged. |
| Stage 1 deck byte-identical (76,555 bytes) | yes | **N/A** | No deck render path touched. |
| 450/450 Solva v2 schema+validator | yes | **N/A** | No schema/validator file touched. |
| Surface ratchets (api / v1 / combined) | yes | **MATCH** via `test_phase4_4_dual_mount_smoke.py` 37/37 PASS |
| Cluster's own proving slice (rows B1-B2) | yes | **2/2 GREEN** within the 10/10 batch slice |

---

## §4 — Files modified

| Path | Status | Why |
|---|---|---|
| `tests/invariants/test_no_thin_assertions.py` | MOD | +42 LOC — one new function `test_grandfather_count_below_ceiling` + module-level constant `GRANDFATHER_CEILING = 10` |
| `memory/sprints/INVARIANT_GRANDFATHER_CEILING.md` | NEW | This sprint memo |
| `memory/DEV_PIPELINE.md` | UPDATED | §9 row added (combined with INVARIANT_NO_BESPOKE_RUN_HELPER) |

**Files NOT touched**: any product code, any test file outside `tests/invariants/`, the grandfather YAML itself (no entries added or removed), any fixture file.

---

## §5 — FTT-027..035 disposition

FTT-027..035 (the 9 grandfathered thin-assertion entries) are now **formally accepted as documented debt with structural enforcement of the ceiling**. The audit branch the user pre-specified:

> "If yes → write a brief audit memo `INVARIANT_GRANDFATHER_CEILING_AUDIT.md` documenting confirmation. FTT-027..035 formally accepted as documented debt."
> "If no → add ceiling enforcement (`assert len(grandfather_entries) <= 10`) + proving slice with try-add-11th expecting fail. Sprint memo `INVARIANT_GRANDFATHER_CEILING.md`."

→ This memo is the **"if no"** branch. Enforcement added. FTT-027..035 conditionally accepted: they remain as documented debt UNTIL each test is individually rewritten with a real assertion. Each rewrite drops the YAML count by 1; the ceiling at 10 ensures no silent additions can compensate.

---

## §6 — Discipline notes

- **Scope honoured**: Step 4 directive exactly — added the ceiling check that was missing, no broader scope.
- **No testing subagent used** (per banned-list rule).
- **Proving slice rows B1-B2 GREEN** within the 10/10 batch slice.
- **Locked-area check** done — clear (only `tests/invariants/test_no_thin_assertions.py` touched).
- **No production code changes**.
- **Ceiling is now machine-enforced**: every CI run that includes the invariants suite will fail the build if grandfather count exceeds 10. Audit drift is no longer silent.

---

## §7 — User-direction surface

Step 4 closes with the audit branch (b) outcome — enforcement was missing and is now added. Ships in the 2026-06-27 batch alongside `INVARIANT_NO_BESPOKE_RUN_HELPER.md` (Step 4.5).

Next: Step 5 (Cluster-F F.4 dispatch) per locked sequence.
