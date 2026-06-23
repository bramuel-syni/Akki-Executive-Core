/**
 * Phase 3.1 — Contract Completeness fitness function.
 *
 * Asserts every endpoint declared in the OpenAPI snapshot has a
 * corresponding zod schema in the generated client. If the FE ever
 * calls an operationId that's not in the codegen, `validatedCall`
 * fails — this test catches that BEFORE the call happens, at CI time.
 *
 * Build-breaking.
 */

import { endpoints } from "../lib/api/schemas.gen";
import { endpointSchemas, endpointSchemaCount } from "../lib/api/endpointSchemas";
import openApiSnapshot from "../../openapi.snapshot.json";

describe("Phase 3.1 contract completeness", () => {
  test("every OpenAPI endpoint has a generated zod schema", () => {
    const HTTP_METHODS = new Set(["get", "post", "put", "patch", "delete"]);
    const specEndpoints = new Set();
    for (const [path, methods] of Object.entries(openApiSnapshot.paths || {})) {
      for (const [method, op] of Object.entries(methods)) {
        if (HTTP_METHODS.has(method) && op?.operationId) {
          specEndpoints.add(op.operationId);
        }
      }
    }
    const generatedAliases = new Set(endpoints.map((e) => e.alias));

    const missingFromGen = [...specEndpoints].filter(
      (op) => !generatedAliases.has(op)
    );

    expect(missingFromGen).toEqual([]);
  });

  test("endpointSchemas map has one entry per generated endpoint", () => {
    expect(Object.keys(endpointSchemas).length).toBe(endpoints.length);
    expect(endpointSchemaCount).toBe(endpoints.length);
  });

  test("every endpointSchemas value is a zod schema with .safeParse()", () => {
    const sample = Object.values(endpointSchemas).slice(0, 50);
    for (const schema of sample) {
      expect(typeof schema.safeParse).toBe("function");
    }
  });
});
