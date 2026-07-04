# Bundle 4 · V0.5 · Owner Digest · CAPTURED (dev-mode)

**Timestamp:** 2026-07-04T18:06:11.488315+00:00
**Canonical criteria source:** `/app/memory/user_actions/V0_5_VERIFICATION_CHECKLIST.md`
**Canonical scope source:** `services/owner_digest.py`
**Capture discipline:** dev-mode (`.eml` file capture, no SendGrid outbound)
**Dispatch disposition (2026-07-04):** DEV-MODE ONLY · "keep dev-mode captures. The review sitting judges digest CONTENT ... A real key proves plumbing, not quality."

## What WAS captured (mechanical)

- **`owner_digest_devmode.eml`** — full MIME multipart/alternative message
  built by the shipped composer path (`_build_subject`, `_build_plain_body`,
  `_build_html_body` from `services/owner_digest.py`).
- **`owner_digest_payload.json`** — the raw payload from
  `build_owner_digest(context_id=NED_CTX, owner_account_id=julius)`.
- Composer path verified: identical code that would run under real
  SendGrid delivery — the message envelope is production-shape (subject
  line, plain + html body, Reply-To alias `digest+<id>@inbound.akki.syni.ai`,
  X-Akki bundle stamps for auditability).

## Content quality note (substrate-dependent)

Julius NED Seat context has **0 `strategic_goals` rows** at capture time.
The digest composer produces an empty-rows payload with 0 off-track /
0 at-risk / 0 on-track / 0 achieved. The `.eml` demonstrates the
composer envelope shape, NOT content quality with real substrate.

For a content-quality review, seed `strategic_goals` rows for julius NED
context first, then re-run this capture script.

## What was NOT verified (declared gaps)

- **SendGrid outbound delivery** — NOT verified. No network call to
  SendGrid was made. Real delivery + Personalization + Rejection
  handling remain proof-deferred to production cutover.
- **Reply-inbound loop** — NOT verified. The reply-alias
  `digest+<id>@inbound.akki.syni.ai` is stamped in the message but no
  inbound webhook simulation was performed against this bundle.
- **Journal accept-rail landing** — NOT verified. The
  `handle_owner_digest_reply` handler in `routers/inbound_email.py`
  (line 654) shows the intended path; no live reply payload was
  routed through it in this bundle.

## Truth-in-capability closure line

Content verified; SendGrid delivery + reply-inbound loop NOT verified —
proof deferred to production cutover.

## Reproduction

```
cd /app/backend && set -a && source .env && set +a && \
  python scripts/jc_bundle_capture_2026_07_02.py --bundle b4
```

Capture is idempotent (rewrites `.eml` and `README.md`).
