/**
 * CreateArtefactModal — Patch 2B.1 (initial scaffold) + Chunk 5
 * (2026-05-13) systemic fix + JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE
 * (2026-07-02) multi-select + alpha-sort + in-modal upload.
 *
 * The Decks and Reports tabs each expose a "Create …" action chip in
 * Work Studio. This modal asks for a title, a creation source, and
 * (when the source needs it) a pointer to the brief(s) or document(s)
 * the draft is composed against. It then posts to the unified
 *   POST /api/contexts/{cid}/work-studio/artefacts
 * endpoint, which inserts a draft row in `db.decks` / `db.reports`
 * and returns a `redirect_url` pointing at the block composer.
 *
 * Three sources are supported per kind (deck × report = 6 paths total):
 *
 *   • blank              — empty body, user composes from scratch
 *   • brief              — references one or more Work Studio briefs
 *                          (stripped of the `briefing::` aggregate
 *                          prefix before sending)
 *   • external_document  — references one or more documents already
 *                          uploaded to this workspace (checkbox list)
 *
 * A2 amendments (2026-07-02):
 *   - DECK-017 · alpha-sort briefs by name (localeCompare).
 *   - DECK-018 · multi-select briefs — checkbox list; payload sends
 *                `source_brief_ids: string[]`.
 *   - DECK-020 · alpha-sort documents by name.
 *   - DECK-021 · in-modal "+ Upload new document" button that opens
 *                the existing UploadModal on top; on `onUploaded`
 *                the doc list refetches + newly-uploaded doc is
 *                auto-selected.
 *   - DECK-022 · multi-select documents — checkbox list; payload
 *                sends `source_document_ids: string[]`.
 */
import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "@/lib/api/apiV2";
import { apiErrorMessage } from "@/lib/api";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from "@/components/ui/dialog";
import { Loader2, Upload } from "lucide-react";
import UploadModal from "@/components/upload/UploadModal";


const KIND_LABEL = {
  deck:   { title: "Create a new deck",   submit: "Create deck",   noun: "deck" },
  report: { title: "Create a new report", submit: "Create report", noun: "report" },
};

// The aggregates listing emits compound ids like `briefing::<uuid>`.
// The backend tolerates either form for defence-in-depth, but we
// strip here too so audit logs and ids in flight stay clean.
function stripAggPrefix(raw, expectedPrefix) {
  if (!raw || typeof raw !== "string") return "";
  const idx = raw.indexOf("::");
  if (idx < 0) return raw;
  const prefix = raw.slice(0, idx);
  if (prefix === expectedPrefix) return raw.slice(idx + 2);
  return raw;
}

// JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-017 +
// DECK-020 alpha-sort. Pulled out so both effects use the exact same
// comparator + collation locale.
function sortByNameAlpha(items) {
  return [...(items || [])].sort((a, b) => {
    const an = (a?.name || "").toString();
    const bn = (b?.name || "").toString();
    return an.localeCompare(bn, undefined, { sensitivity: "base" });
  });
}


export default function CreateArtefactModal({ open, onClose, kind, contextId, onCreated }) {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [source, setSource] = useState("blank");
  const [briefs, setBriefs] = useState([]);
  // JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-018 +
  // DECK-022 multi-select. Single-id state replaced with sets that
  // hold selected ids. Serialised to arrays in the submit payload.
  const [selectedBriefIds, setSelectedBriefIds] = useState(() => new Set());
  const [documents, setDocuments] = useState([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState(() => new Set());
  const [briefsLoading, setBriefsLoading] = useState(false);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  // JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-021
  // in-modal upload. Opens the existing UploadModal on top of this
  // dialog; on `onUploaded` we refetch the documents list + auto-
  // select the new doc so the user doesn't have to hunt for it.
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  // Briefs come from the Work Studio aggregates listing — same call
  // the Briefing tab already makes. We only refetch when the user
  // actually picks the brief source, to avoid surprising network
  // traffic on accounts that never use this path.
  useEffect(() => {
    if (!open || source !== "brief" || !contextId) return undefined;
    let dead = false;
    setBriefsLoading(true);
    api
      .get(`/contexts/${contextId}/briefings/aggregates`, { params: { kind: "briefing", page_size: 50 } })
      .then(({ data }) => { if (!dead) setBriefs(sortByNameAlpha(data?.items || [])); })
      .catch(() => { if (!dead) setBriefs([]); })
      .finally(() => { if (!dead) setBriefsLoading(false); });
    return () => { dead = true; };
  }, [open, source, contextId]);

  // Documents — fetched lazily when the external-document source is
  // chosen. We keep it simple: list everything the workspace has and
  // let the user pick. Alpha-sorted per DECK-020.
  //
  // Also re-fetch on `refetchDocsToken` bump — the in-modal upload
  // flow bumps this after a successful upload so the new doc appears
  // in the list without the user closing/re-opening the modal.
  const [refetchDocsToken, setRefetchDocsToken] = useState(0);
  useEffect(() => {
    if (!open || source !== "external_document" || !contextId) return undefined;
    let dead = false;
    setDocumentsLoading(true);
    api
      .get(`/contexts/${contextId}/documents`, { params: { limit: 200 } })
      .then(({ data }) => {
        if (dead) return;
        const rows = Array.isArray(data) ? data : (data?.documents || []);
        setDocuments(sortByNameAlpha(rows));
      })
      .catch(() => { if (!dead) setDocuments([]); })
      .finally(() => { if (!dead) setDocumentsLoading(false); });
    return () => { dead = true; };
  }, [open, source, contextId, refetchDocsToken]);

  useEffect(() => {
    if (!open) {
      setTitle("");
      setSource("blank");
      setSelectedBriefIds(new Set());
      setSelectedDocumentIds(new Set());
      setUploadModalOpen(false);
    }
  }, [open]);

  const label = KIND_LABEL[kind] || KIND_LABEL.deck;

  // JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — checkbox
  // list handlers. Toggle-based add/remove from the Set state; the
  // Checkbox primitive from @/components/ui/checkbox already surfaces
  // the correct chrome (existing pill/list styling parity).
  const toggleBrief = useCallback((briefId) => {
    setSelectedBriefIds((prev) => {
      const next = new Set(prev);
      if (next.has(briefId)) next.delete(briefId);
      else next.add(briefId);
      return next;
    });
  }, []);
  const toggleDocument = useCallback((docId) => {
    setSelectedDocumentIds((prev) => {
      const next = new Set(prev);
      if (next.has(docId)) next.delete(docId);
      else next.add(docId);
      return next;
    });
  }, []);

  // JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-021
  // upload callback. `UploadModal` calls `onUploaded(newDoc)` on
  // success. We bump the refetch token to reload the doc list, then
  // wait for the list to update via a follow-up effect that auto-
  // selects the new doc id.
  const [autoSelectDocIdAfterUpload, setAutoSelectDocIdAfterUpload] = useState(null);
  const onDocumentUploaded = useCallback((newDoc) => {
    setUploadModalOpen(false);
    if (newDoc && newDoc.id) {
      setAutoSelectDocIdAfterUpload(newDoc.id);
    }
    setRefetchDocsToken((t) => t + 1);
    toast.success("Document uploaded — added to your selection.");
  }, []);

  // Once the doc list refetch lands, auto-select the newly-uploaded doc.
  useEffect(() => {
    if (!autoSelectDocIdAfterUpload) return;
    if (documentsLoading) return;
    const hit = documents.some((d) => d.id === autoSelectDocIdAfterUpload);
    if (hit) {
      setSelectedDocumentIds((prev) => {
        const next = new Set(prev);
        next.add(autoSelectDocIdAfterUpload);
        return next;
      });
      setAutoSelectDocIdAfterUpload(null);
    }
  }, [autoSelectDocIdAfterUpload, documents, documentsLoading]);

  const submit = async (e) => {
    e?.preventDefault?.();
    const t = title.trim();
    if (!t) {
      toast.error("Title is required.");
      return;
    }
    if (source === "brief" && selectedBriefIds.size === 0) {
      toast.error("Pick at least one brief or switch to Blank.");
      return;
    }
    if (source === "external_document" && selectedDocumentIds.size === 0) {
      toast.error("Pick at least one document or switch to Blank.");
      return;
    }
    // Track A Phase 5 (2026-06-04, W6) — blank-source route hands off
    // to the Drafting Side Drawer (W5 path) with the right format
    // for the kind. Skips the /artefacts POST entirely; the Drafting
    // drawer's /save-draft is what writes the work_studio_exports
    // row on first save.
    if (source === "blank") {
      onClose && onClose();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("akki:open-drafting-drawer", {
          detail: { kind, title: t },
        }));
      }
      return;
    }
    setBusy(true);
    try {
      // JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-018
      // + DECK-022 plural payload. Backend accepts both singular and
      // plural for 1 release; we always send plural. Aggregate-id
      // prefix stripping is still applied per-id.
      const briefIdsPlural = source === "brief"
        ? Array.from(selectedBriefIds).map((bid) => stripAggPrefix(bid, "briefing"))
        : [];
      const documentIdsPlural = source === "external_document"
        ? Array.from(selectedDocumentIds)
        : [];
      const payload = {
        kind,
        title: t,
        source,
        source_brief_ids: briefIdsPlural,
        source_document_ids: documentIdsPlural,
      };
      const { data } = await api.post(
        `/contexts/${contextId}/work-studio/artefacts`,
        payload,
      );
      const newId = data?.artefact_id;
      const redirect = data?.redirect_url || (newId ? `/app/studio/composer/${kind}/${newId}` : null);
      toast.success(`${label.noun.charAt(0).toUpperCase()}${label.noun.slice(1)} created.`);
      onCreated && onCreated(data);
      onClose && onClose();
      if (redirect) navigate(redirect);
    } catch (err) {
      toast.error(apiErrorMessage(err, `Could not create ${label.noun}.`));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <Dialog open={open} onOpenChange={(v) => !v && !busy && onClose && onClose()}>
        <DialogContent className="max-w-lg bg-[var(--parchment)]" data-testid={`create-artefact-modal-${kind}`}>
          <DialogHeader>
            <DialogTitle className="akki-serif text-[18px] text-[var(--ink)]">{label.title}</DialogTitle>
            <DialogDescription className="text-[12.5px] text-[var(--muted)]">
              Give it a title. Pick a source. We&apos;ll land you in the editor.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <Label className="text-[12px]" htmlFor="create-artefact-title">Title</Label>
              <Input
                id="create-artefact-title"
                autoFocus
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={kind === "report" ? "e.g. Q1 Board Report" : "e.g. April ExCo Read-out"}
                className="rounded-sm text-[13.5px] mt-1"
                data-testid={`create-artefact-title-${kind}`}
              />
            </div>

            <fieldset>
              <legend className="text-[12px] text-[var(--muted)] mb-2">Start from</legend>
              <div className="space-y-1.5">
                {[
                  { key: "blank",              label: "Blank — I'll write it from scratch." },
                  { key: "brief",              label: "One or more existing briefs in this workspace." },
                  { key: "external_document",  label: "One or more external documents I've uploaded." },
                ].map((opt) => (
                  <label
                    key={opt.key}
                    className={[
                      "flex items-start gap-2 px-3 py-2 border rounded-sm cursor-pointer",
                      source === opt.key
                        ? "border-[var(--ink)] bg-white"
                        : "border-[var(--rule)] hover:border-[var(--ink)]/40",
                    ].join(" ")}
                  >
                    <input
                      type="radio"
                      name="source"
                      checked={source === opt.key}
                      onChange={() => setSource(opt.key)}
                      className="mt-1"
                      data-testid={`create-artefact-source-${opt.key}`}
                    />
                    <span className="text-[13px] text-[var(--ink)]">{opt.label}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            {source === "brief" && (
              <div data-testid="create-artefact-brief-picker">
                <div className="flex items-center justify-between mb-1">
                  <Label className="text-[12px]">Pick one or more briefs</Label>
                  {selectedBriefIds.size > 0 && (
                    <span
                      className="text-[11px] text-[var(--muted)]"
                      data-testid="create-artefact-brief-selected-count"
                    >
                      {selectedBriefIds.size} selected
                    </span>
                  )}
                </div>
                {briefsLoading ? (
                  <p className="text-[11.5px] text-[var(--muted)] italic mt-1 inline-flex items-center gap-1">
                    <Loader2 className="w-3 h-3 animate-spin" /> Loading briefs…
                  </p>
                ) : briefs.length === 0 ? (
                  <p
                    className="text-[11.5px] text-[var(--muted)] italic mt-1"
                    data-testid="create-artefact-brief-empty"
                  >
                    No briefs in this workspace yet. Compose one through Solva, or pick &quot;Blank&quot;.
                  </p>
                ) : (
                  <div
                    className="mt-1 max-h-52 overflow-y-auto border border-[var(--rule)] rounded-sm bg-white divide-y divide-[var(--rule)]"
                    data-testid="create-artefact-brief-checkbox-list"
                  >
                    {briefs.map((b) => {
                      const isChecked = selectedBriefIds.has(b.id);
                      return (
                        <label
                          key={b.id}
                          className="flex items-center gap-2 px-3 py-2 hover:bg-[var(--cream-deep)] cursor-pointer text-[13px] text-[var(--ink)]"
                          data-testid={`create-artefact-brief-option-${b.id}`}
                        >
                          <Checkbox
                            checked={isChecked}
                            onCheckedChange={() => toggleBrief(b.id)}
                            data-testid={`create-artefact-brief-checkbox-${b.id}`}
                          />
                          <span className="truncate">{b.name}</span>
                        </label>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {source === "external_document" && (
              <div data-testid="create-artefact-document-picker">
                <div className="flex items-center justify-between mb-1">
                  <Label className="text-[12px]">Pick one or more documents</Label>
                  <div className="flex items-center gap-3">
                    {selectedDocumentIds.size > 0 && (
                      <span
                        className="text-[11px] text-[var(--muted)]"
                        data-testid="create-artefact-document-selected-count"
                      >
                        {selectedDocumentIds.size} selected
                      </span>
                    )}
                    <button
                      type="button"
                      onClick={() => setUploadModalOpen(true)}
                      className="inline-flex items-center gap-1 text-[11.5px] text-[var(--accent)] hover:text-[var(--accent-dark)] hover:underline"
                      data-testid="create-artefact-document-upload-trigger"
                    >
                      <Upload className="w-3 h-3" strokeWidth={1.8} />
                      Upload new
                    </button>
                  </div>
                </div>
                {documentsLoading ? (
                  <p className="text-[11.5px] text-[var(--muted)] italic mt-1 inline-flex items-center gap-1">
                    <Loader2 className="w-3 h-3 animate-spin" /> Loading documents…
                  </p>
                ) : documents.length === 0 ? (
                  <p
                    className="text-[11.5px] text-[var(--muted)] italic mt-1"
                    data-testid="create-artefact-document-empty"
                  >
                    No documents uploaded yet. Use &quot;Upload new&quot; above, or pick &quot;Blank&quot;.
                  </p>
                ) : (
                  <div
                    className="mt-1 max-h-52 overflow-y-auto border border-[var(--rule)] rounded-sm bg-white divide-y divide-[var(--rule)]"
                    data-testid="create-artefact-document-checkbox-list"
                  >
                    {documents.map((d) => {
                      const isChecked = selectedDocumentIds.has(d.id);
                      const display = d.name || d.original_name || d.id;
                      return (
                        <label
                          key={d.id}
                          className="flex items-center gap-2 px-3 py-2 hover:bg-[var(--cream-deep)] cursor-pointer text-[13px] text-[var(--ink)]"
                          data-testid={`create-artefact-document-option-${d.id}`}
                        >
                          <Checkbox
                            checked={isChecked}
                            onCheckedChange={() => toggleDocument(d.id)}
                            data-testid={`create-artefact-document-checkbox-${d.id}`}
                          />
                          <span className="truncate">{display}</span>
                        </label>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            <DialogFooter>
              <Button type="button" variant="ghost" onClick={onClose} disabled={busy}>Cancel</Button>
              <Button
                type="submit"
                disabled={busy || !title.trim()}
                className="bg-[var(--ink)] hover:bg-[var(--ink)]/90 text-[var(--parchment)] rounded-sm"
                data-testid={`create-artefact-submit-${kind}`}
              >
                {busy && <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />}
                {label.submit}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-021
          in-modal upload. Radix Dialog nesting is supported (the
          UploadModal stacks on top; state preserved). `onUploaded`
          bumps the refetch token so the doc list refreshes + the new
          doc gets auto-selected via the follow-up effect above. */}
      <UploadModal
        open={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploaded={onDocumentUploaded}
      />
    </>
  );
}
