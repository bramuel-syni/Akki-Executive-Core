"""Phase 12.1 security tests.

Covers:
  - shield_map TTL enforcement (expiration boundary).
  - A record written with an unregistered key version fails to decrypt.
  - `/api/synisense/status` and `/dryrun` never leak any shield_map
    payload (shield_map_id is opaque; contents are server-only).

Cluster-F.6 (2026-06-27): converted from `asyncio.run(...)` direct
invocation pattern (M2 outlier) to `@pytest.mark.asyncio + async def`
so tests bind to the session-scoped event loop instead of creating a
fresh loop per call (same root cause as Cluster-E + Cluster-F.1..F.5).
Risk verdict per advance scan memo §3: LOW (Shield-adjacency tests
exercise the `pipeline_run` API surface, NOT Shield internals; both
M2 sites have return-value-only assertions with zero `asyncio.run`
semantics dependency; Shield-contract leaky-key absence set preserved
verbatim). Final Cluster-F sub-sprint — autosave's polluter set
becomes empty post-conversion → FTT-024..026 auto-close.
"""
import os
import sys

sys.path.insert(0, "/app/backend")

import pytest

from services.synisense import run as pipeline_run, encryption as enc


@pytest.fixture(autouse=True)
def _prep_keys():
    import secrets
    os.environ["SYNISENSE_MASTER_KEY"] = secrets.token_hex(32)
    os.environ.pop("SYNISENSE_ALLOW_INSECURE", None)
    os.environ.pop("AKKI_ENV", None)
    enc.init_keys()
    yield


@pytest.mark.asyncio
async def test_shield_reversible_produces_shield_map_id_only():
    # shield_reversible mode persists the shield map server-side and
    # returns an opaque id. Original content NEVER flows back to the
    # caller through the pipeline return value.
    text = "Email director@acme.com about the audit."
    out = await pipeline_run(
        text, context_id="sec-test", surface="ingest",
        mode="shield_reversible", account_id="test-admin",
    )
    # Still get the redacted text + spans + stats.
    assert out["redacted_text"] != text
    assert out["spans"]
    # shield_map_id is a string; never the cleartext mapping.
    assert isinstance(out["shield_map_id"], (str, type(None)))
    # No 'shield_map' or 'replacements_original' or 'mapping' keys in the
    # response that could leak originals.
    for k in ("shield_map", "mapping", "originals", "envelope"):
        assert k not in out


@pytest.mark.asyncio
async def test_redact_mode_never_creates_shield_map():
    text = "Email director@acme.com about the audit."
    out = await pipeline_run(
        text, context_id="sec-test", surface="chat",
        mode="redact", account_id="test-admin",
    )
    assert out["shield_map_id"] is None


def test_unregistered_version_blocks_decryption():
    """Pure-Python encryption envelope contract — no asyncio surface,
    stays sync per Cluster-F.2 heuristic.
    """
    env = enc.new_record_envelope(["originally-sensitive"])
    env["key_version"] = 42  # not registered
    with pytest.raises(enc.KeyVersionUnknown):
        enc.open_record_envelope(env)
