// EnhanceDeckModal.jsx
// Canonical Spec: UX Brief v1.1 (7 July 2026) §4.5.
// JC-WS-DECK-QA-RECOVERY-STAGE-2 · Async-from-start Enhance journey.
//
// Modal: "Improve a Deck you already have"
//   - Styled file upload accepting DOCX, PPTX, PDF
//   - Filename tile + Remove control post-select
//   - Instructions field (verbatim placeholder from §4.5)
//   - Enhance CTA disabled until BOTH file + instructions present
//   - Output format PPTX/PDF/Auto (default "Auto — matches your uploaded file")
//   - Progress checklist mapping 1:1 to real backend phases (async-from-start:
//     kickoff POST returns 202 with job handle; FE polls status endpoint)
//   - Completion CTAs Download / Take to Chat / Close
//   - Enhanced card lands at top of Deck list with Draft + Akki Generated badges + pulse
//   - Card opens Deck Detailed View (auto-open per §4.5)
//
// Backend endpoint: POST /api/contexts/{cid}/work-studio/enhance/deck
//   (multipart form-data · file + instructions + output_format)
//   Returns 202 with {export_id, job_id, phase, status_url, ...}
//
// Status endpoint: GET /api/contexts/{cid}/decks/generation-status/{job_id}
//   Returns {job_id, phase, progress, result?, error?}
//   Phase enum: queued → reading_upload → structuring → drafting → complete | error
//
// Two-layer ceiling clarification (banked from user): async-from-start solves
// the EDGE ceiling; Shield-internal 20s asyncio.wait_for cap at
// services/synisense/shield/llm_router.py:186 STILL applies (HOLD pending
// Emergent). Enhance completion MAY block at the same phase as s05 — this is
// EXPECTED, not a bug. Do NOT manufacture completion. Partial-with-honest-
// declaration beats fabricated-green.

import React, { useEffect, useRef, useState } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Sparkles, Download, MessageSquare, X, Check, Upload, FileText } from "lucide-react";
import { toast } from "sonner";
import api from "@/lib/api/apiV2";
import { apiErrorMessage } from "@/lib/api";

// Modal phase enum (local FE)
const PHASE = {
  FORM: "form",
  KICKING_OFF: "kicking_off",
  GENERATING: "generating",
  COMPLETE: "complete",
};

// Progress checklist steps (v1.1 §4.5 · "a checklist of steps completing sequentially").
// Phases map 1:1 to backend enum values.
const PROGRESS_STEPS = [
  { key: "reading", label: "Reading your uploaded file" },
  { key: "structuring", label: "Structuring the enhancements" },
  { key: "drafting", label: "Drafting the enhanced deck" },
];

// Accepted file types per v1.1 §4.5 ("accepting DOCX, PPTX, and PDF files").
const ACCEPTED_TYPES = ".docx,.pptx,.pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/pdf";
const ACCEPTED_EXT_RE = /\.(docx|pptx|pdf)$/i;

// Instructions placeholder — VERBATIM from v1.1 §4.5.
const INSTRUCTIONS_PLACEHOLDER = "What should change — e.g. Tighten the executive summary, restructure the flow, update the theme.";

// Auto sublabel — VERBATIM from v1.1 §4.5.
const AUTO_SUBLABEL = "Auto — matches your uploaded file";

/**
 * EnhanceDeckModal — v1.1 §4.5 implementation.
 *
 * Props:
 *   - open · bool · controls dialog visibility
 *   - onOpenChange · (bool) → void · dialog open-state hook
 *   - contextId · string · required · scopes the enhance kickoff to a context
 *   - onDeckEnhanced · (row) → void · optional · fires on Path A completion
 *     so the parent can render the enhanced card at the top of the Deck list
 *     and auto-open the Deck Detailed View (per §4.5 "clicking the card opens
 *     the Deck Detailed View").
 */
export const EnhanceDeckModal = ({ open, onOpenChange, contextId, onDeckEnhanced }) => {
  const [phase, setPhase] = useState(PHASE.FORM);
  const [file, setFile] = useState(null);
  const [instructions, setInstructions] = useState("");
  const [outputFormat, setOutputFormat] = useState("auto");
  const [error, setError] = useState(null);
  const [progressState, setProgressState] = useState({
    reading: "pending", structuring: "pending", drafting: "pending",
  });
  const [enhancedRow, setEnhancedRow] = useState(null);
  const fileInputRef = useRef(null);

  // Reset when dialog closes.
  useEffect(() => {
    if (!open) {
      setPhase(PHASE.FORM);
      setFile(null);
      setInstructions("");
      setOutputFormat("auto");
      setError(null);
      setProgressState({ reading: "pending", structuring: "pending", drafting: "pending" });
      setEnhancedRow(null);
    }
  }, [open]);

  const canSubmit = phase === PHASE.FORM && !!file && !!instructions.trim();

  const handleFilePick = (e) => {
    const chosen = e.target.files?.[0];
    if (!chosen) return;
    if (!ACCEPTED_EXT_RE.test(chosen.name)) {
      toast.error("Only DOCX, PPTX, or PDF files are accepted.");
      return;
    }
    setFile(chosen);
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const humanSize = (bytes) => {
    if (!bytes) return "";
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(0)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  const extLabel = file
    ? (file.name.match(/\.([a-z]+)$/i)?.[1]?.toUpperCase() || "FILE")
    : "";

  // v1.1 §4.5 · Enhance journey — async-from-start.
  // Kickoff returns 202 with job handle; FE polls until complete or error.
  const handleEnhance = async () => {
    if (!canSubmit) return;
    setPhase(PHASE.KICKING_OFF);
    setError(null);

    toast.success("Deck enhancement in progress", {
      description: "This may take up to 60 seconds while Akki applies your instructions.",
    });

    try {
      const fd = new FormData();
      fd.append("instructions", instructions.trim());
      fd.append("output_format", outputFormat);
      fd.append("file", file);

      setPhase(PHASE.GENERATING);
      setProgressState({ reading: "active", structuring: "pending", drafting: "pending" });

      const { data: kickoff } = await api.post(
        `/contexts/${contextId}/work-studio/enhance/deck`,
        fd,
        { headers: { "Content-Type": "multipart/form-data" } },
      );
      if (!kickoff || !kickoff.job_id) {
        throw new Error("Enhance kick-off did not return a job handle.");
      }

      const jobId = kickoff.job_id;
      const statusUrl = `/contexts/${contextId}/decks/generation-status/${jobId}`;
      // Poll up to 5 minutes (150 * 2s). Async pattern makes edge ceiling
      // irrelevant. If the Shield-internal 20s cap fires, the job will
      // enter `error` phase and the FE surfaces the error with the exact
      // exception type + message. Do NOT retry silently (dispatch banking).
      //
      // JC-WS-DECK-QA-RECOVERY-STAGE-2 (2026-07-05) — poll transient tolerance.
      // Occasional Cloudflare 502 responses on the polling GET are noise
      // that should NOT terminate an otherwise-healthy background job.
      // We swallow up to N consecutive network/5xx errors and keep polling.
      // If N is exceeded, we surface the error honestly. Terminal phases
      // (`complete` / `error`) from the backend job store are ALWAYS
      // authoritative and never suppressed.
      const MAX_CONSECUTIVE_POLL_ERRORS = 6; // ~12s tolerance for edge blips
      let consecutivePollErrors = 0;
      let terminalRow = null;
      let terminalError = null;
      for (let i = 0; i < 150; i += 1) {
        // Await BEFORE first poll to avoid racing the runner's initial set_phase.
        await new Promise((r) => setTimeout(r, 2000));
        let st;
        try {
          const resp = await api.get(statusUrl);
          st = resp.data;
          consecutivePollErrors = 0;
        } catch (pollErr) {
          consecutivePollErrors += 1;
          if (consecutivePollErrors >= MAX_CONSECUTIVE_POLL_ERRORS) {
            throw pollErr;
          }
          continue;
        }
        const backendPhase = st?.phase;
        if (backendPhase === "queued" || backendPhase === "reading_sources") {
          setProgressState({ reading: "active", structuring: "pending", drafting: "pending" });
        } else if (backendPhase === "structuring") {
          setProgressState({ reading: "done", structuring: "active", drafting: "pending" });
        } else if (backendPhase === "drafting") {
          setProgressState({ reading: "done", structuring: "done", drafting: "active" });
        } else if (backendPhase === "complete") {
          setProgressState({ reading: "done", structuring: "done", drafting: "done" });
          terminalRow = st.result;
          break;
        } else if (backendPhase === "error") {
          terminalError = st.error || { message: "Enhance failed." };
          break;
        }
      }

      if (terminalError) {
        throw new Error(terminalError.message || "Enhance failed.");
      }
      if (!terminalRow) {
        throw new Error("Enhancement timed out after 5 minutes. Please try again — the job may still complete in the background.");
      }

      setEnhancedRow(terminalRow);
      setPhase(PHASE.COMPLETE);

      // v1.1 §4.5 · "Clicking the card opens the Deck Detailed View —
      // the same view used for generated decks." Fire the parent hook so
      // the enhanced card lands at the top of the Deck list; parent may
      // also auto-open the Detailed View post-modal-close.
      if (onDeckEnhanced) onDeckEnhanced(terminalRow);
    } catch (e) {
      setError(apiErrorMessage(e));
      setPhase(PHASE.FORM);
      toast.error(apiErrorMessage(e));
    }
  };

  const download = async () => {
    const exportId = enhancedRow?.id || enhancedRow?.export_id;
    if (!exportId) return;
    try {
      const { data } = await api.post(
        `/contexts/${contextId}/work-studio/exports/${exportId}/download-token`,
      );
      if (data?.download_url) {
        window.open(data.download_url, "_blank");
      } else {
        toast.error("Download link unavailable.");
      }
    } catch (e) {
      toast.error(apiErrorMessage(e));
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="sm:max-w-[560px]"
        data-testid="enhance-deck-modal"
      >
        <DialogHeader>
          <DialogTitle data-testid="enhance-deck-modal-title">
            Improve a Deck you already have
          </DialogTitle>
        </DialogHeader>

        {(phase === PHASE.FORM || phase === PHASE.KICKING_OFF) && (
          <div className="space-y-5" data-testid="enhance-deck-form">
            {/* Source file — v1.1 §4.5 styled file upload */}
            <div className="space-y-2">
              <Label className="text-[11px] uppercase tracking-widest text-neutral-500">
                Source file
              </Label>
              {!file ? (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full flex items-center justify-center gap-2 border-2 border-dashed border-neutral-300 rounded-md py-6 text-sm text-neutral-600 hover:border-neutral-400 hover:bg-neutral-50 transition-colors"
                  data-testid="enhance-file-upload-btn"
                >
                  <Upload className="w-4 h-4" />
                  Upload a DOCX, PPTX, or PDF
                </button>
              ) : (
                <div
                  className="flex items-center gap-3 border border-neutral-200 rounded-md px-3 py-2.5 bg-neutral-50"
                  data-testid="enhance-file-tile"
                >
                  <FileText className="w-5 h-5 text-neutral-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-neutral-900 truncate" data-testid="enhance-file-name">
                      {file.name}
                    </div>
                    <div className="text-xs text-neutral-500">
                      {extLabel} · {humanSize(file.size)}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={removeFile}
                    className="text-xs text-neutral-500 hover:text-neutral-900 px-2 py-1 hover:bg-neutral-200 rounded transition-colors"
                    data-testid="enhance-file-remove-btn"
                  >
                    Remove
                  </button>
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_TYPES}
                onChange={handleFilePick}
                className="hidden"
                data-testid="enhance-file-input"
              />
            </div>

            {/* Instructions — verbatim placeholder */}
            <div className="space-y-2">
              <Label htmlFor="enhance-instructions" className="text-[11px] uppercase tracking-widest text-neutral-500">
                Instructions
              </Label>
              <textarea
                id="enhance-instructions"
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                placeholder={INSTRUCTIONS_PLACEHOLDER}
                rows={3}
                className="w-full text-sm rounded-md border border-neutral-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent resize-none"
                data-testid="enhance-instructions-input"
              />
            </div>

            {/* Output format — PPTX / PDF / Auto (Auto default with verbatim sublabel) */}
            <div className="space-y-2">
              <Label className="text-[11px] uppercase tracking-widest text-neutral-500">
                Output format
              </Label>
              <div className="space-y-2" data-testid="enhance-output-format-group">
                {[
                  { key: "pptx", label: "PPTX", sublabel: null },
                  { key: "pdf", label: "PDF", sublabel: null },
                  { key: "auto", label: "Auto", sublabel: AUTO_SUBLABEL },
                ].map((opt) => (
                  <label
                    key={opt.key}
                    className={`flex items-start gap-3 border rounded-md px-3 py-2.5 cursor-pointer transition-colors ${
                      outputFormat === opt.key
                        ? "border-neutral-900 bg-neutral-50"
                        : "border-neutral-200 hover:border-neutral-300"
                    }`}
                    data-testid={`enhance-output-format-${opt.key}`}
                  >
                    <input
                      type="radio"
                      name="output_format"
                      value={opt.key}
                      checked={outputFormat === opt.key}
                      onChange={() => setOutputFormat(opt.key)}
                      className="mt-1"
                      data-testid={`enhance-output-format-radio-${opt.key}`}
                    />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-neutral-900">{opt.label}</div>
                      {opt.sublabel && (
                        <div className="text-xs text-neutral-500 mt-0.5">{opt.sublabel}</div>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {error && (
              <div
                className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2"
                data-testid="enhance-error"
              >
                {error}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="ghost"
                onClick={() => onOpenChange(false)}
                data-testid="enhance-cancel-btn"
              >
                Cancel
              </Button>
              <Button
                onClick={handleEnhance}
                disabled={!canSubmit}
                aria-disabled={!canSubmit ? "true" : "false"}
                className="bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="enhance-submit-btn"
              >
                {phase === PHASE.KICKING_OFF ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Enhancing…
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Enhance
                  </>
                )}
              </Button>
            </div>
          </div>
        )}

        {phase === PHASE.GENERATING && (
          <div className="space-y-4" data-testid="enhance-generating-body">
            <div className="text-sm text-neutral-600">
              Akki is enhancing your deck. This modal will update as each step completes.
            </div>
            <ul className="space-y-2" data-testid="enhance-progress-list">
              {PROGRESS_STEPS.map((step) => {
                const s = progressState[step.key] || "pending";
                return (
                  <li
                    key={step.key}
                    className="flex items-center gap-3"
                    data-testid={`enhance-progress-step-${step.key}`}
                  >
                    {s === "done" ? (
                      <Check className="w-4 h-4 text-emerald-600" />
                    ) : s === "active" ? (
                      <Loader2 className="w-4 h-4 text-neutral-900 animate-spin" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-neutral-300" />
                    )}
                    <span
                      className={`text-sm ${
                        s === "done" ? "text-neutral-900" : s === "active" ? "text-neutral-900 font-medium" : "text-neutral-400"
                      }`}
                    >
                      {step.label}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {phase === PHASE.COMPLETE && (
          <div className="space-y-4" data-testid="enhance-completion-body">
            <div className="text-sm text-neutral-700">
              Enhancement complete. Your enhanced deck is now in the deck list.
            </div>
            <div className="flex flex-wrap gap-2" data-testid="enhance-completion-ctas">
              <Button
                onClick={download}
                className="bg-neutral-900 text-white hover:bg-neutral-800"
                data-testid="enhance-complete-download-btn"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  onOpenChange(false);
                  window.location.href = "/app/chat";
                }}
                data-testid="enhance-complete-take-to-chat-btn"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                Take to Chat
              </Button>
              <Button
                variant="ghost"
                onClick={() => onOpenChange(false)}
                data-testid="enhance-complete-close-btn"
              >
                <X className="w-4 h-4 mr-2" />
                Close
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default EnhanceDeckModal;
