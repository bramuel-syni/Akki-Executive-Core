#!/usr/bin/env node
/**
 * Phase 3.1 — codegen post-processor.
 *
 * `openapi-zod-client` emits `schemas.gen.ts` with `const endpoints =
 * makeApi([...])` — but `endpoints` is NOT exported, only used internally
 * to construct the `api` (Zodios) export.
 *
 * Our `endpointSchemas.js` needs `endpoints` exported so we can build the
 * operationId → zod schema lookup. This script adds the `export` keyword
 * to the `endpoints` declaration.
 *
 * Run automatically after `yarn codegen`.
 */
const fs = require("node:fs");
const path = require("node:path");

const TARGET = path.resolve(
  __dirname,
  "..",
  "src",
  "lib",
  "api",
  "schemas.gen.ts"
);

if (!fs.existsSync(TARGET)) {
  console.error(`!! ${TARGET} missing — did codegen fail?`);
  process.exit(2);
}

let src = fs.readFileSync(TARGET, "utf8");

// Add `export` before `const endpoints = makeApi([...])`
const before = src.match(/^const endpoints = makeApi/m);
if (!before) {
  if (src.match(/^export const endpoints = makeApi/m)) {
    console.log("✓ endpoints already exported — no-op");
    process.exit(0);
  }
  console.error("!! `const endpoints = makeApi` line not found");
  process.exit(2);
}

src = src.replace(
  /^const endpoints = makeApi/m,
  "export const endpoints = makeApi"
);

fs.writeFileSync(TARGET, src);
console.log("✓ exported `endpoints` from schemas.gen.ts");
