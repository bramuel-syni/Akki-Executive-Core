"""Phase 15 — Master Documentation Download Endpoints.

Three FastAPI routes deliver the two master docs (PRODUCT.md, DEVELOPMENT.md)
as Markdown downloads, plus a zip bundle. Sources live under /app/memory/.

Auth model: currently UNAUTHENTICATED. This is intentional because the
preview pod is private. The downloads are not surfaced in the public
frontend either. Before exposing this on a public-route surface, gate
the routes behind `require_admin` (the codebase's standard superadmin
dependency).

# TODO(prod-hardening): gate behind require_admin once docs go public-route.
"""
from __future__ import annotations

import io
import logging
import os
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/docs", tags=["docs-download"])


# Resolver — kept as a module-level function (not a constant) so tests can
# monkeypatch the source paths. The mapping below is the single source of
# truth for what each download endpoint serves.
def _resolve_doc_paths() -> Dict[str, Path]:
    """Return the canonical source paths for each downloadable doc."""
    memory_dir = Path(os.environ.get("AKKI_MEMORY_DIR") or "/app/memory")
    return {
        "product":      memory_dir / "PRODUCT.md",
        "development":  memory_dir / "DEVELOPMENT.md",
        "features":     memory_dir / "PRODUCT_FEATURE_REVIEW.md",
        "module_specs": memory_dir / "MODULE_PRODUCT_SPECS.md",
    }


_DOWNLOAD_FILENAMES: Dict[str, str] = {
    "product":      "AKKI_PRODUCT.md",
    "development":  "AKKI_DEVELOPMENT.md",
    "features":     "AKKI_PRODUCT_FEATURE_REVIEW.md",
    "module_specs": "AKKI_MODULE_PRODUCT_SPECS.md",
}


def _missing_docs() -> List[str]:
    """Return list of doc keys whose source file is missing."""
    paths = _resolve_doc_paths()
    return [k for k, p in paths.items() if not p.exists() or p.stat().st_size == 0]


def _not_generated_response(missing: List[str]) -> JSONResponse:
    """Documented 503 shape — Pre-Read §C honesty/safety requirement."""
    logger.error(
        "docs_download: source markdown missing or empty",
        extra={"missing": missing},
        exc_info=True,
    )
    return JSONResponse(
        status_code=503,
        content={
            "error":   "documentation_not_yet_generated",
            "missing": missing if len(missing) < 2 else ["both"],
        },
    )


@router.get("/product")
async def download_product_doc():
    """Stream PRODUCT.md as an attachment."""
    paths = _resolve_doc_paths()
    src = paths["product"]
    if not src.exists() or src.stat().st_size == 0:
        return _not_generated_response(["product"])
    return FileResponse(
        path=str(src),
        media_type="text/markdown",
        filename=_DOWNLOAD_FILENAMES["product"],
        headers={
            "Content-Disposition": (
                f'attachment; filename="{_DOWNLOAD_FILENAMES["product"]}"'
            ),
        },
    )


@router.get("/development")
async def download_development_doc():
    """Stream DEVELOPMENT.md as an attachment."""
    paths = _resolve_doc_paths()
    src = paths["development"]
    if not src.exists() or src.stat().st_size == 0:
        return _not_generated_response(["development"])
    return FileResponse(
        path=str(src),
        media_type="text/markdown",
        filename=_DOWNLOAD_FILENAMES["development"],
        headers={
            "Content-Disposition": (
                f'attachment; filename="{_DOWNLOAD_FILENAMES["development"]}"'
            ),
        },
    )


@router.get("/bundle.zip")
async def download_doc_bundle():
    """Stream a zip containing PRODUCT.md + DEVELOPMENT.md as
    AKKI_PRODUCT.md and AKKI_DEVELOPMENT.md respectively.

    Builds in-memory (`io.BytesIO`) — no disk artefact, no temp file.
    """
    missing = _missing_docs()
    if missing:
        return _not_generated_response(missing)

    paths = _resolve_doc_paths()
    buf = io.BytesIO()
    try:
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for key, src in paths.items():
                arcname = _DOWNLOAD_FILENAMES[key]
                # Read bytes (not text) — preserves UTF-8 BOM-free content.
                zf.writestr(arcname, src.read_bytes())
    except Exception:
        logger.exception("docs_download: failed to build bundle zip")
        return JSONResponse(
            status_code=503,
            content={"error": "documentation_bundle_build_failed"},
        )

    buf.seek(0)
    return StreamingResponse(
        content=iter([buf.getvalue()]),
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="AKKI_DOCS.zip"',
        },
    )


__all__ = ["router"]
