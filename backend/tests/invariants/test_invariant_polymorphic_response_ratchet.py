"""Phase 5.2 Part B — invariant: polymorphic-response routes must ratchet down.

The Phase 5.2 Part B dispatch targets the ~49 `Optional[Dict[str, Any]]`
response-model routes that remain in `backend/routers/`. These are the
"polymorphic surfaces" left after Phase 3.1 narrowed the obvious cases
into `contracts/responses.py`'s open-shape models.

This invariant pins the current count at a baseline and fails the build
if any new `Optional[Dict[str, Any]]` route is ADDED (count would
go UP). It also asserts that the marker count (`phase-3.0:narrow-in-3.1`)
stays in lock-step — drift between marker count and response-model count
means someone narrowed a route without removing the TODO marker (or vice
versa, removed the marker without narrowing).

The pattern is the canonical ratchet — same shape as Phase 4.3's
boundary-imports invariant. Tightenings (narrowings) are allowed; new
loosenings (more polymorphic routes) are not.

When a route is narrowed in a future sprint:
  1. Replace `response_model=Optional[Dict[str, Any]]` with the new
     specific Pydantic model.
  2. Remove the `# phase-3.0:narrow-in-3.1` marker on that line.
  3. Run a wire-byte-equivalence check (the harness below provides one
     per-route plumbing helper).
  4. Decrement `_BASELINE_POLY_ROUTE_COUNT` and
     `_BASELINE_NARROW_MARKER_COUNT` by 1 each in this file.

Wire-byte equivalence harness (companion utility):
  See `_compute_response_model_count()` for the canonical grep used by
  the OpenAPI ratchet check. The Phase 4.4 dual-mount smoke continues
  to be the authoritative public-surface contract (sha pins).
"""
from __future__ import annotations

import re
from pathlib import Path


ROUTERS_DIR = Path(__file__).resolve().parents[2] / "routers"

# Baseline captured 2026-06-24 (Phase 5.4 Narrowing Batch 1 close — was 49 / 55
# at Phase 5.2; 7 routes narrowed in this batch via codemod 002).
# Decrement by 1 every time a route is narrowed.
_BASELINE_POLY_ROUTE_COUNT = 42

# `# phase-3.0:narrow-in-3.1` markers across all routers. Some markers
# appear on `List[Dict[str, Any]]` shapes (not response_model lines)
# so this count is slightly higher than the route count.
_BASELINE_NARROW_MARKER_COUNT = 48

# The grep pattern that defines a "polymorphic response-model route".
# Matches FastAPI handler decorators with `response_model=Optional[Dict[str, Any]]`
# or `response_model=Dict[str, Any]`. The regex tolerates whitespace
# variations.
_POLY_RESPONSE_RE = re.compile(
    r"""response_model\s*=\s*(?:Optional\s*\[\s*Dict\s*\[\s*str\s*,\s*Any\s*\]\s*\]|Dict\s*\[\s*str\s*,\s*Any\s*\])""",
)

_NARROW_MARKER_RE = re.compile(r"#\s*phase-3\.0\s*:\s*narrow-in-3\.1")


def _compute_response_model_count() -> int:
    """Count `Optional[Dict[str, Any]]` response_model occurrences across
    all router files. This is the canonical Phase 5.2 Part B metric."""
    count = 0
    for path in ROUTERS_DIR.rglob("*.py"):
        try:
            body = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        count += len(_POLY_RESPONSE_RE.findall(body))
    return count


def _compute_narrow_marker_count() -> int:
    """Count `# phase-3.0:narrow-in-3.1` markers across all router files."""
    count = 0
    for path in ROUTERS_DIR.rglob("*.py"):
        try:
            body = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        count += len(_NARROW_MARKER_RE.findall(body))
    return count


def test_polymorphic_response_routes_only_ratchet_down() -> None:
    """`Optional[Dict[str, Any]]` route count must not grow.

    Decrement `_BASELINE_POLY_ROUTE_COUNT` when a route is narrowed —
    do NOT increment it. New routes MUST ship with a concrete response
    model from `contracts/responses.py` (or add a new model there).
    """
    actual = _compute_response_model_count()
    assert actual <= _BASELINE_POLY_ROUTE_COUNT, (
        f"Phase 5.2 Part B invariant — polymorphic-response-route count "
        f"grew: actual={actual} > baseline={_BASELINE_POLY_ROUTE_COUNT}.\n\n"
        f"A new FastAPI route was added with "
        f"`response_model=Optional[Dict[str, Any]]` (or `Dict[str, Any]`). "
        f"This is not allowed in Phase 5.2+. Define a specific Pydantic "
        f"model in `contracts/responses.py` and use that instead.\n\n"
        f"If the route's response shape is genuinely polymorphic, define "
        f"a `Union[...]` with a discriminator field."
    )
    # Tightening signal: if the actual count is below baseline, the
    # invariant still passes — encourage decrementing the baseline so
    # the ratchet stays meaningful.
    if actual < _BASELINE_POLY_ROUTE_COUNT:
        # Soft signal — not a failure. The grep is the contract; the
        # baseline is the "yardstick we expect to ratchet down".
        pass


def test_narrow_marker_count_in_lockstep() -> None:
    """`# phase-3.0:narrow-in-3.1` marker count must not drift away from
    the polymorphic-route count.

    Markers can be slightly higher than route count because some markers
    sit on `List[Dict[str, Any]]` non-response_model lines. But the gap
    must stay within a small tolerance — large drift means someone
    narrowed a route without removing the marker (or removed a marker
    without narrowing).
    """
    actual = _compute_narrow_marker_count()
    assert actual <= _BASELINE_NARROW_MARKER_COUNT, (
        f"Phase 5.2 Part B invariant — `phase-3.0:narrow-in-3.1` marker "
        f"count grew: actual={actual} > baseline={_BASELINE_NARROW_MARKER_COUNT}.\n\n"
        f"New polymorphic-shape TODO marker added. Either narrow the route "
        f"now (preferred) or, if genuinely necessary to ship as polymorphic, "
        f"increment `_BASELINE_NARROW_MARKER_COUNT` in this test AND document "
        f"the rationale in the sprint memo."
    )


def test_response_model_count_and_marker_count_align() -> None:
    """The two metrics must stay within a small tolerance — drift means
    a route was narrowed but the marker wasn't removed (or vice versa)."""
    route_count = _compute_response_model_count()
    marker_count = _compute_narrow_marker_count()
    # Markers can be slightly higher (List[Dict[str, Any]] cases without
    # response_model). Tolerance: ≤ 10 marker-over-route.
    gap = marker_count - route_count
    assert -2 <= gap <= 10, (
        f"Phase 5.2 Part B invariant — marker/route count drift: "
        f"markers={marker_count}, routes={route_count}, gap={gap}.\n\n"
        f"A route was narrowed but its `# phase-3.0:narrow-in-3.1` marker "
        f"was not removed (or vice versa). Bring them back into lock-step "
        f"by either removing the orphaned marker or re-narrowing the route."
    )
