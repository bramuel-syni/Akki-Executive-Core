"""Global invariants — Phase 0 (Re-Architecture).

Four build-breaking invariants that guard the product's structural
guarantees against regression. The Phase 0 dispatch (page 9 of the
approved Syni Re-Architecture Plan) defines them as:

  1. tenancy — no tenant-scoped collection queried without account_id
     filter. OBSERVE MODE in Phase 0: violations recorded to
     /app/memory/invariants/tenancy_violations.json, build does NOT
     fail on count > 0 yet. Phase 2 will flip to enforce-mode.

  2. shield-no-leak — no [[ENT_...]] token survives in ANY user-
     visible surface output. Generalised across chat, Solva
     narration, Work Studio compile, brief, pulse idea.

  3. fail-closed — an injected Shield failure yields a refusal
     (not a passthrough). Deterministic; no live LLM call.

  4. audit-always — every successful Shield invocation writes both
     a `synisense_audit_log` row AND a `synisense_trust_receipts`
     row. Integration-marked (real Shield call).

Plus one DELIBERATE-VIOLATION smoke
(`test_invariant_violations_smoke.py`) that is `@pytest.mark.skip`'d
by default. Unskip locally to prove the tenancy invariant has teeth:
when the deliberate offender is in scope, the scanner records the
violation.
"""
