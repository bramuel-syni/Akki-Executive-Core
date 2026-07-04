/**
 * JC-WS-DECK-A8-BACKEND-PERSISTENCE · 2026-07-02
 *
 * Canonical spec: /app/memory/rules/TAB_HONESTY_RULE.md
 *              + /app/memory/sprints/JC_WS_DECK_A8_BACKEND_PERSISTENCE.md
 *
 * TAB HONESTY RULE enforcement — upgrades A8 Your Notes from
 * localStorage MVP to account-persisted CRUD via /api/deck-notes/{doc_id}.
 * F.6 discipline-pay: N/A · user-authored content, no LLM path.
 *
 * Storage contract:
 *   GET    /api/deck-notes/{document_id}  → {content, updated_at} or 404
 *   PUT    /api/deck-notes/{document_id}  → upsert; body {content}
 *   DELETE /api/deck-notes/{document_id}  → 204
 *
 * One-way import from localStorage on first load (no user data stranded):
 *   1. On mount, GET the note for this doc.
 *   2. If GET 404 AND localStorage has legacy content → PUT to backend.
 *   3. On successful PUT, localStorage.removeItem for that key.
 *   4. If backend GET 200 → IGNORE localStorage entirely (never re-import).
 *   5. On import PUT failure → keep localStorage, retry next mount.
 */
import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import api from "@/lib/api/apiV2";

const LEGACY_STORAGE_KEY_PREFIX = "akki:deck-notes:";
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

function legacyStorageKey(contextId, artefactId) {
  return `${LEGACY_STORAGE_KEY_PREFIX}${contextId}:${artefactId}`;
}

/**
 * Read legacy localStorage content (for one-way import from A8 MVP).
 * Returns null if no legacy content exists.
 */
function readLegacyLocalStorage(contextId, artefactId) {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(legacyStorageKey(contextId, artefactId));
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    const content = typeof parsed.content === "string" ? parsed.content : "";
    return content ? content : null;
  } catch {
    return null;
  }
}

function clearLegacyLocalStorage(contextId, artefactId) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(legacyStorageKey(contextId, artefactId));
  } catch {
    // no-op
  }
}

export default function DeckNotes({ contextId, artefactId }) {
  const [content, setContent] = useState("");
  const [savedAt, setSavedAt] = useState(null);
  const [confirmClearOpen, setConfirmClearOpen] = useState(false);
  const [savedIndicator, setSavedIndicator] = useState("");
  const [loaded, setLoaded] = useState(false);
  const debounceRef = useRef(null);
  const tickRef = useRef(null);
  const importedRef = useRef(false);

  // Load backend notes on mount / doc-change. One-way import from
  // localStorage if backend is empty and legacy content exists.
  useEffect(() => {
    let cancelled = false;
    setLoaded(false);
    (async () => {
      try {
        const resp = await api.get(`/deck-notes/${artefactId}`);
        if (cancelled) return;
        const nextContent = (resp && resp.data && typeof resp.data.content === "string") ? resp.data.content : "";
        const nextUpdatedAt = (resp && resp.data && resp.data.updated_at) || null;
        setContent(nextContent);
        setSavedAt(nextUpdatedAt);
        setSavedIndicator(formatSavedIndicator(nextUpdatedAt));
        setLoaded(true);
        // Backend has content — ignore localStorage entirely (never re-import).
      } catch (err) {
        // If backend GET returns 404, check legacy localStorage for one-way import.
        const is404 = err && err.response && err.response.status === 404;
        if (!is404) {
          setLoaded(true);
          return;
        }
        const legacyContent = readLegacyLocalStorage(contextId, artefactId);
        if (!legacyContent || importedRef.current) {
          if (cancelled) return;
          setContent("");
          setSavedAt(null);
          setSavedIndicator("");
          setLoaded(true);
          return;
        }
        // One-way import — PUT legacy content to backend, then clear localStorage.
        try {
          importedRef.current = true;
          const importResp = await api.put(`/deck-notes/${artefactId}`, { content: legacyContent });
          if (cancelled) return;
          const importedContent = (importResp && importResp.data && typeof importResp.data.content === "string") ? importResp.data.content : legacyContent;
          const importedUpdatedAt = (importResp && importResp.data && importResp.data.updated_at) || null;
          setContent(importedContent);
          setSavedAt(importedUpdatedAt);
          setSavedIndicator(formatSavedIndicator(importedUpdatedAt));
          setLoaded(true);
          // Only clear localStorage on successful PUT — never strand user data.
          clearLegacyLocalStorage(contextId, artefactId);
          // Telemetry hook (swap for real telemetry when Pulse feed available).
          try { console.log("deck_notes.localstorage_migration.completed", { artefactId }); } catch { /* no-op */ }
        } catch (putErr) {
          // Import PUT failed — keep localStorage, present legacy content in UI.
          if (cancelled) return;
          importedRef.current = false;
          setContent(legacyContent);
          setSavedAt(null);
          setSavedIndicator("");
          setLoaded(true);
        }
      }
    })();
    return () => { cancelled = true; };
  }, [contextId, artefactId]);

  // Debounced autosave — PUT 500ms after last keystroke.
  const scheduleSave = useCallback((nextContent) => {
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(async () => {
      try {
        const resp = await api.put(`/deck-notes/${artefactId}`, { content: nextContent });
        const stamp = (resp && resp.data && resp.data.updated_at) || null;
        if (stamp) {
          setSavedAt(stamp);
          setSavedIndicator(formatSavedIndicator(stamp));
        }
      } catch {
        // Silent — user keeps their in-memory state; next save attempt retries.
      }
    }, AUTOSAVE_DEBOUNCE_MS);
  }, [artefactId]);

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

  const handleClearConfirmed = async () => {
    try {
      await api.delete(`/deck-notes/${artefactId}`);
    } catch {
      // Silent — even if delete fails, clear UI state locally.
    }
    setContent("");
    setSavedAt(null);
    setSavedIndicator("");
    setConfirmClearOpen(false);
    // Best-effort — also clear any lingering legacy localStorage under this key.
    clearLegacyLocalStorage(contextId, artefactId);
  };

  const isEmpty = !content;

  return (
    <div className="mx-4 my-4" data-testid="deck-notes-root">
      <div className="flex items-center justify-between mb-2">
        <div className="text-[13px] text-[var(--muted)]">
          Private notes — synced to your account.
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
            disabled={isEmpty || !loaded}
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
        placeholder="Write your private notes about this deck. Ctrl+Z / Ctrl+Y for undo / redo. Autosaves as you type — syncs to your account."
        className="w-full min-h-[400px] p-3 border border-[var(--rule)] rounded-md bg-[var(--parchment)] text-[13px] leading-relaxed font-mono resize-y focus:outline-none focus:border-[var(--oxblood)]"
        data-testid="deck-notes-textarea"
        disabled={!loaded}
      />

      {isEmpty && loaded && (
        <div
          className="text-[11px] text-[var(--muted)] italic mt-2"
          data-testid="deck-notes-empty-state"
        >
          No notes yet. Notes are private to your account and sync across your devices.
        </div>
      )}

      <Dialog open={confirmClearOpen} onOpenChange={setConfirmClearOpen}>
        <DialogContent data-testid="deck-notes-clear-confirm">
          <DialogHeader>
            <DialogTitle>Clear all notes?</DialogTitle>
          </DialogHeader>
          <p className="text-[13px] text-[var(--muted)]">
            This removes the deck-scoped notes from your account. This cannot be undone.
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
