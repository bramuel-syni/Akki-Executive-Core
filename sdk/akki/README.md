# `@akki/akki-sdk`

TypeScript SDK for the AKKI **Akki** bounded context.

Surface: `/v1/akki/*` — see `/app/memory/API_VERSIONING.md` for the versioning contract.

## Install

This is a local-only SDK at present (not published to npm). To consume it:

```bash
cp -r /app/sdk/akki ./vendor/akki-sdk
```

## Usage

```ts
import { AkkiClient } from './vendor/akki-sdk';

const client = new AkkiClient({
  baseUrl: 'https://api.example.com',
  authToken: process.env.AKKI_TOKEN,
});

// Example: hit any of the 593 generated operations
// const result = await client.someOperation();
```

## What this contains

- `index.ts` — auto-generated TypeScript source. Schemas + Client class.
- `package.json` — minimal package metadata. `npm run build` requires a local `tsc`.
- `index.openapi.json` — the source OpenAPI slice (committed for reproducibility).

## Regeneration

Whenever the `/v1/akki/*` surface changes:

```bash
cd /app/backend
python scripts/generate_sdk_slices.py   # refresh openapi-sdk/
cd /app
python backend/scripts/build_sdk.py     # rebuild the SDK
```

The `tests/invariants/test_invariant_sdk_slices.py` invariant will fail the CI build if the slice files drift from the live OpenAPI without being regenerated.
