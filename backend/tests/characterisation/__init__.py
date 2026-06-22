"""Characterisation (golden) tests — Phase 0 (Re-Architecture).

Pin CURRENT behaviour of the three hot-path surfaces (chat round-trip,
Solva analyze, Work Studio compile lifecycle) as-is, quirks included.

Behaviour shifts must be deliberate: when one of these tests fails,
the developer either accepts the new golden (intentional behaviour
change — must be approved per Discipline Rail R2) or reverts the
code change (unintentional regression).

The goldens snapshot STRUCTURAL shape for LLM-bearing fields (field
presence, type, non-empty checks) rather than text content, because
the LLM is non-deterministic. The audit-row write is asserted
deterministically.

All tests in this directory are `@pytest.mark.integration` — they
run against the live Anthropic LLM via the real Shield pipeline. Run
explicitly with `pytest -m integration`.
"""
