# Bundle 5 · V0.5 · Origin Briefs · HALTED

**Timestamp:** 2026-07-02  
**Canonical criteria source:** `/app/memory/user_actions/V0_5_VERIFICATION_CHECKLIST.md`

## Halt reason

Bundle spec: "one brief triggered from Solva and one from TM, each delivered at origin."

**Blockers:**

1. **Solva origin-brief trigger unclear.** `routers/solva_briefing.py:47` prefix is `/api/solva/briefing` — this is the state-tracking endpoint (`solva_briefing_state` collection stores per-user × area briefing progress), NOT the origin-brief EMIT endpoint. Need to identify which Solva v2 session path emits an origin brief and under what condition (session completion? synthesis phase? artefact export?). Grep on `origin_brief\|briefings_monitor` in routers/ did not surface the emit callsite in this pass.

2. **TM origin-brief trigger unclear.** `routers/tasks.py` + `routers/tasks_initiatives.py` — where does a task/initiative emit an origin brief? Fan-out per `JC_WAVE3_ORIGIN_BRIEFS_SOLVA_TM_FANOUT.md` (CLOSED 2026-06-26) but the exact trigger action (task creation? state change? completion? contributor comment?) is not surfaced by name-based grep alone.

3. **Delivery capture requires the same SendGrid wiring as Bundle 4** for email delivery, plus in-app notification queue query. If briefs deliver via both, both channels need capture. Bundle 4 blockers apply here too (real outbound to a real Gmail).

## What's needed from user to proceed

- **Solva v2 session flow that emits origin brief.** Which session type (framing? question? phase D? completion?) triggers the brief? User confirmation from `JC_WAVE3_ORIGIN_BRIEFS_SOLVA_TM_FANOUT.md` scope.
- **TM action that emits origin brief.** Which task-management action fires the brief? (task creation with contributor? initiative fan-out complete? etc.)
- **Delivery target confirmation.** Same as Bundle 4 — is real outbound to `juliusaopio@gmail.com` authorized, or throwaway address?

## What HAS been staged

- `/app/memory/evidence/2026_07_02/bundle_v0_5_origin_briefs/` folder created.

## Immediate resume recipe

```
# 1. Locate trigger callsites (needs codebase grep with confirmed keywords)
grep -rn "emit_origin_brief\|origin_brief.*insert\|briefings_monitor.insert" /app/backend/routers /app/backend/services

# 2. Fire Solva origin brief
# (endpoint TBC once located)

# 3. Fire TM origin brief
# (endpoint TBC once located)

# 4. Capture each brief's outbound delivery + in-app notification queue entry
# 5. Timestamp trail README
```

**Do NOT block P3/P4/A4 chain on this bundle.**
