"""Contract surface snapshot invariant — Phase 1.

Per Operating Protocol v2 §1.7: "Public contracts cannot change
silently." This test pins the public surface of each contract
Protocol via `inspect.signature` snapshots. A silent change to any
method signature OR addition / removal of any method FAILS the build
— the developer must explicitly bless the new snapshot, which makes
the contract change visible in code review.

Snapshot files live next to this test as
`{contract}.contract_snapshot.json`. First run blesses; subsequent
runs compare.

What is captured per method:
  * parameter names (in order, including kwarg-only)
  * default-value presence (boolean — actual default is not part of
    the contract identity; presence is)
  * annotation type names (str form via `_anno_repr`) — pins return
    type and parameter types

What is NOT captured:
  * docstrings (mutable without breaking the contract)
  * default values (mutable for tuning without breaking the surface)
  * actual generic parameters' inner types beyond top-level name
"""
from __future__ import annotations

import inspect
import json
import typing
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Importing the contract Protocols pulls them into scope; their
# signatures are the surface under test.
from contracts import AkkiContract, SolvaContract, SyniSenseContract


SNAPSHOT_DIR = Path(__file__).parent
SNAPSHOTS = {
    "synisense": (SyniSenseContract, SNAPSHOT_DIR / "synisense.contract_snapshot.json"),
    "solva":     (SolvaContract,     SNAPSHOT_DIR / "solva.contract_snapshot.json"),
    "akki":      (AkkiContract,      SNAPSHOT_DIR / "akki.contract_snapshot.json"),
}


def _anno_repr(anno: Any) -> str:
    """Stable string form of a type annotation.

    `inspect.signature` returns the bare annotation object; we
    normalise to a string so JSON snapshot diffing is reliable.
    """
    if anno is inspect.Parameter.empty:
        return "<no-annotation>"
    if anno is None:
        return "None"
    # typing constructs (Optional, List, etc.) — use the repr; it's
    # stable for the typing module's display rules.
    return str(anno).replace("typing.", "")


def _method_signature_snapshot(fn: Any) -> Dict[str, Any]:
    """Return JSON-friendly snapshot of a method's signature."""
    sig = inspect.signature(fn)
    params: List[Dict[str, Any]] = []
    for name, p in sig.parameters.items():
        if name == "self":
            continue
        params.append({
            "name":       name,
            "kind":       str(p.kind),
            "annotation": _anno_repr(p.annotation),
            "has_default": p.default is not inspect.Parameter.empty,
        })
    return {
        "parameters": params,
        "return":     _anno_repr(sig.return_annotation),
    }


def _contract_snapshot(cls: type) -> Dict[str, Any]:
    """Return JSON-friendly snapshot of a Protocol class's full surface."""
    methods: Dict[str, Any] = {}
    for name in sorted(dir(cls)):
        if name.startswith("_"):
            continue
        attr = getattr(cls, name)
        if not callable(attr):
            continue
        methods[name] = _method_signature_snapshot(attr)
    return {
        "class":       cls.__name__,
        "method_count": len(methods),
        "methods":     methods,
    }


def _read_snapshot(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_snapshot(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ───────────────────────── tests ─────────────────────────

@pytest.mark.parametrize("name", sorted(SNAPSHOTS.keys()))
def test_contract_surface_matches_snapshot_or_blesses_first_run(name: str) -> None:
    """Each contract's surface matches the committed snapshot.

    On first run (no snapshot file), writes the snapshot and passes.
    On subsequent runs, compares; FAILS on any method add/remove
    or any signature change. The developer must explicitly delete
    the snapshot file and re-run to re-bless after an intentional
    contract change.
    """
    cls, snap_path = SNAPSHOTS[name]
    current = _contract_snapshot(cls)
    committed = _read_snapshot(snap_path)
    if committed is None:
        _write_snapshot(snap_path, current)
        return  # first-run bless

    # Method set comparison
    cur_methods = set(current["methods"].keys())
    com_methods = set(committed["methods"].keys())
    added = cur_methods - com_methods
    removed = com_methods - cur_methods
    assert not added, (
        f"{name}: NEW methods on contract surface (not in snapshot): "
        f"{sorted(added)!r}. Delete {snap_path.name} + re-run to bless."
    )
    assert not removed, (
        f"{name}: REMOVED methods from contract surface: "
        f"{sorted(removed)!r}. Delete {snap_path.name} + re-run to bless."
    )
    # Per-method signature comparison
    for m in sorted(cur_methods):
        cur_sig = current["methods"][m]
        com_sig = committed["methods"][m]
        assert cur_sig == com_sig, (
            f"{name}.{m}: signature drift. snapshot={com_sig!r} "
            f"current={cur_sig!r}. Delete {snap_path.name} + re-run to bless."
        )


def test_every_contract_method_has_account_id_kwarg() -> None:
    """ACCOUNT_ID INVARIANT — Phase 1 dispatch §"Mandatory behaviour-
    preservation" + §"Acceptance criteria" both require `account_id: str`
    as a required keyword on every method on every contract.
    """
    failures: List[str] = []
    for name, (cls, _) in SNAPSHOTS.items():
        for m_name in sorted(dir(cls)):
            if m_name.startswith("_"):
                continue
            attr = getattr(cls, m_name)
            if not callable(attr):
                continue
            sig = inspect.signature(attr)
            params = sig.parameters
            if "account_id" not in params:
                failures.append(f"{name}.{m_name}: missing `account_id` parameter")
                continue
            p = params["account_id"]
            anno = _anno_repr(p.annotation)
            if anno not in ("str", "<no-annotation>"):
                failures.append(
                    f"{name}.{m_name}: `account_id` annotation is {anno!r}, expected `str`"
                )
            if p.default is not inspect.Parameter.empty:
                failures.append(
                    f"{name}.{m_name}: `account_id` has a default; must be required"
                )
            if p.kind not in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                failures.append(
                    f"{name}.{m_name}: `account_id` kind {p.kind!r} unsuitable; "
                    f"expected KEYWORD_ONLY or POSITIONAL_OR_KEYWORD"
                )
    assert not failures, (
        "Contract surface violates account_id invariant:\n  "
        + "\n  ".join(failures)
    )


def test_contract_method_counts() -> None:
    """Pre-Read §4 pinned the method counts: 5 + 5 + 11 = 21.
    Phase 4.0 widening (Pre-Read §9.1) raised to: 5 + 6 + 12 = 23.
    """
    expected = {"synisense": 5, "solva": 6, "akki": 12}
    actual: Dict[str, int] = {}
    for name, (cls, _) in SNAPSHOTS.items():
        actual[name] = sum(
            1 for m in dir(cls)
            if not m.startswith("_") and callable(getattr(cls, m))
        )
    assert actual == expected, (
        f"Contract method count drift — expected {expected!r}, got {actual!r}"
    )


def test_adapters_implement_contracts() -> None:
    """Every adapter declares it implements its contract.

    The adapters live at `backend/contracts/_adapters/{synisense,solva,akki}.py`.
    `@runtime_checkable Protocol` allows isinstance() check.
    """
    from contracts._adapters.synisense import InProcessSyniSenseAdapter
    from contracts._adapters.solva import InProcessSolvaAdapter
    from contracts._adapters.akki import InProcessAkkiAdapter

    syn = InProcessSyniSenseAdapter()
    sol = InProcessSolvaAdapter()
    akk = InProcessAkkiAdapter()

    # runtime_checkable Protocol — verifies the adapter's surface
    # implements all required attributes.
    assert isinstance(syn, SyniSenseContract), (
        "InProcessSyniSenseAdapter does not implement SyniSenseContract"
    )
    assert isinstance(sol, SolvaContract), (
        "InProcessSolvaAdapter does not implement SolvaContract"
    )
    assert isinstance(akk, AkkiContract), (
        "InProcessAkkiAdapter does not implement AkkiContract"
    )
