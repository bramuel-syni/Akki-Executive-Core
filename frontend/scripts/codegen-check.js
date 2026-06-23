#!/usr/bin/env node
/**
 * Phase 3.1 codegen drift check.
 *
 * Re-generates `src/lib/api/schemas.gen.ts` into a temp file, diffs against
 * the committed copy. If they differ, fail with exit code 1 so CI breaks.
 *
 * Used by `yarn codegen:check`.
 */
const { execSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const COMMITTED = path.resolve(__dirname, "..", "src", "lib", "api", "schemas.gen.ts");
const TEMP = path.resolve(__dirname, "..", "src", "lib", "api", ".schemas.gen.ts.check.tmp");
const SPEC = path.resolve(__dirname, "..", "openapi.snapshot.json");

if (!fs.existsSync(SPEC)) {
  console.error(`!! openapi.snapshot.json missing: ${SPEC}`);
  process.exit(2);
}
if (!fs.existsSync(COMMITTED)) {
  console.error(`!! committed schemas.gen.ts missing: ${COMMITTED}`);
  process.exit(2);
}

try {
  execSync(`npx openapi-zod-client ${SPEC} -o ${TEMP}`, { stdio: "inherit" });
  // Apply the same post-processing as the main `yarn codegen` step so the
  // diff isn't tripped by the `export const endpoints` shim.
  let tempSrc = fs.readFileSync(TEMP, "utf8");
  tempSrc = tempSrc.replace(
    /^const endpoints = makeApi/m,
    "export const endpoints = makeApi"
  );
  fs.writeFileSync(TEMP, tempSrc);
} catch (e) {
  console.error("!! codegen failed");
  process.exit(2);
}

const committed = fs.readFileSync(COMMITTED, "utf8");
const fresh = fs.readFileSync(TEMP, "utf8");
fs.unlinkSync(TEMP);

if (committed !== fresh) {
  console.error("!! schemas.gen.ts drift detected.");
  console.error("   Committed file differs from a fresh codegen run.");
  console.error("   Fix: run `yarn codegen` and commit the result.");
  process.exit(1);
}

console.log("✓ schemas.gen.ts is in sync with openapi.snapshot.json");
process.exit(0);
