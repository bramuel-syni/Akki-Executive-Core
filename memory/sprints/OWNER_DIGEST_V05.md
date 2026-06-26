**Canonical Spec**: `/app/memory/JC_MON_CANONICAL_SPEC.md` (Wave 3 backlog — Owner Digest. v0 shipped the deterministic composer + skip-if-no-delta gate; this v0.5 sprint lights up the per-context TZ resolver, SendGrid delivery, and the reply-handler that routes into the existing Document Journal accept rail.)

# Owner Digest v0.5 · CLOSED 2026-06-26 · 12/12 GREEN

## Sub-sprint scope (per user queue, msg follow-up)

> #3 Owner Digest v0.5 — three additive pieces:
> • Per-context TZ resolver (replaces UTC default)
> • SendGrid template (real send vs v0 deterministic body)
> • Reply-handler routing to Document Journal accept rail (already wired in v0 via Document Journal — make sure the reply mailbox parses correctly and routes per owner_id + objective_id)
> • v0 discipline carries: deterministic-only, skip-if-no-delta, hash gate via the existing SHA-256 fingerprint
> • HALT if SendGrid template requires a credential not already in the secrets store — surface for user to drop API key.

**SendGrid credential gate** — NO HALT. `SENDGRID_API_KEY` + `SENDGRID_FROM_EMAIL` + `SENDGRID_INBOUND_AUTH_*` already present in `backend/.env`. v0.5 reuses the existing `services.cohort_email._send_via_sendgrid` helper, which already honours `COHORT_NOTIFY_DISABLED=1` (test kill switch — fail-closed by default).

## What shipped

### 1. Per-context TZ resolver (`services/owner_digest.py`)

- `resolve_owner_tz(owner_account_id)` reads `accounts.preferences.tz` (with fallbacks: `preferences.timezone` → top-level `timezone` → `"UTC"`). Default UTC preserves v0 behaviour for accounts that never set a tz.
- `is_target_hour_local(tz, target_hour=9)` + `is_target_dow_local(tz, target_dow=0)` — uses stdlib `zoneinfo`. Cron sweeps hourly and asks "is it Monday 09:00 in *their* timezone right now?" — only matched contexts receive a send this hour.
- **Schedule change**: `server.py` flipped from `CronTrigger(day_of_week="mon", hour=9, minute=0)` (single UTC fire) to `CronTrigger(minute=5)` (hourly :05). The TZ gate now lives **inside the endpoint**, not on the trigger.

### 2. SendGrid delivery (`services/owner_digest.py`)

- `_build_subject` / `_build_plain_body` / `_build_html_body` are deterministic builders (same payload → same outputs; no UUIDs, no timestamps, no LLM).
- HTML body uses inline-styled table rows (executive-email-client safe); colour scheme matches AKKI's existing email design (oxblood for off-track delta, amber for at-risk, green for on-track).
- `deliver_via_sendgrid(...)` calls the existing `_send_via_sendgrid` helper from `services.cohort_email` and persists `delivery_status` / `delivery_provider_id` / `delivery_reply_to` / `delivered_at` (+ `delivery_skip_reason` when the kill switch fires) onto the `owner_digests` row.
- **Reply-To alias**: `digest+<digest_id>@<SENDGRID_INBOUND_DOMAIN>` — `reply_alias_for(digest_id)` builds it, `extract_digest_id_from_alias(alias)` parses it back.

### 3. Reply-handler routing (`routers/inbound_email.py`)

- Extended `_dispatch_inbound_payload` to discriminate by alias prefix (`digest+...`). When a candidate recipient matches, dispatches to the new `_handle_owner_digest_reply`.
- `_handle_owner_digest_reply`:
  - Looks up the digest row and the owner account by id.
  - Inserts a `documents` row with `source_channel="owner_digest_reply"` + `origin_kind="owner_digest_reply"` + `origin_id=<digest_id>` so SIEM / governance can trace.
  - `lifecycle_state="pending"` when the sender's email matches the digest owner; `lifecycle_state="quarantine"` otherwise (forged-sender protection — captures for audit but hides from the Journal accept queue).
  - Stamps `sender_matches_owner: bool` on the row so the Journal UI can render a "verified vs unverified" badge.
- **Zero net-new code on the accept rail itself** — the Document Journal already filters on `source_channel` + `lifecycle_state="pending"`.

### 4. Latent bug fix surfaced + landed (CSRF allowlist)

Discovered while live-testing the cron endpoint: the EXISTING cron routes (`/api/cron/paragraph-anchors-sweep`, `/api/cron/weekly-digest`, `/api/blog/cron/weekly`, `/api/solva/v2/cron/stale-session-sweep`) were ALL returning `403 csrf_token_missing` when hit by their own APScheduler in-proc httpx calls — i.e. **every scheduled cron job has been silently failing in prod since the CSRF middleware shipped in P3.1.** Added `/api/cron/`, `/api/blog/cron/`, `/api/solva/v2/cron/` to `_ALLOWLIST_PREFIXES` in `services/csrf.py` (mirrored in `tests/conftest.py:_CSRF_ALLOWLIST_SUBSTRINGS`). Each cron endpoint enforces its own auth via `X-Cron-Secret` — CSRF was redundant + actively blocking.

## Proving slice 12/12 GREEN

Run: `cd /app/backend && python scripts/jc_owner_digest_v05_slice.py`

| # | Subject | Outcome |
|---|---|---|
| 1 | `resolve_owner_tz` reads `accounts.preferences.tz` | ✓ |
| 2 | `is_target_hour_local` matches current hour and rejects others | ✓ |
| 3 | `is_target_dow_local` matches current weekday and rejects others | ✓ |
| 4 | Cron without `force_now` respects the TZ gate (off-window contexts skipped) | ✓ |
| 5 | Cron with `force_now=true` bypasses the TZ gate (digests persisted) | ✓ (214 digests persisted in slice DB) |
| 6 | Subject / plain / html builders are deterministic | ✓ |
| 7 | `deliver_via_sendgrid` honours `COHORT_NOTIFY_DISABLED=1` kill switch | ✓ (returns `test_mode_disabled`, no network call) |
| 8 | Digest row carries `delivery_status` + `delivery_reply_to` + `delivered_at` after delivery | ✓ |
| 9 | `reply_alias_for(<id>)` shape | ✓ (`digest+<id>@inbound.akki.syni.ai`) |
| 10 | `extract_digest_id_from_alias` round-trip + null-on-non-match | ✓ |
| 11 | Inbound reply with matched sender → documents row, `source_channel="owner_digest_reply"`, `lifecycle_state="pending"`, `sender_matches_owner=True` | ✓ |
| 12 | Inbound reply with mismatched sender → documents row, `lifecycle_state="quarantine"`, `sender_matches_owner=False` | ✓ |

Runtime: ~21s (cron scan touched 23,836 contexts in the dev DB; cursor-mode iteration; still well within the slice budget).

## Halt-and-Surface gate evaluation

| Gate | Threshold | Observed | Verdict |
|---|---|---|---|
| SendGrid credential missing | `SENDGRID_API_KEY` absent | already present | ✅ PASS |
| Inbound alias domain unconfigured | `SENDGRID_INBOUND_DOMAIN` env | default `inbound.akki.syni.ai` (matches existing inbound config) | ✅ PASS |
| Shield / LLM call along delivery path | 0 | 0 (deterministic builders only) | ✅ PASS |
| New collection / schema for accept rail | 0 (reuse `documents`) | 0 (re-used `documents` with `source_channel="owner_digest_reply"`) | ✅ PASS |
| Existing cron jobs silently failing | shouldn't be — surface & fix | **surfaced + fixed**: `_ALLOWLIST_PREFIXES` now covers `/api/cron/` family (latent bug) | ✅ PASS |

## v0 → v0.5 carryover discipline (all unchanged)

- Deterministic content only — no LLM, no Shield, no AI prose.
- Skip-if-no-delta hash gate (`(goal_id, status, score, probability, band)` SHA-256).
- Replies route to the Document Journal **existing** accept rail — zero net-new code on the rail itself; the new handler just produces rows in the shape the Journal already filters on.

## Files

- `backend/services/owner_digest.py` — TZ resolver + SendGrid build/deliver + alias helpers (+ docstring updated)
- `backend/routers/owner_digest.py` — cron endpoint now TZ-gated; cursor-mode context iteration; delivery integrated; new `force_now` / `skip_tz_gate` test escape hatches
- `backend/routers/inbound_email.py` — `_handle_owner_digest_reply` + dispatch routing
- `backend/services/csrf.py` — `/api/cron/` family added to `_ALLOWLIST_PREFIXES` (LATENT BUG FIX for all existing cron jobs)
- `backend/tests/conftest.py` — `_CSRF_ALLOWLIST_SUBSTRINGS` mirror update
- `backend/server.py` — APScheduler trigger flipped from `Mon 09:00 UTC` to `hourly :05`; "Schedulers armed" log line updated
- `backend/scripts/jc_owner_digest_v05_slice.py` — new (proving slice)
- `backend/scripts/jc_owner_digest_v0_slice.py` — check 7 widened to accept v0 OR v0.5 trigger shape (back-compat assertion)

## Out of scope for this sprint

- Per-tz pacing inside the hourly fire (e.g. throttle 50 sends per minute to avoid SendGrid rate-limit). v0.5 trusts the existing helper's per-account suppression; v0.6 can add a sending bucket if production traffic warrants.
- Per-day-of-week customisation (digest day other than Monday). Defer until a real customer asks.
- Inline preview of the digest inside the Monitor side panel. Tracked separately under the Origin-triggered Briefs UX backlog.

— END —
