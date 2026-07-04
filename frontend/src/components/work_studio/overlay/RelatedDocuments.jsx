/**
 * JC-WS-DECK-A10-BACKEND-RETRIEVAL-LINEAGE-REGENERATE · 2026-07-04
 *
 * Canonical spec: /app/memory/sprints/JC_WS_DECK_A10_BACKEND_RETRIEVAL_LINEAGE_REGENERATE.md
 *              + /app/memory/sprints/JC_WS_DECK_A10_RELATED_DOCS_MVP.md (predecessor)
 *              + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A10.
 *
 * A10-MVP shell (DECK-066 explicitly attached documents) + A10-BE upgrade
 * (DECK-064 retrieval + DECK-065 similarity + DECK-067 lineage + DECK-084/085/086/087
 *  regenerate + version chain).
 *
 * Per-surface F.6 (banked in memo header):
 *   - GET /related → F.6 N/A (metadata-scored)
 *   - GET /lineage → F.6 N/A (graph traversal)
 *   - POST /regenerate → F.6 SHIELD-ROUTED (canonical chokepoint · commit-lock enforced)
 *
 * TAB HONESTY RULE: all state server-side (documents collection versioning);
 * regenerate creates new documents row, prior preserved.
 *
 * Stories closed:
 *   DECK-064 ✅ Backend retrieval engine (GET /related)
 *   DECK-065 ✅ Metadata similarity (folded into retrieval; embedding-based deferred)
 *   DECK-066 ✅ Explicitly attached documents (legacy · preserved as fallback)
 *   DECK-067 ✅ Lineage graph (GET /lineage)
 *   DECK-084 ✅ Version chain (regenerated_from + version_number)
 *   DECK-085 ✅ Regenerate route (POST /regenerate)
 *   DECK-086 ✅ Commit-lock enforcement (409 compile-bridge shape)
 *   DECK-087 ✅ Prior versions preserved (never overwritten)
 */
import React, { useCallback, useEffect, useState } from "react";
import api from "@/lib/api/apiV2";
import { GitBranch, RotateCcw, Lock } from "lucide-react";

export default function RelatedDocuments({ doc }) {
  const documentId = doc && doc.id;
  const contextId = doc && doc.context_id;
  const isCommitted = (doc && doc.lifecycle_state) === "committed";
  const legacySourceIds = (doc && Array.isArray(doc.source_document_ids))
    ? doc.source_document_ids
    : [];

  const [related, setRelated] = useState([]);
  const [lineage, setLineage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!documentId) return () => {};
    let cancelled = false;
    setLoading(true);
    Promise.all([
      api.get(`/decks/${documentId}/related`).catch(() => ({ data: [] })),
      api.get(`/decks/${documentId}/lineage`).catch(() => ({ data: null })),
    ]).then(([rel, lin]) => {
      if (cancelled) return;
      setRelated((rel && Array.isArray(rel.data)) ? rel.data : []);
      setLineage((lin && lin.data) || null);
    }).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, [documentId]);

  const handleOpen = useCallback((docId) => {
    if (typeof window === "undefined") return;
    if (!contextId) return;
    window.dispatchEvent(new CustomEvent(
      "akki:open-document-overlay",
      { detail: { contextId, artefactId: docId } },
    ));
  }, [contextId]);

  const handleRegenerate = async () => {
    if (!documentId || isCommitted || regenerating) return;
    setRegenerating(true);
    setError(null);
    try {
      const resp = await api.post(`/decks/${documentId}/regenerate`, {});
      const newDoc = resp && resp.data && resp.data.new_document;
      if (newDoc && newDoc.id) {
        // Optimistic navigation to new version.
        handleOpen(newDoc.id);
      }
    } catch (err) {
      if (err && err.response && err.response.status === 409) {
        setError("Committed decks cannot be regenerated. Create a new draft to iterate.");
      } else {
        setError((err && err.message) || "Regenerate failed");
      }
    } finally {
      setRegenerating(false);
    }
  };

  // Prefer backend related over legacy source_document_ids.
  const showBackend = related.length > 0;
  const showLegacy = !showBackend && legacySourceIds.length > 0;

  const versionNumber = lineage && lineage.document && lineage.document.version_number;
  const ancestorsCount = lineage && Array.isArray(lineage.ancestors) ? lineage.ancestors.length : 0;
  const descendantsCount = lineage && Array.isArray(lineage.descendants) ? lineage.descendants.length : 0;
  const siblingsCount = lineage && Array.isArray(lineage.siblings) ? lineage.siblings.length : 0;
  const totalInChain = 1 + ancestorsCount + descendantsCount;

  return (
    <div
      data-testid="related-docs-root"
      className="mx-4 my-4 space-y-3"
    >
      {/* Lineage / version chip. */}
      {lineage && lineage.document && (
        <div
          className="flex items-center gap-3 border border-[var(--rule)] bg-[var(--parchment)] rounded-md px-3 py-2"
          data-testid="related-docs-lineage-chip"
        >
          <GitBranch className="w-3.5 h-3.5" strokeWidth={1.6} />
          <div className="flex-1 text-[12px]">
            <span className="font-mono">
              v{versionNumber || 1} of {totalInChain}
            </span>
            {ancestorsCount > 0 && (
              <span
                className="ml-3 text-[var(--muted)]"
                data-testid="related-docs-lineage-ancestors"
              >
                {ancestorsCount} ancestor{ancestorsCount === 1 ? "" : "s"}
              </span>
            )}
            {descendantsCount > 0 && (
              <span
                className="ml-3 text-[var(--muted)]"
                data-testid="related-docs-lineage-descendants"
              >
                {descendantsCount} descendant{descendantsCount === 1 ? "" : "s"}
              </span>
            )}
            {siblingsCount > 0 && (
              <span
                className="ml-3 text-[var(--muted)]"
                data-testid="related-docs-lineage-siblings"
              >
                {siblingsCount} sibling{siblingsCount === 1 ? "" : "s"}
              </span>
            )}
          </div>
          {/* Regenerate affordance. */}
          <button
            type="button"
            onClick={handleRegenerate}
            disabled={isCommitted || regenerating}
            className={
              "text-[11px] px-2 py-1 border border-[var(--rule)] rounded flex items-center gap-1 "
              + (isCommitted || regenerating
                ? "opacity-50 cursor-not-allowed"
                : "hover:bg-[var(--cream-deep)]/40")
            }
            data-testid="related-docs-regenerate-btn"
            title={isCommitted
              ? "regenerate not available on committed decks"
              : "Regenerate as new draft version (F.6 Shield-routed)"}
          >
            {isCommitted ? (
              <Lock className="w-3 h-3" strokeWidth={1.6} />
            ) : (
              <RotateCcw className="w-3 h-3" strokeWidth={1.6} />
            )}
            {regenerating ? "Regenerating…" : "Regenerate"}
          </button>
        </div>
      )}

      {error && (
        <div
          className="text-[12.5px] text-[var(--oxblood)]"
          data-testid="related-docs-regenerate-error"
        >
          {error}
        </div>
      )}

      {loading && (
        <div className="text-[12.5px] italic text-[var(--muted)]" data-testid="related-docs-loading">
          Loading related decks…
        </div>
      )}

      {/* Backend-scored related decks (preferred). */}
      {!loading && showBackend && (
        <>
          <div className="text-[13px] text-[var(--muted)] mb-2">
            Related decks scored by metadata similarity (source-doc overlap · category · context).
          </div>
          <ul className="space-y-2">
            {related.map((r, idx) => (
              <li
                key={`${r.id}-${idx}`}
                data-testid="related-docs-item"
                className="border border-[var(--rule)] rounded-md px-3 py-2 bg-[var(--parchment)] flex items-center justify-between"
              >
                <div className="flex-1 min-w-0">
                  <div className="text-[12.5px] truncate">{r.name || r.id}</div>
                  <div className="text-[10.5px] font-mono text-[var(--muted)]">
                    score {(r.similarity_score || 0).toFixed(3)}
                    {r.category ? ` · ${r.category}` : ""}
                  </div>
                </div>
                <button
                  type="button"
                  className="text-[11px] px-2 py-1 border border-[var(--rule)] rounded hover:bg-[var(--rule)] transition-colors"
                  onClick={() => handleOpen(r.id)}
                  data-testid="related-docs-item-open-button"
                >
                  Open
                </button>
              </li>
            ))}
          </ul>
        </>
      )}

      {/* Legacy fallback: source_document_ids. */}
      {!loading && showLegacy && (
        <>
          <div className="text-[13px] text-[var(--muted)] mb-2">
            Documents explicitly attached to this deck at creation time. Click to open a source document.
          </div>
          <ul className="space-y-2">
            {legacySourceIds.map((docId, idx) => (
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
        </>
      )}

      {!loading && !showBackend && !showLegacy && (
        <div
          className="mx-0 my-8 py-16 px-6 text-center text-[var(--muted)] italic text-[13px] border border-dashed border-[var(--rule)] rounded-md"
          data-testid="related-docs-empty-state"
        >
          No related documents. This deck was not created from source briefs or uploaded documents.
        </div>
      )}
    </div>
  );
}
