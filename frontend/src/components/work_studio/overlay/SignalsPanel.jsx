/**
 * JC-WS-DECK-A9-BACKEND-DECK-SIGNAL-EXTRACTION · 2026-07-04
 *
 * Canonical spec: /app/memory/rules/TAB_HONESTY_RULE.md
 *              + /app/memory/sprints/JC_WS_DECK_A9_BACKEND_DECK_SIGNAL_EXTRACTION.md
 *              + /app/memory/sprints/JC_WS_DECK_A9_SIGNALS_MVP.md (predecessor)
 *              + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A9.
 *
 * Signals tab — A9-MVP (FE-only read of intelligence_report.recommendations)
 * + A9-BE upgrade (backend extraction via /api/decks/{id}/signals).
 * TAB HONESTY RULE: signal state is server-side (deck_signals collection);
 * addressed toggle via PATCH — no localStorage.
 *
 * F.6 discipline-pay: FULL (backend Shield-routed). FE calls the shipped
 * endpoint; no LLM SDK reference in this file.
 *
 * Stories closed:
 *   DECK-060 ✅ Backend deck-signal extraction (POST /extract)
 *   DECK-063 ✅ Persisted signal state + addressed toggle (GET + PATCH)
 */
import React, { useCallback, useEffect, useState } from "react";
import api from "@/lib/api/apiV2";
import { Sparkles, Shield } from "lucide-react";

function formatUpdatedIndicator(updatedAt) {
  if (!updatedAt) return "";
  const then = new Date(updatedAt);
  if (Number.isNaN(then.getTime())) return "";
  const seconds = Math.max(0, Math.round((Date.now() - then.getTime()) / 1000));
  if (seconds < 5) return "Updated just now";
  if (seconds < 60) return `Updated ${seconds}s ago`;
  if (seconds < 3600) return `Updated ${Math.round(seconds / 60)}m ago`;
  return `Updated ${then.toLocaleString([], { dateStyle: "medium", timeStyle: "short" })}`;
}

export default function SignalsPanel({ doc }) {
  const documentId = doc && doc.id;
  const report = doc && doc.intelligence_report;
  const legacyRecs = (report && Array.isArray(report.recommendations)) ? report.recommendations : [];

  const [backendSignals, setBackendSignals] = useState([]);
  const [derivationClass, setDerivationClass] = useState(null);
  const [updatedAt, setUpdatedAt] = useState(null);
  const [shieldAuditId, setShieldAuditId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState(null);

  const applyResponse = useCallback((data) => {
    if (!data) return;
    setBackendSignals(Array.isArray(data.signals) ? data.signals : []);
    setDerivationClass(data.derivation_class || null);
    setUpdatedAt(data.updated_at || null);
    setShieldAuditId(data.shield_audit_event_id || null);
  }, []);

  useEffect(() => {
    if (!documentId) return () => {};
    let cancelled = false;
    setLoading(true);
    (async () => {
      try {
        const resp = await api.get(`/decks/${documentId}/signals`);
        if (cancelled) return;
        applyResponse(resp && resp.data);
      } catch (err) {
        if (cancelled) return;
        setError((err && err.message) || "Failed to load signals");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [documentId, applyResponse]);

  const handleExtract = async () => {
    if (!documentId || extracting) return;
    setExtracting(true);
    setError(null);
    try {
      const resp = await api.post(`/decks/${documentId}/signals/extract`, {});
      applyResponse(resp && resp.data);
    } catch (err) {
      setError((err && err.message) || "Extraction failed");
    } finally {
      setExtracting(false);
    }
  };

  const handleToggleAddressed = async (signalId, nextAddressed) => {
    if (!documentId) return;
    // Optimistic UI update.
    setBackendSignals((prev) => prev.map((s) => (s.id === signalId ? { ...s, addressed: nextAddressed } : s)));
    try {
      const resp = await api.patch(`/decks/${documentId}/signals/${signalId}`, { addressed: nextAddressed });
      applyResponse(resp && resp.data);
    } catch {
      // Revert on failure.
      setBackendSignals((prev) => prev.map((s) => (s.id === signalId ? { ...s, addressed: !nextAddressed } : s)));
    }
  };

  const hasBackend = backendSignals.length > 0;
  const displayList = hasBackend ? backendSignals : legacyRecs;
  const updatedIndicator = formatUpdatedIndicator(updatedAt);

  return (
    <div
      id="document-overlay-tab-content-signals-body"
      data-testid="signals-panel-root"
      className="mx-4 my-4 space-y-3"
    >
      <div className="flex items-center justify-between">
        <div className="text-[13px] text-[var(--muted)]">
          {hasBackend
            ? "Signals extracted from this deck. Toggle addressed as you review."
            : "Recommendations surfaced from the deck's intelligence report. Review these before you commit."}
        </div>
        <div className="flex items-center gap-3">
          {derivationClass && (
            <span
              className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border border-[var(--rule)] text-[var(--muted)] flex items-center gap-1"
              data-testid="signals-panel-derivation-class"
              title="De-identification class inherited from source deck"
            >
              <Shield className="w-3 h-3" strokeWidth={1.6} /> {derivationClass}
            </span>
          )}
          {updatedIndicator && (
            <span
              className="text-[10.5px] italic text-[var(--muted)]"
              data-testid="signals-panel-updated-indicator"
            >
              {updatedIndicator}
            </span>
          )}
          <button
            type="button"
            onClick={handleExtract}
            disabled={extracting || !documentId}
            className="text-[11px] px-2 py-0.5 border border-[var(--rule)] rounded-sm hover:bg-[var(--cream-deep)]/40 disabled:opacity-50 flex items-center gap-1"
            data-testid="signals-panel-extract-btn"
            title="Extract signals from this deck (F.6 Shield-routed)"
          >
            <Sparkles className="w-3 h-3" strokeWidth={1.6} />
            {extracting ? "Extracting…" : hasBackend ? "Re-extract" : "Extract signals"}
          </button>
        </div>
      </div>

      {shieldAuditId && (
        <div
          className="text-[10.5px] font-mono text-[var(--muted)] truncate"
          data-testid="signals-panel-shield-audit-id"
          title="Shield audit event id — deep-link to Trust Center audit"
        >
          shield_audit_event_id: {shieldAuditId}
        </div>
      )}

      {loading && (
        <div className="text-[12.5px] italic text-[var(--muted)]" data-testid="signals-panel-loading">
          Loading signals…
        </div>
      )}

      {error && (
        <div className="text-[12.5px] text-[var(--oxblood)]" data-testid="signals-panel-error">
          {error}
        </div>
      )}

      {!loading && displayList.length === 0 && (
        <div
          className="mx-0 my-8 py-16 px-6 text-center text-[var(--muted)] italic text-[13px] border border-dashed border-[var(--rule)] rounded-md"
          data-testid="signals-panel-empty-state"
        >
          No signals surfaced yet. Click &quot;Extract signals&quot; to fire the pipeline (Shield-routed), or wait for the deck&apos;s intelligence report to produce recommendations.
        </div>
      )}

      {!loading && displayList.length > 0 && (
        <ul className="space-y-2">
          {displayList.map((rec, idx) => {
            const id = (rec && rec.id) || `rec-${idx}`;
            const text = (rec && rec.text) || "";
            const addressed = Boolean(rec && rec.addressed);
            const category = (rec && rec.category) || null;
            return (
              <li
                key={id}
                data-testid="signals-panel-item"
                className="border border-[var(--rule)] rounded-md px-3 py-2 bg-[var(--parchment)] flex items-start gap-2"
              >
                <button
                  type="button"
                  onClick={() => hasBackend && handleToggleAddressed(id, !addressed)}
                  disabled={!hasBackend}
                  className={
                    "text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded shrink-0 " +
                    (addressed
                      ? "bg-[var(--muted)] text-white"
                      : "bg-[var(--oxblood)] text-white")
                    + (hasBackend ? " cursor-pointer hover:opacity-80" : " cursor-default")
                  }
                  data-testid="signals-panel-item-badge"
                  title={hasBackend ? "Toggle addressed" : ""}
                >
                  {addressed ? "Addressed" : "Open"}
                </button>
                <div className="flex-1">
                  <p className="text-[13px] leading-relaxed">{text}</p>
                  {category && (
                    <span
                      className="text-[10px] uppercase tracking-wide text-[var(--muted)]"
                      data-testid="signals-panel-item-category"
                    >
                      {category}
                    </span>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
