/**
 * JC-WS-DECK-A9-SIGNALS-MVP · 2026-07-02
 *
 * Canonical spec: /app/memory/sprints/JC_WS_DECK_A9_SIGNALS_MVP.md
 * Path A execution plan: JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A9.
 *
 * FE-only render of existing doc.intelligence_report.recommendations.
 * NO Shield-routed extraction. NO new LLM prompt. F.6 discipline-pay N/A.
 * Full-A9 deck-signal extraction engine + Pulse feed integration DEFERRED
 * (scope-escalation candidate · ~150+ LOC backend + F.6 pay-in).
 */
import React from "react";

export default function SignalsPanel({ doc }) {
  const report = doc && doc.intelligence_report;
  const recommendations = (report && Array.isArray(report.recommendations)) ? report.recommendations : [];

  if (recommendations.length === 0) {
    return (
      <div
        className="mx-4 my-8 py-16 px-6 text-center text-[var(--muted)] italic text-[13px] border border-dashed border-[var(--rule)] rounded-md"
        data-testid="signals-panel-empty-state"
      >
        No signals surfaced yet. Recommendations from the deck's intelligence report will appear here once available.
      </div>
    );
  }

  return (
    <div
      id="document-overlay-tab-content-signals-body"
      data-testid="signals-panel-root"
      className="mx-4 my-4 space-y-3"
    >
      <div className="text-[13px] text-[var(--muted)] mb-2">
        Recommendations surfaced from the deck's intelligence report. Review these before you commit.
      </div>
      <ul className="space-y-2">
        {recommendations.map((rec, idx) => {
          const id = (rec && rec.id) || `rec-${idx}`;
          const text = (rec && rec.text) || "";
          const addressed = Boolean(rec && rec.addressed);
          return (
            <li
              key={id}
              data-testid="signals-panel-item"
              className="border border-[var(--rule)] rounded-md px-3 py-2 bg-[var(--parchment)] flex items-start gap-2"
            >
              <span
                className={
                  "text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded shrink-0 " +
                  (addressed
                    ? "bg-[var(--muted)] text-white"
                    : "bg-[var(--oxblood)] text-white")
                }
              >
                {addressed ? "Addressed" : "Open"}
              </span>
              <p className="text-[13px] leading-relaxed">{text}</p>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
