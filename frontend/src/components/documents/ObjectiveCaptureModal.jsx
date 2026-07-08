/**
 * ObjectiveCaptureModal — Phase E.3 (2026-05-26).
 *
 * JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1 (2026-07-08) — Draft Creation
 * Pipeline fix per UX Brief v1.0 §4.2. Modal now has TWO required fields:
 *   1. Title — the name of the document (v1.0 spec addition; was missing)
 *   2. Goal  — a plain-language statement of the document's purpose
 * Plus optional Context. Title carries through to the drawer header on save
 * (DB-018/029/030 · modal-title → drawer-header transition).
 *
 * Fires when the user creates a new Draft via the Drafts tab's
 * "+ New draft" CTA. Save-and-Start-Drafting label per v1.0 §4.2.
 *
 * Inputs: open, onOpenChange, onSave({title, goal, context}).
 */
import React, { useState } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";


export default function ObjectiveCaptureModal({ open, onOpenChange, onSave }) {
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("");
  const [context, setContext] = useState("");
  const [saving, setSaving] = useState(false);

  const onSubmit = async () => {
    if (!title.trim() || !goal.trim()) return;
    setSaving(true);
    try {
      // JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1 · title threaded to onSave
      // so it lands as `documents.name` on the create call (DB-018).
      await onSave({ title: title.trim(), goal: goal.trim(), context: context.trim() });
      // Clear + close on success.
      setTitle("");
      setGoal("");
      setContext("");
      onOpenChange(false);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md" data-testid="objective-capture-modal">
        <DialogHeader>
          <DialogTitle className="text-[15px]">Create a new draft</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          {/* v1.0 §4.2 · Title is a REQUIRED field per spec. */}
          <div>
            <p className="text-[11px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] mb-1.5">Title <span className="text-[var(--muted)]">(required)</span></p>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Give this draft a name…"
              autoFocus
              maxLength={300}
              className="w-full border border-[var(--rule)] rounded-sm px-2 py-1.5 text-[13px] focus:outline-none focus:border-[var(--ink)]"
              data-testid="objective-modal-title-input"
            />
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] mb-1.5">Goal <span className="text-[var(--muted)]">(required)</span></p>
            <input
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="What this draft is trying to do…"
              className="w-full border border-[var(--rule)] rounded-sm px-2 py-1.5 text-[13px] focus:outline-none focus:border-[var(--ink)]"
              data-testid="objective-modal-goal-input"
            />
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] mb-1.5">Context (optional)</p>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              rows={3}
              placeholder="Anything Akki should keep in mind while you draft…"
              className="w-full border border-[var(--rule)] rounded-sm px-2 py-1.5 text-[12.5px] focus:outline-none focus:border-[var(--ink)]"
              data-testid="objective-modal-context-input"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} size="sm" data-testid="objective-modal-cancel">Cancel</Button>
          <Button
            onClick={onSubmit}
            disabled={!title.trim() || !goal.trim() || saving}
            size="sm"
            data-testid="objective-modal-save"
          >
            {saving ? <Loader2 className="w-3 h-3 animate-spin mr-1.5" /> : null}
            Save and Start Drafting
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
