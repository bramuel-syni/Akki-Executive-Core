**Canonical Spec**: `/app/memory/sprints/BUG_ANALYZE_UPLOAD.md` (BUG-ANL-UPLOAD-GRIDFS Phase 3 closure 2026-06-26 · 11/11 GREEN · §"Out of scope" line 197-200 explicitly defers inline-blob sunset to P2 backlog: "Once the backfill runs in prod, the legacy `data_b64` reader can be removed and the GridFS-only reader can replace `read_workbook_bytes`. Lifted to P2 backlog in `BACKLOG_SCHEDULE.md`.") + `/app/memory/DEV_PIPELINE.md §1` step 2 (GridFS backfill --commit complete 2026-06-27 09:19 UTC · 3068 rows migrated · 0 errors · local Mongo confirmed) + cross-references `sprints/JC_LLM_MODELS_REFRESH_EVALUATION.md` (predecessor queue item 7 evaluation; surfacing user-dep backlog discipline).

# Sprint JC-INLINE-BLOB-SUNSET-EVALUATION — pre-staged plan held for 2026-07-03 timer

**Status**: SHIPPED (evaluation memo only) · READ-ONLY · 0 LOC mutated outside memo · HARD STOP at evaluation surface · pre-staged plan held for 2026-07-03 timer · 1 CRITICAL user-dependent gate surfaced (PROD backfill state) · 1 carryover user-action pending (K8s ingress annotations)
**Date**: 2026-06-30
**Predecessor**: `sprints/BUG_ANALYZE_UPLOAD.md` (Phase 3 CLOSED 2026-06-26) · `sprints/JC_LLM_MODELS_REFRESH_EVALUATION.md` (queue item 7 surfaced 2026-06-30)
**Successor**: `JC-INLINE-BLOB-SUNSET-FIX` dispatch, can fire on/after 2026-07-03 with user confirmation on Gate A (CRITICAL) below

---

## §1 — Soak status audit (CLEAN)

### §1.1 — Closure date verification

| Source | Citation | Date |
|---|---|---|
| Sprint memo title | `sprints/BUG_ANALYZE_UPLOAD.md` line 6 "Phase 3 implementation CLOSED 2026-06-26 · 11/11 GREEN" | 2026-06-26 |
| DEV_PIPELINE §2 Active Dispatch | "BUG-ANL-UPLOAD-GRIDFS — VERIFIED CLOSED 2026-06-26 · 11/11 GREEN · 5/5 regression GREEN" | 2026-06-26 |
| DEV_PIPELINE §1 Step 2 | "GridFS Backfill --commit COMPLETE 2026-06-27 09:19 UTC. ... 3068 rows migrated · 0 errors · runtime 4.436s" | 2026-06-27 (post-close backfill of local Mongo) |

**Soak window**: 2026-06-26 closure + 7d = 2026-07-03 sunset eligibility.
**Today**: 2026-06-30 = T+4 days.
**Remaining**: **3 days in soak**.

### §1.2 — Post-close incident scan (CLEAN)

Method: `grep -E "data_b64|gridfs|workbook_blob|analysis_blob|413|MAX_BYTES|over_500mb|upload.*fail" /var/log/supervisor/backend.err.log` over the 4-day window since closure.

**Result**: 0 upload/GridFS-related errors. The 19 matched lines were all:
- `synisense.engine.signal_derivation` INFO log lines with "413" in millisecond timing strings (NOT HTTP 413)
- `akki.news_aggregator` INFO log lines with "413" in news source timing strings
- 1 deprecated `en_core_web_trf` warning (unrelated to upload path)

**Verdict**: 0 incidents requiring investigation. Soak audit CLEAN. Per autonomous mandate path "If soak audit clean AND scope verified AND today < 2026-07-03 → hold evaluation as pre-staged plan, surface to me, await timer" — proceeding to scope inventory + dispatch shape recommendation as pre-staged plan.

---

## §2 — Sunset scope inventory (small + focused)

Disk grep cross-validation per lesson #6:
```bash
grep -rn "data_b64\|read_workbook_bytes\|build_analysis_from_uploads" --include="*.py" routers/ services/
grep -rn "data_b64" --include="*.py" routers/ services/ models/
grep -rn "build_analysis_from_uploads" tests/invariants/tenancy_escape_allowlist.yml
```

### §2.1 — Functions to REMOVE

| File | Lines | Symbol | Removal type | LOC |
|---|---:|---|---|---:|
| `services/analysis_lifecycle.py` | L242-307 | `build_analysis_from_uploads()` | REMOVE entire function | ~65 |
| `services/analysis_lifecycle.py` | L426 | `"build_analysis_from_uploads"` entry in `__all__` | REMOVE entry | 1 |
| `routers/workbook_analysis.py` | L76 | `build_analysis_from_uploads,` orphan import | REMOVE import | 1 |
| `services/analysis_lifecycle.py` | L163-165 | `data_b64` fallback branch in `read_workbook_bytes()` | SIMPLIFY (remove branch) | ~5 |
| `services/analysis_lifecycle.py` | L166-170 | Raise message references both fields | SIMPLIFY (only `gridfs_id` now) | ~2 |

**Discovery (lesson #6)**: `build_analysis_from_uploads` is IMPORTED in `routers/workbook_analysis.py:76` but NOT CALLED anywhere — orphan import. Production code uses `build_analysis_metadata()` (the GridFS-aware constructor) at the streaming-upload sites. Removal is safe at the production-code dimension; only test-scaffolding (now non-existent — see §2.4) referenced the legacy constructor.

### §2.2 — Comments + docstrings to UPDATE

| File | Lines | Update |
|---|---:|---|
| `services/analysis_lifecycle.py` | L17-21 | Remove "dual-reads ... falls back to `data_b64` for LEGACY rows" — simplify to "reads GridFS via `download_to_tempfile`" |
| `services/analysis_lifecycle.py` | L142-153 | Remove "Returns `(bytes, None)` for LEGACY rows" + simplify to GridFS-only return signature |
| `routers/workbook_analysis.py` | L167 | Remove "(bytes, None) for legacy `data_b64` rows" comment |
| `routers/workbook_analysis.py` | L428-429 | Remove "NEW shape ... dual-read ... handles legacy `data_b64` rows transparently" |
| `routers/workbook_analysis.py` | L1034 | Remove "GridFS-migrated rows AND legacy `data_b64` inline rows" |
| `routers/workbook_analysis.py` | L1085 | Remove "`data_b64` reads have no tempfile to clean" |

### §2.3 — Tenancy allowlist YAML refresh

| File | Lines | Update |
|---|---:|---|
| `tests/invariants/tenancy_escape_allowlist.yml` | L535, L538, L753, L755 | Refresh justification prose: replace 4 references to `build_analysis_from_uploads(account_id, context_id) call (L710-716)` with `build_analysis_metadata(account_id, context_id)` (the GridFS-aware constructor that's the actual call site at L710-716) |

These are TEXT justifications in audit prose, not code dependencies. The line numbers L710-716 in workbook_analysis.py ALREADY call `build_analysis_metadata` (the GridFS-aware constructor). The allowlist prose just hasn't been refreshed to match. **F.5 single-batched-edit lesson APPLIED at fix dispatch**: all 4 prose updates in one search_replace operation.

### §2.4 — Test scaffolding

Disk grep result: **0 test files** import `build_analysis_from_uploads` or use `data_b64` literal references. The legacy constructor was preserved at BUG-ANL-UPLOAD-GRIDFS ship time "for unit tests / characterisation tests that still pass raw bytes through this constructor" — but no test currently exercises it. Sunset removal is safe at the test-scaffolding dimension.

### §2.5 — Scripts (slice + backfill)

| File | Lines | Action |
|---|---:|---|
| `scripts/jc_bug_analyze_upload_slice.py` | Row H (legacy dual-read; L466-485) | Convert to negative-rail "synthetic `data_b64` row raises RuntimeError" (defensive assertion that the sunset path correctly refuses inline reads) |
| `scripts/jc_bug_analyze_upload_slice.py` | Row I (backfill idempotency; L500-580) | Either REMOVE or convert to negative-rail "0 inline rows in collection" assertion |
| `scripts/jc_bug_analyze_upload_backfill.py` | Entire script | OPTIONAL: archive to `scripts/archive/jc_bug_analyze_upload_backfill.py` (no longer needed post-sunset; preserve for historical audit). Recommended: ARCHIVE not DELETE. |

### §2.6 — Estimated total LOC delta

| Category | LOC delta |
|---|---:|
| Code removal (functions + branches + imports) | ~-74 LOC |
| Comment + docstring simplification | ~-15 LOC |
| Tenancy allowlist YAML prose refresh | ~+4 / -4 LOC |
| Slice script conversion (Rows H + I) | ~+10 / -50 LOC |
| Backfill script archive (filesystem move, no LOC change) | 0 |
| **Net** | **~-129 LOC** |

Small, focused, mechanical scope. Single-dispatch capacity.

---

## §3 — Migration completeness re-verification (LOCAL DB CONFIRMED · PROD UNKNOWN)

### §3.1 — Local Mongo state (LIVE QUERY)

Run: `python3 -c "<motor query>"` with `MONGO_URL` + `DB_NAME` from `backend/.env`:

```python
async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    for coll in ('workbook_blobs', 'analysis_blobs'):
        total       = await db[coll].count_documents({})
        gridfs_only = await db[coll].count_documents({'gridfs_id': {'$exists': True}, 'data_b64': {'$exists': False}})
        inline_only = await db[coll].count_documents({'data_b64':  {'$exists': True}, 'gridfs_id': {'$exists': False}})
        hybrid      = await db[coll].count_documents({'gridfs_id': {'$exists': True}, 'data_b64': {'$exists': True}})
        neither     = await db[coll].count_documents({'gridfs_id': {'$exists': False}, 'data_b64': {'$exists': False}})
        print(f'  {coll}: total={total} | gridfs_only={gridfs_only} | inline_only={inline_only} | hybrid={hybrid} | neither={neither}')
    fs_files  = await db.fs.files.count_documents({})
    fs_chunks = await db.fs.chunks.count_documents({})
    print(f'  fs.files={fs_files} | fs.chunks={fs_chunks}')
```

**Result (live, 2026-06-30)**:
```
workbook_blobs:  total=147   | gridfs_only=147   | inline_only=0 | hybrid=0 | neither=0
analysis_blobs:  total=3477  | gridfs_only=3477  | inline_only=0 | hybrid=0 | neither=0
fs.files=3624 | fs.chunks=7636
```

**Math check**: `147 + 3477 = 3624` ✓ (1:1 mapping metadata row ↔ GridFS file).

**Local dev state: 100% MIGRATED.** Zero legacy `data_b64` rows. Sunset is safe at the local-dev dimension.

### §3.2 — PROD Atlas state (UNKNOWN — CRITICAL USER-DEPENDENT GATE)

Per BUG memo §USER_ACTION_CHECKLIST item 🟢 #3 (line 146-167):
> "**Backfill the legacy inline rows (OPTIONAL)** — The dual-read helper (`read_workbook_bytes`) handles legacy `data_b64` rows transparently — backfill is NOT required for the new code to work. Run only if you want to consolidate storage ahead of the inline-path sunset (P2 backlog item)."

The local backfill (3068 rows migrated 2026-06-27 09:19 UTC per DEV_PIPELINE §1 Step 2) was against the LOCAL Mongo. **PROD Atlas backfill state is NOT KNOWN from this evaluation surface.**

**The sunset is GATED on prod backfill confirmation**:
- If sunset proceeds AND prod has legacy `data_b64` rows → those rows become INACCESSIBLE (read path no longer falls back; the dual-read helper RAISES `RuntimeError` if neither `gridfs_id` nor `data_b64` is present, and the simplified post-sunset version will only check `gridfs_id`)
- If prod has 0 legacy `data_b64` rows OR prod backfill has been run → sunset is safe

**Verification options for user**:
1. **Confirm prod backfill ran**: user runs `python scripts/jc_bug_analyze_upload_backfill.py --commit` against prod Atlas (DRY-RUN first) in a quiet window
2. **Verify prod has 0 legacy rows**: user runs the §3.1 query against prod Atlas; if `inline_only=0` AND `hybrid=0`, sunset is safe
3. **Accept the risk**: user explicitly authorizes sunset without prod state confirmation (unlikely; would lose access to any legacy rows)

---

## §4 — Locked-area sweep (CLEAN)

| Area | Touched at fix dispatch? | Touched at evaluation? |
|---|:---:|:---:|
| Shield internals (`services/synisense/shield/client.py`) | NO | NO |
| Shield tier router (`services/synisense/shield/llm_router.py`) | NO | NO |
| Track-2 schema (`perspective_spread` + divergent deck builder) | NO | NO |
| Monitor pre-warmer (`services/monitor/*`) | NO | NO |
| OAuth provider live endpoints | NO | NO |
| WS Doc UI (doc-generation rendering) | NO (only internal helpers in workbook_analyzer; UI untouched) | NO |
| Storage arc (Azure SAS work; PAUSED awaiting creds) | NO | NO |
| Existing GridFS upload path | NO (sunset only removes legacy READ branch; upload write path unchanged) | NO |
| Backfilled 3068 rows | NO | NO |
| Bespoke-run invariant (M1+M2 ceilings) | NO (sunset is NOT in M1+M2 family) | NO |
| FTT registry | NO (no FTT IDs map to sunset; not in pollution-closure family) | NO |
| Surface ratchet `/api/* = 2769a08145e76744` | NO (no new routes; no removed routes) | NO |
| Test files using inline-blob scaffolding | NO (per §2.4 finding: 0 test files exercise legacy path) | NO |
| Tenancy allowlist YAML | YES (4 prose updates per §2.3; F.5 single-batch) | NO |

**Cleared.** Only intentional sunset-scope mutations + 4 tenancy prose updates. F.6 Shield-contract discipline-pay N/A (no Shield-adjacent test files touched).

---

## §5 — Cleanup dispatch shape recommendation

### §5.1 — Single dispatch RECOMMENDED

Per 5 evidence rows:
1. Scope is small (~129 net LOC reduction across 2 files + comment/YAML refresh)
2. All changes share IDENTICAL mechanic (remove `data_b64` fallback paths + reference updates)
3. No cross-component dependency requires sequencing (orphan import removal + branch removal + comment refresh are independent edits)
4. Single proving slice can cover all functional checks in 10-12 rows
5. Regression bar = the existing 5/5 BUG memo regression bar re-run post-sunset (well-rehearsed)

### §5.2 — Sub-dispatch alternatives REJECTED

- **Sequential sub-dispatches (5.A removal + 5.B comment refresh + 5.C tenancy YAML)**: REJECTED — over-ceremony for ~130 LOC mechanical scope; same pattern as Cluster-G G.5 single-dispatch geometry
- **Phased with intermediate validation**: REJECTED — local dev already 100% migrated; intermediate states would burn time without surfacing new evidence

### §5.3 — Proving slice spec (10-12 rows)

| Row | Check | Notes |
|---:|---|---|
| 1 | Sunset-aware analyze upload slice 9-or-10/11 GREEN | Rows H (legacy dual-read) + I (backfill) converted to negative-rail OR removed; remaining 9 rows preserved at GREEN |
| 2 | `read_workbook_bytes()` raises RuntimeError on synthetic `data_b64`-only row | Defensive negative check: confirm sunset behavior is correct refusal, not silent failure |
| 3 | Surface ratchet UNCHANGED `2769a08145e76744` | No new/removed routes |
| 4 | JC-TL Stage 1 deck byte-identity at 76555 bytes | Regression-free baseline (locked since BUG-ANL-UPLOAD-GRIDFS) |
| 5 | JC-TM Fan-Out 24/25 GREEN | Same baseline as BUG memo regression |
| 6 | JC-TL Track-2 convergent + divergent UNCHANGED | 73280 bytes + 69105 bytes; same baseline |
| 7 | Solva v2 schema regression 249/249 PASS | Same broad-subset as BUG memo |
| 8 | autosave defensive 3/3 | B.2 polluter-pair pattern; Cluster-F closure regression-free |
| 9 | phase4_2 A+D defensive 8/8 | Surface ratchets lockstep |
| 10 | Invariant suite 3/3 | M1+M2 ceilings UNCHANGED at 0/1 FINAL |
| 11 | AST source-check (`data_b64` absent from product code) | Lesson #4 G.3-VERIFICATION; AST scan of `routers/` + `services/` confirms 0 `data_b64` literal references after sunset |
| 12 | Log scan during synthetic 50 MB CSV upload + read | 0 errors; 0 `data_b64` references in trace |

12-row slice. Foreground execution estimate: ~90-120s. G.1 poll-cadence safe.

### §5.4 — F.6 Shield-contract discipline-pay

**N/A** — sunset does NOT touch Shield-adjacent test files OR Shield internal code. Only the workbook_analyzer read path simplification (which has never touched Shield).

---

## §6 — Risk classification + rollback plan

### §6.1 — Risk level

| Dimension | Risk | Reasoning |
|---|:---:|---|
| Local dev | LOW | 0 inline rows confirmed (§3.1); rollback trivially safe |
| PROD Atlas (if backfill confirmed) | LOW | Same as local |
| PROD Atlas (if backfill NOT confirmed) | **MEDIUM-HIGH** | Legacy rows become unreadable; data-access regression |
| Code mechanic | LOW | ~130 LOC net removal; mechanical; reviewable in one PR |
| Surface ratchet | NIL | 0 route changes |
| Test regression | LOW | 0 tests exercise legacy path (§2.4) |

### §6.2 — Rollback plan

If a regression surfaces post-sunset:
1. **Single git revert** of the sunset commit restores `build_analysis_from_uploads()` + `data_b64` branch in `read_workbook_bytes()` + comments + tenancy allowlist + slice rows
2. **Re-deploy** with dual-read restored; data accessibility resumes
3. **Estimated rollback time**: ~5-10 minutes (single revert + supervisor restart on dev; CI redeploy on prod)
4. **Pattern is reversible**: BUG-ANL-UPLOAD-GRIDFS commit history shows the inline-base64 → GridFS migration is mechanically symmetric; restoring the dual-read fallback is mechanical

---

## §7 — Schedule note (EXPLICIT TIMER GATE)

| Boundary | Date | Today | Days remaining |
|---|---|---|---:|
| BUG-ANL-UPLOAD-GRIDFS closure | 2026-06-26 | 2026-06-30 | T+4 (elapsed) |
| 7-day soak window end | 2026-07-03 | 2026-06-30 | **3 days remaining** |
| Earliest sunset fix execution | 2026-07-03 (00:00 UTC) | 2026-06-30 | **3 days remaining** |

**HARD GATE**: cleanup execution requires today ≥ 2026-07-03. **DO NOT FIRE EARLIER.** Per user dispatch instruction "cleanup execution requires 2026-07-03 or later (don't fire earlier)."

Per autonomous mandate path "If soak audit clean AND scope verified AND today < 2026-07-03 → hold evaluation as pre-staged plan, surface to me, await timer" — **CURRENT STATE**.

When timer expires on 2026-07-03 AND Gate A (CRITICAL) is cleared, fix dispatch can autonomously proceed at the next dispatch boundary.

---

## §8 — USER-DEPENDENT GATES (surface for awareness)

### §8.1 — Gate A (CRITICAL · sunset-blocking)

**PROD Atlas backfill state verification.** Per §3.2, sunset removes the dual-read fallback path. If prod Atlas has any legacy `data_b64` rows, they become INACCESSIBLE post-sunset. User must confirm one of:
1. Prod backfill has been run (via `python scripts/jc_bug_analyze_upload_backfill.py --commit` against prod Atlas)
2. Prod has 0 legacy rows (via the §3.1 motor query against prod Atlas)
3. User accepts the data-access risk explicitly

Without this confirmation, sunset MUST NOT proceed even when timer expires.

**Update 2026-06-30 (follow-on dispatch `JC-INLINE-BLOB-SUNSET-PROD-COUNT`)**: User picked option (b) — run motor count query against prod Atlas. Credential-probe (step 1) HALTED: prod Atlas connection string NOT present in current pod env (`backend/.env` `MONGO_URL` is local-dev only; no `MONGODB_PROD_URI`/`ATLAS_URI`/`PROD_MONGO_URL` env vars set; k8s standard secret mount paths `/var/run/secrets`+`/etc/secrets`+`/run/secrets` all absent; `.env.example` mentions prod-shape as commented template only). Motor query (step 2) NOT executed. **Gate A remains OPEN**; sub-gate added: **user creds injection required before count query can run**. Injection paths: (a) inject `MONGODB_PROD_URI` env var into pod session (agent reads once + disconnects; agent MUST NOT log raw value at any point); (b) mount k8s secret to `/var/run/secrets/prod-mongo`; (c) supply connection string inline to a one-shot script invocation. Sunset fix dispatch still gated on timer 2026-07-03 + Gate A cleared.

**Update 2026-06-30 (follow-on dispatch `JC-INLINE-BLOB-SUNSET-PROD-COUNT-RESUME`)**: User chose injection path (b) — k8s secret mount at `/var/run/secrets/prod-mongo`. Single mount-presence check per user dispatch step 1 mandate: (a) `test -e /var/run/secrets/prod-mongo` → NOT present; (b) parent directory `/var/run/secrets` → ABSENT; (c) alternate parent `/run/secrets` → ABSENT. Per user contract "If the mount is NOT yet in place → HARD STOP immediately, surface to me: 'mount not present.' Do NOT poll in a loop. Do NOT attempt to create the mount. Do NOT wait beyond one check" — HARD STOP fired cleanly. Motor query NOT executed. 0 connection string touched. 0 raw file reads. **Gate A remains OPEN**; unblocking action for user/platform: provision k8s secret at `/var/run/secrets/prod-mongo` containing prod Atlas connection string; next dispatch can then execute the motor query. **Timer backstop preserved**: sunset dispatch remains gated on (i) 2026-07-03 timer expiry + (ii) Gate A cleared. Per user direction, if mount not restored before/at timer expiry, sunset falls back to timer + dual-read fallback — dual-read helper continues to handle any legacy `data_b64` rows in prod transparently until such time as prod verification lands.

### §8.2 — Gate B (CARRYOVER · NOT sunset-blocking)

**K8s ingress annotations** on `akki.syni.ai` per BUG memo USER_ACTION_CHECKLIST item 🔴 #1 (lines 116-134):
```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size:    "512m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
```

This pending action governs the WRITE path (large uploads); sunset only touches the READ path. **NOT a sunset-blocking gate** but worth surfacing for completeness. Independent dispatch sequencing.

**Update 2026-06-30 (Tigris storage pivot rescope)**: user's platform-side direction to "drop the ingress ticket" (issued during Tigris pivot dispatch on assumption that Emergent Object Store supports browser-direct-presigned uploads) is HELD PENDING because integration playbook retrieved 2026-06-30 revealed built-in Tigris is BACKEND-MEDIATED (playbook: "No presigned URLs — all access must go through your backend"). Under Path A' (built-in Tigris) the ingress annotation dependency FLIPS from FALLBACK back to LOAD-BEARING for all files > 8 MB. Ticket NOT closed; disposition depends on user's Path A'/B'/C' choice per `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md §3` + updated recontextualization at `user_actions/K8S_INGRESS_STATUS.md`. **Still NOT sunset-blocking** — the sunset only removes the legacy READ fallback for `data_b64` rows; the ingress annotation issue governs the storage-pivot WRITE flow which is independent. Gate B stays CARRYOVER status; escalation on the ingress side is tracked in the storage rescope arc, not this sunset arc.

---

## §9 — Discipline notes

- **READ-ONLY scope honoured**: 0 LOC mutated outside this memo file + DEV_PIPELINE §9 row (added BEFORE memo per lesson #1)
- **Canonical spec cited on line 1**: explicit cite of `BUG_ANALYZE_UPLOAD.md` closure memo + DEV_PIPELINE §1 Step 2 backfill log + predecessor `JC_LLM_MODELS_REFRESH_EVALUATION.md` cross-reference
- **F.3-ADVANCE memo-order slip lesson APPLIED**: §9 row authored BEFORE this memo file
- **F.5 YAML-edit slip lesson N/A at eval**: no YAML edits this evaluation; F.5 single-batch APPLIES at fix dispatch for 4 tenancy_escape_allowlist.yml prose updates
- **G.1 slice-poll-cadence-mismatch N/A at eval**: READ-ONLY evaluation; no slice runs in scope
- **G.3-VERIFICATION AST-over-grep APPLIED at eval**: grep used for scope inventory; live DB motor query for migration completeness; AST not required at evaluation surface (will be at fix proving slice Row 11)
- **NEW lesson #5 UNQUARANTINED runtime PASS baseline N/A at eval**: BUG-ANL-UPLOAD-GRIDFS proving slice 11/11 GREEN already captured at closure 2026-06-26; lesson #5 applies at fix dispatch as Row 1 = sunset-aware slice 9-or-10/11 GREEN expected
- **NEW lesson #6 file-names-from-disk APPLIED**: `build_analysis_from_uploads` orphan-import discovery + `read_workbook_bytes` dual-read structure + tenancy allowlist references all sourced from disk grep + view, NOT from memo prose. BUG memo cited for closure date + USER_ACTION_CHECKLIST only.
- **No testing subagent used** (per user explicit ban)
- **No scope creep beyond evaluation deliverables**: 9 numbered sections matching user's 7 deliverable categories + 2 supporting sections
- **No build steps executed**: evaluation is READ-ONLY by definition
- **HARD STOP at evaluation surface** per dispatch shape; pre-staged plan held for 2026-07-03 timer
- **Cluster-G arc CLOSED · Cluster-C arc CLOSED · LLM_MODELS_REFRESH .2/.3 BACKLOG · storage arc PAUSED · inline-blob sunset PRE-STAGED**

---

## §10 — User-direction surface (HARD STOP)

Inline-blob sunset evaluation milestone:
- ✅ Closure date verified (2026-06-26 per BUG memo line 6 + DEV_PIPELINE §2)
- ✅ Post-close incident scan CLEAN (0 upload/GridFS errors in 4-day window)
- ✅ Local Mongo state CONFIRMED 100% migrated (workbook_blobs 147/147 GridFS-only · analysis_blobs 3477/3477 GridFS-only · fs.files+fs.chunks math checks out)
- ✅ Sunset scope inventoried (~129 net LOC across 2 files + tenancy YAML + 5 comments)
- ✅ Orphan-import discovery (`build_analysis_from_uploads` imported but not called) via lesson #6 disk grep
- ✅ Locked-area sweep CLEAN (Shield + Track-2 + Monitor + OAuth + WS Doc + storage arc + surface ratchet all 0)
- ✅ Dispatch shape recommendation SINGLE `JC-INLINE-BLOB-SUNSET-FIX` (12-row proving slice spec'd)
- ✅ Risk classification + rollback plan documented (LOW local · MEDIUM-HIGH prod if backfill unconfirmed)
- ✅ Schedule timer gate enforced (DO NOT FIRE before 2026-07-03; 3 days remaining)
- ✅ 2 user-dep gates surfaced (Gate A CRITICAL prod backfill · Gate B CARRYOVER K8s ingress)

**Open questions surfaced for user**:
1. **Gate A (CRITICAL — sunset-blocking)**: PROD Atlas backfill state — please confirm via one of: (a) prod `--commit` backfill run completed, (b) prod inline-row count is 0, (c) explicit risk acceptance
2. **Gate B (carryover — non-blocking for sunset)**: K8s ingress annotations on `akki.syni.ai` — independent dispatch but pending since BUG-ANL-UPLOAD-GRIDFS closure
3. **Backfill script archive policy**: archive `scripts/jc_bug_analyze_upload_backfill.py` to `scripts/archive/` or keep in place for historical reference? (RECOMMENDED: ARCHIVE not DELETE)
4. **Row H + Row I slice script policy**: convert to negative-rail assertions (preserves auditability) or remove (cleaner)? (RECOMMENDED: convert to negative-rail)

**Per autonomous mandate path "If soak audit clean AND scope verified AND today < 2026-07-03 → hold evaluation as pre-staged plan, surface to me, await timer"**:
- Pre-staged plan COMPLETE
- Timer gate: 2026-07-03 (3 days remaining)
- Autonomous proceed eligible IF Gate A cleared + timer expires
- HARD STOP at this evaluation surface

Files:
- `memory/sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md` NEW (this file · canonical spec line 1)
- `memory/DEV_PIPELINE.md` §9 row added BEFORE memo (lesson #1 honoured)

0 LOC mutated outside memo file. 0 product code touched. 0 testing subagent calls. Standing rules unchanged.

End of evaluation memo.
