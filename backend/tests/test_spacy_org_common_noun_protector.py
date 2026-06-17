"""Phase 14 — spaCy ORG common-noun protector.

Pre-Phase-14, spaCy's NER tagged disease names like "Malaria" as ORG
(the screenshot symptom: "Malaria token suggests an organization").
The Phase 14 fix adds `_ORG_PROTECTOR_TERMS` — a narrow static
allow-list that drops spaCy ORG hits when the surface form matches.

This test loads the real spaCy model (no mocks per Phase 14 brief)
and runs the full deidentifier path over three representative inputs:
  - "Malaria is endemic..." → Malaria MUST NOT be redacted
  - "Following the meeting..." → Following MUST NOT be redacted
  - "Apple Inc reported earnings..." → Apple Inc MUST still be
    redacted (the protector is narrow; real ORGs are unaffected)
"""
from __future__ import annotations

import pytest

from services.synisense.shield import deidentifier as dx


pytestmark = pytest.mark.asyncio


async def test_malaria_disease_name_not_redacted_as_org():
    """User-screenshot reproduction: 'Malaria' must not be tagged ORG."""
    result = await dx.deidentify(
        "Malaria is endemic in the region.",
        tenant_id="phase14-org-protector-disease",
        purpose="chat.standard_response",
    )
    assert "Malaria" in result.redacted_text, (
        f"Phase 14 ORG protector failed — 'Malaria' was redacted. "
        f"Got: {result.redacted_text!r}"
    )
    # No ORG token should appear at all in this sentence.
    assert "[[ENT_ORG_" not in result.redacted_text, (
        f"Unexpected ORG redaction: {result.redacted_text!r}"
    )


async def test_following_generic_capitalised_noun_not_redacted():
    """'Following' at sentence-start sometimes tags as ORG. Protector
    must catch."""
    result = await dx.deidentify(
        "Following the meeting, we agreed on the next steps.",
        tenant_id="phase14-org-protector-following",
        purpose="chat.standard_response",
    )
    assert "Following" in result.redacted_text, (
        f"Phase 14 ORG protector failed — 'Following' was redacted. "
        f"Got: {result.redacted_text!r}"
    )


async def test_genuine_company_still_redacted_as_org():
    """The protector is narrow; real ORGs must still be caught."""
    result = await dx.deidentify(
        "Apple Inc reported earnings this quarter.",
        tenant_id="phase14-org-protector-real-org",
        purpose="chat.standard_response",
    )
    # Apple Inc must be redacted (it is a genuine ORG, NOT in
    # _ORG_PROTECTOR_TERMS).
    assert "Apple Inc" not in result.redacted_text, (
        f"Phase 14 ORG protector was too aggressive — 'Apple Inc' "
        f"survived redaction. Got: {result.redacted_text!r}"
    )
    assert "[[ENT_ORG_" in result.redacted_text, (
        f"Genuine ORG entity must produce an ORG token. "
        f"Got: {result.redacted_text!r}"
    )


def test_org_protector_terms_constant_exported():
    assert hasattr(dx, "_ORG_PROTECTOR_TERMS")
    assert isinstance(dx._ORG_PROTECTOR_TERMS, frozenset)
    assert "malaria" in dx._ORG_PROTECTOR_TERMS  # disease bucket
    assert "monday" in dx._ORG_PROTECTOR_TERMS   # weekday bucket
    assert "january" in dx._ORG_PROTECTOR_TERMS  # month bucket
    assert "following" in dx._ORG_PROTECTOR_TERMS  # generic-noun bucket


def test_org_protector_terms_does_not_overreach():
    """Sanity-check the protector list isn't accidentally including
    real proper nouns or brand names. Negative cases that must NOT
    be in the list."""
    assert "apple" not in dx._ORG_PROTECTOR_TERMS
    assert "google" not in dx._ORG_PROTECTOR_TERMS
    assert "akki" not in dx._ORG_PROTECTOR_TERMS
    assert "claude" not in dx._ORG_PROTECTOR_TERMS
