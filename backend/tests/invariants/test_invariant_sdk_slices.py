"""Phase 5 — invariant: per-context OpenAPI slice files stay in sync with
the live OpenAPI document.

The slice files at `/app/backend/openapi-sdk/{ctx}.openapi.json` are the
canonical SDK input for partner integrations. They must always reflect
the current `/v1/{ctx}/*` slice of the live OpenAPI. Anyone making a
route change that touches the `/v1/*` surface MUST regenerate the slice
files via `python scripts/generate_sdk_slices.py`.

This test calls the generator in `--check` mode and fails the build if
the on-disk slices diverge from what would be generated against the
live OpenAPI right now.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SLICE_DIR = REPO_ROOT / "openapi-sdk"
GENERATOR = REPO_ROOT / "scripts" / "generate_sdk_slices.py"


def test_slice_files_exist() -> None:
    """All three per-context slice files must exist."""
    for ctx in ("synisense", "solva", "akki"):
        target = SLICE_DIR / f"{ctx}.openapi.json"
        assert target.exists(), (
            f"Missing per-context OpenAPI slice file: {target}. "
            f"Run `python scripts/generate_sdk_slices.py` to create it."
        )


def test_slice_files_are_valid_json() -> None:
    """Each slice file must be valid JSON and have OpenAPI top-level keys."""
    for ctx in ("synisense", "solva", "akki"):
        target = SLICE_DIR / f"{ctx}.openapi.json"
        with open(target) as f:
            doc = json.load(f)
        for key in ("openapi", "info", "paths", "components"):
            assert key in doc, f"{target.name} missing top-level key '{key}'"
        assert doc["info"]["version"] == "1.0", f"{target.name} info.version mismatch"
        # Every path must live under the per-context prefix.
        prefix = f"/v1/{ctx}/"
        bad = [p for p in doc["paths"] if not p.startswith(prefix)]
        assert not bad, f"{target.name} contains paths outside {prefix}: {bad[:5]}"


def test_slice_files_match_live_openapi() -> None:
    """The on-disk slices must exactly match what the generator would produce.

    Runs `scripts/generate_sdk_slices.py --check`. Non-zero exit
    indicates drift — the test fails and the operator must regenerate.
    """
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"Slice files have drifted from the live OpenAPI document.\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}\n"
        f"Fix: `python scripts/generate_sdk_slices.py` from /app/backend/."
    )


def test_slice_path_counts_match_live() -> None:
    """Sum of per-context slice path counts must equal the live /v1/* slice count.

    The live `/v1/*` slice was pinned at 619 paths at Phase 4.4 close;
    the sum of per-context slice path counts must equal that to prove
    the slicer hasn't dropped any routes.
    """
    total = 0
    counts = {}
    for ctx in ("synisense", "solva", "akki"):
        target = SLICE_DIR / f"{ctx}.openapi.json"
        with open(target) as f:
            doc = json.load(f)
        counts[ctx] = len(doc["paths"])
        total += counts[ctx]
    # Phase 4.4 close baseline: 619 /v1/* paths total.
    EXPECTED = 619
    assert total == EXPECTED, (
        f"Per-context slice path counts sum to {total}, expected {EXPECTED} "
        f"(Phase 4.4 baseline). Counts: {counts}"
    )
