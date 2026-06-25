/**
 * PerMessageSynisenseBadge — the sole surviving Synisense marker on
 * the chat surface (JC-CHAT Stage A, 2026-06-25).
 *
 * Two states:
 *   • Collapsed (default): kicker label
 *       "N IDENTIFIERS PROTECTED · RESTORED ON YOUR VIEW"
 *     Hover tooltip surfaces the layer breakdown — same as ZZ.1.
 *   • Expanded (click / Enter / Space): inline panel revealing
 *       (1) per-turn audit data (identified + masked + class-based
 *           rendering pulled from /api/chats/{cid}/audit-panel) and
 *       (2) a "Privacy report (this conversation)" PDF download
 *           that calls the existing per-conversation endpoint
 *           /api/chats/{cid}/privacy-report.pdf.
 *
 * Stage A migrations rolled in here (per JC_CHAT_marker_inventory):
 *   • S0-F1 — Privacy-report relocation. The export was per-
 *     conversation today (clean move, not narrowing). Same chatId,
 *     same PDF.
 *   • S0-F2 — a11y carry-over from the removed header AUDIT button.
 *     The previous binding was only `title="View audit log"`; that
 *     plus an `aria-label` now sit on the badge's expand affordance.
 *   • Auto-mounted AuditPanel removal — the per-turn audit lives
 *     here now (chat-local UI; the AuditPanel component file itself
 *     stays untouched for Solva).
 *
 * Original ZZ.1 behaviour preserved:
 *   • 0 identifiers → render "—" (no expand affordance).
 *   • > 0 identifiers → kicker label + expandable audit access.
 */
import React, { useCallback, useEffect, useRef, useState } from "react";
import api from "../../lib/api/apiV2";
import { apiErrorMessage } from "../../lib/api";

export default function PerMessageSynisenseBadge({
  runs,
  testId,
  chatId,
  messageId,
}) {
  const [hoverOpen, setHoverOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [auditData, setAuditData] = useState(null);
  const [auditErr, setAuditErr] = useState(null);
  const [auditBusy, setAuditBusy] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadErr, setDownloadErr] = useState(null);
  const reducedRef = useRef(false);

  useEffect(() => {
    reducedRef.current = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }, []);

  const n = runs?.identifiers_redacted ?? 0;
  const lb = runs?.layer_breakdown || { regex: 0, presidio: 0, llm: 0 };

  const labelText =
    n === 0
      ? "—"
      : n === 1
      ? "1 IDENTIFIER PROTECTED · RESTORED ON YOUR VIEW"
      : `${n} IDENTIFIERS PROTECTED · RESTORED ON YOUR VIEW`;

  const fetchAudit = useCallback(async () => {
    if (!chatId || !messageId) return;
    setAuditBusy(true);
    setAuditErr(null);
    try {
      const { data } = await api.get(
        `/chats/${chatId}/audit-panel`,
        { params: { message_id: messageId } },
      );
      setAuditData(data);
    } catch (e) {
      const status = e?.response?.status;
      if (status === 404) {
        setAuditErr(
          "Audit data isn’t available for this turn yet — it usually appears within a few seconds. Refresh once it has settled.",
        );
      } else {
        setAuditErr(apiErrorMessage(e));
      }
    } finally {
      setAuditBusy(false);
    }
  }, [chatId, messageId]);

  const onExpand = useCallback(async () => {
    if (expanded) {
      setExpanded(false);
      return;
    }
    setExpanded(true);
    if (!auditData && !auditBusy) await fetchAudit();
  }, [expanded, auditData, auditBusy, fetchAudit]);

  const onKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        onExpand();
      }
    },
    [onExpand],
  );

  const onDownloadPrivacy = useCallback(async () => {
    if (!chatId) return;
    setDownloading(true);
    setDownloadErr(null);
    try {
      const res = await api.get(`/chats/${chatId}/privacy-report.pdf`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(res.data);
      const a = window.document.createElement("a");
      a.href = url;
      a.download = `privacy-report-${chatId}.pdf`;
      window.document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setDownloadErr(apiErrorMessage(e));
    } finally {
      setDownloading(false);
    }
  }, [chatId]);

  // Zero-identifier case: render the muted dash, no expand affordance.
  if (n === 0) {
    return (
      <span
        className="font-mono text-[10px] uppercase tracking-[0.14em] px-[6px] py-[1px] rounded-sm bg-[rgba(122,46,46,0.06)] text-[var(--oxblood)]"
        data-testid={testId || "chat-msg-synisense-badge"}
      >
        {labelText}
      </span>
    );
  }

  return (
    <span className="inline-flex flex-col items-start">
      <span
        className="relative inline-flex"
        onMouseEnter={() => setHoverOpen(true)}
        onMouseLeave={() => setHoverOpen(false)}
        onFocus={() => setHoverOpen(true)}
        onBlur={() => setHoverOpen(false)}
      >
        <button
          type="button"
          tabIndex={0}
          onClick={onExpand}
          onKeyDown={onKeyDown}
          aria-expanded={expanded}
          aria-controls={`${testId}-panel`}
          aria-label={`Identifiers protected: ${n}. Open this turn's audit log.`}
          title="Open this turn's audit log"
          className="font-mono text-[10px] uppercase tracking-[0.14em] px-[6px] py-[1px] rounded-sm bg-[rgba(122,46,46,0.06)] text-[var(--oxblood)] cursor-pointer hover:bg-[rgba(122,46,46,0.12)] focus:outline-none focus:ring-2 focus:ring-[var(--oxblood)] focus:ring-offset-1"
          data-testid={testId || "chat-msg-synisense-badge"}
          data-identifiers-redacted={n}
          data-identifiers-restored={n}
          aria-describedby={hoverOpen ? `${testId}-tooltip` : undefined}
        >
          {labelText}
        </button>
        {hoverOpen && !expanded && (
          <span
            id={`${testId}-tooltip`}
            role="tooltip"
            className="absolute left-0 top-full mt-1 z-30 whitespace-nowrap font-mono text-[10px] tracking-wide px-2 py-1 rounded-sm bg-[var(--ink)] text-[var(--parchment)]"
            style={{
              transition: reducedRef.current ? "none" : "opacity 150ms ease",
            }}
            data-testid={`${testId || "chat-msg-synisense-badge"}-tooltip`}
          >
            Redacted before model: {n} · Restored on your view: {n} · Layer 1 regex · {lb.regex || 0} · Layer 2 Presidio · {lb.presidio || 0} · Layer 3 fallback · {lb.llm || 0}
          </span>
        )}
      </span>

      {expanded && (
        <div
          id={`${testId}-panel`}
          role="region"
          aria-label="Per-turn Synisense audit details"
          data-testid={`${testId}-expanded`}
          className="mt-2 w-full max-w-[640px] border border-[var(--rule)] bg-[var(--cream)]/60 rounded-sm p-3 text-[12px] text-[var(--ink)] leading-relaxed"
        >
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-[var(--oxblood)]">
              This turn’s audit · {n} protected
            </div>
            <button
              type="button"
              onClick={onExpand}
              className="text-[11px] text-[var(--muted)] hover:text-[var(--ink)]"
              data-testid={`${testId}-collapse`}
              aria-label="Collapse audit panel"
            >
              Close
            </button>
          </div>

          {auditBusy && (
            <p
              className="text-[11.5px] text-[var(--muted)] italic"
              data-testid={`${testId}-loading`}
            >
              Loading audit details…
            </p>
          )}
          {!auditBusy && auditErr && (
            <p
              className="text-[11.5px] text-rose-700"
              data-testid={`${testId}-error`}
            >
              {auditErr}
            </p>
          )}
          {!auditBusy && !auditErr && auditData && (
            <AuditDetail data={auditData} />
          )}

          <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-[var(--rule)] pt-2">
            <button
              type="button"
              onClick={onDownloadPrivacy}
              disabled={downloading}
              data-testid={`${testId}-privacy-report`}
              className="inline-flex items-center gap-1.5 px-2 py-1 rounded-sm border border-[var(--rule)] bg-white hover:border-[var(--accent)] text-[11.5px] disabled:opacity-60"
              title="Download the per-conversation privacy report PDF"
              aria-label="Download privacy report for this conversation"
            >
              {downloading ? "Generating…" : "Privacy report (this conversation) · PDF"}
            </button>
            {downloadErr && (
              <span
                className="text-[10.5px] text-rose-700"
                data-testid={`${testId}-privacy-error`}
              >
                {downloadErr}
              </span>
            )}
          </div>
        </div>
      )}
    </span>
  );
}

function AuditDetail({ data }) {
  // The /audit-panel response composes prose for executive readability.
  // Mirror the AuditPanel component's shape minimally — show headline +
  // top sections, never raw enum values. The component's own deep view
  // remains available for Solva surfaces; this is the chat-local
  // condensed surface.
  if (!data) return null;
  const headline = data.headline_prose || data.headline || "";
  const sections = Array.isArray(data.sections) ? data.sections : [];
  return (
    <div className="space-y-2" data-testid="badge-audit-detail">
      {headline && (
        <p className="text-[12px] text-[var(--ink)]" data-testid="badge-audit-headline">
          {headline}
        </p>
      )}
      {sections.slice(0, 4).map((s, idx) => (
        <div key={s.id || s.title || idx}>
          {s.title && (
            <p className="text-[10px] uppercase tracking-[0.14em] text-[var(--muted)] mb-0.5">
              {s.title}
            </p>
          )}
          {s.prose && (
            <p className="text-[11.5px] text-[var(--ink)]">{s.prose}</p>
          )}
          {Array.isArray(s.items) && s.items.length > 0 && (
            <ul className="list-disc list-inside text-[11.5px] text-[var(--ink)] space-y-0.5">
              {s.items.slice(0, 6).map((it, i) => (
                <li key={i}>{typeof it === "string" ? it : it?.label || ""}</li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}
