"""Owner Digest v0.5 — Monday 9am owner-tz (real per-context resolution),
deterministic-only, skip-if-no-delta. SendGrid delivery + reply-handler
routing into the existing Document Journal accept rail.

Canonical spec: /app/memory/JC_MON_CANONICAL_SPEC.md (Wave 3 backlog item
"Owner Digest" — v0 shipped the deterministic composer + skip-gate; v0.5
lights up the delivery rail and the reply rail).

What this module does:
  • Composes a per-context, per-owner weekly digest from the
    `strategic_goals` collection. Deterministic content ONLY — no
    Shield, no LLM, no synthesised prose.
  • Captures a snapshot hash so the next run can SKIP the digest
    when nothing material changed since the last delivery.
  • Persists the digest into `db.owner_digests` for retrieval by
    delivery rails (email transport, in-app notification, etc.).
  • v0.5: resolves per-context owner timezone via `accounts.preferences.tz`;
    cron caller pulls only the contexts whose local hour matches the
    target 9 AM.
  • v0.5: sends via SendGrid (`_send_via_sendgrid` from
    `services.cohort_email`) with a deterministic plain+HTML body
    and a `Reply-To: digest+<id>@<SENDGRID_INBOUND_DOMAIN>` alias so
    replies route back into the Document Journal accept rail via the
    existing inbound-email handler.
  • v0.5: the inbound handler discriminates by alias prefix
    (`digest+...`) and inserts a `documents` row with
    `source_channel="owner_digest_reply"` + `lifecycle_state="pending"`
    so the Journal's existing accept affordance picks it up — zero
    net-new code on the accept rail itself.
"""
from __future__ import annotations

import hashlib
import json
import os
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



# ─── v0.5 — per-context TZ resolver ────────────────────────────────


# IANA tz database is included with Python 3.9+ stdlib (zoneinfo).
try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except Exception:  # pragma: no cover — Py<3.9 fallback (no-op)
    ZoneInfo = None  # type: ignore
    ZoneInfoNotFoundError = Exception  # type: ignore


async def resolve_owner_tz(owner_account_id: str) -> str:
    """Look up the owner's preferred timezone string. Default UTC."""
    acc = await db.accounts.find_one(
        {"id": owner_account_id},
        {"_id": 0, "preferences": 1, "timezone": 1},
    )
    tz = (
        (acc or {}).get("preferences", {}).get("tz")
        or (acc or {}).get("preferences", {}).get("timezone")
        or (acc or {}).get("timezone")
        or "UTC"
    )
    return tz or "UTC"


def is_target_hour_local(tz_name: str, target_hour: int = 9) -> bool:
    """True iff "right now" in the owner's tz is the target hour of day.

    Used by the hourly cron sweep: only the contexts whose owner-tz
    matches the target local hour receive a digest send this hour.
    Defaults to UTC when the tz string is unknown.
    """
    if ZoneInfo is None:
        return datetime.now(timezone.utc).hour == target_hour
    try:
        zi = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        zi = ZoneInfo("UTC")
    return datetime.now(zi).hour == target_hour


def is_target_dow_local(tz_name: str, target_dow: int = 0) -> bool:
    """True iff "right now" in the owner's tz is the target day-of-week.

    Monday = 0 (Python weekday()).
    """
    if ZoneInfo is None:
        return datetime.now(timezone.utc).weekday() == target_dow
    try:
        zi = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        zi = ZoneInfo("UTC")
    return datetime.now(zi).weekday() == target_dow


# ─── v0.5 — SendGrid delivery ──────────────────────────────────────


def _build_subject(payload: Dict[str, Any]) -> str:
    counts = (
        f"{payload['rows_off_track']} off-track · "
        f"{payload['rows_at_risk']} at-risk · "
        f"{payload['rows_on_track']} on-track"
    )
    return f"AKKI Owner Digest · {payload['week_label']} · {counts}"


def _build_plain_body(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"AKKI Owner Digest · week {payload['week_label']}")
    lines.append("")
    lines.append(
        f"Goals: {payload['rows_count']}  ·  Off-track: {payload['rows_off_track']}  "
        f"·  At-risk: {payload['rows_at_risk']}  ·  On-track: {payload['rows_on_track']}  "
        f"·  Achieved: {payload['rows_achieved']}"
    )
    lines.append("")
    for r in payload["rows"][:20]:
        delta = ""
        if r.get("delta_score") is not None:
            sign = "+" if r["delta_score"] >= 0 else ""
            delta = f"  ({sign}{r['delta_score']}pt)"
        status_label = (r.get("status") or "").replace("_", " ").title()
        score = "—" if r.get("current_score") is None else f"{r['current_score']}%"
        lines.append(
            f"- [{status_label}] {r.get('title') or '(untitled)'}  ·  {score}{delta}"
        )
    lines.append("")
    lines.append(
        "Reply to this email to drop a note in your Document Journal — "
        "Akki routes it as a pending document tied to this digest."
    )
    return "\n".join(lines)


def _build_html_body(payload: Dict[str, Any]) -> str:
    rows_html: List[str] = []
    for r in payload["rows"][:20]:
        status = (r.get("status") or "").replace("_", " ").title()
        score = "—" if r.get("current_score") is None else f"{r['current_score']}%"
        delta_html = ""
        if r.get("delta_score") is not None:
            sign = "+" if r["delta_score"] >= 0 else ""
            color = "#a63030" if r["delta_score"] < 0 else "#1f7a3a"
            delta_html = (
                f" <span style='color:{color};font-size:12px'>"
                f"({sign}{r['delta_score']}pt)</span>"
            )
        rows_html.append(
            "<tr>"
            f"<td style='padding:6px 10px;font-size:13px;color:#444'>{status}</td>"
            f"<td style='padding:6px 10px;font-size:13px'>{(r.get('title') or '').replace('<','&lt;')[:140]}</td>"
            f"<td style='padding:6px 10px;font-size:13px;text-align:right'>"
            f"{score}{delta_html}</td>"
            "</tr>"
        )
    counts_html = (
        f"<span style='color:#a63030'><strong>{payload['rows_off_track']}</strong> off-track</span>"
        f" · <span style='color:#b08020'><strong>{payload['rows_at_risk']}</strong> at-risk</span>"
        f" · <span style='color:#1f7a3a'><strong>{payload['rows_on_track']}</strong> on-track</span>"
    )
    return (
        "<html><body style='font-family:-apple-system,Segoe UI,sans-serif;"
        "color:#222;background:#fafaf6;padding:32px'>"
        f"<h2 style='margin:0 0 8px 0;font-size:18px'>AKKI Owner Digest · {payload['week_label']}</h2>"
        f"<p style='color:#666;margin:0 0 18px'>{counts_html}</p>"
        "<table style='border-collapse:collapse;width:100%;background:#fff;"
        "border:1px solid #eee'><tbody>"
        + "".join(rows_html)
        + "</tbody></table>"
        "<p style='color:#888;font-size:12px;margin:18px 0 0'>"
        "Reply to this email to drop a note in your Document Journal — Akki routes "
        "it as a pending document tied to this digest."
        "</p></body></html>"
    )


def reply_alias_for(digest_id: str) -> str:
    """Reply-To alias the FE digest emails out so the inbound webhook
    can recognise replies as digest replies and route to the Journal."""
    inbound_domain = os.environ.get(
        "SENDGRID_INBOUND_DOMAIN", "inbound.akki.syni.ai",
    )
    return f"digest+{digest_id}@{inbound_domain}"


def extract_digest_id_from_alias(alias: str) -> Optional[str]:
    """Parse a `digest+<id>@…` alias and return the digest id. None if
    the alias doesn't match the digest reply shape."""
    if not alias:
        return None
    local = alias.split("@", 1)[0]
    if not local.startswith("digest+"):
        return None
    return local[len("digest+"):] or None


async def deliver_via_sendgrid(
    *, digest_id: str, to_email: str, payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Send the digest email via SendGrid. Returns the provider response.

    Reuses `services.cohort_email._send_via_sendgrid` so we don't open a
    second SendGrid client. The helper already honours the
    `COHORT_TEST_KILL_SENDGRID=1` test kill switch so unit/integration
    runs never actually open a network connection.
    """
    from services.cohort_email import _send_via_sendgrid

    subject = _build_subject(payload)
    plain = _build_plain_body(payload)
    html = _build_html_body(payload)
    reply_to = reply_alias_for(digest_id)
    result = _send_via_sendgrid(
        to_email=to_email,
        subject=subject,
        plain_body=plain,
        html_body=html,
        reply_to=reply_to,
    )
    # Persist delivery status on the digest row.
    set_fields: Dict[str, Any] = {
        "delivery_status": result.get("status"),
        "delivery_provider_id": result.get("provider_id"),
        "delivery_reply_to": reply_to,
        "delivered_at": iso(now()),
    }
    if "reason" in result:
        set_fields["delivery_skip_reason"] = result["reason"]
    await db.owner_digests.update_one(
        {"id": digest_id}, {"$set": set_fields},
    )
    return result
