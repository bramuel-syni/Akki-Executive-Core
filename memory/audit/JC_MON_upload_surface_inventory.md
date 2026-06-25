# JC-MON Stage 0 · Q2 — Tracking-checkbox upload-surface inventory

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md`
>
> **Purpose:** Inventory EVERY upload surface in the app, then design
> ONE shared `UploadOptions` affordance to drop in (not reimplemented
> per-surface). The canonical-spec rule: "Implement as ONE shared
> UploadOptions affordance dropped into each — not reimplemented per
> surface."
>
> **Counts** — 12 file-upload surfaces total · 7 in-scope (gets the
> shared affordance) · 5 out-of-scope (transient artefacts not
> persisted to `db.documents` for tracking).
>
> **Surface count is large but bounded** — under the canonical spec's
> ">5 surfaces → report the count before touching many" rule, this doc
> IS that report. The implementation is one component file + 7 import
> sites; the per-surface footprint is 3-5 LOC each.

---

## 1 · The shared `UploadOptions` component

Lives at `frontend/src/components/upload/UploadOptions.jsx` (new).
Stateless presentational. Two checkboxes:

```
[ ] Use this document for performance tracking
[ ] Mark as base document          ← shown only when `allowBase={true}`
```

API:
```typescript
type UploadOptionsState = {
  useForTracking: boolean;     // → use_for_tracking=true in upload POST
  isBaseDocument: boolean;     // → is_base_document=true (Monitor surface only)
};

<UploadOptions
  value={state}
  onChange={setState}
  allowBase={false}            // Monitor page sets this to true
  testIdPrefix="upload-options-<surface-id>"
/>
```

Each consumer threads the `useForTracking` boolean into the FormData
body of its upload POST (existing endpoints accept it as a new optional
form field — backend addition in Stage 1).

---

## 2 · Full upload-surface inventory

| # | Surface | File | Purpose | Posts to `db.documents`? | Affordance | Notes |
|---|---|---|---|:---:|:---:|---|
| 1 | **UploadModal** | `components/upload/UploadModal.jsx:434` | Document Journal modal — the primary org-wide upload affordance | ✅ | **IN-SCOPE** | Canonical entry point. Used from `/app/documents`, `?upload=1` deep-link, AppShell quick-action. |
| 2 | **ObjectivesProjectsPanel** | `components/monitor/ObjectivesProjectsPanel.jsx:326` | Monitor objectives panel — direct upload from the Monitor surface | ✅ | **IN-SCOPE + `allowBase=true`** | The ONE surface where `Mark as base document` is offered. Future-Stage-1: also surface a "PENDING" filter for emailed-in docs (per Stage 1 ingestion model). |
| 3 | **CompilationWizard** | `components/work_studio/CompilationWizard.jsx:881` | Work Studio compile-job source upload | ✅ | **IN-SCOPE** | Sources persisted to `db.documents` so they show in Journal AND become tracking-eligible. |
| 4 | **WorkStudioAnalyze** | `pages/WorkStudioAnalyze.jsx:189` | Workbook upload for Solva v2 Analyze | ✅ | **IN-SCOPE** | Workbooks ARE often performance evidence (financial models, KPI dashboards). Tracking flag aligns. |
| 5 | **AnalyzeJournal** | `pages/AnalyzeJournal.jsx:183` | Journal-level Analyze listing upload | ✅ | **IN-SCOPE** | Same as #4. |
| 6 | **ContributionAttachPicker** | `components/cycle/ContributionAttachPicker.jsx:221` | Cycle contribution attachments | ✅ | **IN-SCOPE** | Contributions are exactly the kind of evidence Monitor reads. |
| 7 | **ContributorPortal** | `pages/ContributorPortal.jsx:256` | Public magic-link contributor portal (JC-TM Stage 2) | ✅ | **IN-SCOPE** | Contributor uploads ALREADY flow to `db.documents` with `task_id`. Public surface — the checkbox copy needs to be friendly to non-employees ("Mark this as performance evidence" instead of internal jargon). |
| 8 | **EnhanceModal** | `components/studio/EnhanceModal.jsx:659` | Enhance an existing artefact with a new source | ❌ transient | **SKIP** | Enhance sources are transient — they don't persist as Journal docs. Tracking flag would be misleading. |
| 9 | **Chat attachment** | `pages/Chat.jsx:2047` | Chat-message attachment | ❌ transient | **SKIP** | Chat attachments are conversational context, not Journal docs. Many are one-shot images / pdfs the user references mid-conversation. |
| 10 | **Solva AttachDocumentModal** | `components/solva/AttachDocumentModal.jsx:171` | Attach doc to Solva voice-audit context | ❌ transient | **SKIP** | Solva audit context — bounded to one coaching session. Not Journal-eligible. |
| 11 | **Solva FramingScreen** | `components/solva/flow/FramingScreen.jsx:213` | Initial framing upload on Solva voice-audit entry | ❌ transient | **SKIP** | Same as #10. |
| 12 | **BlockComposer** | `components/studio/BlockComposer.jsx` | Block-composer asset upload (briefing/deck/report assets) | ❌ transient | **SKIP** | Block-composer assets are per-block static media (images, charts) embedded into the artefact. Not Journal docs. |

**Total: 12 surfaces · 7 IN-SCOPE · 5 SKIPPED.**

---

## 3 · Per-surface integration plan

The plan for each IN-SCOPE surface is 3-5 LOC: import the component,
add a state hook, render below the file input, thread the boolean into
the FormData on submit.

| # | Surface | Existing FormData call | New line | LOC delta |
|---|---|---|---|---:|
| 1 | UploadModal | `formData.append("file", f)` | `formData.append("use_for_tracking", uploadOptions.useForTracking ? "true" : "false")` | +5 |
| 2 | ObjectivesProjectsPanel | (same shape) | + `is_base_document` for the Monitor page | +6 |
| 3 | CompilationWizard | (same) | (same) | +5 |
| 4 | WorkStudioAnalyze | (same) | (same) | +5 |
| 5 | AnalyzeJournal | (same) | (same) | +5 |
| 6 | ContributionAttachPicker | (same) | (same) | +5 |
| 7 | ContributorPortal | (same — public surface) | (same, with friendlier copy override via prop) | +5 |

Total surface-side LOC: ≈ 36. Plus the new `UploadOptions.jsx`
component (≈ 70 LOC).

---

## 4 · Backend payload contract

The canonical upload endpoint
`POST /api/contexts/{context_id}/documents` (routers/documents.py:385)
currently accepts:

```
file, display_name, description, data_trust, mentioned_account_ids,
related_doc_id, relation_type, category
```

Stage 1 adds **two optional form fields**:

```
use_for_tracking: Optional[bool] = False
is_base_document: Optional[bool] = False
```

Both default false, both flow straight onto the document row.
**No new endpoint; additive only.** The ContributorPortal upload route
(`POST /api/tasks/contribute/{token}/upload`) gets the same two
optional fields — additive on a public route, no security regression
(both fields are bool, both default false).

---

## 5 · Scope cuts (explicit)

- **Per-surface UX copy variants** — the component's `testIdPrefix` and
  optional `labelOverride` props handle the ContributorPortal's
  friendlier wording. No A/B testing scaffold; one canonical label per
  surface, locked at integration time.
- **Drawer-width / drawer-pattern** — explicitly OUT OF SCOPE per the
  JC-MON canonical spec scope guardrails (`JC-UI-DRAWER` is a separate
  future dispatch).
- **Bulk-tracking-flag toggle** in the Document Journal (e.g. select-N
  docs → "mark all for tracking") — out of scope; the flag lives at
  point-of-upload only. The Journal will surface the flag as a chip on
  each row (Stage 1 read-side display), but bulk-mutation lives in a
  later P2 polish.

---

## 6 · Implementation order (gated by Stage 0 close-out)

1. Ship `UploadOptions.jsx` (new component, no consumer wires yet).
2. Backend: add `use_for_tracking` + `is_base_document` to the two
   upload endpoints + `db.documents` schema (Stage 1).
3. Wire surfaces 1, 2, 7 first (UploadModal, ObjectivesProjectsPanel,
   ContributorPortal) — these are the three the proving slice
   exercises. The remaining 4 (CompilationWizard, WorkStudioAnalyze,
   AnalyzeJournal, ContributionAttachPicker) ship in batch later in
   Stage 1.

---

## 7 · Verdict

**12 surfaces inventoried · 7 in-scope · ONE shared component is the
right shape (matches the canonical-spec rule). Surface count is large
but bounded; the per-surface footprint is small (3-5 LOC). Implement
the component first, then wire 3 surfaces for the Stage 1 proving
slice, then batch the remaining 4.**

**Total implementation footprint:** ≈ 110 LOC across 1 new component
+ 7 small touch-ups + 2 backend additive form fields. No reshape, no
regression risk. Proceed to Stage 1.
