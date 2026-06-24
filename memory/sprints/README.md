# Sprint Memo Convention

Every phase-close report must, before being declared shipped:
1. Update `/app/memory/DEV_PIPELINE.md` §4 Invariant Ladder + §5 Surface Ratchet + §9 Phase History **FIRST**.
2. Confirm the update via grep/diff evidence.
3. **THEN** write the sprint memo at `/app/memory/sprints/<phase>.md`.

> **Order matters.** Writing the sprint memo BEFORE the §9 row creates a CI window where the `pipeline-log-sync` gate would fail (the new memo exists but its identifier isn't in §9 yet). Flipping the order so DEV_PIPELINE.md lands first closes that window — the sprint memo can only land into a state where §9 is already updated.

> Phase Pipeline-Log-Sync (2026-06-24) established this rail. Phase B0 (2026-06-24) is the first dispatch using the flipped order.

