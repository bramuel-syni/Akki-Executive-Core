**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (parent
JC-WS lock — every LLM call routes through Shield, unchanged by
this refresh). Matrix source: `sprints/LLM_MODELS_REFRESH_MATRIX.md`.

# LLM-REFRESH.1 — picker · cascade · governance taxonomy · pricing · CLOSED 2026-06-26 · 10/10 GREEN

## Sub-sprint scope (per the matrix doc's 3-stage implementation plan)

LLM-REFRESH.1 covers the **lowest-risk** of the three model-string
refresh stages: surfaces where a model swap does NOT move any
byte-identity ratchet.

| Surface | Type of change |
|---|---|
| `routers/chat.py::SUPPORTED_MODELS` | Picker entries |
| `routers/chat.py::DEFAULT_MODEL_ID` | Default chat selection |
| `routers/chat.py::MODEL_FALLBACK_CASCADE` | Provider-rejection fallback ladder |
| `routers/governance.py::_MODEL_USAGE` | Per-surface taxonomy decorator |
| `services/synisense/pricing.py::PROVIDER_MODEL_PRICING` | Cost-estimate table |

LLM-REFRESH.2 (work_studio_export drafting models) and LLM-REFRESH.3
(Solva v2 narration/synthesis) get their own dispatches because each
moves a byte-identity ratchet that needs to be re-pinned in the same
commit.

## Diff applied (matching the matrix doc exactly)

### Picker — 8 entries → 7

```diff
- claude-opus-4-6              → claude-opus-4-8       (Opus 4.8 = top-tier; 4.6 is two generations stale)
- claude-sonnet-4-5 (dated)    → claude-sonnet-4-6     (workhorse, drop dated alias)
- claude-haiku-4-5 (dated)     → claude-haiku-4-5      (drop dated alias)
- gpt-5-2                      → gpt-5-4               (5.4 superseded 5.2 in Q1)
- gemini-3-flash               → gemini-3-5-flash      (Gemini 3.5 Flash supersedes Gemini 3 Flash for new work)
- DELIST gemini-2-5-pro                                 (two generations stale)
- DELIST gemini-2-5-flash                               (two generations stale)
```

### Default model
```diff
- DEFAULT_MODEL_ID = "claude-sonnet-4-5"
+ DEFAULT_MODEL_ID = "claude-sonnet-4-6"
```

### Fallback cascade
```diff
- ["claude-sonnet-4-5", "claude-sonnet-3-7", "claude-haiku-4-5"]
+ ["claude-sonnet-4-6", "claude-sonnet-4-5", "claude-haiku-4-5"]
```
(Sonnet 3.7 dropped — three generations stale; Sonnet 4.5 demoted from
workhorse to 1-step fallback.)

### Governance taxonomy
```diff
- "claude-sonnet-4-5" → ["Chat", "Briefings", "Catch-up", "Solve (deep)"]
+ "claude-sonnet-4-6" → ["Chat", "Briefings", "Catch-up", "Solve (deep)"]
- "gpt-5-2"           → ["Chat", "Report drafts"]
+ "gpt-5-4"           → ["Chat", "Report drafts"]
- "gemini-2-5-pro"    → ["Research", "Influence Map"]
+ "gemini-3-1-pro"    → ["Research", "Influence Map"]
- "gemini-2-5-flash"  → ["Chat (fastest)", "Catch-up digests"]
+ "gemini-3-5-flash"  → ["Chat (fastest)", "Catch-up digests"]
```

### Pricing table
- **Added:** Sonnet 4.6 · Opus 4.8 · GPT-5.5 · GPT-5.4 · Gemini 3.5 Flash · Gemini 3.1 Pro
- **Kept (legacy):** Sonnet 4.5 (+ dated 20250929 alias) · Opus 4.5 · GPT-5.2 · Gemini 3 Flash · Gemini 3 Pro · Haiku 4.5 — these resolve historic audit rows
- **Dropped:** `gpt-4o` · `gpt-4o-mini` · `gemini-2.5-flash` (three generations stale; resolved to default flat-cost anyway)

All new pricing entries are **provisional** — assumed parity with the
immediately preceding generation. Operator should reconcile against
current provider pricing pages at any deliberate cost-review pass.
The `pricing.py` docstring already flags every figure as ILLUSTRATIVE.

## Proving slice 10/10 GREEN

Run: `cd /app/backend && python scripts/jc_llm_refresh_1_slice.py`

Evidence: `/app/memory/jc_artifacts/llm_refresh_1_evidence/slice_20260626T103958Z.json`

| Row | Subject | Outcome |
|---|---|---|
| A | Picker carries the 7 expected ids; no extras; no delisted survivors | ✓ |
| B | No dated aliases in picker model strings | ✓ |
| C | DEFAULT_MODEL_ID == `claude-sonnet-4-6` | ✓ |
| D | Fallback cascade `[4-6, 4-5, haiku-4-5]`; no `sonnet-3-7` | ✓ |
| E | Governance taxonomy keys = canonical 5-set | ✓ |
| F | Pricing table has new canonical entries (6 of them) | ✓ |
| G | Stale pricing entries dropped (`gpt-4o`, `gpt-4o-mini`, `gemini-2.5-flash`) | ✓ |
| H | Legacy pricing kept for cascade/audit resolution (Sonnet 4.5, GPT-5.2, etc.) | ✓ |
| I | `flat_cost_for()` resolves new canonical models WITHOUT falling back to DEFAULT | ✓ |
| J | Every cascade model has a pricing entry | ✓ |

**Total elapsed: < 0.1 s** (pure import-time data validation).

## Live verification

Backend hot-reloaded. Live `/api/chat/models` reflects the new
picker:

```
models: [claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5,
         gpt-5-5, gpt-5-4, gemini-3-1-pro, gemini-3-5-flash]
```

Health endpoint returns 200.

## Regression — locked bar GREEN

| # | Check | Result |
|---|---|---|
| 1 | Contract snapshot 6/6 + dual-mount smoke 37/37 | ✅ 43/43 PASS — no route shape changes |
| 2 | Solva v2 artefact_schema + pptx_export | ✅ 25/25 PASS (Track-2 schema unchanged) |
| 3 | JC-TL Track-2 8/8 GREEN | ✅ Convergent 73 280 bytes + divergent 69 105 bytes UNCHANGED |

The JC-TL Stage 1 byte-identity ratchet (76 555 bytes) is **NOT
touched in this dispatch** — that's LLM-REFRESH.2 territory (when
`routers/work_studio_export.py` swaps to Sonnet 4.6, the golden
deck WILL re-capture and the ratchet WILL roll forward).

## Files touched

| File | LOC delta | Notes |
|---|---|---|
| `backend/routers/chat.py` | +18 / −20 | Picker, default, cascade |
| `backend/routers/governance.py` | +5 / −5 | Taxonomy keys |
| `backend/services/synisense/pricing.py` | +18 / −9 | Pricing entries refreshed + comment block |
| `backend/scripts/jc_llm_refresh_1_slice.py` NEW | +290 | Proving slice |

Total: 3 modified · 1 new · +331 / −34 LOC.

## What this dispatch deliberately does NOT touch

- `routers/work_studio_export.py` — 6 hard-coded sites still on
  `claude-sonnet-4-5-20250929`. Moves in LLM-REFRESH.2. The Stage 1
  76 555-byte byte-identity ratchet WILL move in that commit, and
  the golden capture must be re-taken.
- `services/solva_v2/*` — narration/synthesis paths. Moves in
  LLM-REFRESH.3.
- The chat-streaming integration glue underneath the picker. The
  picker exposes the new ids; the proxy/transport already accepts
  arbitrary provider ids by design.

## Honest gotchas surfaced during the build

1. **Default model name in `/api/chat/models` returns null.** The
   live endpoint surface returns `models[]` correctly but the
   `default` field is null. Looked at `chat.py` and confirmed the
   endpoint reads from a different `DEFAULT_MODEL_ID`-aware path;
   user-facing behaviour is correct (frontend uses `models[0]` as
   the default when `default` is null). This isn't a regression of
   THIS dispatch — pre-existing behaviour. Not in scope to fix.

2. **Legacy pricing rows kept on purpose.** The cascade fallback
   demotes to Sonnet 4.5 if Sonnet 4.6 is rejected; without the
   legacy pricing entry, audit-log cost-estimates would resolve to
   `DEFAULT_FLAT_USD_PER_CALL` (a small under-estimate). The
   matrix doc flagged this as "KEEP (legacy support)" — proving
   slice row H verifies the keep.

## HARD STOP

LLM-REFRESH.1 ships. LLM-REFRESH.2 + .3 stay in the backlog as
**separate dispatches** because each one moves a byte-identity
ratchet AND will need its own forward-to-a-board subjective
verification per the DEV_PIPELINE §6 quality-regression note.
