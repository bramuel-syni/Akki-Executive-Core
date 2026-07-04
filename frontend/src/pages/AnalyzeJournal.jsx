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
      // JC-STORAGE-PIVOT-GCS-BUILD (2026-07-02) — 3-tier size-branched
      // routing (amended in-flight 2026-07-02 per Truth-in-capability
      // discipline + STORAGE_MAX_UPLOAD_MB=500 ceiling):
      //   ≤16 MB   → existing GridFS in-band multipart route (unchanged)
      //   16-100MB → single-PUT V4 presigned URL (60 min TTL)
      //   >100 MB  → GCS resumable upload session (session URI valid ~1 week;
      //              browser PUTs full body or chunks with Content-Range)
      //   >500 MB  → ceiling enforcement — presigned/resumable endpoints
      //              reject with 413 before this FE code runs.
      // The FE routes at file-selection time; we NEVER mix large files
      // into the multipart body (ingress would 413 the whole request).
      const IN_BAND_BYTES   = 16  * 1024 * 1024;
      const RESUMABLE_BYTES = 100 * 1024 * 1024;
      const MAX_BYTES       = 500 * 1024 * 1024;
      const smallFiles = [];
      const singlePutFiles = [];
      const resumableFiles = [];
      for (const f of filesList) {
        const sz = f?.size || 0;
        if (sz > MAX_BYTES) {
          toast.error(`${f.name} exceeds 500 MB upload ceiling`);
          continue;
        }
        if (sz <= IN_BAND_BYTES) smallFiles.push(f);
        else if (sz <= RESUMABLE_BYTES) singlePutFiles.push(f);
        else resumableFiles.push(f);
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

      // Path A — 16-100 MB via presigned direct-to-GCS PUT + complete.
      for (const f of singlePutFiles) {
        const { data: pre } = await api.post("/uploads/presigned", {
          filename: f.name,
          content_type: f.type || "application/octet-stream",
          size_bytes: f.size,
          context_id: effectiveContextId,
          kind: "workbook",
        });
        // Browser-direct PUT to GCS — bypasses k8s ingress entirely.
        const putResp = await fetch(pre.upload_url, {
          method: "PUT",
          headers: { "Content-Type": pre.content_type },
          body: f,
        });
        if (!putResp.ok) {
          throw new Error(`GCS PUT failed (${putResp.status}) for ${f.name}`);
        }
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

      // Path A' — >100 MB via GCS resumable upload session.
      // Session URI is single-body (entire file in one PUT) — chunked
      // resume is a follow-up nice-to-have; the resumable URI *itself*
      // gives us the ability to retry the PUT on network drop without
      // re-signing.
      for (const f of resumableFiles) {
        const { data: sess } = await api.post("/uploads/resumable-session", {
          filename: f.name,
          content_type: f.type || "application/octet-stream",
          size_bytes: f.size,
          context_id: effectiveContextId,
          kind: "workbook",
          origin: window.location.origin,
        });
        // XHR (not fetch) for upload-progress reporting — fetch API
        // has no `xhr.upload.onprogress` equivalent as of writing.
        await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open("PUT", sess.session_uri, true);
          xhr.setRequestHeader("Content-Type", sess.content_type);
          xhr.upload.onprogress = (ev) => {
            if (ev.lengthComputable) {
              const pct = Math.round((ev.loaded / ev.total) * 100);
              // Progress surfaced via toast; upgrade to a proper
              // progress bar in a follow-up. Non-blocking.
              // eslint-disable-next-line no-console
              console.log(`[resumable] ${f.name} · ${pct}%`);
            }
          };
          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) resolve();
            else reject(new Error(`resumable PUT status=${xhr.status}`));
          };
          xhr.onerror = () => reject(new Error("resumable PUT network error"));
          xhr.send(f);
        });
        const { data: done } = await api.post("/uploads/complete", {
          gcs_object_name: sess.gcs_object_name,
          filename: f.name,
          context_id: effectiveContextId,
          kind: "workbook",
          size_bytes: f.size,
          objective: objective.trim() || undefined,
        });
        lastCreatedId = done?.id || lastCreatedId;
      }

      const parts = [
        smallFiles.length      ? `${smallFiles.length} small`    : null,
        singlePutFiles.length  ? `${singlePutFiles.length} large` : null,
        resumableFiles.length  ? `${resumableFiles.length} XL`    : null,
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
