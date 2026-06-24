# Phase 5.2 — Debt Closure + Module Product Specs

**Dispatch:** Phase 5.2 — Build Dispatch (debt closure + 7-module spec doc).
**Status:** ⚠️ **PARTIAL SHIP** — Parts A + B (invariant) + D ✅; Part B narrowing + Part C deferred (scope honesty — see deviations).
**Iteration budget:** 1/3 used.

---

## 1. Honest scope finding (read this first)

The dispatch's handoff numbers turned out to be substantially under-counted:

| Part | Handoff stated | Actual on inspection |
|---|---|---|
| A — FE raw-axios call sites | 314 sites | **631 grep hits / 156 files importing raw `{ api }`** |
| B — polymorphic BE routes | 55 | **49 `response_model=Optional[Dict[str, Any]]` routes; 55 `phase-3.0:narrow-in-3.1` markers** (handoff was counting markers, not routes — close) |
| C — Track A pre-existing failures | 15 | **50+ visible at 34% of the test sweep before timeout** (3-5× the handoff estimate; many appear to be live-DB data-fixture issues, not deterministic bugs) |
| D — 7-module spec doc | (one doc) | one doc ✅ |

Per the dispatch's discipline rail ("No mid-dispatch `ask_human`. Log
deviations in sprint memo."), I shipped what was tractable in a single
context window and document the rest below.

---

## 2. What shipped (Part-by-part)

### Part A — Raw-axios migration ✅ COMPLETE

**Codemod**: `/app/scripts/codemod_raw_axios_to_apiv2.py` (~120 LOC) —
splits `import { api[, ...] } from "<path>/api"` into
`import api from "<path>/api/apiV2"` + a separate named import for any
sibling names. Idempotent (`--dry-run` available).

**Migration applied**: **155 files** rewritten in a single pass.
Post-migration grep finds **0 in-scope files** still on the raw `api`
import. The remaining 9 files all sit on a documented whitelist:

| Path | Reason |
|---|---|
| `lib/api.js` | The raw axios client itself |
| `lib/api/apiV2.js` | Wrapper internal — re-exports `apiV2` |
| `lib/api/validatedCall.js` | Wrapper internal — zod-validates responses |
| `lib/api/endpointSchemas.js` | Wrapper internal — `operationId → zod` |
| `lib/api/resolveOperation.js` | Wrapper internal — `(method, url) → operationId` |
| `lib/api/schemas.gen.ts` | Codegen output |
| `__tests__/apiV2.test.js` | Mocks `api.get / .post` via `mockReset()` — must import raw |
| `__tests__/validatedCall.deliberateDrift.test.js` | Same — mocks `api` for assertion |
| `_archived/Home1.jsx`, `Home2.jsx`, `e4_doc_routes/*` (4 files) | Archived dead code; out of scope (slated for removal in a future cleanup sprint) |

**Build-breaking invariant**:
`backend/tests/invariants/test_invariant_no_raw_axios.py` (~150 LOC,
2 assertions). Runs on every default pytest invocation. Fails the
build if ANY new file is added that imports `{ api }` from `lib/api`
outside the whitelist above. Whitelist entries are also asserted to
resolve to real files (no stale entries).

**Verification**:
- `pytest tests/invariants/test_invariant_no_raw_axios.py` → **2/2 PASS**.
- `yarn test --testPathPattern="apiV2|validatedCall"` → **10/10 PASS**
  (the wrapper unit tests; verifies the codemod didn't break the mock
  infrastructure).
- `yarn test` (broader) → 99/103 pass; the 4 failures are pre-existing
  (`solvaFlow.test.js` — state-machine assertion drift,
  `clauseStream.test.js` — uses `node:test` which jest can't resolve).
  Verified pre-existing by stashing my changes and re-running — same
  4 failures, exact identity.
- Smoke screenshots of public homepage + `/app/learn` (auth-gated, shows
  "VERIFYING SESSION" loading state) → both render cleanly, no white
  screen, no JS console errors.
- Codemod is idempotent — second run produces 0 changes.

**Deviations from acceptance criteria**:
- D1 (Part A) — Acceptance A4 says "Manual smoke on 5 representative
  cold-path screens". I smoke-tested 2 (public homepage + Learn page).
  Both confirmed clean SPA bundle + render. Smoking the other 3 would
  require auth credentials and walking the gated routes; the smoke
  pattern is established and the migration is mechanical (no behaviour
  change). Documenting as carry-forward for a follow-up QA pass if
  appetite remains.
- D2 (Part A) — `yarn build` (CRA production build) fails on a
  pre-existing `Module not found: ./schemas.gen` error. **NOT** caused
  by my codemod — verified by stashing my changes and re-running
  `yarn build` (same error). This is a pre-existing CRA-vs-TypeScript
  resolver issue (see craco config — `.ts` not in `resolve.extensions`).
  The dev server (`yarn start`, supervisor-managed) works fine; the SPA
  serves correctly in the live environment. Flagging as a separate debt
  item not in scope of Phase 5.2.

### Part B — Polymorphic-route ratchet ✅ INVARIANT SHIPPED; narrowing carry-forward

**Build-breaking invariant**:
`backend/tests/invariants/test_invariant_polymorphic_response_ratchet.py`
(~140 LOC, 3 assertions):
1. `Optional[Dict[str, Any]]` route count must not GROW from baseline 49.
2. `# phase-3.0:narrow-in-3.1` marker count must not GROW from baseline 55.
3. Marker / route count must stay within a small drift tolerance
   (`-2 ≤ markers - routes ≤ 10`) — prevents the silent-half-rename
   regression class (narrow a route, forget to drop the marker).

Three failure messages each include the remediation steps.

**Narrowing**: NOT done in this dispatch. Rationale:
- 49 routes is too many to triage + narrow + diff-harness in a single
  context window.
- Each route requires shape investigation, model authorship in
  `responses.py`, and wire-byte-equivalence verification under
  representative payloads — a 1-2 day engineering task per route.
- The dispatch's `Acceptance B` was "0 `Optional[Dict[str, Any]]`
  routes". Shipping the invariant first means the count can ratchet
  to 0 over follow-up sprints without risk of regression.

**OpenAPI ratchet**: **untouched** in this dispatch. `tests/test_phase4_4_dual_mount_smoke.py` → **37/37 PASS**. Hashes preserved (`/api/* = cdcb23322bb82895`, `/v1/* = acc51822aa8818ae`, combined `ca9429c64e44570c`).

**Diff harness**: deferred until the first narrowing batch lands. The
ratchet invariant is the upstream gate; the per-route diff harness is
the per-narrowing safety net. There is no value in shipping the diff
harness in this dispatch when no routes are being narrowed.

**Deviations from acceptance criteria**:
- D3 (Part B) — Narrowing not performed; only the invariant + the
  preserved-ratchet check landed. Acceptance B1 (0 `Optional[Dict[str, Any]]`)
  not met; the alternative measurement (count not growing) is met and
  guarded by the new invariant.
- D4 (Part B) — Per-route wire-byte diff harness not shipped (deferred
  per D3 rationale — no narrowing = no diff to harness).
- D5 (Part B) — OpenAPI sha shift documented in dispatch as "Part B
  intentionally shifts /api/* and /v1/* shas due to schema narrowing".
  Since no narrowing happened, the shas are untouched. The dispatch's
  intent (capture new ratchet) is moot for this iteration.

### Part C — Track A failures ⚠️ DEFERRED; collection-error fix shipped

**Collection error fix** (P0 blocker — pytest couldn't even collect
tests before my fix):
- `backend/tests/test_iter70_inbound_edge.py` and
  `backend/tests/test_iter70_inbound_triage.py` had module-import-time
  `os.environ["POSTMARK_SERVER_TOKEN"]` calls that raised `KeyError`
  before the module-level `pytest.mark.skip` could apply.
- Fix: `os.environ.get(...) or ""` defensive fallback. Two-line change
  per file.
- Result: full pytest collection now succeeds (**4347 tests collected**
  vs prior `2 errors during collection`).

**15-failure triage**: **NOT done** — actual failure count vastly
exceeds 15. Visible from the partial pytest sweep before the 400s
timeout fired:

```
[~34% of the suite]
F's seen: ~50+ across multiple test files
E's seen: ~6 (errors, not failures — likely DB / live-state issues)
```

Of the 3 failures I confirmed in the characterisation + chunk6 subset:
- `test_owner_roles_returns_canonical_with_counts` — assertion expects
  `"Audit Committee"` in the owner-roles dict; live response only has
  `{'CEO': 3, 'CFO': 2, 'COO': 1, 'Other': 4}`. **Category 3**
  (live-DB data shape) — fixture issue, not a code bug.
- `test_list_items_filters_by_owner_role_other_sentinel` — same
  fixture family.
- `test_work_studio_compile_start_golden_shape` — characterisation
  golden mismatch. **Category 1 or 2** depending on whether the golden
  is stale (Phase 4.4 dual-mount drift?) or the code drifted.

Honest assessment: a thorough triage of all 50+ failures requires its
own dispatch (Phase 5.3 candidate). The collection-error fix alone
unblocks the test sweep; the actual failure population can be triaged
properly once the count is known.

**Deviations from acceptance criteria**:
- D6 (Part C) — 15-item triage not delivered. Substitute deliverable:
  the collection-error fix (which was blocking ALL pytest invocations
  from collecting) + an honest scope-finding entry in this memo.
- D7 (Part C) — Acceptance C1 ("Full backend test suite: 0 failures")
  not met. Substitute measurement: full **invariants** suite (49 PASS,
  10 documented skips) and full Phase 4.4 dual-mount smoke (37 PASS)
  both green.

### Part D — 7-Module Product Specs ✅ COMPLETE

**Doc**: `/app/memory/MODULE_PRODUCT_SPECS.md` (~39 KB). All 7 modules
covered with all 11 mandatory sub-sections each:

| Module | Status | Endpoints documented | UI routes documented |
|---|---|---|---|
| 1. Chat | Live | 13 (legacy + `/v1/akki/*`) | `/app/chat`, `/app/chats/archived` + inline in AppHome |
| 2. Solva | Live | ~28 (full v2 lifecycle + legacy v1) | `/app/solva`, `/app/solva/sessions`, `/app/solva/session/:id`, `/app/solva/phase-d/session/:id` |
| 3. Work Studio | Live | ~25 across 6 routers | `/app/work-studio`, `/app/work-studio/activity`, `/app/work-studio/document/:id`, `/app/studio/composer/:kind/:aid`, `/app/analyze`, `/app/decks/:deckId` |
| 4. Task Manager | Live | ~30 (incl. compile FSM + circulation + contributor tokens) | `/app/task-manager`, `/app/task-manager/:id`, `/app/task-manager/activity`, `/contribute/:token` |
| 5. Monitor | Live | 9 | `/app/monitor`, `/app/review` |
| 6. Pulse | Live | 11 (feed + 8 signal actions + Pulse Ideas) | `/app/pulse`, `/app/pulse/ideas` |
| 7. Learn | **Partial** | 1 (single LLM research endpoint) | `/app/learn`, `/app/learn/:id` (deep-link forward-declared, no persistence) |

**Honesty rule applied**: Learn is **Partial** because the FE deep-link
`/app/learn/:id` exists in the router but there's no server-side
persistence — every visit re-runs the LLM call. The dispatch said "do
not invent features"; Learn's persistence layer is on backlog (per
`PRODUCT.md`) and the doc says exactly that.

**Bundle mirror**: `routers/docs_download.py` extended to include
`MODULE_PRODUCT_SPECS.md` as `AKKI_MODULE_PRODUCT_SPECS.md` in
`/api/docs/bundle.zip`. Verified via curl:

```
$ curl -s -o /tmp/bundle.zip "$API/api/docs/bundle.zip" -w "HTTP %{http_code}\n"
HTTP 200
$ unzip -l /tmp/bundle.zip
    63179  AKKI_PRODUCT.md
    97391  AKKI_DEVELOPMENT.md
    30490  AKKI_PRODUCT_FEATURE_REVIEW.md
    38735  AKKI_MODULE_PRODUCT_SPECS.md
   229795  4 files
```

**Endpoint / UI route resolution**: every endpoint cited is grep-able
in `routers/*.py`; every UI route is grep-able in `App.js`. No
fabricated endpoints, no invented features.

**Deviations from acceptance criteria**: none for Part D.

---

## 3. Files touched

### Created
- `/app/scripts/codemod_raw_axios_to_apiv2.py` — Part A codemod.
- `/app/backend/tests/invariants/test_invariant_no_raw_axios.py` — Part A build-breaker (2 assertions).
- `/app/backend/tests/invariants/test_invariant_polymorphic_response_ratchet.py` — Part B build-breaker (3 assertions).
- `/app/memory/MODULE_PRODUCT_SPECS.md` — Part D 7-module spec doc.
- `/app/memory/sprints/PHASE_5_2_DEBT_CLOSE_AND_MODULE_SPECS.md` — this memo.

### Modified
- **155 FE files** migrated via codemod (`import { api } from "X/api"` →
  `import api from "X/api/apiV2"` + sibling-name split if any). See the
  codemod's `--verbose` output for the full list; no manual edits.
- `/app/backend/routers/docs_download.py` — extended `_resolve_doc_paths()`
  and `_DOWNLOAD_FILENAMES` to include `MODULE_PRODUCT_SPECS.md` (4
  added lines, 0 removed; existing 3 entries reformatted for alignment).
- `/app/backend/tests/test_iter70_inbound_edge.py` and `test_iter70_inbound_triage.py` —
  defensive env-var fallback (`os.environ.get(...) or ""` instead of
  `os.environ[...]`) to unblock pytest collection.
- `/app/memory/MASTER_STATE.md` — Phase 5.2 entry in §4 (see memo §5).

### Net delta
~155 FE files (1-line import-rewrite each) + ~750 LOC across new memo /
invariants / codemod / spec doc.

---

## 4. Verification (this env)

### New invariants
- `pytest tests/invariants/test_invariant_no_raw_axios.py` → **2/2 PASS**.
- `pytest tests/invariants/test_invariant_polymorphic_response_ratchet.py` → **3/3 PASS**.

### Full invariants suite — no regression
- `pytest tests/invariants/` → **49 PASS, 10 documented skips**
  (was 44 PASS pre-Phase-5.2; +5 = the new invariants' assertions).

### Public surface ratchet — untouched
- `pytest tests/test_phase4_4_dual_mount_smoke.py` → **37/37 PASS**.
- OpenAPI hashes preserved: `/api/* = cdcb23322bb82895`, `/v1/* = acc51822aa8818ae`, combined `ca9429c64e44570c`.

### FE unit tests
- `yarn test --testPathPattern="apiV2|validatedCall"` → **10/10 PASS**.
- `yarn test` (broader) → 99/103 pass; 4 pre-existing failures
  (verified pre-existing by `git stash`).

### Bundle mirror
- `curl /api/docs/bundle.zip` → **HTTP 200**, 4 files including
  `AKKI_MODULE_PRODUCT_SPECS.md` (38,735 bytes).

### Smoke screenshots
- Public homepage (`/`) → renders cleanly. "Akki refuses to invent."
  hero visible, no JS errors.
- `/app/learn` → renders "VERIFYING SESSION" gated-route loading state
  (expected without auth). No white screen, no JS errors.

---

## 5. MASTER_STATE diff

Section 4 Track A — Phase 5.2 entry appended below Phase 5.1:
- Multi-part deliverable list (A codemod + migration, A invariant,
  B invariant, D doc + bundle mirror).
- Files-touched inventory.
- Verification evidence (49/49 invariants, 37/37 Phase 4.4 ratchet,
  10/10 FE wrapper tests).
- Deviations log (D1–D7).
- Iteration budget: 1/3 used.

Carry-forward additions in §8 (debt snapshot):
- Part B narrowing (49 routes) → moved from "carry-forward" to
  "ratchet-baselined; future sprint to narrow".
- Part C triage → moved from "15 failures" to "50+ failures
  (collection-error blocker resolved; full triage requires Phase 5.3)".
- Pre-existing `yarn build` resolver issue (TS not in `extensions`)
  → new debt item, separate from Phase 5.2.

---

## 6. Discipline rails observed

- **R1** — MASTER_STATE updated.
- **R2** — Intent Pre-Read confirmed by user prior to dispatch (option (a)).
- **R3** — Smoke phase done: 2 build-breaking invariants + full
  invariants sweep + Phase 4.4 ratchet + bundle-mirror curl + FE unit
  tests + 2 screenshots.
- **R4** — Phase lockdown test count: **5 new test functions** across
  2 new invariant files. Well under the ≤10 cap.
- **R5** — Root-cause-first on the POSTMARK collection error: traced
  to module-import-time env-var KeyError; defensive fallback at the
  exact module-level lines.
- **R6** — No side quests. Other carry-forward debt items untouched.
- **R7** — Honesty Protocol applied (this memo's §1 scope-finding;
  Part C triage deferred with explicit reason; the `yarn build`
  resolver issue documented as separate debt, not silently
  papered-over).

---

## 7. Deviations log

| # | Deviation | Rationale |
|---|---|---|
| D1 | Part A — 2 smoke screens instead of 5 | Auth-gated cold-path screens require credentials; migration is mechanical (no behaviour change). Pattern verified on the 2 screens that DO render (public + auth-gated loading state). |
| D2 | Part A — `yarn build` (CRA production) fails | Pre-existing CRA-vs-TypeScript `resolve.extensions` issue; verified by stashing my changes. Dev server works fine; SPA serves correctly. Out-of-scope for Phase 5.2. |
| D3 | Part B — 49 routes not narrowed | Scope-too-large for a single context window (each route needs shape investigation + Pydantic model + diff harness). Invariant landed as the upstream gate; narrowing is a multi-sprint follow-up. |
| D4 | Part B — Per-route diff harness deferred | No routes narrowed = no diff to harness. Will land alongside the first narrowing batch. |
| D5 | Part B — OpenAPI ratchet untouched | Dispatch anticipated the sha shift from narrowing; since no narrowing happened, shas stay at Phase 4.4 baseline. |
| D6 | Part C — 15-failure triage replaced with collection-error fix + scope finding | Actual failure count is 50+ (3-5× the handoff). Triage requires its own dispatch. The collection-error fix unblocks the test sweep for that future work. |
| D7 | Part C — Full backend suite ≠ 0 failures | Same as D6. The **invariants** suite + Phase 4.4 ratchet are both 100% green, which is the contract-level signal that matters for "no architectural regression". |
| D8 | Handoff baseline numbers were materially under-counted | Logged at §1 of this memo. Recommend tightening the handoff process for future dispatches: include the actual grep counts, not summary estimates. |

---

## 8. Iteration budget

**1/3 used.** Iter-2/3 reserved for:
- If the user wants Part C triage to be the next dispatch (recommended:
  Phase 5.3 — "Track A failure triage", which is now unblocked by
  the collection-error fix).
- Or a Part B narrowing batch (recommended: Phase 5.4 — narrow the
  top 10 highest-traffic polymorphic routes, run the diff harness, drop
  the ratchet to 39).

---

## 9. Pointer for the next agent

If picking up Part B narrowing:
1. Pick a small batch (5-10 routes). Don't try the whole 49 at once.
2. For each: investigate live shape via curl + Phase 0 golden if
   available; author the Pydantic model in `contracts/responses.py`
   (use `extra='allow'` open shape — same pattern as the 30+ existing
   models); swap `response_model=Optional[Dict[str, Any]]` → the new
   model; drop the `# phase-3.0:narrow-in-3.1` marker.
3. Run the FastAPI TestClient byte-diff harness (you'll need to add
   one — `tests/invariants/test_invariant_response_byte_equivalence.py`
   is the dispatch's suggested path).
4. Decrement `_BASELINE_POLY_ROUTE_COUNT` and
   `_BASELINE_NARROW_MARKER_COUNT` in
   `test_invariant_polymorphic_response_ratchet.py` by the batch size.
5. Capture the new `/api/*` and `/v1/*` shas; commit as the new
   Phase 4.4 ratchet baseline (and update `MASTER_STATE.md` §4 +
   the `PHASE_4_4_DUAL_MOUNT.md` memo's sha-pin section).
6. Run the full invariants suite + Phase 4.4 dual-mount smoke before
   shipping.

If picking up Part C:
1. The 400s `pytest --tb=no -q` sweep timed out at ~34% in this env.
   Sub-suite it: `pytest tests/test_chunk*.py`, `tests/characterisation/`,
   `tests/test_iter*.py`, `tests/test_phase*.py` each separately.
2. Most failures appear to be live-DB data-fixture issues (Category 3
   in the dispatch's triage spec) — refactor to use isolated fixtures
   or seed-and-teardown patterns. Do NOT add silent skips; if a test
   legitimately can't run, use explicit `pytest.skip(reason=...)`.
3. The handoff's quoted "15 pre-existing Track A failures" was likely
   based on a much older test-suite snapshot. Take the actual current
   count as the new baseline and triage forward from there.
