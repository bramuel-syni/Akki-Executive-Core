/**
 * UploadOptions — JC-MON Stage 1 shared affordance (2026-06-25)
 *
 * The single component that surfaces "Use this document for performance
 * tracking" + optional "Mark as base document" across every upload
 * surface. Per the JC-MON canonical spec § Stage 1 and the
 * `/app/memory/audit/JC_MON_upload_surface_inventory.md` inventory:
 * implement ONE shared affordance, drop into 7 consumers (3-5 LOC
 * each), not reimplemented per surface.
 *
 * Stage 1 also folds in the per-surface sessionStorage memory
 * enhancement (user dispatch decision #2 = ii). The memory key is
 * scoped by `testIdPrefix` so different surfaces don't bleed
 * preferences across each other.
 *
 * Stateless presentational. The parent owns the value + onChange.
 * Two checkboxes, lucide icons, akki design tokens, kebab-case testids.
 */

import { Checkbox } from "@/components/ui/checkbox";
import { Database, BookmarkCheck } from "lucide-react";
import { useEffect, useRef } from "react";

const SS_KEY = (prefix) => `akki:upload-options:${prefix}:lastTracked`;

/**
 * @param {object} props
 * @param {{ useForTracking: boolean, isBaseDocument: boolean }} props.value
 * @param {(next: { useForTracking: boolean, isBaseDocument: boolean }) => void} props.onChange
 * @param {boolean} [props.allowBase=false] — Monitor surface only
 * @param {string} [props.testIdPrefix="upload-options"]
 * @param {string} [props.labelOverride] — friendlier copy variant
 *   (e.g. "Mark this as performance evidence" for ContributorPortal)
 * @param {boolean} [props.disabled=false]
 */
export default function UploadOptions({
  value,
  onChange,
  allowBase = false,
  testIdPrefix = "upload-options",
  labelOverride,
  disabled = false,
}) {
  const trackingLabel =
    labelOverride || "Use this document for performance tracking";

  // ── sessionStorage per-surface memory (JC-MON Stage 1 dispatch
  //     decision #2 = ii). Hydrate the tracking flag on first mount;
  //     persist the flag on every change. The memory key includes
  //     `testIdPrefix` so two surfaces don't bleed preferences across.
  const hydratedRef = useRef(false);
  useEffect(() => {
    if (hydratedRef.current || typeof window === "undefined") return;
    hydratedRef.current = true;
    try {
      const stored = sessionStorage.getItem(SS_KEY(testIdPrefix));
      if (stored === "true" && !value?.useForTracking) {
        onChange({
          useForTracking: true,
          isBaseDocument: !!value?.isBaseDocument,
        });
      }
    } catch {
      /* sessionStorage unavailable — silent. */
    }
    // Only on mount.
  }, []);

  const setTracking = (checked) => {
    onChange({
      useForTracking: !!checked,
      isBaseDocument: !!value?.isBaseDocument,
    });
    try {
      sessionStorage.setItem(SS_KEY(testIdPrefix), checked ? "true" : "false");
    } catch {
      /* silent */
    }
  };
  const setBase = (checked) =>
    onChange({
      useForTracking: !!value?.useForTracking,
      isBaseDocument: !!checked,
    });

  return (
    <div
      className="space-y-2 p-2 border border-[var(--rule)] rounded-sm bg-[var(--parchment)]/30"
      data-testid={`${testIdPrefix}-root`}
    >
      <label
        className="flex items-start gap-2 cursor-pointer"
        data-testid={`${testIdPrefix}-tracking-label`}
      >
        <Checkbox
          checked={!!value?.useForTracking}
          onCheckedChange={setTracking}
          disabled={disabled}
          data-testid={`${testIdPrefix}-tracking-checkbox`}
          aria-label={trackingLabel}
          className="mt-0.5"
        />
        <span className="text-[12.5px] text-[var(--ink)] leading-snug">
          <span className="inline-flex items-center gap-1.5">
            <Database
              className="w-3 h-3 text-[var(--muted)]"
              strokeWidth={1.7}
              aria-hidden="true"
            />
            {trackingLabel}
          </span>
          <span className="block text-[10.5px] text-[var(--muted)] mt-0.5">
            Lets Monitor read this document when assessing objectives.
          </span>
        </span>
      </label>

      {allowBase && (
        <label
          className="flex items-start gap-2 cursor-pointer pt-1.5 border-t border-[var(--rule)]"
          data-testid={`${testIdPrefix}-base-label`}
        >
          <Checkbox
            checked={!!value?.isBaseDocument}
            onCheckedChange={setBase}
            disabled={disabled}
            data-testid={`${testIdPrefix}-base-checkbox`}
            aria-label="Mark as base document"
            className="mt-0.5"
          />
          <span className="text-[12.5px] text-[var(--ink)] leading-snug">
            <span className="inline-flex items-center gap-1.5">
              <BookmarkCheck
                className="w-3 h-3 text-[var(--muted)]"
                strokeWidth={1.7}
                aria-hidden="true"
              />
              Mark as base document
            </span>
            <span className="block text-[10.5px] text-[var(--muted)] mt-0.5">
              Defines what objectives are tracked against (e.g. the
              strategic plan or performance agreement).
            </span>
          </span>
        </label>
      )}
    </div>
  );
}
