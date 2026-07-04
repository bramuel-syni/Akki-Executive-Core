/**
 * Module label constants — ThinkLab rename arc preparation surface.
 *
 * Canonical Spec: `/app/memory/audits/SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md`
 * + user directive 2026-07-02 (three-pick resolution + rename-arc §9 defaults).
 *
 * The Solva engine (`services/solva_v2/*`, backend internals) KEEPS the
 * name "Solva" verbatim. The Solva module (user-visible product surface
 * — nav labels, page titles, buttons, headers, emails, PDF/PPTX headers,
 * Doc Journal copy) RENAMES to "ThinkLab".
 *
 * This file is the single-point-of-change surface for all user-visible
 * strings that reference the module by name. The rename arc's Phase 1
 * dispatch (post-A1) will touch ONLY this file (plus supporting nav /
 * URL wiring) to flip the module label — every A1..A10 sub-sprint that
 * introduces module-referring copy imports from here and stays put.
 *
 * Two documented labels today:
 *
 *   MODULE_LABELS.thinklab    — user-visible module name. Used in nav
 *                               labels, page titles, CTAs ("Take into
 *                               ThinkLab"), tooltips, PDF/PPTX headers,
 *                               Doc Journal citation labels.
 *
 *   MODULE_LABELS.solvaEngine — user-visible engine-health label. Used
 *                               ONLY on admin/status surfaces where the
 *                               engine's technical health is the point
 *                               (e.g. StatusPage engine-health chip).
 *                               PER AUDIT §4 CASE 6 — this label KEEPS
 *                               the "Solva" name because it is
 *                               explicitly about the engine, not the
 *                               module.
 *
 * Any A1..A10 sub-sprint that introduces new module-referring copy MUST
 * import from this constants file (or hardcode "ThinkLab" verbatim per
 * user's ThinkLab-Ready Strings Guard). Never hardcode "Solva" for a
 * user-visible module reference — that's an engine-vs-module confusion.
 */
export const MODULE_LABELS = Object.freeze({
  thinklab: "ThinkLab",
  solvaEngine: "Solva engine",
  // P3 expansion (2026-07-02) — user-visible surface strings that route through the module label.
  thinklabSession: "ThinkLab session",
  thinklabSessions: "ThinkLab sessions",
  thinklabSessionLog: "ThinkLab session log",
  thinklabSubmodules: "ThinkLab sub-modules",
  thinklabConnecting: "ThinkLab \u2014 connecting",
  whatThinkLabCanOffer: "What ThinkLab can offer",
  thinklabSessionReasoningAudit: "ThinkLab session's reasoning audit",
});

// Convenience helpers so callers don't have to know the shape.
export const moduleLabel = () => MODULE_LABELS.thinklab;
export const solvaEngineLabel = () => MODULE_LABELS.solvaEngine;
