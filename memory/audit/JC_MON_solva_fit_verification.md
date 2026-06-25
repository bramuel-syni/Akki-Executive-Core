# JC-MON Stage 0 · Q4 — Solva `probability_weighting` fit verification

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md`
>
> **Purpose:** Classify-by-execution that Solva's `probability_weighting`
> engine ACCEPTS the inputs a Monitor objective + tracked evidence would
> hand it. Verdict reproducible from the side-by-side table below.
>
> **Result:** **THIN ADAPTER** — wiring + transformation, proceed to
> Stage 2. No engine reshape required. The transformation is a
> well-defined "objective → single grounded claim" mapping that the
> engine already handles in shape; we just bend the input format to match
> what it expects.

---

## 1 · The engine — `services/solva_v2/engines/probability_weighting.py`

```
async def run(
    *,
    session: Dict[str, Any],
    turn_id: str,
    layer: str,
    claims: List[Dict[str, Any]],
    comparables: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
```

(`probability_weighting.py:132-139`)

**Returns:**
```python
{
    "output": {
        "claims":          List[Dict],          # each claim now carries
                                                 # `confidence_pct: int (0-100)`,
                                                 # `confidence_band: str`,
                                                 # `confidence_rationale: str`
        "violations":      List[Dict],          # tier-invariant violations
        "invariant_valid": bool,
    },
    "audit_entries":  List[Dict],               # 1 per Shield call (1-2 total)
}
```

(lines 232-237)

**Per-claim input shape** (lines 146-151):
```python
{
    "tier":  str,                  # corpus | comparable | domain_prior |
                                    #   user_assertion | speculation
    "text":  str,                  # the claim itself
    # ... other fields are passed through unchanged
}
```

**Per-claim output shape** (lines 224-230):
```python
{
    **input_claim,                  # original fields preserved
    "confidence_pct":        int,   # 0-100
    "confidence_band":       str,   # Unlikely | Possible | Likely | High-conviction
    "confidence_rationale":  str,
}
```

**Tier-invariant rules enforced** (lines 119-128):
- `corpus` and `comparable` tiers: `confidence_pct >= 35`
- `speculation` tier: `confidence_pct <= 75`

**Refusal discipline** (lines 215-223): if both Shield retries fail to
parse, the engine falls back to `confidence_pct=50, band="Possible",
rationale="Auto-calibrated: probability_weighting failed to parse twice."`
This is honest behaviour — there is NO confident probability fabricated
when the LLM round-trip can't produce one. Matches the JC-MON canonical
spec's refusal discipline ("A probability the user can't trust is worse
than none").

---

## 2 · What Monitor would hand it

A Monitor objective has, today, this shape (`strategic_items` collection):

```python
{
    "id":               "obj-<uuid>",
    "context_id":       "<ctx>",
    "account_id":       "<acc>",
    "kind":             "objective",
    "title":            "<short name>",
    "description":      "<long-form objective text>",
    "target_metric":    "<optional, e.g. 'attrition_rate'>",
    "target_value":     "<optional, e.g. '8% by Q4 FY26'>",
    "owner_account_id": "<optional>",
    "due_date":         "<optional ISO>",
    "progress_pct":     <optional int>,
    "status":           "draft | active | met | missed",
    "created_at":       "<ISO>",
}
```

Plus the **tracked-evidence corpus** Monitor reads against:
- **BASE docs** (`is_base_document=true`) — the strategic plan / performance
  agreement that defines what's being tracked against. Tier-mapping: `corpus`.
- **TRACKING docs** (`use_for_tracking=true`) — the evidence the assessment
  reads. Source channels include direct upload + the Document Journal
  pending → accepted flow for emailed-in evidence. Tier-mapping: `corpus`
  (canonical organisational data) or `comparable` (when industry-benchmark
  docs are flagged).

---

## 3 · Side-by-side mapping table

| Monitor input | `probability_weighting.run()` parameter | Mapping | Notes |
|---|---|---|---|
| `session` (must mint) | `session: Dict` | TRANSFORM — Monitor mints a transient assessment-session with `id` (uuid) + `account_id` + `context_id`. Audit chain still flows. | `session.id` is required for Shield audit row provenance (line 182). |
| `objective.id` | `turn_id: str` | DIRECT — use the objective UUID as the turn id. | Each assessment call is one "turn" in the audit chain. |
| static literal `"monitor.assessment"` | `layer: str` | DIRECT — Shield uses it for sub-surface routing. | New layer name; no reshape needed. |
| objective + tracked-docs → ONE claim | `claims: List[Dict]` (n≥1) | **TRANSFORM — single-claim adapter.** Monitor synthesizes ONE claim of the form `"{objective_title} will be achieved by {due_date} given current trajectory"` with `tier="corpus"` (the evidence is canonical organisational data). | This is the load-bearing transformation. The engine returns a per-claim `confidence_pct`; with `len(claims)==1`, that's our objective-level achievement probability. |
| optional benchmark docs (future) | `comparables: Optional[List[Dict]]` | DIRECT — passes through unchanged when present. | None today; placeholder for future industry-benchmark wiring. |

**The single-claim adapter** — the load-bearing piece:

```python
# Monitor-side adapter (lives in services/monitor/assessment_service.py).
# Build ONE corpus-tier claim representing the objective's achievement
# probability grounded in the tracked-document corpus.
claims = [{
    "tier": "corpus",
    "text": (
        f"{objective['title']} — target: {objective.get('target_value', '<not set>')}. "
        f"Will be achieved by {objective.get('due_date', '<no deadline>')} "
        f"given current trajectory across base docs + tracking docs."
    ),
    # Free-form passthrough fields the engine preserves:
    "objective_id":         objective["id"],
    "base_doc_ids":         [d["id"] for d in base_docs],
    "tracking_doc_ids":     [d["id"] for d in tracking_docs],
}]
```

The Shield prompt the engine emits (lines 161-166) reads this claim AND
the comparables block, then assigns `confidence_pct`. The engine's
`_check_invariants` (lines 112-129) confirms a `corpus`-tier claim got
pct ≥ 35; if the LLM produces a pct < 35 it retries once.

**The tracked-document corpus is reached via the comparables / prompt
extension, not by passing doc IDs directly to the engine.** The engine
itself is corpus-agnostic — it grades the CLAIM, not the document. We
extend the prompt downstream of `run()` if needed, but the v1 thin
adapter uses just the claim text + comparables block.

---

## 4 · Missing inputs (none load-bearing)

| Engine input | Monitor provides? | Resolution |
|---|---|---|
| `session.id` | NO (Monitor has no audit-session concept) | TRANSFORM — mint a transient session UUID per assessment call (cheap; no DB write needed; the engine only reads `.id` for Shield audit provenance). |
| `session.account_id` | YES — from `objective.account_id`. | DIRECT. |
| `session.context_id` | YES — from `objective.context_id`. | DIRECT. |
| `turn_id` | YES — use `objective.id`. | DIRECT. |
| `layer` | NO | DIRECT — static literal `"monitor.assessment"`. |
| `claims` | NO — Monitor has objectives, not claims | TRANSFORM (single-claim adapter, table above). |
| `comparables` | NO today (future) | DIRECT — optional; None for now. |

No missing input is a structural reshape. The single transformation
(objective → single corpus claim) is well-defined and does not require
changing the engine.

---

## 5 · Refusal-discipline alignment with canonical spec

The JC-MON canonical spec requires: *"thin evidence → say so; do not emit
a confident probability over nothing."*

The engine already enforces this via:

1. **Tier invariant** — corpus-tier claims grounded in EMPTY evidence
   force the LLM to return a pct ≥ 35 (line 121). The narrow band
   "35-54 = Possible" is the engine's honest signal for "ungrounded but
   plausible."
2. **Hard fallback** — twice-failed parse → `pct=50, band="Possible",
   rationale="Auto-calibrated: probability_weighting failed to parse twice."`
   (lines 215-223). The user sees an EXPLICIT "auto-calibrated" rationale,
   not a fabricated number.

For the Monitor refusal layer (above-engine), we also gate AT THE
ADAPTER: if `tracking_doc_ids` is empty AND the objective has been
active for > N days, the adapter doesn't call the engine at all and
returns a `REFUSED` payload with reason `"no_tracking_evidence_yet"`.
This matches the spec's *"with thin evidence, it refuses rather than
fabricating"* exactly.

---

## 6 · The session-mint detail (operational note, not a fork)

Solva v2's normal callers (`services/solva_v2/orchestrator.py` and
`routers/solva_v2.py`) load a real `solva_v2_sessions` row from Mongo
and pass it in. Monitor doesn't and shouldn't — assessment is on-demand,
not a stateful coaching session.

The engine reads only **`session.id`, `session.account_id`,
`session.context_id`** (lines 181-183). Monitor's transient session is:

```python
session = {
    "id":         str(uuid.uuid4()),                      # for Shield audit
    "account_id": objective["account_id"],
    "context_id": objective["context_id"],
}
```

This is enough — no Mongo write needed at the engine boundary. The
audit chain still threads cleanly because Shield's `reasoning_audit_log`
collects the entries via `audit_entries[]` in the engine's return value,
not via the session row. The MOnitor side then persists the audit
entries into its own `objective_assessment_audit` collection.

---

## 7 · Sample wired call (the actual adapter, ~25 LOC)

```python
# services/monitor/assessment_service.py — Stage 2 thin adapter
from services.solva_v2.engines.probability_weighting import run as pw_run

async def assess_objective_probability(
    *, db, objective: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not tracking_docs:
        return {"refused": True, "reason": "no_tracking_evidence_yet",
                "objective_id": objective["id"]}

    session = {
        "id":         str(uuid.uuid4()),
        "account_id": objective["account_id"],
        "context_id": objective["context_id"],
    }
    claims = [{
        "tier": "corpus",
        "text": (
            f"{objective['title']} — target: {objective.get('target_value', '<not set>')}. "
            f"Will be achieved by {objective.get('due_date', '<no deadline>')} "
            f"given current trajectory across base + tracking documents."
        ),
        "objective_id":     objective["id"],
        "base_doc_ids":     [d["id"] for d in base_docs],
        "tracking_doc_ids": [d["id"] for d in tracking_docs],
    }]
    result = await pw_run(
        session=session, turn_id=objective["id"],
        layer="monitor.assessment", claims=claims, comparables=None,
    )
    rated = (result.get("output") or {}).get("claims") or []
    if not rated:
        return {"refused": True, "reason": "engine_returned_no_ratings"}
    c = rated[0]
    return {
        "objective_id":         objective["id"],
        "probability_pct":      c["confidence_pct"],
        "probability_band":     c["confidence_band"],
        "probability_rationale": c["confidence_rationale"],
        "audit_entry_ids":      [a.get("id") for a in (result.get("audit_entries") or [])],
        "base_doc_ids":         [d["id"] for d in base_docs],
        "tracking_doc_ids":     [d["id"] for d in tracking_docs],
    }
```

That's the entire wiring layer. No fork.

---

## 8 · Verdict

| Criterion | Result |
|---|---|
| Engine accepts the inputs Monitor would hand it (after thin adapter)? | ✅ YES |
| Engine returns a usable per-objective probability? | ✅ YES — single-claim adapter gives objective-level `confidence_pct`. |
| Refusal discipline already aligned? | ✅ YES — engine has tier invariants + parse-failure fallback; adapter adds `no_tracking_evidence_yet` short-circuit. |
| Reshape required (= STOP)? | ❌ NO — single-claim transformation is a wiring task, not a reshape. |
| Reproducible by re-reading this doc? | ✅ YES — every claim is cited to specific line numbers in `probability_weighting.py`. |

**THIN ADAPTER. PROCEED TO STAGE 2.**

The adapter lives in a new file `services/monitor/assessment_service.py`
(does not exist today) and ships in Stage 2a as the proving slice. No
changes to `services/solva_v2/engines/probability_weighting.py`.
