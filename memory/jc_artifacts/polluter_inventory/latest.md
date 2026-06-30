# Polluter Inventory — 2026-06-30T17:09:04.331866+00:00

READ-ONLY observability snapshot of bespoke-`_run` / `asyncio.run` polluter landscape.

## Live tree counts
- M1 (`_run` helper) files: **0**
- M2 (`asyncio.run` in test body) sites: **26** across **8** files

## Grandfather YAML state
- M1 entries: **0** / ceiling 0
- M2 entries: **26** / ceiling 26

## Drift report
- ✅ No new M1 polluters
- ✅ No stale M1 entries
- ✅ No new M2 polluters
- ✅ No stale M2 entries

## Per-sub-sprint roll-up
- **A+D fix preserves this asyncio.run with snapshot/restore** — M1: 0 · M2: 1
- **Cluster-G (post-F)** — M1: 0 · M2: 25

## Closure status
✅ All grandfather entries match the live tree. No drift.