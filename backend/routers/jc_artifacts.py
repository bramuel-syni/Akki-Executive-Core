"""JC artefact viewing — internal, superadmin-gated downloads.

This router exists so the user can pull JC build artefacts directly
out of the preview pod by hitting an authenticated URL. The first
artefact wired through is the Track-2 divergent first-render deck
(`/app/memory/jc_artifacts/jc_tl/track2/divergent-first-render.pptx`)
— shipped 2026-06-26 per `JC_TL_TRACK2_MIN_SCOPE.md`.

Auth model: `is_superadmin` gate. JC artefacts are internal build
outputs; never surfaced to non-admin users.

The whitelist approach (rather than path traversal under
`/app/memory/jc_artifacts/`) is deliberate: we ONLY serve the
artefacts we've explicitly chosen to expose. Adding a new artefact
URL is a one-line registration.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from core import get_current_account

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jc-artifacts", tags=["jc-artifacts"])


async def _require_admin(current: Dict[str, Any] = Depends(get_current_account)) -> Dict[str, Any]:
    if not current.get("is_superadmin"):
        raise HTTPException(status_code=403, detail="Superadmin only.")
    return current


# Whitelist of artefacts exposed for internal viewing. Key = URL slug;
# value = (filesystem path, download filename, media type).
_ARTEFACTS = {
    "track2/divergent-first-render.pptx": (
        Path("/app/memory/jc_artifacts/jc_tl/track2/divergent-first-render.pptx"),
        "JC-TL-Track2-divergent-first-render.pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ),
    "track2/convergent-regression.pptx": (
        Path("/app/memory/jc_artifacts/jc_tl/track2/convergent-regression.pptx"),
        "JC-TL-Track2-convergent-regression.pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ),
    # JC-TL GP ship (2026-06-26) — 3 representative divergent renders.
    "gp-ship/regulatory.pptx": (
        Path("/app/memory/jc_artifacts/jc_tl/03-gp-ship/sess-jctl-gp-ship-regulatory.pptx"),
        "JC-TL-GP-Ship-Regulatory.pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ),
    "gp-ship/investment.pptx": (
        Path("/app/memory/jc_artifacts/jc_tl/03-gp-ship/sess-jctl-gp-ship-investment.pptx"),
        "JC-TL-GP-Ship-Investment.pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ),
    "gp-ship/launch.pptx": (
        Path("/app/memory/jc_artifacts/jc_tl/03-gp-ship/sess-jctl-gp-ship-launch.pptx"),
        "JC-TL-GP-Ship-Launch.pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ),
}


@router.get("/track2/{filename}")
async def get_track2_artefact(filename: str, _: Dict[str, Any] = Depends(_require_admin)):
    """Serve a JC-TL Track-2 build artefact. Superadmin only."""
    slug = f"track2/{filename}"
    if slug not in _ARTEFACTS:
        raise HTTPException(status_code=404, detail="artefact_not_whitelisted")
    fs_path, download_name, media_type = _ARTEFACTS[slug]
    if not fs_path.exists():
        raise HTTPException(status_code=404, detail="artefact_file_missing")
    return FileResponse(
        path=str(fs_path),
        media_type=media_type,
        filename=download_name,
    )


@router.get("/gp-ship/{filename}")
async def get_gp_ship_artefact(filename: str, _: Dict[str, Any] = Depends(_require_admin)):
    """Serve a JC-TL GP ship build artefact. Superadmin only.

    Exposes the 3 representative divergent renders produced by the
    proving slice (`scripts/jc_tl_gp_ship_slice.py`):
      • regulatory.pptx — regulatory-action persona spread
        (auditor / regulator / customer-advocate)
      • investment.pptx — investment-thesis persona spread
        (founder / CFO / VC partner)
      • launch.pptx — product-launch persona spread
        (PM / engineering / sales)
    """
    slug = f"gp-ship/{filename}"
    if slug not in _ARTEFACTS:
        raise HTTPException(status_code=404, detail="artefact_not_whitelisted")
    fs_path, download_name, media_type = _ARTEFACTS[slug]
    if not fs_path.exists():
        raise HTTPException(status_code=404, detail="artefact_file_missing")
    return FileResponse(
        path=str(fs_path),
        media_type=media_type,
        filename=download_name,
    )
