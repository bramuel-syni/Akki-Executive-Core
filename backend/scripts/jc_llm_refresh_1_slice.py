"""LLM-REFRESH.1 — proving slice for the Feb 2026 model-string refresh.

Source of truth: `/app/memory/sprints/LLM_MODELS_REFRESH_MATRIX.md`
(per-call-site refresh diff). Surfaces touched in this sub-sprint:
  * `routers/chat.py::SUPPORTED_MODELS` (picker)
  * `routers/chat.py::DEFAULT_MODEL_ID`
  * `routers/chat.py::MODEL_FALLBACK_CASCADE`
  * `routers/governance.py::_MODEL_USAGE`
  * `services/synisense/pricing.py::PROVIDER_MODEL_PRICING`

NOT touched in this sub-sprint:
  * `routers/work_studio_export.py` — board-pack drafting; LLM-REFRESH.2
    moves the JC-TL Stage 1 byte-identity pin and gets its own dispatch.
  * `services/solva_v2/*` — narration/synthesis; LLM-REFRESH.3.

Run from the repo root:
    cd /app/backend && python scripts/jc_llm_refresh_1_slice.py
"""
from __future__ import annotations

import asyncio
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

from routers.chat import (  # noqa: E402
    SUPPORTED_MODELS, DEFAULT_MODEL_ID, MODEL_FALLBACK_CASCADE,
)
from routers.governance import _MODEL_USAGE  # noqa: E402
from services.synisense.pricing import (  # noqa: E402
    PROVIDER_MODEL_PRICING, flat_cost_for,
)


ART_DIR = Path("/app/memory/jc_artifacts/llm_refresh_1_evidence")
ART_DIR.mkdir(parents=True, exist_ok=True)


# Expected picker after LLM-REFRESH.1 (per matrix doc).
EXPECTED_PICKER_IDS = [
    "claude-opus-4-8",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
    "gpt-5-5",
    "gpt-5-4",
    "gemini-3-1-pro",
    "gemini-3-5-flash",
]
DELISTED_IDS = {
    "claude-opus-4-6",        # → 4-8
    "claude-sonnet-4-5",      # → 4-6 in picker
    "gpt-5-2",                # → 5-4
    "gemini-3-flash",         # → 3.5-flash
    "gemini-2-5-pro",         # delisted
    "gemini-2-5-flash",       # delisted
}
EXPECTED_DEFAULT = "claude-sonnet-4-6"
EXPECTED_CASCADE = [
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
]


def row_a_picker_shape() -> Dict[str, Any]:
    """Row A — Chat picker carries the 7 expected entries; no stale ids."""
    actual_ids = [m["id"] for m in SUPPORTED_MODELS]
    extra = [i for i in actual_ids if i not in EXPECTED_PICKER_IDS]
    missing = [i for i in EXPECTED_PICKER_IDS if i not in actual_ids]
    delisted_still_present = [i for i in actual_ids if i in DELISTED_IDS]
    return {
        "row": "A", "subject": "Picker shape",
        "actual_count": len(actual_ids),
        "expected_count": len(EXPECTED_PICKER_IDS),
        "extra_ids": extra,
        "missing_ids": missing,
        "delisted_still_present": delisted_still_present,
        "PASS": (
            len(actual_ids) == len(EXPECTED_PICKER_IDS)
            and not extra and not missing
            and not delisted_still_present
        ),
    }


def row_b_picker_model_strings() -> Dict[str, Any]:
    """Row B — Picker model strings drop dated aliases."""
    bad: List[Dict[str, str]] = []
    for m in SUPPORTED_MODELS:
        ms = m["model"]
        if "20250929" in ms or "20251001" in ms or "20260416" in ms:
            bad.append({"id": m["id"], "model": ms, "reason": "dated_alias"})
    return {
        "row": "B", "subject": "No dated aliases in picker",
        "bad_entries": bad,
        "PASS": not bad,
    }


def row_c_default_model() -> Dict[str, Any]:
    """Row C — DEFAULT_MODEL_ID points at the new workhorse."""
    return {
        "row": "C", "subject": "Default model id",
        "actual": DEFAULT_MODEL_ID,
        "expected": EXPECTED_DEFAULT,
        "PASS": DEFAULT_MODEL_ID == EXPECTED_DEFAULT,
    }


def row_d_cascade() -> Dict[str, Any]:
    """Row D — Fallback cascade is [4-6 → 4-5 → haiku-4-5]; no 3-7."""
    has_3_7 = any(m == "claude-sonnet-3-7" for m in MODEL_FALLBACK_CASCADE)
    return {
        "row": "D", "subject": "Fallback cascade shape",
        "actual":   MODEL_FALLBACK_CASCADE,
        "expected": EXPECTED_CASCADE,
        "has_sonnet_3_7": has_3_7,
        "PASS": MODEL_FALLBACK_CASCADE == EXPECTED_CASCADE and not has_3_7,
    }


def row_e_governance_taxonomy() -> Dict[str, Any]:
    """Row E — governance._MODEL_USAGE has refreshed keys."""
    keys = set(_MODEL_USAGE.keys())
    expected_keys = {
        "claude-sonnet-4-6", "claude-haiku-4-5",
        "gpt-5-4", "gemini-3-1-pro", "gemini-3-5-flash",
    }
    stale_keys = keys - expected_keys
    return {
        "row": "E", "subject": "Governance taxonomy keys",
        "actual_keys":   sorted(keys),
        "expected_keys": sorted(expected_keys),
        "stale_keys":    sorted(stale_keys),
        "PASS": keys == expected_keys,
    }


def row_f_pricing_new_entries() -> Dict[str, Any]:
    """Row F — Pricing table has entries for all new canonical models."""
    required = [
        ("anthropic", "claude-sonnet-4-6"),
        ("anthropic", "claude-opus-4-8"),
        ("openai",    "gpt-5.5"),
        ("openai",    "gpt-5.4"),
        ("gemini",    "gemini-3.5-flash"),
        ("gemini",    "gemini-3.1-pro"),
    ]
    missing = [k for k in required if k not in PROVIDER_MODEL_PRICING]
    return {
        "row": "F", "subject": "Pricing — new canonical entries present",
        "required":  required,
        "missing":   missing,
        "PASS": not missing,
    }


def row_g_pricing_stale_dropped() -> Dict[str, Any]:
    """Row G — Pricing table drops `gpt-4o`, `gpt-4o-mini`, `gemini-2.5-flash`."""
    stale = [
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o-mini"),
        ("gemini", "gemini-2.5-flash"),
    ]
    still_present = [k for k in stale if k in PROVIDER_MODEL_PRICING]
    return {
        "row": "G", "subject": "Pricing — stale entries dropped",
        "stale_check":   stale,
        "still_present": still_present,
        "PASS": not still_present,
    }


def row_h_pricing_legacy_kept() -> Dict[str, Any]:
    """Row H — Pricing table keeps Sonnet 4.5 legacy entry for cascade
    fallback + audit-row resolution, even though it's no longer in the
    picker."""
    needed = [
        ("anthropic", "claude-sonnet-4-5"),           # cascade fallback
        ("anthropic", "claude-sonnet-4-5-20250929"),  # historic audit rows
        ("anthropic", "claude-opus-4-5"),             # historic audit rows
        ("openai",    "gpt-5.2"),                     # historic audit rows
        ("gemini",    "gemini-3-flash"),              # legacy fast tier
        ("gemini",    "gemini-3-pro"),                # legacy
    ]
    missing = [k for k in needed if k not in PROVIDER_MODEL_PRICING]
    return {
        "row": "H", "subject": "Pricing — legacy entries kept",
        "needed":  needed,
        "missing": missing,
        "PASS": not missing,
    }


def row_i_pricing_lookup_resolves() -> Dict[str, Any]:
    """Row I — flat_cost_for() resolves for new + legacy models without
    falling back to DEFAULT_FLAT_USD_PER_CALL."""
    probes = [
        ("anthropic", "claude-sonnet-4-6", 0.0030),
        ("anthropic", "claude-opus-4-8",   0.0150),
        ("openai",    "gpt-5.5",           0.0030),
        ("openai",    "gpt-5.4",           0.0015),
        ("gemini",    "gemini-3.1-pro",    0.0040),
        ("gemini",    "gemini-3.5-flash",  0.0006),
    ]
    bad: List[Dict[str, Any]] = []
    for provider, model, expected in probes:
        actual = flat_cost_for(provider, model)
        if abs(actual - expected) > 1e-9:
            bad.append({"provider": provider, "model": model,
                        "expected": expected, "actual": actual})
    return {
        "row": "I", "subject": "Pricing lookup resolves new canonical models",
        "probes": probes,
        "bad":    bad,
        "PASS":   not bad,
    }


def row_j_cascade_models_in_pricing() -> Dict[str, Any]:
    """Row J — every model in the cascade has a pricing entry (so audit
    row cost-estimates don't fall back to DEFAULT)."""
    bad = []
    for model_id in MODEL_FALLBACK_CASCADE:
        # cascade ids carry the dash-style id; pricing uses the same id.
        if ("anthropic", model_id) not in PROVIDER_MODEL_PRICING:
            bad.append(model_id)
    return {
        "row": "J", "subject": "Cascade models all priced",
        "cascade": MODEL_FALLBACK_CASCADE,
        "unpriced": bad,
        "PASS": not bad,
    }


async def main():
    print("=" * 70)
    print("LLM-REFRESH.1 — model-string refresh proving slice")
    print("=" * 70)
    t0 = time.time()
    rows = [
        row_a_picker_shape,
        row_b_picker_model_strings,
        row_c_default_model,
        row_d_cascade,
        row_e_governance_taxonomy,
        row_f_pricing_new_entries,
        row_g_pricing_stale_dropped,
        row_h_pricing_legacy_kept,
        row_i_pricing_lookup_resolves,
        row_j_cascade_models_in_pricing,
    ]
    results = []
    for fn in rows:
        try:
            res = fn()
        except Exception as exc:  # noqa: BLE001
            res = {"row": fn.__name__, "exception": f"{type(exc).__name__}: {exc}", "PASS": False}
        results.append(res)
        verdict = "✓ PASS" if res.get("PASS") else "✗ FAIL"
        print(f"  {res.get('row')}: {verdict}")
        if not res.get("PASS"):
            print(f"     {json.dumps({k: v for k, v in res.items() if k != 'PASS'}, default=str)[:300]}")

    n_pass = sum(1 for r in results if r.get("PASS"))
    n_total = len(results)
    print()
    print("=" * 70)
    print(f"RESULT: {n_pass}/{n_total} GREEN")
    print(f"Total elapsed: {round(time.time() - t0, 2)}s")
    print("=" * 70)

    out_path = ART_DIR / f"slice_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps({
        "ran_at":   datetime.now(timezone.utc).isoformat(),
        "n_pass":   n_pass,
        "n_total":  n_total,
        "all_green": n_pass == n_total,
        "results":  results,
    }, default=str, indent=2))
    print(f"Evidence → {out_path}")

    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    rc = asyncio.run(main())
    sys.exit(rc)
