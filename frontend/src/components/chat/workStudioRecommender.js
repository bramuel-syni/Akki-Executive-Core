/**
 * workStudioRecommender — Stage 4.2 (2026-06-24).
 *
 * Pure-JS heuristic that maps the user's objective + description
 * into the best-fit Work Studio kind. Lives outside the modal so
 * we can unit-test it without spinning up React.
 *
 * Discipline: zero LLM calls. The recommender is a regex pipeline
 * ordered high-confidence → low-confidence; the first matching
 * group wins. Falls back to "brief" when no signal fires so the
 * UI always has a default selection.
 *
 * Returns:
 *   { id: KindId, reason: string | null }
 *
 * `reason` is null only when no pattern matched. The caller surfaces
 * `reason` as quiet hint text below the kind grid.
 */

export const RECOMMENDER_KINDS = [
  "brief",
  "deck",
  "report",
  "minutes",
  "committee_pack",
  "board_pack",
];

const _KIND_PATTERNS = [
  // Board-pack signals — explicit "for the board", "board pack",
  // "board paper". Catches directors / NED audiences too.
  {
    id: "board_pack",
    reason: "Board-grade pack — directors as the audience",
    rx: /\b(board\s+pack|board\s+paper|board\s+meeting|for\s+the\s+board|main\s+board|directors|NEDs?|non-?executive)\b/i,
  },
  // Committee-pack signals — named committees or "committee pack".
  {
    id: "committee_pack",
    reason: "Committee pack — named committee as the audience",
    rx: /\b(committee\s+pack|committee\s+paper|for\s+the\s+committee|(?:audit|risk|remuneration|nomination|investment|exec(?:utive)?|advisory)\s+committee)\b/i,
  },
  // Minutes signals — meeting record / record-of-decisions framing.
  {
    id: "minutes",
    reason: "Meeting minutes — record-of-decisions framing",
    rx: /\b(minutes|meeting\s+minutes|record\s+of\s+(?:meeting|decisions?)|attendees|action\s+items?|agenda\s+items?)\b/i,
  },
  // Deck signals — slides / presentation / deck. Common verbs:
  // "present", "walk through", "pitch".
  {
    id: "deck",
    reason: "Slide deck — presentation framing",
    rx: /\b(deck|slides?|slide\s+deck|presentation|powerpoint|pptx?|pitch\s+deck|walk[ -]?through|present\s+(?:this|to|the))\b/i,
  },
  // Report signals — long-form / detailed analysis / white paper.
  // Note the explicit length hints — "long-form" / "detailed" /
  // "10-page" / "report" itself.
  {
    id: "report",
    reason: "Long-form report — detailed analysis framing",
    rx: /\b(report|long[- ]?form|detailed\s+(?:analysis|report|write[ -]?up)|white\s+paper|deep[ -]?dive|in[ -]?depth|\d+[ -]?page)\b/i,
  },
  // Brief signals — explicit "brief" / "summary" / "TL;DR" / "one-
  // pager". Lower priority than deck/report so explicit framings win.
  {
    id: "brief",
    reason: "Concise brief — short summary framing",
    rx: /\b(brief|summary|tl;?\s*dr|one[- ]?pager|short\s+summary|key\s+points)\b/i,
  },
];

export function recommendKind(objective, description) {
  // Concatenate objective + description so we catch cues from
  // either field. Objective sits first (more recent user intent).
  const haystack = `${objective || ""}\n${description || ""}`;
  if (!haystack.trim()) return { id: "brief", reason: null };
  for (const p of _KIND_PATTERNS) {
    if (p.rx.test(haystack)) return { id: p.id, reason: p.reason };
  }
  return { id: "brief", reason: null };
}
