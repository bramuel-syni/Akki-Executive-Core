/**
 * JC-WS-DECK-A7-INTELLIGENCE-TAB-COMPLETION · 2026-07-02
 *
 * Canonical spec: /app/memory/rules/TAB_HONESTY_RULE.md
 *              + /app/memory/sprints/JC_WS_DECK_A7_INTELLIGENCE_TAB_COMPLETION.md
 *              + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A7.
 *
 * Intelligence tab expanded content — MVP. Reads existing
 * `doc.intelligence_report` — no new backend LOC, no new LLM prompt.
 * Refresh button is a PURE RE-FETCH via the caller's `onRefresh`
 * callback (which calls `loadDoc()` on the parent DocumentOverlay).
 *
 * F.6 discipline-pay: N/A · Refresh is a pure GET re-fetch of already-
 * computed intelligence_report. No new LLM path introduced. Full-A7
 * regeneration engine (if desired later) would introduce F.6 pay-in.
 *
 * Stories closed (MVP-level):
 *   DECK-045 ✅ Plain-language explanation (renders confidence_rationale)
 *   DECK-046 ✅ Clarity metrics (confidence_pct + sources_count + pending_recs)
 *   DECK-047 ✅ Provenance sub-section (source_document_ids list)
 *   DECK-049 ✅ Refresh Intelligence button (pure re-fetch via onRefresh)
 *
 * Deferred to full-A7 backend engine dispatch:
 *   DECK-048 (if present) + LLM-driven regeneration — requires F.6 pay-in.
 */
import React from "react";
import { RefreshCw, BarChart3, BookOpen, FileText } from "lucide-react";

function formatIso(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
}

export default function IntelligencePanelExpanded({ doc, onRefresh }) {
  const report = (doc && doc.intelligence_report) || null;
  const rationale = (doc && typeof doc.confidence_rationale === "string" && doc.confidence_rationale.trim())
    ? doc.confidence_rationale.trim()
    : (report && typeof report.confidence_rationale === "string" ? report.confidence_rationale.trim() : "");
  const sourceIds = (doc && Array.isArray(doc.source_document_ids)) ? doc.source_document_ids : [];
  const scoredAt = (doc && (doc.confidence_recomputed_at || doc.confidence_scored_at)) || null;

  const confidencePct = report && typeof report.confidence_pct === "number" ? report.confidence_pct : null;
  const sourcesCount = report && typeof report.sources_count === "number" ? report.sources_count : sourceIds.length;
  const pendingRecs = report && typeof report.pending_recommendations === "number" ? report.pending_recommendations : 0;

  return (
    <div
      data-testid="intelligence-panel-expanded-root"
      className="mx-4 my-4 space-y-4"
    >
      {/* DECK-046 · Clarity metrics */}
      <div
        data-testid="intelligence-panel-clarity-metrics"
        className="border border-[var(--rule)] rounded-md bg-[var(--parchment)] p-3"
      >
        <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] mb-2">
          <BarChart3 className="w-3 h-3" strokeWidth={1.6} />
          Clarity metrics
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <div className="text-[11px] text-[var(--muted)]">Confidence</div>
            <div className="text-[18px] font-mono text-[var(--ink)]" data-testid="intelligence-panel-confidence-pct">
              {confidencePct !== null ? `${confidencePct}%` : "—"}
            </div>
          </div>
          <div>
            <div className="text-[11px] text-[var(--muted)]">Sources</div>
            <div className="text-[18px] font-mono text-[var(--ink)]" data-testid="intelligence-panel-sources-count">
              {sourcesCount}
            </div>
          </div>
          <div>
            <div className="text-[11px] text-[var(--muted)]">Pending recs</div>
            <div className="text-[18px] font-mono text-[var(--ink)]" data-testid="intelligence-panel-pending-recs">
              {pendingRecs}
            </div>
          </div>
        </div>
        {scoredAt && (
          <div className="mt-2 text-[10.5px] italic text-[var(--muted)]">
            Scored at {formatIso(scoredAt)}
          </div>
        )}
      </div>

      {/* DECK-045 · Plain-language explanation */}
      <div
        data-testid="intelligence-panel-explanation"
        className="border border-[var(--rule)] rounded-md bg-white p-3"
      >
        <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] mb-2">
          <BookOpen className="w-3 h-3" strokeWidth={1.6} />
          Explanation
        </div>
        {rationale ? (
          <p className="text-[13px] leading-relaxed text-[var(--ink)] whitespace-pre-line">
            {rationale}
          </p>
        ) : (
          <p className="text-[12px] italic text-[var(--muted)]" data-testid="intelligence-panel-explanation-empty">
            No plain-language explanation has been captured for this document.
          </p>
        )}
      </div>

      {/* DECK-047 · Provenance */}
      <div
        data-testid="intelligence-panel-provenance"
        className="border border-[var(--rule)] rounded-md bg-white p-3"
      >
        <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] mb-2">
          <FileText className="w-3 h-3" strokeWidth={1.6} />
          Provenance
        </div>
        {sourceIds.length > 0 ? (
          <ul className="space-y-1">
            {sourceIds.map((id, idx) => (
              <li key={`${id}-${idx}`}
                  data-testid="intelligence-panel-provenance-item"
                  className="text-[12px] font-mono text-[var(--muted)]">
                {id}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-[12px] italic text-[var(--muted)]" data-testid="intelligence-panel-provenance-empty">
            No source documents are attached to this deck.
          </p>
        )}
      </div>

      {/* DECK-049 · Refresh Intelligence — pure re-fetch, no LLM path */}
      <div className="flex justify-end">
        <button
          type="button"
          onClick={() => onRefresh && onRefresh()}
          className="px-3 py-1.5 text-[11.5px] uppercase tracking-[0.14em] font-mono text-[var(--ink)] hover:bg-[var(--cream-deep)]/40 border border-[var(--rule)] rounded-sm flex items-center gap-1.5"
          data-testid="intelligence-panel-refresh-btn"
          title="Re-fetch the intelligence report from the server"
        >
          <RefreshCw className="w-3.5 h-3.5" strokeWidth={1.6} />
          Refresh Intelligence
        </button>
      </div>
    </div>
  );
}
