/**
 * JC-WS-DECK-A5-HEADER-FOOTER-PARITY-SHARE · 2026-07-02
 *
 * Canonical spec: /app/memory/rules/TAB_HONESTY_RULE.md
 *              + /app/memory/sprints/JC_WS_DECK_A5_HEADER_FOOTER_PARITY_SHARE.md
 *              + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A5.
 *
 * Detail-view footer parity — mounts BELOW the Tabs primitive (chrome
 * hard line: R7 preserved). Ships 4 affordances reachable from any tab:
 *   - Continue in Chat  → dispatches `akki:continue-in-chat` event
 *   - Continue in Solva → dispatches `akki:continue-in-solva` event
 *   - Download DOCX     → reuses existing render endpoint
 *   - Share             → client-side URL builder + clipboard copy
 *
 * TAB HONESTY RULE respected: Share URL references artefact_id +
 * activeTab only; recipient's own notes (A8-backend) are fetched
 * per-recipient-account — never leak sender's private data.
 */
import React, { useState } from "react";
import { toast } from "sonner";
import { MessageSquare, Brain, Download, Share2 } from "lucide-react";

export default function DetailFooter({ contextId, artefactId, activeTab, onDownload }) {
  const [copied, setCopied] = useState(false);

  const handleContinueInChat = () => {
    if (typeof window === "undefined") return;
    window.dispatchEvent(new CustomEvent(
      "akki:continue-in-chat",
      { detail: { contextId, artefactId } },
    ));
    toast.success("Opening Chat with this deck attached.");
  };

  const handleContinueInSolva = () => {
    if (typeof window === "undefined") return;
    window.dispatchEvent(new CustomEvent(
      "akki:continue-in-solva",
      { detail: { contextId, artefactId } },
    ));
    toast.success("Opening ThinkLab with this deck attached.");
  };

  const handleShare = async () => {
    if (typeof window === "undefined") return;
    // Client-side URL builder — includes ?tab=<activeTab> for deep-link.
    // TAB HONESTY: recipient's own notes are fetched per-their-account;
    // sender's private notes NEVER leak in the URL.
    const url = new URL(window.location.href);
    url.searchParams.set("artefact_id", artefactId);
    if (activeTab) url.searchParams.set("tab", activeTab);
    const shareUrl = url.toString();
    try {
      if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(shareUrl);
        setCopied(true);
        toast.success("Share link copied to clipboard.");
        window.setTimeout(() => setCopied(false), 3000);
      } else {
        toast.info(shareUrl);
      }
    } catch {
      toast.error("Could not copy link. Please copy manually.");
    }
  };

  return (
    <div
      data-testid="document-overlay-detail-footer"
      className="border-t border-[var(--rule)] px-4 py-3 flex items-center justify-end gap-2 bg-[var(--cream)]"
    >
      <button
        type="button"
        onClick={handleContinueInChat}
        className="px-3 py-1.5 text-[11.5px] uppercase tracking-[0.14em] font-mono text-[var(--ink)] hover:bg-[var(--cream-deep)]/40 border border-[var(--rule)] rounded-sm flex items-center gap-1.5"
        data-testid="document-overlay-continue-in-chat-btn"
        title="Open Chat with this deck attached"
      >
        <MessageSquare className="w-3.5 h-3.5" strokeWidth={1.6} />
        Continue in Chat
      </button>
      <button
        type="button"
        onClick={handleContinueInSolva}
        className="px-3 py-1.5 text-[11.5px] uppercase tracking-[0.14em] font-mono text-[var(--ink)] hover:bg-[var(--cream-deep)]/40 border border-[var(--rule)] rounded-sm flex items-center gap-1.5"
        data-testid="document-overlay-continue-in-solva-btn"
        title="Open ThinkLab with this deck attached"
      >
        <Brain className="w-3.5 h-3.5" strokeWidth={1.6} />
        Continue in ThinkLab
      </button>
      <button
        type="button"
        onClick={() => onDownload && onDownload("docx")}
        className="px-3 py-1.5 text-[11.5px] uppercase tracking-[0.14em] font-mono text-[var(--ink)] hover:bg-[var(--cream-deep)]/40 border border-[var(--rule)] rounded-sm flex items-center gap-1.5"
        data-testid="document-overlay-footer-download-btn"
        title="Download DOCX"
      >
        <Download className="w-3.5 h-3.5" strokeWidth={1.6} />
        Download
      </button>
      <button
        type="button"
        onClick={handleShare}
        className="px-3 py-1.5 text-[11.5px] uppercase tracking-[0.14em] font-mono text-[var(--ink)] hover:bg-[var(--cream-deep)]/40 border border-[var(--rule)] rounded-sm flex items-center gap-1.5"
        data-testid="document-overlay-share-btn"
        title="Copy share link for this deck"
      >
        <Share2 className="w-3.5 h-3.5" strokeWidth={1.6} />
        {copied ? "Copied!" : "Share"}
      </button>
    </div>
  );
}
