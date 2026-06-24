# P0.2 Follow-on — Rotation Checklist (PRODUCE ONLY · ROTATE NOTHING)

**Generated:** 2026-06-24 (post-P0 audit close-out, push pending user).
**Source dispatch:** Step 2 of "Post-P0 push verification + Rotation checklist + P1 execution".
**Method:** Cross-referenced `memory/audit/P0_exposure_report.md` (counts + first-doc top-8 field shape from the deleted dumps) AGAINST a live MongoDB inspection of the same collections (top-level key shape only — no values inspected). The dumps themselves have been removed from the working tree by `git filter-repo`'s rewrite; the live DB has the same schema and is the closest faithful proxy for "what was in the dumps".

**Scope discipline:** Counts + field-name presence only. No values inspected anywhere in this checklist.

**Output rule (per dispatch):** Each row below has an explicit verdict on whether the field-shape report confirms presence — overstating exposure is as bad as understating.

---

## P0 — Active session / auth (rotate first)

| # | Item | Where it lives | Field-shape report confirms presence? | Rotation mechanism | Blast radius |
|---|---|---|---|---|---|
| 1 | **User password hashes** | `accounts.password_hash` | **YES** — live `accounts` (31 443 docs) carries `password_hash`. Top-8 field cap in `P0_exposure_report.md` line 15 truncated the column at "h…" alphabetically, but the live schema confirms presence. Dump field shape is identical schema; hashes are present. | Per-account manual reset via admin (`POST /api/admin/accounts/{id}/force_password_reset` if it exists) OR a mass `force_password_reset_required=true` flag with on-next-login enforcement. Implementation choice for the user. | Offline-crack of weak passwords if the hash strength is bcrypt-low-cost. Most consequential single item. |
| 2 | **MFA pending secrets / enrolled secrets** | `accounts.mfa_secret_pending` (and any `accounts.mfa_secret` if present) | **YES** — live schema carries `mfa_secret_pending`, `mfa_enabled`, `mfa_enrolled_at`, `mfa_failed_attempts`. | Per-account MFA reset: clear `mfa_secret_pending`, force re-enrolment; for already-enrolled users, force MFA re-enrolment on next login. Behaviour depends on the existing MFA flow's idempotency. | TOTP token predictability for users whose secrets were dumped — practical effect: an attacker with the secret can generate valid TOTP codes for ~30s each. |
| 3 | **Active sessions / session cookies** | `sessions` collection (currently empty) + JWT bearer issuance state | **NO** — `sessions` collection in live DB shows 0 docs (empty in the dumps too per `P0_exposure_report.md` line 39). JWTs in this codebase are stateless (per `backend/api/auth.py` patterns); no session row dump implication. **However:** the JWT signing secret (`JWT_SECRET` in `.env`) was NOT in any dump (the `.env` is gitignored AND not in `backup/`). | If the deploy uses long-lived JWTs and the operator wants to invalidate all existing tokens, rotate the JWT signing secret + bump the `JWT_ISSUED_BEFORE` low-water-mark (if any). Otherwise, no action required for sessions. | Existing JWTs continue to validate until they expire on their own clock. |
| 4 | **CSRF/double-submit secrets** | Whatever `.env` carries (`CSRF_SECRET` or per-process); NOT in DB dumps | **NO** — no CSRF-named field in any high-value collection. | Rotate the env-side CSRF secret + redeploy if the operator wants to invalidate in-flight tokens. | Negligible — CSRF tokens rotate per session anyway. |

## P1 — Service / vendor credentials (rotate second)

| # | Item | Where it lives | Field-shape report confirms presence? | Rotation mechanism | Blast radius |
|---|---|---|---|---|---|
| 5 | **Per-context inbound webhook tokens** | `accounts.inbound_token`, `contexts.inbound_token` | **YES** — live schema carries `inbound_token` on both `accounts` (31 443 docs) AND `contexts` (23 284 docs). `P0_exposure_report.md` line 27 shows `contexts.inbound_token` in the top-8. | Per-context regeneration — admin endpoint or manual DB op (`db.contexts.update({}, {$set: {inbound_token: <new>}}, multi)`). Whoever calls the inbound webhooks needs the new value. | An attacker with the old token could post forged events into the org's inbox until rotation. |
| 6 | **`auth_events.credentials` field** | `auth_events.credentials` (17 435 docs) | **YES** — live schema confirms field name presence; PRESUMED to be a hash or metadata blob per typical `auth_events` design, NOT the raw credential value. **Field-shape report alone cannot distinguish hash-of-credential from credential-itself — this row needs the user to confirm the field's storage semantics before rotating.** | If the field stores hashes/metadata only (most likely per the `synisense_audit_log.request_hash` pattern in the same codebase), no rotation required — hashes are not secrets. If the field stores raw credentials (unlikely but worth confirming), every authed_via credential needs rotation. | Conditional on storage semantics — likely zero, possibly catastrophic (depends on the field's actual content). **User confirmation needed before action.** |
| 7 | **Emergent LLM key + provider keys (OpenAI, Anthropic, Gemini, etc.)** | `.env` (`EMERGENT_LLM_KEY`, etc.), NOT in DB dumps | **NO** — exposure report shows no provider-key-named field in any collection. `.env` was not part of the `backup/` dumps. | If the operator wants belt-and-braces hygiene, rotate via Profile → Universal Key (Emergent) OR the vendor dashboard (OpenAI / Anthropic / Google). Not required by the exposure. | Negligible by exposure — but a separate hygiene call is the conservative play if there's ever been a leaked-key suspicion outside this audit. |
| 8 | **MongoDB connection string** | `.env` (`MONGO_URL`), NOT in DB dumps | **NO** — env-side, not collection-side. | Rotate the DB password + the `MONGO_URL` env var if the operator wants to invalidate stored connection state. Not required by this exposure. | If the URL was never in a dump, no rotation needed for THIS event. |
| 9 | **Object storage credentials (S3/GCS)** | `.env` (storage credentials), NOT in DB dumps | **NO** — env-side. | N/A for this exposure. | Negligible. |
| 10 | **Stripe / payment-vendor keys** | `.env` (`STRIPE_KEY`, etc.), NOT in DB dumps | **NO** — env-side. | N/A for this exposure. | Negligible. |

## P2 — Informational (presence-uncertain or low-blast-radius)

| # | Item | Where it lives | Field-shape report confirms presence? | Rotation mechanism | Blast radius |
|---|---|---|---|---|---|
| 11 | **User-pasted secrets in chat content** | `chat_messages.content` (5 308 docs in live; 2 482 in latest dump per `P0_exposure_report.md` line 23) | **POSSIBLE BUT NOT CONFIRMED** — `chat_messages.content` is free-form text; users may have pasted API keys, passwords, or PII into chat. Field shape confirms a `content` column exists; whether it contains pasted secrets requires content inspection, which IS NOT performed in this checklist (dispatch rule). | If the operator wants to audit: a regex sweep over `chat_messages.content` for known secret patterns (Stripe `sk_…`, GitHub `ghp_…`, OpenAI `sk-…`, etc.) — but the sweep would itself land secrets in memory of the running script. Operator decides whether the audit is worth the risk. | Range — from zero (no user ever pasted a secret) to high (a single dev pasted a prod API key once). Cannot quantify without content inspection. |
| 12 | **Solva session payloads** | `solva_v2_sessions` (1 481 docs in live; 934 in dump) | **NO direct sensitive field name** — the schema's `account_id`, `cluster_id`, etc., are identifier metadata. Session BODY content (the reasoning text) is not flagged by sensitive-substring heuristic but COULD contain pasted secrets via the same logic as chat_messages. | Same as #11 above — operator decides. | Same range as #11; lower probability than chat. |
| 13 | **Audit chain hashes** | `chat_audit_log.row_hash` / `prev_hash`, `synisense_audit_log.request_hash` / `response_hash` | **YES** — schema confirms these fields. | **NO ROTATION NEEDED.** These are SHA-256 / Blake-style hashes for tamper-evidence — they are NOT secrets; exposing them does not expose any input. Listed for transparency, not for action. | None — hashes are the public-by-design side of the tamper-evident chain. |
| 14 | **`auth_events.authed_via`** | `auth_events.authed_via` (17 435 docs) | **YES** — schema confirms field. Likely a method-name enum (`"password"`, `"google_oauth"`, etc.), NOT a credential. | **NO ROTATION NEEDED.** This is the auth-method label, not the credential itself. | None — method labels are not secrets. |

## Empty collections (no rotation impact)

Live + dump both report 0 docs:
- `auth_log` · `uploads` · `user_consents` · `consent_decisions` · `magic_links` · `sessions` · `user_settings` · `passwords` · `password_resets` · `api_tokens` · `service_keys`

These collections either never existed in this environment OR were purged before the dump dates. No rotation impact.

## `.env` and config files — explicit non-impact

The `backup/` directory contained MongoDB BSON dumps only (per `mongodump` convention: one `.bson` + one `.metadata.json` per collection). It did **not** contain any `.env`, JSON config, JWT signing material, or vendor SDK file. The leak surface is **purely the DB collections listed above**. Env-side credentials are NOT impacted by this specific exposure and do not require rotation as part of this audit — though operators may rotate them for general hygiene.

## Suggested rotation order (for the user — produce only)

If the user chooses to rotate ANYTHING, recommended sequence:

1. **First wave (P0 items above):**
   - #1 password hashes — flag all accounts for forced reset on next login.
   - #2 MFA secrets — force re-enrolment on next login for any user with `mfa_secret_pending` populated.
2. **Second wave (P1):**
   - #5 inbound tokens — regenerate per-context + notify webhook senders.
   - #6 confirm `auth_events.credentials` storage semantics; rotate only if raw values are stored.
3. **Third wave (P2):**
   - #11 (optional) regex sweep over `chat_messages.content` for known secret patterns, if operator deems the risk-vs-effort worthwhile.

## What this checklist deliberately DOES NOT include

- **Rotation execution.** Per dispatch rule, this is a checklist only. Every action is "operator decides".
- **Content inspection.** No `chat_messages.content` body, no `solva_v2_sessions` reasoning text, no `accounts.password_hash` value was read for this report.
- **Recommendations on rotation tooling.** The mechanisms above are described at the schema level. The user knows their admin/ops tooling better than this checklist.

## Cross-reference

- Detailed counts + first-doc field shape: `memory/audit/P0_exposure_report.md`.
- CI lane triage: `memory/audit/P0_ci_log_triage.md`.
- Sprint memo for P0 close-out: `memory/sprints/PHASE_AUDIT_P0.md`.

---

## Verdict: `auth_events.credentials` — **(i) hash/metadata** (actually simpler: source-label list)

**Read date:** 2026-06-24 follow-on dispatch.
**Method:** Code-read only. No DB value of `auth_events.credentials` inspected anywhere.

### Single write-site

Grep found exactly one writer (plus one reader on the admin surface):
```
$ grep -rn "auth_events" backend/ --include="*.py"
  backend/core.py:233            await db.auth_events.insert_one({
  backend/core.py:237                "credentials": credentials,
  backend/routers/admin_auth_events.py:46   rows = await db.auth_events.find(...)
  backend/routers/admin_auth_events.py:65   creds = r.get("credentials") or []
```

### Code path that fills `credentials`

`backend/core.py:95` constructs the candidate list:
```python
95:  candidates: list[tuple[str, str]] = []
96:  auth_header = request.headers.get("Authorization", "")
97:  if auth_header.startswith("Bearer "):
98:      bearer = auth_header[7:].strip()
99:      if bearer:
100:         candidates.append(("bearer", bearer))
101: cookie_token = request.cookies.get("access_token")
102: if cookie_token:
103:     candidates.append(("cookie", cookie_token))
```

Each tuple is `(source_label, raw_jwt_token)`. So far the token IS in the tuple, but it never escapes:

`backend/core.py:187` (success path) and `:204` (failure path) BOTH apply the same comprehension that DROPS the token:
```python
187: creds_seen = [s for s, _ in candidates]
204: credentials=[s for s, _ in candidates],
```

The pattern `[s for s, _ in candidates]` binds:
- `s` → the source label (`"bearer"` or `"cookie"`)
- `_` → the raw token (discarded by convention)

The list passed to `_record_auth_event(..., credentials=...)` therefore contains ONLY label strings. At `core.py:237` that list is inserted into the document verbatim:
```python
233: await db.auth_events.insert_one({
234:     "at": _dt.now(_tz.utc).isoformat(),
235:     "ok": ok,
236:     "reason": reason,
237:     "credentials": credentials,    # ← list of strings: "bearer"/"cookie"
238:     "authed_via": authed_via,
...
```

### Possible domain of values

`auth_events.credentials` can only ever be one of:
- `[]` — no credentials provided (the `no_credentials` 401 branch at `core.py:106`).
- `["bearer"]` — Authorization header only.
- `["cookie"]` — access_token cookie only.
- `["bearer", "cookie"]` — both submitted (the dual-credential branch that the `dual_mismatch` flag tracks).

**No JWT, no token, no password, no secret ever lands in `auth_events.credentials` per this write-site.**

### Verdict

**(i) hash/metadata.** The field stores a list of source labels (`"bearer"` / `"cookie"`) ONLY. This is even safer than a hash — there is no underlying token recoverable from the stored value because the token was never persisted in the first place; the comprehension `[s for s, _ in candidates]` discards it at the FE of `_record_auth_event` before any I/O.

**No code bug.** The write-site is correct by design — the `_` in the comprehension is the deliberate discard of the token half of each `(label, token)` tuple.

**Rotation impact:** None on this field. Folds into the existing P0 wave's forced password reset (item #1 above). `auth_events.credentials` itself can stay as-is — it does not contribute to the exposure surface.

### Confirmation that no other write-site exists

```
$ grep -rn '"credentials"' backend/ --include="*.py"
  backend/core.py:237            "credentials": credentials,
  backend/routers/admin_auth_events.py:65        creds = r.get("credentials") or []   # READ side
```

The admin router only READS `credentials` to render the admin UI (`admin_auth_events.py:65`). There is no `update_one` / `update_many` / `findAndModify` against `auth_events` anywhere in the tree. Single write-site; verdict is unambiguous.
