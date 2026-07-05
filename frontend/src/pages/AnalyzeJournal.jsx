/**
 * AnalyzeJournal — Track A Phase 2 (2026-06-04).
 *
 * Mirrors DocumentsPage shell: a clean listing of the user's
 * Analyses with `?aid=<id>` URL contract for drawer-open.
 *
 * Opened at `/app/analyze`. The legacy flat surface at
 * `/app/work-studio/analyze` redirects to this route (App.js).
 */
import React, { useEffect, useState, useCallback, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import AppShell from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import api from "@/lib/api/apiV2";
import { apiErrorMessage } from "@/lib/api";
import { toast } from "sonner";
import AnalyzeDrawer from "@/components/analyze/AnalyzeDrawer";
import { Loader2, Plus, UploadCloud } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

function fmtRel(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    const diffH = (Date.now() - d.getTime()) / 36e5;
    if (diffH < 1) return `${Math.max(1, Math.round(diffH * 60))} min ago`;
    if (diffH < 24) return `${Math.round(diffH)}h ago`;
    return d.toLocaleDateString();
  } catch { return "—"; }
}

// ─────────────────────────────────────────────────────────────
// JC-STORAGE-STAGE-1B-CEILING-AND-RESUMABLE (2026-07-02)
// Chunked resumable PUT to a GCS session URI, with commit-state
// query on network drop so uploads resume from the last committed
// byte rather than restart from zero. See:
//   https://cloud.google.com/storage/docs/performing-resumable-uploads
// ─────────────────────────────────────────────────────────────
async function putFileViaResumableSession({
  file, sessionUri, contentType, chunkBytes, onProgress, maxRetriesPerChunk = 3,
}) {
  const total = file.size;
  let offset = 0;

  const queryCommittedOffset = async () => {
    // Zero-length PUT with `Content-Range: bytes */TOTAL` asks GCS
    // to report the highest committed byte via the Range response
    // header. GCS returns 308 Resume Incomplete on partial upload
    // or 200/201 on completion. We interpret Range: bytes=0-N and
    // resume from N+1.
    // eslint-disable-next-line no-restricted-syntax -- GCS resumable-upload session URI (not app backend); api client's Bearer/CSRF/X-Active-Context interceptors would conflict with GCS's signed-URL auth
    const resp = await fetch(sessionUri, {
      method: "PUT",
      headers: { "Content-Range": `bytes */${total}` },
    });
    if (resp.status === 200 || resp.status === 201) {
      return total;   // fully uploaded already
    }
    if (resp.status !== 308) {
      throw new Error(`resumable state-query status=${resp.status}`);
    }
    const rangeHeader = resp.headers.get("Range");
    if (!rangeHeader) return 0;   // nothing committed yet
    const m = rangeHeader.match(/bytes=0-(\d+)/);
    if (!m) return 0;
    return parseInt(m[1], 10) + 1;
  };

  while (offset < total) {
    const end = Math.min(offset + chunkBytes, total) - 1;
    const chunk = file.slice(offset, end + 1);

    let attempt = 0;
    let uploaded = false;
    let lastError = null;
    while (attempt < maxRetriesPerChunk && !uploaded) {
      attempt += 1;
      try {
        // Per GCS resumable-upload contract: single-chunk PUTs must
        // carry `Content-Range: bytes START-END/TOTAL`. On success
        // GCS returns 308 (partial) or 200/201 (final chunk).
        // eslint-disable-next-line no-restricted-syntax -- GCS resumable-upload session URI (not app backend); api client's Bearer/CSRF/X-Active-Context interceptors would conflict with GCS's signed-URL auth
        const resp = await fetch(sessionUri, {
          method: "PUT",
          headers: {
            "Content-Type": contentType,
            "Content-Range": `bytes ${offset}-${end}/${total}`,
          },
          body: chunk,
        });
        if (resp.status === 200 || resp.status === 201 || resp.status === 308) {
          uploaded = true;
          offset = end + 1;
          if (typeof onProgress === "function") onProgress(offset, total);
        } else {
          lastError = new Error(`chunk PUT status=${resp.status}`);
        }
      } catch (netErr) {
        lastError = netErr;
      }
      if (!uploaded && attempt < maxRetriesPerChunk) {
        // Query commit state — the chunk may have partially landed
        // even on a network drop; resume from GCS's authoritative
        // last-committed byte.
        try {
          const committed = await queryCommittedOffset();
          if (committed > offset) {
            offset = committed;
            uploaded = true;
            if (typeof onProgress === "function") onProgress(offset, total);
          }
        } catch (queryErr) {
          // fall through to next attempt
        }
      }
    }
    if (!uploaded) {
      throw lastError || new Error("chunk upload failed after retries");
    }
  }
}

export default function AnalyzeJournal() {
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const aid = params.get("aid");
  // BUG-ANL-001 (2026-06-04, user pick = option a) — route guard.
  // The Analyze Journal page silently rendered when no context_id
  // was available; the user could see the upload form but the
  // POST /workbook/upload-multi would 400 with `context_id_required`.
  // We now redirect on mount if no context is selected: to the
  // user's default context if known, or to /app/home with an
  // informational toast if not.
  const auth = useAuth();
  const activeContextId = auth?.activeContextId || null;
  const defaultContextId = auth?.account?.default_context_id || null;
  const authReady = auth?.account !== undefined;  // AuthContext sets account after /auth/me lands
  const urlCtx = params.get("context_id") || null;
  const effectiveContextId = urlCtx || activeContextId || defaultContextId || null;

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [objective, setObjective] = useState("");
  const fileInput = useRef(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/workbook/v2/analyses");
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      toast.error(apiErrorMessage(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // BUG-ANL-001 — mount-time route guard.
  // Runs once the AuthContext is hydrated. If we have a default
  // context but the URL is missing context_id, we backfill the URL
  // via setParams(replace=true) so future calls (upload, etc.)
  // can read it off the query string. If there's no default
  // context, we bounce to /app/home with a polite picker prompt.
  // The original `context_id_required` toast from any background
  // call is suppressed by the redirect happening BEFORE the user
  // can trigger an upload.
  useEffect(() => {
    if (!authReady) return;
    if (urlCtx) return;            // URL already carries it — nothing to do
    if (defaultContextId || activeContextId) {
      const next = new URLSearchParams(params);
      next.set("context_id", defaultContextId || activeContextId);
      setParams(next, { replace: true });
      return;
    }
    // No context anywhere — bounce to /app/home with a picker prompt.
    toast.info("Pick a context to view your Analyze Journal.");
    navigate("/app/home", { replace: true });
  }, [authReady, urlCtx, defaultContextId, activeContextId, params, setParams, navigate]);

  // Re-load whenever the drawer closes so the listing reflects new
  // notes / objective edits.
  useEffect(() => {
    if (!aid) load();
  }, [aid, load]);

  const openDrawer = (id) => {
    const next = new URLSearchParams(params);
    next.set("aid", id);
    setParams(next, { replace: false });
  };

  const closeDrawer = () => {
    const next = new URLSearchParams(params);
    next.delete("aid");
    setParams(next, { replace: false });
  };

  const onCreate = async (filesList) => {
    if (!filesList || filesList.length === 0) return;
    if (!effectiveContextId) {
      // The mount guard should have redirected before this point;
      // belt-and-braces in case the user navigates to the page
      // and clicks Upload before the guard's useEffect runs.
      toast.info("Pick a context first to upload an analysis.");
      navigate("/app/home", { replace: true });
      return;
    }
    setCreating(true);
    try {
      // JC-STORAGE-STAGE-1B-CEILING-AND-RESUMABLE (2026-07-02) — 2-tier
      // size-branched routing (resumable-default above the 16 MB gate;
      // 100 MB intermediate tier from the compaction-dropped mid-flight
      // amendment is DISCARDED per user directive):
      //   ≤16 MB  → existing GridFS in-band multipart route (unchanged)
      //   16MB<size≤500MB → GCS resumable upload session (chunked PUT
      //                     with `Content-Range: bytes X-Y/total`;
      //                     8 MiB chunks; retry-on-drop via commit-state
      //                     query on the session URI)
      //   >500 MB → server-side 413 ceiling_exceeded (we surface early
      //             from this FE for a tidy UX)
      // The FE routes at file-selection time; we NEVER mix large files
      // into the multipart body (ingress would 413 the whole request).
      const IN_BAND_BYTES  = 16  * 1024 * 1024;
      const MAX_BYTES      = 500 * 1024 * 1024;
      const CHUNK_BYTES    = 8   * 1024 * 1024;   // 8 MiB · GCS-recommended
      const smallFiles = [];
      const largeFiles = [];
      for (const f of filesList) {
        const sz = f?.size || 0;
        if (sz > MAX_BYTES) {
          toast.error(`${f.name} exceeds 500 MB upload ceiling`);
          continue;
        }
        if (sz <= IN_BAND_BYTES) smallFiles.push(f);
        else                     largeFiles.push(f);
      }

      let lastCreatedId = null;

      // Path B — small files via existing in-band multipart route.
      if (smallFiles.length > 0) {
        const fd = new FormData();
        for (const f of smallFiles) fd.append("files", f);
        if (objective.trim()) fd.append("objective", objective.trim());
        // BUG-ANL-001 — thread context_id into the FormData so the
        // backend at /workbook/upload-multi:660-665 doesn't fall back
        // to `active_context_id` (which may also be empty on a fresh
        // session). Explicit > implicit.
        fd.append("context_id", effectiveContextId);
        const { data } = await api.post("/workbook/upload-multi", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        lastCreatedId = data?.id || null;
      }

      // Path A — >16 MB via GCS resumable session (chunked PUT).
      for (const f of largeFiles) {
        // Ask backend for a resumable session URI. Backend enforces
        // the 500 MB ceiling and the ≤16 MB use-in-band gate — this FE
        // only pre-screens to keep the UX tight; the server is truth.
        const { data: pre } = await api.post("/uploads/presigned", {
          filename: f.name,
          content_type: f.type || "application/octet-stream",
          size_bytes: f.size,
          context_id: effectiveContextId,
          kind: "workbook",
          origin: window.location.origin,
        });
        // pre.method === "RESUMABLE" · pre.upload_session_uri holds the URI.
        await putFileViaResumableSession({
          file: f,
          sessionUri: pre.upload_session_uri,
          contentType: pre.content_type,
          chunkBytes: CHUNK_BYTES,
          onProgress: (loaded, total) => {
            // Non-blocking progress surface; upgrade to a progress bar
            // component in a follow-up. Kept in console for now.
            // eslint-disable-next-line no-console
            console.log(`[resumable] ${f.name} · ${Math.round((loaded/total)*100)}%`);
          },
        });
        const { data: done } = await api.post("/uploads/complete", {
          gcs_object_name: pre.gcs_object_name,
          filename: f.name,
          context_id: effectiveContextId,
          kind: "workbook",
          size_bytes: f.size,
          objective: objective.trim() || undefined,
        });
        lastCreatedId = done?.id || lastCreatedId;
      }

      const parts = [
        smallFiles.length ? `${smallFiles.length} small`  : null,
        largeFiles.length ? `${largeFiles.length} large`  : null,
      ].filter(Boolean).join(" + ");
      toast.success(`Analysis created (${parts || filesList.length + " files"})`);
      setObjective("");
      await load();
      if (lastCreatedId) openDrawer(lastCreatedId);
    } catch (e) {
      toast.error(apiErrorMessage(e));
    } finally {
      setCreating(false);
      // BUG-ANL-002 (2026-06-04) — ALWAYS clear input.value after an
      // upload attempt, success OR failure. Pre-fix the clear lived
      // inside the success branch only, so a failed upload left the
      // input holding the picked filename. The next OS-picker
      // selection of the SAME file would not fire `onChange` (the
      // canonical HTML quirk — input.value unchanged → no event) →
      // silent failure. Moving the clear to `finally` guarantees
      // every retry starts from a clean value, so re-picking the
      // same file always re-triggers the upload.
      if (fileInput.current) fileInput.current.value = "";
    }
  };

  return (
    <AppShell>
      <div className="max-w-5xl mx-auto px-6 py-8" data-testid="analyze-journal-page">
        <header className="mb-8 flex items-baseline justify-between">
          <div>
            <h1 className="text-[24px] text-[var(--ink)]">Analyze Journal</h1>
            <p className="text-[13px] text-[var(--muted)] mt-1">
              Every analysis you've run, plus the context you captured at the time.
            </p>
          </div>
        </header>

        {/* New analysis — objective + file picker */}
        <section className="border border-[var(--rule)] rounded-sm p-5 bg-white mb-8" data-testid="analyze-journal-new">
          <p className="text-[11px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] mb-2">
            New analysis
          </p>
          <input
            type="text"
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            placeholder="What are you trying to learn? (optional)"
            className="w-full text-[13.5px] bg-[var(--cream-deep)]/30 border border-[var(--rule)] rounded-sm px-3 py-2 mb-3 outline-none focus:border-[var(--ink)]"
            data-testid="analyze-journal-objective"
          />
          <div className="flex items-center gap-2">
            <input
              ref={fileInput}
              type="file"
              accept=".xlsx,.csv"
              multiple
              onChange={(e) => onCreate(e.target.files)}
              className="hidden"
              data-testid="analyze-journal-file-input"
            />
            <Button
              onClick={() => fileInput.current?.click()}
              disabled={creating}
              data-testid="analyze-journal-upload-btn"
            >
              {creating ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Uploading…</>
              ) : (
                <><UploadCloud className="w-4 h-4 mr-2" /> Upload files (.xlsx / .csv)</>
              )}
            </Button>
            <p className="text-[11px] text-[var(--muted)]">
              Multiple files supported · up to 250 MB each
            </p>
          </div>
        </section>

        {/* Listing */}
        <section data-testid="analyze-journal-list">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-5 h-5 animate-spin text-[var(--muted)]" />
            </div>
          ) : rows.length === 0 ? (
            <div
              className="border border-dashed border-[var(--rule)] rounded-sm p-10 text-center bg-white"
              data-testid="analyze-journal-empty"
            >
              <p className="text-[14px] text-[var(--ink)]">No analyses yet.</p>
              <p className="text-[12.5px] text-[var(--muted)] mt-1">
                Upload one or more spreadsheets to begin.
              </p>
            </div>
          ) : (
            <ul className="divide-y divide-[var(--rule)] border-t border-b border-[var(--rule)]">
              {rows.map((r) => (
                <li
                  key={r.id}
                  className="py-4 cursor-pointer hover:bg-[var(--cream-deep)]/40 px-3 transition-colors"
                  onClick={() => openDrawer(r.id)}
                  data-testid={`analyze-journal-row-${r.id}`}
                >
                  <div className="flex items-baseline justify-between gap-3">
                    <p className="text-[14px] text-[var(--ink)] truncate">{r.title}</p>
                    <span className="text-[10px] uppercase tracking-[0.14em] font-mono text-[var(--muted)] shrink-0">
                      {r.status}
                    </span>
                  </div>
                  <p className="text-[12px] text-[var(--muted)] mt-0.5">
                    {r.source_count} source{r.source_count === 1 ? "" : "s"}
                    {" · "}{r.note_count} note{r.note_count === 1 ? "" : "s"}
                    {" · "}updated {fmtRel(r.updated_at)}
                  </p>
                  {r.objective && (
                    <p className="text-[12.5px] text-[var(--ink)] mt-1 italic line-clamp-2">
                      "{r.objective}"
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <AnalyzeDrawer aid={aid} onClose={closeDrawer} />
    </AppShell>
  );
}
