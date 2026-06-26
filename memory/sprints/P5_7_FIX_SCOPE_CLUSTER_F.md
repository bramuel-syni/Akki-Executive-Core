**Canonical Spec**: `/app/memory/sprints/JC_POLLUTION_B2_HALT.md` (B.2 HALT identified the systemic wrong-loop-binding anti-pattern across the 14 unconverted polluter files · this memo source-reads all 14 + groups them into sub-sprints · READ-ONLY · no test/product code mutations · HARD STOP at memo close)

# Sprint P5.7-FIX-SCOPE-CLUSTER-F — broad sync→async conversion scope memo

**Status**: SHIPPED (memo only) · HARD STOP at memo surface · AWAITING USER SUB-SPRINT DISPATCH
**Date**: 2026-06-26
**Predecessor**: `sprints/JC_POLLUTION_B2_HALT.md` (B.2 HALT surfaced the empirical mechanism — `event_loop_binding_leak_from_sync_run_in_polluter_files`); `sprints/JC_POLLUTION_CLUSTER_E_FIX.md` (mechanical pattern proven 9/9 GREEN on the first file)
**Discipline**: READ-ONLY contract honoured. 0 test/product/fixture/invariant files mutated. Pure source-read + grouping-design output.

---

## §0 — 14-file evidence table

Each file's `_run`-helper or `asyncio.run` call site captured file:line precisely. Mechanism class assigned per the B.2 HALT taxonomy:

- **M1**: `def _run(coro): return asyncio.get_event_loop().run_until_complete(coro)` helper + sync tests + Motor I/O via FastAPI middleware (`from core import db` + `AsyncClient`/`ASGITransport`) — Cluster-E's exact mechanical fix shape
- **M2**: `asyncio.run(...)` direct on pure-Python coroutines (no Motor I/O through FastAPI) — A+D-style policy mutation; different fix shape

| # | File | Helper line(s) | Sync tests | LOC | Motor I/O? | Class | Notes |
|---|---|---|---:|---:|:---:|:---:|---|
| 1 | `tests/test_phase_p2_a2_microsoft_pkce.py` | `_run` at 72-74 | 7 | 205 | yes | M1 | Microsoft OAuth PKCE flow |
| 2 | `tests/test_phase_p2_b1_security_headers.py` | `_run` at 30-31 | 5 | 122 | yes | M1 | Security-header middleware |
| 3 | `tests/test_phase_p2_b4_password_change.py` | `_run` at 34-35 | 4 | 172 | yes | M1 | Account password mutation |
| 4 | `tests/test_phase_p2_b6_admin_force_reset.py` | `_run` at 24-25 | 4 | 155 | yes | M1 | Admin-triggered password reset |
| 5 | `tests/test_phase_p2_d2_health_composite.py` | `_run` at 21-22 | 4 | 64 | yes | M1 | Health-composite endpoint |
| 6 | `tests/test_phase_p3_1_csrf.py` | `_run` at 21-22 | 7 | 161 | yes | M1 | CSRF token mint + verify |
| 7 | `tests/test_phase_p3_2_cookie_hardening.py` | `_run` at 25-26 | 2 | 84 | yes | M1 | Cookie attributes (Secure/HttpOnly/SameSite) |
| 8 | `tests/test_phase_p3_4_session_timeout.py` | `_run` at 25-26 | 5 | 140 | yes | M1 | Session timeout enforcement |
| 9 | `tests/test_phase_p5_5_session_reauth.py` | `_run` at 46-47 | 4 | 209 | yes | M1 | Re-auth ladder |
| 10 | `tests/test_phase_p5_7_5_bounce_webhook.py` | `_run` at 21-22 | 5 | 154 | yes | M1 | SendGrid bounce webhook |
| 11 | `tests/test_phase_p5_7_waitlist_reminder.py` | `_run` at 36-37 | 8 | 221 | yes | M1 | Waitlist reminder send path |
| 12 | `tests/test_phase_p5_8_inbox_migration.py` | `_run` at 40-41 | 7 | 199 | yes | M1 | Inbox migration script |
| 13 | `tests/test_phase_p5_9_admin_button_and_badge.py` | `_run` at 23-24 | 4 | 132 | yes | M1 | Admin UI gating |
| 14 | `tests/test_synisense_security.py` | `asyncio.run(...)` at 35 + 52 | 3 | 63 | **no** | **M2** | Pure-Python Synisense pipeline call |

**Totals**: 13 M1 files (66 sync tests, ~2018 LOC) + 1 M2 file (3 sync tests, 63 LOC) = **14 files, 69 sync tests**.

### §0.1 — Key structural insights

1. **Mechanism uniformity within M1**: every M1 file uses the EXACT same 2-line `_run` helper at the top of the file. Mechanical fix is identical to Cluster-E's: drop helper + `import asyncio` becomes unused (if no other use) + add `import pytest` + add `@pytest.mark.asyncio` decorators + convert `def` to `async def` + replace `_run(coro)` with `await coro`.

2. **M2 file is the only outlier**: `test_synisense_security.py` has zero `from core import db`, `AsyncClient`, or `ASGITransport` references — it's a 63-LOC pure-Python file calling `pipeline_run(...)` directly via `asyncio.run`. The wrong-loop-binding mechanism MIGHT NOT actually be its pollution shape; the actual mechanism could be A+D-style asyncio policy mutation. **Treat M2 as separate scope** — needs its own per-file investigation before fix-shape choice.

3. **No mixed patterns surfaced**: every polluter file has 0 `@pytest.mark.asyncio` markers — no half-converted files in the candidate set. Clean greenfield for the mechanical conversion.

4. **No file has size > 221 LOC**: the largest is 221 LOC (`test_phase_p5_7_waitlist_reminder.py`). Mechanical conversion across the largest is still tractable in a single sub-sprint.

5. **Sync test count per file ranges 2-8** with median ≈ 5. Even-distribution sub-sprints (2-3 files of ~10-15 tests each) are reachable.

### §0.2 — Locked-area scan across all 14 files

Per the user's HALT condition "If any of the 14 files reveals coupling to Shield / WS Generate Doc UI / Track-2 schema / Monitor pre-warmer in its production-code touches → HALT":

| File | Touches Shield? | WS Generate Doc UI? | Track-2 schema? | Monitor pre-warmer? |
|---|:---:|:---:|:---:|:---:|
| #1 microsoft_pkce | no | no | no | no |
| #2 security_headers | no | no | no | no |
| #3 password_change | no | no | no | no |
| #4 admin_force_reset | no | no | no | no |
| #5 health_composite | no | no | no | no |
| #6 csrf | no | no | no | no |
| #7 cookie_hardening | no | no | no | no |
| #8 session_timeout | no | no | no | no |
| #9 session_reauth | no | no | no | no |
| #10 bounce_webhook | no | no | no | no |
| #11 waitlist_reminder | no | no | no | no |
| #12 inbox_migration | no | no | no | no |
| #13 admin_button_and_badge | no | no | no | no |
| #14 synisense_security | **🟧 indirect** — calls `pipeline_run(...)` which is a Shield-routed pipeline | no | no | no |

**File #14 (`test_synisense_security.py`) exercises the Shield path** via its `pipeline_run` calls. The TEST exercises the locked area (legitimate test coverage of the Shield path is expected), but the proposed FIX (sync→async conversion or env+loop-policy restore) is purely test-side mechanical and doesn't touch the Shield source. Should still HALT-surface this for explicit user acknowledgement when its sub-sprint dispatches.

---

## §1 — Sub-sprint grouping proposal

Per user dispatch — group into 5-7 sub-sprints of 2-3 files each. Grouping criteria applied: (a) mechanism uniformity (M1 vs M2), (b) test count proximity, (c) risk class (Shield-exercising file isolated to own sub-sprint).

### §1.1 — Six sub-sprints (recommended)

| Sub-sprint | Files | Sync tests | Total LOC | Class | Risk |
|---|---|---:|---:|:---:|---|
| **F.1** — Auth-mutation P2 (paired heavy-touch admin state) | #3 password_change · #4 admin_force_reset | 8 | 327 | M1 | low (clean pattern, mutates admin account row) |
| **F.2** — Security-headers + Cookie-hardening (small + heavy-state-shaping) | #2 security_headers · #7 cookie_hardening · #5 health_composite | 11 | 270 | M1 | low (smallest LOC group, no admin row mutation) |
| **F.3** — CSRF + Session lifecycle (heavy CSRF/session surface area) | #6 csrf · #8 session_timeout · #9 session_reauth | 16 | 510 | M1 | medium (CSRF middleware coverage; needs careful proving slice for token round-trips) |
| **F.4** — Email surfaces (SendGrid bounce + waitlist) | #10 bounce_webhook · #11 waitlist_reminder | 13 | 375 | M1 | low-medium (SendGrid-disabled flag set by conftest; email-path smoke covered indirectly) |
| **F.5** — Inbox migration + Admin UI gating + OAuth | #12 inbox_migration · #13 admin_button_and_badge · #1 microsoft_pkce | 18 | 536 | M1 | medium (largest test-count group; OAuth flow has more conditional branches) |
| **F.6** — Synisense security (DIFFERENT mechanism class — isolated) | #14 synisense_security | 3 | 63 | **M2** | **medium-high** (Shield-path exercise + M2 means fix-shape decision needs per-file analysis; HALT-and-surface trigger pre-armed) |

**Total**: 14 files / 69 sync tests / 6 sub-sprints. Avg 2.3 files per sub-sprint.

### §1.2 — Why this grouping

- **F.1 pairs P2-B4 + P2-B6** — both mutate `accounts` rows for `admin@akki.ai`. Co-converting in one diff gives a single, reviewable PR for "admin-mutation-test hygiene".
- **F.2 keeps the small files together** — security_headers (5 tests, 122 LOC) + cookie_hardening (2 tests, 84 LOC) + health_composite (4 tests, 64 LOC). Smallest combined LOC. Good "warm-up" sub-sprint.
- **F.3 isolates the CSRF/session lifecycle trio** — these tests have the most middleware-touched paths (CSRF middleware, session middleware, auth dep). Proving slice needs care.
- **F.4 pairs the two SendGrid surfaces** — bounce_webhook + waitlist_reminder. Both use conftest's `COHORT_NOTIFY_DISABLED` flag; co-converting reduces risk of one diverging from the other's pattern.
- **F.5 groups the largest test counts** — microsoft_pkce (7), inbox_migration (7), admin_button_and_badge (4) = 18 tests. Largest sub-sprint by test count but still in the 2-3-file range.
- **F.6 isolates the M2 outlier** — `test_synisense_security.py` is structurally different. Forcing it into a multi-file sub-sprint would mix mechanism classes and dilute the proving slice's signal. Own sub-sprint with explicit HALT-trigger for the Shield-exercise check.

### §1.3 — Alternative groupings considered + rejected

- **5-sub-sprint version (3+3+3+3+2)**: would push sub-sprint sizes higher (3-file sprints have ~15-20 tests each); rejected because F.6 must stay isolated per mechanism class, leaving only 13 M1 files to spread across 4 sub-sprints — average 3.25 files/sprint, which exceeds the "2-3 file" guideline.
- **7-sub-sprint version (split F.5 in two)**: would isolate microsoft_pkce in its own sub-sprint; rejected because the 7-test file isn't structurally different from inbox_migration (7 tests) or P5_7_waitlist_reminder (8 tests). No risk-class differentiation to justify the split.

---

## §2 — Per-sub-sprint proving-slice design

Each sub-sprint will have its own proving slice. Common rows (4 + N where N = number of files in the sub-sprint):

| Row | Check |
|---|---|
| 1 | Sub-sprint's first file PASSES in isolation post-fix |
| 2 | Sub-sprint's second file (and third if applicable) PASSES in isolation post-fix |
| 3 + ... | Each file paired with the autosave file (`test_track_b_phase_b5_g6_notes_autosave.py`) — confirms the wrong-loop-binding is closed for the previously-confirmed B.2 pair |
| ... | Each file paired with the cluster-E-fixed audit-panel file as defensive (ensures we don't undo Cluster-E's closure) |
| Final-2 | Combined sub-sprint files + autosave paired-pytest — all PASS |
| Final-1 | Log scan: 0 occurrences of `Future attached to a different loop` across all paired runs |
| Final | Loop-binding sanity: post-sub-sprint, `asyncio.get_event_loop_policy().get_event_loop()` returns a non-closed loop |

**Per-sub-sprint slice target**: ≥ (N + 5) rows GREEN, where N is the file count in that sub-sprint.

### §2.1 — F.6 (M2) proving slice has additional rows

For `test_synisense_security.py`, the conversion may not be a clean sync→async pattern. Three options will be explored in the F.6 dispatch:

- **(a)** Convert tests to `@pytest.mark.asyncio + async def` and replace `asyncio.run(pipeline_run(...))` with `await pipeline_run(...)`. Same Cluster-E mechanical pattern. Likely works if `pipeline_run` is genuinely async.
- **(b)** Apply A+D-style env+loop-policy snapshot/restore around `asyncio.run` — keeps tests sync but neutralizes policy mutation.
- **(c)** If neither (a) nor (b) is viable (e.g., `pipeline_run` makes tight coupling to sync internals), park the file and flag for separate refactor.

F.6's slice will include extra rows for the M2-specific decision: (i) Shield-path exercise still returns the expected refusal/pass surface post-fix, (ii) env restoration if path (b) is chosen.

---

## §3 — Total LOC estimate per sub-sprint

| Sub-sprint | Mechanical conversion LOC | Proving slice LOC (NEW) | Sprint memo LOC |
|---|---:|---:|---:|
| F.1 | ~50 (8 tests × ~6 LOC delta) | ~150 | ~200 |
| F.2 | ~65 (11 tests) | ~170 | ~200 |
| F.3 | ~95 (16 tests) | ~200 | ~250 |
| F.4 | ~80 (13 tests) | ~180 | ~220 |
| F.5 | ~110 (18 tests) | ~220 | ~270 |
| F.6 | ~30 (3 tests, M2) | ~180 (more rows for Shield + M2 verification) | ~250 (mechanism decision rationale documented) |
| **Total Cluster-F** | **~430 LOC test-side conversion** | **~1100 LOC across 6 slices** | **~1390 LOC across 6 memos** |

These are estimates; actual delta per file is unknown until conversion is attempted (some tests may have implicit sync dependencies that need extra care).

---

## §4 — Latent-flake risk class (per user request)

Per dispatch:
> "Cluster-F closes FTT-024..026 + an unknown number of latent landmine flakes — surface latent-flake risk class in the memo"

**Latent flake mechanism**: any test file using `_run = asyncio.get_event_loop().run_until_complete(coro)` is a landmine. If a `@pytest.mark.asyncio` file is added to the suite alphabetically AFTER an unconverted sync polluter, the new file becomes flaky immediately. Cluster-F closes 14 such landmines.

**Currently-unsurfaced landmine candidates** (estimated count, NOT investigated in this memo):
- Any sync test file in `backend/tests/` not in the 14-file Cluster-F list that ALSO uses `_run` / `asyncio.run` / `run_until_complete` on Motor-touching coroutines.
- A quick grep across the test tree would reveal this; **deferring to a Cluster-F sub-sprint zero ("survey")** if user wants to know the true count before committing to F.1..F.6.

**Risk shape**:
- Each landmine is silent until a new `@pytest.mark.asyncio` file is added that runs alphabetically after it.
- Pre-A+D evidence: phase4_2's two leaks (env + asyncio.run policy) silently broke 8 unrelated tests. The wrong-loop-binding mechanism is the same shape, applied to ~13 polluter files.
- **Expected outcome of full Cluster-F**: removes the systemic anti-pattern from the codebase. Any future `@pytest.mark.asyncio` test that runs after these (now-converted) files won't trigger wrong-loop-binding.

**Recommended addition** (NOT required for sub-sprint dispatch): authorise an exhaustive grep-scan of the whole test tree to find any other landmines. Estimated ~10-30 min slice.

---

## §5 — Locked-area re-confirmation (per scope memo §6 discipline)

**Aggregate locked-area scan across all 14 files (per §0.2 table)**:
- 13 of 14 files: zero touches to any locked area (Shield · WS Generate Doc UI · Track-2 schema · Monitor pre-warmer)
- 1 of 14 files (#14 `test_synisense_security.py`): TEST exercises the Shield path via `pipeline_run` calls — this is legitimate test coverage; the proposed FIX is purely test-side mechanical. **F.6 dispatch will surface this explicitly per locked-area discipline.**

No production code touches required across all 6 sub-sprints. All fixes are test-side.

---

## §6 — HALT conditions per sub-sprint (pre-authorised)

For each sub-sprint:
1. If isolation regression (file fails in isolation post-conversion) → HALT
2. If proving slice <100% GREEN on its target row count → HALT
3. If any converted test has timing-dependent assertions that break under `@pytest.mark.asyncio` semantics → HALT, surface the timing dependency
4. If any sub-sprint reveals a mixed-async-pattern file (already had `@pytest.mark.asyncio` markers BEFORE conversion — i.e., the 14-file scan missed something) → HALT, surface

For F.6 specifically:
5. If `pipeline_run` turns out to not be async-callable directly → HALT, choose option (b) env+loop-policy restore OR option (c) park
6. If the Shield-path exercise's expected refusal/pass surface changes post-fix → HALT, the test semantics shifted

---

## §7 — Files produced by this scope memo

| Path | Status |
|---|---|
| `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md` | NEW — this memo (~400 lines · READ-ONLY) |
| `/app/memory/DEV_PIPELINE.md` | UPDATED — §9 row (per standing rule) |
| `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` | (potential future update) — could add a "Cluster-F polluters" entry summarising the 14 files; deferred to sub-sprint dispatches |

## §8 — Files NOT touched by this memo

- 0 product code mutated
- 0 test files mutated
- 0 fixture files mutated
- 0 invariant files mutated
- 0 proving-slice scripts authored (deferred to each sub-sprint)

---

## §9 — User-direction surface (next dispatch)

Six sub-sprints surfaced, sized 2-3 files each, each with own proving slice + HARD STOP. Dispatch order recommendation (smallest-risk first, largest-leverage last):

1. **F.2** (smallest LOC, low risk — security_headers + cookie_hardening + health_composite) — proves the mechanical pattern at scale (3 files vs Cluster-E's 1 file)
2. **F.1** (admin-mutation pair — password_change + admin_force_reset)
3. **F.4** (SendGrid surfaces — bounce_webhook + waitlist_reminder)
4. **F.5** (largest test-count group — microsoft_pkce + inbox_migration + admin_button_and_badge)
5. **F.3** (CSRF/session lifecycle — most middleware-touched; needs careful proving slice)
6. **F.6** (M2 outlier — Synisense security; explicit HALT pre-armed)

Or alternatively, dispatch all 6 in parallel — they touch DIFFERENT files, no collision. Sequencing-vs-parallel is a tradeoff between sequential evidence accumulation (each sub-sprint informs the next) and time-to-close (all 6 at once is fastest).

After Cluster-F closes (all 6 sub-sprints), the post-Cluster-F state:
- FTT-024..026 CLOSED via removed source of pollution
- Systemic wrong-loop-binding anti-pattern removed from 14 files
- 12 → 9 remaining FTT IDs in active tracker (Cluster C still parked: FTT-004..009 intra-file fixture refactor)
