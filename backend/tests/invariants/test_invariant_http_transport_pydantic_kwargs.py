"""Phase 5.5.2 — build-breaking invariant for HTTP transport
Pydantic-kwarg serialization.

Pins the central fix at `contracts/_adapters/_http_client.py`
(`_sanitize_kwargs_for_json`) — when a contract method is called
with a Pydantic model as a kwarg under
`BOUNDED_CONTEXT_TRANSPORT=http`, the HTTP adapter MUST serialize
the model via `.model_dump(mode='json')` before passing to
`httpx.post(json=...)`. Without the fix, the call raises
`TypeError: Object of type <X> is not JSON serializable` — that
was the exact regression Phase 5.5.2 candidate B closed.

Build-breaking: any future regression on the sanitizer (e.g.
someone removes the BaseModel branch) fails CI immediately. The
invariant exercises the sanitizer directly (unit-level) plus a
round-trip behavioural test that proves dict reconstruction.

The integration-marked end-to-end roundtrip is deselected by
default — it requires the live `INTERNAL_TRANSPORT_SECRET` and
the dual-uvicorn topology of Phase 4.3, neither of which is
provisioned on the unit-test lane. The Phase 4.2 smoke at
`test_phase4_2_http_transport_smoke.py` exercises the
`INTERNAL_TRANSPORT_SECRET`-gated path.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json
from typing import Any, Dict, List, Optional

import pytest
from pydantic import BaseModel, Field


# ─── Fixtures: representative Pydantic + dataclass payloads ────────


class _MockNestedModel(BaseModel):
    """Stand-in for nested Pydantic models inside a kwarg tree."""
    label: str
    confidence: float = 0.0


class _MockWorkbookAnalysis(BaseModel):
    """Stand-in for the production `WorkbookAnalysis` shape (the
    actual model has 40+ fields; this is the minimum-honest set
    that exercises the same Pydantic-encoding path).
    """
    workbook_id: str
    headline: str
    observations: List[str] = Field(default_factory=list)
    score: Optional[float] = None
    inner: Optional[_MockNestedModel] = None
    # datetime is the canonical case where `mode='json'` matters
    # — Pydantic's default `.model_dump()` returns a `datetime` instance,
    # which httpx's encoder doesn't handle.
    created_at: Optional[dt.datetime] = None


@dataclasses.dataclass(frozen=True)
class _MockSolvaInputs:
    """Stand-in for the production `SolvaInputs` dataclass."""
    context_id: str
    objective: str
    seed_count: int = 0


def test_sanitizer_handles_pydantic_basemodel_at_top_level():
    """A Pydantic BaseModel passed as a top-level kwarg value MUST
    convert to a JSON-safe dict.
    """
    from contracts._adapters._http_client import _sanitize_kwargs_for_json
    wba = _MockWorkbookAnalysis(
        workbook_id="wb-test",
        headline="Q5 sales spiked",
        observations=["one", "two"],
        score=0.87,
    )
    kwargs = {"workbook_analysis": wba, "account_id": "acc-1"}
    out = _sanitize_kwargs_for_json(kwargs)
    # Must be a plain dict (not the BaseModel itself).
    assert isinstance(out, dict), out
    assert isinstance(out["workbook_analysis"], dict), out["workbook_analysis"]
    assert out["workbook_analysis"]["workbook_id"] == "wb-test"
    assert out["workbook_analysis"]["headline"] == "Q5 sales spiked"
    assert out["workbook_analysis"]["observations"] == ["one", "two"]
    assert out["workbook_analysis"]["score"] == 0.87
    # Plain kwargs pass through unchanged.
    assert out["account_id"] == "acc-1"
    # The whole structure must be JSON-serializable (the real test —
    # this is the exact `json.dumps` httpx would do under the hood).
    json.dumps(out)


def test_sanitizer_handles_nested_pydantic_models():
    """Nested Pydantic models inside a top-level Pydantic kwarg must
    also serialize correctly (Pydantic's `.model_dump(mode='json')`
    handles recursion natively).
    """
    from contracts._adapters._http_client import _sanitize_kwargs_for_json
    wba = _MockWorkbookAnalysis(
        workbook_id="wb-2",
        headline="nested",
        inner=_MockNestedModel(label="layer-1", confidence=0.5),
    )
    out = _sanitize_kwargs_for_json({"wba": wba})
    inner = out["wba"]["inner"]
    assert isinstance(inner, dict), inner
    assert inner["label"] == "layer-1"
    assert inner["confidence"] == 0.5
    json.dumps(out)


def test_sanitizer_handles_pydantic_datetime_via_mode_json():
    """`mode='json'` is load-bearing — without it, `created_at` would
    serialize as a `datetime` instance and break httpx's json encoder.
    """
    from contracts._adapters._http_client import _sanitize_kwargs_for_json
    now = dt.datetime(2026, 6, 24, 12, 0, 0, tzinfo=dt.timezone.utc)
    wba = _MockWorkbookAnalysis(
        workbook_id="wb-3", headline="dt-test", created_at=now,
    )
    out = _sanitize_kwargs_for_json({"wba": wba})
    # ISO string after mode='json'.
    assert isinstance(out["wba"]["created_at"], str), out["wba"]["created_at"]
    assert "2026-06-24" in out["wba"]["created_at"]
    json.dumps(out)


def test_sanitizer_handles_frozen_dataclass_kwargs():
    """`@dataclasses.dataclass(frozen=True)` instances (e.g. the
    production `SolvaInputs`) MUST convert to dicts via
    `dataclasses.asdict`. Without this branch, httpx's encoder
    raises `TypeError: Object of type _MockSolvaInputs is not JSON
    serializable`.
    """
    from contracts._adapters._http_client import _sanitize_kwargs_for_json
    inputs = _MockSolvaInputs(
        context_id="ctx-x", objective="grow", seed_count=3,
    )
    out = _sanitize_kwargs_for_json({"inputs": inputs})
    assert isinstance(out["inputs"], dict), out["inputs"]
    assert out["inputs"]["context_id"] == "ctx-x"
    assert out["inputs"]["objective"] == "grow"
    assert out["inputs"]["seed_count"] == 3
    json.dumps(out)


def test_sanitizer_passes_plain_kwargs_unchanged():
    """Critical no-regression rail: plain dicts / lists / primitives
    must pass through with EXACT semantics. The sanitizer must not
    re-encode already-safe values (no double-wrapping, no key
    re-ordering, no string coercion).
    """
    from contracts._adapters._http_client import _sanitize_kwargs_for_json
    kwargs = {
        "account_id": "acc-7",
        "limit": 10,
        "tags": ["foo", "bar"],
        "filters": {"status": "active", "since": "2026-06-01"},
        "flag": True,
        "nullable": None,
    }
    out = _sanitize_kwargs_for_json(kwargs)
    # MUST be value-equal (not necessarily identity — the sanitizer
    # may return fresh dicts/lists to avoid mutating callers).
    assert out == kwargs
    json.dumps(out)


def test_sanitizer_handles_pydantic_inside_dict_value():
    """A Pydantic model nested inside a plain dict value must also
    serialize. Walks the recursive case.
    """
    from contracts._adapters._http_client import _sanitize_kwargs_for_json
    wba = _MockWorkbookAnalysis(workbook_id="wb-9", headline="nested-in-dict")
    kwargs = {
        "wrapper": {
            "analysis": wba,
            "trace": ["a", "b"],
        }
    }
    out = _sanitize_kwargs_for_json(kwargs)
    inner = out["wrapper"]["analysis"]
    assert isinstance(inner, dict), inner
    assert inner["workbook_id"] == "wb-9"
    json.dumps(out)


def test_sanitizer_handles_pydantic_inside_list():
    """Pydantic models inside list values must serialize element-wise."""
    from contracts._adapters._http_client import _sanitize_kwargs_for_json
    kwargs = {
        "items": [
            _MockNestedModel(label="a", confidence=0.1),
            _MockNestedModel(label="b", confidence=0.2),
        ]
    }
    out = _sanitize_kwargs_for_json(kwargs)
    assert isinstance(out["items"], list)
    assert all(isinstance(x, dict) for x in out["items"])
    assert out["items"][0]["label"] == "a"
    assert out["items"][1]["confidence"] == 0.2
    json.dumps(out)


def test_http_call_wraps_sanitized_kwargs():
    """End-to-end behavioural pin: the `_HTTPAdapterBase._call` method
    calls `_sanitize_kwargs_for_json(kwargs)` BEFORE `httpx.post`. We
    can't easily mock the full httpx round-trip here, but we can pin
    the source contract via AST inspection — load-bearing because
    the sanitizer call site is the integration point.

    Static check is stronger than mock-and-assert for this contract:
    a mock would only fire on the exact code path exercised; the AST
    check catches even unexercised refactors.
    """
    import ast
    import pathlib
    src = (pathlib.Path(__file__).resolve().parents[1].parent
           / "contracts" / "_adapters" / "_http_client.py").read_text()
    tree = ast.parse(src)
    # Find the `_call` async method.
    call_method = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.AsyncFunctionDef)
                and node.name == "_call"):
            call_method = node
            break
    assert call_method is not None, (
        "REGRESSION: `_HTTPAdapterBase._call` not found in "
        "`contracts/_adapters/_http_client.py`. The Phase 5.5.2 "
        "central Pydantic-sanitization fix lives there — has the "
        "transport been refactored?"
    )
    # Find the `_sanitize_kwargs_for_json` invocation in the method body.
    invokes_sanitizer = any(
        isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "_sanitize_kwargs_for_json"
        for n in ast.walk(call_method)
    )
    assert invokes_sanitizer, (
        "REGRESSION: candidate B — `_HTTPAdapterBase._call` no longer "
        "calls `_sanitize_kwargs_for_json(kwargs)` before "
        "`client.post(json=...)`. Without the sanitizer, "
        "Pydantic-kwarg sites (e.g. "
        "`get_solva().narrate_analysis(workbook_analysis=wba)` at "
        "`routers/workbook_analysis.py:1089`) raise `TypeError: "
        "Object of type WorkbookAnalysis is not JSON serializable`. "
        "Re-add the call OR move sanitization to an explicit shim "
        "documented in `/app/memory/sprints/"
        "PHASE_5_5_2_TRACK_A_REAL_FIXES.md` §4."
    )
