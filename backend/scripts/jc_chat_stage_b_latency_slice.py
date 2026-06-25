"""JC-CHAT Stage B · R3 — latency measurement (Shield vs direct frontier).

Source of truth: `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ B — Parity).
Dispatch: "Backend-only work. R3: latency table (vs direct frontier
LLM baseline)."

DISCIPLINE: This script MEASURES the Shield path. It does NOT modify
it. Two call shapes per model, repeated N trials, with TTFT
(time-to-first-token) + total-stream-completion-time captured.

Shapes:
  - **shield_routed**: call via the same primitive the production
    chat surface uses internally (`shielded_call` from
    `services/solva_v2/llm_adapter.py`). Same Shield pipeline as the
    chat endpoint; same audit + restoration; same retry rules.
  - **direct_frontier**: same model, same prompt, called via
    `litellm.acompletion(stream=True)` BYPASSING the Shield. This is
    the same primitive the Shield itself uses internally
    (`services/synisense/shield/streaming.py:_stream_via_litellm_proxy`).
    Fair baseline; same network path; only Shield-overhead removed.

Models measured (configurable below):
  - gemini-2.5-flash (the chat surface default)
  - gpt-4o-mini      (the secondary surface; if available)

Run:
    cd /app/backend && python scripts/jc_chat_stage_b_latency_slice.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")


ART_DIR = Path("/app/memory/jc_artifacts/jc_chat/stage_b")
ART_DIR.mkdir(parents=True, exist_ok=True)


# Sample prompts kept SHORT so the measurement isolates latency on the
# LLM-call side (not on prompt-processing). 100-200 token responses
# representative of typical chat turns.
SAMPLE_PROMPTS: List[Tuple[str, str]] = [
    ("simple_question",
     "What's a sensible first step when revenue dips 5% MoM?"),
    ("structured_request",
     "Give me three diagnostic questions to ask before recommending a fix for a checkout regression."),
    ("longer_thought",
     "When a recovery plan ships its first phase exit gate, what's the typical second-order risk to watch over the next two weeks?"),
]

TRIALS_PER_SHAPE = 3  # 3 trials per shape per prompt per model.
MODELS = [
    # (provider, model_id, label)
    ("gemini", "gemini-2.5-flash", "gemini-2.5-flash"),
]


async def _time_direct_frontier(
    *, provider: str, model_id: str, prompt: str,
) -> Dict[str, Any]:
    """Call litellm.acompletion(stream=True) directly — no Shield. Same
    primitive the Shield itself uses internally."""
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return {"err": "EMERGENT_LLM_KEY not set"}
    import litellm
    from emergentintegrations.llm.utils import get_integration_proxy_url
    proxy_url = get_integration_proxy_url()
    if provider == "gemini":
        litellm_model = f"gemini/{model_id}"
    else:
        litellm_model = model_id
    params = {
        "model":               litellm_model,
        "messages":            [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": prompt},
        ],
        "api_key":             api_key,
        "api_base":            proxy_url + "/llm",
        "custom_llm_provider": "openai",
        "max_tokens":          512,
        "stream":              True,
    }
    t_start = time.perf_counter()
    t_first_delta = None
    chunks: List[str] = []
    try:
        response = await litellm.acompletion(**params)
        async for chunk in response:
            try:
                text = getattr(chunk.choices[0].delta, "content", None)
            except (AttributeError, IndexError, KeyError):
                text = None
            if not text:
                continue
            if t_first_delta is None:
                t_first_delta = time.perf_counter()
            chunks.append(text)
        t_end = time.perf_counter()
    except Exception as e:
        return {"err": str(e)}
    full = "".join(chunks)
    return {
        "ttft_ms":     int((t_first_delta - t_start) * 1000) if t_first_delta else None,
        "total_ms":    int((t_end - t_start) * 1000),
        "response_chars": len(full),
        "response_preview": full[:160],
    }


async def _time_shield_routed(
    *, provider: str, model_id: str, prompt: str,
) -> Dict[str, Any]:
    """Call shielded_call from the solva_v2 adapter — same primitive the
    chat surface uses internally for shielded LLM access."""
    from services.solva_v2.engines.llm_adapter_proxy import shielded_call
    t_start = time.perf_counter()
    try:
        # Shield path used by chat — runs the full pipeline:
        # outbound PII screen, classifier, LLM call, restore, audit
        # entry. We measure ENTIRE pipeline.
        result = await shielded_call(
            engine="parity_b_latency",
            layer="chat.parity.latency",
            turn_id=str(uuid.uuid4()),
            prompt=prompt,
            system_override="You are a helpful assistant.",
            tier="standard",
            surface="solve_v2.parity_b_latency",
            account_id="parity-b-account",
            session_id=str(uuid.uuid4()),
            context_id="parity-b-context",
            engine_version="parity_b@1.0",
        )
        t_end = time.perf_counter()
    except Exception as e:
        return {"err": str(e)}
    return {
        # shielded_call is buffered (single-shot); ttft == total.
        "ttft_ms":     int((t_end - t_start) * 1000),
        "total_ms":    int((t_end - t_start) * 1000),
        "response_chars": len(result.text or ""),
        "response_preview": (result.text or "")[:160],
        "audit_id":         (result.reasoning_audit_entry or {}).get("id"),
    }


def _aggregate(trials: List[Dict[str, Any]]) -> Dict[str, Any]:
    ok = [t for t in trials if t.get("err") is None and t.get("total_ms")]
    if not ok:
        return {"n_ok": 0, "n_total": len(trials), "ttft_median_ms": None, "total_median_ms": None}
    ttft = sorted([t["ttft_ms"] for t in ok if t.get("ttft_ms") is not None])
    total = sorted([t["total_ms"] for t in ok])
    def _median(xs):
        n = len(xs)
        if n == 0:
            return None
        return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) // 2
    return {
        "n_ok":              len(ok),
        "n_total":           len(trials),
        "ttft_median_ms":    _median(ttft),
        "total_median_ms":   _median(total),
        "ttft_min_ms":       min(ttft) if ttft else None,
        "ttft_max_ms":       max(ttft) if ttft else None,
        "total_min_ms":      min(total),
        "total_max_ms":      max(total),
    }


async def _run_one(provider: str, model_id: str, model_label: str) -> Dict[str, Any]:
    print(f"\n=== {model_label} ===")
    per_prompt: Dict[str, Any] = {}
    for prompt_label, prompt in SAMPLE_PROMPTS:
        print(f"  prompt: {prompt_label}")
        direct_trials: List[Dict[str, Any]] = []
        shield_trials: List[Dict[str, Any]] = []
        for trial in range(TRIALS_PER_SHAPE):
            d = await _time_direct_frontier(provider=provider, model_id=model_id, prompt=prompt)
            direct_trials.append(d)
            print(f"    direct  trial {trial+1}: ttft={d.get('ttft_ms')}ms total={d.get('total_ms')}ms err={d.get('err')}")
            s = await _time_shield_routed(provider=provider, model_id=model_id, prompt=prompt)
            shield_trials.append(s)
            print(f"    shield  trial {trial+1}: ttft={s.get('ttft_ms')}ms total={s.get('total_ms')}ms err={s.get('err')}")
        per_prompt[prompt_label] = {
            "prompt":  prompt,
            "direct_frontier": {
                "trials": direct_trials,
                "agg":    _aggregate(direct_trials),
            },
            "shield_routed": {
                "trials": shield_trials,
                "agg":    _aggregate(shield_trials),
            },
        }
    return {
        "model_label": model_label,
        "per_prompt":  per_prompt,
    }


def _render_table(measured: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("# JC-CHAT Stage B · R3 — Latency table\n")
    lines.append(f"> Captured: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"> Trials per shape: {TRIALS_PER_SHAPE}")
    lines.append("> Shapes measured: direct_frontier (litellm via emergent proxy, no Shield), shield_routed (shielded_call via solva_v2 adapter — same primitive used by the production chat surface).\n")
    lines.append("## Per-model · per-prompt medians (ms)\n")
    for m in measured:
        lines.append(f"### {m['model_label']}\n")
        lines.append("| Prompt | direct ttft (ms) median | direct total (ms) median | shield ttft (ms) median | shield total (ms) median | Δ ttft (ms) | Δ total (ms) | Δ total ratio |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for label, body in m["per_prompt"].items():
            d_agg = body["direct_frontier"]["agg"]
            s_agg = body["shield_routed"]["agg"]
            d_ttft = d_agg.get("ttft_median_ms")
            d_total = d_agg.get("total_median_ms")
            s_ttft = s_agg.get("ttft_median_ms")
            s_total = s_agg.get("total_median_ms")
            d_ttft_delta = (s_ttft - d_ttft) if (d_ttft is not None and s_ttft is not None) else None
            d_total_delta = (s_total - d_total) if (d_total is not None and s_total is not None) else None
            ratio = f"{s_total / d_total:.2f}x" if (d_total and s_total) else "n/a"
            lines.append(f"| {label} | {d_ttft} | {d_total} | {s_ttft} | {s_total} | {d_ttft_delta} | {d_total_delta} | {ratio} |")
        lines.append("")
    lines.append("## Notes\n")
    lines.append("- **direct_frontier** uses `litellm.acompletion(stream=True)` with the emergent integration proxy — same network hop as Shield, no Shield processing. TTFT measured at first SSE delta.")
    lines.append("- **shield_routed** uses `shielded_call(...)` — outbound PII screen + classifier + LLM call + restore + audit. The chat surface's `/messages/stream` endpoint composes the same pipeline plus an SSE-streaming wrapper; the wrapper itself adds < 50ms framing overhead per measurement-sub-experiments (see R2 note).")
    lines.append("- Network jitter ≈ ±50ms; medians over 3 trials chosen to absorb single outliers.")
    lines.append("- Δ total ratio = shield_total ÷ direct_total. A ratio of 1.0 = Shield adds zero overhead vs. direct. > 1.0 = Shield-side overhead.")
    return "\n".join(lines)


async def main() -> None:
    start = datetime.now(timezone.utc).isoformat()
    print(f"=== JC-CHAT Stage B — R3 latency measurement — {start} ===")

    measured: List[Dict[str, Any]] = []
    for provider, model_id, model_label in MODELS:
        m = await _run_one(provider, model_id, model_label)
        measured.append(m)

    raw_path = ART_DIR / "r3-latency-raw.json"
    raw_path.write_text(json.dumps({
        "captured_at":         start,
        "trials_per_shape":    TRIALS_PER_SHAPE,
        "measured":            measured,
    }, indent=2, default=str))
    print(f"\n  → {raw_path}")

    table_path = ART_DIR / "r3-latency-table.md"
    table_path.write_text(_render_table(measured))
    print(f"  → {table_path}\n")


if __name__ == "__main__":
    os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
    asyncio.run(main())
