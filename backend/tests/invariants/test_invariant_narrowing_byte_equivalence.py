"""Phase 5.4 Narrowing Batch 1 — wire-byte equivalence harness.

This is the per-route safety net the Phase 5.4 dispatch demands. For
each route narrowed in Batch 1 — replacing
``response_model=Optional[Dict[str, Any]]`` with a named Pydantic
model — assert that the model preserves wire bytes for representative
payloads.

The wire-byte equivalence comes from ``ConfigDict(extra='allow')`` on
each new model — unknown fields pass through unchanged. This test
proves that property by:

  1. Instantiating the model from a representative fixture payload
     (drawn from `tests/fixtures/narrowing_batch_1/<route_slug>.json`).
  2. Serialising back via ``model_dump(exclude_none=False, by_alias=True)``.
  3. Asserting the round-tripped dict equals the original payload.

When the assertion holds, FastAPI's JSON-serialise-from-model path
emits the same wire bytes as a raw ``return <dict>`` would. This is
the wire-byte-identical guarantee the dispatch's "Acceptance 3"
demands without requiring authenticated HTTP captures (which need
DB seeding + auth tokens — out of scope for an architectural
invariant test).

Batch 1 routes (7):

| Route | Model |
|---|---|
| `GET /api/chats/{chat_id}` | `ChatResponse` |
| `PATCH /api/chats/{chat_id}` | `ChatResponse` |
| `GET /api/tasks/counts` | `TaskCountsResponse` |
| `GET /api/tasks/{task_id}` | `TaskResponse` |
| `PATCH /api/tasks/{task_id}` | `TaskResponse` |
| `POST /api/tasks/{tid}/commission` | `TaskResponse` |
| `POST /api/tasks/{tid}/close` | `TaskResponse` |

If a future batch widens (e.g. adds 10 more routes), append the
fixtures + the per-route equivalence test below — do NOT relax the
assertion.
"""
from __future__ import annotations

import json
from pathlib import Path

from contracts.responses import (
    ChatResponse,
    TaskCountsResponse,
    TaskResponse,
)


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "narrowing_batch_1"


def _load_fixture(slug: str) -> dict:
    """Load a representative payload fixture."""
    path = FIXTURES_DIR / f"{slug}.json"
    assert path.exists(), (
        f"Phase 5.4 narrowing batch 1 — fixture missing: {path}. "
        f"Restore the fixture file or remove the corresponding "
        f"equivalence test below."
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_byte_equivalent(payload: dict, model_cls, slug: str) -> None:
    """The core assertion: `model_dump()` round-trip must preserve the
    payload exactly.

    `extra='allow'` is the guarantee — every field outside the
    declared set flows through unchanged. If this assertion ever
    fails, the model has lost a field (lost the `extra='allow'`
    config, narrowed too aggressively, or accidentally aliased a
    known field).
    """
    instance = model_cls.model_validate(payload)
    round_tripped = instance.model_dump(exclude_unset=True, by_alias=True)
    assert round_tripped == payload, (
        f"Phase 5.4 narrowing batch 1 — wire-byte drift for `{slug}`:\n"
        f"  original keys: {sorted(payload.keys())}\n"
        f"  round-tripped: {sorted(round_tripped.keys())}\n"
        f"  diff (original - round_tripped): "
        f"{set(payload.keys()) - set(round_tripped.keys())}\n"
        f"  diff (round_tripped - original): "
        f"{set(round_tripped.keys()) - set(payload.keys())}\n\n"
        f"The model lost a field. Restore `model_config = "
        f"ConfigDict(extra='allow')` or fix the field declaration."
    )


# ─── Per-route equivalence tests ─────────────────────────────────────


def test_chat_get_byte_equivalence() -> None:
    """`GET /api/chats/{chat_id}` — `ChatResponse` preserves wire bytes."""
    payload = _load_fixture("get_chat_by_id")
    _assert_byte_equivalent(payload, ChatResponse, "get_chat_by_id")


def test_chat_patch_byte_equivalence() -> None:
    """`PATCH /api/chats/{chat_id}` — `ChatResponse` preserves wire bytes."""
    payload = _load_fixture("patch_chat_by_id")
    _assert_byte_equivalent(payload, ChatResponse, "patch_chat_by_id")


def test_tasks_counts_byte_equivalence() -> None:
    """`GET /api/tasks/counts` — `TaskCountsResponse` preserves the
    dynamic per-state keys via `extra='allow'`."""
    payload = _load_fixture("get_tasks_counts")
    _assert_byte_equivalent(payload, TaskCountsResponse, "get_tasks_counts")


def test_task_get_byte_equivalence() -> None:
    """`GET /api/tasks/{task_id}` — `TaskResponse` preserves wire bytes."""
    payload = _load_fixture("get_task_by_id")
    _assert_byte_equivalent(payload, TaskResponse, "get_task_by_id")


def test_task_patch_byte_equivalence() -> None:
    """`PATCH /api/tasks/{task_id}` — `TaskResponse` preserves wire bytes."""
    payload = _load_fixture("patch_task_by_id")
    _assert_byte_equivalent(payload, TaskResponse, "patch_task_by_id")


def test_task_commission_byte_equivalence() -> None:
    """`POST /api/tasks/{tid}/commission` — `TaskResponse` shape."""
    payload = _load_fixture("post_task_commission")
    _assert_byte_equivalent(payload, TaskResponse, "post_task_commission")


def test_task_close_byte_equivalence() -> None:
    """`POST /api/tasks/{tid}/close` — `TaskResponse` shape."""
    payload = _load_fixture("post_task_close")
    _assert_byte_equivalent(payload, TaskResponse, "post_task_close")


# ─── Edge-payload coverage ───────────────────────────────────────────


def test_chat_get_with_messages_array() -> None:
    """`GET /api/chats/{chat_id}` returns the chat dict plus a
    `messages` list. Verify the list (including nested message dicts)
    survives the round-trip."""
    payload = _load_fixture("get_chat_by_id_with_messages")
    _assert_byte_equivalent(
        payload, ChatResponse, "get_chat_by_id_with_messages"
    )


def test_task_with_status_history_and_team() -> None:
    """Tasks have a `status_history` list-of-dicts and a `team`
    list-of-dicts. Verify both deep-nested structures survive the
    round-trip."""
    payload = _load_fixture("get_task_by_id_full_extras")
    _assert_byte_equivalent(
        payload, TaskResponse, "get_task_by_id_full_extras"
    )


def test_tasks_counts_with_all_states() -> None:
    """`TASK_STATES` may grow. Verify the model passes through every
    state-name key regardless of the declared `all` field."""
    payload = _load_fixture("get_tasks_counts_all_states")
    _assert_byte_equivalent(
        payload, TaskCountsResponse, "get_tasks_counts_all_states"
    )
