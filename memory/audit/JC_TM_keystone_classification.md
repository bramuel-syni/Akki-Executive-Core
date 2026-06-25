# JC-TM Keystone Classification — TaskDrawer

> **Source of truth:** `/app/memory/JC_TM_CANONICAL_SPEC.md`
> **Date:** 2026-06-25
> **Verdict:** 🟢 **WIRED — no placeholder gap. Move straight to proving slice.**

---

## Verdict (by execution)

The TaskDrawer keystone is **LIVE in production**. Clicking a task card in
`TaskListing` sets `?task_id=<uuid>` on the URL; the URL change triggers
`TaskDrawer.jsx` (mounted in `TaskManager.jsx:237`) to open with the real five-tab
surface filled from wired endpoints. No placeholder shim was found at runtime.

## Evidence — by execution, not by static read

Screenshot at `/tmp/jc_tm_keystone_smoke.png` (preserved as
`/app/memory/jc_artifacts/JC-TM-keystone-smoke-2026-06-25.jpg`) shows the
following on `?task_id=tsk-a6ec7468b2d6`:

| Probe | Result | Evidence |
|---|---|---|
| `[data-testid="task-drawer-state-badge"]` | **FOUND** | DOM probe returned element |
| Tab — Plan | present | DOM probe + visible in screenshot |
| Tab — Contributions | present | DOM probe + visible in screenshot |
| Tab — Drafts | present | DOM probe + visible in screenshot |
| Tab — Intelligence | present | DOM probe + visible in screenshot |
| Tab — Compile | present | DOM probe + visible in screenshot |
| `text=/coming soon\|placeholder/i` | **absent** | DOM probe |
| Plan tab content | Real fields rendered — `OBJECTIVE`, `SUCCESS CRITERIA`, `OUTPUT`, `TEAM` (Empty-but-real, since the test task is bare) | Visible in screenshot |
| Footer CTAs | Commission · Use in Solva · Use in Chat · Generate brief · Test hypothesis · Share task — all rendered | Visible in screenshot |

## Why the "placeholder" framing came from

`TaskManager.jsx:17` (pre-edit) carried this docstring:

> "Clicking a task card opens a placeholder 'Task drawer coming soon' sheet via TaskListing."

That was true at the F.2 milestone. The F.3 work
(`TaskDrawer.jsx:1-17` docstring confirms: "Universal Task surface. Mounts on
Task Manager (replacing F.2's placeholder)…") landed but the page-level
docstring wasn't updated.

**Action taken:** updated the stale docstring in `TaskManager.jsx` to point at
F.3 + this memo. Single-file edit, no behaviour change.

## Implication for the JC-TM execution order

- **Step 1:** ✅ Complete. Keystone wired; no "wire the drawer" sub-step needed.
- **Step 2:** Move straight to the proving slice (board-pack task end-to-end).

## Lines / files involved

| File | Lines | Purpose |
|---|---|---|
| `frontend/src/pages/TaskManager.jsx` | 17 (docstring), 237 (`<TaskDrawer />` mount) | Page hosts the listing + mounts the drawer |
| `frontend/src/components/tasks/TaskListing.jsx` | 126-130 (`openTask` handler), 269 (card `onClick`) | Card click sets `?task_id=<id>` |
| `frontend/src/components/tasks/TaskDrawer.jsx` | 73-79 (`useSearchParams` → `tid`), 1-17 (docstring describing 5 tabs) | Drawer reads `?task_id=` and opens |

## Wired backend endpoints (confirmed available, from `routers/tasks.py`)

| Surface | Endpoint | Status |
|---|---|---|
| Task details + lifecycle | `GET /api/tasks/{task_id}` · `PATCH /api/tasks/{task_id}` · `POST /api/tasks/{task_id}/commission` · `POST /api/tasks/{task_id}/close` | Wired |
| Contributions + revisions | `PATCH /api/tasks/{task_id}/contributions/{contributor_id}` | Wired |
| Contributor portal | `GET /api/tasks/contribute/{token}` · `POST /api/tasks/contribute/{token}/upload` · `/comment` · `/submit` | Wired |
| Reinvite | `POST /api/tasks/{task_id}/contributors/{contributor_id}/reinvite` | Wired |
| Intelligence (readiness + AI) | `GET /api/tasks/{task_id}/intelligence` · `POST /api/tasks/{task_id}/intelligence/regenerate` | Wired |
| Compile pipeline | `GET /api/tasks/{task_id}/compile` · `POST /api/tasks/{task_id}/compile/draft` · `/review/complete` · `/circulation/send` · `/circulation/close` · `/final-production/apply-comment` · `/final-production/complete` · `/compile/commit` | Wired |
| Circulation portal | `GET /api/tasks/circulation/{token}` · `POST /api/tasks/circulation/{token}/comment` | Wired |
| Drafts | `GET /api/tasks/{task_id}/drafts` | Wired |

This is the keystone-confirmed surface area for Step 2 proving slice.
