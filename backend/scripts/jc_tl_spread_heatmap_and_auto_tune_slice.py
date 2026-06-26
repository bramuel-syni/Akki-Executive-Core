"""JC-TL Spread-heatmap delta + Auto-tune candidates — proving slice.

Source of truth:
  • `/app/memory/JC_TL_CANONICAL_SPEC.md` §4 (GP — divergent spread)
  • `/app/memory/JC_MON_CANONICAL_SPEC.md` (Monitor surface)

Two newly-unblocked items shipping together (per user direction at
AUTONOMOUS BACKLOG RUN 2026-06-26 — "after GP ship: spread-heatmap
+ auto-tune in parallel"):

  • `services/solva_v2/spread_heatmap.py::compute_spread_delta`
  • `services/monitor/objective_candidate_service.py::_build_candidates_prompt`
    accepts `divergent_blind_spots`; backwards-byte-compatible when
    omitted.

Both items are pure-prompt / pure-data; no Shield call exercised
inline (the auto-tune Shield path lives behind the existing
`generate_candidate_objectives` engine surface, which is unchanged
in its external contract and continues to be exercised by
`jc_mon_stage_3_0_candidate_objectives_slice.py` for the
no-blind-spots baseline).

Run from the repo root:
    cd /app/backend && python scripts/jc_tl_spread_heatmap_and_auto_tune_slice.py
"""
from __future__ import annotations

import asyncio
import copy
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")

from services.solva_v2.spread_heatmap import compute_spread_delta  # noqa: E402
from services.monitor.objective_candidate_service import (  # noqa: E402
    _build_candidates_prompt,
)
from scripts.jc_tl_gp_ship_slice import (  # noqa: E402
    session_a_regulatory, session_b_investment,
)

ART_DIR = Path("/app/memory/jc_artifacts/jc_tl/04-spread-heatmap-auto-tune")
ART_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────
# Spread-heatmap delta rows.
# ──────────────────────────────────────────────────────────────────


def row_a_identical_sessions_zero_delta() -> Dict[str, Any]:
    """Row A — Same session vs itself → all personas stable; no add/remove."""
    s = session_a_regulatory()
    delta = compute_spread_delta(s, s)
    all_stable = all(p["direction"] == "stable" and p["delta_pct"] == 0
                     for p in delta["personas"])
    return {"row": "A", "subject": "Identical sessions → zero delta",
            "delta": delta,
            "PASS": (
                all_stable
                and not delta["personas_added"]
                and not delta["personas_removed"]
                and delta["spread_breadth_delta"] == 0
                and not delta["blind_spots_added"]
                and not delta["blind_spots_removed"]
            )}


def row_b_shifted_confidence() -> Dict[str, Any]:
    """Row B — Same personas, all confidence_pct +10 → all 'up'."""
    s_prev = session_a_regulatory()
    s_curr = copy.deepcopy(s_prev)
    for p in s_curr["synthesis"]["perspective_spread"]["personas"]:
        p["confidence_pct"] = min(99, p["confidence_pct"] + 10)
    delta = compute_spread_delta(s_prev, s_curr)
    all_up = all(p["direction"] == "up" and p["delta_pct"] == 10 for p in delta["personas"])
    return {"row": "B", "subject": "All confidence +10 → all 'up'",
            "delta_persona_count": len(delta["personas"]),
            "first_persona": delta["personas"][0] if delta["personas"] else None,
            "PASS": all_up and not delta["personas_added"] and not delta["personas_removed"]}


def row_c_persona_added_and_removed() -> Dict[str, Any]:
    """Row C — Different sessions (regulatory vs investment) → all personas
    are added/removed (no overlap)."""
    s_prev = session_a_regulatory()
    s_curr = session_b_investment()
    delta = compute_spread_delta(s_prev, s_curr)
    return {"row": "C", "subject": "Disjoint persona sets → added + removed populated",
            "personas_added":   delta["personas_added"],
            "personas_removed": delta["personas_removed"],
            "deltas":           len(delta["personas"]),
            "PASS": (
                len(delta["personas_added"]) == 3
                and len(delta["personas_removed"]) == 3
                and len(delta["personas"]) == 0   # zero overlap
            )}


def row_d_breadth_delta_positive() -> Dict[str, Any]:
    """Row D — Spread breadth widens by 8 pct → spread_breadth_delta == 8."""
    s_prev = session_a_regulatory()
    s_curr = copy.deepcopy(s_prev)
    # Original: 72/68/58 → max-min = 14
    # New: bump highest by +4 and lower the lowest by -4 → max-min = 22
    personas = s_curr["synthesis"]["perspective_spread"]["personas"]
    personas[0]["confidence_pct"] += 4   # auditor 72 → 76
    personas[2]["confidence_pct"] -= 4   # customer-advocate 58 → 54
    delta = compute_spread_delta(s_prev, s_curr)
    return {"row": "D", "subject": "Spread breadth widens by 8 pct",
            "breadth_delta": delta["spread_breadth_delta"],
            "PASS": delta["spread_breadth_delta"] == 8}


def row_e_blind_spots_added() -> Dict[str, Any]:
    """Row E — New blind-spot in curr → blind_spots_added picks it up."""
    s_prev = session_a_regulatory()
    s_curr = copy.deepcopy(s_prev)
    s_curr["synthesis"]["perspective_spread"]["blind_spots"].append({
        "persona_label": "Auditor",
        "blind_spot_description": "Newly surfaced cost-of-trust dimension the prior reads missed entirely.",
        "source_citations": [{"source_input_id": "audit-bs-new", "source_kind": "audit_log",
                              "excerpt": "fresh signal — added 2026-06-26"}],
    })
    delta = compute_spread_delta(s_prev, s_curr)
    return {"row": "E", "subject": "New blind-spot → blind_spots_added populated",
            "n_added": len(delta["blind_spots_added"]),
            "n_removed": len(delta["blind_spots_removed"]),
            "added_text": delta["blind_spots_added"][0] if delta["blind_spots_added"] else None,
            "PASS": len(delta["blind_spots_added"]) == 1
                    and len(delta["blind_spots_removed"]) == 0}


def row_f_non_gp_session_returns_empty() -> Dict[str, Any]:
    """Row F — Non-Get-Perspectives session → empty delta, no raise."""
    s_prev = {"id": "convergent-prev", "submodule": "diagnose", "synthesis": {"scenarios": []}}
    s_curr = session_a_regulatory()
    delta = compute_spread_delta(s_prev, s_curr)
    return {"row": "F", "subject": "Non-GP previous session → empty common set",
            "personas_added":   delta["personas_added"],
            "personas_removed": delta["personas_removed"],
            "common_deltas":    len(delta["personas"]),
            "PASS": (
                len(delta["personas"]) == 0
                and len(delta["personas_added"]) == 3    # all curr personas land as added
                and len(delta["personas_removed"]) == 0
            )}


# ──────────────────────────────────────────────────────────────────
# Auto-tune candidate-objectives prompt rows.
# ──────────────────────────────────────────────────────────────────


def row_g_prompt_baseline_byte_identical_when_no_blind_spots() -> Dict[str, Any]:
    """Row G — Without `divergent_blind_spots`, the prompt is BYTE-IDENTICAL
    to the prior path's behaviour. Load-bearing: JC-MON Stage 3.0
    proving slice should re-run cleanly without re-pinning."""
    base_docs = [
        {"name": "Strategic plan FY26", "extracted_text": "Reduce time-to-receivable by 18% YoY."},
        {"name": "Performance agreement", "extracted_text": "Owner is accountable for AR aging metric."},
    ]
    prompt_a = _build_candidates_prompt(base_docs=base_docs, context_label="Treasury")
    prompt_b = _build_candidates_prompt(base_docs=base_docs, context_label="Treasury",
                                        divergent_blind_spots=None)
    prompt_c = _build_candidates_prompt(base_docs=base_docs, context_label="Treasury",
                                        divergent_blind_spots=[])
    return {"row": "G", "subject": "No-blind-spots prompt path byte-identical",
            "a_eq_b": prompt_a == prompt_b,
            "a_eq_c": prompt_a == prompt_c,
            "PASS": prompt_a == prompt_b == prompt_c}


def row_h_prompt_includes_blind_spot_block_when_supplied() -> Dict[str, Any]:
    """Row H — With blind-spots, prompt grows the 'BLIND-SPOTS' block."""
    base_docs = [{"name": "Plan", "extracted_text": "Targets."}]
    bs = [
        "Cost-of-trust dimension the prior reads missed.",
        "Customer-felt tone not captured in compliance log.",
    ]
    p_with    = _build_candidates_prompt(base_docs=base_docs, divergent_blind_spots=bs)
    p_without = _build_candidates_prompt(base_docs=base_docs)
    has_block = "BLIND-SPOTS SURFACED BY A RECENT GET-PERSPECTIVES SESSION" in p_with
    has_both  = all(s in p_with for s in bs)
    grows     = len(p_with) > len(p_without)
    return {"row": "H", "subject": "Prompt grows BLIND-SPOTS block when supplied",
            "has_block": has_block,
            "has_both_blind_spots": has_both,
            "grew_by_bytes": len(p_with) - len(p_without),
            "PASS": has_block and has_both and grows}


def row_i_prompt_deterministic_blind_spot_order() -> Dict[str, Any]:
    """Row I — Same blind-spots passed in different order → identical prompt
    (deterministic sort enforced)."""
    base_docs = [{"name": "Plan", "extracted_text": "Targets."}]
    bs1 = ["Alpha blind-spot.", "Bravo blind-spot.", "Charlie blind-spot."]
    bs2 = ["Charlie blind-spot.", "Alpha blind-spot.", "Bravo blind-spot."]
    p1 = _build_candidates_prompt(base_docs=base_docs, divergent_blind_spots=bs1)
    p2 = _build_candidates_prompt(base_docs=base_docs, divergent_blind_spots=bs2)
    return {"row": "I", "subject": "Blind-spot order-independent (deterministic sort)",
            "byte_equal": p1 == p2,
            "PASS": p1 == p2}


def row_j_prompt_dedupes_and_strips_blank_blind_spots() -> Dict[str, Any]:
    """Row J — Duplicate blind-spots dedupe; blank strings stripped."""
    base_docs = [{"name": "Plan", "extracted_text": "Targets."}]
    bs = ["Alpha.", "alpha.", "Alpha.", "", "   ", "Bravo."]  # dupe + 2 blanks
    p = _build_candidates_prompt(base_docs=base_docs, divergent_blind_spots=bs)
    counts = {label: p.count(f"- {label}") for label in ("Alpha.", "alpha.", "Bravo.")}
    return {"row": "J", "subject": "Blind-spots dedupe + strip blank",
            "counts": counts,
            "PASS": (counts.get("Alpha.") == 1
                     and counts.get("alpha.") == 1   # case-sensitive — both kept
                     and counts.get("Bravo.") == 1)}


async def main():
    print("=" * 70)
    print("JC-TL Spread-heatmap + Auto-tune — proving slice")
    print("=" * 70)
    t0 = time.time()
    rows = [
        ("A", row_a_identical_sessions_zero_delta),
        ("B", row_b_shifted_confidence),
        ("C", row_c_persona_added_and_removed),
        ("D", row_d_breadth_delta_positive),
        ("E", row_e_blind_spots_added),
        ("F", row_f_non_gp_session_returns_empty),
        ("G", row_g_prompt_baseline_byte_identical_when_no_blind_spots),
        ("H", row_h_prompt_includes_blind_spot_block_when_supplied),
        ("I", row_i_prompt_deterministic_blind_spot_order),
        ("J", row_j_prompt_dedupes_and_strips_blank_blind_spots),
    ]
    results = []
    for tag, fn in rows:
        t_row = time.time()
        try:
            r = fn()
        except Exception as exc:  # noqa: BLE001
            r = {"row": tag, "exception": f"{type(exc).__name__}: {exc}", "PASS": False}
        r["elapsed_s"] = round(time.time() - t_row, 3)
        results.append(r)
        verdict = "✓ PASS" if r.get("PASS") else "✗ FAIL"
        print(f"  Row {tag}: {verdict}")
        if not r.get("PASS"):
            print(f"     {json.dumps({k: v for k, v in r.items() if k != 'PASS'}, default=str)[:400]}")
    n_pass = sum(1 for r in results if r.get("PASS"))
    n_total = len(results)
    print()
    print("=" * 70)
    print(f"RESULT: {n_pass}/{n_total} GREEN")
    print(f"Total elapsed: {round(time.time() - t0, 2)}s")
    print("=" * 70)
    out_path = ART_DIR / f"slice_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps({
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "n_pass": n_pass, "n_total": n_total,
        "all_green": n_pass == n_total,
        "results": results,
    }, default=str, indent=2))
    print(f"Evidence → {out_path}")
    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    rc = asyncio.run(main())
    sys.exit(rc)
