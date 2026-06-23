"""Phase 5.1 — invariant: deployment boot smoke MUST stay registered.

The Phase 5.1 dispatch added an operational invariant — a
docker-compose triad boot smoke at
``backend/tests/deploy/test_compose_boot_smoke.py`` — that proves the
three-process topology (akki / synisense / solva + Mongo) boots end-
to-end, serves a representative ``/v1/<ctx>/*`` route per context via
the akki ingress, and tears down with no leaked containers/volumes.

That smoke itself is decorated with ``@pytest.mark.deploy_smoke`` and
is excluded by default (it requires docker, ~3min wall-clock, and is
intended for the CI deploy lane). The problem with such opt-in tests is
that they can be silently broken — deleted, renamed, un-decorated, or
have their marker removed from ``pytest.ini`` — and nobody notices
until the deploy lane fails.

This invariant runs on EVERY pytest invocation and fails the build if
any of the following lock-step relationships drift:

  1. The smoke file exists at the canonical path.
  2. The ``deploy_smoke`` marker is registered in ``pytest.ini``
     (otherwise pytest emits ``PytestUnknownMarkWarning`` and the
     marker silently no-ops).
  3. The canonical smoke test function name is present in the file
     (no rename / accidental deletion of the test).
  4. The ``@pytest.mark.deploy_smoke`` decoration is present on the
     test (otherwise the test would run on every pytest invocation
     and break the default lane).
  5. The ``docker-compose.yml`` the smoke references exists at the
     expected path.
  6. The honest-skip branch (``pytest.skip("docker daemon
     unavailable...")``) is preserved — otherwise the smoke would
     fail loudly on environments without docker rather than skip
     cleanly.

If any check fails, this invariant fails the build with a clear
remediation pointer.
"""
from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_FILE = REPO_ROOT / "tests" / "deploy" / "test_compose_boot_smoke.py"
PYTEST_INI = REPO_ROOT / "pytest.ini"
COMPOSE_FILE = REPO_ROOT / "deploy" / "docker-compose.yml"

CANONICAL_TEST_NAME = "test_compose_triad_boots_and_serves_all_three_contexts"


def test_deploy_smoke_file_exists() -> None:
    """The Phase 5.1 deploy smoke file must exist at the canonical path."""
    assert SMOKE_FILE.exists(), (
        f"Phase 5.1 deploy smoke file missing: {SMOKE_FILE}. "
        f"This is a build-breaking regression — restore the file or "
        f"see /app/memory/sprints/PHASE_5_1_DEPLOY_SMOKE.md for the "
        f"sprint memo describing what it must contain."
    )


def test_deploy_smoke_marker_registered_in_pytest_ini() -> None:
    """The ``deploy_smoke`` marker must be registered in pytest.ini.

    Without registration, ``@pytest.mark.deploy_smoke`` emits
    ``PytestUnknownMarkWarning`` and the marker silently no-ops —
    meaning the smoke would run on every default pytest invocation
    (slow, docker-dependent) instead of being opt-in.
    """
    assert PYTEST_INI.exists(), f"pytest.ini missing at {PYTEST_INI}"
    body = PYTEST_INI.read_text(encoding="utf-8")
    assert "deploy_smoke" in body, (
        "Phase 5.1 `deploy_smoke` marker missing from pytest.ini. "
        "Without registration, the marker silently no-ops and the "
        "smoke would run on every default pytest invocation. Add "
        "`deploy_smoke: ...` under [pytest] markers."
    )


def test_canonical_smoke_test_present() -> None:
    """The canonical smoke test function name must be present.

    Renaming or removing the test would silently shrink the operational
    invariant. The function name is pinned here so a rename forces a
    matching update in this invariant + the sprint memo.
    """
    body = SMOKE_FILE.read_text(encoding="utf-8")
    assert f"def {CANONICAL_TEST_NAME}(" in body, (
        f"Canonical smoke test `{CANONICAL_TEST_NAME}` missing from "
        f"{SMOKE_FILE.name}. If you renamed the test, update this "
        f"invariant + the sprint memo at "
        f"/app/memory/sprints/PHASE_5_1_DEPLOY_SMOKE.md to match."
    )


def test_smoke_decorated_with_deploy_smoke_marker() -> None:
    """The smoke MUST carry ``@pytest.mark.deploy_smoke``.

    Without the decoration, the smoke would run on every default
    pytest invocation — slow, docker-dependent, and noisy. The
    decoration is what keeps it opt-in.
    """
    body = SMOKE_FILE.read_text(encoding="utf-8")
    # Tolerate any whitespace between the decorator and the def line.
    pattern = re.compile(
        r"@pytest\.mark\.deploy_smoke\s*\n\s*def\s+"
        + re.escape(CANONICAL_TEST_NAME)
        + r"\b",
        re.MULTILINE,
    )
    assert pattern.search(body), (
        f"`@pytest.mark.deploy_smoke` decoration missing from "
        f"`{CANONICAL_TEST_NAME}` in {SMOKE_FILE.name}. Without it, "
        f"the smoke would run on every default pytest invocation."
    )


def test_compose_file_referenced_exists() -> None:
    """The docker-compose.yml the smoke targets must exist.

    The smoke computes ``COMPOSE_FILE = REPO_ROOT / "backend" /
    "deploy" / "docker-compose.yml"``. From the smoke's own POV,
    REPO_ROOT walks up two parents from ``tests/deploy/<file>``,
    which lands at ``/app`` — so the resolved path is the same
    ``/app/backend/deploy/docker-compose.yml`` we assert here.
    """
    assert COMPOSE_FILE.exists(), (
        f"Phase 5 deploy compose file missing: {COMPOSE_FILE}. The "
        f"deploy smoke references it via subprocess; without this "
        f"file the smoke would `docker compose up` against nothing."
    )


def test_honest_skip_branch_preserved() -> None:
    """The honest ``pytest.skip("docker daemon unavailable...")`` branch
    must remain in the smoke.

    Honesty Protocol (per the Phase 5.1 dispatch): when docker is
    unavailable, the smoke must SKIP with a clear reason — NOT a
    silent pass. The skip-message string itself is the contract a
    CI operator greps for; pin its keywords so a future "clean up
    the skip message" diff doesn't accidentally drop the honesty
    signal.
    """
    body = SMOKE_FILE.read_text(encoding="utf-8")
    assert "pytest.skip" in body, (
        "Honest-skip branch removed from the deploy smoke. Per the "
        "Phase 5.1 dispatch's Honesty Protocol, the smoke must skip "
        "with a clear reason when docker is unavailable — NOT pass "
        "silently. Restore the `pytest.skip(\"docker daemon "
        "unavailable...\")` branch."
    )
    assert "docker daemon unavailable" in body, (
        "Honest-skip reason string drifted. The string `docker daemon "
        "unavailable` is the contract a CI operator greps for; keep "
        "it verbatim in the skip message."
    )
    assert "NOT a silent pass" in body, (
        "Honesty-protocol marker `NOT a silent pass` removed from the "
        "skip message. Restore it — the explicit non-silence claim is "
        "the documented intent of the honest-skip pattern."
    )
