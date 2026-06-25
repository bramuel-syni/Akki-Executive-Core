/* JC-WS Phase 2 (2026-06-25) — Analyze workspace (Part B of canonical spec).

   Surfaces the four MISSING canonical-spec elements:
     d) Highlights-as-tweet-cards grouped under topics
     e) Docked free-text prompt at the bottom
     f) Data-aware question tips strip
     g) "Finish & export" handoff to the shared Document Generation export wizard

   This component renders as a new tab inside AnalyzeDrawer. The existing
   Observations/Notes/Export tabs remain untouched (compatibility) — this
   tab is the canonical-spec workspace.
*/
import React, { useEffect, useState, useCallback, useMemo, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api/apiV2";
import { apiErrorMessage } from "@/lib/api";
import { toast } from "sonner";
import { Send, Sparkles, FileDown, Loader2, AlertCircle, TrendingUp, Activity, Search, BarChart3, FlaskConical } from "lucide-react";

// Topic vocabulary → label + icon + color. Tight closed-set per backend
// `VALID_TOPICS` so we never silently group an unknown topic.
const TOPIC_META = {
  trend:    { label: "Trend",        icon: TrendingUp,    color: "bg-blue-500/10 text-blue-700 border-blue-200" },
  anomaly:  { label: "Anomaly",      icon: Activity,      color: "bg-amber-500/10 text-amber-700 border-amber-200" },
  forecast: { label: "Forecast",     icon: BarChart3,     color: "bg-emerald-500/10 text-emerald-700 border-emerald-200" },
  target:   { label: "Target",       icon: Search,        color: "bg-indigo-500/10 text-indigo-700 border-indigo-200" },
  validate: { label: "Validation",   icon: Sparkles,      color: "bg-slate-500/10 text-slate-700 border-slate-200" },
  simulate: { label: "Simulation",   icon: FlaskConical,  color: "bg-purple-500/10 text-purple-700 border-purple-200" },
  refusal:  { label: "Can't answer", icon: AlertCircle,   color: "bg-rose-500/10 text-rose-700 border-rose-200" },
};

const TOPIC_ORDER = ["trend", "anomaly", "forecast", "simulate", "target", "validate", "refusal"];

export default function HighlightsWorkspace({ aid, analysis, onAnalysisUpdate }) {
  const [tips, setTips]               = useState([]);
  const [tipsLoading, setTipsLoading] = useState(false);
  const [prompt, setPrompt]           = useState("");
  const [asking, setAsking]           = useState(false);
  const [finishing, setFinishing]     = useState(false);
  const [finishResult, setFinishResult] = useState(null);
  const promptRef = useRef(null);

  const highlights = useMemo(() => analysis?.highlights || [], [analysis]);

  // ── Group highlights by topic ────────────────────────────────────────
  const grouped = useMemo(() => {
    const buckets = {};
    for (const h of highlights) {
      const topic = TOPIC_META[h?.topic] ? h.topic : "validate";
      if (!buckets[topic]) buckets[topic] = [];
      buckets[topic].push(h);
    }
    // Preserve canonical order; only show non-empty topics.
    return TOPIC_ORDER.filter((t) => buckets[t]?.length).map((t) => ({
      topic: t,
      meta:  TOPIC_META[t],
      cards: buckets[t],
    }));
  }, [highlights]);

  // ── Load data-aware tips on mount + when highlights change ────────────
  const loadTips = useCallback(async () => {
    if (!aid) return;
    setTipsLoading(true);
    try {
      const { data } = await api.get(`/workbook/v2/analyses/${aid}/tips`);
      setTips(data?.tips || []);
    } catch (err) {
      // Tips are non-fatal; fall back to empty list. The deterministic
      // server-side fallback already produces useful suggestions.
      setTips([]);
    } finally {
      setTipsLoading(false);
    }
  }, [aid]);

  useEffect(() => { loadTips(); }, [loadTips, highlights.length]);

  // ── Docked prompt → /ask → accreted highlight ──────────────────────────
  const submitPrompt = useCallback(async () => {
    const q = (prompt || "").trim();
    if (!q) return;
    setAsking(true);
    try {
      const { data } = await api.post(`/workbook/v2/analyses/${aid}/ask`, { question: q });
      if (data?.highlight) {
        // Update the parent analysis row optimistically.
        if (onAnalysisUpdate) {
          onAnalysisUpdate((prev) => ({
            ...(prev || {}),
            highlights: [...(prev?.highlights || []), data.highlight],
          }));
        }
        setPrompt("");
        if (data.highlight.refused) {
          toast.info("Refusal surfaced — see the highlight for what's missing.");
        }
      }
    } catch (err) {
      toast.error(apiErrorMessage(err, "Could not ask the workspace."));
    } finally {
      setAsking(false);
    }
  }, [aid, prompt, onAnalysisUpdate]);

  const onTipClick = useCallback((tipText) => {
    setPrompt(tipText);
    if (promptRef.current) promptRef.current.focus();
  }, []);

  // ── Finish & export → export wizard handoff ──────────────────────────
  const finishAndExport = useCallback(async () => {
    setFinishing(true);
    setFinishResult(null);
    try {
      const { data } = await api.post(`/workbook/v2/analyses/${aid}/finish`, {
        kind: "report",
        objective: analysis?.objective || "",
      });
      setFinishResult(data);
      if (!data?.ok) {
        toast.info(data?.hint || "Ask at least one question before exporting.");
      } else {
        toast.success(`Ready to export — ${data.highlights_count} highlight(s) composed into a brief.`);
      }
    } catch (err) {
      toast.error(apiErrorMessage(err, "Could not prepare export."));
    } finally {
      setFinishing(false);
    }
  }, [aid, analysis]);

  // ── Render ─────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-full" data-testid="analyze-workspace">
      {/* ── Header with Finish & export CTA ─────────────────────────────── */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div>
          <div className="text-sm font-semibold text-foreground">Workspace</div>
          <div className="text-xs text-muted-foreground">
            {highlights.length} highlight{highlights.length === 1 ? "" : "s"}
            {analysis?.objective ? ` · ${analysis.objective.slice(0, 60)}` : ""}
          </div>
        </div>
        <Button
          size="sm"
          variant="default"
          disabled={finishing || !highlights.length}
          onClick={finishAndExport}
          data-testid="analyze-workspace-finish-export-btn"
        >
          {finishing ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <FileDown className="h-3.5 w-3.5 mr-1.5" />}
          Finish &amp; export
        </Button>
      </div>

      {/* ── Finish export result preview ─────────────────────────────────── */}
      {finishResult?.ok && (
        <div className="px-4 py-3 bg-emerald-50/60 border-b text-xs space-y-1" data-testid="analyze-workspace-finish-result">
          <div className="font-medium text-emerald-900">Composed brief ready for the export wizard.</div>
          <div className="text-muted-foreground">
            {finishResult.highlights_count} highlight(s){finishResult.refused_count ? ` · ${finishResult.refused_count} refusal(s) excluded` : ""}.
            Use the &quot;Export&quot; tab to ship as DOCX / PDF / PPTX.
          </div>
        </div>
      )}

      {/* ── Highlight feed (grouped by topic) ─────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-4 py-3" data-testid="analyze-workspace-highlights-feed">
        {grouped.length === 0 ? (
          <EmptyState onTipClick={onTipClick} tips={tips} tipsLoading={tipsLoading} />
        ) : (
          <div className="space-y-6">
            {grouped.map(({ topic, meta, cards }) => (
              <TopicGroup key={topic} topic={topic} meta={meta} cards={cards} />
            ))}
          </div>
        )}
      </div>

      {/* ── Docked prompt + tips strip ─────────────────────────────────────── */}
      <div className="border-t bg-background/95 backdrop-blur" data-testid="analyze-workspace-dock">
        {tips.length > 0 && grouped.length > 0 && (
          <div className="px-4 pt-3 pb-2 flex flex-wrap gap-1.5" data-testid="analyze-workspace-tips-strip">
            {tips.map((tip, i) => (
              <button
                key={i}
                type="button"
                onClick={() => onTipClick(tip.text)}
                className="text-xs px-2.5 py-1 rounded-full border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
                data-testid={`analyze-workspace-tip-${i}`}
              >
                <span className="text-muted-foreground mr-1.5 capitalize">{tip.intent}</span>
                {tip.text}
              </button>
            ))}
          </div>
        )}
        <div className="px-4 py-3">
          <div className="flex gap-2 items-end">
            <Textarea
              ref={promptRef}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ask anything about the data — forecast, simulate, validate, extract…"
              rows={2}
              className="flex-1 resize-none text-sm"
              disabled={asking}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  submitPrompt();
                }
              }}
              data-testid="analyze-workspace-prompt-input"
            />
            <Button
              size="sm"
              disabled={asking || !prompt.trim()}
              onClick={submitPrompt}
              data-testid="analyze-workspace-prompt-submit"
            >
              {asking ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </div>
          <div className="text-[10px] text-muted-foreground mt-1.5 px-0.5">
            Plain language works. <kbd className="px-1 py-0.5 bg-muted rounded text-[9px]">⌘↵</kbd> to send. Capabilities run under the surface; you see the highlight.
          </div>
        </div>
      </div>
    </div>
  );
}


/* ─────────────────────────────────────────────────────────────────────────────
 * Inner pieces — kept in-file so the workspace ships as a single unit.
 * ─────────────────────────────────────────────────────────────────────────── */

function EmptyState({ tips, tipsLoading, onTipClick }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center" data-testid="analyze-workspace-empty">
      <Sparkles className="h-8 w-8 text-muted-foreground/40 mb-3" />
      <div className="text-sm font-medium text-foreground mb-1">Ask the workspace</div>
      <div className="text-xs text-muted-foreground max-w-sm mb-5">
        Each question runs the right analyzer — forecast, simulate, validate, extract, anomaly — under the surface. The answers accrete here as cards.
      </div>
      {tipsLoading ? (
        <div className="text-xs text-muted-foreground"><Loader2 className="h-3 w-3 inline mr-1 animate-spin" /> Suggesting questions for your data…</div>
      ) : tips.length > 0 ? (
        <div className="flex flex-wrap gap-1.5 justify-center max-w-md" data-testid="analyze-workspace-empty-tips">
          {tips.map((tip, i) => (
            <button
              key={i}
              type="button"
              onClick={() => onTipClick(tip.text)}
              className="text-xs px-2.5 py-1 rounded-full border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
              data-testid={`analyze-workspace-empty-tip-${i}`}
            >
              <span className="text-muted-foreground mr-1.5 capitalize">{tip.intent}</span>
              {tip.text}
            </button>
          ))}
        </div>
      ) : (
        <div className="text-xs text-muted-foreground">Type a question below to begin.</div>
      )}
    </div>
  );
}


function TopicGroup({ topic, meta, cards }) {
  const Icon = meta.icon;
  return (
    <div data-testid={`analyze-workspace-topic-${topic}`}>
      <div className="flex items-center gap-2 mb-2.5">
        <Badge variant="outline" className={`${meta.color} text-[10px] uppercase tracking-wide font-semibold px-2 py-0.5`}>
          <Icon className="h-3 w-3 mr-1" />
          {meta.label}
        </Badge>
        <span className="text-[11px] text-muted-foreground">{cards.length}</span>
      </div>
      <div className="space-y-2">
        {cards.map((card) => (
          <HighlightCard key={card.id || card.created_at} card={card} topic={topic} />
        ))}
      </div>
    </div>
  );
}


function HighlightCard({ card, topic }) {
  const confidence = card.confidence || "medium";
  const isRefusal = topic === "refusal" || card.refused;
  const ap = card.analyzer_payload || {};
  // Cards with a real analyzer payload behind them get a natural
  // "View underlying read" affordance — JC-WS Phase 3 deep-link.
  // Refusals don't get it (there's nothing underneath to deep-link to).
  const hasUnderlyingRead = !isRefusal && (ap.target || ap.scenario || ap.horizon);
  const [expanded, setExpanded] = React.useState(false);
  return (
    <div
      className={`rounded-md border bg-card p-3 transition-shadow hover:shadow-sm ${isRefusal ? "border-rose-200/70" : ""}`}
      data-testid={`analyze-workspace-card-${card.id || ""}`}
    >
      <div className="text-sm font-semibold text-foreground leading-snug mb-1.5">
        {card.title || "(untitled)"}
      </div>
      <div className="text-xs text-muted-foreground leading-relaxed">
        {card.body || ""}
      </div>
      {(card.asked_question || card.citation || !isRefusal) && (
        <div className="mt-2.5 pt-2 border-t flex items-center justify-between gap-3 text-[10px] text-muted-foreground">
          <div className="flex items-center gap-2 truncate">
            {card.citation && <span className="font-mono">{card.citation}</span>}
            {card.asked_question && (
              <span className="italic truncate">&ldquo;{card.asked_question}&rdquo;</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {hasUnderlyingRead && (
              <button
                type="button"
                onClick={() => setExpanded((v) => !v)}
                className="text-[10px] text-muted-foreground hover:text-foreground transition-colors underline-offset-4 hover:underline"
                data-testid={`analyze-workspace-card-${card.id || ""}-view-raw`}
              >
                {expanded ? "Hide underlying read" : "View underlying read"}
              </button>
            )}
            {!isRefusal && (
              <Badge variant="outline" className="text-[9px] py-0 px-1.5 uppercase">{confidence}</Badge>
            )}
          </div>
        </div>
      )}
      {expanded && hasUnderlyingRead && (
        <div className="mt-2.5 pt-2.5 border-t bg-muted/30 -mx-3 -mb-3 px-3 py-2.5 rounded-b-md" data-testid={`analyze-workspace-card-${card.id || ""}-raw-panel`}>
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5 font-semibold">
            Underlying read · {ap.intent || card.intent || "—"}
          </div>
          <dl className="grid grid-cols-[80px_1fr] gap-x-3 gap-y-1 text-xs">
            {ap.target && (
              <>
                <dt className="text-muted-foreground">Target</dt>
                <dd className="font-mono">{ap.target}</dd>
              </>
            )}
            {ap.horizon && (
              <>
                <dt className="text-muted-foreground">Horizon</dt>
                <dd className="font-mono">{ap.horizon}</dd>
              </>
            )}
            {ap.scenario && (
              <>
                <dt className="text-muted-foreground">Scenario</dt>
                <dd className="italic">{ap.scenario}</dd>
              </>
            )}
            {ap.rationale && (
              <>
                <dt className="text-muted-foreground">Rationale</dt>
                <dd>{ap.rationale}</dd>
              </>
            )}
          </dl>
          <div className="mt-2 text-[10px] text-muted-foreground">
            Workspace dispatched this to the {ap.intent || "matching"} analyzer. The narration above is the read; the parameters are what the run was anchored on.
          </div>
        </div>
      )}
    </div>
  );
}
