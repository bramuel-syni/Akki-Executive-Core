# BACKLOG_SCHEDULE — explicitly logged items deferred by the autonomy contract

> **Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (parent).
> Items here are deferred deliberately and carry an explicit
> condition for re-pickup. Items are listed in priority order.
> Format: `[Pri] · Item · Why deferred · Unblock condition`.

## Logged 2026-06-26 — AUTONOMOUS BACKLOG RUN waves 1+2

### P0 (deferred at user direction)

— **(none)** — Phase 3 GridFS migration was the only P0; it closed
2026-06-26 with 11/11 proving slice + 5/5 regression GREEN.

### P1 (deferred at user direction)

1. **FTT-014 — `test_phase_i5_open_questions::test_i5_B1_backfill_idempotent` deterministic regression** (NEW, promoted from pollution-tracker reclassification 2026-06-26). The per-file capture (`P5_7_PER_FILE_CAPTURE.md`) confirmed the test fails in isolation (FAIL_DETERMINISTIC at 12.2 s), not from pollution. Real bug hiding behind the broad-suite noise. **Bug-fix sprint required**: investigate the backfill-idempotency assertion drift in isolation; identify whether it's a per-test setup issue (Mongo collection state from prior in-FILE tests inside `test_phase_i5_open_questions.py`), a real backfill-idempotency regression in the i5 open-questions code path, or an environment-coupled assertion. *Unblock condition:* user picks fix scope (debug now vs. file Phase-I5 audit). Surface: `FAILING_TEST_TRACKER.md` → DETERMINISTIC REGRESSIONS section.

2. **`services/solva_v2/` directory rename + `solva_phase_d_sessions` Mongo
   collection rename** — Blocked on Track-2 schema relocation
   (locked-area collision — Track-2 schema files live INSIDE
   `services/solva_v2/`). Defer until **JC-WS Phase 4 or post-GP-ship
   stabilisation** when the Track-2 surface is provably stable in
   production AND the directory rename can carry its own quality
   regression. *Touched by:* nothing in this dispatch. *Surface
   rationale:* the autonomy contract HALT-on-locked-area rule
   directly applies; renaming would risk Track-2 byte-identity
   ratchets that just shipped GREEN.

2. **Phase 5.6.1 — CSRF auth-rig drift fix.** Test-infra surgery
   (40-50 % of 101 failing tests). Second-order effects possible.
   Deferred to deliberate sprint when user is awake.
   *Source:* `sprints/PHASE_5_5_3_BROADER_DRIFT_TRIAGE.md`.

3. **Wave 4 — JC-TL Get-Perspectives ship.** Requires user eyeball
   on Track-2 divergent first-render. Download URL is live at
   `/api/jc-artifacts/track2/divergent-first-render.pptx`. Unblocks
   when user sign-off received. *Side effects of unblocking:*
   Spread-heatmap delta + Auto-tune candidate objectives both
   become eligible.

4. **Owner Digest weekly email scoping.** Requires user direction
   on 6 questions (schedule, audience, content slate, CTAs,
   suppression, opt-out). Smallest-valuable-slice already sketched
   in `AUTONOMOUS_BACKLOG_RUN_20260626T1020Z_WAVE2.md`. Defer until
   user steers.

5. **JC-MON background tracker scoping.** Requires user direction
   on 3 questions (trigger source, cost ceiling, on-demand
   conflict). Trigger criterion (on-demand has proved trustworthy)
   is met. Defer until user steers.

11. **Cross-test pollution cleanup sprint (now: 4 confirmed pairs · 10 FTT IDs).**
    Bisect closed 2026-06-26 (newest first):
    - **P5.7-BISECT** — statically-narrowed predecessor search.
      **4 confirmed polluter→polluted pairs surfaced**:
        · `test_phase4_2_http_transport_smoke.py` → 3 polluted files
          (FTT-015..022 = 8 FTT IDs)
        · `test_phase_p5_10_audit_panel_direct_linkage.py` →
          `test_track_b_phase2_task_lifecycle.py` (FTT-023, **tiered**)
      **KEY**: one file is the polluter for 8 of 10 confirmed FTT IDs;
      that file is ALSO a deterministic regression itself.
      **2 holdouts** for full-(a) binary search:
        · `test_p_cleanup_c_help_tooltip_suppression.py` (FTT-010..012)
        · `test_track_b_phase_b5_g6_notes_autosave.py` (FTT-024..026)
      **1 intra-file cluster** for separate sprint:
        · `test_iter41_signal_actions_in_process.py` (FTT-004..009)
      All halt conditions clear; 0 locked-area polluters.
    - P5.7-PER-FILE-CAPTURE (scope cut 24→18); P5.7-CAPTURE-B-ATTEMPT-1
      (in-process broad-suite hung at 16%); P5.7-DIAG (initial diagnosis).

    *Unblock condition:* user picks fix scope: (a) single-file surgical
    on `test_phase4_2_http_transport_smoke.py` (closes 8 FTT IDs + own
    deterministic regression in 1 sprint); (b) all-4-pairs cleanup
    (closes 10 FTT IDs); (c) defer fix & run full-(a) binary search
    on the 2 holdouts first to see if they consolidate to the same
    polluter. Agent recommendation: **(c) first, then (b)**.
    Sprint memos: `sprints/P5_7_DIAG_test_pollution.md`,
    `sprints/P5_7_CAPTURE_B_ATTEMPT_1.md`,
    `sprints/P5_7_PER_FILE_CAPTURE.md`,
    `sprints/P5_7_BISECT.md`.

### P2 (logged proactively)

6. **Inline-blob sunset.** Once `jc_bug_analyze_upload_backfill.py
   --commit` runs in prod AND a 7-day soak passes with zero
   `data_b64`-touching reads logged, replace the `read_workbook_bytes`
   helper with a GridFS-only reader and drop the inline-decode arm.
   Add the `tests/invariants/test_no_inline_data_b64.py` guard at
   the same commit. *Unblock condition:* 7 days post-`--commit` +
   clean soak log.

7. **GridFS orphan-absence ratchet.** Assert every `fs.files` row
   has at least one matching metadata row in `workbook_blobs` /
   `analysis_blobs`. Currently impossible to violate (per-row atomic
   rollback covers this) but worth a guard at scale.
   *Unblock condition:* P2 dispatch when invariant team has 1-hour
   slot.

8. **Owner Digest weekly email · WITH GridFS-streamed workbook
   attachment inline.** Unifies the JC-TM Fan-Out email rails with
   the new GridFS-streaming Analyze pipes — same email service,
   same workbook storage backend, attached inline as a download
   link. Proposed by main agent in the Phase 3 close potential-
   improvement note; **logged here, NOT scoped, NOT shipped today.**
   *Unblock condition:* GP ships + Owner Digest scoping starts. Bring
   back as a proposed scoping question at that time, not before.

9. **Backend-tests.yml full-tree lane expansion (Phase 5.7).** Move
   from today's targeted-green scope to full-tree gating. Gated on
   Phase 5.6.1 → 5.6.4 GREEN + 7-day clean run. Per
   `sprints/PHASE_5_5_3_BROADER_DRIFT_TRIAGE.md`.

10. **Polymorphic-response-ratchet narrowing batch.** Currently
    🟡 `actual=43 > baseline=42`; `actual=50 markers > baseline=48`.
    Pre-existing drift across one Track-2 add + 2 markers from
    pre-this-dispatch work. Defer to Phase 5.6+ when the broader-
    suite drift is also being touched.

11. **Frontend below-HIGH yarn findings (40)** — listed in Wave 3.
    Mechanical cleanup. Per autonomy contract, picked up inside
    Wave 3 if scope is mechanical-only.

12. **CRA TS-resolver fix** — listed in Wave 3. Investigative
    first, then mechanical. Status: not started.

## Logged 2026-06-26 — AUTONOMOUS BACKLOG RUN wave 3 (in progress)

— Items here are landed by Wave 3 close. See the wave 3 handoff
note for the up-to-date status.

## Operating rules

- **Add to this file** the moment an item is deferred — don't let
  it become tribal knowledge in a sprint memo.
- **Each row carries an unblock condition.** "Defer indefinitely"
  is a valid condition only when there's no foreseeable trigger.
- **Promote up** when the unblock condition fires (move from P2 to
  P1, or from "deferred" to the active queue).
- **Cite this file** when a sprint memo opens with "the related
  deferred item from BACKLOG_SCHEDULE.md is …".
