"""Synisense — illustrative per-provider/per-model pricing table.

Phase F (2026-05-16). Code-controlled (NOT API-editable) — same
governance pattern as `ALLOWED_PURPOSES` in `config.py`.

Values are ILLUSTRATIVE approximations for the bank-QA billing
estimate surface. They are NOT committed pricing, NOT invoiced, and
the frontend MUST mark every figure as "estimated" prominently.

Each entry: `(input_usd_per_million_tokens, output_usd_per_million_tokens,
flat_usd_per_call_assumption)`. We use a flat-per-call estimate
because the Shield audit log doesn't record token counts today —
that's a Phase G+ task once real metering is in place.
"""
from __future__ import annotations

from typing import Dict, Tuple

# (per_million_input_USD, per_million_output_USD, flat_per_call_USD_estimate)
#
# LLM-REFRESH.1 (2026-06-26) — refreshed against the Feb 2026 canonical
# matrix in `memory/sprints/LLM_MODELS_REFRESH_MATRIX.md`. Provisional
# pricing for new model rows assumes parity with the immediately
# preceding generation; operator should reconcile against current
# provider pricing pages at any deliberate cost-review pass.
PROVIDER_MODEL_PRICING: Dict[Tuple[str, str], Tuple[float, float, float]] = {
    # ── Anthropic ─────────────────────────────────────────────────────
    ("anthropic", "claude-sonnet-4-6"):          (3.00, 15.00, 0.0030),  # current workhorse
    ("anthropic", "claude-sonnet-4-5"):          (3.00, 15.00, 0.0030),  # prior workhorse — kept for legacy reads + cascade fallback
    ("anthropic", "claude-sonnet-4-5-20250929"): (3.00, 15.00, 0.0030),  # historic audit rows
    ("anthropic", "claude-haiku-4-5"):           (0.80, 4.00,  0.0008),
    ("anthropic", "claude-opus-4-8"):            (15.00, 75.00, 0.0150),  # current top-tier (provisional pricing)
    ("anthropic", "claude-opus-4-5"):            (15.00, 75.00, 0.0150),  # prior top-tier — kept for legacy reads
    # ── OpenAI ────────────────────────────────────────────────────────
    ("openai",    "gpt-5.5"):                    (2.50, 20.00, 0.0030),
    ("openai",    "gpt-5.4"):                    (1.25, 10.00, 0.0015),
    ("openai",    "gpt-5.2"):                    (1.25, 10.00, 0.0015),  # legacy — kept for audit row resolution
    # ── Google ────────────────────────────────────────────────────────
    ("gemini",    "gemini-3.5-flash"):           (0.30, 1.20,  0.0006),  # current fast tier
    ("gemini",    "gemini-3-flash"):             (0.50, 2.00,  0.0010),  # prior fast tier — kept for legacy reads
    ("gemini",    "gemini-3-pro"):               (1.25, 5.00,  0.0025),  # kept for legacy reads
    ("gemini",    "gemini-3.1-pro"):             (2.00, 8.00,  0.0040),  # current top-tier
}

# Fallback for unknown combinations — conservative midpoint.
DEFAULT_FLAT_USD_PER_CALL = 0.0020


def flat_cost_for(provider: str, model: str) -> float:
    """Return the per-call flat USD estimate for a (provider, model)
    pair, falling back to the default if unknown."""
    key = (provider or "", model or "")
    entry = PROVIDER_MODEL_PRICING.get(key)
    if entry is None:
        # Try matching by provider alone (model variants).
        for (p, _), v in PROVIDER_MODEL_PRICING.items():
            if p == provider:
                return v[2]
        return DEFAULT_FLAT_USD_PER_CALL
    return entry[2]
