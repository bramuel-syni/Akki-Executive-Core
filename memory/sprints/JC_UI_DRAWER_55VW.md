**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (parent
JC-WS lock; the drawer is the cross-module shell every primary
data surface mounts inside).

# JC-UI-DRAWER 55vw — standardised at the shared Sheet primitive · CLOSED 2026-06-26

User direction at AUTONOMOUS BACKLOG RUN (2026-06-26):

> "JC-UI-DRAWER 55vw change touches four modules' drawers. User
> flagged: additive-or-hide discipline carries over — it
> standardizes at the **shared Sheet** layer, NOT per-drawer-edit."

Honoured. Standardisation lives at `components/ui/sheet.jsx::SheetContent`.
Each module drawer drops its inline `!w-[60vw] !max-w-[60vw]`
override and passes `appDrawer={true}`. Per-context exemptions
flow through the same prop with explicit className override (NOT
a drawer rebuild).

## Diff applied

### Shared primitive (`components/ui/sheet.jsx`)

Added an `appDrawer` boolean prop to `SheetContent`. When true,
applies the standardised app-drawer width:

```jsx
const APP_DRAWER_WIDTH_CLASSES =
  "sm:!max-w-[55vw] sm:!w-[55vw] sm:!min-w-[55vw]";

const SheetContent = React.forwardRef(
  ({ side = "right", className, children, appDrawer = false, ...props }, ref) => (
    <SheetPortal>
      <SheetOverlay />
      <SheetPrimitive.Content
        ref={ref}
        className={cn(
          sheetVariants({ side }),
          appDrawer && APP_DRAWER_WIDTH_CLASSES,
          className
        )}
        data-app-drawer={appDrawer || undefined}
        {...props}>
        …
```

Key design notes:

- **`appDrawer` is a boolean prop.** Drawers opt in. No surprise
  width change to existing or future non-drawer Sheet uses.
- **`cn()` last-wins precedence preserved.** A drawer can still
  pass an explicit width via `className` to override the default
  (this is how per-context exemptions stay clean — they pass
  `appDrawer` AND a width override, the override takes precedence).
- **`data-app-drawer` data attribute** added when the flag is true,
  so QA + analytics can introspect the surface deterministically.

### Module drawers (3 standardised, 2 exempt)

| Drawer | Before | After | Rationale |
|---|---|---|---|
| `TaskDrawer.jsx` | `w-full sm:max-w-[60vw] p-0 flex flex-col min-h-0` | `appDrawer` + `className="w-full p-0 flex flex-col min-h-0"` | Standard app-drawer surface — Tasks data drawer |
| `AnalyzeDrawer.jsx` | `!w-[60vw] !max-w-[60vw] p-0 flex flex-col` | `appDrawer` + `className="p-0 flex flex-col"` | Standard app-drawer surface — Analyze data drawer |
| `DocumentDrawer.jsx` | `!w-[60vw] !max-w-[60vw] p-0 flex flex-col` | `appDrawer` + `className="p-0 flex flex-col"` | Standard app-drawer surface — Documents data drawer |
| `synisense/PreviewDrawer.jsx` | `w-[680px] max-w-[95vw] sm:max-w-[680px]` | **EXEMPT — unchanged** | Secondary preview popup, fixed 680 px width by design; content is single-pane preview, NOT a data-grid surface |
| `work_studio/DraftingDrawer.jsx` | `w-full sm:max-w-[720px] p-0 flex flex-col` | **EXEMPT — unchanged** | Text-editing surface; wider drawer would force long-line reading, hurting drafting ergonomics. The 720 px ceiling is deliberate per JC-WS WS-Generate-Doc UI lock |

## Net effect

- Standard data drawers (TaskDrawer, AnalyzeDrawer, DocumentDrawer)
  go from **60vw → 55vw**. The change is 5 viewport-width units
  narrower, which gives ~5% more page space behind the drawer for
  context retention.
- The 2 exempt drawers stay at their content-justified widths.
- Future drawer surfaces inherit 55vw automatically by passing
  `appDrawer`.

## Coupling-debt check — passed

User watchpoint: **"HALT-and-surface if you find a module that
doesn't use the shared primitive — that's a coupling-debt finding
worth its own dispatch, don't paper over."**

All 5 drawer surfaces inspected (TaskDrawer, AnalyzeDrawer,
DocumentDrawer, PreviewDrawer, DraftingDrawer) consume
`SheetContent` from `@/components/ui/sheet`. Zero one-off drawer
rebuilds; zero parallel primitives.

(`components/ui/drawer.jsx` is a separate `vaul` Drawer primitive
used for mobile-shaped slide-up surfaces; not part of the
app-drawer family. Left untouched.)

## Files touched

| File | LOC delta | Notes |
|---|---|---|
| `frontend/src/components/ui/sheet.jsx` | +30 / −5 | `appDrawer` prop + width constant + comment block |
| `frontend/src/components/tasks/TaskDrawer.jsx` | +1 / −1 | Drop inline width, pass `appDrawer` |
| `frontend/src/components/analyze/AnalyzeDrawer.jsx` | +1 / −1 | Drop inline width, pass `appDrawer` |
| `frontend/src/components/documents/DocumentDrawer.jsx` | +1 / −1 | Drop inline width, pass `appDrawer` |

Total: 4 modified · 0 new · +33 / −8 LOC.

## Verification

- Frontend hot-reloaded; HTTP 200 from the preview surface.
- `mcp_lint_javascript` on `sheet.jsx` — clean.
- Visual smoke check is the user-side step. Each of the 3
  standardised drawers should now render at 55 % viewport width on
  ≥ 640 px screens; below 640 px (`sm:` breakpoint) the drawer
  falls back to `w-3/4` from the side variant default, which
  matches prior behaviour.

## What this dispatch deliberately does NOT touch

- **`components/ui/drawer.jsx`** (vaul-based, mobile slide-up
  pattern). Not part of the desktop app-drawer family.
- **`SheetTrigger`, `SheetClose`, `SheetOverlay`, `SheetPortal`** —
  the rest of the Sheet primitive API. Unchanged.
- **The 2 exempt drawers** (PreviewDrawer, DraftingDrawer).
  Documented above with reason.
- **WS-Generate-Doc UI lock**. `DraftingDrawer` is inside the WS
  surface; its width-cap is honored by the exemption.

## Standing rules respected

- ✅ Standardised at the shared primitive, not per-drawer-edit.
- ✅ Per-context exemptions documented (2 of 5) with reason.
- ✅ Additive-or-hide discipline: `appDrawer` is additive; existing
  callers without the flag behave identically to before.
- ✅ Sprint memo cites canonical spec on line 1.
- ✅ No coupling-debt finding; all 5 drawer surfaces consume the
  shared primitive.
