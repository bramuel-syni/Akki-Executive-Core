"""Phase 14 — tenant entity length floor (≥ 4 chars).

Pre-Phase-14, `tenant_entities.harvest()` and `lookup_in_text()`
accepted any non-empty entity. A 2-char entry like "Le" or "On" in
the tenant catalogue would word-boundary-match the prefix of longer
words like "Lemonrr" → leave `"monrr"` raw in the prompt → user sees
the "onrr" fragment in the LLM's reply (the screenshot symptom).

This test injects a synthetic in-memory catalogue and asserts the
≥ 4 chars filter at LOOKUP time. (The harvester filter is tested
implicitly by the lookup path — the lookup is the last line of
defence against a stale cache.)
"""
from __future__ import annotations

import time

import pytest

from services.synisense.shield import tenant_entities as te


pytestmark = pytest.mark.asyncio


def _patch_cache(monkeypatch, tenant_id: str, entries):
    """Force the in-memory cache to return our test catalogue.
    Note `_CACHE_LOADED_AT` holds `time.monotonic()` floats."""
    catalogue = [
        {"entity_text": e, "entity_type": "ORG"} for e in entries
    ]
    monkeypatch.setitem(te._CACHE, tenant_id, catalogue)
    monkeypatch.setitem(te._CACHE_LOADED_AT, tenant_id, time.monotonic())


async def test_lookup_skips_short_catalogue_entries(monkeypatch):
    """Length floor: entries < 4 chars must be skipped at lookup
    even if they survived in a stale cache."""
    tid = "tenant-phase14-lookup"
    _patch_cache(
        monkeypatch, tid,
        ["Le", "On", "Bra", "Bram", "Bramuel", "Mary Anne"],
    )
    hits = await te.lookup_in_text(
        "Lemonrr Bramuel Mary Anne Onorrible Bram zero",
        tenant_id=tid,
    )
    matched = sorted({h["match"] for h in hits})
    # 4+ char entries: Bram (matched alone) + Bramuel + Mary Anne.
    # 2-3 char entries: Le, On, Bra MUST NOT match.
    assert "Bramuel" in matched
    assert "Mary Anne" in matched
    assert "Bram" in matched  # 4 chars, word-boundary "Bram zero" hit
    assert "Le" not in matched, (
        f"Phase 14 length floor violated — 'Le' (2 chars) matched. hits={matched}"
    )
    assert "On" not in matched, (
        f"Phase 14 length floor violated — 'On' (2 chars) matched. hits={matched}"
    )
    assert "Bra" not in matched, (
        f"Phase 14 length floor violated — 'Bra' (3 chars) matched. hits={matched}"
    )


async def test_lookup_does_not_leave_fragment_in_remaining_text(monkeypatch):
    """Direct check of the `onrr`-fragment regression — a 2-char
    entity like 'Le' must not eat the start of 'Lemonrr' and leave
    'monrr' raw."""
    tid = "tenant-phase14-fragment"
    _patch_cache(monkeypatch, tid, ["Le"])  # the pre-Phase-14 bug seed
    hits = await te.lookup_in_text("Lemonrr is a name.", tenant_id=tid)
    # Length-floor must prevent the prefix match entirely. Zero hits.
    assert hits == [], (
        f"Phase 14 length floor failed to suppress the 2-char 'Le' "
        f"prefix bite. hits={hits}"
    )


async def test_lookup_accepts_exactly_4_char_entries(monkeypatch):
    """Boundary inclusive — 4 chars is the floor."""
    tid = "tenant-phase14-boundary"
    _patch_cache(monkeypatch, tid, ["Acme"])
    hits = await te.lookup_in_text("Acme has reported earnings.", tenant_id=tid)
    assert any(h["match"] == "Acme" for h in hits), (
        f"Phase 14 floor must INCLUDE 4-char entries. hits={hits}"
    )
