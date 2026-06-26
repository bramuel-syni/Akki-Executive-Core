**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (parent
JC-WS lock for every Shield-routed LLM call). This refresh follows
the directive in DEV_PIPELINE §6 ("LLM_MODELS_REFRESH · NEXT
SPRINT") with the autonomy-contract guidance "use current provider
matrix + emergent-key conventions; document the refresh diff in
sprint memo."

# LLM_MODELS_REFRESH — Feb 2026 canonical matrix + per-surface refresh diff

**Scope:** Documentation-only. NO code changes shipped from this
dispatch. The matrix below is the proposed canonical refresh for
the next deliberate sprint that's willing to take the quality-
regression hit (every model swap is a confounding variable per
DEV_PIPELINE §6 footnote).

## Today's mixed state (audited 2026-06-26)

I grepped `routers/` + `services/` for model identifiers and found
**21 distinct model strings** across the codebase, of which **7 are
stale** (pre-Feb-2026 generation). Three classes of call-site:

1. **`routers/chat.py::SUPPORTED_MODELS`** — the user-facing chat
   picker, exposing 8 model choices (3 Anthropic · 2 OpenAI · 3 Google).
2. **`routers/chat.py::MODEL_FALLBACK_CASCADE`** — the 3-step
   model-id-rejection fallback (chosen → Sonnet 4.5 → Sonnet 3.7 →
   Haiku 4.5).
3. **`routers/governance.py::_MODEL_USAGE`** — the per-surface
   taxonomy that decorates the `connected_models` API for the
   governance dashboard.
4. **`routers/work_studio_export.py`** — hard-codes
   `claude-sonnet-4-5-20250929` at 4 sites for board-pack drafting
   (P1 plan, P2 enrichment).
5. **`services/synisense/pricing.py::PROVIDER_MODEL_PRICING`** —
   per-call cost estimate table.

## Proposed canonical matrix (Feb 2026)

| Provider | Tier | Current canonical | Replaces |
|---|---|---|---|
| Anthropic | Workhorse (default) | **Claude Sonnet 4.6** | Sonnet 4.5 |
| Anthropic | Long-form / deep reasoning | **Claude Opus 4.8** | Opus 4.6 / 4.7 |
| Anthropic | Fast / cheap safety net | **Claude Haiku 4.5** | (unchanged) |
| OpenAI | Newest / chat default | **GPT-5.5** | (unchanged) |
| OpenAI | Balanced / fast | **GPT-5.4** | GPT-5.2 |
| OpenAI | Cheap / classification | **GPT-5.4 Mini** | (new tier) |
| Google | Most advanced | **Gemini 3.1 Pro** | Gemini 2.5 Pro |
| Google | Fast flagship | **Gemini 3.5 Flash** | (new) — replaces Gemini 3 Flash for new work |
| Google | Legacy fast | Gemini 3 Flash | kept as fallback |

## Per-call-site refresh diff

Format: `call site` → `current model` → `proposed model` → `rationale`

### `routers/chat.py::SUPPORTED_MODELS` (picker)

| # | Current id | Current model string | Proposed model string | Rationale |
|---|---|---|---|---|
| 1 | claude-opus-4-6 | `claude-opus-4-6` | `claude-opus-4-8` | Opus 4.8 is the current top-tier; 4.6 is two generations stale |
| 2 | claude-sonnet-4-5 | `claude-sonnet-4-5-20250929` | `claude-sonnet-4-6` | Sonnet 4.6 is the current workhorse; drop the dated alias |
| 3 | claude-haiku-4-5 | `claude-haiku-4-5-20251001` | `claude-haiku-4-5` | Drop dated alias, keep family head |
| 4 | gpt-5-5 | `gpt-5.5` | `gpt-5.5` | Already current |
| 5 | gpt-5-2 | `gpt-5.2` | `gpt-5.4` | GPT-5.4 superseded 5.2 mid-Q1 |
| 6 | gemini-3-1-pro | `gemini-3.1-pro` | `gemini-3.1-pro` | Already current (highest in Gemini 3 line) |
| 7 | gemini-3-flash | `gemini-3-flash` | `gemini-3.5-flash` | Gemini 3.5 Flash supersedes Gemini 3 Flash for new work |
| 8 | gemini-2-5-pro | `gemini-2.5-pro` | DELIST | Two generations stale |
| 9 | gemini-2-5-flash | `gemini-2.5-flash` | DELIST | Two generations stale |

Net: 8 picker entries → 7 picker entries (drop the two stale Gemini 2.5 rows).

`DEFAULT_MODEL_ID = "claude-sonnet-4-5"` → `"claude-sonnet-4-6"`.

### `routers/chat.py::MODEL_FALLBACK_CASCADE`

| Step | Current | Proposed |
|---|---|---|
| 1 | `claude-sonnet-4-5` workhorse | `claude-sonnet-4-6` |
| 2 | `claude-sonnet-3-7` Anthropic-published anchor | `claude-sonnet-4-5` (drop 3.7 — 3 generations stale) |
| 3 | `claude-haiku-4-5` safety net | `claude-haiku-4-5` (unchanged) |

### `routers/governance.py::_MODEL_USAGE` (taxonomy)

| Current model | Surfaces | Proposed model |
|---|---|---|
| `claude-sonnet-4-5` | Chat, Briefings, Catch-up, Solve (deep) | `claude-sonnet-4-6` |
| `claude-haiku-4-5` | Chat (fast), Ingestion, Signal extraction | `claude-haiku-4-5` |
| `gpt-5-2` | Chat, Report drafts | `gpt-5-4` |
| `gemini-2-5-pro` | Research, Influence Map | `gemini-3.1-pro` |
| `gemini-2-5-flash` | Chat (fastest), Catch-up digests | `gemini-3.5-flash` |

### `routers/work_studio_export.py` (Board Pack drafting)

Four hard-coded sites: `p1_model`, `p2_model`, and 4 `model_id`
audit-log fields. All currently `claude-sonnet-4-5-20250929`.

| Site | Current | Proposed | Notes |
|---|---|---|---|
| L560 `p1_model` | `claude-sonnet-4-5-20250929` | `claude-sonnet-4-6` | Drop dated alias |
| L708 `p2_model` | `claude-sonnet-4-5-20250929` | `claude-sonnet-4-6` | Drop dated alias |
| L1000 audit `model_id` | `claude-sonnet-4-5` | `claude-sonnet-4-6` | Audit-log echo of L560 |
| L1472 audit `model_id` | `claude-sonnet-4-5-20250929` | `claude-sonnet-4-6` | Audit-log echo of L708 |
| L1559 audit `model_id` | `claude-sonnet-4-5-20250929` | `claude-sonnet-4-6` | Audit-log echo of L708 |
| L1896 audit `model_id` | `claude-sonnet-4-5` | `claude-sonnet-4-6` | Enhance flow |

⚠️ **Quality-regression risk.** Stage 1 deck byte-identical at
76555 bytes is pinned against `claude-sonnet-4-5-20250929`
outputs. Swapping to Sonnet 4.6 WILL change the deck contents
(LLM outputs are model-dependent). This isn't a defect — it's
the expected consequence of a model swap — but it means **the
JC-TL Stage 1 76555-byte byte-identity ratchet has to be rolled
forward in the same commit as the model swap, with a fresh
golden capture.**

### `services/synisense/pricing.py::PROVIDER_MODEL_PRICING`

| Current key | Action | Proposed key | Pricing (input/output USD per million tokens) |
|---|---|---|---|
| `("anthropic", "claude-sonnet-4-5-20250929")` | DROP | — | — |
| `("anthropic", "claude-sonnet-4-5")` | KEEP (legacy support) | unchanged | `(3.00, 15.00, 0.0030)` |
| `("anthropic", "claude-sonnet-4-6")` | ADD | new | `(3.00, 15.00, 0.0030)` (provisional — assumes pricing parity) |
| `("anthropic", "claude-haiku-4-5")` | KEEP | unchanged | `(0.80, 4.00, 0.0008)` |
| `("anthropic", "claude-opus-4-5")` | DROP | — | — |
| `("anthropic", "claude-opus-4-8")` | ADD | new | `(15.00, 75.00, 0.0150)` (provisional — assumes pricing parity) |
| `("openai", "gpt-4o")` | DROP | — | — |
| `("openai", "gpt-4o-mini")` | DROP | — | — |
| `("openai", "gpt-5.4")` | ADD | new | `(1.25, 10.00, 0.0015)` (provisional) |
| `("openai", "gpt-5.5")` | ADD | new | `(2.50, 20.00, 0.0030)` (provisional) |
| `("gemini", "gemini-2.5-flash")` | DROP | — | — |
| `("gemini", "gemini-3-flash")` | KEEP (legacy support) | unchanged | `(0.50, 2.00, 0.0010)` |
| `("gemini", "gemini-3.5-flash")` | ADD | new | `(0.30, 1.20, 0.0006)` (provisional — assumes pricing parity) |
| `("gemini", "gemini-3-pro")` | KEEP (legacy support) | unchanged | `(1.25, 5.00, 0.0025)` |
| `("gemini", "gemini-3.1-pro")` | ADD | new | `(2.00, 8.00, 0.0040)` (provisional) |

Pricing notes are **illustrative** (per `pricing.py` docstring); will need
operator review against current provider pricing pages at commit time.

## Implementation plan (deliberate sprint — NOT this dispatch)

The actual code swap is a 3-step sprint:

### Sprint LLM-REFRESH.1 — Picker + cascade + governance taxonomy

1-day sprint. Touch:
- `routers/chat.py` (SUPPORTED_MODELS + DEFAULT_MODEL_ID + MODEL_FALLBACK_CASCADE)
- `routers/governance.py` (`_MODEL_USAGE`)
- `services/synisense/pricing.py` (entries)

Verification: chat picker shows new set; cost estimates change
proportionally; governance "connected models" page reflects new
taxonomy. No artefact-quality regression because chat is freeform.

### Sprint LLM-REFRESH.2 — Work Studio drafting models

2-day sprint. Touch:
- `routers/work_studio_export.py` (6 sites)
- Re-capture the JC-TL Stage 1 golden deck on the new model; roll
  the 76555-byte ratchet forward to its new value
- Run JC-TM Fan-Out + JC-MON Stage 3 against the new model;
  recapture any byte-stable artefacts

Quality regression: HALT if user-perceived deck quality drops.
"Forward-to-a-board" subjective test required per the
"Why this is parked, not actioned now" note in DEV_PIPELINE §6.

### Sprint LLM-REFRESH.3 — Solva v2 narration / extraction / synthesis

3-day sprint. Touch:
- `services/solva_v2/llm_adapter.py` (model selection per role)
- `services/solva_v2/analyze_narration.py` (narration model)
- `services/solva_v2/payload_builder.py` (synthesis model)

Quality regression: each Solva v2 surface (Chat, Briefings,
Catch-up, Solve deep) needs a separate subjective sign-off.

## Skipped intentionally

- **Direct provider SDK calls.** None exist outside Shield. The
  Shield contract (every LLM call routed through
  `services/synisense/shield/client.py`) is unchanged by this
  refresh; only the model strings inside the call sites change.

- **Adding Claude Opus 4.7 to the chat picker.** The picker is
  positioned for end-user choice, not Anthropic's model bench.
  4.8 (top tier) + 4.6 (workhorse) + 4.5 (Haiku family) covers
  the use cases; exposing 4.7 + 4.6 + 4.5 would be three Anthropic
  rows of "different generations of the same family" without
  meaningful product differentiation.

- **Adding Sora 2 video generation.** Out of scope — no current
  surface uses video.

- **Switching the Audit dashboard's Catch-up digest to GPT.** Stay
  on Gemini Flash for that surface; Gemini's Flash tier remains the
  fastest digest-class generator and the catch-up use case prizes
  speed > nuance.

## Halt items

None at this layer. The refresh is **documentation-only** in this
dispatch. The deliberate-sprint code swaps will each need user
sign-off because every swap moves the byte-identity pins.

## Standing rules respected

- ✅ Every LLM call routes through Shield — unchanged.
- ✅ Tenancy + audit + fail-closed semantics — unchanged.
- ✅ No direct provider SDK calls — unchanged.
- ✅ Sprint memo cites canonical spec on line 1.
- ✅ Did not chain into code change — this is the matrix, not the
  swap.
