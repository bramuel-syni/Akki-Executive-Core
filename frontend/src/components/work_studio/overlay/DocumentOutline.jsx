/**
 * JC-WS-DECK-A6-DOCUMENT-TAB-CONTENT · 2026-07-02
 *
 * Canonical spec: /app/memory/rules/TAB_HONESTY_RULE.md
 *              + /app/memory/sprints/JC_WS_DECK_A6_DOCUMENT_TAB_CONTENT.md
 *              + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A6.
 *
 * Document tab content — MVP (DECK-040 structured outline + DECK-043
 * source-context pointer). Reads existing `doc.structured_content.sections`
 * (already returned by /work-studio/documents/{aid}) — no new backend LOC.
 * TAB HONESTY RULE respected: sections are computed from the authoritative
 * document (structured_content), not a browser-local cache.
 *
 * Stories closed (MVP-level):
 *   DECK-040 ✅ Structured outline navigation (section headings + click-to-scroll)
 *   DECK-043 ✅ Source-context section (pointer to Related Documents tab with source count)
 *
 * Deferred to full-A6 backend engine dispatch:
 *   DECK-044 Edit source-context — requires PATCH endpoint for a new
 *            `source_context` field on documents (~150+ LOC backend).
 */
import React from "react";
import { List, ExternalLink } from "lucide-react";

function scrollToHeading(headingText) {
  if (typeof window === "undefined" || typeof document === "undefined") return;
  const el = Array.from(document.querySelectorAll('[data-testid="document-overlay-surface-editor"] h2'))
    .find((h) => (h.textContent || "").trim() === headingText.trim());
  if (el && typeof el.scrollIntoView === "function") {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

export default function DocumentOutline({ doc, onOpenRelatedTab }) {
  const sections = (doc && doc.structured_content && Array.isArray(doc.structured_content.sections))
    ? doc.structured_content.sections
    : [];
  const sourceCount = (doc && Array.isArray(doc.source_document_ids))
    ? doc.source_document_ids.length
    : 0;
  const outlineItems = sections
    .map((s) => (s && typeof s.heading === "string" ? s.heading.trim() : ""))
    .filter(Boolean);

  if (outlineItems.length === 0 && sourceCount === 0) return null;

  return (
    <div
      data-testid="document-outline-root"
      className="mx-4 mt-2 mb-4 border border-[var(--rule)] rounded-md bg-[var(--parchment)] p-3"
    >
      {outlineItems.length > 0 && (
        <div className="mb-2" data-testid="document-outline-list">
          <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] mb-1.5">
            <List className="w-3 h-3" strokeWidth={1.6} />
            Outline
          </div>
          <ol className="space-y-0.5 pl-4 list-decimal marker:text-[var(--muted)]">
            {outlineItems.map((heading, idx) => (
              <li
                key={`${heading}-${idx}`}
                data-testid="document-outline-item"
                className=""
              >
                <button
                  type="button"
                  onClick={() => scrollToHeading(heading)}
                  className="text-[12.5px] text-[var(--ink)] hover:text-[var(--oxblood)] hover:underline text-left"
                  data-testid="document-outline-item-btn"
                  title={`Scroll to "${heading}"`}
                >
                  {heading}
                </button>
              </li>
            ))}
          </ol>
        </div>
      )}
      {sourceCount > 0 && (
        <div
          className="pt-2 border-t border-[var(--rule)] flex items-center justify-between"
          data-testid="document-outline-source-context"
        >
          <span className="text-[11.5px] text-[var(--muted)] italic">
            Generated from {sourceCount} source {sourceCount === 1 ? "document" : "documents"}.
          </span>
          {onOpenRelatedTab && (
            <button
              type="button"
              onClick={onOpenRelatedTab}
              className="text-[11px] px-2 py-0.5 border border-[var(--rule)] rounded-sm hover:bg-[var(--cream-deep)]/40 flex items-center gap-1"
              data-testid="document-outline-open-related-btn"
              title="Open Related Documents tab"
            >
              Related <ExternalLink className="w-3 h-3" strokeWidth={1.6} />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
