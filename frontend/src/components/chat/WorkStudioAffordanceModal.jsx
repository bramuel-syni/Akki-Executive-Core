/**
 * WorkStudioAffordanceModal — Chat B1.1 (2026-06-24).
 *
 * Manual affordance: user opens a modal from the chat composer
 * toolbar, picks one of the 6 generation kinds, reviews mechanically
 * pre-filled `description` / `objective` / `scope` derived from the
 * live conversation, and hands off to the existing
 * `/api/contexts/{ctxId}/work-studio/export/{kind}` route (WS1 made
 * this route accept all 6 kinds uniformly).
 *
 * Pre-fill is MECHANICAL (no LLM call):
 *   - description ← last N user/assistant turns concatenated.
 *   - objective   ← user's most recent message (the last imperative
 *                    is approximated by taking the last sentence-
 *                    sized chunk of the last user message).
 *   - scope       ← single-line composite of context name +
 *                    conversation title (or empty if both absent).
 *
 * Per the B1.1 dispatch (`PART 1` Work Studio trigger lock):
 *   - NOT a model-tool-call (Phase Shield-Tools is separate).
 *   - NOT an intent classifier (the user explicitly initiates).
 *   - Receipts land in Trust Center, not in the conversation.
 *   - Zero net-new LLM calls introduced by the pre-fill mechanics.
 */
import { useEffect, useMemo, useState } from "react";
import api from "@/lib/api/apiV2";
import { apiErrorMessage } from "@/lib/api";
import { toast } from "sonner";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  FileText, Presentation, FileSpreadsheet, ClipboardList,
  Users, Building, Download, Loader2, ExternalLink, CheckCircle2,
} from "lucide-react";

const KINDS = [
  { id: "brief",          label: "Brief",          blurb: "1-2 page summary", Icon: FileText },
  { id: "deck",           label: "Deck",           blurb: "PPTX slides",      Icon: Presentation },
  { id: "report",         label: "Report",         blurb: "Long-form DOCX",   Icon: FileSpreadsheet },
  { id: "minutes",        label: "Minutes",        blurb: "Meeting record",   Icon: ClipboardList },
  { id: "committee_pack", label: "Committee Pack", blurb: "Multi-section pack", Icon: Users },
  { id: "board_pack",     label: "Board Pack",     blurb: "Board-grade pack", Icon: Building },
];

// Mechanical pre-fill helpers — pure JS, no LLM.
const _truncateChars = (s, n) => (s && s.length > n ? s.slice(0, n - 1) + "…" : s || "");

function _prefillDescription(messages, contextName) {
  // Concatenate the last 6 messages (or however many exist), with
  // role tags. Cap at 4000 chars so the modal stays readable and
  // the LLM prompt downstream isn't bloated.
  if (!messages || messages.length === 0) {
    return contextName
      ? `Discussion in context "${contextName}". (No prior turns recorded.)`
      : "(New conversation — no prior turns to summarise.)";
  }
  const tail = messages.slice(-6);
  const lines = tail.map((m) => {
    const role = (m.role || "user").toUpperCase();
    const body = (m.content || "").trim();
    return `[${role}]\n${body}`;
  });
  return _truncateChars(lines.join("\n\n"), 4000);
}

function _prefillObjective(messages) {
  // Find the last user message, then approximate the user's last
  // imperative by taking the last sentence-sized chunk. If the
  // user's last message is short (<240 chars), use it whole.
  if (!messages || messages.length === 0) return "";
  const lastUser = [...messages].reverse().find((m) => (m.role || "user") === "user");
  if (!lastUser) return "";
  const text = (lastUser.content || "").trim();
  if (text.length <= 240) return text;
  // Split on `. ! ? \n\n` boundaries; take the last meaningful chunk.
  const parts = text
    .split(/(?<=[.!?])\s+|\n\n+/)
    .map((s) => s.trim())
    .filter((s) => s.length >= 12);
  return _truncateChars((parts[parts.length - 1] || text).trim(), 600);
}

function _prefillScope(contextName, chatTitle) {
  const bits = [];
  if (contextName) bits.push(`Context: ${contextName}.`);
  if (chatTitle) bits.push(`Conversation: ${chatTitle}.`);
  return bits.join(" ");
}

export default function WorkStudioAffordanceModal({
  open, onClose, messages, contextId, contextName, chatTitle,
}) {
  const [step, setStep] = useState("pick");            // pick | review | working | done | error
  const [kind, setKind] = useState("brief");
  const [description, setDescription] = useState("");
  const [objective, setObjective] = useState("");
  const [scope, setScope] = useState("");
  const [exportId, setExportId] = useState(null);
  const [exportRow, setExportRow] = useState(null);
  const [errMsg, setErrMsg] = useState("");

  // Mechanical pre-fill — computed once on open, then user-editable.
  const preDesc = useMemo(
    () => _prefillDescription(messages, contextName),
    [messages, contextName]
  );
  const preObj = useMemo(() => _prefillObjective(messages), [messages]);
  const preScope = useMemo(
    () => _prefillScope(contextName, chatTitle),
    [contextName, chatTitle]
  );

  useEffect(() => {
    if (open) {
      setStep("pick");
      setKind("brief");
      setDescription(preDesc);
      setObjective(preObj);
      setScope(preScope);
      setExportId(null);
      setExportRow(null);
      setErrMsg("");
    }
  }, [open, preDesc, preObj, preScope]);

  // Poll the export status when working.
  useEffect(() => {
    if (step !== "working" || !exportId || !contextId) return;
    let cancelled = false;
    const tick = async () => {
      try {
        const { data } = await api.get(
          `/contexts/${contextId}/work-studio/exports/${exportId}`
        );
        if (cancelled) return;
        setExportRow(data);
        const status = data?.status;
        if (status === "complete") setStep("done");
        else if (status === "failed") {
          setErrMsg(data?.error || "Generation failed.");
          setStep("error");
        }
      } catch (e) {
        if (!cancelled) {
          setErrMsg(apiErrorMessage(e));
          setStep("error");
        }
      }
    };
    tick();
    const iv = setInterval(tick, 4000);
    return () => { cancelled = true; clearInterval(iv); };
  }, [step, exportId, contextId]);

  const canSubmit =
    !!contextId &&
    description.trim().length >= 12 &&
    objective.trim().length >= 8 &&
    scope.trim().length >= 4;

  async function onCreate() {
    if (!canSubmit) return;
    setStep("working");
    setErrMsg("");
    try {
      const { data } = await api.post(
        `/contexts/${contextId}/work-studio/export/${kind}`,
        {
          description: description.trim(),
          objective: objective.trim(),
          scope: scope.trim(),
        },
      );
      setExportId(data?.export_id || null);
      if (!data?.export_id) {
        setErrMsg("Server did not return an export_id.");
        setStep("error");
      }
    } catch (e) {
      setErrMsg(apiErrorMessage(e));
      setStep("error");
    }
  }

  async function onDownload() {
    if (!exportRow?.download_token || !contextId || !exportId) return;
    try {
      const url =
        `${api.__raw.defaults.baseURL}/contexts/${contextId}/work-studio/` +
        `exports/${exportId}/download?token=` +
        encodeURIComponent(exportRow.download_token);
      // Cookie + Authorization headers are not attached to a plain
      // window.open call; use a fetch + blob to preserve auth.
      const r = await api.__raw.get(
        `/contexts/${contextId}/work-studio/exports/${exportId}/download?token=${encodeURIComponent(exportRow.download_token)}`,
        { responseType: "blob" },
      );
      const blob = new Blob([r.data]);
      const a = document.createElement("a");
      const objectUrl = URL.createObjectURL(blob);
      a.href = objectUrl;
      a.download = exportRow.file_name || `artefact.${exportRow.output_format || "bin"}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(objectUrl);
      // Suppress lint — url is computed for parity but not used here.
      void url;
    } catch (e) {
      toast.error(apiErrorMessage(e));
    }
  }

  const noContext = !contextId;

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent
        className="bg-[var(--cream)] border-[var(--rule)] max-w-2xl"
        data-testid="chat-ws-affordance-dialog"
      >
        <DialogHeader>
          <DialogTitle className="akki-serif font-normal text-[18px]">
            Create from this conversation
          </DialogTitle>
          <DialogDescription className="text-[13px] text-[var(--deep)] leading-relaxed pt-1">
            Hand off the live discussion to Work Studio as a finished
            artefact. Pre-fill is derived mechanically from the chat —
            edit any field, then create.
          </DialogDescription>
        </DialogHeader>

        {noContext && (
          <div
            className="bg-amber-50 border border-amber-200 text-amber-900 text-[12.5px] px-3 py-2 rounded-sm"
            data-testid="chat-ws-no-context-banner"
          >
            This chat isn&apos;t tied to an organisation. Open it inside an
            organisation context to create a Work Studio artefact.
          </div>
        )}

        {(step === "pick" || step === "review") && !noContext && (
          <div className="space-y-3">
            <div>
              <p className="text-[11px] uppercase tracking-[0.08em] text-[var(--muted)] mb-1.5">
                Kind
              </p>
              <div
                className="grid grid-cols-3 gap-2"
                data-testid="chat-ws-kind-grid"
              >
                {KINDS.map(({ id, label, blurb, Icon }) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => { setKind(id); setStep("review"); }}
                    className={`text-left px-2.5 py-2 border rounded-sm transition-colors ${
                      kind === id
                        ? "border-[var(--accent)] bg-white"
                        : "border-[var(--rule)] bg-white/60 hover:bg-white"
                    }`}
                    data-testid={`chat-ws-kind-${id}`}
                  >
                    <div className="flex items-center gap-1.5 text-[13px] text-[var(--ink)]">
                      <Icon className="w-3.5 h-3.5 text-[var(--accent)]" />
                      <span>{label}</span>
                    </div>
                    <p className="text-[10.5px] text-[var(--muted)] italic mt-0.5">{blurb}</p>
                  </button>
                ))}
              </div>
            </div>

            {step === "review" && (
              <div className="space-y-2.5">
                <div>
                  <label
                    htmlFor="chat-ws-description"
                    className="text-[11px] uppercase tracking-[0.08em] text-[var(--muted)]"
                  >
                    Description (last 6 turns)
                  </label>
                  <textarea
                    id="chat-ws-description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={5}
                    maxLength={4000}
                    className="w-full mt-1 px-2 py-1.5 text-[12.5px] border border-[var(--rule)] rounded-sm bg-white focus:outline-none focus:border-[var(--accent)] resize-none akki-serif leading-relaxed"
                    data-testid="chat-ws-description"
                  />
                </div>
                <div>
                  <label
                    htmlFor="chat-ws-objective"
                    className="text-[11px] uppercase tracking-[0.08em] text-[var(--muted)]"
                  >
                    Objective (your last ask)
                  </label>
                  <textarea
                    id="chat-ws-objective"
                    value={objective}
                    onChange={(e) => setObjective(e.target.value)}
                    rows={2}
                    maxLength={800}
                    className="w-full mt-1 px-2 py-1.5 text-[12.5px] border border-[var(--rule)] rounded-sm bg-white focus:outline-none focus:border-[var(--accent)] resize-none akki-serif leading-relaxed"
                    data-testid="chat-ws-objective"
                  />
                </div>
                <div>
                  <label
                    htmlFor="chat-ws-scope"
                    className="text-[11px] uppercase tracking-[0.08em] text-[var(--muted)]"
                  >
                    Scope (audience / context)
                  </label>
                  <textarea
                    id="chat-ws-scope"
                    value={scope}
                    onChange={(e) => setScope(e.target.value)}
                    rows={2}
                    maxLength={400}
                    className="w-full mt-1 px-2 py-1.5 text-[12.5px] border border-[var(--rule)] rounded-sm bg-white focus:outline-none focus:border-[var(--accent)] resize-none akki-serif leading-relaxed"
                    data-testid="chat-ws-scope"
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {step === "working" && (
          <div
            className="flex items-center gap-3 py-6 px-3"
            data-testid="chat-ws-working"
          >
            <Loader2 className="w-5 h-5 text-[var(--accent)] animate-spin" />
            <div className="text-[13px] text-[var(--deep)]">
              Generating the {KINDS.find((k) => k.id === kind)?.label || kind}.
              This usually takes 30–90 seconds.
            </div>
          </div>
        )}

        {step === "done" && exportRow && (
          <div
            className="space-y-2.5 py-2 px-2"
            data-testid="chat-ws-done"
          >
            <div className="flex items-center gap-2 text-[13px] text-[var(--ink)]">
              <CheckCircle2 className="w-4 h-4 text-emerald-700" />
              <span>
                {KINDS.find((k) => k.id === kind)?.label || kind} ready —{" "}
                <em>{exportRow.file_name}</em>
              </span>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={onDownload}
                className="bg-[var(--accent)] hover:bg-[var(--accent)]/90 text-white rounded-sm h-8"
                data-testid="chat-ws-download-btn"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" /> Download
              </Button>
              <a
                href={`/app/work-studio?aid=${exportRow.id || exportId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[12.5px] border border-[var(--rule)] rounded-sm hover:bg-white"
                data-testid="chat-ws-open-link"
              >
                <ExternalLink className="w-3.5 h-3.5" /> Open in Work Studio
              </a>
            </div>
          </div>
        )}

        {step === "error" && (
          <div
            className="text-[13px] text-red-800 bg-red-50 border border-red-200 rounded-sm px-3 py-2"
            data-testid="chat-ws-error"
          >
            <strong>Couldn&apos;t create the artefact.</strong>{" "}
            <span className="block mt-1 text-[12px]">{errMsg}</span>
          </div>
        )}

        <DialogFooter className="gap-2">
          {step === "review" && (
            <>
              <Button
                variant="outline"
                onClick={() => setStep("pick")}
                className="rounded-sm h-8"
                data-testid="chat-ws-back-btn"
              >
                Back
              </Button>
              <Button
                onClick={onCreate}
                disabled={!canSubmit}
                className="bg-[var(--accent)] hover:bg-[var(--accent)]/90 text-white rounded-sm h-8"
                data-testid="chat-ws-create-btn"
              >
                Create
              </Button>
            </>
          )}
          {step === "pick" && (
            <Button
              variant="outline"
              onClick={onClose}
              className="rounded-sm h-8"
              data-testid="chat-ws-cancel-btn"
            >
              Cancel
            </Button>
          )}
          {(step === "working" || step === "done" || step === "error") && (
            <Button
              variant="outline"
              onClick={onClose}
              className="rounded-sm h-8"
              data-testid="chat-ws-close-btn"
            >
              Close
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
