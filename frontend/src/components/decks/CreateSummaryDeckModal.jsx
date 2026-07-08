// CreateSummaryDeckModal.jsx
// Canonical Spec: UX Brief v1.1 (7 July 2026) §4.2 + §4.3.
// JC-WS-DECK-QA-RECOVERY-STAGE-1 · v1.1-compliant Create Summary Deck flow.
// Structural fix: eliminates Work Studio Composer + approval workflow from
// the deck creation path. Backend engines (`/decks/outline` +
// `/decks/{id}/generate` with confirmed=true) are REUSED — this component
// chains them invisibly so the user sees ONE modal with title → Start From
// radio → in-place progress checklist → completion CTAs.
//
// v1.1 story IDs closed by this component (per RULE-CANONICAL-SPEC-UX-BRIEF-V1-1):
//   DECK-013, DECK-014, DECK-015, DECK-016, DECK-017, DECK-018, DECK-019,
//   DECK-020, DECK-021, DECK-022, DECK-023, DECK-024, DECK-025, DECK-026,
//   DECK-027, DECK-028, DECK-029, DECK-030, DECK-031, DECK-032, DECK-033.

import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Loader2, Sparkles, Download, MessageSquare, X, Check, Search, FileText } from "lucide-react";
import { toast } from "sonner";
import api from "@/lib/api/apiV2";
import { apiErrorMessage } from "@/lib/api";

// Modal phase enum
const PHASE = {
  FORM: "form",
  GENERATING: "generating",
  COMPLETE: "complete",
};

// Start From radio options + v1.1 sublabels (§4.2 verbatim intent).
const START_FROM_OPTIONS = [
  {
    key: "brief",
    label: "An existing brief in this workspace",
    sublabel: "Akki generates the deck immediately from your selected brief(s).",
  },
  {
    key: "uploaded",
    label: "An external document I've already uploaded",
    sublabel: "Akki generates the deck immediately from your selected document(s).",
  },
  {
    key: "blank",
    label: "Blank — I'll write it myself",
    sublabel: "You author the context first; deck is generated from what you write.",
  },
];

// v1.1 §4.3 — progress checklist steps (verbatim labels).
const PROGRESS_STEPS = [
  { key: "reading", label: "Reading your sources" },
  { key: "structuring", label: "Structuring the slides" },
  { key: "drafting", label: "Drafting the content" },
];

export default function CreateSummaryDeckModal({
  open,
  contextId,
  onOpenChange,
  onDeckCreated,   // (deck) => void — parent auto-opens detail view
  onGoToChat,      // (deck) => void — take-to-chat CTA handler
  onDownload,      // (deck) => void — download CTA handler
}) {
  const [phase, setPhase] = useState(PHASE.FORM);
  const [title, setTitle] = useState("");
  const [startFrom, setStartFrom] = useState("brief");
  const [sources, setSources] = useState([]); // [{id, name, kind}]
  const [availableSources, setAvailableSources] = useState([]);
  const [sourceSearch, setSourceSearch] = useState("");
  const [sourcesLoading, setSourcesLoading] = useState(false);
  const [progressState, setProgressState] = useState({ reading: "pending", structuring: "pending", drafting: "pending" });
  const [createdDeck, setCreatedDeck] = useState(null);
  const [error, setError] = useState(null);

  // Reset on close.
  useEffect(() => {
    if (!open) {
      const t = setTimeout(() => {
        setPhase(PHASE.FORM);
        setTitle("");
        setStartFrom("brief");
        setSources([]);
        setSourceSearch("");
        setProgressState({ reading: "pending", structuring: "pending", drafting: "pending" });
        setCreatedDeck(null);
        setError(null);
      }, 200);
      return () => clearTimeout(t);
    }
  }, [open]);

  // Load available sources when startFrom changes (brief or uploaded).
  useEffect(() => {
    if (!open || startFrom === "blank" || !contextId) return;
    let live = true;
    (async () => {
      setSourcesLoading(true);
      try {
        // For "brief" — v1.1 says "briefs and Akki-generated documents". For
        // MVP Stage 1 we pull from the documents endpoint (which covers both
        // uploaded AND Akki-generated docs); UI subtly disambiguates via
        // filter on server response. Simplified for Stage 1; can refine to
        // dedicated briefs endpoint in a later arc.
        const { data } = await api.get(`/contexts/${contextId}/documents`);
        if (!live) return;
        const items = Array.isArray(data) ? data : (data?.items || []);
        // For "brief" show all; for "uploaded" show all (same substrate for MVP).
        const mapped = items.slice(0, 200).map(d => ({
          id: d.id || d.doc_id,
          name: d.title || d.name || d.filename || "(Untitled)",
          kind: startFrom,
        })).filter(x => x.id);
        setAvailableSources(mapped);
      } catch (e) {
        // Silent — empty state is acceptable for MVP.
        setAvailableSources([]);
      } finally {
        if (live) setSourcesLoading(false);
      }
    })();
    return () => { live = false; };
  }, [open, startFrom, contextId]);

  const filteredSources = useMemo(() => {
    const q = sourceSearch.trim().toLowerCase();
    if (!q) return availableSources;
    return availableSources.filter(s => s.name.toLowerCase().includes(q));
  }, [availableSources, sourceSearch]);

  const isSourceSelected = (id) => sources.some(s => s.id === id);
  const toggleSource = (item) => {
    setSources(prev => (
      prev.some(s => s.id === item.id)
        ? prev.filter(s => s.id !== item.id)
        : [...prev, item]
    ));
  };
  const removeTag = (id) => setSources(prev => prev.filter(s => s.id !== id));

  // Create Deck CTA enablement (v1.1 §4.2 — title required; sources required
  // unless blank).
  const canSubmit = useMemo(() => {
    if (!title.trim()) return false;
    if (startFrom === "blank") return true;
    return sources.length > 0;
  }, [title, startFrom, sources]);

  // v1.1 §4.3 · async kick-off (POST returns 202 immediately) + polling.
  // JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — removes synchronous LLM-await
  // behind the ~21s DETERMINISTIC-EDGE-TIMEOUT-CEILING. The kick-off POST
  // returns in <1s with a job handle; the FE polls the status endpoint every
  // 2s and maps backend phases 1:1 to the progress checklist.
  const handleCreate = async () => {
    if (!canSubmit) return;
    setPhase(PHASE.GENERATING);
    setError(null);

    // Toast on generation start (v1.1 §4.3 requirement).
    toast.success("Deck generation in progress", {
      description: "This may take up to 60 seconds while Akki drafts the slides.",
    });

    try {
      // Step 1 · Outline kick-off (STANDARD tier, no deep-slot burn — now async).
      // JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — even the outline call
      // is Shield-routed and subject to the DETERMINISTIC-EDGE-TIMEOUT-CEILING,
      // so it too returns a job handle and is polled via the status endpoint.
      setProgressState({ reading: "active", structuring: "pending", drafting: "pending" });
      const outlineBody = {
        intent: title.trim() + (sources.length ? ` — sources: ${sources.map(s => s.name).join(", ")}` : ""),
        audience: null,
        target_slides: 8,
      };
      const { data: outlineKickoff } = await api.post(`/contexts/${contextId}/decks/outline`, outlineBody);
      if (!outlineKickoff || !outlineKickoff.job_id) {
        throw new Error("Outline kick-off did not return a job handle.");
      }
      const outlineStatusUrl = `/contexts/${contextId}/decks/generation-status/${outlineKickoff.job_id}`;
      // Poll outline job (max 150s — usually completes in <15s).
      // JC-WS-DECK-QA-RECOVERY-STAGE-2 (2026-07-05) — poll transient tolerance.
      let outlineConsecErrors = 0;
      let outline = null;
      let outlineErr = null;
      for (let i = 0; i < 75; i += 1) {
        await new Promise((r) => setTimeout(r, 2000));
        let st;
        try {
          const resp = await api.get(outlineStatusUrl);
          st = resp.data;
          outlineConsecErrors = 0;
        } catch (pollErr) {
          outlineConsecErrors += 1;
          if (outlineConsecErrors >= 6) throw pollErr;
          continue;
        }
        if (st?.phase === "complete") {
          outline = st.result;
          break;
        }
        if (st?.phase === "error") {
          outlineErr = st.error || { message: "Outline planning failed." };
          break;
        }
      }
      if (outlineErr) {
        throw new Error(outlineErr.message || "Outline planning failed.");
      }
      if (!outline || !outline.id) {
        throw new Error("Outline generation timed out after 150 seconds. Please try again.");
      }

      // Step 2 · Kick-off deck generation (async · 202 with job handle).
      // Endpoint returns immediately regardless of LLM duration.
      const { data: kickoff } = await api.post(
        `/contexts/${contextId}/decks/${outline.id}/generate`,
        { confirmed: true, edits: null },
      );

      if (!kickoff || !kickoff.job_id) {
        throw new Error("Kick-off did not return a job handle.");
      }

      // Step 3 · Poll status endpoint every 2s. Map backend phases 1:1 to
      // the progress checklist. Stop on `complete` or `error`.
      const jobId = kickoff.job_id;
      const statusUrl = `/contexts/${contextId}/decks/generation-status/${jobId}`;
      // Safety ceiling — 5 minutes max poll duration. If generation is still
      // running past that the FE surfaces a timeout error and the backend
      // job continues in the background (idempotent on next kick-off attempt).
      //
      // JC-WS-DECK-QA-RECOVERY-STAGE-2 (2026-07-05) — poll transient tolerance.
      // Occasional Cloudflare 502 on GET polls is noise; swallow up to N
      // consecutive errors before failing. Terminal backend phases
      // (complete/error) remain authoritative.
      const MAX_CONSECUTIVE_POLL_ERRORS = 6; // ~12s tolerance
      let consecutivePollErrors = 0;
      const pollMax = 150; // 150 * 2s = 300s
      let deck = null;
      let jobError = null;
      for (let i = 0; i < pollMax; i += 1) {
        await new Promise((r) => setTimeout(r, 2000));
        let status;
        try {
          const resp = await api.get(statusUrl);
          status = resp.data;
          consecutivePollErrors = 0;
        } catch (pollErr) {
          consecutivePollErrors += 1;
          if (consecutivePollErrors >= MAX_CONSECUTIVE_POLL_ERRORS) {
            throw pollErr;
          }
          continue;
        }
        const backendPhase = status?.phase;
        // Map backend phase to progress checklist state.
        if (backendPhase === "queued" || backendPhase === "reading_sources") {
          setProgressState({ reading: "active", structuring: "pending", drafting: "pending" });
        } else if (backendPhase === "structuring") {
          setProgressState({ reading: "done", structuring: "active", drafting: "pending" });
        } else if (backendPhase === "drafting") {
          setProgressState({ reading: "done", structuring: "done", drafting: "active" });
        } else if (backendPhase === "complete") {
          setProgressState({ reading: "done", structuring: "done", drafting: "done" });
          deck = status.result;
          break;
        } else if (backendPhase === "error") {
          jobError = status.error || { message: "Generation failed." };
          break;
        }
      }

      if (jobError) {
        throw new Error(jobError.message || "Generation failed.");
      }
      if (!deck) {
        throw new Error("Generation timed out after 5 minutes. Please try again — the job may still complete in the background.");
      }

      const enriched = { ...deck, _user_title: title.trim(), _sources: sources };
      setCreatedDeck(enriched);
      setPhase(PHASE.COMPLETE);

      // v1.1 §4.3: "Deck Detailed View opens automatically without requiring
      // the user to click the card." Fire the parent hook AFTER the modal
      // transitions to the completion phase (user still sees the Download
      // / Take-to-Chat / Close CTAs; parent may open the detail view in a
      // side pane or navigate). We do NOT auto-close the modal — user
      // explicitly closes via the Close CTA.
      if (onDeckCreated) onDeckCreated(enriched);
    } catch (e) {
      setError(apiErrorMessage(e));
      setPhase(PHASE.FORM);
      toast.error(apiErrorMessage(e));
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="max-w-2xl bg-white border border-[var(--rule)] rounded-sm"
        data-testid="create-summary-deck-modal"
      >
        <DialogHeader>
          <DialogTitle className="akki-serif text-[22px] text-[var(--ink)]">
            {phase === PHASE.COMPLETE ? "Deck ready" : "Create Summary Deck"}
          </DialogTitle>
        </DialogHeader>

        {/* PHASE 1 · Form (title + Start From radio + source multi-select) */}
        {phase === PHASE.FORM && (
          <div className="space-y-6" data-testid="create-deck-form">
            {/* Title (required) */}
            <div>
              <Label className="text-[11px] uppercase tracking-[0.16em] text-slate-500">
                Title
              </Label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. April ExCo Read-out"
                className="mt-1.5"
                data-testid="create-deck-title-input"
                autoFocus
              />
            </div>

            {/* Start From radio (3 options with sublabels · v1.1 §4.2) */}
            <div>
              <Label className="text-[11px] uppercase tracking-[0.16em] text-slate-500 mb-2 block">
                Start from
              </Label>
              <div className="space-y-2" data-testid="start-from-radio-group">
                {START_FROM_OPTIONS.map(opt => (
                  <label
                    key={opt.key}
                    className={`flex items-start gap-3 p-3 border rounded-sm cursor-pointer transition-colors ${
                      startFrom === opt.key
                        ? "border-[var(--accent)] bg-[var(--accent)]/5"
                        : "border-[var(--rule)] hover:border-[var(--muted)]"
                    }`}
                    data-testid={`start-from-option-${opt.key}`}
                  >
                    <input
                      type="radio"
                      name="startFrom"
                      value={opt.key}
                      checked={startFrom === opt.key}
                      onChange={() => { setStartFrom(opt.key); setSources([]); }}
                      className="mt-1"
                      data-testid={`start-from-radio-${opt.key}`}
                    />
                    <div className="flex-1">
                      <div className="text-[14px] text-[var(--ink)]">{opt.label}</div>
                      <div className="text-[12px] text-[var(--muted)] mt-0.5">{opt.sublabel}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Source multi-select (only for brief / uploaded) */}
            {startFrom !== "blank" && (
              <div data-testid="source-multi-select-container">
                <Label className="text-[11px] uppercase tracking-[0.16em] text-slate-500 mb-2 block">
                  {startFrom === "brief" ? "Select brief(s)" : "Select document(s)"}
                </Label>
                <div className="relative mb-2">
                  <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-[var(--muted)]" />
                  <Input
                    value={sourceSearch}
                    onChange={(e) => setSourceSearch(e.target.value)}
                    placeholder="Search…"
                    className="pl-8"
                    data-testid="source-search-input"
                  />
                </div>
                <div
                  className="max-h-40 overflow-y-auto border border-[var(--rule)] rounded-sm bg-[var(--cream-deep)]/20"
                  data-testid="source-select-list"
                >
                  {sourcesLoading && (
                    <div className="p-3 text-[12px] text-[var(--muted)] flex items-center gap-2">
                      <Loader2 className="w-3 h-3 animate-spin" /> Loading…
                    </div>
                  )}
                  {!sourcesLoading && filteredSources.length === 0 && (
                    <div className="p-3 text-[12px] text-[var(--muted)]" data-testid="source-empty-state">
                      No matches. {startFrom === "uploaded" && "Don\u2019t see it? Upload from Documents first."}
                    </div>
                  )}
                  {!sourcesLoading && filteredSources.map(item => {
                    const selected = isSourceSelected(item.id);
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => toggleSource(item)}
                        className={`w-full text-left px-3 py-2 flex items-center gap-2 text-[13px] hover:bg-white transition-colors ${
                          selected ? "bg-white" : ""
                        }`}
                        data-testid={`source-option-${item.id}`}
                      >
                        <span className={`w-4 h-4 border rounded-sm flex items-center justify-center ${
                          selected ? "bg-[var(--accent)] border-[var(--accent)]" : "border-[var(--rule)]"
                        }`}>
                          {selected && <Check className="w-3 h-3 text-white" />}
                        </span>
                        <FileText className="w-3.5 h-3.5 text-[var(--muted)] shrink-0" />
                        <span className="truncate">{item.name}</span>
                      </button>
                    );
                  })}
                </div>

                {/* Selected sources as tags below the list */}
                {sources.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3" data-testid="source-tags-list">
                    {sources.map(s => (
                      <span
                        key={s.id}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-[var(--accent)]/10 border border-[var(--accent)]/30 rounded-sm text-[11px] text-[var(--ink)]"
                        data-testid={`source-tag-${s.id}`}
                      >
                        {s.name}
                        <button
                          type="button"
                          onClick={() => removeTag(s.id)}
                          className="hover:text-red-600"
                          data-testid={`source-tag-remove-${s.id}`}
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="text-[12px] text-red-700 bg-red-50 border border-red-200 rounded-sm p-2" data-testid="create-deck-error">
                {error}
              </div>
            )}

            {/* Create Deck CTA (inactive until title entered + sources if applicable) */}
            <div className="flex justify-end pt-2">
              <Button
                onClick={handleCreate}
                disabled={!canSubmit}
                className="bg-[var(--accent)] hover:bg-[var(--accent)]/90 text-white rounded-sm h-10 px-6"
                data-testid="create-deck-submit-btn"
              >
                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                Create Deck
              </Button>
            </div>
          </div>
        )}

        {/* PHASE 2 · In-place progress checklist */}
        {phase === PHASE.GENERATING && (
          <div className="space-y-4 py-4" data-testid="deck-generation-progress">
            <ol className="space-y-3">
              {PROGRESS_STEPS.map((step, idx) => {
                const status = progressState[step.key];
                return (
                  <li
                    key={step.key}
                    className="flex items-center gap-3"
                    data-testid={`progress-step-${step.key}-${status}`}
                  >
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center border ${
                      status === "done" ? "bg-emerald-600 border-emerald-600 text-white" :
                      status === "active" ? "border-[var(--accent)] text-[var(--accent)]" :
                      "border-[var(--rule)] text-[var(--muted)]"
                    }`}>
                      {status === "done" ? <Check className="w-3.5 h-3.5" /> :
                       status === "active" ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> :
                       <span className="text-[10px] font-mono">{idx + 1}</span>}
                    </span>
                    <span className={`text-[14px] ${
                      status === "done" ? "text-[var(--ink)]" :
                      status === "active" ? "text-[var(--accent)] font-medium" :
                      "text-[var(--muted)]"
                    }`}>
                      {step.label}
                    </span>
                  </li>
                );
              })}
            </ol>
            <p className="text-[11px] text-[var(--muted)] italic pt-2">
              You&apos;ll see the deck as soon as it&apos;s ready — usually 30-60 seconds.
            </p>
          </div>
        )}

        {/* PHASE 3 · Completion CTAs (Download · Take to Chat · Close) */}
        {phase === PHASE.COMPLETE && createdDeck && (
          <div className="space-y-4 py-4" data-testid="deck-completion-ctas">
            <div className="flex items-center gap-3 p-3 bg-emerald-50 border border-emerald-200 rounded-sm">
              <Check className="w-4 h-4 text-emerald-700 shrink-0" />
              <p className="text-[13px] text-emerald-900">
                Deck created. Detail view opens behind this modal.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-end">
              <Button
                variant="outline"
                onClick={() => onDownload?.(createdDeck)}
                className="rounded-sm h-9"
                data-testid="deck-complete-download-btn"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" /> Download
              </Button>
              <Button
                variant="outline"
                onClick={() => onGoToChat?.(createdDeck)}
                className="rounded-sm h-9"
                data-testid="deck-complete-take-to-chat-btn"
              >
                <MessageSquare className="w-3.5 h-3.5 mr-1.5" /> Take to Chat
              </Button>
              <Button
                onClick={() => onOpenChange(false)}
                className="bg-[var(--ink)] hover:bg-[var(--ink)]/90 text-white rounded-sm h-9"
                data-testid="deck-complete-close-btn"
              >
                Close
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
