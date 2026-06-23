"""Phase 5.1 — Deployment boot smoke tests.

Houses the docker-compose triad smoke (`test_compose_boot_smoke.py`).
Marker: `deploy_smoke` (registered in `pytest.ini`). Excluded from the
default pytest invocation; opted-in via `pytest -m deploy_smoke` on a
CI lane that has docker installed.

The companion build-breaking invariant lives at
`tests/invariants/test_invariant_deploy_smoke_present.py` and runs on
every pytest invocation — it proves the smoke file + marker + canonical
test function name stay in lock-step with the deploy README and the
docker-compose.yml referenced by the smoke.
"""
