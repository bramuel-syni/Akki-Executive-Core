#!/usr/bin/env python3
"""Phase 5 Part E — Local TypeScript SDK generator from per-context OpenAPI slices.

Reads `/app/backend/openapi-sdk/{synisense,solva,akki}.openapi.json` and
emits a minimal TypeScript SDK per context under `/app/sdk/<ctx>/`.
Each SDK is a single `index.ts` file with:

  • Type definitions for every schema in `components.schemas`
  • One async function per operation, named after the path + method
  • A small `Client` class wrapping `fetch()` with auth headers

This generator is purposefully lightweight — production SDK pipelines
should use `openapi-typescript` or `openapi-generator-cli`; this script
is the in-tree fallback that proves the slice files are SDK-consumable
without external tooling. The output is small, readable, and useful
as-is for partner integration smoke tests.

Usage:
    python scripts/build_sdk.py [--clean]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
SLICE_DIR = REPO_ROOT / "backend" / "openapi-sdk"
OUTPUT_ROOT = REPO_ROOT / "sdk"


def _ts_identifier(s: str) -> str:
    """Sanitise an OpenAPI string to a TS-safe identifier."""
    out = re.sub(r"[^A-Za-z0-9_]", "_", s)
    if not out or out[0].isdigit():
        out = "_" + out
    return out


def _op_name(method: str, path: str) -> str:
    """Camel-cased operation name derived from method + path segments."""
    parts = [method.lower()]
    for seg in path.strip("/").split("/"):
        if seg.startswith("{") and seg.endswith("}"):
            parts.append("By" + _ts_identifier(seg[1:-1]).capitalize())
        else:
            parts.append(_ts_identifier(seg).capitalize())
    return parts[0] + "".join(p.capitalize() if i > 0 else p for i, p in enumerate(parts[1:]))


def _ts_type_for(schema: Dict[str, Any]) -> str:
    """Map a JSONSchema fragment to a TypeScript type expression."""
    if "$ref" in schema:
        ref = schema["$ref"].rsplit("/", 1)[-1]
        return _ts_identifier(ref)
    t = schema.get("type")
    if isinstance(t, list):
        return " | ".join(_ts_type_for({"type": x}) for x in t)
    if t == "string":
        if schema.get("enum"):
            return " | ".join(f'"{e}"' for e in schema["enum"])
        return "string"
    if t in ("integer", "number"):
        return "number"
    if t == "boolean":
        return "boolean"
    if t == "array":
        return f"Array<{_ts_type_for(schema.get('items', {}))}>"
    if t == "object":
        return "Record<string, unknown>"
    if "oneOf" in schema:
        return " | ".join(_ts_type_for(s) for s in schema["oneOf"])
    if "anyOf" in schema:
        return " | ".join(_ts_type_for(s) for s in schema["anyOf"])
    return "unknown"


def _emit_schema(name: str, schema: Dict[str, Any]) -> str:
    """Emit a TS `export type` or `export interface` for a single schema."""
    ident = _ts_identifier(name)
    if schema.get("type") == "object" and schema.get("properties"):
        props_lines: List[str] = []
        required = set(schema.get("required") or [])
        for prop, sub in schema["properties"].items():
            opt = "" if prop in required else "?"
            ts = _ts_type_for(sub)
            props_lines.append(f"  {_ts_identifier(prop)}{opt}: {ts};")
        body = "\n".join(props_lines)
        return f"export interface {ident} {{\n{body}\n}}"
    # Non-object schemas → type aliases
    return f"export type {ident} = {_ts_type_for(schema)};"


def _emit_client(context: str, slice_doc: Dict[str, Any]) -> str:
    """Emit the TS client module body for a single context."""
    paths = slice_doc.get("paths", {})
    schemas = slice_doc.get("components", {}).get("schemas", {})

    out: List[str] = []
    out.append("// AUTO-GENERATED — do not edit by hand.")
    out.append(f"// Source: backend/openapi-sdk/{context}.openapi.json")
    out.append(f"// Regenerate via: python scripts/build_sdk.py")
    out.append("")
    out.append("// ── Schemas ──")
    for name, schema in sorted(schemas.items()):
        out.append(_emit_schema(name, schema))
        out.append("")
    out.append("// ── Client ──")
    out.append(f"export interface {context.capitalize()}ClientOptions {{")
    out.append("  baseUrl: string;")
    out.append("  authToken?: string;")
    out.append("  fetchImpl?: typeof fetch;")
    out.append("}")
    out.append("")
    out.append(f"export class {context.capitalize()}Client {{")
    out.append("  private baseUrl: string;")
    out.append("  private authToken?: string;")
    out.append("  private fetchImpl: typeof fetch;")
    out.append("")
    out.append(f"  constructor(opts: {context.capitalize()}ClientOptions) {{")
    out.append("    this.baseUrl = opts.baseUrl.replace(/\\/$/, '');")
    out.append("    this.authToken = opts.authToken;")
    out.append("    this.fetchImpl = opts.fetchImpl ?? fetch;")
    out.append("  }")
    out.append("")
    out.append("  private async _request(method: string, path: string, body?: unknown): Promise<unknown> {")
    out.append("    const headers: Record<string, string> = { 'Content-Type': 'application/json' };")
    out.append("    if (this.authToken) headers['Authorization'] = `Bearer ${this.authToken}`;")
    out.append("    const resp = await this.fetchImpl(`${this.baseUrl}${path}`, {")
    out.append("      method,")
    out.append("      headers,")
    out.append("      body: body === undefined ? undefined : JSON.stringify(body),")
    out.append("    });")
    out.append("    if (!resp.ok) throw new Error(`${method} ${path} → ${resp.status}`);")
    out.append("    const ct = resp.headers.get('content-type') || '';")
    out.append("    return ct.includes('application/json') ? resp.json() : resp.text();")
    out.append("  }")
    out.append("")
    for path, ops in sorted(paths.items()):
        for method, opdef in sorted(ops.items()):
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            name = _op_name(method, path)
            method_upper = method.upper()
            has_body = method in ("post", "put", "patch")
            sig = (
                f"  async {name}(body?: unknown): Promise<unknown> {{"
                if has_body
                else f"  async {name}(): Promise<unknown> {{"
            )
            out.append(sig)
            out.append(f"    return this._request('{method_upper}', '{path}'"
                       f"{', body' if has_body else ''});")
            out.append("  }")
            out.append("")
    out.append("}")
    out.append("")
    return "\n".join(out)


def _emit_package_json(context: str) -> str:
    return json.dumps(
        {
            "name": f"@akki/{context}-sdk",
            "version": "1.0.0",
            "description": (
                f"AKKI {context.capitalize()} bounded-context SDK. "
                f"Generated from /v1/{context}/* OpenAPI slice."
            ),
            "main": "index.js",
            "types": "index.d.ts",
            "files": ["index.ts", "README.md"],
            "scripts": {
                "build": "tsc index.ts --target ES2020 --module ESNext "
                         "--moduleResolution Node --declaration --strict",
            },
            "license": "UNLICENSED",
        },
        indent=2,
    )


def _emit_readme(context: str, slice_doc: Dict[str, Any]) -> str:
    n_ops = sum(
        1
        for ops in slice_doc.get("paths", {}).values()
        for m in ops.keys()
        if m in ("get", "post", "put", "patch", "delete")
    )
    return f"""# `@akki/{context}-sdk`

TypeScript SDK for the AKKI **{context.capitalize()}** bounded context.

Surface: `/v1/{context}/*` — see `/app/memory/API_VERSIONING.md` for the versioning contract.

## Install

This is a local-only SDK at present (not published to npm). To consume it:

```bash
cp -r /app/sdk/{context} ./vendor/{context}-sdk
```

## Usage

```ts
import {{ {context.capitalize()}Client }} from './vendor/{context}-sdk';

const client = new {context.capitalize()}Client({{
  baseUrl: 'https://api.example.com',
  authToken: process.env.AKKI_TOKEN,
}});

// Example: hit any of the {n_ops} generated operations
// const result = await client.someOperation();
```

## What this contains

- `index.ts` — auto-generated TypeScript source. Schemas + Client class.
- `package.json` — minimal package metadata. `npm run build` requires a local `tsc`.
- `index.openapi.json` — the source OpenAPI slice (committed for reproducibility).

## Regeneration

Whenever the `/v1/{context}/*` surface changes:

```bash
cd /app/backend
python scripts/generate_sdk_slices.py   # refresh openapi-sdk/
cd /app
python backend/scripts/build_sdk.py     # rebuild the SDK
```

The `tests/invariants/test_invariant_sdk_slices.py` invariant will fail the CI build if the slice files drift from the live OpenAPI without being regenerated.
"""


def build(clean: bool = False) -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for ctx in ("synisense", "solva", "akki"):
        slice_path = SLICE_DIR / f"{ctx}.openapi.json"
        if not slice_path.exists():
            print(f"ERROR: slice file missing — {slice_path}. Run "
                  f"`python backend/scripts/generate_sdk_slices.py` first.")
            return 2
        with open(slice_path) as f:
            slice_doc = json.load(f)

        out_dir = OUTPUT_ROOT / ctx
        if clean and out_dir.exists():
            for f in out_dir.iterdir():
                f.unlink()
        out_dir.mkdir(parents=True, exist_ok=True)

        (out_dir / "index.ts").write_text(_emit_client(ctx, slice_doc))
        (out_dir / "package.json").write_text(_emit_package_json(ctx) + "\n")
        (out_dir / "README.md").write_text(_emit_readme(ctx, slice_doc))
        # Pin the source slice next to the generated code for reproducibility.
        (out_dir / "index.openapi.json").write_text(json.dumps(slice_doc, indent=2) + "\n")
        n_ops = sum(
            1
            for ops in slice_doc["paths"].values()
            for m in ops.keys()
            if m in ("get", "post", "put", "patch", "delete")
        )
        print(f"built {out_dir} — {n_ops} operations, "
              f"{len(slice_doc['components']['schemas'])} schemas")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clear each output directory before regenerating.",
    )
    args = parser.parse_args()
    return build(clean=args.clean)


if __name__ == "__main__":
    sys.exit(main())
