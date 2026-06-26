"""Owner Digest v0 — Monday 9am owner-tz, deterministic-only, skip-if-no-delta.

Canonical spec: /app/memory/JC_MON_CANONICAL_SPEC.md (Wave 3 backlog item
"Owner Digest v0" — Monday morning ritual, owner-tz, deterministic-only
content, skip-if-no-delta; replies route to TM Journal accept rail).

What this module does:
  • Computes a per-context, per-owner weekly digest from the
    `strategic_goals` collection. Deterministic content ONLY — no
    Shield, no LLM, no synthesised prose.
  • Captures a snapshot hash so the next run can SKIP the digest
    when nothing material changed since the last delivery.
  • Persists the digest into `db.owner_digests` for retrieval by
    delivery rails (email transport, in-app notification, etc.).
  • The cron entry point lives in `routers/owner_digest.py`.

Out of scope (v0):
  • Email/SMS transport — the digest row is the artefact; delivery
    rails are wired in v0.5 once SendGrid templates are approved.
  • Per-user TZ resolution beyond what `account.preferences.tz`
    already exposes — defaults to UTC when missing.
  • Reply-routing to the Document Journal — the canonical spec says
    "replies route to TM Journal accept rail" which means the reply
    handler stuffs the inbound message into the existing
    `documents` collection with `source_channel='owner_digest_reply'`
    and lifecycle_state='pending' so the Journal's existing accept
    affordance picks it up. The reply handler is also v0.5.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from core import db, iso, now


# ─── Helpers ────────────────────────────────────────────────────────


def _iso_week(dt: datetime) -> str:
    """Return ISO week label 'YYYY-Www'. UTC-anchored."""
    y, w, _ = dt.isocalendar()
    return f"{y:04d}-W{w:02d}"


def _score_band(score: Optional[float]) -> str:
    if score is None:
        return "unknown"
    if score >= 80:
        return "strong"
    if score >= 60:
        return "moderate"
    if score >= 40:
        return "weak"
    return "critical"


def _delta_hash(payload: Dict[str, Any]) -> str:
    """Stable hash of the *content* fields used for skip-if-no-delta.

    Only the parts of the payload that signal "material change" go in.
    Timestamps, render order, and counters are excluded.
    """
    rows = []
    for r in payload.get("rows", []):
        rows.append({
            "goal_id":    r.get("goal_id"),
            "status":     r.get("status"),
            "score":      r.get("current_score"),
            "probability": r.get("probability"),
            "band":       _score_band(r.get("current_score")),
        })
    rows.sort(key=lambda x: (x.get("goal_id") or ""))
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ─── Public composer ───────────────────────────────────────────────


async def build_owner_digest(
    *,
    context_id: str,
    owner_account_id: str,
    week_label: Optional[str] = None,
) -> Dict[str, Any]:
    """Compose a fresh deterministic digest payload for `context_id`.

    The composition reads `strategic_goals` for this context, plus
    each goal's `score_history` to determine "last week's score" for
    the delta. **Zero LLM/Shield calls.** Returns a dict ready to
    `insert_one` into `db.owner_digests`. Caller decides whether to
    persist (skip-if-no-delta gate lives in `compose_or_skip`).
    """
    week_label = week_label or _iso_week(now())
    week_start = now() - timedelta(days=7)

    goals = await db.strategic_goals.find(
        {"context_id": context_id}, {"_id": 0},
    ).to_list(500)

    rows: List[Dict[str, Any]] = []
    for g in goals:
        hist = g.get("score_history") or []
        # Last score recorded BEFORE the 7-day window opened — that's
        # the "previous reading" we compare against. If no historical
        # entry pre-dates the window, treat prev_score as None.
        prev_score: Optional[float] = None
        prev_score_at_dt: Optional[datetime] = None
        for h in hist:
            ts = h.get("recorded_at")
            try:
                hdt = datetime.fromisoformat((ts or "").replace("Z", "+00:00"))
                if hdt.tzinfo is None:
                    hdt = hdt.replace(tzinfo=timezone.utc)
            except Exception:  # noqa: BLE001 — best-effort parse
                continue
            if hdt >= week_start:
                continue
            if prev_score_at_dt is None or hdt > prev_score_at_dt:
                prev_score = h.get("score")
                prev_score_at_dt = hdt

        curr_score = g.get("current_score")
        delta_score = None
        if isinstance(prev_score, (int, float)) and isinstance(curr_score, (int, float)):
            delta_score = round(curr_score - prev_score, 2)

        rows.append({
            "goal_id":       g.get("id"),
            "title":         g.get("title"),
            "status":        g.get("status"),
            "category":      g.get("category"),
            "current_score": curr_score,
            "previous_score": prev_score,
            "delta_score":   delta_score,
            "probability":   g.get("probability"),
            "target_value":  g.get("target_value"),
            "target_metric": g.get("target_metric"),
            "target_date":   g.get("target_date"),
        })

    rows.sort(key=lambda r: (
        # Surface "off_track" + "at_risk" first; achievements last.
        {"off_track": 0, "at_risk": 1, "on_track": 2,
         "achieved": 3, "abandoned": 4, "not_started": 5}.get(r.get("status") or "", 9),
        r.get("title") or "",
    ))

    payload: Dict[str, Any] = {
        "week_label": week_label,
        "context_id": context_id,
        "owner_account_id": owner_account_id,
        "rows": rows,
        "rows_count": len(rows),
        "rows_off_track": sum(1 for r in rows if r.get("status") == "off_track"),
        "rows_at_risk":   sum(1 for r in rows if r.get("status") == "at_risk"),
        "rows_on_track":  sum(1 for r in rows if r.get("status") == "on_track"),
        "rows_achieved":  sum(1 for r in rows if r.get("status") == "achieved"),
        "generated_at": iso(now()),
        # Tag the surface; the future reply rail uses this to route
        # the inbound document into the Document Journal pending
        # state with the right source_channel marker.
        "surface": "owner_digest_v0",
    }
    payload["delta_hash"] = _delta_hash(payload)
    return payload


def _to_dt(iso_str: str) -> datetime:
    """Best-effort ISO-8601 → aware datetime."""
    try:
        d = datetime.fromisoformat((iso_str or "").replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


async def compose_or_skip(
    *, context_id: str, owner_account_id: str,
    week_label: Optional[str] = None,
) -> Tuple[Dict[str, Any], bool]:
    """Compose the digest and decide if we should skip (no delta).

    Returns `(payload, should_skip)`. When `should_skip=True` the
    caller MUST NOT persist or deliver — the previous digest's hash
    matches this one, meaning nothing material changed since the
    last delivery. When `False`, the caller persists the row +
    triggers the delivery rail.
    """
    payload = await build_owner_digest(
        context_id=context_id, owner_account_id=owner_account_id,
        week_label=week_label,
    )
    last = await db.owner_digests.find_one(
        {"context_id": context_id, "owner_account_id": owner_account_id},
        sort=[("generated_at", -1)],
    )
    if last and last.get("delta_hash") == payload["delta_hash"]:
        return payload, True
    return payload, False


async def persist_digest(payload: Dict[str, Any]) -> str:
    """Insert the digest row, return its `id`."""
    import uuid
    payload = dict(payload)
    payload["id"] = str(uuid.uuid4())
    await db.owner_digests.insert_one(payload)
    payload.pop("_id", None)
    return payload["id"]
