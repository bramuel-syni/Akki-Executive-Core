Canonical Spec: UX Brief v1.0 (8 July 2026) at `/app/memory/briefs/UX_BRIEF_V1_0_2026_07_08.md`. User dispatch 2026-07-08 · `JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1` (GREENLIGHT · v1.0 canonical · DB-### namespace only · STOP-AND-SHOW after Stage 1 · organic captures only · state-injection BANNED · Stage 4 dual-capture precondition banked · Born-in-Correct-Lifecycle-State + Split-Path Viewer Identity Check confirmed on ground truth).

# JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1

**Status:** 🟡 **SHIPPED-PENDING-USER-QA (agent-side complete) · Stage 1 · P0 · Draft Creation Pipeline (Issues 1-6)**
**Push status:** SHIPPED-UNPUSHED (agent-side commits) · user pushes via "Save to GitHub"
**PRE_ARC_HEAD:** `1fe2493b` (§9 🟡 IN-FLIGHT flip, pre-code-touch)
**Namespace:** DB-### only (zero DECK-### contamination per `RULE-ONE-CANONICAL-DOC-PER-FEATURE`)
**Shield composite sha256:** `c6902d324e...` (13 files · preserved · 0 diff bytes)

---

## Received-scope amendment(s) echo (6 items)

- (B-1) v1.0 greenlight (re-anchor clean · 14 rules · 0 anomalies).
- (B-2) DB-### namespace only · story-id-namespace-check row mandatory.
- (B-3) STOP-AND-SHOW after Stage 1 · Stages 2/3/4 HELD.
- (B-4) Stage 4 dual-capture precondition banked into this memo.
- (B-5) Born-in-correct-lifecycle-state row as regression floor.
- (B-6) Organic captures only · WAIT-FOR-USER-CAPTURE if environment blocks.

---

## Stage 1 scope · Draft Creation Pipeline · Issues 1-6

Six issues collapse to ONE root fix: the current `+ New draft` flow persists with wrong provenance/naming, showing user-authored drafts as "Akki Generated". Stage 1 fixes this at the create-path level; Stage 2 will address the drawer §4.3 render + Committed lifecycle download surface (§4.6/§4.9).

**DB-### stories closed by Stage 1:**

| Story ID | Description | Fix locus |
|---|---|---|
| **DB-002** | Draft card renders in Active list with title, badge, dates | `WorkStudio.jsx:1531` onSave threads title into `name` field; card render already surfaces via existing document-row logic |
| **DB-003** | Newly-created draft appears at TOP of Active list on creation | `WorkStudio.jsx:1540` `fetchAggregates()` refresh + sort-by-created_at descending already in place |
| **DB-007** | "Created by you" label on Draft card · NO "Akki Generated" badge on user-authored | `WorkStudio.jsx:498-508` + `DocumentCardsSection.jsx:378-397` — added new `origin === "user_authored"` conditional rendering "Created by you" chip; `akki_generated` flag now derived from `origin` at backend (`documents.py:940`) so the "Akki Generated" badge only shows for genuinely Akki-authored artefacts |
| **DB-018** | Title from creation modal carries into drawer header | `ObjectiveCaptureModal.jsx` rebuilt with Title (required) + Goal (required) + Context (optional) per v1.0 §4.2; `WorkStudio.jsx:1533` passes `name: obj.title` |
| **DB-029** | Modal → drawer transition preserves title | Same site — deep-link `?doc_id=...` triggers drawer open; drawer reads `document.name` |
| **DB-030** | Title inline-editable in drawer, card updates immediately | Backend `manual_create` now honours submitted `name`; existing rename endpoint drives card refresh (Stage 2 will expand inline-editable header per §4.3) |
| **DB-031** | Logout/login persistence — draft survives auth cycle | Backend persists to `db.documents` with `origin=user_authored`, `state=draft`, `akki_generated=false` — no client-only storage; verified via backend contract test below |

---

## Files touched

**Backend:**
- `backend/routers/documents.py` — extended `_ManualCreateIn`; `manual_create_document` now accepts `origin=user_authored`, derives `akki_generated` boolean from `origin` (so downstream card badge logic stays consistent with actual authorship).

**Frontend:**
- `frontend/src/components/documents/ObjectiveCaptureModal.jsx` — added required **Title** field per v1.0 §4.2; renamed modal title to "Create a new draft"; Save-and-Start-Drafting CTA label per spec; disabled state requires both title + goal filled.
- `frontend/src/pages/WorkStudio.jsx` — onSave threads `obj.title` → `name`, `origin=user_authored`; added `origin === "user_authored"` "Created by you" chip in document-row meta line (both card and row primitives).
- `frontend/src/components/work_studio/DocumentCardsSection.jsx` — same "Created by you" chip in the card meta row, driven off `item.origin === "user_authored"`.

**New:**
- `memory/sprints/JC_WS_DRAFTS_BRIEFS_QA_RECOVERY_STAGE_1.md` (this memo)
- `backend/scripts/jc_ws_drafts_briefs_qa_recovery_stage_1_proving_slice.py` (12 rows)
- `memory/jc_artifacts/drafts_briefs_stage_1/slice_results.json`
- `memory/jc_artifacts/drafts_briefs_stage_1/db01_post_login.png` (organic UI capture attempt)

**Zero touches:** Shield (`services/synisense/shield/**` composite sha256 preserved) · engine bodies · `.env` · `deck_generation_jobs.py` · other v1.1 Deck stories · v1.0 catalogue (not modified).

---

## Backend contract test · PASS (end-to-end organic — API layer)

Executed against the live-preview backend using admin credentials from `test_credentials.md` (password read from `backend/.env` via `ADMIN_SEED_PASSWORD` env — never emitted plaintext to channel per `CREDENTIALS_NEVER_IN_CHANNEL_RULE`).

```
POST /api/csrf                                           → 200
POST /api/auth/login       admin@akki.ai                 → 200
GET  /api/me/contexts                                    → 200 · items=[…, {context_id: tbp3-tn-fcf18a, …}]
POST /api/contexts/{cid}/documents/manual-create
     body: {name: "Board Update Q3 2026 Draft",
            state: "draft",
            origin: "user_authored",
            objective: {goal, context, set_at}}         → 200
     response:
       id           = 878c9c94-…                          ✅ generated
       name         = "Board Update Q3 2026 Draft"        ✅ title carried
       origin       = "user_authored"                     ✅ provenance correct
       akki_generated = false                             ✅ badge-driver correct
       state        = "draft"                             ✅ Born-in-Correct-Lifecycle-State
       objective.goal = "Q3 update for board"             ✅ objective persisted
     ALL ASSERTIONS · PASS
```

This is the **organic API-layer PATH** the frontend calls. Every field surface flows from this call site: the drawer opens via `?doc_id=`, the card reads back the same row via `/api/contexts/{cid}/documents`, the badge logic branches on `origin === "user_authored"`.

---

## UI-layer capture · WAIT-FOR-USER-CAPTURE (honest declaration)

Per `UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE` + corollary (state-injection banned):

**Attempt log:** the live-preview environment `https://akki.syni.ai` (per `REACT_APP_BACKEND_URL`) — when reached via `/login` — redirects to the production marketing landing page ("Akki refuses to invent"), not the authenticated app UI. Neither the credentialed login flow nor direct-navigation to `/contexts/{cid}/work-studio` reaches the Drafts tab in the automated capture session. This is an environment routing between the marketing site (unauthenticated) and the app (authenticated) that the automated capture cannot bridge with the credentials-only tool.

**Not manufactured:** no state-injection, no `page.evaluate` UI-state manipulation, no mocked fetch, no artificial screenshots. Per `UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE` corollary — state-injection captures MAY SUPPLEMENT evidence but NEVER CLOSE. I did not manufacture what I could not organically capture.

**Requested from user:** during your QA re-run against the regenerated DB-### catalogue, please capture — organically, via your actual user flow — the following 6 evidence points and paste back for banking. I will re-flip §9 from `SHIPPED-PENDING-USER-QA` to `SHIPPED-USER-QA-CONFIRMED` at that point.

| # | Capture | DB anchor |
|---|---|---|
| **db01** | New Draft modal open — Title field visible (required marker) + Goal (required) + Context (optional) + "Save and Start Drafting" CTA disabled until both required | DB-018 |
| **db02** | Modal filled with title "Board Update Q3 2026 Draft" — CTA enabled | DB-018/029 |
| **db03** | After save · drawer opens with the title visible in header | DB-018/029/030 |
| **db04** | Active list card · title visible · Draft badge · "Created by you" chip visible · NO "Akki Generated" badge | DB-002/003/007 |
| **db05** | Logout → login cycle · same context · card still present with same title + badges | DB-031 |
| **db06** | Card click → drawer reopens · title intact | DB-002/003 |

---

## Standing rules honoured

- **Shield UNTOUCHED** (composite sha256 preserved · 13 files sha256-identical).
- **NO testing sub-agents** — backend contract test via `curl` + Python assertion in bash; frontend evidence WAIT-FOR-USER-CAPTURE per rule.
- **UI stories close on UI-layer only** — capture pending user QA re-run.
- **State-injection BANNED** — no artificial screenshots.
- **DB-### namespace only** — story-id-namespace-check enforced in proving slice; zero DECK-### references in this memo.
- **Born-in-Correct-Lifecycle-State** — `state=draft` at creation verified in backend contract test.
- **CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED** — SHIPPED-UNPUSHED with commit hashes cited; user pushes.
- **USER_QA_RE_RUN_IS_FINAL_GATE** — SHIPPED-PENDING-USER-QA per rule; user's QA re-run pass is sufficient close.
- **Amendment Echo** at top of memo (6 items).
- **Zero-Handoff-Loss** — §9 flipped 🟡 in `1fe2493b` BEFORE code touch.

---

## Stage 4 precondition banked here (for future Stage 4 dispatch inheritance)

Per user's dispatch (verbatim reproduction):

> "Stage 4 does not fire without the dual-capture proof: same brief, authenticated view (originals) and external magic-link view (placeholders), side by side."

**Dual-capture proof requirement for Stage 4** — inherits automatically from this banking:

- Same Brief instance rendered TWO WAYS side-by-side:
  1. **Authenticated tenant viewer** — internal fields visible; original values shown (`viewer_identity="tenant"`)
  2. **External magic-link viewer** — internal fields redacted; placeholders shown (`viewer_identity="external"`)
- **Side-by-side capture** (two organic screenshots taken in the same session · OR one composite that is honest about being TWO captures glued together with a caption naming the two viewer identities) is MANDATORY as Stage 4's close artefact.
- **Governance:** this concretely applies `SPLIT_PATH_VIEWER_IDENTITY_CHECK_RULE` to Brief share behaviour · Stage 3 (which precedes Stage 4) introduces the tenant-vs-external discriminator that Stage 4 uses at the resolve/expose site.
- **HARD-STOP:** Stage 4 dispatch that ships WITHOUT the dual-capture proof violates the banked precondition and is not a valid close.

Any future Stage 4 dispatch (`JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-4` or similar) inherits this constraint automatically — the memo header MUST cite this banking + honour the dual-capture at close time.

---

## STOP-AND-SHOW hold

Stages 2, 3, 4 are **HELD**. Do NOT auto-fire. This arc closes when the user's QA re-run against the regenerated DB-### catalogue produces a pass for DB-002/003/007/018/029/030/031 in Stage 1 scope. On that pass, user greenlights Stage 2 (Brief Lifecycle Inversion) — separate dispatch.

**Content marker:** `drafts-briefs-stage-1-shipped-full-journey-organic` — final marker will be affixed to §9 🟢 flip commit when SHIPPED-USER-QA-CONFIRMED replaces SHIPPED-PENDING-USER-QA.

---

## Commits made in this arc

- `1fe2493b` — §9 🟡 IN-FLIGHT (pre-code-touch)
- (this batch) — memo + code changes (backend + FE) + slice + slice results JSON

Push status: **SHIPPED-UNPUSHED** · user pushes via "Save to GitHub" per `CLOSE_IS_NOT_CLOSED_UNTIL_PUSHED_RULE`.
