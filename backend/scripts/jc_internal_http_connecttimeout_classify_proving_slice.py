"""JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY · 9-row proving slice.

Canonical Spec: user dispatch 2026-07-05 · `JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY`.

CLASSIFY-ONLY arc — zero code / config / env / silencing / gating touches to
`contracts/_adapters/_http_client.py`, its callers, `BOUNDED_CONTEXT_TRANSPORT`,
or any try/except surface. Shield UNTOUCHED. Testing sub-agents BANNED.
MOCKED-integrations line preserved. HARD STOP at report close.

Slice rows:
  R1 memo exists at canonical path
  R2 memo line 1 cites Canonical Spec (Zero-Handoff-Loss rule)
  R3 all 5 mandated section headers present (§1..§5)
  R4 review-sitting verdict token present in §5 (CLEAR-TO-PROCEED |
     HOLD-FOR-RECAPTURE | PROCEED-WITH-CAVEAT)
  R5 R7 zero-touch discipline: no diff on protected paths since
     the pre-arc HEAD (protected = _http_client.py, contracts/__init__.py,
     contracts/_adapters/*.py, services/synisense/shield/**, backend/server.py)
  R6 Shield sha256 identity (13 files under services/synisense/shield/**
     unchanged during this arc)
  R7 DEV_PIPELINE.md §9 has a row for this arc
  R8 5 bundle READMEs still present under /app/memory/evidence/2026_07_02/
     (didn't touch bundle capture outputs)
  R9 amendment-echo verified: memo contains "Received-scope echo" block +
     "Two reinforcements received (echoed)" block
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path("/app")
MEMO = APP_ROOT / "memory" / "sprints" / "JC_INTERNAL_HTTP_CONNECTTIMEOUT_CLASSIFY.md"
DEV_PIPELINE = APP_ROOT / "memory" / "DEV_PIPELINE.md"
BUNDLE_ROOT = APP_ROOT / "memory" / "evidence" / "2026_07_02"

# Files that MUST NOT be modified during this arc (R7 zero-touch).
PROTECTED_PATHS = [
    "backend/contracts/_adapters/_http_client.py",
    "backend/contracts/__init__.py",
    "backend/contracts/_adapters/synisense.py",
    "backend/contracts/_adapters/solva.py",
    "backend/contracts/_adapters/akki.py",
    "backend/server.py",
    "backend/.env",
]

SHIELD_ROOT = APP_ROOT / "backend" / "services" / "synisense" / "shield"

# Pre-arc commit hash — the tip of what the previous arc closed at
# (JC-FE-CODEMOD-001-CLOSE-CONDITIONS · aff25763). Any diff on
# PROTECTED_PATHS since this SHA would break R5.
PRE_ARC_HEAD = "aff25763"

BUNDLE_READMES = [
    BUNDLE_ROOT / "bundle_v0_5_owner_digest" / "README.md",
    BUNDLE_ROOT / "bundle_v0_5_monitor_reassessment" / "README.md",
    BUNDLE_ROOT / "bundle_v0_5_origin_briefs" / "README.md",
    BUNDLE_ROOT / "bundle_llm_refresh_2_work_studio" / "README.md",
    BUNDLE_ROOT / "bundle_llm_refresh_3_solva_v2" / "README.md",
]

results: list[dict] = []


def add(row: str, ok: bool, detail: str = "", **extras) -> None:
    results.append({"row": row, "ok": ok, "detail": detail, **extras})
    marker = "PASS" if ok else "FAIL"
    print(f"[{marker}] {row} — {detail}")


def r1_memo_exists() -> None:
    ok = MEMO.exists() and MEMO.stat().st_size > 2000
    add(
        "R1_memo_exists",
        ok,
        f"path={MEMO} exists={MEMO.exists()} size={MEMO.stat().st_size if MEMO.exists() else 0}",
    )


def r2_memo_line1_cites_canonical_spec() -> None:
    if not MEMO.exists():
        add("R2_line1_canonical_spec_cite", False, "memo missing")
        return
    line1 = MEMO.read_text().splitlines()[0]
    ok = (
        "Canonical Spec" in line1
        and "JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY" in line1
    )
    add("R2_line1_canonical_spec_cite", ok, f"line1={line1[:180]!r}")


def r3_all_five_sections_present() -> None:
    if not MEMO.exists():
        add("R3_sections_present", False, "memo missing")
        return
    body = MEMO.read_text()
    needed = [
        "§1 · Target identification",
        "§2 · Surface enumeration",
        "§3 · Per-surface failure-mode classification",
        "§4 · Environment scope",
        "§5 · Evidence-bundle priority audit",
    ]
    missing = [h for h in needed if h not in body]
    add(
        "R3_sections_present",
        not missing,
        f"missing={missing}",
    )


def r4_verdict_token_present() -> None:
    if not MEMO.exists():
        add("R4_verdict_token", False, "memo missing")
        return
    body = MEMO.read_text()
    tokens = ["CLEAR-TO-PROCEED", "HOLD-FOR-RECAPTURE", "PROCEED-WITH-CAVEAT"]
    hits = [t for t in tokens if t in body]
    # Verdict section: check it appears after the §5 header.
    idx_s5 = body.find("§5 · Evidence-bundle priority audit")
    verdict_span = body[idx_s5:] if idx_s5 >= 0 else ""
    verdict_hits = [t for t in tokens if t in verdict_span]
    ok = len(hits) >= 1 and len(verdict_hits) >= 1
    add(
        "R4_verdict_token",
        ok,
        f"tokens_in_memo={hits} tokens_in_§5={verdict_hits}",
    )


def r5_zero_touch_on_protected_paths() -> None:
    """R7 zero-touch discipline. Verify none of the PROTECTED_PATHS
    differ from PRE_ARC_HEAD tree state.

    Uses `git diff --stat PRE_ARC_HEAD -- <path>` — empty output means
    no drift on that path.
    """
    try:
        proc = subprocess.run(
            ["git", "diff", "--stat", PRE_ARC_HEAD, "--"] + PROTECTED_PATHS,
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as e:  # noqa: BLE001
        add("R5_zero_touch", False, f"git diff failed: {e}")
        return
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if proc.returncode != 0:
        add("R5_zero_touch", False, f"rc={proc.returncode} stderr={err[:200]}")
        return
    ok = out == ""
    add(
        "R5_zero_touch",
        ok,
        f"protected_paths={len(PROTECTED_PATHS)} diff_stat_bytes={len(out)}",
        raw_out=out[:500] if out else "",
    )


def r6_shield_sha256_identity() -> None:
    """Shield UNTOUCHED — assert no files under services/synisense/shield/**
    have changed since PRE_ARC_HEAD tree."""
    if not SHIELD_ROOT.exists():
        add("R6_shield_sha256_identity", False, f"shield root missing: {SHIELD_ROOT}")
        return
    try:
        proc = subprocess.run(
            ["git", "diff", "--stat", PRE_ARC_HEAD, "--", "backend/services/synisense/shield/"],
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as e:  # noqa: BLE001
        add("R6_shield_sha256_identity", False, f"git diff failed: {e}")
        return
    out = (proc.stdout or "").strip()
    ok = proc.returncode == 0 and out == ""
    # Count shield files as a supplementary sanity check.
    shield_files = list(SHIELD_ROOT.rglob("*.py"))
    add(
        "R6_shield_sha256_identity",
        ok,
        f"shield_py_files={len(shield_files)} diff_bytes={len(out)}",
    )


def r7_dev_pipeline_row_exists() -> None:
    if not DEV_PIPELINE.exists():
        add("R7_dev_pipeline_row", False, "DEV_PIPELINE missing")
        return
    body = DEV_PIPELINE.read_text()
    marker = "JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY"
    ok = marker in body
    idx = body.find(marker)
    add(
        "R7_dev_pipeline_row",
        ok,
        f"marker_present={ok} idx={idx}",
    )


def r8_bundle_readmes_intact() -> None:
    missing = [str(p) for p in BUNDLE_READMES if not p.exists()]
    ok = not missing
    add(
        "R8_bundle_readmes_intact",
        ok,
        f"bundles_expected={len(BUNDLE_READMES)} missing={missing}",
    )


def r9_amendment_echo_present() -> None:
    if not MEMO.exists():
        add("R9_amendment_echo", False, "memo missing")
        return
    body = MEMO.read_text()
    scope_echo = "Received-scope echo" in body
    reinforcements_echo = "Two reinforcements received (echoed)" in body
    ok = scope_echo and reinforcements_echo
    add(
        "R9_amendment_echo",
        ok,
        f"scope_echo={scope_echo} reinforcements_echo={reinforcements_echo}",
    )


def main() -> int:
    print(
        "=" * 60,
        "\nJC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY · proving slice · 9 rows",
        "\nCanonical Spec: user dispatch 2026-07-05",
        "\nCLASSIFY-ONLY · R7 zero-touch · Shield UNTOUCHED",
        "\nTesting sub-agents BANNED. Pure bash execution.\n",
        "=" * 60,
        sep="",
    )
    r1_memo_exists()
    r2_memo_line1_cites_canonical_spec()
    r3_all_five_sections_present()
    r4_verdict_token_present()
    r5_zero_touch_on_protected_paths()
    r6_shield_sha256_identity()
    r7_dev_pipeline_row_exists()
    r8_bundle_readmes_intact()
    r9_amendment_echo_present()

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    summary = {
        "arc": "JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY",
        "canonical_spec": "user dispatch 2026-07-05",
        "discipline": "CLASSIFY-ONLY · R7 zero-touch",
        "passed": passed,
        "total": total,
        "green": passed == total,
        "rows": results,
    }
    out_path = Path("/app/backend/scripts/.jc_internal_http_connecttimeout_classify_slice_results.json")
    out_path.write_text(json.dumps(summary, indent=2))

    print(f"\n{'=' * 60}")
    print(f"RESULT · {passed}/{total} GREEN · saved to {out_path}")
    print("=" * 60)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
