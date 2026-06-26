# AUTONOMOUS BACKLOG RUN — Wave 1 close · 2026-06-26

**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (parent
JC-WS lock).

This is the Wave 1 handoff per the AUTONOMOUS BACKLOG RUN contract
locked in the user message dated 2026-06-26. Phase 3 GridFS
migration was the gating event; it closed 11/11 GREEN before this
wave started.

## Wave 1 outcomes

| Item | Status | Detail |
|---|---|---|
| 1. `services/solva_v2/` directory rename | 🛑 HALT-AND-SURFACE | 66 import sites + 57 files. Track-2 schema files (`artefact_schema.py`, `pptx_exporter.py`) live INSIDE this directory — per autonomy contract, locked-area collision (**Track-2 schema**) → HALT. |
| 2. `solva_phase_d_sessions` Mongo collection rename | 🛑 HALT-AND-SURFACE | 22 files × 50 references. This is the Solva v2 session storage including Track-2 sessions just shipped at 73280/69105 bytes. Same locked-area collision as item 1 — HALT. |
| 3. News aggregator UA rotation | ✅ DONE | Implemented Safari-shaped UA fallback in `services/news_aggregator.py::fetch_one`. nation-africa **still 403 after rotation** (verified via fresh log line). Per contract conditional drop: `nation-africa.enabled = false` in `data/news_sources.json`. News sweep now runs 14 sources cleanly (down from 15, no 403 warnings). |
| 4. INVARIANT_HEALTH.md scaffold | ✅ DONE | `/app/memory/INVARIANT_HEALTH.md` written — single-pane-of-glass dashboard mirroring DEV_PIPELINE §4 plus `last verified` + `verification command` + `current value`. 30 invariant rows across code-layer, contract/schema, test-hygiene, repo/CI hygiene, and feature-guard sections. 3 known 🟡 pre-existing-drift rows surfaced for triage. |
| 5. Phase 5.5.3 broader-suite drift triage | ✅ DONE (investigative) | `/app/memory/sprints/PHASE_5_5_3_BROADER_DRIFT_TRIAGE.md` written. Headline: **101 files, 202 fails, 11 errors** (the "~7+" prediction undercounted by ~14×). Dominant failure mode: `httpx.HTTPStatusError: HTTP 500 at /app/backend/contracts/_adapters/_http_client.py:286` — single root cause hitting many tests. Three working hypotheses identified (CSRF auth-rig drift ≈ 40-50 %, tenancy seed-data drift ≈ 15-20 %, Track A/B contract re-pin ≈ 15-20 %). Proposed Phase 5.6.1 → 5.7 remediation sequence. NO code changes shipped from this dispatch. |

## Plus — immediate post-Phase-3 action (priority 0)

**Track-2 divergent first-render download URL** is live:

```
GET https://akki-executive.preview.emergentagent.com/api/jc-artifacts/track2/divergent-first-render.pptx
```

- Auth required (superadmin only — `is_superadmin` gate).
- Verified: 401 unauthenticated; 200 + **69 105 bytes** (matches source) with admin JWT.
- Implemented at `backend/routers/jc_artifacts.py` (new); whitelist
  pattern so adding the next artefact is a one-line registration.
- Surface ratchet rolled forward: `/api/* = e0e4e1a48a57cef9` ·
  `/v1/* = a2c20282a273d240` · combined `1cee028104e93e99`. Path
  count 631/629. 43/43 contract-snapshot + dual-mount-smoke tests
  GREEN.

The convergent regression deck (73 280 bytes) is also exposed at
`/api/jc-artifacts/track2/convergent-regression.pptx` for side-by-side
review.

## Plus — production runbook written

`/app/memory/runbooks/PROD_INGRESS_AND_MEMORY.md` — 3-command
kubectl runbook covering the K8s ingress annotations + pod memory
bump that gate the BUG-ANL-UPLOAD-GRIDFS deployment. Includes
verification commands, rollback steps, and "what happens if not
applied" guidance (dual-read keeps reads working forever).

## Files touched (Wave 1)

| File | Change | Notes |
|---|---|---|
| `backend/services/news_aggregator.py` | UA rotation on 403 + `_BROWSER_FALLBACK_UA` module-const | News fetch path |
| `backend/data/news_sources.json` | `nation-africa.enabled = false` + dated note | Persistent disable per contract |
| `backend/routers/jc_artifacts.py` NEW | Superadmin-gated JC artefact download | First instance: Track-2 deck |
| `backend/akki_app.py` | `_jc_artifacts` import + `_jc_artifacts.router` registration | 2-line add |
| `backend/tests/test_phase4_4_dual_mount_smoke.py` | `EXPECTED_API_SHA` + `EXPECTED_V1_SHA` + `EXPECTED_COMBINED_SHA` + path counts rolled forward; comment block updated | Surface-ratchet roll |
| `memory/DEV_PIPELINE.md` | §1 + §2 + §4 + §5 + §9 updated | BUG-ANL-UPLOAD-GRIDFS close audited |
| `memory/INVARIANT_HEALTH.md` NEW | Observability dashboard scaffold | 30 invariant rows |
| `memory/runbooks/PROD_INGRESS_AND_MEMORY.md` NEW | K8s deployment runbook | User-actionable |
| `memory/sprints/PHASE_5_5_3_BROADER_DRIFT_TRIAGE.md` NEW | Triage document | Investigative only |
| `memory/sprints/BUG_ANALYZE_UPLOAD.md` NEW | Sprint memo for the Phase 3 close | Canonical-spec cited line 1 |
| `memory/jc_artifacts/phase_5_5_3_failing_files_20260626.txt` NEW | 101 failing files alphabetical list | Triage artefact |

## Redeploy status — Wave 1

- N/A — Wave 1 ships infra cleanup + investigative docs + the
  authenticated artefact download. The Phase 3 GridFS migration
  is the one user-facing change that warrants a deploy, and it's
  gated on user-applied K8s ingress annotations per the runbook.
- No prod push attempted in this dispatch.

## Five-check regression — re-verified post Wave 1

The same 5-check bar that closed Phase 3 was re-run after Wave 1
changes landed:

| # | Check | Result |
|---|---|---|
| 1 | JC-TL Stage 1 — convergent deck 76555 bytes byte-identical | ✅ (no Wave 1 changes touched the deck pipeline) |
| 2 | Solva v2 schema+validator | ✅ 249 PASS (same 3 pre-existing CSRF fails confirmed PRE-EXISTING) |
| 3 | Contract snapshot 6/6 + dual mount smoke 37/37 | ✅ 43/43 PASS — ratchet rolled forward to absorb the 1 new JC artefact route |
| 4 | JC-TM Fan-Out | ✅ 24/25 (unchanged from baseline) |
| 5 | JC-TL Track-2 convergent + divergent render | ✅ 8/8 (unchanged from baseline) |

## Halt items surfaced for user direction

Two Wave 1 items hit the **locked-area collision** rule and need
user direction before they can ship:

### 🛑 H1: `services/solva_v2/` rename
- 66 import sites · 57 files in the directory · ~1 MB tree
- Track-2 schema files (`artefact_schema.py`, `pptx_exporter.py`,
  `engines/*`, `payload_builder.py`) live INSIDE this directory
- Per autonomy contract: "Locked-area collision (Track-2 schema) → HALT"
- Question for user: name suggestion? `services/solva/` collides with
  the existing top-level layout; `services/solva_artefacts/` reads
  honestly given the v2 surface IS the artefact-generation engine.
  Alternative: keep the directory name (it's grandfathered by the
  existing invariant) and only rename the public surface tags. Cost
  to defer: zero — the grandfathered exemption is stable.

### 🛑 H2: `solva_phase_d_sessions` Mongo collection rename
- 22 files · 50 references
- This is the storage for Solva v2 sessions including the just-shipped
  Track-2 sessions (73280 / 69105 bytes per render)
- Mongo collection rename is a `db.runCommand({renameCollection: ...})`
  call; can be done online but writes during the rename window will
  fail
- Per autonomy contract: locked-area collision again (Track-2
  session storage) → HALT
- Cost to defer: zero — the collection name is internal; no client
  knows about it.

Both halt items are book-keeping cleanups, not product blockers.
Defer indefinitely if you'd rather close other backlog first.

## Wave 1 standing rules respected

- ✅ No testing subagent. Proving slices + pytest only.
- ✅ Every change: DEV_PIPELINE §1 + §2 + §4 + §5 + §9 updated;
  sprint memo cites canonical spec on line 1.
- ✅ Halt-and-surface honoured for both locked-area collisions.
- ✅ Did not invent new work — closed pre-existing backlog items.

## Wave 2 scope (preview — not yet executed)

Per the user contract, Wave 2 is:

- Owner Digest weekly email (TM email rails reuse)
- Spread-heatmap delta (gated on Get-Perspectives ship — HALT until
  user signs Track-2)
- Auto-tune candidate objectives (gated on Get-Perspectives ship — HALT)
- JC-MON background tracker (post-on-demand proof)
- LLM_MODELS_REFRESH (matrix update — pure text)

Of these, two are gated on the GP ship (which is itself in HALT
state per the autonomy contract — requires user eyeball on
Track-2 render). The remaining three are independent:

1. **LLM_MODELS_REFRESH** — lowest risk, pure text/docs. Will
   start with this.
2. **JC-MON background tracker** — medium scope. Will tackle
   after #1.
3. **Owner Digest weekly email** — largest scope (touches TM
   email rails). Will assess after #1+#2; may break into smaller
   slice or defer.

## Open questions for the user

1. Want me to proceed into Wave 2 directly, or surface Wave 1 for
   review first?
2. The two halt items (H1 + H2) — defer indefinitely, or schedule
   for a future low-risk window when Track-2 is in a quieter state?
3. The Phase 5.5.3 triage doc proposes a Phase 5.6.1 → 5.7
   remediation sequence. Want me to pick up Phase 5.6.1 (CSRF
   auth-rig) inside this AUTONOMOUS BACKLOG RUN, or leave it for
   a deliberate sprint?

— End of Wave 1 close.
