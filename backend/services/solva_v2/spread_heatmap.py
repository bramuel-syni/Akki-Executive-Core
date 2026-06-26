"""JC-TL Spread-Heatmap Delta — per-persona confidence_pct drift.

Source of truth: `/app/memory/JC_TL_CANONICAL_SPEC.md` §4
(Get-Perspectives — DIVERGE to a spread). User direction at
AUTONOMOUS BACKLOG RUN (2026-06-26):

> "Spread-heatmap delta — Per-persona `confidence_pct` drift
> across consecutive GP sessions. Schema-only addition + one
> charting helper, no new exporter mode. Implement only after
> GP ships (it needs GP session output as input signal)."

GP ship closed 2026-06-26 (6/6 GREEN proving slice). This module
is the schema-only delta computation; FE charting is a downstream
dispatch when the user steers it.

Contract:

  compute_spread_delta(session_prev, session_curr) -> SpreadDelta

  where SpreadDelta = {
    "previous_session_id":  str,
    "current_session_id":   str,
    "personas":             [PersonaDelta dicts],
    "personas_added":       [str],     # personas in curr, not in prev
    "personas_removed":     [str],     # personas in prev, not in curr
    "spread_breadth_delta": float,     # (curr max - curr min) - (prev max - prev min)
    "blind_spots_added":    [str],     # blind-spot labels surfaced this session
    "blind_spots_removed":  [str],
  }

  PersonaDelta = {
    "persona_label":      str,
    "previous_pct":       int,
    "current_pct":        int,
    "delta_pct":          int,         # current - previous
    "direction":          "up"|"down"|"stable",
  }

Pure / deterministic / no LLM / no IO. Used by:
  • The FE charting helper (future dispatch) that renders the
    delta as a heatmap row.
  • The auto-tune candidate-objectives path
    (`monitor_candidate_objectives` engine) — blind_spots_added
    feeds in as a fresh signal.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


_STABLE_THRESHOLD_PCT = 2  # absolute delta ≤ 2 pct → "stable"


def _extract_personas(session: Dict[str, Any]) -> Dict[str, int]:
    """Lift `{persona_label: confidence_pct}` from a GP session.

    Returns `{}` if the session is not a Get-Perspectives session
    OR has no perspective_spread populated. Caller-friendly:
    `compute_spread_delta` treats both sides symmetrically and an
    empty dict means "no overlap" without raising.
    """
    submod = (session.get("submodule") or "").lower()
    if submod not in {"get_perspective", "get-perspectives"}:
        return {}
    synth = session.get("synthesis") or {}
    spread = synth.get("perspective_spread") or {}
    personas = spread.get("personas") or []
    out: Dict[str, int] = {}
    for p in personas:
        label = (p.get("persona_label") or "").strip()
        if not label:
            continue
        try:
            pct = int(p.get("confidence_pct") or 0)
        except (TypeError, ValueError):
            continue
        out[label] = pct
    return out


def _extract_blind_spots(session: Dict[str, Any]) -> List[str]:
    """Lift blind-spot descriptions from a GP session as a stable list."""
    submod = (session.get("submodule") or "").lower()
    if submod not in {"get_perspective", "get-perspectives"}:
        return []
    synth = session.get("synthesis") or {}
    spread = synth.get("perspective_spread") or {}
    bs = spread.get("blind_spots") or []
    out: List[str] = []
    for b in bs:
        desc = (b.get("blind_spot_description") or "").strip()
        if desc:
            out.append(desc)
    return out


def _direction(delta: int) -> str:
    if delta > _STABLE_THRESHOLD_PCT:
        return "up"
    if delta < -_STABLE_THRESHOLD_PCT:
        return "down"
    return "stable"


def compute_spread_delta(
    session_prev: Dict[str, Any],
    session_curr: Dict[str, Any],
) -> Dict[str, Any]:
    """Per-persona confidence_pct drift between two GP sessions.

    Both arguments must be Get-Perspectives sessions with
    `synthesis.perspective_spread` populated. If either side has
    no perspectives, the function returns a well-formed empty
    delta rather than raising — callers benefit from a stable
    shape regardless of input completeness.

    Determinism: persona_label is a sort key, so the output
    ordering is byte-stable for identical inputs.
    """
    prev_personas = _extract_personas(session_prev)
    curr_personas = _extract_personas(session_curr)
    prev_blind = set(_extract_blind_spots(session_prev))
    curr_blind = set(_extract_blind_spots(session_curr))

    common = sorted(set(prev_personas.keys()) & set(curr_personas.keys()))
    added = sorted(set(curr_personas.keys()) - set(prev_personas.keys()))
    removed = sorted(set(prev_personas.keys()) - set(curr_personas.keys()))

    deltas: List[Dict[str, Any]] = []
    for label in common:
        p_prev = prev_personas[label]
        p_curr = curr_personas[label]
        d = p_curr - p_prev
        deltas.append({
            "persona_label": label,
            "previous_pct":  p_prev,
            "current_pct":   p_curr,
            "delta_pct":     d,
            "direction":     _direction(d),
        })

    # Spread breadth = max - min of confidence_pct within session.
    def _breadth(d: Dict[str, int]) -> int:
        if not d:
            return 0
        vs = list(d.values())
        return max(vs) - min(vs)

    breadth_delta = _breadth(curr_personas) - _breadth(prev_personas)

    return {
        "previous_session_id":  session_prev.get("id"),
        "current_session_id":   session_curr.get("id"),
        "personas":             deltas,
        "personas_added":       added,
        "personas_removed":     removed,
        "spread_breadth_delta": breadth_delta,
        "blind_spots_added":    sorted(curr_blind - prev_blind),
        "blind_spots_removed":  sorted(prev_blind - curr_blind),
    }


__all__ = ["compute_spread_delta"]
