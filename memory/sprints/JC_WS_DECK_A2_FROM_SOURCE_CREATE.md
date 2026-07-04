**Canonical Spec:** User dispatch **2026-07-02** (`JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE` build sprint, revised order A3 → A2 → rename arc, passenger rule active) + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A2`.

# JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE

**Type:** Build sub-sprint. **Third Path A dispatch.**
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a2_proving_slice.py` (15 rows). Testing sub-agents BANNED.
**Locked-area sweep:** F.6 Shield contract untouched · JC-CHAT invariants untouched · Solva engine untouched · storage arc untouched · OAuth untouched · Monitor untouched · Surface A (`/app/decks`) untouched.

---

## 0. Executive Summary

Path A's third dispatch closes the From-Source create journey on Surface B (`CreateArtefactModal`). Five DECK-XXX stories flip via multi-select adaptation + alpha-sort + in-modal upload trigger. The pulse-mirror passenger from A3 rides successfully to `DocumentRow` (aggregates listing) via the `work_studio_export_id` bridge field on `db.documents` rows.

**What shipped:**

| Story | State | How |
| :--- | :--- | :--- |
| DECK-017 | ❌ MISSING → ✅ MET | `sortByNameAlpha(items)` helper applied post-fetch on the briefs list (uses `localeCompare` with `sensitivity: "base"`). |
| DECK-018 | ❌ MISSING → ✅ MET | Backend `CreateArtefactRequest.source_brief_ids: List[str]` (`model_validator` coerces legacy singular → plural + logs deprecation WARNING). Frontend replaced native `<select>` with a checkbox list using the existing `@/components/ui/checkbox` primitive. Body seed concatenates each brief's active-revision prose with `\n\n---\n\n` divider + a header line per brief when >1 selected. |
| DECK-020 | ❌ MISSING → ✅ MET | Same `sortByNameAlpha(items)` helper applied to the documents list. |
| DECK-021 | ❌ MISSING → ✅ MET | "+ Upload new document" affordance mounted inside the doc picker; opens the existing `UploadModal` on top of `CreateArtefactModal` (Radix Dialog stacks natively). On `onUploaded(newDoc)`: refetch docs list, then auto-select the new doc id once it appears in the refetched list. See §X for the `UploadOptions` → `UploadModal` clarification. |
| DECK-022 | ❌ MISSING → ✅ MET | Same shape as DECK-018 for `source_document_ids`. |

**Passenger (pulse-mirror on `DocumentRow`):** ✅ SHIPPED. `?pulse=<work_studio_exports_id>` on URL → DocumentRow matches via `row.work_studio_export_id === pulseId` (the canonical bridge field on `db.documents` rows set by `_create_continue_chat`). Applies the shared `.ws-doc-card-pulse-glow` keyframe. No new CSS. Scroll-into-view remains only on `DocumentCardsSection` per non-racing rule.

**Backend touched:** `work_studio_from_source.py` — `CreateArtefactRequest` model + endpoint logic (~90 LOC net; substantial rewrite of the source-resolution branches).
**Frontend touched:** `CreateArtefactModal.jsx` (~140 LOC — checkbox lists + upload trigger + auto-select + payload plural) · `WorkStudio.jsx` `DocumentRow` (~10 LOC — pulse-mirror passenger).
**Chrome conformance HARD rule honoured:** checkboxes = existing `Checkbox` primitive; upload = existing `UploadModal`; no new components, no new endpoints, no new npm deps.

---

## §X. Component Naming Clarification (UploadOptions vs UploadModal)

**User dispatch text:** *"Mount existing `UploadOptions` component inside CreateArtefactModal, wired to existing `/documents/upload` endpoint."*

**R0 scan discovery:** `UploadOptions.jsx` (JC-MON Stage 1, 2026-06-25) is a **stateless presentational checkbox affordance** for "Use for performance tracking" + "Mark as base document" flags. It does NOT do file upload — it's the meta-options surface on OTHER upload flows.

The **actual file-upload dialog** is `UploadModal.jsx` — a heavyweight Radix Dialog with drag-and-drop, file picker, metadata form, trust level, category dropdown, and multipart POST to `/api/contexts/{cid}/documents/upload`.

**Interpretation:** The user's spec conflated the two names. The functional intent (mount an existing upload affordance inside CreateArtefactModal, don't build a new one) unambiguously points at `UploadModal`. Chrome conformance HARD rule applied — reused `UploadModal` verbatim (no fork, no wrapper, no new component).

**Radix Dialog nesting:** `UploadModal` opens as a sibling `<Dialog>` in the same React subtree (via `<>...</>` fragment in CreateArtefactModal's return). Radix handles focus-trap + z-index stacking natively. No custom modal manager needed. State preservation of the outer CreateArtefactModal is guaranteed (React reconciliation).

---

## 1. Chrome Conformance HARD Rule (self-audit)

| Story | Chrome conformance verdict |
| :--- | :--- |
| DECK-017 / DECK-020 (alpha sort) | Pure JS `.sort()` in the fetch handler. Zero chrome introduced. |
| DECK-018 / DECK-022 (multi-select) | Native `<select>` replaced by `Checkbox` component from `@/components/ui/checkbox` (same primitive used by `UploadOptions`, `TaskSetupWizard`, `CompilationWizard`, etc.). Same border/rounded-sm/hover styling as the existing radio-button source picker in the same modal — visually native. |
| DECK-021 (in-modal upload) | Existing `UploadModal` mounted as a nested `<Dialog>`. No fork, no wrapper, no new component. Existing `/documents/upload` endpoint (multipart) — no new endpoint. |
| Passenger (pulse-mirror) | Existing `.ws-doc-card-pulse-glow` CSS keyframe from A3 — zero new CSS. Existing `data-pulse` attribute pattern. Existing `?pulse=` URL param plumbing. Bridge via existing `work_studio_export_id` field on `db.documents` rows. |

---

## 2. Backend Contract Change · Backward-Compat Design

**Model:** `CreateArtefactRequest` now carries **both** singular + plural fields:

```py
class CreateArtefactRequest(BaseModel):
    kind: Literal["deck", "report"]
    title: str
    source: Literal["blank", "brief", "external_document"]
    source_brief_ids: List[str] = Field(default_factory=list, max_length=25)
    source_document_ids: List[str] = Field(default_factory=list, max_length=25)
    # DEPRECATED singular (backward-compat, will be removed in a follow-on)
    source_brief_id: Optional[str] = None
    source_document_id: Optional[str] = None

    @model_validator(mode="after")
    def _coerce_singular_to_plural(self) -> "CreateArtefactRequest":
        if self.source_brief_id and not self.source_brief_ids:
            self.source_brief_ids = [self.source_brief_id]
            logger.warning("create_artefact.deprecated_singular_field field=source_brief_id ...")
        if self.source_document_id and not self.source_document_ids:
            self.source_document_ids = [self.source_document_id]
            logger.warning("create_artefact.deprecated_singular_field field=source_document_id ...")
        return self
```

**Follow-on dispatch trigger:** grep production logs for `create_artefact.deprecated_singular_field`. When zero hits over a rolling 7-day window, ship a follow-on that removes singular fields + validator + backward-compat mirrors on the DB row.

**DB row:** artefact rows in `db.decks` / `db.reports` now carry **both** plural + singular fields (singular = first-element mirror). Consumers can migrate to plural at their own pace.

**Downstream grep audit (per lesson #6 file-name-from-YAML/AST discipline):**
* `admin_extractions.py:122,125` — reads `source_document_id` on task rows (unrelated model, out of A2 scope).
* `admin_tenants.py:177,180` — same.
* `work_studio_overlay.py:368,675` — reads `source_document_ids` (already plural, no change).
* `work_studio_export.py` — reads `source_document_ids` (already plural).
* `documents.py`, `documents/**` — irrelevant.
* Frontend `TasksInitiativesPanel.jsx` reads `task.source_document_id` — different model (tasks), not artefact. Out of A2 scope.
* Frontend `DocumentOverlay.jsx:699,700,1113` reads `report.audit.source_document_ids` (already plural, no change).

**Zero downstream consumers of the CreateArtefactRequest singular fields.** Backward-compat is defensive, not required by any existing reader.

---

## 3. Product Code Changes

### 3.1 Backend

**`/app/backend/routers/work_studio_from_source.py`:**
* Import `model_validator` from pydantic.
* `CreateArtefactRequest` extended with plural fields + coercion validator + WARNING logs.
* `create_work_studio_artefact` endpoint refactored:
  * `if body.source == "brief"` branch iterates `body.source_brief_ids`, fetches each brief, concatenates prose with divider.
  * `if body.source == "external_document"` branch iterates `body.source_document_ids`, fetches each doc, concatenates seeds.
  * DB row insert writes both plural + singular (singular = first element) for backward-compat readability.
  * Audit metadata emits both plural + singular.

### 3.2 Frontend

**`/app/frontend/src/components/work_studio/CreateArtefactModal.jsx`** (rewritten via `create_file overwrite=True` — substantial change; ~140 LOC net):
* New `sortByNameAlpha(items)` helper.
* State: `selectedBriefIds: Set<string>` + `selectedDocumentIds: Set<string>` (was singular strings).
* `toggleBrief` + `toggleDocument` handlers.
* Fetch effects apply `sortByNameAlpha` on the received arrays.
* Doc-list `useEffect` also watches a `refetchDocsToken` (bumped by upload flow).
* `+ Upload new` button opens `UploadModal`.
* `onDocumentUploaded(newDoc)` bumps refetch token + sets pending auto-select id.
* Follow-up effect auto-selects the new doc id once it appears in the refetched list.
* Submit payload sends `source_brief_ids` + `source_document_ids` arrays (backward-compat singular fields NOT sent).

**`/app/frontend/src/pages/WorkStudio.jsx`** (`DocumentRow` — pulse-mirror passenger):
* Component signature adds `pulseId` prop.
* `pulsed` predicate matches against `row.id` OR `row.work_studio_export_id`.
* ClassName concat + `data-pulse` attribute conditionally applied.
* Call site (line 1339 area) passes `pulseId={searchParams.get("pulse") || null}`.

### 3.3 What did NOT change

* **Surface A** (`Decks.jsx`, `db.decks`, `/app/decks`) — byte-identical.
* **DocumentOverlay** chrome — untouched.
* **UploadModal** — untouched (reused verbatim).
* **Chat surface** — untouched.
* **Solva engine** — untouched.

---

## 4. Locked-Area Sweep (memo)

* 0 Shield-adjacent code touched.
* 0 JC-CHAT surface files touched.
* 0 Solva engine files touched.
* 0 storage-arc files touched.
* 0 OAuth files touched.
* 0 Monitor files touched.
* 0 Surface A files touched.
* Zero-Handoff-Loss: `DEV_PIPELINE.md §9` row landed BEFORE any code edit or memo authoring.
* Canonical Spec citation on line 1.
* Six banked discipline lessons in play throughout.

---

## 5. Proving Slice (15 rows)

**File:** `/app/backend/scripts/jc_ws_deck_a2_proving_slice.py`.

| # | Row | Method |
| ---: | :--- | :--- |
| R1 | Pre-fix baseline — FE-only-label + pollution ceilings GREEN | pytest |
| R2 | DECK-017 alpha-sort briefs — `sortByNameAlpha` applied to briefs setState | Static grep |
| R3 | DECK-020 alpha-sort docs — `sortByNameAlpha` applied to documents setState | Static grep |
| R4 | DECK-018 multi-select briefs — payload `source_brief_ids` array; 0/1/2/3 selection all work via checkbox toggles | Static grep + Pydantic roundtrip |
| R5 | DECK-022 multi-select docs — payload `source_document_ids` array | Static grep + Pydantic roundtrip |
| R6 | DECK-021 in-modal upload — `UploadModal` mounted; `onUploaded` bumps refetch; auto-select effect wired | Static grep |
| R7 | In-modal upload race handling — `autoSelectDocIdAfterUpload` state + follow-up effect exists | Static grep |
| R8 | Backward compat — Pydantic model coerces singular → plural + WARNING log fires | Runtime Pydantic test |
| R9 | Chrome check — no new npm deps; no parallel upload component; no new modal shell | package.json + component grep |
| R10 | Passenger pulse-mirror — DocumentRow accepts `pulseId` + applies `data-pulse` + `.ws-doc-card-pulse-glow` (or SKIP with reasoning if any of DECK-017/018/020/021/022 slipped) | Static grep |
| R11 | Module-label-ready strings — 0 new "Solva"/"ThinkLab" literals in A2-touched FE files | Structural grep |
| R12 | F.6 Shield-contract preservation | pytest |
| R13 | JC-CHAT invariants preserved | pytest |
| R14 | Pollution ceilings unchanged (M1=0 / M2=1 FINAL) | pytest |
| R15 | End-to-end shape audit — CreateArtefactModal state flow → plural payload → backend endpoint accepts → DB row carries plural + singular + audit metadata coherent | Static shape check |

---

## 6. HARD STOP

15-row proving slice pending. **NO auto-dispatch.** Next in the queue is the rename arc Phase 1 (per user's revised order A3 → A2 → rename arc → then A4-A10). Fires ONLY on explicit user approval.

Surfacing for user review + next-dispatch pick.
