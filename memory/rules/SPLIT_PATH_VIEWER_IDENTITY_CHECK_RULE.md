# RULE-SPLIT-PATH-VIEWER-IDENTITY-CHECK

**Status:** Permanent · Effective 2026-07-08 · Banked from user dispatch introducing `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1`.

## Rule

Any "resolve / expose / share" fix (any code path that decides what a viewer can see, based on their identity or credential) MUST be checked with a SPLIT-PATH (viewer-identity-based) discriminator BEFORE it ships. A render fix is NEVER applied to a single code path that both tenant AND external views inherit — because those views have different governance requirements and different sanitization rules.

**The two canonical viewer identities:**

| Identity | Description | Governance |
|---|---|---|
| **Tenant viewer** | Authenticated user of the tenant that owns the entity | Full-fidelity view · all internal fields · all actions |
| **External viewer** | Unauthenticated or foreign-tenant user reaching via a share link | Sanitized view · internal fields redacted · restricted actions |

## Rule applied

- **A single-path fix is banned.** If a bug is fixed by "just show the field," but that fix ships on a code path that both identities use, the sanitized view now leaks that field to externals. Fix must be gated on `viewer_identity ∈ {tenant, external}` explicitly.
- **A cross-path regression is required in every proving slice** for any resolve/expose/share fix. The slice MUST assert:
  1. Tenant viewer sees the expected full-fidelity view.
  2. External viewer sees the expected sanitized view.
  3. External viewer does NOT see any field that internal-only sanitization should have redacted.
- **The auth discriminator must be an explicit function argument or middleware output** — never inferred from URL alone or from `Referer` header. A share-token-based external must produce a `viewer_identity="external"` label that the render layer honors.

## Reference precedents

- **Stage 4 of `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-*`** (Issue 11) — the resolve/expose/share fix for Briefs must be gated on the tenant-vs-external discriminator introduced in Stage 3 (which is why Stage 3 precedes Stage 4 · Stage 4 reuses Stage 3's discriminator).
- Prior Deck arc: the deck-share and deck-download paths were separated for this reason (a shared deck download must not carry internal metadata like `draft_notes` even if the tenant download shows them).

## Proving-slice pattern

```
Rn · Split-path viewer identity discriminator present at expose site
     · grep the expose/share/resolve function; assert it branches on `viewer_identity`
     · No single-path expose function (banned pattern)

Rn+1 · Tenant viewer sees full-fidelity view
     · assert all expected fields present

Rn+2 · External viewer sees sanitized view
     · assert restricted fields absent
     · assert no fields leaked that internal-sanitization should have redacted
```

## Precedence with related rules

- `BORN_IN_CORRECT_LIFECYCLE_STATE_RULE.md` — initial state must be correct on both viewer paths; the entity is born once, but rendered many times through split viewer identities.
- `USER_QA_RE_RUN_IS_FINAL_GATE_RULE.md` — split-path leak is invisible to structural tests; user QA re-run is the final gate.
- `WRONG_BOARD_REJECTION_RULE.md` — a fix that ships as "expose-any" on a shared code path is a wrong-board close claim.

## Applicability

- Applies to Stage 4 of the current `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-*` arc (Issue 11 · resolve/expose/share fix).
- Applies to ANY future resolve/expose/share fix in ANY feature (Deck, Draft, Brief, Signal, Solva Frame, Chat, or new features).

## Origin

Banked in the user dispatch of 2026-07-08 introducing `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1`. Explicit acknowledgment of the pattern that surface any "just fix the render" resolution — without a viewer-identity split — invariably leaks tenant-internal data to externals when the same render code serves both identities.
