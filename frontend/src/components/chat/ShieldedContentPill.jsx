/**
 * ShieldedContentPill — reinstated per user amendment 2026-07-02
 * (JC-CHAT-STAGE-A-AMENDMENT-SHIELD-PILL-PLUS-SEE-MORE).
 *
 * Renders BELOW each assistant chat message that had Synisense
 * shielding applied. Two elements inside the pill container:
 *   1. The classic "Content screened · N" chip (button-styled per
 *      the pre-Stage-A JSX snapshot; hover tooltip = by_type
 *      breakdown; keyboard accessible).
 *   2. A "See more" button that opens a chat-level audit modal
 *      replicating the content previously shown by the removed
 *      header AUDIT button (`AuditDialog` at Chat.jsx:2284 pre-
 *      commit-1352e0d5).
 *
 * Coexists with `PerMessageSynisenseBadge` — the badge stays on the
 * meta row above the message body ("N IDENTIFIERS PROTECTED …" with
 * per-turn audit-panel expansion + Privacy report PDF). This pill
 * sits below the message body with the ambient span count + the
 * chat-level See more.
 *
 * Canonical spec: /app/memory/JC_CHAT_CANONICAL_SPEC.md §A + user
 * amendment 2026-07-02.
 * Amendment memo: /app/memory/sprints/JC_CHAT_STAGE_A_AMENDMENT.md.
 */
import React, { useEffect, useState } from "react";
import { FileLock2, Download } from "lucide-react";
import api from "../../lib/api/apiV2";
import { apiErrorMessage } from "../../lib/api";
import { toast } from "sonner";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../ui/dialog";

/**
 * Small helper — formats an {entity_type: count, ...} map into
 * "email ×3, phone ×2" for tooltip use. Matches the pre-Stage-A
 * `formatSyniBreakdown` in Chat.jsx.
 */
function formatBreakdown(byType) {
  if (!byType || typeof byType !== "object") return "";
  return Object.entries(byType)
    .filter(([, n]) => n > 0)
    .sort((a, b) => b[1] - a[1])
    .map(([t, n]) => `${t} ×${n}`)
    .join(", ");
}

export default function ShieldedContentPill({ m, chatId }) {
  const [dialogOpen, setDialogOpen] = useState(false);

  const stats = m?.synisense_stats;
  const spans = stats?.spans_redacted ?? 0;
  if (m?.role === "user" || spans <= 0) return null;

  const breakdownText = formatBreakdown(stats?.by_type);
  const countLabel = spans === 1 ? "span" : "spans";
  const tooltipText = `Content screened. ${spans} ${countLabel} redacted.${
    breakdownText ? `\n\n${breakdownText}` : ""
  }`;
  const ariaText = `Content screened. ${spans} ${countLabel} redacted.${
    breakdownText ? ` ${breakdownText}` : ""
  }`;

  return (
    <>
      <div
        className="mt-2 inline-flex items-center gap-1 text-[10.5px] text-[var(--muted)]"
        data-testid="chat-synisense-icon"
      >
        <button
          type="button"
          className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-sm border border-[var(--rule)] bg-[var(--cream-deep)]/40 hover:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)] cursor-help"
          aria-label={ariaText}
          title={tooltipText}
        >
          <FileLock2 className="w-3 h-3 text-[var(--accent)]" aria-hidden="true" />
          <span>
            Content screened · {spans}
          </span>
        </button>
        <button
          type="button"
          onClick={() => setDialogOpen(true)}
          data-testid="chat-synisense-see-more-btn"
          className="ml-1 px-1.5 py-0.5 rounded-sm border border-[var(--rule)] bg-transparent hover:border-[var(--accent)] hover:text-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)] text-[10.5px] text-[var(--muted)] transition-colors"
          aria-label="See more audit details"
        >
          See more
        </button>
      </div>
      <ChatAuditDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        chatId={chatId}
      />
    </>
  );
}

/**
 * ChatAuditDialog — chat-level audit modal. Content parity with the
 * removed pre-Stage-A AuditDialog (Chat.jsx:2284 pre-commit-1352e0d5).
 * Fetches:
 *   - GET /api/chats/{cid}/audit          (rows + append-only hash chain)
 *   - GET /api/chats/{cid}/synisense-metrics (identifiers_redacted,
 *                                              model_calls, storyline)
 * Export:
 *   - GET /api/chats/{cid}/audit/export.zip (ZIP with verify.py)
 * Cross-link:
 *   - `akki:open-trust-panel` event → AppShell Trust Panel.
 */
function ChatAuditDialog({ open, onClose, chatId }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    if (!open || !chatId) return;
    setLoading(true);
    api
      .get(`/chats/${chatId}/audit`)
      .then(({ data }) => setRows(data?.rows || []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
    api
      .get(`/chats/${chatId}/synisense-metrics`)
      .then(({ data }) => setMetrics(data))
      .catch(() => setMetrics(null));
  }, [open, chatId]);

  const onDownload = async () => {
    if (!chatId) return;
    try {
      const res = await api.get(`/chats/${chatId}/audit/export.zip`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = window.document.createElement("a");
      a.href = url;
      a.download = `akki-chat-audit-${chatId.slice(0, 8)}.zip`;
      window.document.body.appendChild(a);
      a.click();
      window.document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success("Audit pack downloaded.");
    } catch (e) {
      toast.error(apiErrorMessage(e));
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent
        className="bg-[var(--cream)] border-[var(--rule)] max-w-3xl max-h-[80vh] overflow-y-auto"
        data-testid="chat-audit-dialog"
      >
        <DialogHeader>
          <div className="flex items-center justify-between gap-3">
            <DialogTitle className="akki-serif font-normal">Audit trail</DialogTitle>
            <Button
              size="sm"
              onClick={onDownload}
              disabled={loading || rows.length === 0}
              className="bg-[var(--ink)] hover:bg-[var(--ink)]/90 text-white text-[11.5px] h-8"
              data-testid="chat-audit-export-btn"
            >
              <Download className="w-3 h-3 mr-1.5" /> Export audit pack
            </Button>
          </div>
          <DialogDescription className="text-[12.5px] text-[var(--muted)]">
            Append-only, hash-chained. Auditors can verify the chain by recomputing
            each row&apos;s SHA256 against the canonical JSON of (prev_hash, id, at,
            account_id, chat_id, action, payload, ip, ua_sha). The export bundles a
            stdlib-only <code className="font-mono text-[11px] px-1">verify.py</code>{" "}
            for one-shot validation.
          </DialogDescription>
        </DialogHeader>
        {metrics && (
          <div
            className="border border-[var(--rule)] bg-[var(--cream)]/40 rounded-sm p-3 mb-3"
            data-testid="chat-audit-synisense-metrics"
          >
            <div className="flex flex-wrap gap-x-6 gap-y-2 items-baseline">
              <div>
                <span className="block text-[10px] uppercase tracking-[0.18em] text-[var(--muted)]">
                  Identifiers redacted
                </span>
                <span
                  className="akki-serif text-[24px] text-[var(--accent)]"
                  data-testid="metric-identifiers"
                >
                  {metrics.identifiers_redacted}
                </span>
                <span className="text-[11px] text-[var(--muted)] ml-1">
                  in this conversation
                </span>
              </div>
              <div>
                <span className="block text-[10px] uppercase tracking-[0.18em] text-[var(--muted)]">
                  Model calls
                </span>
                <span
                  className="akki-serif text-[24px] text-[var(--accent)]"
                  data-testid="metric-modelcalls"
                >
                  {metrics.model_calls}
                </span>
                <span className="text-[11px] text-[var(--muted)] ml-1">
                  through Synisense Shield
                </span>
              </div>
            </div>
            {metrics.storyline && (
              <p
                className="akki-serif text-[14px] text-[var(--ink)] italic mt-3 leading-relaxed"
                data-testid="metric-storyline"
              >
                {metrics.storyline}
              </p>
            )}
            <div className="flex justify-end mt-3">
              <button
                type="button"
                onClick={() => {
                  onClose();
                  window.dispatchEvent(new Event("akki:open-trust-panel"));
                }}
                className="group inline-flex items-center gap-2 text-[13px] font-medium text-[var(--graphite)] hover:text-[var(--ink)] transition-colors"
                data-testid="chat-audit-trust-panel-link"
              >
                View full Trust Panel
                <span className="inline-flex items-center transition-all text-[var(--graphite)] group-hover:text-[var(--oxblood)] group-hover:ml-1">
                  →
                </span>
              </button>
            </div>
          </div>
        )}
        {loading ? (
          <p className="text-[12px] text-[var(--muted)] italic text-center py-8">
            Loading…
          </p>
        ) : rows.length === 0 ? (
          <p className="text-[12px] text-[var(--muted)] italic text-center py-8">
            No audit rows yet.
          </p>
        ) : (
          <div className="font-mono text-[11px] space-y-2" data-testid="chat-audit-rows">
            {rows.map((r) => (
              <div
                key={r.id}
                className="bg-white border border-[var(--rule)] rounded-sm p-2.5"
              >
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <span className="text-[var(--accent)] uppercase">{r.action}</span>
                  <span className="text-[var(--muted)] text-[10px]">{r.at}</span>
                </div>
                {r.payload_summary && (
                  <p className="text-[var(--ink)] mt-1 text-[11px] font-sans">
                    {r.payload_summary}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
