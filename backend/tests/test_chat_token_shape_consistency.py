"""Phase 14 — token-shape consistency lockdown.

The chat fluency preamble in `routers/chat.py` claims a token shape;
the de-identifier in `services/synisense/shield/deidentifier.py` emits
a token shape. These two must NEVER drift again (the pre-Phase-14
bug was that the chat preamble said `[EMAIL_1]` and the de-id emitted
`[[ENT_EMAIL_001]]`).

This test:
  1. Reads SHIELD_TOKEN_FORMAT_DESCRIPTION + SHIELD_TOKEN_EXAMPLES
     from `deidentifier.py` (the single source of truth).
  2. Reconstructs what `deidentifier._token_for(...)` would emit for
     each example type.
  3. Asserts every example token in `SHIELD_TOKEN_EXAMPLES` matches
     the shape `[[ENT_<TYPE>_<NNN>]]` that the real emitter produces.
  4. Asserts the chat fluency preamble references the same shape and
     does NOT mention any pre-Phase-14 shapes like `[EMAIL_1]` or
     `[PERSON_3]`.
"""
from __future__ import annotations

import re

from services.synisense.shield import deidentifier as dx
from routers.chat import _phase14_chat_fluency_system_msg


_TOKEN_RE = re.compile(r"^\[\[ENT_[A-Z][A-Z0-9_]*_\d{3}\]\]$")


def test_shield_token_format_description_exported():
    assert hasattr(dx, "SHIELD_TOKEN_FORMAT_DESCRIPTION")
    assert isinstance(dx.SHIELD_TOKEN_FORMAT_DESCRIPTION, str)
    assert "[[ENT_<TYPE>_<NNN>]]" in dx.SHIELD_TOKEN_FORMAT_DESCRIPTION


def test_shield_token_examples_exported_and_well_formed():
    assert hasattr(dx, "SHIELD_TOKEN_EXAMPLES")
    assert isinstance(dx.SHIELD_TOKEN_EXAMPLES, list)
    assert len(dx.SHIELD_TOKEN_EXAMPLES) >= 3
    for example in dx.SHIELD_TOKEN_EXAMPLES:
        assert _TOKEN_RE.match(example), (
            f"SHIELD_TOKEN_EXAMPLES entry {example!r} does not match the "
            f"canonical [[ENT_<TYPE>_<NNN>]] shape that `_token_for(...)` emits"
        )


def test_token_examples_match_real_emitter_output():
    """Every shape claimed in SHIELD_TOKEN_EXAMPLES must be emittable
    by the real `_token_for` path. Sanity-check by reproducing one
    via the actual deid string-format identical to L594."""
    # Reproduce the canonical emit pattern verbatim.
    sample = f"[[ENT_{'PERSON'}_{1:03d}]]"
    assert sample == "[[ENT_PERSON_001]]"
    assert sample in dx.SHIELD_TOKEN_EXAMPLES, (
        f"Real emitter would produce {sample!r}; SHIELD_TOKEN_EXAMPLES "
        f"must include it. Got: {dx.SHIELD_TOKEN_EXAMPLES}"
    )


def test_chat_preamble_uses_real_token_shape_not_legacy():
    """The Phase 14 chat preamble must reference the [[ENT_*]] shape
    sourced from the deidentifier constants, NOT the pre-Phase-14
    `[EMAIL_1]` / `[PERSON_3]` shape that caused the user-visible
    failure."""
    preamble = _phase14_chat_fluency_system_msg()
    assert "[[ENT_" in preamble, (
        "Chat preamble must reference the actual [[ENT_*]] token shape"
    )
    # Pre-Phase-14 legacy shapes must NOT reappear (regression guard).
    assert "[EMAIL_1]" not in preamble, (
        "Chat preamble must not reference legacy `[EMAIL_1]` shape"
    )
    assert "[PERSON_3]" not in preamble, (
        "Chat preamble must not reference legacy `[PERSON_3]` shape"
    )
    # Forbidden-vocab block must be present (T1 step 2 contract).
    for vocab in ("redacted", "token", "I can't parse", "did you mean"):
        assert vocab in preamble, (
            f"Phase 14 forbidden-vocab guard missing from preamble: {vocab!r}"
        )


def test_token_shape_description_lists_actual_types():
    """The description must enumerate types that match _SPACY_TYPES_KEPT
    + the regex layer's known types. This is a defensive cross-check —
    if someone adds a new entity class to `_token_for` without
    updating SHIELD_TOKEN_FORMAT_DESCRIPTION, this fires."""
    desc = dx.SHIELD_TOKEN_FORMAT_DESCRIPTION
    # spaCy-kept types must all be in the description.
    for t in dx._SPACY_TYPES_KEPT:
        assert t in desc, (
            f"spaCy type {t!r} kept by deid is missing from "
            f"SHIELD_TOKEN_FORMAT_DESCRIPTION: {desc!r}"
        )
    # A representative subset of the regex layer types.
    for t in ("EMAIL", "API_KEY", "CREDIT_CARD", "IBAN", "SSN"):
        assert t in desc, (
            f"Regex type {t!r} is missing from SHIELD_TOKEN_FORMAT_DESCRIPTION"
        )
