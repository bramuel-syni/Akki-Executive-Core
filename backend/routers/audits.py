"""audits router — public read-only markdown audit-file server.

Serves the four planning audits shipped 2026-07-02 (JC-WS deck
conformance, Solva-module rename regression, Shield-below-chat
investigation, Solva-engine-vs-module distinction) under
`/api/audits/{name}` for direct browser access at the preview URL.

Content is non-sensitive planning documentation — no auth is required.
Strict allowlist prevents path traversal or arbitrary file exposure.

Dispatch: AUDITS-BACKEND-ROUTE (2026-07-02) + JC-WS-A1-BASELINE-
INVARIANT-RESTORATION (2026-07-02) which renamed the halted
regression-audit file to `SOLVA_MODULE_RENAME_REGRESSION_AUDIT.md`
to restore the FE-only-label hard-ratchet invariant to zero backend
matches. Full rename provenance is captured in
`memory/DEV_PIPELINE.md §9`.

Proving slice: /app/backend/scripts/audits_backend_route_proving_slice.py.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse


router = APIRouter(prefix="/api", tags=["audits"])


AUDITS_DIR = Path("/app/memory/audits")

# Strict allowlist — only these three filenames are served. Anything
# else returns 404. This is deliberately non-configurable to keep the
# route surface locked to the current dispatch's approved artefacts.
_ALLOWLIST = frozenset(
    {
        "JC_WS_DECK_CONFORMANCE_AUDIT.md",
        "SOLVA_MODULE_RENAME_REGRESSION_AUDIT.md",
        "SHIELD_BELOW_CHAT_REGRESSION_INVESTIGATION.md",
        "SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md",
    }
)


@router.get("/audits/{name}", response_class=PlainTextResponse)
def get_audit(name: str) -> PlainTextResponse:
    """Serve a whitelisted audit markdown file as plain markdown text.

    Args:
        name: Bare filename (e.g. `JC_WS_DECK_CONFORMANCE_AUDIT.md`).
            Must be exactly one of the three allowlisted names. Anything
            containing path-traversal tokens (`..`, `/`, `\\`, absolute
            paths) or not in the allowlist returns 404.

    Returns:
        text/markdown body with UTF-8 charset.

    Raises:
        HTTPException 404 for any non-allowlisted filename or path-
        traversal attempt.
    """
    # Reject obvious path-traversal / non-basename inputs BEFORE the
    # allowlist check, so callers get a clean 404 without ever loading
    # a resolved path near the filesystem.
    if not name or "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=404, detail="audit not found")
    if name not in _ALLOWLIST:
        raise HTTPException(status_code=404, detail="audit not found")

    target = AUDITS_DIR / name
    # Defensive: even after allowlist, confirm the resolved path is
    # actually under AUDITS_DIR (no symlink surprises).
    try:
        resolved = target.resolve(strict=True)
    except (FileNotFoundError, RuntimeError):
        raise HTTPException(status_code=404, detail="audit not found")
    if AUDITS_DIR.resolve() not in resolved.parents:
        raise HTTPException(status_code=404, detail="audit not found")

    try:
        body = target.read_text(encoding="utf-8")
    except OSError:
        raise HTTPException(status_code=404, detail="audit not found")

    return PlainTextResponse(
        content=body,
        media_type="text/markdown; charset=utf-8",
    )
