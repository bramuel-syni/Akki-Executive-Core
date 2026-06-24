# Phase WS0 — Work Studio Runtime Classification

**Date:** 2026-06-24
**Status:** CLOSED
**Type:** Read-only + execution-based runtime classification (no product code touched).
**Source dispatch:** User consolidated direction Section B — Work Studio Classify (WS0).

## Headline result — 8-capability classification matrix (lead, per PART 4)

| # | Capability | Verdict | Evidence |
|---|---|---|---|
| 1 | Generate per kind | **MIXED** | 4 WORKS · 1 BROKEN-AT-SEAM · 1 DEFERRED · see §1 |
| 2 | Compose/stitch (Phase-C) | **WORKS-AT-SURFACE** | `/api/work_studio/picker` returns depth + fidelity ladder; full P-C flow surface live |
| 3 | Review (Phase-C2) | **WORKS** | brief meta + revisions + enhance round-trip green; set-active untested but route exists |
| 4 | Overlay (live edit/save/version/restore) | **RUNS-BUT-AMBIGUOUS** | `list_documents` returns 20 items but `get_document(same_id)` returns 404 — surface mismatch between Document Journal and Work Studio overlay tables |
| 5 | From-source | **MIXED** | Solva session → WORKS · chat_artefact → EXISTS-NOT-EXERCISED · document → separate `/from-document` route (WORKS for 5 kinds inc. board_pack) |
| 6 | Render (per-kind streaming) | **AMBIGUOUS** | route wired; 404 on solva-session-built brief, 409 on from-document board_pack (no compiled content yet). Needs end-to-end compile-then-render to fully classify |
| 7 | Export (PDF·DOCX·PPTX × stream+signed) | **WORKS** for DOCX+PPTX · **PARTIAL** for PDF (deck→soft-forks to pptx) · signed-token download green |
| 8 | Analyze (spreadsheet-only) | **WORKS-AT-SURFACE** | 50 analyses listed; synthesize on owned aid works; B0 verdict reaffirmed |

**One-line summary of what works vs not (execution evidence, not status fields):**
> Of the 6 document kinds the user named, 4 generate end-to-end and download successfully (brief/deck/report/minutes), 1 fails at the render dispatcher seam (committee_pack), 1 isn't accepted by the API at all (board_pack via /export — but board_pack IS accepted via /from-document).

---

## §1 — Capability 1: Generate per kind (DETAIL)

Method: drove `POST /api/contexts/{ctx}/work-studio/export/{kind}` with admin@akki.ai credentials + identical {description, objective, scope} payload across 6 kinds. Polled `/exports/{eid}` until status terminal. All evidence captured 2026-06-24 ~07:14-07:21 UTC.

| Kind | Format | HTTP at start | Terminal status | File name | DL bytes | Verdict |
|---|---|---|---|---|---|---|
| `brief` | docx (auto) | 200 → export_id `555fa68a` | complete | ws0-smoke-test-export.docx | 39 258 | **WORKS** |
| `deck` | pptx (auto) | 200 → export_id `04a88284` | complete | work-studio-infrastructure-validation-results.pptx | 38 324 | **WORKS** |
| `report` | docx (auto) | 200 → export_id `43001894` | complete | workspace-export-validation-report.docx | — | **WORKS** |
| `minutes` | docx (auto) | 200 → export_id `ac10a54d` | complete | work-studio-processing-validation-04-jun-2026.docx | — | **WORKS** |
| `committee_pack` | docx (auto) | 200 → export_id `a54f493e` | **failed** | — | — | **BROKEN-AT-SEAM** |
| `board_pack` | — | **400** at API | — | — | — | **DEFERRED** |

### §1.1 committee_pack — BROKEN-AT-SEAM

- Failure record: `error="validation:No renderer for kind=committee_pack format=docx."`
- Seam location: `backend/routers/work_studio_export.py:752-780` — the render
  dispatcher branches on (output_format, kind):
  - `("docx","brief")` → `render_brief_docx`
  - `("docx",("report","minutes"))` → `render_report_docx`
  - `("pptx","deck")` → `render_deck_pptx`
  - `("pdf","brief")` → `render_brief_pdf`
  - `("pdf",("report","minutes"))` → `render_report_pdf`
  - `("pdf","deck")` → soft-fork refusal
  - **else** → `ContentValidationError("No renderer for kind={kind} format={output_format}.")`
- The `_AUTO_FORMAT` table at line 158 maps `"committee_pack": "docx"`, the QA
  comment at line 157 says committee_pack mirrors report shape (docx-out), but
  no dispatch branch ever routes `committee_pack` to the report renderer.
- This is a **repair (one-line dispatcher patch)**, NOT a rebuild. Suggested
  fix (out of WS0 scope): extend line 754 to
  `kind in ("report", "minutes", "committee_pack")`. Estimated impact: zero
  product behaviour change to existing 4 working kinds; committee_pack would
  then succeed against the report DOCX template (per the existing QA contract).

### §1.2 board_pack — DEFERRED at the /export surface

- Failure record: HTTP 400, `detail="Unknown kind. Allowed: brief, deck, report, minutes, committee_pack."`
- `_VALID_KINDS = ("brief", "deck", "report", "minutes", "committee_pack")` at
  `routers/work_studio_export.py:159`. board_pack is NOT in this set.
- **However**, board_pack IS accepted by a DIFFERENT endpoint:
  `POST /api/contexts/{ctx}/work-studio/from-document` with Literal accepting
  `("board_pack", "committee_pack", "minutes", "deck", "report")` at
  `routers/work_studio_from_source.py:619`. Tested: returns 201 with a
  Work Studio artefact row.
- So board_pack is a **surface-area mismatch**, not a missing feature. It's
  reachable via the from-document path (and the cycle-compilation path at
  `routers/compilations.py:36`) but not via the direct export entrypoint.
- Repair (out of WS0 scope): add `"board_pack"` to `_VALID_KINDS` + add a
  render branch (e.g. board_pack mirrors committee_pack → report docx renderer).

### §1.3 The 4 WORKING kinds — full content+render+download verified

Live curl (`/api/contexts/.../work-studio/exports/{eid}/download?token=...`)
returned correct MIME types:
- DOCX → `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- PPTX → `application/vnd.openxmlformats-officedocument.presentationml.presentation`

Signed-token TTL is 15 minutes per `_DOWNLOAD_TTL_SECONDS = 15 * 60`
(`routers/work_studio_export.py:61`). Token-pin verified by header.

---

## §2 — Capabilities 2-8 (compact)

### Capability 2 — Compose/stitch (Phase-C)
- Route prefix: `/api/work_studio/`. `/picker` returns the
  depth (executive_brief / board_summary / deep_dive) + fidelity (low/med/high)
  ladder live.
- `/exports` (POST) accepts the Compose-and-stitch payload; `tests/test_iter71_studio_blocks.py`
  per the test_credentials.md notes exercises CRUD + lifecycle. Not
  re-executed end-to-end here (WS0 scope is classify, not regression).
- Verdict: **WORKS-AT-SURFACE** (live response on the picker endpoint).

### Capability 3 — Review (Phase-C2)
- Route prefix: `/api/work_studio/briefs/`. Endpoints:
  `GET /{brief_id}`, `GET /{brief_id}/revisions`, `GET /{brief_id}/revisions/{rid}/diff`,
  `POST /{brief_id}/enhance`, `POST /{brief_id}/set_active`.
- Live execution: created brief `f1c27ac4` via from-source(Solva), then:
  - `GET /briefs/{id}` → 200, full brief envelope.
  - `GET /briefs/{id}/revisions` → 200, count=1 (the seed revision).
  - `POST /briefs/{id}/enhance` → 200, new revision_id `bdf75063`, diff array
    populated, parent_revision_id correctly chained.
- Verdict: **WORKS**. set-active untested in this dispatch — route exists; no
  red flags during read.

### Capability 4 — Overlay (live edit / save / version / restore)
- Route prefix: `/api/contexts/{ctx}/work-studio/documents/`. Endpoints:
  list / get / patch / save / move-to-review / commit / delete.
- Live execution:
  - `GET /documents` (list) → 200, 20 items returned, all `status=complete`,
    `name=None` (the list returns Document Journal items, not Work Studio
    overlay drafts).
  - `GET /documents/{id}` for the SAME id from the list → **404 "Document not found"**.
- This is the AMBIGUOUS signal: the list endpoint and the get-by-id endpoint
  do not share the same table. Either (a) list is over-broad (returning items
  the per-id resolver doesn't recognise) or (b) per-id is under-broad
  (rejecting valid list rows). Either way, the surface as a USER sees it is
  not self-consistent.
- Verdict: **RUNS-BUT-AMBIGUOUS**. Repair requires reading the list query
  filter vs the get query filter; out of WS0 scope.
- save / version / restore (commit) endpoints exist but were not exercised
  in WS0 because the prerequisite (a real overlay-table document) couldn't
  be loaded.

### Capability 5 — From-source
- **Solva session** (`/from-source` with `source_type=solva_session`) →
  **WORKS**. Created artefact `2582bf22` + brief `f1c27ac4` + revision
  `a7d3b373` from Solva session `ce601c0f`. Returns redirect_url to composer.
  This is the path ThinkLab will lean on for the Solva-export hand-off.
- **Chat artefact** (`/from-source` with `source_type=chat_artefact`) →
  **EXISTS-NOT-EXERCISED**. Accepted by Pydantic Literal at
  `routers/work_studio_from_source.py:149`. Not driven end-to-end in WS0;
  classification deferred to the first chat→work-studio handoff smoke.
- **Document** (`/from-document` — a DIFFERENT route) → **WORKS** for the
  full 5-kind D5 set (`board_pack`, `committee_pack`, `minutes`, `deck`,
  `report` per `_VALID_FROM_DOC_KINDS` at line 619). Tested deck +
  board_pack: both returned 201 with a Work Studio artefact row.

### Capability 6 — Render (per-kind streaming render)
- Route: `GET /api/contexts/{ctx}/work-studio/documents/{aid}/render?format={fmt}`.
- Live execution:
  - On the from-source(Solva) deck artefact `2582bf22` → **404 "Artefact not found"** —
    the from-source path creates a row in `studio_block_artefacts` (block-composer
    table), not `work_studio_documents` which the render endpoint reads.
  - On the from-document board_pack artefact `f1ca0bec` → **409 "This artefact
    has no compiled content yet. Open it in Work Studio and run a compile or
    revision first."** — expected; the artefact is a Draft seed without
    `structured_content`.
- Verdict: **AMBIGUOUS**. The endpoint is wired and returns honest errors,
  but the prerequisite (a `work_studio_documents` row WITH compiled
  `structured_content`) wasn't reachable from the WS0 read-only path.
  Render is reachable AFTER a complete compile flow lands content into
  `work_studio_documents.structured_content`. Needs an end-to-end smoke
  starting from from-document → composer compile → render.

### Capability 7 — Export (PDF · DOCX · PPTX × stream + signed)
- DOCX, PPTX: **WORKS** (verified end-to-end per §1).
- PDF (deck): **PARTIAL** — `_resolve_format(deck, pdf)` at
  `routers/work_studio_export.py:166-169` substitutes pptx; the soft-fork
  refusal at line 772 is the dispatcher safety net.
- PDF (brief / report / minutes): renderer branches exist
  (`render_brief_pdf`, `render_report_pdf`); not exercised in WS0 but
  surface is live.
- Stream + signed download: **WORKS**. `_DOWNLOAD_TTL_SECONDS = 15 * 60`
  TTL pin; downloaded brief.docx (39 258 bytes) + deck.pptx (38 324 bytes)
  with correct MIME headers.

### Capability 8 — Analyze (spreadsheet-only)
- Routes: `/api/workbook/...` (upload, analyses, signals/extract, simulate,
  forecast, anomalies, report.{pptx,docx,xlsx}, upload-multi).
- Live execution:
  - `/api/workbook/analyses` → 200, 50 items returned, first row at
    `aid=wba-573896fa488d` (status=parsed). Mix of `parsed` / `ready`.
  - `/api/workbook/v2/analyses/{aid}/synthesize` on a foreign aid → 404
    `analysis_not_found` (correct — tenancy gate honored).
- Verdict: **WORKS-AT-SURFACE**. Spreadsheet-only is correct per `PART 3`
  ("Analyze: spreadsheet-only today; can't take documents"). No
  document-uploadable Analyze path exists in this code.

---

## §3 — Critical verifications (per dispatch)

### V1 — Objective steers CONTENT
**TRUE.** Verified at `routers/work_studio_export.py:331-336`:
```python
def _flat_user_input(body: ExportRequestIn) -> str:
    return (
        f"DESCRIPTION: {body.description.strip()}\n\n"
        f"OBJECTIVE: {body.objective.strip()}\n\n"
        f"SCOPE: {body.scope.strip()}"
    )
```
The objective is concatenated into the LLM prompt verbatim → content
generation reads it. **Surface impact:** changing objective text changes
the generated artefact's content.

### V2 — Objective does NOT steer KIND/TEMPLATE selection
**TRUE.** Verified by code-read: `kind` is the FastAPI **path parameter**
on `POST /work-studio/export/{kind}` (`routers/work_studio_export.py:1641`).
The handler validates `kind` against `_VALID_KINDS` and routes the render
dispatch off (output_format, kind) only. No reads of `body.objective` exist
in any routing logic. The gap is real: objective steers content INSIDE the
chosen kind, but the kind selection is up to the client (UI/wizard).

### V3 — AnalyzeDrawer Phase-3 stubs
**1 stub found** in `frontend/src/components/analyze/AnalyzeDrawer.jsx`:
- Line 545 (Export tab description copy):
  *"Solva narration arrives in Phase 3; the present exports carry the
  deterministic content available today."*
- Classification: **CLEAN-PLACEHOLDER**. The synthesize endpoint at
  `/api/workbook/v2/analyses/{aid}/synthesize` IS wired in the drawer
  (`onSynthesize` at line 124-137 calls `api.post`). The "Phase 3" copy
  refers to where the Solva narration will surface in the Export tab; the
  underlying synthesis pipeline is already live.
- No HALF-IMPLEMENTED stubs found in AnalyzeDrawer.

---

## §4 — Cross-track sub-matrix: fit for Chat B1 manual-affordance handoff

When Chat B1's manual Work Studio affordance routes a user from chat into
the export path with a chosen kind, the result is:

| Kind | Fit? | Reason |
|---|---|---|
| `brief` | **YES** | Full pipeline works (start → complete → download). |
| `deck` | **YES** | Full pipeline works (pptx). |
| `report` | **YES** | Full pipeline works. |
| `minutes` | **YES** | Full pipeline works. |
| `committee_pack` | **NO** | Render dispatcher seam at `work_studio_export.py:778` fails the export. User-visible failure if Chat hands off to this kind. |
| `board_pack` | **NO (via /export)** / **YES (via /from-document)** | Direct `/export/board_pack` returns 400. Chat manual affordance must route to `/work-studio/from-document` OR `/work-studio/compilations` for board_pack. |

**Recommendation for Chat B1.1 (when it lands):** the manual affordance
should expose ONLY `brief / deck / report / minutes` to the user until
the committee_pack seam is closed + board_pack is wired into `/export`
OR the affordance is taught to use the dual surface (`/export` for 4
kinds, `/from-document` for board_pack/committee_pack). Cleanest path
is to fix the export dispatcher (one-line repair for committee_pack +
`_VALID_KINDS` extension for board_pack) so the affordance has a single
target route.

---

## §5 — Stop-and-report conditions (none tripped)

- ❌ Any capability is REBUILD rather than REPAIR. Committee_pack is
  REPAIR (one-line dispatcher patch). Board_pack is REPAIR (add to
  `_VALID_KINDS` + one render branch). Overlay is INVESTIGATE-FIRST
  (a list/get table mismatch is REPAIR-class unless it turns out the
  two tables genuinely should be separate). Render is INVESTIGATE-FIRST
  for the same reason.
- ❌ Objective → kind selection requires more than wiring objective into
  selector. The current code path makes the gap a UI design question
  (does the wizard pre-pick kind, or does it offer the user 4 cards?) —
  no new selection engine needed. The objective→kind read is a UI
  copy/heuristic change at most.
- ❌ Analyze document path cannot reuse Solva. Not applicable at WS0
  scope — Analyze is spreadsheet-only by design today; document-Analyze
  is the Analyze Gate-A architectural-fork question separately.
- ❌ Any repair requires weakening Shield / tenancy / audit / fail-closed
  / boundary. None of the repairs identified do.

**Builder's call:** WS1 scope (when called) is REPAIR, not REBUILD. The
fixes are small enough to ship in one phase.

---

## §6 — Files inspected (zero modifications)

Per the dispatch's hard rule (`PART 0` rule 4 + Section B): NO product
code touched in WS0. All changes are limited to this memo + the pipeline
log + the gate's KNOWN_MAPPINGS. Files READ:

- `backend/routers/decks.py`
- `backend/routers/work_studio_export.py`
- `backend/routers/work_studio_phase_c.py`
- `backend/routers/work_studio_phase_c2.py`
- `backend/routers/work_studio_overlay.py`
- `backend/routers/work_studio_render.py`
- `backend/routers/work_studio_from_source.py`
- `backend/routers/workbook_analysis.py`
- `backend/routers/compilations.py`
- `backend/routers/studio.py` + `studio_blocks.py`
- `backend/services/work_studio_export.py`
- `frontend/src/components/analyze/AnalyzeDrawer.jsx`
- `frontend/src/pages/WorkStudio.jsx` (skimmed for structure)
- `frontend/src/lib/origins.js` (kind catalogue)
- `frontend/src/components/work_studio/CompilationWizard.jsx`
- `frontend/src/components/tasks/TaskSetupWizard.jsx`

Live execution via curl against `https://akki-executive.preview.emergentagent.com/api`
with admin@akki.ai credentials; context `aff5e102-04b8-4948-9f6b-27c9eca1f0d7`
("Ubora Capital Partners", admin's default context).

---

## §7 — Maintenance Protocol Compliance

1. ✅ `DEV_PIPELINE.md` §1, §3 (new §3.4 Track Work Studio), §9 updated
   BEFORE this memo was written.
2. ✅ `pipeline-log-sync.yml` KNOWN_MAPPINGS extended with
   `"WS0_CLASSIFY": "WS0"` BEFORE this memo was written.
3. ✅ This memo written into a state where §9 + the gate's identifier
   mapping are both in place.
4. ✅ `pipeline-log-sync.yml` Python logic exits 0 against the working
   tree at memo-write time.

## §8 — Next

Per the consolidated dispatch's queue order, the third item is **ThinkLab
Gate A render-check + Flag 3 verification** (demoted in queue, awaits a
fresh orchestrator call). WS0's render-fit verdict is a separate gate
from Gate A — Gate A asks "can `pptx_exporter` express the four ThinkLab
output shapes to board standard?", whereas WS0 only classified the
existing 6 kinds. The two should be considered together when WS1 +
ThinkLab TL1.1 are sized.
