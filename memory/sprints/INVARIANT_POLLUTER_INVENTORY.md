**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1` (Cluster-F closes existing polluters; this READ-ONLY observability slice produces a JSON dashboard of the current polluter landscape after each sub-sprint to validate the closure schedule is on track · shipped parallel with JC-POLLUTION-CLUSTER-F4-FIX 2026-06-27 · no scope collision with F.4)

# Sprint INVARIANT_POLLUTER_INVENTORY — READ-ONLY polluter-landscape observability slice

**Status**: SHIPPED · READ-ONLY (zero LOC mutated in any test/invariant/product file) · proving slice **3/3 GREEN** stable across 2 runs · HARD STOP at slice close
**Date**: 2026-06-27
**Predecessor**: `sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md` (the invariant whose state this slice observes)
**Parallel sibling**: `sprints/JC_POLLUTION_CLUSTER_F4_FIX.md` (the F.4 sub-sprint shipped simultaneously)

---

## §0 — What this slice is (and isn't)

**Is**:
- A READ-ONLY observability harness — `backend/scripts/jc_polluter_inventory_slice.py` (~280 LOC).
- Re-runs the M1 + M2 AST scan that the bespoke-run invariant uses + cross-references against `bespoke_run_helper_grandfathered.yml`.
- Produces a JSON dashboard + a human-readable `latest.md` summary per invocation.
- Designed to be run manually between sub-sprints by a human reviewer or the agent.

**Isn't**:
- A build-time invariant (does NOT run in `pytest`).
- A fix authority (does NOT mutate any file).
- A test that the testing-agent harness picks up.
- An ongoing scheduled job.

This is a **snapshot reporting tool**, not a guard. The guards are `test_no_bespoke_run_helper_in_tests` + `test_grandfather_list_does_not_drift` + `test_grandfather_count_below_ceiling`, which run in the invariants suite. This slice just *observes* their state on demand.

---

## §1 — Output shape

### §1.1 — JSON dashboard

Written to `/app/memory/jc_artifacts/polluter_inventory/inventory_<ISO-UTC-timestamp>.json`. Schema:

```json
{
  "generated_at": "2026-06-27T03:31:30.059222+00:00",
  "live_scan": {
    "m1_file_count": 11,
    "m2_site_count": 28,
    "m2_file_count": 9
  },
  "grandfather": {
    "m1_entry_count": 11,
    "m2_entry_count": 28,
    "m1_ceiling": 11,
    "m2_ceiling": 28,
    "m1_ceiling_proximity": "11/11",
    "m2_ceiling_proximity": "28/28"
  },
  "drift": {
    "new_m1_ungrandfathered": [],
    "stale_m1_in_yaml": [],
    "new_m2_ungrandfathered": [],
    "stale_m2_in_yaml": []
  },
  "sub_sprint_rollup": {
    "F.3": {"m1": 3, "m2": 0},
    "F.5": {"m1": 3, "m2": 0},
    "F.6": {"m1": 0, "m2": 2},
    "Cluster-G (post-F)": {"m1": 5, "m2": 25},
    "A+D fix preserves this asyncio.run with snapshot/restore": {"m1": 0, "m2": 1}
  },
  "closure_status": {
    "all_grandfathered_match_live": true
  }
}
```

### §1.2 — Human-readable `latest.md`

Always overwrites `/app/memory/jc_artifacts/polluter_inventory/latest.md` — fast "what is the polluter landscape right now?" lookup. Mirrors the JSON structure as markdown sections.

---

## §2 — Proving slice (3/3 GREEN)

```
============================================================================
POLLUTER INVENTORY SLICE — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
============================================================================
  Row P1  GREEN  inventory matches YAML + live tree (no drift)
            yaml m1=11  yaml m2=28  live m1=11  live m2=28  clean_drift=True
  Row P2  GREEN  new-test injection surfaces as ungrandfathered M1
            probe='backend/tests/test_zzz_inventory_probe.py' surfaced=True
  Row P3  GREEN  output artefacts written: JSON + latest.md
            json=inventory_20260627T033130_059222+0000.json  md=latest.md
============================================================================
RESULT  3/3 GREEN
============================================================================
```

**Key signals**:
- **P1**: inventory counts match the YAML; no drift surfaced (post-F.4 state: 11 M1 / 28 M2 grandfathered, same counts live).
- **P2**: end-to-end test of the new-site detection — temp test file with bespoke `_run` injected, inventory rebuilt, the probe surfaces in `drift.new_m1_ungrandfathered`. Auto-cleanup deletes the probe after assertion.
- **P3**: artefacts persist correctly + JSON is well-formed (json.loads round-trips).

---

## §3 — Initial snapshot (post-F.4)

Per-sub-sprint roll-up confirms the closure schedule:

| Bucket | M1 | M2 | Notes |
|---|---:|---:|---|
| F.3 (csrf + session_timeout + session_reauth) | 3 | 0 | Cluster-F middle-medium-risk |
| F.5 (microsoft_pkce + inbox_migration + admin_button_and_badge) | 3 | 0 | Cluster-F largest test-count group |
| F.6 (synisense_security) | 0 | 2 | M2 outlier; Shield-adjacency HALT pre-armed |
| Cluster-G (post-F) | 5 | 25 | Discovered by INVARIANT_NO_BESPOKE_RUN_HELPER baseline scan; needs its own scope memo after F.6 |
| A+D-preserved | 0 | 1 | `test_phase4_2_http_transport_smoke.py:254` — wrapped by env+loop-policy snapshot/restore |
| **TOTAL** | **11** | **28** |

Closure trajectory across remaining Cluster-F sub-sprints (F.3 + F.5 + F.6): 6 M1 + 2 M2 = 8 entries close. M1_CEILING will ratchet 11 → 8 → 5 (after F.5) → 2 (or wherever F.3 lands) → 0 (after F.6). Then Cluster-G dispatch consumes the remaining 5 M1 + 26 M2.

---

## §4 — Regression-check ladder

| Check | Required | Result | Notes |
|---|---|---|---|
| Invariant suite | yes | **92 pass / 7 pre-existing failures** | This slice does NOT add any pytest tests — invariants count unchanged from post-Step 4+4.5 baseline. |
| Stage 1 deck / Solva 450 / pptx | yes | **N/A** | No product code touched. |
| Surface ratchets | yes | **MATCH** via phase4_4 dual_mount_smoke 37/37 PASS |
| Slice's own 3 rows | yes | **3/3 GREEN** stable across 2 runs |

---

## §5 — Files produced

| Path | Status |
|---|---|
| `backend/scripts/jc_polluter_inventory_slice.py` | NEW (~280 LOC, READ-ONLY) |
| `memory/jc_artifacts/polluter_inventory/inventory_20260627T033130_059222+0000.json` | NEW (first snapshot) |
| `memory/jc_artifacts/polluter_inventory/latest.md` | NEW (mirrors first snapshot) |
| `memory/sprints/INVARIANT_POLLUTER_INVENTORY.md` | NEW (this memo) |
| `memory/DEV_PIPELINE.md` | UPDATED — §9 row added |

**Files NOT touched**: any product code, any test file, any invariant file, any fixture file. Pure-additive ship.

---

## §6 — Discipline notes

- **Scope honoured**: READ-ONLY observability as scoped in Dispatch 2.
- **No testing subagent used** (per banned-list rule).
- **Proving slice 3/3 GREEN** — HARD STOP at slice close.
- **Locked-area check** done — clear (only a new script + new artefact files; no test/invariant/product mutation).
- **No code changes anywhere** outside the new script + the artefact outputs.
- **Parallel ship with F.4 was safe**: F.4 touches 2 test files + 2 invariant files; this slice touches 0 of those. Zero collision.
- **Designed for repeated use**: every Cluster-F sub-sprint should run this slice as part of its surface-and-close cycle. Drift-free runs validate the closure-schedule lock is intact.

---

## §7 — User-direction surface (HARD STOP)

This slice is now part of the standing toolkit. Recommended workflow for F.5 / F.3 / F.6:

1. Pre-sub-sprint: run `python3 backend/scripts/jc_polluter_inventory_slice.py` → confirm clean drift (sanity check before edits begin)
2. Apply sub-sprint conversions (test file edits)
3. Update YAML (remove entries for closed files) + ratchet M1_CEILING/M2_CEILING down
4. Run the sub-sprint's own proving slice
5. Post-sub-sprint: re-run the inventory slice → confirm the new state is drift-free and the ceilings match

Awaiting next dispatch (F.5 per locked sequence). Standing rules unchanged.
