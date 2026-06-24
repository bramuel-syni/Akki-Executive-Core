/**
 * workStudioRecommender — Stage 4.2 unit suite (2026-06-24).
 *
 * Locks the objective → kind heuristic in the Chat Work Studio
 * affordance modal. The recommender is a pure-JS regex pipeline so
 * we exercise the contract directly without React. Each test
 * captures one user intent the patterns are claiming to support.
 *
 * If a future patch loosens a pattern and the cascade order changes,
 * one of these tests will break and the regression surfaces here
 * instead of on a live customer.
 */
import { recommendKind } from "../workStudioRecommender";

describe("recommendKind — objective → kind heuristic", () => {
  test("empty input → defaults to brief, no reason surfaced", () => {
    const r = recommendKind("", "");
    expect(r).toEqual({ id: "brief", reason: null });
  });

  test("null input is safe → defaults to brief", () => {
    const r = recommendKind(null, undefined);
    expect(r.id).toBe("brief");
    expect(r.reason).toBeNull();
  });

  test("'board pack' phrasing routes to board_pack with reason", () => {
    const r = recommendKind("Need a board pack for next month's meeting.", "");
    expect(r.id).toBe("board_pack");
    expect(r.reason).toMatch(/Board-grade/);
  });

  test("'for the board' phrasing routes to board_pack", () => {
    const r = recommendKind("Build something for the board.", "");
    expect(r.id).toBe("board_pack");
  });

  test("'audit committee' phrasing routes to committee_pack", () => {
    const r = recommendKind("Prep for the audit committee on Friday.", "");
    expect(r.id).toBe("committee_pack");
  });

  test("'committee pack' phrasing routes to committee_pack", () => {
    const r = recommendKind("Draft a committee pack covering Q4.", "");
    expect(r.id).toBe("committee_pack");
  });

  test("'meeting minutes' routes to minutes", () => {
    const r = recommendKind("Capture the meeting minutes from today.", "");
    expect(r.id).toBe("minutes");
  });

  test("'attendees + action items' routes to minutes", () => {
    const r = recommendKind(
      "Note the attendees and action items.",
      ""
    );
    expect(r.id).toBe("minutes");
  });

  test("'slide deck' routes to deck", () => {
    const r = recommendKind("Build a slide deck on Q3 performance.", "");
    expect(r.id).toBe("deck");
  });

  test("'PowerPoint' phrasing routes to deck", () => {
    const r = recommendKind("Make this a PowerPoint walk-through.", "");
    expect(r.id).toBe("deck");
  });

  test("'long-form report' routes to report", () => {
    const r = recommendKind("Produce a long-form report on this.", "");
    expect(r.id).toBe("report");
  });

  test("'detailed analysis' routes to report", () => {
    const r = recommendKind("Give me a detailed analysis.", "");
    expect(r.id).toBe("report");
  });

  test("'10-page write-up' routes to report (digit + page hint)", () => {
    const r = recommendKind("Need a 10-page write-up by Friday.", "");
    expect(r.id).toBe("report");
  });

  test("'short summary' routes to brief", () => {
    const r = recommendKind("Just a short summary, please.", "");
    expect(r.id).toBe("brief");
    expect(r.reason).toMatch(/Concise brief/);
  });

  test("'TL;DR' phrasing routes to brief", () => {
    const r = recommendKind("TL;DR on the new policy.", "");
    expect(r.id).toBe("brief");
  });

  test("'one-pager' routes to brief", () => {
    const r = recommendKind("Send me a one-pager.", "");
    expect(r.id).toBe("brief");
  });

  test("freeform ask with no kind cues → brief fallback (null reason)", () => {
    const r = recommendKind(
      "What's the right approach to onboarding new hires?",
      ""
    );
    expect(r.id).toBe("brief");
    expect(r.reason).toBeNull();
  });

  test("description carries the cue when objective is generic", () => {
    const r = recommendKind(
      "Write this up",
      "We discussed the upcoming risk committee paper."
    );
    expect(r.id).toBe("committee_pack");
  });

  test("board_pack wins over deck when both cues appear (priority)", () => {
    // The user explicitly says board pack — directors as audience —
    // even though they mention 'slides'. Board signal must win to
    // honour the audience framing.
    const r = recommendKind(
      "Need a board pack with summary slides.",
      ""
    );
    expect(r.id).toBe("board_pack");
  });

  test("committee_pack wins over deck when both cues appear", () => {
    const r = recommendKind(
      "Risk committee presentation deck.",
      ""
    );
    expect(r.id).toBe("committee_pack");
  });

  test("minutes wins over report when meeting cues lead", () => {
    const r = recommendKind(
      "Meeting minutes with a detailed report of decisions.",
      ""
    );
    expect(r.id).toBe("minutes");
  });
});
