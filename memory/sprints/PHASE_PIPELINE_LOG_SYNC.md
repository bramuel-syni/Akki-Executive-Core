# Phase Pipeline-Log-Sync — Sprint-Memo ↔ §9 Row Consistency CI Gate

**Ship date:** 2026-06-24
**Status:** ✅ SHIPPED (iter-1, single-dispatch)
**Dispatch:** Pipeline Init Follow-up — Verify Chat History + Add Pipeline-Log-Sync CI Gate
**Iteration budget:** 1/1 used.

---

## §1 — Compliance & Debt Snapshot

- **Zero product code touched.** Only `DEV_PIPELINE.md` edits + 1 new CI workflow + this memo.
- **Public ratchet held trivially:** `/api/* = cdcb23322bb82895`, `/v1/* = acc51822aa8818ae`, combined `ca9429c64e44570c`.
- **Honesty rail:** Part A revealed the §3.3 + §9 corrections from the prior dispatch were NEVER applied (context cut-off before save). Reported directly in §2 rather than pretending it was already correct.
- **Maintenance Protocol dogfooded:** this sprint memo + matching §9 row + the new CI gate together prove the loop.

---

## §2 — Part A: Verification of Chat history correction

### What I cat-ed before any edits

**§3.3 Track Chat (BEFORE)** — confirmed STALE (net-new B0 only; `Sprint memos: [none yet]`):

```
### 3.3 Track Chat — Consumer-Grade Chat UX (parallel product track)
- **Current state:** B0 queued behind TL1.2 close
- **Locked decisions:** ...
- **Sprint memos:** [none yet]
```

**§9 Phase History (BEFORE)** — confirmed STALE (zero prior Chat rows; table ended at Phase 4.1).

### Honest report

The prior dispatch's "Pipeline Init — CORRECTION on Track Chat" message was **NOT applied**. The previous turn investigated Chat history (found 5 prior Chat-related phases: Phase 5.10, Phase F, H2, H2.5, Phase 14) but ran out of context BEFORE writing the edits. The `finish` block ran with the file in its pre-correction state. This dispatch's Part A is the actual application.

### Lookups performed (re-grep evidence)

```bash
# Sprint memos with chat keywords
$ ls /app/memory/sprints/ | grep -i "chat\|fluency\|detection"
P5_10_chat_resilience.md
PHASE_14_CHAT_FLUENCY.md
PHASE_F_CHAT_BOUNDARY_STATE.md

# H2 / H2.5 — Shield Uniformity Audit + Streaming PII fix (Chat-coverage)
$ ls /app/memory/sprints/ | grep -E "^H2"
H2_5_FINAL_CLOSEOUT.md
H2_5_FOLLOWUP_CLOSEOUT.md
H2_5_SHIELD_MODE_CONTRACT.md
H2_5_STREAMING_PII_FIX_STATE.md
H2_SHIELD_UNIFORMITY_AUDIT.md
```

### Five prior Chat-related phases located + applied to §3.3 prior history

| Phase | Date | Sprint memo |
|---|---|---|
| 5.10 | 2026-02-23 (fork-resume) | `P5_10_chat_resilience.md` — production cancellation + audit-panel red error |
| F | 2026-05-21 | `PHASE_F_CHAT_BOUNDARY_STATE.md` — chrome refinement |
| H2 | 2026-05-24 (read-only) | `H2_SHIELD_UNIFORMITY_AUDIT.md` — Shield Uniformity Audit |
| H2.5 | 2026-05-24 | `H2_5_STREAMING_PII_FIX_STATE.md` — Streaming PII fix + audit-integrity |
| 14 | 2026-06-05 | `PHASE_14_CHAT_FLUENCY.md` — Chat Fluency & Detection Hardening |

### §3.3 (AFTER) — cat output

```
### 3.3 Track Chat — Consumer-Grade Chat UX
- **Status:** Currently **LIVE** (operational); consumer-grade redesign queued behind TL1.2 close.
- **Prior history:**
  - **Phase 5.10** (2026-02-23 fork-resume) — Chat resilience...
  - **Phase F** (2026-05-21) — Akki Chat boundary-removal pass...
  - **H2** (2026-05-24, read-only) — Shield Uniformity Audit...
  - **H2.5** (2026-05-24) — Streaming PII fix + audit-integrity invariant...
  - **Phase 14** (2026-06-05) — Chat Fluency & Detection Hardening...
- **Current operational state** (per `MODULE_PRODUCT_SPECS.md` §1 — Chat is module #1, not #2):
  - **UI routes**: `/app/chat` → `Chat.jsx`; `/app/chats/archived` → `ArchivedChats.jsx`; inline in `AppHome.jsx`.
  - **BE endpoints**: 13 routes under `/api/chats/*` + dual-mount `/v1/akki/chats/*`...
  - **Owning context**: Akki...
  - **Integrations**: `shield_invoke` + `issue_trust_receipt` + `get_shield_audit_by_chat`...
  - **Known debt**: 6 `/api/chats/*` endpoints still `Optional[Dict[str, Any]]`; streaming Shield UI parked...
- **Planned next track (consumer-grade redesign) — queued behind TL1.2:**
  - **Locked decisions:** ...
  - **Locked B0 scope:** ...
  - **Next dispatch:** Chat B0 (read-only pre-read).
  - **Then:** Chat B1+ sized at ~3-4 phases.
```

Re-triage correction: the prior dispatch incorrectly referenced "MODULE_PRODUCT_SPECS.md §2 (Chat module)". Chat is actually module **#1** per `MODULE_PRODUCT_SPECS.md` head. Corrected in §3.3.

### §9 (AFTER) — cat output

Added 5 prior Chat rows in chronological position (sort = reverse-chronological by ship date) — Phase 14 (2026-06-05) sits between Phase 4.1 and H2.5; H2.5 + H2 (2026-05-24); Phase F (2026-05-21); Phase 5.10 (2026-02-23) at the bottom. Sort-order note added at the top of §9.

---

## §3 — Part B: Pipeline-log-sync CI gate

### Workflow file

**Location:** `.github/workflows/pipeline-log-sync.yml`
**LOC:** ~210 (~80 header docstring + ~130 Python script body).

### Algorithm summary

1. Enumerate `memory/sprints/*.md`, excluding non-phase log files (CHUNK_*, BACKLOG*, BUG_*, *_LOG.md, *_DIAGNOSIS.md, *_AUDIT.md, etc. — full SKIP_PREFIXES / SKIP_SUFFIXES / SKIP_EXACT literals in the script).
2. Derive canonical phase identifier from each retained filename (`PHASE_5_5_2_*` → `5.5.2`; `H2_*` → `H2`; `PHASE_TL0_*` → `TL0`; `P5_10_*` → `5.10`; `PHASE_F_*` → `F`; known mappings table for irregulars like `PHASE_PIPELINE_LOG_SYNC` → `Pipeline-Log-Sync`).
3. Slice §9 Phase History from `DEV_PIPELINE.md`; collect `Phase` column values.
4. Assert each retained-memo identifier is present in §9. Surface ALL mismatches at once with `::error file=...` GitHub Actions annotations.

### Failure modes the gate catches
- New sprint memo lands; builder forgot to add §9 row.
- §9 row deleted/edited; sprint memo still present.
- Sprint memo renamed without §9 update.
- Sprint memo filename doesn't parse cleanly → fails with actionable diagnostic.

### Failure modes explicitly OUT of scope
- §9 row exists but Summary / Closed columns are stale (would require semantic equality logic — high false-positive risk).
- §4 Invariant Ladder / §5 Surface Ratchet drift (no canonical anchor to ratchet against).
- Sprint memo title canonicalisation drift (no source-of-truth schema).

### Clean-state smoke (local — simulating what CI will run)

Extracted the Python script body from `.github/workflows/pipeline-log-sync.yml` (the `<<'PYEOF' ... PYEOF` heredoc) to `/tmp/pipeline_log_sync_body.py`, dedented the 10-space indent, ran from `/app`:

```
$ python3 /tmp/pipeline_log_sync_body.py
pipeline-log-sync: OK. 93 retained sprint memo(s) checked: 25 have matching §9 rows, 68 are legacy-allowlisted (pre-2026-06-24 Maintenance Protocol baseline).
EXIT: 0
```

Breakdown:
- 93 total parseable phase memos in `memory/sprints/`.
- 25 have explicit §9 rows (the original 14 from the prior dispatch + the 5 Chat prior-history rows added in Part A + the new Pipeline-Log-Sync row + dedup counting per the §9 cell rather than per memo file — H2.5 has 4 sub-memos all → "H2.5" identifier).
- 68 fall through to the LEGACY_ALLOWLIST baseline (pre-Maintenance-Protocol phases that don't need §9 rows; the historical 0/1/2/3/4 series + Greek-letter Phase-1 sub-series + Phase 5.6-5.22 sub-series + Phase A/B/C/D/E/F.1/L bundle).

### Synthetic-regression smoke (local)

Removed the `| Pipeline-Log-Sync | ... |` row from §9 to simulate the failure mode:

```
$ python3 /tmp/pipeline_log_sync_body.py
::error file=memory/sprints/PHASE_PIPELINE_LOG_SYNC.md::pipeline-log-sync: sprint memo 'PHASE_PIPELINE_LOG_SYNC.md' (identifier 'Pipeline-Log-Sync') has no matching row in memory/DEV_PIPELINE.md §9 Phase History and is not in the LEGACY_ALLOWLIST. Add a row to §9 with the Phase column set to 'Pipeline-Log-Sync' per the Maintenance Protocol + sprints/README.md convention.
EXIT: 1
```

GitHub Actions `::error file=...::` annotation will surface directly on the offending sprint memo in the PR diff view — actionable for the reviewer + the builder.

Restored the row; clean-state re-run exits 0. Verified.

### Workflow header cross-references

Header docstring explicitly cites:
- `memory/DEV_PIPELINE.md` Maintenance Protocol (last section) — names this CI gate as the §4 + §5 + §9 update enforcement.
- `memory/sprints/README.md` — the 3-step sprint memo convention.

---

## §4 — Part C: §4 Invariant Ladder update

```
| CI gates | codemod-drift + dep-audit-strict + invariants.yml + backend-tests.yml (scoped) | ✅ |
| CI gates | pipeline-log-sync (sprint memo ↔ DEV_PIPELINE §9 row consistency) | ✅ |
```

New row added; cat-pasted in close report.

---

## §5 — Dogfood proof

The new gate's first dogfooded entry IS this sprint memo:
- New sprint memo: `memory/sprints/PHASE_PIPELINE_LOG_SYNC.md` (this file).
- New §9 row: `| Pipeline-Log-Sync | 2026-06-24 | Sprint-memo ↔ DEV_PIPELINE §9 row consistency CI gate; first dogfooded by this entry | sprints/PHASE_PIPELINE_LOG_SYNC.md |`.
- Local workflow run (clean state, evidence in §3 above): **EXIT 0** with `93 retained sprint memo(s) checked: 25 have matching §9 rows, 68 are legacy-allowlisted`.

If anyone deletes the §9 `Pipeline-Log-Sync` row, the workflow fails on its own sprint memo — exactly the desired self-defending behaviour (proven by §3's synthetic-regression run: **EXIT 1** with actionable diagnostic).

---

## §6 — Sprint memo pointer

This file: `/app/memory/sprints/PHASE_PIPELINE_LOG_SYNC.md`.

Cross-linked from:
- `DEV_PIPELINE.md` §9 Phase History (Pipeline-Log-Sync row).
- `.github/workflows/pipeline-log-sync.yml` header docstring (cross-reference block).

---

## §7 — Deviations log

**D1 — Sprint-memo filename irregulars.** The `KNOWN_MAPPINGS` dict in the workflow script names canonical identifiers for memos whose filename doesn't follow the digit-separator pattern (`PIPELINE_LOG_SYNC` → `Pipeline-Log-Sync`; `TL0_THINKLAB_PREREAD` → `TL0`). Future irregular memos must add a mapping here AND the §9 row simultaneously — flagged inline in the workflow header so the next dispatch sees the constraint.

**D2 — §9 row sort order.** The original §9 had no explicit sort-order note; the AFTER state adds one ("reverse chronological by ship date") at the top of §9, since the prior-Chat-row insertions surfaced the ambiguity (Phase 14 ships in 2026-06-05; Phase 4.1 has no ship date in MASTER_STATE; the relative order matters for QA review). Not a behaviour change to the gate — the gate only checks set membership of the Phase column, not order. Documented in §9 header for human readers.

**D3 — Prior dispatch's correction message was NOT applied.** Surfaced honestly in §2; the previous turn ran out of context after the investigation but before the file edits. This dispatch's Part A IS the actual fix.

**No other deviations.** No product code touched. No invariants touched outside the new pipeline-log-sync gate. No CI workflows touched except the one this dispatch authored.
