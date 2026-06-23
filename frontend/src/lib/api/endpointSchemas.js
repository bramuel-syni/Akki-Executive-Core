/**
 * Phase 3.1 — endpointSchemas
 *
 * Builds an `operationId → zod schema` lookup from the generated
 * `schemas.gen.ts`. JS files import this to validate responses without
 * touching the codegen output.
 *
 * The generated file exports `endpoints` (an array of route definitions
 * with `alias` = operationId and `response` = zod schema). We index it.
 */

// Note: the import is .ts but craco/CRA 5.0.1 handles cross-file imports
// of .ts modules from .js consumers via babel-loader.
// eslint-disable-next-line import/no-unresolved
import { endpoints } from "./schemas.gen";

/**
 * { [operationId: string]: ZodSchema }
 */
export const endpointSchemas = Object.fromEntries(
  endpoints.map((e) => [e.alias, e.response])
);

/**
 * Total number of registered schemas — used by the contractCompleteness test.
 */
export const endpointSchemaCount = endpoints.length;
