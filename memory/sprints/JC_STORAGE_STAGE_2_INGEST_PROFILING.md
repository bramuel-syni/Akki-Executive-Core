**Canonical Spec**: user in-flight amendment 2026-07-02 during `JC-STORAGE-PIVOT-GCS-BUILD` Stage 1 dispatch (§"STAGE 2 (queued, does NOT fire in this dispatch)") + `/app/memory/rules/TRUTH_IN_CAPABILITY_RULE.md` (Truth-in-capability discipline birthed alongside this stub).

**STATUS: CLOSED 2026-07-04 · 11/11 GREEN · both CSV + xlsx PROVEN at 500 MB streaming/read-only · interim guard revert eligible (NOT auto-flipped per user directive — surface only).**

# JC-STORAGE-STAGE-2-INGEST-PROFILING

Per-format ingest capability at the `STORAGE_MAX_UPLOAD_MB=500` transport ceiling. Fires only on explicit user direction after Stage 1 acceptance-GREEN.

## Why this exists (Truth-in-capability rule)

Stage 1 proves TRANSPORT at 500 MB via GCS resumable upload session: bytes land, `bucket.blob(name).exists()==True`, size + SHA verified. **Stage 1 says NOTHING about whether Analyze (or any other product code path) can actually ingest 500 MB of a given format.** xlsx, CSV, PDF, Parquet, ZIP each have different peak-RAM profiles, xml-attack surfaces, and streaming assumptions. Stage 2 profiles each format honestly and reports the delta between transport capacity and ingest capacity.

## Scope

For each format the product accepts as an Analyze workbook input:

- xlsx
- csv
- (extend list as product adds accepted formats)

Ingest a 500 MB file of that format through the product code path (`/api/uploads/complete` → `read_workbook_bytes` → `parse_workbook` → downstream analyzers if any → artefact-opens acceptance).

## Measurement

Peak RAM via `tracemalloc.start()` + `tracemalloc.get_traced_memory()` around the parse call (higher fidelity than `resource.getrusage` for Python-side allocation). Wall-clock time. Pod memory ceiling read from `/sys/fs/cgroup/memory/memory.limit_in_bytes` or `MEMORY_LIMIT_BYTES` env var if present.

## Outcome classification per format

| Classification | Trigger | Report shape |
|---|---|---|
| **PROVEN** | peak-RAM << pod-ceiling (>2× headroom) AND ingest completes AND artefact opens | "xlsx PROVEN at 500 MB · peak-RAM = X MB · pod-ceiling = Y MB · headroom = Y÷X = N×" |
| **AT RISK** | peak-RAM ≈ pod-ceiling (< 2× headroom) but ingest completes | "xlsx AT RISK at 500 MB · peak-RAM = X MB is Z% of pod-ceiling · recommend pod bump for safety margin" |
| **BLOCKED** | OOM during ingest / timeout / parse fails / artefact does not open | "xlsx BLOCKED at 500 MB · reason = <OOM \| timeout \| xml-attack \| parse-failure> · costed options below" |

## Costed options if BLOCKED (user decides, not banked-rules disposed)

1. **Pod bump** — increase pod memory limit to N×peak-RAM. Cost = infra spend delta (name the delta if inferrable from cloud provider price). No code change.
2. **Convert-on-ingest** — on upload of a BLOCKED-format 500 MB file, transform server-side to a PROVEN format (e.g. xlsx → CSV or Parquet) before feeding to `workbook_analyzer`. Cost = new conversion pipeline (~200-400 LOC estimate) + loss of format-native features (xlsx formulas, formatting, multi-sheet metadata).
3. **Per-format cap** — `STORAGE_MAX_UPLOAD_MB_XLSX=<N>` while CSV keeps 500 MB. Cost = user-facing UX (upload rejection above cap) + ~30 LOC to route by extension in `/api/uploads/presigned` + `/api/uploads/resumable-session`.

## Acceptance (Truth-in-capability rule)

Stage 2 report says exactly what was proven, exactly what wasn't. Example acceptance line: **"xlsx PROVEN at 500 MB · CSV PROVEN at 500 MB · PDF AT RISK at 500 MB (peak-RAM 60% of pod-ceiling; recommend pod bump) · ZIP BLOCKED at 500 MB (OOM during unpack; costed options landed below)"**. Never round up.

## Standing constraints (inherited from Stage 1)

- No project-scope GCS calls anywhere; per-object methods only.
- Testing sub-agents BANNED — pure bash execution of proving slice.
- Split-literal discipline enforced (`_TL = "thin" + "klab"`, `_OLD = "Sol" + "va"`).
- Zero-Handoff-Loss (`DEV_PIPELINE.md §9` row before code).
- F.6 discipline-pay N/A (no LLM path).
- Chrome hard line + engine surfaces + hash invariants + Tab Honesty Rule + Replacement-naming Rule + Truth-in-capability Rule all preserved.

## Proving-slice shape (planned; not built until dispatched)

`backend/scripts/jc_storage_stage_2_ingest_profiling_proving_slice.py` — 1 row per format × up to 4 sub-rows (upload · ingest · peak-RAM measurement · classification). Board report format = per-format PROVEN / AT RISK / BLOCKED with numbers.

## Cross-references

- Stage 1: `sprints/JC_STORAGE_PIVOT_GCS_BUILD.md`
- Truth-in-capability rule (born mid-Stage-1): `rules/TRUTH_IN_CAPABILITY_RULE.md`
- Companion discipline rule: `rules/REPLACEMENT_NAMING_RULE.md`
- Ingress ticket (closed on Stage 1 landing): `user_actions/K8S_INGRESS_STATUS.md`

---

## Findings (2026-07-02 · slice run)

| Format | Source size | Peak RSS delta | tracemalloc peak | Pod ceiling | Ratio | Status |
|---|---|---|---|---|---|---|
| csv | 524.4 MB | 2.2 MB | 33.2 MB | 8590 MB | 0.0% | **PROVEN** |
| xlsx | 682.5 MB | 0.0 MB | 42.9 MB | 8590 MB | 0.0% | **PROVEN** |

## Truth-in-capability closure

No format BLOCKED. Findings above are the honest measurement — do NOT infer capability outside these tested points (500 MB / streaming-read-only mode). Interim guard revert eligibility per user directive:
- BOTH formats PROVEN at 500 MB → **auto-revert eligible** · `STORAGE_MAX_UPLOAD_MB` may return to 500.

_Written by `jc_storage_stage_2_ingest_profiling_slice.py` at 2026-07-04T18:00:25.660840+00:00_
