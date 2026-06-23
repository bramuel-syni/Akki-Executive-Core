# Partner Onboarding

> Phase 5 — Sell-Ready snapshot.

Welcome. This document is your one-page reference for integrating with AKKI's three bounded products: **SyniSense**, **Solva**, and **Akki**.

## What you can buy

| Product | What it does | Persona |
|---|---|---|
| **SyniSense** | Data-governance / PII pipeline. Trust Center forensic surface. Signals API for typed intelligence events. | Governance / compliance lead at a regulated SMB |
| **Solva** | Reasoning-governance. Multi-document analyzer. Citation-pinned briefings + admin telemetry. | Analyst / chief-of-staff |
| **Akki** | Orchestrator + identity + product surfaces (Chat, Pulse, Documents, Decks, Studio, Sandbox, ...). | Operator + executive + analyst |

See `/app/memory/PRODUCT_FEATURE_REVIEW.md` for the full feature matrix and current maturity per product.

## SDK location

| Layer | Location |
|---|---|
| Versioned OpenAPI slices (canonical schema) | `/app/backend/openapi-sdk/{synisense,solva,akki}.openapi.json` |
| Local TypeScript SDK (generated) | `/app/sdk/{synisense,solva,akki}/` |
| SDK regeneration | `python backend/scripts/build_sdk.py` |

The TypeScript SDK ships as a single `index.ts` per context with:
- type definitions for every schema in the slice
- one async method per operation
- a `Client` class wrapping `fetch()` with auth headers

For production-grade SDK generation in other languages (Python, Go, Java, etc.), use the OpenAPI slice files with [`openapi-generator-cli`](https://github.com/OpenAPITools/openapi-generator) or your tooling of choice.

## Versioning policy

| Path prefix | Status | Use this when... |
|---|---|---|
| `/v1/{context}/*` | **Stable** versioned SDK surface. Per-context major bumps. No sunset planned. | You're integrating new code |
| `/api/*` | **Legacy-stable.** Same handlers as `/v1/*`. No deprecation window without ≥ 12 months notice + `Deprecation:` HTTP headers. | You're integrating against an existing internal app |

Full policy: `/app/memory/API_VERSIONING.md`.

## Auth model

| Surface | Auth |
|---|---|
| Public routes (`/v1/akki/blog/posts`, healthchecks, etc.) | None |
| User routes | Bearer token (JWT) in `Authorization: Bearer <token>` |
| Admin routes | Bearer token + admin role on `account` |
| Tenancy-scoped routes | Bearer token + context membership on `context_id` |
| Cross-context internal transport | NOT for partners — `/api/internal/v1/*` is HMAC-signed and excluded from `/v1/*`. |

Token acquisition:
- **Email/password:** `POST /v1/akki/auth/login` → `{access_token}`
- **Magic link:** `POST /v1/akki/auth/magic/request` → email + `/v1/akki/auth/magic/consume`
- **Google OAuth:** gated on customer-supplied GCP creds (see PRODUCT_FEATURE_REVIEW §7)

## Rate limits posture

This is a placeholder; concrete limits will be published per pricing tier once `/app/memory/COMMERCIAL_POSTURE.md` matures past placeholder state. As an integrator today, expect:

- Soft per-token rate limit on chat / briefing render endpoints (LLM-cost gated)
- No public rate limit on read-only endpoints
- Burst-friendly behaviour on signal reads (Pulse / Monitor)
- Document upload size cap configured per tenant

## What is NOT public

These surfaces are part of the platform's internal cohesion but NOT for partner consumption:

- `/api/internal/v1/*` — cross-context HMAC-signed transport
- `/api/healthz/*` — operational liveness probes
- The `Akki Universal LLM key` plumbing — managed internally; the SDK doesn't expose it

## Support

For Phase 5 onboarding (engineering pre-sales):
- Reference doc: `/app/memory/PRODUCT_FEATURE_REVIEW.md`
- Commercial posture: `/app/memory/COMMERCIAL_POSTURE.md`
- API versioning: `/app/memory/API_VERSIONING.md`
- Slack / channel: _placeholder — to be assigned per deal_
- Escalation: _placeholder — to be assigned per deal_

## Quickstart

```ts
import { SynisenseClient } from '@akki/synisense-sdk';

const syni = new SynisenseClient({
  baseUrl: 'https://api.example.com',
  authToken: process.env.AKKI_TOKEN,
});

// Pull recent trust-center activity for your account.
const activity = await syni.getV1SynisenseTrustCenterActivity();

// List signals (typed event feed) for a context.
const signals = await syni.getV1SynisenseV1EngineSignalTypes();
```

The auto-generated method names mirror the path + method. Use `index.ts` as the source of truth — it lists every reachable operation.

## Buy-vs-build hint

Partner integrations have three patterns we've seen so far:

1. **SyniSense as a guardrail.** You operate your own LLM platform; you call SyniSense Shield as a deidentify→reidentify wrapper. Pure backend-to-backend integration; no Akki UX surfaced to your users.
2. **Solva as an analyst.** You feed Solva your documents + question, render a citation-pinned briefing, surface the brief in your own product.
3. **Full triad embedded.** Your team uses Akki as the daily-driver SaaS; SyniSense + Solva are the underlying capabilities your operators get for free.

Pick the smallest pattern that solves your problem. Upgrades between patterns are additive (no breaking auth / schema migrations).
