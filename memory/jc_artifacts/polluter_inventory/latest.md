# Polluter Inventory — 2026-06-27T03:45:21.265443+00:00

READ-ONLY observability snapshot of bespoke-`_run` / `asyncio.run` polluter landscape.

## Live tree counts
- M1 (`_run` helper) files: **8**
- M2 (`asyncio.run` in test body) sites: **28** across **9** files

## Grandfather YAML state
- M1 entries: **8** / ceiling 8
- M2 entries: **28** / ceiling 28

## Drift report
- ✅ No new M1 polluters
- ✅ No stale M1 entries
- ✅ No new M2 polluters
- ✅ No stale M2 entries

## Per-sub-sprint roll-up
- **A+D fix preserves this asyncio.run with snapshot/restore** — M1: 0 · M2: 1
- **Cluster-G (post-F)** — M1: 5 · M2: 25
- **F.3** — M1: 3 · M2: 0
- **F.6** — M1: 0 · M2: 2

## Closure status
✅ All grandfather entries match the live tree. No drift.