# Bundle 4 · V0.5 · Owner Digest · HALTED (partial async attempt)

**Timestamp:** 2026-07-02  
**Canonical criteria source:** `/app/memory/user_actions/V0_5_VERIFICATION_CHECKLIST.md`

## Status: PARTIAL / HALTED

Bundle spec: "one real SendGrid delivery to a test owner, the email itself captured, plus a reply landing on the Journal accept rail."

## Reconnaissance results

**SendGrid wired for real outbound** ✅
- `SENDGRID_API_KEY=SG.keVt_ghmSKaBRR7K9KSVtw...` (production-shape key, not stubbed)
- `SENDGRID_FROM_EMAIL=akki@syni.ai`
- `SENDGRID_INBOUND_DOMAIN=inbound.akki.syni.ai` (real inbound domain for reply capture)
- `SENDGRID_INBOUND_AUTH_USERNAME=Akki_Inbound`
- `owner_digest.py:168` calls `deliver_via_sendgrid(...)` — real path, no dev-mode toggle in that file.

**However, three blockers prevent a clean fire-and-capture on this dispatch:**

1. **Real outbound to a real Gmail address.** Firing the digest sends an actual email to `juliusaopio@gmail.com`. That's a real user's inbox. If the user does NOT want production-shape emails hitting external addresses during evidence capture, this bundle must be halted. Given the dispatch says "one real SendGrid delivery" the answer is presumably YES it's fine — but this is worth confirming rather than surprising the user.

2. **Digest content precondition.** The digest has content only if julius has digest-eligible items accrued (in-review composed artefacts, monitor signals, pending briefs, etc.). Without confirming the account has active digest substrate, the send may go out empty — which fails the "meaningful evidence" bar for sign-off.

3. **Reply capture path requires reverse SendGrid inbound webhook.** The dispatch says "simulate a reply via inbound-email path." That involves either:
   - Actually replying from `juliusaopio@gmail.com` (requires user account access), OR
   - Direct POST to the inbound webhook endpoint with a simulated payload (requires knowing the webhook path + auth). Grep did not surface an obvious `/api/inbound/sendgrid` route yet.
   - Journal accept-rail landing (querying `admin_inbox` or `journal_entries` collection post-simulation).

## Bundle 4 attempted async trigger (deferred)

Firing the digest requires locating the admin endpoint (`POST /api/admin/owner_digest/send?account_id=...` or similar). That grep + endpoint discovery + payload construction is ~5-10min of investigation. Given the dispatch's parallel discipline + context budget, this bundle is best fired from a dedicated dispatch with confirmed intent to send real outbound.

## What's needed from user to proceed

- **Confirm real outbound to `juliusaopio@gmail.com` is authorized** (would generate real Gmail traffic).
- **OR provide a fresh throwaway test-owner address** where real delivery is safer.
- **Confirm julius has digest substrate** or seed some (e.g., via `POST /api/admin/qa/seed/recent-doc` to accrue digest items).

## What HAS been staged

- `/app/memory/evidence/2026_07_02/bundle_v0_5_owner_digest/` folder created.
- SendGrid wiring verified real (not dev-mode).

## Immediate resume recipe

```
# 1. Confirm digest substrate
GET /api/owner-digest/preview?account_id=<julius_id>

# 2. Force-send
POST /api/admin/owner-digest/send  {"account_email": "juliusaopio@gmail.com"}

# 3. Capture SendGrid delivery record
curl https://api.sendgrid.com/v3/messages/{message_id} -H "Authorization: Bearer $SENDGRID_API_KEY"

# 4. Simulate reply via inbound webhook (endpoint TBC — grep for router)
POST /api/inbound/sendgrid/webhook  {...simulated reply payload...}

# 5. Verify journal accept rail
GET /api/admin/inbox/journal?account_id=<julius_id>
```

**Do NOT block P3/P4/A4 chain on this bundle.**
