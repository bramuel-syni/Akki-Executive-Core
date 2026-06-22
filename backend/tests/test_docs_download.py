"""Phase 15 — smoke tests for the master-doc download endpoints.

Deterministic file-IO + zip-parse tests; runs in the default sweep.
NO @pytest.mark.integration — these test the routes, not LLM behaviour.

Acceptance per Phase 15 dispatch §D:
  1. /api/docs/product → 200, text/markdown, attachment, body > 5000 bytes
  2. /api/docs/development → same shape
  3. /api/docs/bundle.zip → 200, zip parses, exactly 2 members
     (AKKI_PRODUCT.md + AKKI_DEVELOPMENT.md), each non-empty
  4. Missing source file → 503 with documented JSON shape
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Importing the FastAPI app pulls in the entire backend boot graph.
# The default sweep already exercises this import in 80+ other tests,
# so the cost is negligible here.
from server import app  # noqa: E402


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_product_download_streams_markdown(client: TestClient) -> None:
    r = client.get("/api/docs/product")
    assert r.status_code == 200, (
        f"expected 200 for /api/docs/product, got {r.status_code}: {r.text[:200]}"
    )
    ct = r.headers.get("content-type", "")
    assert ct.startswith("text/markdown"), f"content-type was {ct!r}"
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd, f"content-disposition was {cd!r}"
    assert "AKKI_PRODUCT.md" in cd, f"filename missing from content-disposition: {cd!r}"
    body = r.content
    assert len(body) > 5000, (
        f"PRODUCT.md body too short ({len(body)} bytes) — likely a stub, "
        "not the full doc"
    )
    # Sanity-check: the doc opens with the canonical heading.
    assert b"Akki / Syni \xe2\x80\x94 Product Reference" in body[:300] or \
           b"# Akki" in body[:300], "PRODUCT.md heading not found"


def test_development_download_streams_markdown(client: TestClient) -> None:
    r = client.get("/api/docs/development")
    assert r.status_code == 200, (
        f"expected 200 for /api/docs/development, got {r.status_code}: {r.text[:200]}"
    )
    ct = r.headers.get("content-type", "")
    assert ct.startswith("text/markdown"), f"content-type was {ct!r}"
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd, f"content-disposition was {cd!r}"
    assert "AKKI_DEVELOPMENT.md" in cd, f"filename missing from content-disposition: {cd!r}"
    body = r.content
    assert len(body) > 5000, (
        f"DEVELOPMENT.md body too short ({len(body)} bytes) — likely a stub"
    )
    assert b"# Akki" in body[:300], "DEVELOPMENT.md heading not found"


def test_bundle_zip_contains_both_files(client: TestClient) -> None:
    r = client.get("/api/docs/bundle.zip")
    assert r.status_code == 200, (
        f"expected 200 for /api/docs/bundle.zip, got {r.status_code}: {r.text[:200]}"
    )
    ct = r.headers.get("content-type", "")
    assert ct.startswith("application/zip"), f"content-type was {ct!r}"
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd and "AKKI_DOCS.zip" in cd, (
        f"content-disposition was {cd!r}"
    )

    buf = io.BytesIO(r.content)
    with zipfile.ZipFile(buf, mode="r") as zf:
        names = sorted(zf.namelist())
        assert names == ["AKKI_DEVELOPMENT.md", "AKKI_PRODUCT.md"], (
            f"zip members mismatch — got {names}"
        )
        for n in names:
            info = zf.getinfo(n)
            assert info.file_size > 5000, (
                f"zip member {n} too small ({info.file_size} bytes) — "
                "likely a stub or truncation"
            )
            content = zf.read(n)
            assert content.startswith(b"# Akki"), (
                f"zip member {n} doesn't start with expected heading"
            )


def test_missing_file_returns_503(monkeypatch, tmp_path, client: TestClient) -> None:
    """Verify the documented 503 shape when a source file is missing.

    Implementation strategy (per dispatch §D #4): monkeypatch the
    `_resolve_doc_paths` resolver so both downloads point at non-
    existent files inside `tmp_path`. The router's `_missing_docs()`
    helper then surfaces the documented JSON shape.
    """
    from routers import docs_download

    fake_paths = {
        "product":     tmp_path / "MISSING_PRODUCT.md",
        "development": tmp_path / "MISSING_DEVELOPMENT.md",
    }
    # Neither file exists — _resolve_doc_paths short-circuits.
    assert not fake_paths["product"].exists()
    assert not fake_paths["development"].exists()

    monkeypatch.setattr(docs_download, "_resolve_doc_paths", lambda: fake_paths)

    # Each individual route surfaces the missing key.
    r = client.get("/api/docs/product")
    assert r.status_code == 503, f"expected 503, got {r.status_code}: {r.text[:200]}"
    body = r.json()
    assert body == {
        "error":   "documentation_not_yet_generated",
        "missing": ["product"],
    }, f"unexpected 503 body: {body!r}"

    r = client.get("/api/docs/development")
    assert r.status_code == 503
    body = r.json()
    assert body == {
        "error":   "documentation_not_yet_generated",
        "missing": ["development"],
    }, f"unexpected 503 body: {body!r}"

    # Bundle endpoint reports both via the documented "both" shape.
    r = client.get("/api/docs/bundle.zip")
    assert r.status_code == 503, f"expected 503, got {r.status_code}: {r.text[:200]}"
    body = r.json()
    assert body == {
        "error":   "documentation_not_yet_generated",
        "missing": ["both"],
    }, f"unexpected bundle 503 body: {body!r}"


def test_one_file_missing_in_bundle_reports_single_key(monkeypatch, tmp_path,
                                                       client: TestClient) -> None:
    """Edge case: if only one doc is missing, bundle.zip should report
    that single key (not 'both'). Belt for the `len(missing) < 2`
    branch."""
    from routers import docs_download

    # Use the real product path but a missing development path.
    real_product = Path("/app/memory/PRODUCT.md")
    assert real_product.exists(), "test fixture: PRODUCT.md must exist"
    fake_paths = {
        "product":     real_product,
        "development": tmp_path / "MISSING_DEVELOPMENT.md",
    }
    monkeypatch.setattr(docs_download, "_resolve_doc_paths", lambda: fake_paths)

    r = client.get("/api/docs/bundle.zip")
    assert r.status_code == 503
    body = r.json()
    assert body == {
        "error":   "documentation_not_yet_generated",
        "missing": ["development"],
    }, f"unexpected single-missing 503 body: {body!r}"
