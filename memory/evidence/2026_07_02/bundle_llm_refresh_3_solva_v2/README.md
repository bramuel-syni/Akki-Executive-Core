# Bundle 2 · LLM_REFRESH .3 · Solva v2 · GAP-DECLARED (paths verified, no sessions run)

**Timestamp:** 2026-07-04T18:06:11.488315+00:00
**Canonical criteria source:** `/app/memory/user_actions/LLM_REFRESH_SIGNOFF_CHECKLIST.md`
**Canonical scope source:** `/app/memory/sprints/JC_LLM_MODELS_REFRESH_EVALUATION.md`
**Dispatch disposition (2026-07-04):** (a) + (b) combined — grep-verify 4 paths in `submodules.py`; if all present, use for captures; log drift.

## Path enumeration verification

Shipped paths (`services/solva_v2/submodules.py::SUBMODULE_NAMES`):
```
['seek_clarity', 'develop_strategy', 'simulate_hypothesis', 'get_perspective']
```

User-directive paths:
```
['develop_strategy', 'seek_clarity', 'simulate_hypothesis', 'get_perspective']
```

**No drift. All 4 user-directive paths present in `services/solva_v2/submodules.py::SUBMODULE_NAMES` with exact snake_case naming. Zero missing, zero extras.**

## What WAS captured (mechanical)

- `path_verification.json` — the exact shipped enum vs the user
  directive with delta.

## What was NOT captured (declared gap)

- **4 full sessions × 4 paths** (`develop_strategy`, `seek_clarity`,
  `simulate_hypothesis`, `get_perspective`) — **NOT run**.
- Julius has **0 existing solva_sessions** (zero) at capture
  time. A full session on each path requires:
   - Session creation (`POST /api/solva/v2/sessions` with `submodule=<path>`)
   - Framing + Question layer traversal (LLM streaming, ~30-60s each)
   - Synthesis + Artefact export (LLM streaming, ~30-60s each)
   - Total per path: ~2-4 min · 4 paths = **8-16 min of LLM streaming**
- Substrate quality note: julius has 6 docs across NED + Govt
  contexts. Full-fidelity session captures would benefit from richer
  substrate first (same substrate gap surfaced by Bundle 1).

## Truth-in-capability closure line

4 Solva v2 paths verified present in code and named-consistent with
dispatch (no drift). 4 sessions × 4 paths NOT captured — deferred to
richer substrate + dedicated dispatch window for LLM-streaming budget.

## Reproduction (once substrate + dispatch window authorized)

```bash
# Per-path headless session driver (pseudo — needs full-arc runner):
for path in seek_clarity develop_strategy simulate_hypothesis get_perspective; do
  # 1. Create session with submodule=$path
  # 2. Step framing → question → synthesis → artefact
  # 3. Capture streaming logs + final artefact
  # (Requires an existing driver script or new one at
  #  scripts/jc_solva_v2_session_driver.py)
done
```
