/**
 * JC-WS-DECK-A6-BACKEND-SOURCE-CONTEXT-PATCH · 2026-07-04
 *
 * Canonical spec: /app/memory/rules/TAB_HONESTY_RULE.md
 *              + /app/memory/sprints/JC_WS_DECK_A6_BACKEND_SOURCE_CONTEXT_PATCH.md
 *              + /app/memory/sprints/JC_WS_DECK_A6_DOCUMENT_TAB_CONTENT.md (MVP predecessor)
 *              + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A6.
 *
 * Document tab content — A6-MVP shell (DECK-040 structured outline +
 * DECK-043 source-context pointer) + A6-BE upgrade (DECK-044 source-context
 * edit with debounced autosave against /api/deck-source-context/{doc_id}).
 * TAB HONESTY RULE: edit state is account-persisted server-side, no
 * localStorage strand (mirrors A8-BE DeckNotes pattern verbatim).
 *
 * Stories closed:
 *   DECK-040 ✅ Structured outline navigation (section headings + click-to-scroll)
 *   DECK-043 ✅ Source-context section (pointer to Related Documents tab with source count)
 *   DECK-044 ✅ Edit source-context (click-to-edit textarea + 500ms debounced autosave)
 *
 * F.6 discipline-pay: N/A · user-authored content, no LLM path.
 */
import React, { useCallback, useEffect, useRef, useState } from "react";
import { List, ExternalLink, Pencil, X, Check } from "lucide-react";
import api from "@/lib/api/apiV2";

const AUTOSAVE_DEBOUNCE_MS = 500;

function scrollToHeading(headingText) {
  if (typeof window === "undefined" || typeof document === "undefined") return;
  const el = Array.from(document.querySelectorAll('[data-testid="document-overlay-surface-editor"] h2'))
    .find((h) => (h.textContent || "").trim() === headingText.trim());
  if (el && typeof el.scrollIntoView === "function") {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

/**
 * Formats a "relative time since save" indicator. Mirrors A8-BE DeckNotes
 * exactly for consistency across drawer edit surfaces.
 */
function formatSavedIndicator(updatedAt) {
  if (!updatedAt) return "";
  const then = new Date(updatedAt);
  if (Number.isNaN(then.getTime())) return "";
  const seconds = Math.max(0, Math.round((Date.now() - then.getTime()) / 1000));
  if (seconds < 5) return "Saved just now";
  if (seconds < 60) return `Saved ${seconds}s ago`;
  return `Saved at ${then.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
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

  // A6-BE (DECK-044) — source-context edit state.
  const artefactId = doc && doc.id;
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState(
    (doc && typeof doc.source_context === "string") ? doc.source_context : "",
  );
  const [savedAt, setSavedAt] = useState(
    (doc && doc.source_context_updated_at) || null,
  );
  const [savedIndicator, setSavedIndicator] = useState("");
  const debounceRef = useRef(null);
  const tickRef = useRef(null);
  const textareaRef = useRef(null);

  // Sync in from doc prop changes (e.g. when overlay switches document).
  useEffect(() => {
    setContent((doc && typeof doc.source_context === "string") ? doc.source_context : "");
    setSavedAt((doc && doc.source_context_updated_at) || null);
    setEditing(false);
  }, [artefactId, doc && doc.source_context, doc && doc.source_context_updated_at]);

  // Refresh "Saved Xs ago" indicator every 10s.
  useEffect(() => {
    if (!savedAt) {
      setSavedIndicator("");
      return () => {};
    }
    setSavedIndicator(formatSavedIndicator(savedAt));
    if (tickRef.current) window.clearInterval(tickRef.current);
    tickRef.current = window.setInterval(() => {
      setSavedIndicator(formatSavedIndicator(savedAt));
    }, 10000);
    return () => {
      if (tickRef.current) window.clearInterval(tickRef.current);
    };
  }, [savedAt]);

  // Debounced autosave — PATCH 500ms after last keystroke. Mirrors
  // A8-BE DeckNotes autosave flow (no localStorage — Tab Honesty).
  const scheduleSave = useCallback((nextContent) => {
    if (!artefactId) return;
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(async () => {
      try {
        const resp = await api.patch(
          `/deck-source-context/${artefactId}`,
          { content: nextContent },
        );
        const stamp = (resp && resp.data && resp.data.updated_at) || null;
        if (stamp) {
          setSavedAt(stamp);
          setSavedIndicator(formatSavedIndicator(stamp));
        }
      } catch {
        // Silent — user keeps their in-memory state; next save attempt retries.
      }
    }, AUTOSAVE_DEBOUNCE_MS);
  }, [artefactId]);

  const handleChange = (e) => {
    const next = e.target.value;
    setContent(next);
    scheduleSave(next);
  };

  const startEditing = () => {
    setEditing(true);
    // Focus the textarea after the render tick.
    window.setTimeout(() => {
      if (textareaRef.current) textareaRef.current.focus();
    }, 0);
  };

  const stopEditing = async () => {
    // Flush any pending debounced save synchronously before closing.
    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current);
      debounceRef.current = null;
      if (artefactId) {
        try {
          const resp = await api.patch(
            `/deck-source-context/${artefactId}`,
            { content },
          );
          const stamp = (resp && resp.data && resp.data.updated_at) || null;
          if (stamp) {
            setSavedAt(stamp);
            setSavedIndicator(formatSavedIndicator(stamp));
          }
        } catch { /* silent */ }
      }
    }
    setEditing(false);
  };

  const hasSourceContext = typeof content === "string" && content.trim().length > 0;

  // Original component gated on "outlineItems.length === 0 && sourceCount === 0".
  // A6-BE keeps that shell so we don't render an empty card for docs with no
  // outline AND no sources. But if source_context has been authored, we
  // render even when outline+sources are both empty (edit affordance for
  // decks whose upstream sources were removed still needs to surface).
  if (outlineItems.length === 0 && sourceCount === 0 && !hasSourceContext && !editing) return null;

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
      {(sourceCount > 0 || hasSourceContext || editing) && (
        <div
          className="pt-2 border-t border-[var(--rule)]"
          data-testid="document-outline-source-context"
        >
          {sourceCount > 0 && (
            <div className="flex items-center justify-between mb-1">
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

          {/* A6-BE (DECK-044): source-context free-form area. */}
          <div className="mt-1" data-testid="document-outline-source-context-editor">
            <div className="flex items-center justify-between mb-1">
              <div className="text-[10.5px] uppercase tracking-[0.14em] font-mono text-[var(--muted)]">
                Source context
              </div>
              <div className="flex items-center gap-2">
                {savedIndicator && (
                  <span
                    className="text-[10.5px] text-[var(--muted)] italic"
                    data-testid="document-outline-source-context-saved-indicator"
                  >
                    {savedIndicator}
                  </span>
                )}
                {!editing && (
                  <button
                    type="button"
                    onClick={startEditing}
                    className="text-[11px] px-2 py-0.5 border border-[var(--rule)] rounded-sm hover:bg-[var(--cream-deep)]/40 flex items-center gap-1"
                    data-testid="document-outline-source-context-edit-btn"
                    title={hasSourceContext ? "Edit source context" : "Add source context"}
                  >
                    <Pencil className="w-3 h-3" strokeWidth={1.6} />
                    {hasSourceContext ? "Edit" : "Add"}
                  </button>
                )}
                {editing && (
                  <button
                    type="button"
                    onClick={stopEditing}
                    className="text-[11px] px-2 py-0.5 border border-[var(--rule)] rounded-sm hover:bg-[var(--cream-deep)]/40 flex items-center gap-1"
                    data-testid="document-outline-source-context-done-btn"
                    title="Save and close editor"
                  >
                    <Check className="w-3 h-3" strokeWidth={1.6} />
                    Done
                  </button>
                )}
              </div>
            </div>
            {editing ? (
              <textarea
                ref={textareaRef}
                value={content}
                onChange={handleChange}
                placeholder="Add source context for this deck — a short narrative about what the underlying documents say and why they were selected. Autosaves as you type."
                className="w-full min-h-[100px] p-2 border border-[var(--rule)] rounded-md bg-white text-[12.5px] leading-relaxed font-mono resize-y focus:outline-none focus:border-[var(--oxblood)]"
                data-testid="document-outline-source-context-textarea"
                maxLength={8000}
              />
            ) : (
              <div
                className="text-[12.5px] text-[var(--ink)] whitespace-pre-wrap leading-relaxed"
                data-testid="document-outline-source-context-display"
              >
                {hasSourceContext ? content : (
                  <span className="italic text-[var(--muted)]">
                    No source context set.
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
