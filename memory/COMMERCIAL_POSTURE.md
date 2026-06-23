# Commercial Posture

> Phase 5 — Sell-Ready snapshot. **No dollar figures committed.** Every numeric is a placeholder marked `<…>` for sales/finance to fill in once pricing tiers are agreed.

## Standalone product readiness matrix

| Product | Standalone-sellable today? | What's ready | What's gated |
|---|---|---|---|
| **SyniSense** | **Conditional** | Shield pipeline + Trust Center + Signals API + observability + 30 typed contract methods + `/v1/synisense/*` SDK surface | Standalone deployment depends on platform supervisor unlock (see PHASE_4_3_TOPOLOGY.md §1 deviation). Currently sold as a guardrail component of Akki. |
| **Solva** | **Conditional** | Solva v2 briefing run + workbook analysis + chunked artefact rendering + admin telemetry + `/v1/solva/*` SDK surface | Auth currently piggy-backs Akki's identity layer. A standalone Solva sale would need either its own auth or an integration where the customer's identity layer brokers. |
| **Akki** | **Yes** | The complete SaaS product as it stands today: identity, multi-tenancy, chat, documents, decks, Pulse, Monitor, Portfolio, Studio, Sandbox, inbox routing, shares, committees, cycles, admin, billing primitives | First paying customer triggers live Stripe productionisation + GCP OAuth credentials (gated externally). |

## Bundle paths

| Bundle | Sells | Strategy |
|---|---|---|
| **Akki Solo** | Akki as a one-product SaaS; SyniSense Shield is a transparent server-side guardrail; Trust Center + Signals API NOT surfaced | Smallest, simplest. Fastest time-to-revenue. Target: operator-led SMB. |
| **Akki + SyniSense** | Akki + full Trust Center UI + Signals API as a sellable line item | Adds the governance product. Target: regulated SMB with compliance officer. |
| **Akki + Solva** | Akki + Solva Workbench + multi-document analyses | Adds the reasoning product. Target: SMB with chief-of-staff or analyst. |
| **Full Triad** | All three products at full surface | Current full-product offering. Target: regulated SMB needing governance + reasoning + orchestration. |

## SLA dimensions worth pricing on

Per-product SLA dimensions that warrant a price tier (placeholders only — no dollar figures committed):

### SyniSense

| Dimension | Why it matters | Tier hint |
|---|---|---|
| Shield round-trip p50 / p95 latency | Determines apparent chat / brief responsiveness | < `<N>` ms p95 |
| Trust-receipt durability + availability SLA | Auditability is the value prop | `<N>` nines |
| Audit-log retention window | Compliance requirement | `<N>` years |
| Trust Center read latency | Drilldown UX velocity | < `<N>` s |

### Solva

| Dimension | Why it matters | Tier hint |
|---|---|---|
| Briefing render p50 / p95 | The most-asked-about SLA dimension | < `<N>` s p95 |
| Citation-stability score over reruns | Confidence in deterministic output | ≥ `<N>` % stability |
| Max concurrent analyses per tenant | Capacity guarantee | `<N>` concurrent |
| Multi-document analysis size cap | Per-analysis upper bound | `<N>` documents or `<N>` MB |

### Akki

| Dimension | Why it matters | Tier hint |
|---|---|---|
| Pulse signal freshness lag | Time from event to surface | < `<N>` s |
| Document extraction p95 | First-impression UX | < `<N>` s |
| Chat turn latency p50 | Conversational responsiveness | < `<N>` s |
| Uptime SLA | Standard SaaS dimension | `<N>` nines |
| Per-tenant LLM token budget | Cost-control / commercial gate | `<N>` tokens / month |

## Sale separability checklist

Before a single context can be sold to a customer without dragging the other two:

| Check | Status |
|---|---|
| Context is an independently runnable FastAPI app | ✅ Phase 4.3 (`<ctx>_app:app` standalone import verified) |
| Cross-context calls go through typed contracts only | ✅ Phase 4.3 (0 violations / 0 annotations in `4_3_enforce_mode`) |
| HTTP transport substrate works between processes | ✅ Phase 4.2 (8/8 smoke tests pass under `BOUNDED_CONTEXT_TRANSPORT=http`) |
| Healthcheck triad live + composite proxy | ✅ Phase 4.3 |
| Versioned `/v1/{context}/*` SDK surface published | ✅ Phase 4.4 (619 paths, sha `acc51822aa8818ae`) |
| Per-context Dockerfile + compose + K8s manifests | ✅ Phase 5 Part C (`/app/backend/deploy/`) |
| Per-context OpenAPI SDK slice | ✅ Phase 5 Part B (`/app/backend/openapi-sdk/`) |
| TypeScript SDK build pipeline | ✅ Phase 5 Part E (`/app/sdk/`) |
| Cron supervisor split | ✅ Phase 5 Part D (each `<ctx>_app.py` arms its own crons when standalone) |
| Partner onboarding doc | ✅ Phase 5 Part F (`/app/memory/PARTNER_ONBOARDING.md`) |
| **Platform supervisor unlock** (multi-process activation) | ❌ External blocker |
| **Live Stripe productionisation** | ❌ Gated on first paying customer |
| Per-product brand / signed terms / DPA | ❌ Out-of-scope (sales/legal pre-requisite) |

Engineering is **ready for the platform unlock day**. The 3 ❌ items above are not engineering-resolvable.

## Pricing posture (intent, not numbers)

| Approach | Pros | Cons |
|---|---|---|
| Flat per-seat | Predictable, easy to negotiate | Doesn't capture LLM cost asymmetry |
| Per-seat + LLM cost passthrough | Tracks real consumption | Adds a billing surface to build |
| Tiered by signal volume / brief count / chat turns | Aligns with SLA dimensions | Requires usage telemetry maturity (we have it for chat + brief; partial for signals) |
| Hybrid: floor + usage caps | Best operator UX | Most complex to communicate at sale time |

Strategy intent (sales-led, not engineering-prescribed):
- **Akki Solo** → flat per-seat with a generous chat / document quota
- **Akki + SyniSense** → flat per-seat + audit-retention tier upgrade
- **Akki + Solva** → flat per-seat + briefing render quota tier
- **Full Triad** → flat per-seat with all of the above bundled

## Next decisions for sales/finance

1. Lock dollar floors per tier and quotas per dimension above.
2. Pick the rate-limit numbers in `/app/memory/PARTNER_ONBOARDING.md` "Rate limits posture".
3. Decide whether SyniSense and Solva are sold under the AKKI brand or separately. The engineering surface supports either.
4. Decide whether the SDK is public (npm-published) or partner-only (gated download). The build pipeline is the same; only distribution changes.

## What changes when the supervisor unlocks

Engineering work after the supervisor unlock day:

1. Build + push the three Dockerfiles to your registry.
2. Apply the K8s manifests in `/app/backend/deploy/k8s/`.
3. Set the per-context `INTERNAL_TRANSPORT_BASE_URL_*` env vars on each pod.
4. Verify `/api/healthz/composite` returns `{"status":"ok"}` for each independent process.
5. Cut the public DNS to the akki Service.
6. Decommission the bundled `server.py` process.

**Nothing in the application code needs to change.** The Phase 4 + Phase 5 work was designed for this cutover to be mechanical.
