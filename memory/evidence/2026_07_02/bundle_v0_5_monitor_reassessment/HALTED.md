# Bundle 3 · V0.5 · Monitor Reassessment · HALTED

**Timestamp:** 2026-07-02  
**Canonical criteria source:** `/app/memory/user_actions/V0_5_VERIFICATION_CHECKLIST.md`

## Halt reason

Bundle spec: "a real background-tracker run showing a reassessment fired on a tracked-evidence change (the log + the updated objective)."

**Blockers:**
1. **No existing monitored objective identified in julius contexts.** Need to query `monitor_background_items` for a live objective owned by julius (`f23cd1fe-bbb8-40ea-baa1-73945ca0fcd2`) that has recent enough state to demonstrate a reassessment delta meaningfully.
2. **Background-tracker firing mechanism unclear.** Two paths:
   - Wait for scheduled fire (`akki.news_aggregator` fires nightly per backend logs — but that's the news source, not the objective tracker). Need to identify the actual monitor-tracker scheduler and its cadence.
   - Force-run via admin endpoint. Need to identify which admin endpoint triggers the tracker on-demand. Grep `routers/monitor_*.py` for the admin trigger surface.
3. **Tracked-evidence change is user-facing.** The dispatch prohibits mocking — the change must be introduced via a real UI or shipped API action. Attaching a new document requires the Work Studio upload path (which was ENOSPC-affected during preview instability). Updating a linked brief requires a brief-edit endpoint.

These setup steps individually are feasible but collectively consume ~30-60min of investigation + capture time. Given the dispatch's parallel-with-P3 discipline and context budget constraints, this bundle is best executed with dedicated attention rather than interleaved.

## What's needed from user to proceed

- **Objective pointer.** Which monitored objective under julius should be the target? Options depend on what `monitor_background_items` currently has.
- **Evidence-change vector.** Which shipped user action introduces the change: (a) new doc attached via Work Studio, (b) brief content update, (c) signal update via monitor UI, (d) something else?
- **Tracker fire mechanism.** Wait for scheduled or force-fire via `/api/monitor/admin/tracker/fire` (or equivalent — endpoint TBC)?

## What HAS been staged

- `/app/memory/evidence/2026_07_02/bundle_v0_5_monitor_reassessment/` folder created.

## Immediate resume recipe

```
# 1. Identify target objective
db.monitor_background_items.find({account_id: "f23cd1fe-bbb8-40ea-baa1-73945ca0fcd2"}).limit(3)

# 2. Snapshot BEFORE
GET /api/monitor/background-items/{objective_id} → JSON dump

# 3. Introduce change (user picks vector)
# e.g., POST /api/contexts/{cid}/documents (upload)  OR  POST /api/briefs/{bid} (update)

# 4. Fire tracker (mechanism TBC)
POST /api/monitor/admin/tracker/reassess?item_id={objective_id}

# 5. Log tail + AFTER snapshot
tail -f /var/log/supervisor/backend.out.log | grep tracker
GET /api/monitor/background-items/{objective_id} → JSON dump

# 6. Diff → README.md
```

**Do NOT block P3/P4/A4 chain on this bundle.**
