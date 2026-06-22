"""Phase 1 in-process contract adapters.

These adapters are PASS-THROUGH wrappers around the existing
service-layer functions and direct DB queries. They exist so that:

  - Call sites can migrate to the contract surface in Phase 2 without
    a behaviour change.
  - Phase 4 can swap the in-process adapter for an HTTP-client
    adapter via the dependency-injection accessors in
    `contracts.__init__` (`get_synisense()` / `get_solva()` /
    `get_akki()`).

PHASE 1 RULES:
  - No new logic. Adapters wrap existing functions / DB queries.
  - No behaviour change. The Phase 0 characterisation goldens must
    remain green at every commit.
  - Adapters are the ONLY package allowed to import across context
    boundaries (e.g. `_adapters/synisense.py` may import from
    `services.synisense.shield.*`). The boundary-imports invariant
    test EXEMPTS this directory.
"""
