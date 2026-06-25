Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md`

# JC-MON Stage 1 — Ingestion

> **Closed:** 2026-06-25
> **Acceptance:** 5 / 5 GREEN
> **Artefacts:** `/app/memory/jc_artifacts/JC-MON/01-ingest/`
> **Proving slice:** `/app/backend/scripts/jc_mon_stage_1_ingestion_slice.py`

---

## What this stage covers

The canonical-spec § Stage 1 ingestion model — three landings on
existing document/journal rails, no parallel store:

- **BASE docs** uploaded on the Monitor surface with both
  `use_for_tracking=true` AND `is_base_document=true` — the
  strategic plan / performance agreement.
- **TRACKING docs** uploaded ANYWHERE via the shared `UploadOptions`
  affordance with `use_for_tracking=true` only.
- **EMAILED docs** arriving via the inbound-email pipeline land in
  the Document Journal in **`state="pending"`** + **`source_channel="email"`**;
  a new pending-list endpoint surfaces them; a new accept endpoint
  flips them to `state="active"` (and optionally into the tracking
  set).

Plus the explicit Stage-1 dispatch decision-2 inclusion:
**`UploadOptions.jsx` sessionStorage memory** so a user flagging
multiple uploads in a row doesn't re-tick the checkbox each time.

## Discipline lock around the sessionStorage inclusion

In the Stage 0 finish summary I (the agent) flagged the sessionStorage
memory as a small back-pocket enhancement — explicitly out-of-scope
for Stage 0. The user has now decided to fold it into Stage 1 via
dispatch decision #2 = ii. This sprint memo documents that as a
**deliberate Stage-1 inclusion**, not a smuggled-in enhancement, so
future maintainers see the audit trail.

The memory:
- Lives in `UploadOptions.jsx` (the shared component) — not in any
  per-surface consumer
- Scoped by `testIdPrefix` so the same component in 2 different
  surfaces doesn't cross-bleed state
- Hydrates ONCE on mount (`hydratedRef`), persists on every change
- Storage key shape: `akki:upload-options:<testIdPrefix>:lastTracked`
  (FE evidence shows `akki:upload-options:upload-modal-options:lastTracked = 'true'`
  after a single tick).
- ~10 LOC inside the component itself; zero LOC at each consumer.
- Confirmed working via Playwright snapshot at
  `/app/memory/jc_artifacts/JC-MON/01-ingest/upload-modal-affordance.jpg`.

## Files touched

| Layer | File | Change |
|---|---|---|
| FE | `components/upload/UploadOptions.jsx` (NEW · 137 LOC) | Shared affordance with 2 checkboxes (tracking + base); sessionStorage memory hook scoped by `testIdPrefix`; a11y `aria-label`s + `title`s. |
| FE | `components/upload/UploadModal.jsx` | `uploadOptions` state + `<UploadOptions allowBase={false}>` render + 2 FormData append lines + reset-on-close. |
| FE | `pages/ContributorPortal.jsx` | `uploadOptions` state + `<UploadOptions allowBase={false} labelOverride="Mark this as performance evidence">` (friendlier copy for non-employees) + 1 FormData append. |
| FE | `components/monitor/ObjectivesProjectsPanel.jsx` | `uploadOptions` state + `<UploadOptions allowBase={true}>` (only surface that surfaces the base-doc checkbox) + 2 FormData append lines. |
| BE | `routers/documents.py:upload_document` | 2 new optional form fields: `use_for_tracking`, `is_base_document` (both default `False`). Threaded into the document row insert. |
| BE | `routers/documents.py:sanitize_doc` | Surfaces both new fields on every read so the FE can show them. |
| BE | `routers/documents.py` | NEW `GET /contexts/{cid}/documents/pending` (lists pending emailed docs; tolerant of missing `context_id` since email-pipeline docs may lack one). |
| BE | `routers/documents.py` | NEW `POST /contexts/{cid}/documents/{doc_id}/accept` (flips `state="pending"→"active"`, optionally turns on `use_for_tracking`, backfills `context_id`, writes an audit row). |
| BE | `routers/tasks.py:contributor_upload` | 1 new optional form field: `use_for_tracking` (additive on the public route). `is_base_document` NOT exposed publicly — base-doc designation is owner-side only. |
| BE | `routers/inbound_email.py` | Email-pipeline docs now write `state="pending"` (was `"draft"`) + `source_channel="email"`. Both `use_for_tracking` + `is_base_document` default `False` on arrival. |

**Additive only.** No schema migration. No regression on existing
documents (callers without the new form fields still send valid
requests; default values preserve prior behaviour).

## Backend payload contract — the four landings

| Landing | Endpoint | Form payload | Resulting row |
|---|---|---|---|
| BASE | `POST /api/contexts/{cid}/documents` | `use_for_tracking=true, is_base_document=true` | `state=active, origin=upload, source_channel=upload, use_for_tracking=true, is_base_document=true` |
| TRACKING (anywhere via shared affordance) | `POST /api/contexts/{cid}/documents` | `use_for_tracking=true` | `state=active, origin=upload, source_channel=upload, use_for_tracking=true, is_base_document=false` |
| EMAILED (arrives) | (inbound-email pipeline writes directly) | n/a | `state=pending, origin=email_receipt, source_channel=email, use_for_tracking=false` |
| EMAILED (accepted) | `POST /api/contexts/{cid}/documents/{did}/accept` body `{"use_for_tracking": true}` | `state=active, source_channel=email, use_for_tracking=true, context_id=<backfilled>` |

## Acceptance ledger (5 / 5 GREEN)

```
[✓] S1.a — BASE doc landed with both flags set
       flags={'doc_id': '23f38df4-...', 'use_for_tracking': True, 'is_base_document': True}
[✓] S1.b — TRACKING doc landed with use_for_tracking only
       flags={'doc_id': 'c859fe17-...', 'use_for_tracking': True, 'is_base_document': False}
[✓] S1.c — EMAILED doc landed in pending state + listed
       pending={'doc_id': 'doc-42d65f4e2a', 'state': 'pending', 'source_channel': 'email', 'found_in_pending': True}
[✓] S1.d — EMAILED doc accepted → state=active + tracking on + context_id backfilled
       accept={'doc_id': 'doc-42d65f4e2a', 'accept_status': 200, 'post_state': 'active',
                'use_for_tracking': True, 'context_id_backfilled': True}
[✓] S1.e — Two consecutive tracking uploads honour the flag (BE side)
       both BE requests landed with use_for_tracking=true (sessionStorage hook tested via FE)
```

## Stage-1 inventory consumers — 3 wired, 4 deferred (batch later)

Per the Q2 inventory's integration-order plan:

**Wired in this stage** (the three the proving slice exercises):
1. `UploadModal` — primary affordance
2. `ObjectivesProjectsPanel` — Monitor surface (only surface with
   `allowBase=true`)
7. `ContributorPortal` — public surface (with friendlier copy variant)

**Deferred to a Stage-1 batch follow-up** (not blocking the
proving-slice STOP-and-show):
3. `CompilationWizard`
4. `WorkStudioAnalyze`
5. `AnalyzeJournal`
6. `ContributionAttachPicker`

Each batch consumer is ~5 LOC: import the component, add a state hook,
render the affordance, thread the boolean into the FormData. The
backend already accepts the form field on the canonical endpoint;
batching the 4 consumers is a small follow-up commit and does NOT
block Stage 2a from starting.

## Scope cuts (called out)

- **The base-doc checkbox is rendered on `ObjectivesProjectsPanel`
  only**, per the Q2 inventory. The 6 other in-scope surfaces pass
  `allowBase={false}`; the BE accepts both fields on every surface
  but only the Monitor surface exposes the second checkbox.
- **The pending-list endpoint scopes by account ownership** when the
  email-pipeline doc lacks `context_id` (which is normal — emails
  arrive bound to a task, not a context). The accept endpoint
  backfills `context_id` so subsequent Journal listings find the row.
- **Email arrival uses `state="pending"`** which is a NEW state
  value. Existing states (`draft`, `active`, `committed`,
  `closed`, `archived`) are byte-stable. Pre-Stage-1 email-pipeline
  docs that wrote `state="draft"` are unaffected — they remain at
  `draft` and the user can still find them via the existing Journal
  listing.

## STOP point reached

Stage 1 has surfaced its proving slice with 5/5 GREEN + FE affordance
screenshot. Per the dispatch's "STOP and show before Stage 2a"
discipline, Stage 2a starts after the user surface-and-go's the
Stage-1 evidence package. The canonical-spec § Stage 2a thin slice is
unblocked by the Stage-0 Q4 thin-adapter verdict + the Stage-1
ingestion landing the three doc kinds the assessment engine will
read against.

## Standing-rules check

- [x] No remote pushes
- [x] No JC-WS Generate-Document UI touched
- [x] No JC-TM regression (additive backend fields; `state="pending"`
      is a new value, prior `state="draft"` flows byte-stable)
- [x] Real artefacts on disk (5 JSON + 1 screenshot)
- [x] sessionStorage enhancement explicitly documented as
      Stage-1-deliberate inclusion (user dispatch decision #2 = ii),
      not smuggled in
- [x] Bash + pytest + proving-slice scripts only — no testing subagent
- [x] `LLM_MODELS_REFRESH` still parked
- [x] JC-UI-DRAWER untouched (separate future dispatch)
