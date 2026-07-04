# Bundle 1 · LLM_REFRESH .2 · Work Studio · PARTIAL (substrate-thin)

**Timestamp:** 2026-07-04T18:06:11.488315+00:00
**Canonical criteria source:** `/app/memory/user_actions/LLM_REFRESH_SIGNOFF_CHECKLIST.md`
**Canonical scope source:** `/app/memory/sprints/JC_LLM_MODELS_REFRESH_EVALUATION.md`
**Dispatch disposition (2026-07-04):** (a) NED Seat (default). Pivot allowed if thinner than Govt Exec.

## Substrate probe · findings

```
NED Seat context     (f954d5d0-50d...)  → 3 documents
Govt Exec context    (f50f33e1-a2b...)  → 3 documents
```

**Pivot decision:** NED Seat (dispatch default). Govt Exec substrate has the same doc count (3), so no pivot triggered — both contexts equally thin.

## Existing exports (LLM refresh comparison substrate)

- **2 existing Work Studio export(s)** for julius across all
  contexts (see `existing_export_rosters.json` for full details incl.
  `model_roster` field).
- Bundle spec calls for "one Board Pack and one Deck from the same
  source set on the new roster, side-by-side old-roster outputs if
  they exist." The existing exports provide the "old" comparison side
  if any predate the LLM refresh cutover date. New captures on the
  current roster would consume ~2-5 min of LLM streaming per artifact.

## What WAS captured (mechanical)

- `substrate_probe.json` — doc counts across julius NED + Govt Exec
  contexts and existing Work Studio export inventory.
- `existing_export_rosters.json` — the `model_roster` field per
  existing export, which is the LLM-refresh comparison surface.

## What was NOT captured (declared gaps)

- **Fresh Board Pack + Deck generation on the current roster**
  — NOT performed. Substrate is thin (3 docs on NED, 3 on Govt Exec)
  and would produce degrade-shape output rather than a meaningful
  LLM refresh comparison. Per truth-in-capability: fresh generation
  on thin substrate demonstrates LLM degrade behaviour on sparse
  input, not roster refresh quality.
- **Old-roster comparison outputs** — the `existing_export_rosters.json`
  file contains what's present; whether it precedes the LLM refresh
  cutover is a user judgment on the `model_roster` values dumped.

## Truth-in-capability closure line

Substrate insufficient — Board Pack output demonstrates LLM degrade
behavior on sparse input, not LLM roster refresh quality. Recapture
with richer substrate recommended for meaningful roster comparison.

## Reproduction / next-step to enrich substrate

```bash
# 1. Seed additional strategic docs into julius NED context:
cd /app/backend && set -a && source .env && set +a && \
  python scripts/seed_julius_opio.py

# 2. Re-run this bundle capture:
cd /app/backend && python scripts/jc_bundle_capture_2026_07_02.py --bundle b1
```
