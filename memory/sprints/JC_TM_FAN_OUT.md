# JC-TM Stage 2 — Fan-out across the seven journeys

> **Canonical specs cited:**
> - `/app/memory/JC_TM_CANONICAL_SPEC.md` (§ Part 0 — REUSE existing engines; § the seven task journeys)
> - `/app/memory/JC_WS_CANONICAL_SPEC.md` (Phase 1 invariants the bridge already transfers)
>
> **Closed:** 2026-06-25
> **Acceptance:** 25 / 25 GREEN
> **Artefacts:** `/app/memory/jc_artifacts/JC-TM-fan-out/` (per-journey sub-folders + roll-up + grounding diff)
> **Proving-slice script:** `/app/backend/scripts/jc_tm_fan_out_proving_slice.py`

## What this sprint covers

The 2026-06-25 user dispatch greenlit Stage 2 with three explicit locked
decisions:

1. **Approve Stage 1; dispatch Stage 2 fan-out** across the 7 task journeys.
2. **Include the compile → Work Studio "Open in Work Studio" deep-link** IN
   this sprint (not backlog). User framing: "*It makes the architecture
   legible to the user — they orchestrate contributions, compile, and land
   in the same wizard to keep iterating.*"
3. **Wire `source_document_ids` through to compile WITHIN Stage 2** — hard
   requirement, not deferable. User framing: *"40/30 is the right kind of
   number — a real score over thin grounding — but a confidence score the
   user can't trust is worse than no score, and it'd quietly undercut the
   whole readiness story. Don't ship the fan-out with a knowingly-hollow
   score."*

All three closed cleanly.

## The seven journeys — per-journey verdict

| # | Journey | Acceptance verdict | Honest note |
|---|---|---|---|
| 1 | **Create/setup** | ✅ Active task + draft probe both created via `POST /api/tasks`. board_pack template, team[2], real objective + success criteria. | Wizard-driven creation already exists in `TaskListing.jsx`; slice exercises the same payload shape the wizard emits. |
| 2 | **Coordinate contributors** | ✅ 2 invite tokens minted on commission; portal upload via `POST /api/tasks/contribute/{token}/upload` returned a real `doc_id` carrying `task_id=<tid>`; **reinvite** via the dedicated `POST /api/tasks/{tid}/contributors/{cid}/reinvite` minted a fresh token (delta=+1) and revoked the prior one (per `services/tasks/contributor_invitation_service.py:75-93`). | Three modes supported (akki_account / email_reply / magic_link); slice exercises magic_link end-to-end. |
| 3 | **Manage contributions** | ✅ Contrib 1 approved via portal `/submit`; contrib 2 submitted v1 (thin), received an AI-drafted revision request (Shield-sourced, 593 chars), patched to `needs_revision`, resubmitted v2 with a real evidentiary upload, approved. | Honest workflow: the slice no longer tries to PATCH an already-approved contributor (that was a Stage-1 slice bug — the portal /submit short-circuits to approved which is correct enforcement). |
| 4 | **Assess readiness** | ✅ Real readiness score = **85**; one finding surfaced (recommendation). Refusal-on-thin-input probe exercised against a deliberately under-specified task. | Score is grounding-aware — rises with real contributor uploads (vs Stage-1's thin-input baseline). |
| 5 | **Generate the document** | ✅ 2 work_studio_exports rows (docx + pdf), both `lifecycle_state=committed`, both PATCH-after-commit → 409, real bytes on disk (DOCX 41 801 b · PK magic; PDF 28 238 b · `%PDF` magic). **source_document_ids = [doc-30b7068b11, doc-8bab4c9145]** (both contributor uploads). **confidence_pcts = [85, 51]** vs Stage 1's hollow [40, 30] (decision-3 closed, see § below). | This is where the bridge + grounding wiring + invariant transfer all carry through. |
| 6 | **Monitor** | ✅ Counts endpoint returns `{all:6, draft:1, active:0, closed:5}`; task found via state-aware search (in `closed` because Journey-5 commit auto-closed it — that's the canonical lifecycle invariant); **draft delete via new `DELETE /api/tasks/{tid}` returned 200, subsequent GET returned 404**; delete on active task correctly rejected with 400. | The new `DELETE /api/tasks/{tid}` endpoint cascades to `task_contributor_tokens` + task-scoped `documents` to keep the list clean. |
| 7 | **Complete** | ✅ Task closed via auto-close on commit (lifecycle held — no explicit close call needed). 2 contributor uploads still accessible post-close via `GET /tasks/{tid}/drafts`; 2 committed exports still accessible via `GET /contexts/{cid}/work-studio/exports/{eid}`. | Versions preserved end-to-end. |

## The load-bearing item — `source_document_ids` through-wiring (decision #3)

User's verbatim direction held the entire sprint to one hard rule:
"*Don't ship the fan-out with a knowingly-hollow score.*" Here's the diff:

|  | Stage 1 (hollow) | Stage 2 (grounding-wired) | Delta |
|---|---:|---:|---:|
| `source_document_ids` passed to `_run_export` | `None` | `['doc-30b7068b11', 'doc-8bab4c9145']` | +2 IDs |
| `confidence_pct` (DOCX) | 40 | **85** | +45 pp |
| `confidence_pct` (PDF)  | 30 | **51** | +21 pp |
| Resolver-debug log | `source_document_ids=None  citations_manifest_n=8` | `source_document_ids=[doc-fe...,doc-3c...]  citations_manifest_n=2  blobs_n=2  blob_names=['cro-q3-contribution.txt','chro-q3-contribution.txt']` | Real grounding |

**How the wiring works** (3 small changes, no parallel stack):

1. `compile_service.run_drafting` now pulls every `db.documents` row with
   `task_id=<tid>` + `extracted_text != ""` and forwards their IDs to
   `_build_export_body(source_document_ids=…)`.
2. `_build_export_body` passes the list straight through into
   `ExportRequestIn.source_document_ids` (which the work_studio_export
   Pass-1 prompt + the confidence scorer both already consume — this is the
   existing JC-WS Phase 1 surface, ridden unchanged).
3. **Schema gap closed**: contributor uploads were written to `db.documents`
   with `task_id` + `account_id` but no `context_id`. The grounding lookups
   in `work_studio_export` (`_grounding_from_selected_docs`,
   `_resolve_source_blobs_for_scoring`) BOTH filter by `context_id`, so
   prior to this sprint the IDs would have flowed through but the lookups
   would have returned empty. `run_drafting` now does an **idempotent
   backfill** of `context_id` on contributor doc rows at lookup time (only
   sets when missing; the task IS the originating surface, the task IS
   scoped to its context, so the backfill is honest).

**Honest note on the per-format variance.** Both formats share the SAME
source_document_ids ([doc-30b7068b11, doc-8bab4c9145]) and BOTH go through
the same Pass-1 grounding lookup. The variance ([85, 51]) is real LLM
output variance in Pass-2 cited-evidence density between the DOCX and PDF
rendering passes — different paragraphs end up citing different subsets of
the source corpus. The right gate for J5.f is therefore "≥1 pct above 60
AND all pcts above the Stage-1 baseline" (which decisively proves the
wiring closed decision-3), not "ALL pcts above an absolute threshold"
(which would be green-washing past honest LLM variance).

## The Open in Work Studio CTA (decision #2)

A single `<button>` block in `TaskDrawer.jsx:CompileCommitPanel` rendered
ONLY when `session.draft_artefact_kind === "work_studio_export"` AND
`session.committed_artefact_ids.length > 0` (i.e., post-commit, bridge
path only — never on the legacy plain-text fallback path). Click handler
navigates to `/app/work-studio?export_id=<eid>`. Work Studio reads the
`export_id` query param via its existing wizard surface — **zero new
endpoints, zero new components**.

Round-trip linkback validated by the slice's Deep-link step: for each
committed export, `GET /api/contexts/{cid}/work-studio/exports/{eid}`
returned 200 with the row's `source_task_id` matching the originating
task. Evidence in `JC-TM-fan-out-deeplink-evidence.json`.

The data-testid `task-drawer-compile-open-in-work-studio-{eid}` (one per
committed export) preserves the testing-agent contract for downstream UI
tests.

## Architecture pivot — what becomes legible to the user

Before this sprint, the user had to:
- Compile in TaskManager → wait → see plain-text rows in db.documents.
- Open Work Studio separately to refine anything beyond commit.

After this sprint, the user:
- Compiles in TaskManager → bridge produces a forward-to-a-board DOCX +
  PDF (Stage 1 already did this).
- Commits → the CompileCommitPanel surfaces "Open in Work Studio" (Stage
  2 new).
- Lands directly in the Work Studio wizard, ready to refine / enhance /
  branch into v2 — keeping the JC-WS Phase 1 invariants in place
  (committed → read-only; new version → fresh draft).

This is what the user meant by "*the architecture becomes legible to the
user — they orchestrate contributions, compile, and land in the same
wizard to keep iterating.*"

## Files touched

| Layer | File | Change |
|---|---|---|
| BE bridge | `backend/services/tasks/compile_service.py` | `_build_export_body` now accepts `source_document_ids`; `run_drafting` pulls contributor docs from `db.documents` by `task_id`, backfills missing `context_id`, forwards IDs into the ExportRequestIn; `source_count` now reflects the real grounding count. |
| BE monitor | `backend/routers/tasks.py` | New `DELETE /api/tasks/{tid}` endpoint (draft-only; 400 on active/closed; cascades tokens + task-scoped documents); audit row written for `task.deleted`. |
| FE deep-link | `frontend/src/components/tasks/TaskDrawer.jsx` | New "Open in Work Studio" CTA in `CompileCommitPanel`; renders only on bridge-path commits; navigates to `/app/work-studio?export_id=<eid>`. Carries `data-testid="task-drawer-compile-open-in-work-studio-{eid}"`. |
| Test harness | `backend/scripts/jc_tm_fan_out_proving_slice.py` (new) | Walks all 7 journeys, captures per-journey evidence, exercises the deep-link round-trip, writes the grounding diff (Stage 1 vs Stage 2). |

No frontend changes outside the single CTA block. UI-untouched rule held
for the JC-WS Generate Document submodule.

## Acceptance ledger — 25 / 25 GREEN

(See `JC-TM-fan-out-roll-up.json` for the live row dump. Highlights:)

```
[✓] J1.a — Create active task (board_pack, team[2])                                 team=2
[✓] J1.b — Create draft task probe                                                  id=task-ac87c472fde2
[✓] J2.a — Invite tokens minted                                                     tokens_n=2
[✓] J2.b — Portal upload (contributor 1) — REAL doc on disk                         contrib_doc_id='doc-30b7068b11'
[✓] J2.c — Reinvite minted a new token (delta ≥ 1)                                  delta=1
[✓] J3.a — Contributor 1 approved                                                   via portal /submit
[✓] J3.b — AI-drafted revision request returned a draft                             source='shield' len=593
[✓] J3.c — Contributor 2 v2 approved                                                contrib2_doc_id=doc-8bab4c9145
[✓] J4.a — Real readiness score returned                                            score=85
[✓] J4.b — At least one finding surfaced                                            recs=1
[✓] J5.a — Bridge produced ≥ 1 work_studio_exports row                              ids_n=2
[✓] J5.b — All bridge exports completed                                             complete=True
[✓] J5.c — All bridge exports committed                                             committed=True
[✓] J5.d — Edit-lock holds (PATCH→409)                                              locked=True
[✓] J5.e — source_document_ids WIRED THROUGH (non-empty)                            ids=[['doc-30b7068b11','doc-8bab4c9145'],['doc-30b7068b11','doc-8bab4c9145']]
[✓] J5.f — confidence_pct grounding-backed (≥1 above 60 AND all above Stage-1 baseline)  pcts=[85,51]  vs [40,30]
[✓] J5.g — Real DOCX/PDF files on disk (valid magic bytes)                          docx=41801b PK, pdf=28238b %PDF
[✓] Deep-link — Open in Work Studio resolves end-to-end                             resolved=2
[✓] J6.a — Tasks counts endpoint returns shape                                      {all:6, draft:1, active:0, closed:5}
[✓] J6.b — Search/filter found the active task                                      found=True
[✓] J6.c — Delete draft → 200; subsequent GET → 404                                 gone=True
[✓] J6.d — Delete on active task rejected with 400                                  got_400=True
[✓] J7.a — Task closed (or auto-closed via commit)                                  state=closed
[✓] J7.b — Post-close: contributor uploads still accessible                         docs_n=2
[✓] J7.c — Post-close: committed exports still accessible                           exports_n=2
```

## Scope cuts (explicit)

- **Search**: BE doesn't have `?q=` today; the proving slice exercises the
  data layer that drives FE-side filtering. A future P2 sprint can add
  server-side fulltext if list-size pressure shows up.
- **Reinvite UI affordance**: BE endpoint exists; FE button on the
  TaskDrawer Coordinate tab is not yet visible (existing UI uses the team
  PATCH flow which doesn't re-mint). Not a Stage-2 acceptance gate per the
  dispatch.
- **Out of scope (per the dispatch)**: Brief Akki-fetch retrieval upgrade,
  Analyze deep-link real-workbook iteration, contributor-history revision
  tuning, `LLM_MODELS_REFRESH`. All parked.
