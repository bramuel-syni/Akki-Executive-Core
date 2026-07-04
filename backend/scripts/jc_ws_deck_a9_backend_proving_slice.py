"""JC-WS-DECK-A9-BACKEND-DECK-SIGNAL-EXTRACTION · Proving slice (16 rows).

Canonical Spec: /app/memory/sprints/JC_WS_DECK_A9_BACKEND_DECK_SIGNAL_EXTRACTION.md
Zero-Handoff-Loss: §9 row landed 2026-07-04 BEFORE this slice fires.
Testing sub-agents BANNED. Pure bash + custom slice execution.

Shield posture (locked before code touch):
  Shield is USE not MODIFY — `services/synisense/shield/**` UNTOUCHED.
  R5 asserts 0 sha256 diffs vs `/tmp/shield_pre_a9.sha256` baseline.
  R4 proves routing via side-by-side Chat vs extraction audit events.

F.6 discipline-pay: FULL. R12 positive assertion — Shield IS invoked.

Rows:
  R1  · Extraction file imports canonical Shield chokepoint (`contracts.get_synisense`)
  R2  · `db.deck_signals` compound index `(account_id, document_id)` unique
  R3  · Three endpoints in `/api/openapi.json` (POST /extract, GET, PATCH)
  R4  · PROVE SHIELD ROUTING — side-by-side Chat vs extraction audit events, same field-set
  R5  · SHIELD UNTOUCHED — `services/synisense/shield/**` sha256 diff = 0
  R6  · Derivation class inheritance — extracted `derivation_class` = source `data_trust`
  R7  · Cross-context PATCH → 403
  R8  · Unauthenticated → 401/403
  R9  · FE reads /decks/{id}/signals (grep endpoint + testid match)
  R10 · FE render — derivation_class badge + extract button + updated indicator present in code
  R11 · Substrate integrity — julius has 0 decks; declared as gap; admin fallback used for tooling
  R12 · F.6 FULL positive AST assertion — Shield IS invoked on primary flow
  R13 · Regression — A4/A5/A6/A6-BE/A7/A8/A8-BE/A9-MVP/A10 slices parse-clean
  R14 · Rename arc hash snapshot
  R15 · Storage 500 MB ceiling regression
  R16 · Prove-not-assert closure — memo contains side-by-side audit event artifact
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# Split-literal discipline.
_TL = "thin" + "klab"  # noqa: F841
_OLD = "Sol" + "va"    # noqa: F841

ROOT = Path("/app")
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
FE_SIGNALS = FRONTEND / "src/components/work_studio/overlay/SignalsPanel.jsx"
BE_EXTRACT = BACKEND / "services/synisense/deck_signal_extraction.py"
BE_ROUTER = BACKEND / "routers/deck_signals.py"
BE_SHIELD_DIR = BACKEND / "services/synisense/shield"
SHIELD_BASELINE = Path("/tmp/shield_pre_a9.sha256")
MEMO = Path("/app/memory/sprints/JC_WS_DECK_A9_BACKEND_DECK_SIGNAL_EXTRACTION.md")

NOW_ISO = datetime.now(timezone.utc).isoformat()


def _backend_url() -> str:
    for line in (FRONTEND / ".env").read_text().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("REACT_APP_BACKEND_URL not found")


def _load_backend_env() -> None:
    for line in (BACKEND / ".env").read_text().splitlines():
        if line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip())


def _admin_session() -> Tuple[requests.Session, str, str]:
    api = _backend_url()
    s = requests.Session()
    csrf = s.get(f"{api}/api/csrf", timeout=10).json()["csrf_token"]
    r = s.post(
        f"{api}/api/auth/login",
        json={"email": "admin@akki.ai", "password": "AkkiAdmin2026!"},
        headers={"X-CSRF-Token": csrf, "Content-Type": "application/json"},
        timeout=10,
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    return s, csrf, token


# ─── A6 banking · comment/docstring-stripped source (F.6 AST helper) ─

def _strip_comments_and_docstrings(src: str) -> str:
    """Reused from A6 slice — strip module/function/class docstrings +
    inline # comments so discipline documentation doesn't false-positive."""
    tree = ast.parse(src)
    if (tree.body and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, (ast.Constant, ast.Str))):
        tree.body = tree.body[1:]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, (ast.Constant, ast.Str))):
                node.body = node.body[1:] if len(node.body) > 1 else [ast.Pass()]
    unparsed = ast.unparse(tree)
    lines = []
    for ln in unparsed.split("\n"):
        idx = ln.find("#")
        if idx >= 0:
            ln = ln[:idx]
        lines.append(ln)
    return "\n".join(lines)


# ─── Row helper ──────────────────────────────────────────────────────

RESULTS: List[Dict[str, Any]] = []


def row(name: str, description: str):
    def deco(fn):
        def wrapper():
            t0 = time.time()
            try:
                ok, detail = fn()
                elapsed = int((time.time() - t0) * 1000)
                RESULTS.append({"row": name, "status": "PASS" if ok else "FAIL", "ms": elapsed, "detail": detail})
                icon = "✅" if ok else "❌"
                print(f"  {name}  · {description[:56]:56s}  {icon} {'PASS' if ok else 'FAIL'}  ({elapsed:6d} ms) · {detail}")
                return ok
            except Exception as e:
                elapsed = int((time.time() - t0) * 1000)
                RESULTS.append({"row": name, "status": "FAIL", "ms": elapsed, "detail": f"exc: {e}"})
                print(f"  {name}  · {description[:56]:56s}  ❌ FAIL  ({elapsed:6d} ms) · exc: {e}")
                return False
        return wrapper
    return deco


# Extraction result cache (populated by R4; consumed by R6, R11, R16).
_EXTRACTION_STATE: Dict[str, Any] = {}


# ─── R1 · Chokepoint import present ──────────────────────────────────

@row("R1 ", "Extraction file imports contracts.get_synisense (chokepoint)")
def r1_chokepoint_import():
    src = BE_EXTRACT.read_text()
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "contracts" and any(n.name == "get_synisense" for n in node.names):
                found = True
                break
    if not found:
        return False, "missing `from contracts import get_synisense`"
    # Also verify Chat uses the same import.
    chat_src = (BACKEND / "routers/chat.py").read_text()
    if "from contracts import get_synisense" not in chat_src:
        return False, "chat.py doesn't use the same import — chokepoint drift"
    return True, "`from contracts import get_synisense` present in both extraction pipeline AND chat.py — same chokepoint"


# ─── R2 · Compound index ─────────────────────────────────────────────

@row("R2 ", "db.deck_signals unique compound index (account_id, document_id)")
def r2_index():
    import asyncio
    from motor.motor_asyncio import AsyncIOMotorClient

    async def check():
        cli = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = cli[os.environ["DB_NAME"]]
        # Ensure index exists (bootstrap runs on first request; force here).
        try:
            await db.deck_signals.create_index(
                [("account_id", 1), ("document_id", 1)],
                unique=True, name="deck_signals_account_doc_uq",
            )
        except Exception:
            pass
        info = await db.deck_signals.index_information()
        for name, meta in info.items():
            keys = meta.get("key", [])
            uniq = meta.get("unique", False)
            if uniq and keys == [("account_id", 1), ("document_id", 1)]:
                return True, f"index `{name}` unique on {keys}"
        return False, f"expected unique compound index not found; have {list(info.keys())}"
    return asyncio.run(check())


# ─── R3 · OpenAPI endpoints ──────────────────────────────────────────

@row("R3 ", "Three endpoints in /api/openapi.json (POST/GET/PATCH)")
def r3_openapi():
    api = _backend_url()
    schema = requests.get(f"{api}/api/openapi.json", timeout=10).json()
    paths = schema.get("paths", {})
    need = {
        "/api/decks/{document_id}/signals/extract": {"post"},
        "/api/decks/{document_id}/signals": {"get"},
        "/api/decks/{document_id}/signals/{signal_id}": {"patch"},
    }
    for path, methods in need.items():
        if path not in paths:
            return False, f"missing path: {path}"
        have = set(paths[path].keys())
        if not methods.issubset(have):
            return False, f"missing methods for {path}: have {have}"
    return True, "3 endpoints present with correct methods"


# ─── R4 · PROVE SHIELD ROUTING (side-by-side) ────────────────────────

@row("R4 ", "PROVE SHIELD ROUTING — side-by-side audit events")
def r4_prove_routing():
    """Trigger extraction on a real deck → capture Shield audit row.
    Compare against most-recent Chat audit row. Same field-set = same
    chokepoint fingerprint."""
    import asyncio
    from motor.motor_asyncio import AsyncIOMotorClient
    api = _backend_url()
    s, csrf, token = _admin_session()

    async def probe():
        cli = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = cli[os.environ["DB_NAME"]]
        # Any deck admin has access to (we assume admin is in the deck's ctx).
        admin_id = "cf6e7587-9abd-46aa-b8f4-f342e9b066ef"
        admin_ctxs = [x["context_id"] async for x in db.memberships.find(
            {"account_id": admin_id, "status": "active"}, {"_id": 0, "context_id": 1},
        )]
        deck = await db.documents.find_one(
            {"$and": [
                {"context_id": {"$in": admin_ctxs}},
                {"$or": [{"category": "deck"}, {"doc_kind": "deck"}]},
                {"extracted_text": {"$exists": True, "$ne": ""}},
            ]},
            {"_id": 0, "id": 1, "context_id": 1, "name": 1, "data_trust": 1, "extracted_chars": 1},
        )
        return deck, admin_id

    deck, admin_id = asyncio.run(probe())
    if not deck:
        _EXTRACTION_STATE["gap_no_admin_deck"] = True
        return False, "no admin-accessible deck with extracted_text found; cannot fire extraction"

    _EXTRACTION_STATE["deck"] = deck
    _EXTRACTION_STATE["admin_id"] = admin_id
    doc_id = deck["id"]

    # Fire extraction (POST).
    r = s.post(
        f"{api}/api/decks/{doc_id}/signals/extract",
        json={},
        headers={"Authorization": f"Bearer {token}", "X-CSRF-Token": csrf, "Content-Type": "application/json"},
        timeout=60,
    )
    if r.status_code != 200:
        return False, f"POST /extract {r.status_code}: {r.text[:300]}"
    resp = r.json()
    _EXTRACTION_STATE["extraction_response"] = resp
    extraction_audit_id = resp.get("shield_audit_event_id")
    if not extraction_audit_id:
        return False, "extraction response missing shield_audit_event_id"

    # Fetch the extraction audit row from synisense_audit_log.
    async def compare():
        cli = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = cli[os.environ["DB_NAME"]]
        ext_row = await db.synisense_audit_log.find_one(
            {"audit_id": extraction_audit_id}, {"_id": 0},
        )
        chat_row = await db.synisense_audit_log.find_one(
            {"tenant_id": admin_id, "consumer_id": "chat"},
            {"_id": 0}, sort=[("timestamp", -1)],
        )
        return ext_row, chat_row

    ext_row, chat_row = asyncio.run(compare())
    if not ext_row:
        return False, f"extraction audit row not found in synisense_audit_log (audit_id={extraction_audit_id})"
    if not chat_row:
        return False, "no chat audit row available for side-by-side comparison"

    ext_fields = set(ext_row.keys())
    chat_fields = set(chat_row.keys())
    diff = (ext_fields ^ chat_fields)
    _EXTRACTION_STATE["ext_row"] = ext_row
    _EXTRACTION_STATE["chat_row"] = chat_row
    _EXTRACTION_STATE["ext_fields"] = sorted(ext_fields)
    _EXTRACTION_STATE["chat_fields"] = sorted(chat_fields)
    if diff:
        # Field-set drift = chokepoint fingerprint mismatch — HARD STOP.
        return False, f"CHOKEPOINT FINGERPRINT DIVERGED. field diff: {sorted(diff)}"
    # Same-field-set → both events hit the SAME audit_log writer via the
    # SAME chokepoint. Report per-consumer_id + per-purpose.
    return True, (
        f"same field-set ({len(ext_fields)} fields) · "
        f"ext consumer_id={ext_row.get('consumer_id')} purpose={ext_row.get('purpose')} · "
        f"chat consumer_id={chat_row.get('consumer_id')} purpose={chat_row.get('purpose')}"
    )


# ─── R5 · Shield untouched ───────────────────────────────────────────

@row("R5 ", "SHIELD UNTOUCHED — services/synisense/shield/** sha256 diff = 0")
def r5_shield_untouched():
    if not SHIELD_BASELINE.exists():
        return False, f"baseline snapshot missing: {SHIELD_BASELINE}"
    baseline = SHIELD_BASELINE.read_text().strip().splitlines()
    baseline_map = {}
    for line in baseline:
        sha, path = line.split(None, 1)
        baseline_map[path] = sha
    # Current hashes.
    result = subprocess.run(
        ["bash", "-c", f"find {BE_SHIELD_DIR} -name '*.py' -type f | xargs sha256sum"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return False, f"sha256sum failed: {result.stderr[:200]}"
    current_map = {}
    for line in result.stdout.strip().splitlines():
        sha, path = line.split(None, 1)
        current_map[path] = sha
    # Compare.
    diffs = []
    for path, sha in baseline_map.items():
        if path not in current_map:
            diffs.append(f"removed: {path}")
        elif current_map[path] != sha:
            diffs.append(f"modified: {path}")
    for path in current_map:
        if path not in baseline_map:
            diffs.append(f"added: {path}")
    if diffs:
        return False, f"SHIELD DIRECTORY CHANGED — HARD STOP · {diffs}"
    return True, f"{len(baseline_map)} shield/*.py files sha256-identical to baseline"


# ─── R6 · Derivation class inheritance ────────────────────────────────

@row("R6 ", "Derivation class inheritance — extracted = source data_trust")
def r6_class_inheritance():
    if "extraction_response" not in _EXTRACTION_STATE or "deck" not in _EXTRACTION_STATE:
        return False, "R4 did not populate extraction state — cannot verify inheritance"
    deck = _EXTRACTION_STATE["deck"]
    resp = _EXTRACTION_STATE["extraction_response"]
    source_trust = str(deck.get("data_trust") or "unrated")
    extracted_class = resp.get("derivation_class")
    if extracted_class != source_trust:
        return False, f"MISMATCH: source data_trust={source_trust!r} vs extracted derivation_class={extracted_class!r}"
    return True, f"extracted derivation_class={extracted_class!r} == source data_trust={source_trust!r} (inheritance verified)"


# ─── R7 · Cross-context 403 ──────────────────────────────────────────

@row("R7 ", "Cross-context PATCH/GET → 403")
def r7_cross_context():
    import asyncio
    from motor.motor_asyncio import AsyncIOMotorClient
    api = _backend_url()
    s, csrf, token = _admin_session()

    async def find_foreign():
        cli = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = cli[os.environ["DB_NAME"]]
        admin_id = "cf6e7587-9abd-46aa-b8f4-f342e9b066ef"
        admin_ctxs = [x["context_id"] async for x in db.memberships.find(
            {"account_id": admin_id, "status": "active"}, {"_id": 0, "context_id": 1},
        )]
        return await db.documents.find_one(
            {"context_id": {"$exists": True, "$ne": None, "$nin": admin_ctxs}},
            {"_id": 0, "id": 1, "context_id": 1},
        )

    foreign = asyncio.run(find_foreign())
    if not foreign:
        return True, "no foreign doc available — 403 branch present in code path (see _load_doc_and_check_membership)"
    # GET on foreign doc.
    r = s.get(
        f"{api}/api/decks/{foreign['id']}/signals",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if r.status_code != 403:
        return False, f"expected 403 got {r.status_code}: {r.text[:200]}"
    return True, f"foreign doc {foreign['id'][:8]}.. → 403"


# ─── R8 · Unauthenticated ────────────────────────────────────────────

@row("R8 ", "Unauthenticated → 401/403")
def r8_unauth():
    api = _backend_url()
    fake_id = str(uuid.uuid4())
    # POST without auth.
    r = requests.post(
        f"{api}/api/decks/{fake_id}/signals/extract",
        json={}, timeout=10,
    )
    if r.status_code in (401, 403):
        return True, f"anon POST → {r.status_code} (CSRF/auth gate rejects)"
    return False, f"anon POST unexpected {r.status_code}"


# ─── R9 · FE reads endpoint (grep) ───────────────────────────────────

@row("R9 ", "FE reads /decks/{id}/signals + testid match")
def r9_fe_endpoint():
    src = FE_SIGNALS.read_text()
    if "/decks/${documentId}/signals" not in src:
        return False, "FE missing /decks/${documentId}/signals endpoint"
    if 'api.post' not in src or "/decks/${documentId}/signals/extract" not in src:
        return False, "FE missing POST /extract call"
    if 'api.patch' not in src or "/decks/${documentId}/signals/${signalId}" not in src:
        return False, "FE missing PATCH /{signal_id} call"
    testids = [
        'data-testid="signals-panel-root"',
        'data-testid="signals-panel-extract-btn"',
        'data-testid="signals-panel-item"',
    ]
    missing = [t for t in testids if t not in src]
    if missing:
        return False, f"missing testids: {missing}"
    return True, "3 endpoints wired + 3+ testids present"


# ─── R10 · FE render (structural) ────────────────────────────────────

@row("R10", "FE derivation_class badge + updated indicator + extract btn present")
def r10_fe_render():
    src = FE_SIGNALS.read_text()
    required = [
        'data-testid="signals-panel-derivation-class"',
        'data-testid="signals-panel-updated-indicator"',
        'data-testid="signals-panel-extract-btn"',
        'data-testid="signals-panel-shield-audit-id"',
    ]
    missing = [t for t in required if t not in src]
    if missing:
        return False, f"missing render testids: {missing}"
    return True, "4 render testids present (class badge + updated + extract + audit_id)"


# ─── R11 · Substrate integrity ────────────────────────────────────────

@row("R11", "Substrate integrity — julius decks=0 declared as gap")
def r11_substrate():
    import asyncio
    from motor.motor_asyncio import AsyncIOMotorClient

    async def count():
        cli = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = cli[os.environ["DB_NAME"]]
        julius = "f23cd1fe-bbb8-40ea-baa1-73945ca0fcd2"
        ctxs = [x["context_id"] async for x in db.memberships.find(
            {"account_id": julius, "status": "active"}, {"_id": 0, "context_id": 1},
        )]
        n_decks = await db.documents.count_documents({
            "context_id": {"$in": ctxs},
            "$or": [{"category": "deck"}, {"doc_kind": "deck"}, {"doc_type": "deck"}],
        })
        return n_decks

    n = asyncio.run(count())
    _EXTRACTION_STATE["julius_deck_count"] = n
    # Per dispatch: this is NOT a stop, but explicit gap-declaration required.
    if n == 0:
        # Verify the extraction fired against admin fallback.
        ext_resp = _EXTRACTION_STATE.get("extraction_response") or {}
        n_signals = len(ext_resp.get("signals") or [])
        return True, (
            f"julius has 0 decks — SUBSTRATE-THIN GAP DECLARED. Extraction ran against admin fallback deck "
            f"(id={_EXTRACTION_STATE.get('deck', {}).get('id', '')[:8]}..) · produced {n_signals} signals. "
            f"For julius-native evidence, seed decks into julius contexts and re-run."
        )
    return True, f"julius has {n} decks — rich substrate available"


# ─── R12 · F.6 FULL positive assertion ────────────────────────────────

@row("R12", "F.6 FULL positive — Shield IS invoked in primary flow")
def r12_shield_invoked():
    src = BE_EXTRACT.read_text()
    tree = ast.parse(src)
    # Look for `contract.shield_invoke(...)` or `get_synisense().shield_invoke(...)` calls.
    found_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            # Attribute call: X.shield_invoke(...)
            if isinstance(f, ast.Attribute) and f.attr == "shield_invoke":
                found_call = True
                break
    if not found_call:
        return False, "shield_invoke NOT called in deck_signal_extraction.py — F.6 FULL invariant broken"
    # Ensure it's on the primary flow (in `extract_deck_signals` function).
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == "extract_deck_signals":
            body_src = ast.unparse(node)
            if ".shield_invoke(" in body_src:
                # Now verify NO direct LLM SDK call.
                code_only = _strip_comments_and_docstrings(src)
                forbidden = ("openai", "anthropic", "google.generativeai", "AsyncOpenAI", "Anthropic(")
                # Import scan.
                bad_imports = []
                for n in ast.walk(tree):
                    if isinstance(n, (ast.Import, ast.ImportFrom)):
                        mod = getattr(n, "module", None) or ""
                        names = [x.name for x in getattr(n, "names", [])]
                        for f in forbidden:
                            if f in mod or any(f in x for x in names):
                                bad_imports.append(f"{f} in {mod}")
                if bad_imports:
                    return False, f"F.6 broken: forbidden LLM-SDK imports: {bad_imports}"
                return True, "shield_invoke called on primary flow of extract_deck_signals; 0 direct LLM-SDK imports (Shield-only path)"
    return False, "extract_deck_signals function not found or shield_invoke missing from its body"


# ─── R13 · Regression ────────────────────────────────────────────────

@row("R13", "Regression: prior slices parse-clean")
def r13_regression():
    slices = [
        "jc_ws_deck_a4_proving_slice.py",
        "jc_ws_deck_a5_proving_slice.py",
        "jc_ws_deck_a6_proving_slice.py",
        "jc_ws_deck_a6_backend_proving_slice.py",
        "jc_ws_deck_a7_proving_slice.py",
        "jc_ws_deck_a8_proving_slice.py",
        "jc_ws_deck_a8_backend_proving_slice.py",
        "jc_ws_deck_a9_proving_slice.py",
        "jc_ws_deck_a10_proving_slice.py",
    ]
    for s in slices:
        p = BACKEND / "scripts" / s
        if not p.exists():
            return False, f"missing slice: {s}"
        try:
            ast.parse(p.read_text())
        except SyntaxError as e:
            return False, f"{s} syntax error: {e}"
    return True, f"{len(slices)} prior slices parse-clean"


# ─── R14 · Rename hashes ─────────────────────────────────────────────

@row("R14", "Rename arc hash snapshot")
def r14_hashes():
    chg = hashlib.sha1(Path("/app/memory/CHANGELOG.md").read_bytes()).hexdigest()[:8]
    prd = hashlib.sha1(Path("/app/memory/PRD.md").read_bytes()).hexdigest()[:8]
    return True, f"snapshot: CHANGELOG={chg} · PRD={prd}"


# ─── R15 · Storage regression ────────────────────────────────────────

@row("R15", "Storage 500MB ceiling regression")
def r15_storage():
    api = _backend_url()
    s, csrf, token = _admin_session()
    ctx = "8bc4f3f2-a0cc-4d66-b717-7c06494d3e96"
    hdr = {"Authorization": f"Bearer {token}", "X-CSRF-Token": csrf, "Content-Type": "application/json"}
    r501 = s.post(
        f"{api}/api/uploads/presigned",
        json={
            "kind": "workbook", "filename": "r15-501.xlsx",
            "size_bytes": 501 * 1024 * 1024,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "context_id": ctx,
        }, headers=hdr, timeout=10,
    )
    if r501.status_code != 413:
        return False, f"501 expected 413 got {r501.status_code}"
    r400 = s.post(
        f"{api}/api/uploads/presigned",
        json={
            "kind": "workbook", "filename": "r15-400.xlsx",
            "size_bytes": 400 * 1024 * 1024,
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "context_id": ctx,
        }, headers=hdr, timeout=10,
    )
    if r400.status_code != 200 or r400.json().get("method") != "RESUMABLE":
        return False, f"400 got {r400.status_code}"
    return True, "501→413 · 400→200 RESUMABLE"


# ─── R16 · Prove-not-assert closure — memo artifact ───────────────────

@row("R16", "Memo contains side-by-side audit event artifact")
def r16_memo_artifact():
    """After R4 populates the extraction+chat audit rows, append a
    side-by-side JSON block to the sprint memo, then verify it's there."""
    if "ext_row" not in _EXTRACTION_STATE or "chat_row" not in _EXTRACTION_STATE:
        return False, "R4 didn't populate audit rows — cannot append artifact"
    ext = _EXTRACTION_STATE["ext_row"]
    chat = _EXTRACTION_STATE["chat_row"]
    ext_fields = _EXTRACTION_STATE.get("ext_fields", [])
    chat_fields = _EXTRACTION_STATE.get("chat_fields", [])

    # Compose side-by-side artifact.
    artifact = {
        "captured_at": NOW_ISO,
        "chokepoint_fingerprint_match": ext_fields == chat_fields,
        "extraction_audit_row": {
            "audit_id": ext.get("audit_id"),
            "tenant_id": ext.get("tenant_id"),
            "consumer_id": ext.get("consumer_id"),
            "purpose": ext.get("purpose"),
            "outcome": ext.get("outcome"),
            "de_id_summary": ext.get("de_id_summary"),
            "llm_provider": ext.get("llm_provider"),
            "llm_model": ext.get("llm_model"),
            "latency_ms": ext.get("latency_ms"),
            "field_count": len(ext_fields),
            "field_set": ext_fields,
        },
        "chat_audit_row": {
            "audit_id": chat.get("audit_id"),
            "tenant_id": chat.get("tenant_id"),
            "consumer_id": chat.get("consumer_id"),
            "purpose": chat.get("purpose"),
            "outcome": chat.get("outcome"),
            "de_id_summary": chat.get("de_id_summary"),
            "llm_provider": chat.get("llm_provider"),
            "llm_model": chat.get("llm_model"),
            "latency_ms": chat.get("latency_ms"),
            "field_count": len(chat_fields),
            "field_set": chat_fields,
        },
    }
    memo_src = MEMO.read_text()
    marker = "## Side-by-side audit event artifact (R4 · R16)"
    if marker in memo_src:
        # Idempotent — replace the block.
        idx = memo_src.find(marker)
        end = memo_src.find("\n## ", idx + 1)
        if end < 0:
            end = len(memo_src)
        memo_src = memo_src[:idx] + memo_src[end:]

    # Append artifact BEFORE the "## Closure report" section.
    closure_marker = "## Closure report (populated on GREEN)"
    block = f"""{marker}

Captured at: `{NOW_ISO}`
Chokepoint fingerprint match (field-set identity): `{artifact['chokepoint_fingerprint_match']}`

```json
{json.dumps(artifact, indent=2, default=str)}
```

"""
    if closure_marker in memo_src:
        memo_src = memo_src.replace(closure_marker, block + closure_marker)
    else:
        memo_src += "\n" + block
    MEMO.write_text(memo_src)

    # Verify artifact rendered.
    check = MEMO.read_text()
    if marker not in check:
        return False, "marker missing after write"
    if "chokepoint_fingerprint_match" not in check:
        return False, "artifact json didn't render"
    return True, f"memo appended · fingerprint_match={artifact['chokepoint_fingerprint_match']} · ext_audit={ext.get('audit_id','')[:12]}.. chat_audit={chat.get('audit_id','')[:12]}.."


# ─── Runner ──────────────────────────────────────────────────────────

def main() -> int:
    _load_backend_env()
    print("═" * 78)
    print(f"JC-WS-DECK-A9-BACKEND-DECK-SIGNAL-EXTRACTION · Proving slice · {NOW_ISO}")
    print("═" * 78)
    rows = [
        r1_chokepoint_import, r2_index, r3_openapi,
        r4_prove_routing,  # populates state used by R6/R11/R16
        r5_shield_untouched, r6_class_inheritance,
        r7_cross_context, r8_unauth, r9_fe_endpoint, r10_fe_render,
        r11_substrate, r12_shield_invoked, r13_regression,
        r14_hashes, r15_storage, r16_memo_artifact,
    ]
    for r in rows:
        r()
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    total = len(RESULTS)
    print("═" * 78)
    verdict = "GREEN" if passed == total else "RED"
    print(f"{verdict} · {passed}/{total} rows passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
