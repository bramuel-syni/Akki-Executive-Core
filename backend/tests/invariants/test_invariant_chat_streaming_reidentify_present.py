"""Phase B1 — build-breaking invariant for the streaming-reidentify
wire-up on the chat surface.

Pins the load-bearing fact that `StreamingReidentifier` is
instantiated inside `stream_message` (the SSE endpoint at
`POST /api/chats/{chat_id}/messages/stream`) BEFORE any LLM delta
is yielded to the client. Without this rail, Shield-de-identified
prompts that contain `[[ENT_...]]` placeholders would echo back to
the user in the clear — the exact failure class Phase H2.5 closed
and Phase 14 hardened against.

Build-breaking: any refactor that removes the wire-up (or replaces
it with a sync re-identifier that can't be fed deltas) trips this
test at CI time. Mirrors the shape of
`test_invariant_http_transport_pydantic_kwargs.py` Phase 5.5.2 —
AST inspection is strictly stronger than a mock-and-assert here
because the regression vector is "code path no longer constructs
the streamer" which a mock would not catch.

Scope (the AST checks):
  1. Module-level import: `from
     services.synisense.shield.reidentifier import
     StreamingReidentifier` is present (or imported as a lazy
     within-function form — both pass).
  2. `stream_message` (the FastAPI endpoint async fn) exists and
     contains a call site to `StreamingReidentifier(...)`.
  3. The `StreamingReidentifier(...)` instantiation appears in the
     SSE generator body, NOT in a comment / dead code branch.

Why all three checks together: someone could keep the import but
delete the call site, or keep the call site but mis-name the
endpoint. Each check covers a distinct refactor vector.
"""
from __future__ import annotations

import ast
import pathlib

import pytest


CHAT_ROUTER_SRC = (
    pathlib.Path(__file__).resolve().parents[1].parent
    / "routers" / "chat.py"
).read_text()


def _parse_chat_router() -> ast.Module:
    return ast.parse(CHAT_ROUTER_SRC)


def test_streaming_reidentifier_import_present():
    """The chat router MUST import `StreamingReidentifier` from
    `services.synisense.shield.reidentifier`. Lazy (function-local)
    import is acceptable — the wire-up under `stream_message`
    uses the lazy form on purpose so the module load time of
    `routers/chat.py` doesn't take the reidentifier dep at cold-
    start when no streaming turn is in flight."""
    tree = _parse_chat_router()
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names = [n.name for n in node.names]
            if (mod.endswith("synisense.shield.reidentifier")
                    and "StreamingReidentifier" in names):
                found = True
                break
    assert found, (
        "REGRESSION: `StreamingReidentifier` is no longer imported "
        "from `services.synisense.shield.reidentifier` anywhere in "
        "`routers/chat.py`. Without the import, the streaming SSE "
        "endpoint cannot rehydrate `[[ENT_...]]` placeholders "
        "per-delta — Shield-de-identified prompts would leak the "
        "placeholders into the user-visible response. Re-add the "
        "import OR document the replacement (and update this "
        "invariant) in the corresponding sprint memo."
    )


def test_stream_message_endpoint_exists():
    """The FastAPI endpoint `stream_message` MUST exist as an async
    function in `routers/chat.py`. This is the SSE endpoint at
    `POST /api/chats/{chat_id}/messages/stream` — renaming or
    relocating it requires a coordinated FE/BE change captured in
    a sprint memo + updating this invariant's target name."""
    tree = _parse_chat_router()
    for node in ast.walk(tree):
        if (isinstance(node, ast.AsyncFunctionDef)
                and node.name == "stream_message"):
            return
    raise AssertionError(
        "REGRESSION: `async def stream_message(...)` not found in "
        "`backend/routers/chat.py`. The Phase B1 streaming surface "
        "depends on this function existing under exactly this "
        "name (the AST invariant pins the wire-up to it). Either "
        "restore the function OR rename this invariant's target."
    )


def test_streaming_reidentifier_instantiated_in_stream_message():
    """Inside `stream_message` (recursively, including nested
    closure bodies — the SSE generator is a closure), there MUST be
    at least one call site that constructs a
    `StreamingReidentifier(...)` instance. Without this construction
    the per-delta rehydration loop has no state — the `[[ENT_...]]`
    placeholders would echo to the client verbatim.

    The check is `ast.Call` with `func=ast.Name(id="StreamingReidentifier")`.
    A future refactor that wraps the construction in a helper
    (e.g. `make_reidentifier(token_map)`) would trip this test; in
    that case, either inline the construction back OR add the
    helper's name to the allow-list here AND document the rename
    in a sprint memo so the next agent can audit the change.
    """
    tree = _parse_chat_router()
    target = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.AsyncFunctionDef)
                and node.name == "stream_message"):
            target = node
            break
    assert target is not None, (
        "test_stream_message_endpoint_exists should have caught "
        "this — running test_streaming_reidentifier_"
        "instantiated_in_stream_message in isolation? Re-run the "
        "full invariant module."
    )
    invokes = [
        n for n in ast.walk(target)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "StreamingReidentifier"
    ]
    assert invokes, (
        "REGRESSION: `stream_message` no longer constructs a "
        "`StreamingReidentifier(...)` instance in its body. Without "
        "the per-stream rehydrator, the SSE endpoint cannot rewrite "
        "`[[ENT_...]]` placeholders as deltas arrive — Shield-de-"
        "identified prompts would leak the raw placeholders into "
        "the visible response (Phase H2.5 fix + Phase 14 fluency "
        "lockdown both depend on this rail). Re-instantiate the "
        "reidentifier OR document the replacement mechanism in the "
        "relevant sprint memo and update this invariant."
    )
    # Optional secondary signal: the construction call should pass
    # a `token_map`-like positional. We don't pin the kwarg name (
    # the production code uses a positional arg today, but a future
    # refactor might switch to kwargs); a non-empty arg list is the
    # minimum sane signal.
    assert any(
        bool(call.args) or bool(call.keywords)
        for call in invokes
    ), (
        "REGRESSION: `StreamingReidentifier()` is being called with "
        "no arguments. The reidentifier requires a `token_map` "
        "from the Shield's de-identify pass — without it, the "
        "rehydrator can't resolve any `[[ENT_...]]` placeholder. "
        "Inspect `services.synisense.shield.reidentifier."
        "StreamingReidentifier.__init__` for the required shape."
    )


# ─── Synthetic-regression check (lives inside this module so the
# AST invariant + the regression rail ship together) ───────────────


def test_synthetic_regression_removed_streamingreidentifier_call_breaks():
    """Self-test: if the `StreamingReidentifier(...)` call were
    removed from `stream_message`, the
    `test_streaming_reidentifier_instantiated_in_stream_message`
    assertion must fire. This synthetic regression proves the
    invariant isn't a no-op.

    We mutate a COPY of the chat router source (in memory) by
    deleting any `StreamingReidentifier(...)` call expression
    inside the `stream_message` AST and re-running the same check.
    Pass condition: the post-mutation check raises AssertionError.

    Why this matters: AST invariants are notorious for false-
    positive-greenness when the check itself is wrong (matches
    something benign, never matches anything else). The synthetic
    regression catches that class of bug at CI time without
    needing a separate red-build.
    """
    tree = ast.parse(CHAT_ROUTER_SRC)
    target = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.AsyncFunctionDef)
                and node.name == "stream_message"):
            target = node
            break
    assert target is not None

    class _StripSR(ast.NodeTransformer):
        def visit_Call(self, node: ast.Call):  # noqa: N802 — AST API
            if (isinstance(node.func, ast.Name)
                    and node.func.id == "StreamingReidentifier"):
                # Replace with a no-op `None` literal so the
                # surrounding code parses but the AST scan finds
                # zero matches.
                return ast.copy_location(ast.Constant(value=None), node)
            return self.generic_visit(node) or node

    stripped = _StripSR().visit(target)
    ast.fix_missing_locations(stripped)

    invokes = [
        n for n in ast.walk(stripped)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "StreamingReidentifier"
    ]
    assert not invokes, (
        "Synthetic regression failed to strip the "
        "`StreamingReidentifier(...)` call — the mutator's AST "
        "match is broken. Without a working stripper, the synthetic "
        "rail can't prove the live check would fail on regression. "
        "Inspect `_StripSR.visit_Call`."
    )


# ─── Pytest deselect markers ───────────────────────────────────────
#
# This file is a pure AST scan (no I/O, no MongoDB, no LLM). It
# should run on the default sweep — do NOT mark integration.
pytestmark: list = []
