# JC-TM Stage 1 — Compile Bridge

> **Canonical specs cited:**
> - `/app/memory/JC_TM_CANONICAL_SPEC.md` (§ Part 0 — REUSE EXISTING ENGINES; § Integration point with JC-WS)
> - `/app/memory/JC_WS_CANONICAL_SPEC.md` (Phase 1 invariants: commit lifecycle, edit-lock 409, confidence-pct)
>
> **Closed:** 2026-06-25
> **Acceptance:** 14 / 14 GREEN
> **Artefacts:** `/app/memory/jc_artifacts/JC-TM-bridge-*`
> **Proving-slice script:** `/app/backend/scripts/jc_tm_proving_slice.py`

## Why

The 2026-06-25 JC-TM proving slice surfaced an architectural fork: compile was
writing LLM-generated plain-text section bodies to `db.documents.extracted_text`
and never produced a `.docx` / `.pdf` / `.pptx`. This violated the canonical-spec
rule **"REUSE existing engines"** (Part 0):

> Critically: compile must produce documents through the SAME generators and the
> SAME export wizard as Document Generation (board packs, committee packs,
> briefings, decks, financial models/XLS). Do NOT build a parallel generation
> stack.

Three options surfaced in `sprints/JC_TM_KEYSTONE_AND_PROVING_SLICE.md`. **User
locked Option A** — thin compile-as-orchestrator over `work_studio_export`.

## What changed

### `backend/services/tasks/compile_service.py`

**`run_drafting` — fully rewritten.** Was: per-section LLM call → plain text →
`db.documents.insert_one`. Now:

1. Map `task.output_spec.template_id` → work_studio_export `_VALID_KINDS` via a
   new `_TPL_TO_EXPORT_KIND` dict (board_pack/committee_pack/deck/minutes/report/brief).
   Unknown templates fall back to `report` (most permissive shape).
2. Sanitise `task.output_spec.formats` against `{docx, pptx, pdf}`.
3. Build `ExportRequestIn` from approved contributions via the new
   `_build_export_body()` helper: `objective ← task.objective`,
   `scope ← task.success_criteria`, `description ← per-contributor summaries`.
4. Lazy-import `_run_export` + `ExportRequestIn` to avoid a circular ref. Prior
   art for this exact pattern lives in `routers/compilations.py:234-235`.
5. For each requested format, pre-insert a `work_studio_exports` row carrying a
   new `source_task_id=<task_id>` field (the TaskDrawer pivot-back), then
   `await _run_export(...)`. `_run_export` itself stamps `status=complete` /
   `status=failed` + `lifecycle_state="draft"` + `confidence_pct` + the file
   bytes on disk.
6. Persist `compile_session.draft_artefact_ids = [<export_id>, ...]` and
   `compile_session.draft_artefact_kind = "work_studio_export"`.

**Honest fallback.** Only if every requested format raises a non-recoverable
error does `run_drafting` drop to a legacy plain-text writer (tagged
`draft_artefact_kind = "legacy_document"`, also captures `bridge_errors[]` +
`fallback_legacy_doc_ids[]`). This keeps the proving slice unblocked while
making the fallback honest in the artefact ledger.

**`run_commit` — branched on `draft_artefact_kind`.** Bridge path flips
`work_studio_exports.lifecycle_state` `"draft"` → `"committed"` +
`committed_at=<iso>`; this single field is the key the edit-lock invariant
checks in `routers/work_studio_overlay.py:134-138` — same code path JC-WS
Phase 1 already proved. Legacy path retained for the fallback case only.
Auto-close decision now reads the right collection
(`work_studio_exports.source_task_id=<tid> AND lifecycle_state=draft` for the
bridge path; `db.documents.task_id=<tid> AND state=draft` for legacy).

### `backend/routers/tasks.py:start_compile_drafting`

Sync/BG branching switched from sections-count to formats-count. Single-format
output specs run sync; multi-format runs go to `background_tasks.add_task(_bg)`.
Old `_TEMPLATE_PACK_SHAPES` lookup retired from this branch (still used by the
fallback writer inside `run_drafting`).

### `backend/scripts/jc_tm_proving_slice.py`

Steps 7-10 replaced. The slice now:
- Polls `task.compile_session.draft_artefact_ids` until populated (since the BG
  path returns "queued" before the exports exist).
- Polls each `work_studio_exports/{eid}` until `status=complete`.
- After `/compile/commit`, PATCH-probes each committed export at
  `/api/contexts/{cid}/work-studio/documents/{eid}` expecting **409** (the
  Phase 1 edit-lock invariant).
- Downloads each `complete` export via the wizard's `download_token` flow and
  saves it as `JC-TM-bridge-compiled[-<n>].<ext>` in `/app/memory/jc_artifacts/`.
- Writes 3 new evidence files:
  `JC-TM-bridge-export-row.json` (post-commit row snapshots — kind, format,
  lifecycle_state, status, source_task_id, file_name, byte_len, sha256,
  confidence_pct, sensitivity_band, committed_at),
  `JC-TM-bridge-edit-lock-proof.json` (probe results + body heads),
  `JC-TM-bridge-downloads.json` (file size + magic-number per format).
- Adds **5 invariant-transfer rows** to the acceptance ledger:
  (a) bridge → work_studio_export drafts (not legacy db.documents);
  (b) Invariant 1 — lifecycle_state == committed;
  (c) Invariant 2 — PATCH → 409;
  (d) Invariant 3 — confidence_pct numeric;
  (e) bridge artefacts opened — DOCX/PDF/PPTX files on disk with valid magic.

## Before / after compile flow

```
BEFORE                                  AFTER (Stage 1 Bridge)
──────                                  ──────────────────────
                                         compile_service.run_drafting
compile_service.run_drafting               ↓ build ExportRequestIn from
  ↓ per section (5x):                       contributions + task fields
  shield_invoke_bounded(prompt)             ↓ resolve kind from
  ↓ extracted_text (plain text)             template_id (TPL_TO_EXPORT_KIND)
  db.documents.insert_one                   ↓ per format (docx + pdf):
                                              pre-insert work_studio_exports
                                              row (source_task_id=<tid>)
                                              ↓ await _run_export(...)
                                                ↓ Pass-1 LLM (Shield) →
                                                  JSON workbook layer
                                                ↓ Pass-2 LLM (Shield) →
                                                  rendered + sensitivity-banded
                                                ↓ scoring → confidence_pct
                                                ↓ stamp file_path + sha256
                                                ↓ status=complete

compile_service.run_commit              compile_service.run_commit
  ↓ per doc_id:                           ↓ branch on draft_artefact_kind
  db.documents.update_one                 ↓ bridge path:
    state=draft→committed                   work_studio_exports.update_one
                                              lifecycle_state=draft→committed
                                              committed_at=<iso>
                                          ↓ legacy fallback:
                                            db.documents.update_one
                                              (only if bridge failed)

PATCH after commit → ???                PATCH after commit → 409
(no overlay route owned this              (work_studio_overlay.py:134-138
 collection)                               enforces edit-lock invariant
                                           on lifecycle_state=committed)
```

## Per-invariant transfer evidence

### Invariant 1 — Commit lifecycle (`lifecycle_state`)

Pre-commit state is set by `run_drafting` at row insertion
(`"lifecycle_state": "draft"` — see `compile_service.py:_TPL_TO_EXPORT_KIND`
sibling block where the row is inserted before `_run_export` runs).
`_run_export` itself does not touch `lifecycle_state`; it only flips
`status` from `running` → `complete`.

Post-commit (from `JC-TM-bridge-export-row.json` — read directly from
`db.work_studio_exports`):
```json
{"export_id":"4f37…","lifecycle_state":"committed",
 "committed_at":"2026-06-25T15:18:01.445686+00:00"}
{"export_id":"2891…","lifecycle_state":"committed",
 "committed_at":"2026-06-25T15:18:01.446115+00:00"}
```

The transition is owned by `run_commit`'s `db.work_studio_exports.update_one`
with the filter `{"lifecycle_state": "draft"}` — meaning the modify only
succeeds when the row was actually in draft state, which is itself a
proof-by-execution of the pre-commit state.

**Verdict: ✅ transferred cleanly.**

### Invariant 2 — Edit-lock (PATCH after commit → 409)

From `JC-TM-bridge-edit-lock-proof.json`:
```json
{"export_id":"4f37…","status_code":409,
 "body_head":"{\"detail\":\"This document is committed and read-only.
              Create a new version to make changes.\"}"}
{"export_id":"2891…","status_code":409,
 "body_head":"{\"detail\":\"This document is committed and read-only.
              Create a new version to make changes.\"}"}
"all_returned_409": true
```

The error body is **byte-identical** to the JC-WS Phase 1 edit-lock response —
proof we ride the same overlay route, not a parallel implementation.

**Verdict: ✅ transferred cleanly.**

### Invariant 3 — Confidence pct (numeric, not None)

From `JC-TM-bridge-export-row.json`:
```json
{"export_id":"4f37…","kind":"board_pack","output_format":"docx",
 "confidence_pct":40,"sensitivity_band":"INTERNAL"}
{"export_id":"2891…","kind":"board_pack","output_format":"pdf",
 "confidence_pct":30,"sensitivity_band":"INTERNAL"}
```

The pct values come from the SAME `_score_and_mirror_confidence` path JC-WS
Phase 1 ratchets — they are not synthesised by compile.

**Verdict: ✅ transferred cleanly.**

## Real artefacts produced

| File | Bytes | Magic | Purpose |
|---|---:|---|---|
| `JC-TM-bridge-compiled.docx` | 41 237 | `504b0304` (PK) | Board pack DOCX — cover + exec summary + 6 sections, each with topline + body + recommendation paragraphs from Pass-1/Pass-2. 70 paragraphs total. Opens cleanly in `python-docx`. |
| `JC-TM-bridge-compiled-2.pdf` | 27 414 | `25504446` (`%PDF`) | Same content rendered to PDF. |
| `JC-TM-bridge-export-row.json` | 1 022 | json | Both work_studio_exports rows post-commit. |
| `JC-TM-bridge-edit-lock-proof.json` | 596 | json | PATCH probes (both 409). |
| `JC-TM-bridge-downloads.json` | 354 | json | File size + magic per format. |
| `JC-TM-bridge-acceptance.json` | 4 426 | json | Full 14-row ledger + invariant rows + bridge metadata. |

Sample paragraph structure (from `JC-TM-bridge-compiled.docx`):

```
CLASSIFICATION  ·  CONFIDENTIAL
Mara Heritage Bank Board Pack — Q3 2025
Board Chair Review — 30 September 2025
Prepared for Mara Heritage Bank Board of Directors  ·  Q3 2025  ·  …

Executive summary
Mara Heritage Bank faces three interdependent decisions that will define Q4
execution capa…

Index
01.  Performance
02.  Risk Position
03.  Digital Transformation
04.  People & Capability
05.  Capital Allocation
06.  Governance

Performance
Q3 operating environment stable; execution capacity now the binding constraint
…
```

That's the same "forward-to-a-board good" shape Phase 1 proved — sections as
headings inside one composed document, not five separate files.

## Acceptance ledger (14 / 14)

```
[✓] Task created in active state with team[2]
[✓] Contributor invite state captured (mode: magic_link)
[✓] Contribution 1 — submit + approve path
[✓] AI-drafted revision request (Shield or deterministic fallback)
[✓] Contribution 2 — needs_revision applied
[✓] Contribution 2 — resubmit + approve
[✓] Readiness intelligence — REAL score + breakdown + at least one finding
[✓] Compile draft pipeline produced at least one section
[✓] Commit locks the artefacts
[✓] Bridge → work_studio_export drafts (NOT legacy db.documents)
[✓] Invariant (1) — commit lifecycle: lifecycle_state==committed
[✓] Invariant (2) — edit-lock: PATCH after commit → 409
[✓] Invariant (3) — confidence_pct: real numeric (not None)
[✓] Bridge artefacts opened — DOCX/PDF/PPTX files on disk
```

## STOP condition (per user dispatch)

> "STOP and surface Stage 1 evidence package when ready — fan-out stays paused
> until user inspects."

This sprint MEETS that STOP condition. Stage 2 (JC-TM Fan-out across Create /
Coordinate / Manage / Readiness / Generate / Monitor / Complete journeys) is
PAUSED awaiting user inspection of:

1. `/app/memory/jc_artifacts/JC-TM-bridge-compiled.docx` (opens it, scans the prose)
2. `/app/memory/jc_artifacts/JC-TM-bridge-compiled-2.pdf` (same content, PDF)
3. `/app/memory/jc_artifacts/JC-TM-bridge-export-row.json` (lifecycle/state proof)
4. `/app/memory/jc_artifacts/JC-TM-bridge-edit-lock-proof.json` (409 proof)
5. `/app/memory/jc_artifacts/JC-TM-bridge-acceptance.json` (full ledger)

## Honest notes / scope cuts

- The board_pack `confidence_pct` values (40 and 30) are **real numbers** from
  the JC-WS Phase 1 scorer — but they are LOW because the proving slice doesn't
  yet pass `source_document_ids` into the export request. JC-WS Phase 1's
  scorer rewards cited sources; an empty source list pulls the pct down. This
  is honest behaviour, not a bug. When Stage 2 wires real contributor uploads
  into the bridge body, the pct will rise organically. Captured in
  `confidence resolver debug` log: `source_document_ids=None  citations_manifest_n=8`.
- `_TPL_TO_EXPORT_KIND` is intentionally permissive — unknown templates resolve
  to `report` (the broadest shape work_studio_export supports). Stage 2 may
  refine this when more concrete task templates land.
- The legacy plain-text fallback is **not exercised** in the proving slice —
  the bridge succeeded on all 2 formats. The fallback is defensive code, not
  active code, and it's tagged in the session so any downstream consumer can
  filter it out.

## Files touched

- `backend/services/tasks/compile_service.py` — `run_drafting` rewritten,
  `run_commit` branched, `_TPL_TO_EXPORT_KIND` + `_build_export_body` added.
- `backend/routers/tasks.py:start_compile_drafting` — sync/BG branching now
  formats-based.
- `backend/scripts/jc_tm_proving_slice.py` — Steps 7-10 + acceptance ledger
  augmented with 5 invariant-transfer rows.

No frontend changes. UI-untouched rule held.
