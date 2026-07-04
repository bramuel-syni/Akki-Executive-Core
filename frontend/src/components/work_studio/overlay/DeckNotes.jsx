/**
 * JC-WS-DECK-A8-YOUR-NOTES-MVP · 2026-07-02
 *
 * Canonical spec: /app/memory/sprints/JC_WS_DECK_A8_YOUR_NOTES_MVP.md
 * Path A execution plan: JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A8.
 *
 * Private, deck-scoped notes MVP — localStorage persistence, no backend.
 * Cross-device sync is DEFERRED to the full-A8 backend engine dispatch
 * (~150+ LOC · scope-escalation candidate).
 *
 * Storage contract:
 *   Key:   akki:deck-notes:{contextId}:{artefactId}
 *   Value: JSON { content: string, updated_at: iso-8601 }
 *
 * Stories closed (MVP-level, all 10 per brief §Your Notes tab):
 *   DECK-050 Create · DECK-051 Edit · DECK-052 Delete-parts (native textarea)
 *   DECK-053 Autosave confirmation · DECK-054/055 Cross-session persistence
 *   DECK-056/057 Undo/Redo (native browser textarea) · DECK-058 Offline
 *   DECK-059 Delete entirely (Clear button).
 */
import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";

const STORAGE_KEY_PREFIX = "akki:deck-notes:";
const AUTOSAVE_DEBOUNCE_MS = 500;

/**
 * Formats a "relative time since save" indicator.
 * "Saved just now" if <5s; "Saved 12s ago" up to 60s; else "Saved at HH:MM".
 */
function formatSavedIndicator(updatedAt) {
  if (!updatedAt) return "";
  const then = new Date(updatedAt);
  if (Number.isNaN(then.getTime())) return "";
  const seconds = Math.max(0, Math.round((Date.now() - then.getTime()) / 1000));
  if (seconds < 5) return "Saved just now";
  if (seconds < 60) return `Saved ${seconds}s ago`;
  return `Saved at ${then.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function storageKey(contextId, artefactId) {
  return `${STORAGE_KEY_PREFIX}${contextId}:${artefactId}`;
}

function readNotes(contextId, artefactId) {
  if (typeof window === "undefined") return { content: "", updated_at: null };
  try {
    const raw = window.localStorage.getItem(storageKey(contextId, artefactId));
    if (!raw) return { content: "", updated_at: null };
    const parsed = JSON.parse(raw);
    return {
      content: typeof parsed.content === "string" ? parsed.content : "",
      updated_at: parsed.updated_at || null,
    };
  } catch {
    return { content: "", updated_at: null };
  }
}

function writeNotes(contextId, artefactId, content) {
  if (typeof window === "undefined") return null;
  const updated_at = new Date().toISOString();
  try {
    window.localStorage.setItem(
      storageKey(contextId, artefactId),
      JSON.stringify({ content, updated_at }),
    );
    return updated_at;
  } catch {
    return null;
  }
}

function clearNotes(contextId, artefactId) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(storageKey(contextId, artefactId));
  } catch {
    // no-op
  }
}

export default function DeckNotes({ contextId, artefactId }) {
  const initial = readNotes(contextId, artefactId);
  const [content, setContent] = useState(initial.content);
  const [savedAt, setSavedAt] = useState(initial.updated_at);
  const [confirmClearOpen, setConfirmClearOpen] = useState(false);
  const [savedIndicator, setSavedIndicator] = useState(formatSavedIndicator(initial.updated_at));
  const debounceRef = useRef(null);
  const tickRef = useRef(null);

  // Reload notes when the deck changes (artefactId/contextId swap without unmount).
  useEffect(() => {
    const next = readNotes(contextId, artefactId);
    setContent(next.content);
    setSavedAt(next.updated_at);
    setSavedIndicator(formatSavedIndicator(next.updated_at));
  }, [contextId, artefactId]);

  // Debounced autosave — writes 500ms after last keystroke.
  const scheduleSave = useCallback((nextContent) => {
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(() => {
      const stamp = writeNotes(contextId, artefactId, nextContent);
      if (stamp) {
        setSavedAt(stamp);
        setSavedIndicator(formatSavedIndicator(stamp));
      }
    }, AUTOSAVE_DEBOUNCE_MS);
  }, [contextId, artefactId]);

  const handleChange = (e) => {
    const next = e.target.value;
    setContent(next);
    scheduleSave(next);
  };

  // Refresh the "Saved Xs ago" indicator every 10s.
  useEffect(() => {
    if (!savedAt) return () => {};
    if (tickRef.current) window.clearInterval(tickRef.current);
    tickRef.current = window.setInterval(() => {
      setSavedIndicator(formatSavedIndicator(savedAt));
    }, 10000);
    return () => {
      if (tickRef.current) window.clearInterval(tickRef.current);
    };
  }, [savedAt]);

  const handleClearConfirmed = () => {
    clearNotes(contextId, artefactId);
    setContent("");
    setSavedAt(null);
    setSavedIndicator("");
    setConfirmClearOpen(false);
  };

  const isEmpty = !content;

  return (
    <div className="mx-4 my-4" data-testid="deck-notes-root">
      <div className="flex items-center justify-between mb-2">
        <div className="text-[13px] text-[var(--muted)]">
          Private notes — persisted on this device only.
        </div>
        <div className="flex items-center gap-3">
          {savedIndicator && (
            <span
              className="text-[11px] text-[var(--muted)] italic"
              data-testid="deck-notes-saved-indicator"
            >
              {savedIndicator}
            </span>
          )}
          <button
            type="button"
            className="text-[11px] text-[var(--muted)] hover:text-[var(--oxblood)] disabled:opacity-40"
            disabled={isEmpty}
            onClick={() => setConfirmClearOpen(true)}
            data-testid="deck-notes-clear-button"
          >
            Clear notes
          </button>
        </div>
      </div>

      <textarea
        value={content}
        onChange={handleChange}
        placeholder="Write your private notes about this deck. Ctrl+Z / Ctrl+Y for undo / redo. Autosaves as you type — nothing leaves this browser."
        className="w-full min-h-[400px] p-3 border border-[var(--rule)] rounded-md bg-[var(--parchment)] text-[13px] leading-relaxed font-mono resize-y focus:outline-none focus:border-[var(--oxblood)]"
        data-testid="deck-notes-textarea"
      />

      {isEmpty && (
        <div
          className="text-[11px] text-[var(--muted)] italic mt-2"
          data-testid="deck-notes-empty-state"
        >
          No notes yet. Notes are private to you and stay on this device.
        </div>
      )}

      <Dialog open={confirmClearOpen} onOpenChange={setConfirmClearOpen}>
        <DialogContent data-testid="deck-notes-clear-confirm">
          <DialogHeader>
            <DialogTitle>Clear all notes?</DialogTitle>
          </DialogHeader>
          <p className="text-[13px] text-[var(--muted)]">
            This removes the deck-scoped notes from this browser. This cannot be undone.
          </p>
          <DialogFooter>
            <button
              type="button"
              className="px-3 py-1 text-[12px] border border-[var(--rule)] rounded"
              onClick={() => setConfirmClearOpen(false)}
              data-testid="deck-notes-clear-cancel"
            >
              Cancel
            </button>
            <button
              type="button"
              className="px-3 py-1 text-[12px] bg-[var(--oxblood)] text-white rounded"
              onClick={handleClearConfirmed}
              data-testid="deck-notes-clear-confirm-button"
            >
              Clear notes
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
