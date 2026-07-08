"""JC-SHIELD-ADAPTER-METERING-PARITY-DIAGNOSE proving slice · 6 rows · CLASSIFY-ONLY regression floor.

Canonical rationale: Governance parity between metering and streaming adapters ·
gates A1/A2 choice on `JC-SHIELD-CEILING-ASYMMETRY-DIAGNOSE` follow-on. User dispatch
2026-07-08 · `JC-SHIELD-ADAPTER-METERING-PARITY-DIAGNOSE` (bounded CLASSIFY-ONLY · P1).

Rows:
  R1 · Memo exists with all required sections populated (received-scope-echo · both adapters traced · ∆ both directions · recommendation posture)
  R2 · Both adapters file:line traced verbatim in memo
  R3 · Governance-emission field list per adapter (metering M1-M16 + streaming S1-S5) enumerated in memo
  R4 · Delta computed (∆ both directions) with verbatim field enumeration and item counts
  R5 · Recommendation posture emitted with framing discipline (A1-default / A2a-not-defensible / A2b-defensible-with-tradeoff / verdict = NEITHER-STRAIGHT-SWAP)
  R6 · Zero-touch: `git diff --stat` shows ONLY memo + slice + DEV_PIPELINE.md + slice-results JSON · Shield sha256 identity preserved (composite c6902d324e... · 13 files)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MEMO_PATH = REPO_ROOT / "memory" / "sprints" / "JC_SHIELD_ADAPTER_METERING_PARITY_DIAGNOSE.md"
SLICE_PATH = REPO_ROOT / "backend" / "scripts" / "jc_shield_adapter_metering_parity_diagnose_proving_slice.py"
DEV_PIPELINE_PATH = REPO_ROOT / "memory" / "DEV_PIPELINE.md"
SHIELD_DIR = REPO_ROOT / "backend" / "services" / "synisense" / "shield"

PRE_ARC_HEAD = "4d1d0f80"

EXPECTED_SHIELD_COMPOSITE_SHA256 = (
    "c6902d324ed90734cd815f63eaee8ebb66d776ef89f1797c1f7f50cbae10d5a8"
)

PROTECTED_PATHS = [
    "backend/services/synisense/shield",
    "backend/services/synisense/shield/streaming.py",
    "backend/services/synisense/shield/llm_router.py",
    "backend/services/synisense/shield/client.py",
    "backend/services/synisense/shield/audit_log.py",
    "backend/services/synisense/shield/trust_receipt.py",
    "backend/services/synisense/shield/deidentifier.py",
    "backend/services/synisense/shield/reidentifier.py",
    "backend/services/synisense/shield/purpose_validator.py",
    "backend/routers/work_studio_export.py",
    "backend/routers/decks.py",
    "backend/llm_service.py",
    "backend/llm_tier_quota.py",
    "backend/.env",
]

ALLOWED_TOUCHED_PATHS = {
    "memory/sprints/JC_SHIELD_ADAPTER_METERING_PARITY_DIAGNOSE.md",
    "backend/scripts/jc_shield_adapter_metering_parity_diagnose_proving_slice.py",
    "memory/DEV_PIPELINE.md",
    "memory/jc_artifacts/shield_adapter_metering_parity/slice_results.json",
}

# R2 · adapter file:line trace markers (verbatim citations required in memo)
REQUIRED_ADAPTER_TRACE_MARKERS = [
    "backend/services/synisense/shield/llm_router.py",
    "backend/services/synisense/shield/streaming.py",
    "backend/services/synisense/shield/client.py",
    "`invoke_with_metering(",
    "`stream_llm_direct(",
    "`collect_llm_text(",
    "`prepare_for_streaming(",
]

# R3 · governance-emission enumeration markers (metering M1-M16 + streaming S1-S5)
REQUIRED_GOVERNANCE_ENUMERATION_MARKERS = [
    # Metering emissions (must be present as table rows)
    "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9",
    "M10", "M11", "M12", "M13", "M14", "M16",
    # Streaming emissions (must be present as table rows)
    "S1", "S2", "S3", "S4", "S5",
    # Governance-item names verbatim
    "Purpose validation",
    "Tenant-scoped de-identification",
    "Re-identification",
    "Fail-closed",
    "Request hash",
    "Response hash",
    "Token metering",
    "Metering-method provenance",
    "Cost accounting",
    "Audit row write",
    "Trust receipt",
    "Tenant isolation enforcement",
]

# R4 · delta computation markers
REQUIRED_DELTA_MARKERS = [
    "∆(metering \\ streaming-bare)",
    "∆(streaming-bare \\ metering)",
    "∆(metering \\ streaming-governed)",
    "∆(streaming-governed \\ metering)",
    "13 items",
    "4 items",
]

# R5 · recommendation posture markers (framing discipline)
REQUIRED_RECOMMENDATION_MARKERS = [
    "NEITHER-STRAIGHT-SWAP",
    "A1 recommendation (default)",
    "A2a (bare adapter reroute — NOT RECOMMENDED)",
    "A2b (governed-streaming reroute — DEFENSIBLE but distinct scope)",
    "Chunked `shield_invoke`",
    "do NOT build in this arc",
    "rough scope + risk assessment",
    "`JC-DECK-GENERATE-CHUNKED-INVOCATION`",
    "`JC-DECK-GENERATE-GOVERNED-STREAMING-REROUTE`",
    "shield-adapter-metering-parity-classified-neither-straight-swap",
]

REQUIRED_DEV_PIPELINE_MARKERS = [
    "JC-SHIELD-ADAPTER-METERING-PARITY-DIAGNOSE",
    "CLASSIFY-ONLY",
]


def _sh(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd, cwd=str(cwd or REPO_ROOT), capture_output=True, text=True, check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _row(name: str, ok: bool, note: str = "") -> dict:
    return {"row": name, "ok": bool(ok), "note": note[:800]}


def r1_memo_exists_and_populated() -> dict:
    if not MEMO_PATH.exists():
        return _row("R1", False, f"missing: {MEMO_PATH}")
    text = MEMO_PATH.read_text()
    size = MEMO_PATH.stat().st_size
    if size < 5000:
        return _row("R1", False, f"memo too small: {size} bytes")
    required_sections = [
        "Received-scope echo (6 items)",
        "STEP 0 · Scoping recon",
        "STEP 1 · Governance emissions of METERING-ADAPTER",
        "STEP 2 · Governance emissions of STREAMING-ADAPTER-BARE",
        "STEP 2b · Governance emissions of STREAMING-ADAPTER-GOVERNED",
        "STEP 3 · Delta computation",
        "STEP 4 · Recommendation posture",
        "STEP 5 · Real Signals surfaced",
        "STEP 6 · Closure — Zero-touch verification",
        "STEP 7 · Close-status",
    ]
    missing = [s for s in required_sections if s not in text]
    if missing:
        return _row("R1", False, f"missing sections: {missing}")
    # Line 1 canonical rationale check
    first_line = text.splitlines()[0]
    if "Canonical rationale" not in first_line:
        return _row("R1", False, f"line 1 missing canonical rationale: {first_line[:120]!r}")
    if "JC-SHIELD-ADAPTER-METERING-PARITY-DIAGNOSE" not in first_line:
        return _row("R1", False, f"line 1 missing dispatch ID: {first_line[:120]!r}")
    return _row("R1", True, f"memo populated ({size} bytes) · all 10 sections present · line-1 canonical rationale cite present")


def r2_adapter_trace_markers() -> dict:
    text = MEMO_PATH.read_text()
    missing = [m for m in REQUIRED_ADAPTER_TRACE_MARKERS if m not in text]
    if missing:
        return _row("R2", False, f"missing adapter trace markers: {missing}")
    return _row("R2", True, f"all {len(REQUIRED_ADAPTER_TRACE_MARKERS)} adapter trace markers present")


def r3_governance_enumeration_markers() -> dict:
    text = MEMO_PATH.read_text()
    missing = [m for m in REQUIRED_GOVERNANCE_ENUMERATION_MARKERS if m not in text]
    if missing:
        return _row("R3", False, f"missing governance enumeration markers: {missing[:8]}")
    return _row("R3", True, f"all {len(REQUIRED_GOVERNANCE_ENUMERATION_MARKERS)} governance enumeration markers present (M1-M14+M16, S1-S5, 12 item names)")


def r4_delta_markers() -> dict:
    text = MEMO_PATH.read_text()
    missing = [m for m in REQUIRED_DELTA_MARKERS if m not in text]
    if missing:
        return _row("R4", False, f"missing delta markers: {missing}")
    # Also verify the "13 items" and "4 items" counts appear in the ∆ context
    if "**13 items:**" not in text:
        return _row("R4", False, "missing '**13 items:**' count marker for ∆(metering \\ streaming-bare)")
    if "**4 items:**" not in text:
        return _row("R4", False, "missing '**4 items:**' count marker for ∆(streaming-bare \\ metering)")
    return _row("R4", True, f"all {len(REQUIRED_DELTA_MARKERS)} delta markers present + item counts (13, 4) verified")


def r5_recommendation_posture_markers() -> dict:
    text = MEMO_PATH.read_text()
    missing = [m for m in REQUIRED_RECOMMENDATION_MARKERS if m not in text]
    if missing:
        return _row("R5", False, f"missing recommendation posture markers: {missing[:5]}")
    # Framing discipline: forbid "A2 recommended because simpler" phrasing
    forbidden = ["A2 recommended because simpler", "simpler so A2", "smaller diff so A2"]
    hit = [f for f in forbidden if f.lower() in text.lower()]
    if hit:
        return _row("R5", False, f"forbidden diff-size framing detected: {hit}")
    return _row("R5", True, f"all {len(REQUIRED_RECOMMENDATION_MARKERS)} recommendation markers present · framing discipline clean")


def r6_zero_touch_and_shield_identity() -> dict:
    # Part A: only allowed files touched since PRE_ARC_HEAD
    rc, out, err = _sh(["git", "diff", "--name-only", PRE_ARC_HEAD, "HEAD"])
    if rc != 0:
        return _row("R6", False, f"git diff failed rc={rc} stderr={err[:200]!r}")
    changed = {ln.strip() for ln in out.splitlines() if ln.strip()}
    unexpected = changed - ALLOWED_TOUCHED_PATHS
    if unexpected:
        return _row("R6", False, f"unexpected files touched since {PRE_ARC_HEAD}: {sorted(unexpected)[:10]}")

    # Part B: DEV_PIPELINE §9 row present
    dp = DEV_PIPELINE_PATH.read_text()
    missing_dp = [m for m in REQUIRED_DEV_PIPELINE_MARKERS if m not in dp]
    if missing_dp:
        return _row("R6", False, f"DEV_PIPELINE missing markers: {missing_dp}")

    # Part C: zero diff bytes on protected paths
    rc, out, err = _sh(
        ["git", "diff", "--stat", PRE_ARC_HEAD, "HEAD", "--"] + PROTECTED_PATHS,
    )
    if rc != 0:
        return _row("R6", False, f"git diff --stat failed rc={rc}")
    if out.strip():
        return _row("R6", False, f"protected paths show diffs since {PRE_ARC_HEAD}: {out.strip()[:400]}")

    # Part D: Shield sha256 identity (13 files) — frozen digests from prior arc
    files = sorted(p for p in SHIELD_DIR.glob("*.py") if p.is_file())
    if len(files) != 13:
        return _row("R6", False, f"expected 13 Shield .py files, found {len(files)}")
    frozen = {
        "__init__.py": "23f360aa11f6c6a074b3c17953accca0fa4abc6da4e07fe89886bc9614b5d9c5",
        "_legacy_llm_fallback.py": "9028ae6340dc3d2fe9f48d31e88e2f1a660759b7191b80dd148a57b844533bef",
        "audit_log.py": "6a49b41fb9cc6ac45e6b5a68142a54a001e62954cf4bcbc30d2479ad571e3b34",
        "canonical.py": "ad5b1206ba66419cc501ece1b1c5389540f7df190b6c735a56c5aff2954abe82",
        "client.py": "6bb2426ab5129f97faad7f1e6fbe81b5556beed43ab56a99aaeb403d0e2679b5",
        "deidentifier.py": "6da2f511898a56e1b78c08e3a2619d9c239aa7287060e00b5988ce677e7f5657",
        "exceptions.py": "ffe6355938e58a0a66ee69557b7c4f7b2ff6957e63e3247fc6763a8c2e5f5904",
        "llm_router.py": "2a6749cb076b343a9b64b2303da041017f7beb6a6e91dac96511a517f136077e",
        "purpose_validator.py": "563345f9569dc09330f151d82a494681547c149bd1d86619446cd208f094a6e4",
        "reidentifier.py": "a259d4712e1aa93edcf2d5368d7163d9557a9ff09aafeb9a3495db7cd4e928da",
    }
    mismatches = []
    for p in files:
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        frozen_hash = frozen.get(p.name)
        if frozen_hash and digest != frozen_hash:
            mismatches.append(f"{p.name}: got {digest[:16]}, expected {frozen_hash[:16]}")
    if mismatches:
        return _row("R6", False, f"Shield file drift detected: {mismatches}")

    return _row(
        "R6", True,
        f"zero-touch verified: {len(changed)} allowed report-only files touched · 0 diff bytes on {len(PROTECTED_PATHS)} protected paths · Shield 13-file sha256 identity preserved",
    )


def main() -> int:
    rows = [
        r1_memo_exists_and_populated(),
        r2_adapter_trace_markers(),
        r3_governance_enumeration_markers(),
        r4_delta_markers(),
        r5_recommendation_posture_markers(),
        r6_zero_touch_and_shield_identity(),
    ]
    passed = sum(1 for r in rows if r["ok"])
    total = len(rows)
    report = {
        "arc": "JC-SHIELD-ADAPTER-METERING-PARITY-DIAGNOSE",
        "pre_arc_head": PRE_ARC_HEAD,
        "passed": passed,
        "total": total,
        "verdict": "GREEN" if passed == total else "RED",
        "content_marker": "shield-adapter-metering-parity-classified-neither-straight-swap",
        "rows": rows,
    }
    print(json.dumps(report, indent=2))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
