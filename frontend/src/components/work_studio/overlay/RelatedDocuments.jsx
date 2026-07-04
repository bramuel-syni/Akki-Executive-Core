/**
 * JC-WS-DECK-A10-RELATED-DOCS-MVP · 2026-07-02
 *
 * Canonical spec: /app/memory/sprints/JC_WS_DECK_A10_RELATED_DOCS_MVP.md
 * Path A execution plan: JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A10.
 *
 * FE-only render of existing doc.source_document_ids.
 * NO retrieval engine, NO metadata-similarity, NO lineage graph.
 * Full-A10 backend engine (retrieval + lineage + regenerate route)
 * DEFERRED (scope-escalation candidate · ~200+ LOC backend).
 *
 * Stories closed (MVP-level):
 *   DECK-066 ✅ MET — explicitly attached documents.
 * Deferred:
 *   DECK-064, DECK-065, DECK-067 — retrieval engine.
 *   DECK-084/085/086/087 — regenerate route + version tagging.
 */
import React from "react";

export default function RelatedDocuments({ doc }) {
  const sourceIds = (doc && Array.isArray(doc.source_document_ids))
    ? doc.source_document_ids
    : [];

  const handleOpen = (docId) => {
    // Reuse existing shell event to open a document overlay for the linked doc.
    if (typeof window === "undefined") return;
    const contextId = doc && doc.context_id;
    if (!contextId) return;
    window.dispatchEvent(new CustomEvent(
      "akki:open-document-overlay",
      { detail: { contextId, artefactId: docId } },
    ));
  };

  if (sourceIds.length === 0) {
    return (
      <div
        className="mx-4 my-8 py-16 px-6 text-center text-[var(--muted)] italic text-[13px] border border-dashed border-[var(--rule)] rounded-md"
        data-testid="related-docs-empty-state"
      >
        No related documents. This deck was not created from source briefs or uploaded documents.
      </div>
    );
  }

  return (
    <div
      data-testid="related-docs-root"
      className="mx-4 my-4 space-y-3"
    >
      <div className="text-[13px] text-[var(--muted)] mb-2">
        Documents explicitly attached to this deck at creation time. Click to open a source document.
      </div>
      <ul className="space-y-2">
        {sourceIds.map((docId, idx) => (
          <li
            key={`${docId}-${idx}`}
            data-testid="related-docs-item"
            className="border border-[var(--rule)] rounded-md px-3 py-2 bg-[var(--parchment)] flex items-center justify-between"
          >
            <span className="text-[12px] font-mono text-[var(--muted)]">
              {docId}
            </span>
            <button
              type="button"
              className="text-[11px] px-2 py-1 border border-[var(--rule)] rounded hover:bg-[var(--rule)] transition-colors"
              onClick={() => handleOpen(docId)}
              data-testid="related-docs-item-open-button"
            >
              Open
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
