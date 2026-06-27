**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1 + §6` (Cluster-F sub-sprint F.6 = synisense_security — 1 M2 outlier file · Shield-adjacency HALT pre-armed per scope memo §6 · TWO-DISPATCH approach confirmed by user · this advance scan memo source-reads the 1 file to verify or refine the risk classification before dispatching the mechanical conversion · READ-ONLY · 0 LOC mutated · HARD STOP at memo surface)

# Sprint P5.7-FIX-SCOPE-CLUSTER-F6-ADVANCE — F.6 structural-shape advance scan (Shield-adjacency case)

**Status**: SHIPPED (memo only) · READ-ONLY · HARD STOP at memo surface · AWAITING USER F.6 FIX-SPRINT DISPATCH
**Date**: 2026-06-27
**Predecessor**: `sprints/P5_7_FIX_SCOPE_CLUSTER_F3_ADVANCE.md` (immediate predecessor — first use of the advance-scan model; LOW-risk reclassification proven correct under F.3 fix sprint); `sprints/JC_POLLUTION_CLUSTER_F3_FIX.md` (most recent fix sprint, validates 5-sub-sprint pattern uniformity); `sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §6` (Shield-adjacency HALT pre-arming)
**Discipline**: READ-ONLY contract honoured · 0 LOC mutated · pure source-read + risk-classification output · DEV_PIPELINE.md §9 row added BEFORE this memo (F.3-ADVANCE slip lesson applied)

---

## §0 — Filename verification (per F.1/F.5/F.3 audit-trail discipline)

User dispatch referenced `tests/test_synisense_security.py`. On-disk filename is `tests/test_synisense_security.py`. **EXACT MATCH** — F.6 is the FIRST sub-sprint where the user's filename was exact on first attempt (F.1 corrected `b6_d1`, F.5 corrected `p4_3/p2_c1/p2_c2`, F.3 corrected `p3_5_session_reauth` → `p5_5_session_reauth`). No correction needed.

---

## §1 — File evidence

### §1.1 — `tests/test_synisense_security.py` — 3 sync tests / 64 LOC

| # | Test | LOC | Async surface? | Notes |
|---:|---|---:|:---:|---|
| 1 | `test_shield_reversible_produces_shield_map_id_only` | 30-47 | YES (M2) | `asyncio.run(pipeline_run(... mode="shield_reversible" ...))` at line 35; asserts on output dict shape + absence of leaky keys |
| 2 | `test_redact_mode_never_creates_shield_map` | 50-56 | YES (M2) | `asyncio.run(pipeline_run(... mode="redact" ...))` at line 52; asserts `shield_map_id is None` |
| 3 | `test_unregistered_version_blocks_decryption` | 59-63 | NO | Pure-Python — directly calls `enc.new_record_envelope` + `enc.open_record_envelope`; raises `enc.KeyVersionUnknown`. **STAYS SYNC** per Cluster-F.2 heuristic |

**Autouse fixture `_prep_keys` (lines 20-27)**:
- SYNC fixture
- Mutates `os.environ`: sets fresh `SYNISENSE_MASTER_KEY` (random hex), pops `SYNISENSE_ALLOW_INSECURE`, pops `AKKI_ENV`
- Calls `enc.init_keys()` per test
- **Loop-agnostic** — no asyncio touch; conversion does NOT change this fixture
- Preservable verbatim under sync→async test conversion

**Imports**:
- `services.synisense.run` (Shield API entry point — pure `async def pipeline_run(...)`)
- `services.synisense.encryption` (envelope encrypt/decrypt — pure-Python)

**Pattern classification**: this file is the SINGLE M2 outlier in Cluster-F. Unlike M1 files which have a module-level `def _run(coro): return asyncio.get_event_loop().run_until_complete(coro)` helper, this file calls `asyncio.run(...)` directly inline within 2 sync test bodies.

### §1.2 — Totals

| | Sync tests | Async-convert | Stay sync | LOC total |
|---|---:|---:|---:|---:|
| synisense_security | 3 | 2 | 1 | 64 |
| **F.6 total** | **3** | **2** | **1** | **64** |

By far the smallest Cluster-F sub-sprint by both file count (1) and LOC (64) and test count (3). The M2 conversion ratio is identical to M1 conversions across F.1/F.2/F.4/F.5/F.3 (always preserving pure-Python tests as sync).

---

## §2 — Shield-adjacency audit (load-bearing per dispatch directive)

This is THE critical audit per scope memo §6 ("Shield-adjacency HALT pre-armed"). User explicitly flagged "F.6 has the most pre-armed HALT discipline of any Cluster-F sub-sprint."

### §2.1 — What the tests actually verify

**Test 1 — `test_shield_reversible_produces_shield_map_id_only`** (lines 30-47):
Asserts on the API CONTRACT that Shield doesn't leak:
- `out["redacted_text"] != text` — the response IS redacted (Shield/redact path engaged)
- `out["spans"]` — spans are returned
- `isinstance(out["shield_map_id"], (str, type(None)))` — opaque id, not the cleartext map
- `for k in ("shield_map", "mapping", "originals", "envelope"): assert k not in out` — explicit anti-leak assertion list

**Test 2 — `test_redact_mode_never_creates_shield_map`** (lines 50-56):
Asserts the anti-engagement contract:
- `out["shield_map_id"] is None` — redact mode (non-Shield) does NOT engage Shield

**Test 3 — `test_unregistered_version_blocks_decryption`** (lines 59-63):
Pure-Python encryption envelope test (no Shield path touch):
- Builds envelope with `key_version=42` (unregistered)
- Asserts `enc.open_record_envelope(env)` raises `enc.KeyVersionUnknown`

### §2.2 — Production-code touch surface

| Surface | Touched in tests? | Touched by conversion? |
|---|:---:|:---:|
| `services.synisense.run.pipeline_run` (Shield API entry) | YES — both M2 tests call it | NO — same call, different invocation (`await` vs `asyncio.run`) |
| `services.synisense.run.*` (Shield internals: redact_engine, shield_map_store, ...) | **NO** — tests stop at the API surface | **NO** |
| `services.synisense.encryption` (envelope encrypt/decrypt) | YES — test 3 imports + calls | NO — test 3 STAYS SYNC, no change |
| Shield middleware (if any) | NO | NO |
| WS Generate Doc UI | NO | NO |
| Track-2 schema | NO | NO |
| Monitor pre-warmer | NO | NO |

**Verdict**: the conversion does NOT change Shield CODE. It does NOT change WHAT gets tested. It changes ONLY the HARNESS that invokes the pure `async def pipeline_run(...)` coroutine. The Shield CONTRACT (no leaky keys, mode-specific engagement) is preserved verbatim by the conversion.

### §2.3 — `asyncio.run` semantics audit (the M2-specific question)

The user's stated HALT condition: "**`asyncio.run` semantics matter to the test (event-loop isolation per call) → HALT**." This requires explicit per-test analysis.

`asyncio.run(coro)` does three things `await coro` does not:
1. **Creates a new event loop** (fresh selector loop per call)
2. **Closes async generators** at exit (via `loop.shutdown_asyncgens()`)
3. **Runs the loop's shutdown handlers** (signal handlers, weakref cleanups)

Do any of the 2 F.6 M2 tests rely on these semantics?

- **Test 1**: asserts ONLY on `out["redacted_text"]`, `out["spans"]`, `out["shield_map_id"]`, and absence of leaky keys in the response dict. These are all coroutine RETURN VALUE assertions. The test does NOT:
  - Inspect the event loop after the call returns
  - Register signal handlers or weakrefs
  - Use async generators that depend on `shutdown_asyncgens()`
  - Reuse state across multiple `asyncio.run` calls within the same test body

- **Test 2**: identical shape — single `asyncio.run` call, single return-value assertion (`shield_map_id is None`). Same analysis as Test 1.

- **`pipeline_run` itself** (production code, NOT in scope of touch): is a pure `async def` function from `services.synisense.run`. It does not manage event loops or register loop-scoped state. (Verified by import + reading the module docstring: "async pipeline entry point for redact/shield_reversible modes".)

**Verdict**: NEITHER test relies on `asyncio.run` semantics that don't transfer to `await` under a session-scoped event loop. The conversion is mechanically safe.

### §2.4 — `_prep_keys` autouse fixture interaction with async conversion

The autouse fixture sets `os.environ["SYNISENSE_MASTER_KEY"] = secrets.token_hex(32)` and calls `enc.init_keys()` BEFORE each test. Under the conversion:

- Fixture stays SYNC (no asyncio touch in its body)
- Fixture runs in pytest-asyncio's plugin pre-test phase — works identically for `@pytest.mark.asyncio` tests as for sync tests
- `enc.init_keys()` reads `os.environ` and populates an in-memory key registry — pure-Python, no loop awareness
- The fresh master key per test means cross-test contamination is impossible regardless of event-loop identity

The fixture is safe under conversion.

---

## §3 — Risk classification

| Aspect | Scope-memo signal | Advance-scan verdict | Rationale |
|---|---|---|---|
| File coupling to Shield internals | HIGH (Shield-adjacency HALT pre-armed) | **LOW** | Tests stop at the `pipeline_run` API surface; Shield internals are not exercised |
| Async-conversion mechanics | UNKNOWN (M2 outlier, first sub-sprint of this pattern) | **LOW** | Both M2 sites have return-value-only assertions; no `asyncio.run` semantics dependency |
| Test-shape changes under conversion | UNKNOWN | **NONE** | Conversion replaces `asyncio.run(coro)` with `await coro`; assertion shape preserved verbatim |
| Production-code dependency | HALT pre-armed | **NONE** | 0 production-code touches required |

**Overall F.6 verdict**: LOW risk. Same as F.5/F.3 — the M2 conversion is mechanically equivalent to M1 for tests that only assert on coroutine return values.

**Recommendation**: dispatch F.6 as a single sub-sprint (NOT split). Apply the M2 mechanical conversion: `asyncio.run(coro)` → `await coro` with `@pytest.mark.asyncio + async def` decorator. Preserve the autouse `_prep_keys` fixture verbatim. Preserve `test_unregistered_version_blocks_decryption` as sync (pure-Python).

---

## §4 — Proving slice design recommendation

F.6 is single-file and only has 3 tests; the standard 13-row template would be over-broad. **Recommended 11-row template**:

| Row | Check |
|---|---|
| 1 | `tests/test_synisense_security.py` in isolation post-fix → 3/3 PASS |
| 2 | F.6 file + autosave (B.2 polluter pair) → 6/6 PASS |
| 3 | F.6 file + phase4_2 (A+D defensive — confirms Cluster-A closure intact) → all PASS |
| 4 | F.6 file + p5_10 (Cluster-E defensive — confirms Cluster-E closure intact) → all PASS |
| 5 | F.6 file + microsoft_pkce (F.5 defensive — confirms F.5 closure intact) → all PASS |
| 6 | F.6 file + csrf (F.3 defensive — confirms F.3 closure intact) → all PASS |
| 7 | Combined F.6 + autosave + ALL prior cluster-fixed files (broad sweep) → all PASS |
| 8 | Log scan: zero `Future attached to a different loop` across Row 7's full stdout |
| 9 | Source-assertion: zero `asyncio.run(` calls inside `test_*` function bodies in the F.6 file (M2-specific shape; NOT looking for `_run` helper since F.6 was M2 not M1) |
| 10 | Bespoke-run invariant PASSES with `M2_CEILING=26` (closure-schedule lock validated; 28 → 26 ratchet) |
| 11 | **Shield-contract regression**: re-read the converted file and assert that BOTH M2-converted tests STILL invoke `pipeline_run` with the same modes (`mode="shield_reversible"` + `mode="redact"`) AND STILL assert on the same leaky-key absence set (`shield_map`, `mapping`, `originals`, `envelope`) — this is an AST-level check that the conversion preserved the Shield-contract assertions verbatim |

Row 11 is the F.6-specific addition. It catches any drift in the conversion that might accidentally relax the Shield-contract assertions (e.g., dropping one of the leaky-key checks). This is the discipline-pay for Shield-adjacency: even though the analysis says the conversion is safe, the slice explicitly verifies the contract didn't drift.

---

## §5 — Closure-schedule lock update post-F.6

When F.6 ships:
- Remove 2 M2 entries from `bespoke_run_helper_grandfathered.yml`:
  - `test_synisense_security.py :: test_shield_reversible_produces_shield_map_id_only :: lineno 35`
  - `test_synisense_security.py :: test_redact_mode_never_creates_shield_map :: lineno 52`
- Ratchet `M2_CEILING` from `28` → `26` in `test_no_bespoke_run_helper.py`
- `M1_CEILING` UNCHANGED at `5` (F.6 has no M1 entries to close)
- Post-F.6 state: 5 M1 entries remaining (all `Cluster-G (post-F)`) + 26 M2 entries remaining (25 `Cluster-G (post-F)` + 1 A+D-preserved)
- **FTT-024..026 AUTO-CLOSE** — autosave's polluter set becomes empty (all 14 Cluster-F polluters converted)

---

## §6 — HALT conditions reviewed (pre-armed for the F.6 fix sprint)

Per user dispatch:

1. ✅ **Filename verification** — exact match, no correction needed (§0)
2. ✅ **Direct Shield path calls in test body** — NONE; tests stop at `pipeline_run` API surface (§2.2)
3. ✅ **Conversion requires changing Shield invocation** — NO; `pipeline_run` is called identically (just `await` vs `asyncio.run`) (§2.2)
4. ✅ **`asyncio.run` semantics matter to tests** — NO; both M2 tests have return-value-only assertions (§2.3)
5. ✅ **Production-code dependency emerges** — NO; 0 production touches required (§2.2)
6. ✅ **M2 outlier reveals 2 distinct sub-patterns** — NO; both M2 sites have identical shape (`asyncio.run(pipeline_run(...))` with return-value-only assertions) (§1)

**NO HALT conditions tripped.** F.6 fix sprint is dispatch-ready.

---

## §7 — Recommended F.6 fix sprint shape (when user dispatches)

- **Files**: `tests/test_synisense_security.py` (1 file; LOW risk)
- **Conversion count**: 2 async + 1 sync
- **Proving slice**: 11-row template (§4) — includes Row 11 Shield-contract regression check (F.6-specific)
- **Closure-schedule lock**: remove 2 M2 entries from YAML, ratchet `M2_CEILING` 28 → 26
- **Locked-area**: clear
- **HALT conditions**: 6/6 pre-armed conditions clean
- **Time impact**: smallest sub-sprint of Cluster-F (3 tests / 64 LOC); proving-slice runtime ~30-45 seconds total

When user dispatches the F.6 fix sprint, I'll apply the mechanical M2 conversion as described in §1, ship the 11-row slice as described in §4, and update the closure-schedule lock as described in §5. Standing rules unchanged.

---

## §8 — Discipline notes

- **Scope honoured**: READ-ONLY contract — 0 LOC mutated across the repo.
- **No testing subagent used** (per banned-list rule).
- **Locked-area scan clean** (§2.2).
- **Filename audit-trail discipline applied** (§0) — 0 corrections (first time user's filename was exact).
- **Risk classification refined** (§3) — scope memo's "high risk / HALT pre-armed" → advance scan's "LOW" with rationale.
- **Shield-adjacency surfaced as load-bearing**: §2 documents exactly what the tests touch + what the conversion changes. The Shield-contract regression row (§4 Row 11) is the discipline-pay even though the analysis is clear.
- **F.3-ADVANCE slip lesson applied**: DEV_PIPELINE.md §9 row added BEFORE this memo authored.

---

## §9 — User-direction surface (HARD STOP per dispatch)

F.6 advance scan complete. F.6 fix sprint is **dispatch-ready**.

When user dispatches:
- **Files**: 1 (synisense_security · 3 tests · 64 LOC)
- **Conversion**: 2 async + 1 sync
- **Proving slice**: 11 rows including Shield-contract regression at Row 11
- **Closure-schedule lock**: remove 2 M2 entries + ratchet M2_CEILING 28 → 26
- **Post-F.6**: FTT-024..026 auto-close (autosave polluter set empty)

After F.6 fix sprint closes: Cluster-F arc complete (14/14 polluters converted) → Cluster-F retrospective memo (user-approved, ~150 LOC pure narrative) → Cluster-G READ-ONLY scope memo → Cluster-G sub-sprints → Cluster-C intra-file refactor.

Awaiting next dispatch from user. Standing rules unchanged.

---

## §10 — Time-gate status at memo close

`Sat Jun 27 08:51:48 UTC 2026` at dispatch start. Window opens at `Sat Jun 27 09:12:00 UTC` — **~20 minutes from this surface**. Steps 2 + 3 did NOT auto-fire during this advance-scan dispatch (the window had not crossed at start). The user's standing pre-authorization remains active for the next work cycle.
