/**
 * Phase 3.1 — validatedCall wrapper.
 *
 * Wraps the existing axios `api` client (`lib/api.js`) with runtime zod
 * schema validation against the OpenAPI-generated schemas. Catches
 * frontend/backend response-shape drift.
 *
 * Failure-mode policy (hybrid, per Phase 3 Pre-Read §5):
 *   - dev / staging / preview → fail-closed (throw ContractViolationError)
 *   - production              → fail-open (forward payload + dispatch
 *                                `akki:contract-violation` CustomEvent for
 *                                Sentry / monitoring capture)
 *
 * Usage:
 *   import { validatedCall, endpointSchemas } from "../lib/api/validatedCall";
 *
 *   const { data } = await validatedCall({
 *     operationId: "list_chats_api_chats_get",
 *     method: "get",
 *     url: "/chats",
 *   });
 *
 * Phase 3.2 migrates call sites incrementally. Phase 3.1 keeps the
 * existing `api.*` calls unchanged.
 */

import { api } from "../api";
import { endpointSchemas } from "./endpointSchemas";

/**
 * Thrown when a response fails its zod schema validation in fail-closed mode.
 */
export class ContractViolationError extends Error {
  constructor(operationId, zodError, response) {
    super(
      `Contract violation on ${operationId}: ${zodError?.issues?.[0]?.message || "schema mismatch"}`
    );
    this.name = "ContractViolationError";
    this.operationId = operationId;
    this.zodError = zodError;
    this.response = response;
  }
}

/**
 * Decide which failure mode to use for the current environment.
 * - "throw" → dev / staging / preview (catch drift before users)
 * - "log"   → production (graceful degradation + observability signal)
 */
export function _failurePolicy() {
  // CRA / craco exposes NODE_ENV. Test env counts as dev for fail-closed.
  if (process.env.NODE_ENV !== "production") return "throw";
  // Preview deploys carry the emergent preview host — treat as fail-closed
  // so contract drift surfaces before users see it.
  if (
    typeof process.env.REACT_APP_BACKEND_URL === "string" &&
    process.env.REACT_APP_BACKEND_URL.includes("preview.emergentagent.com")
  ) {
    return "throw";
  }
  return "log";
}

/**
 * Internal: emit a contract-violation event for monitoring.
 */
function _emitViolation(operationId, zodError, response) {
  if (typeof window === "undefined") return;
  try {
    window.dispatchEvent(
      new CustomEvent("akki:contract-violation", {
        detail: {
          operationId,
          issues: zodError?.issues || [],
          url: response?.config?.url,
          status: response?.status,
        },
      })
    );
  } catch (_) {
    /* CustomEvent unavailable (very old browser / SSR) — ignore. */
  }
}

/**
 * Issue an HTTP call through the existing axios `api` client and validate
 * the response body against the zod schema registered for the operationId.
 *
 * @param {object}  opts
 * @param {string}  opts.operationId — key into endpointSchemas
 * @param {string}  opts.method      — "get" | "post" | "put" | "patch" | "delete"
 * @param {string}  opts.url         — request URL (passed to axios as-is)
 * @param {any}    [opts.data]       — request body (for POST/PUT/PATCH)
 * @param {object} [opts.params]     — query params
 * @param {object} [opts.config]     — extra axios config (headers, etc.)
 * @param {boolean}[opts.skipValidation] — if true, bypass zod check (escape hatch)
 *
 * @returns {Promise<{data, status, headers, config}>} — axios response shape
 */
export async function validatedCall(opts) {
  const { operationId, method, url, data, params, config, skipValidation } = opts;
  if (!operationId || !method || !url) {
    throw new Error(
      "validatedCall: operationId, method, and url are required"
    );
  }
  const m = String(method).toLowerCase();
  const httpFn = api[m];
  if (typeof httpFn !== "function") {
    throw new Error(`validatedCall: unknown method "${method}"`);
  }

  // Issue the request via the existing axios client (preserves CSRF, bearer,
  // active-context headers, redirect/rbac event funnel, etc.)
  let response;
  if (m === "get" || m === "delete") {
    response = await httpFn(url, { params, ...config });
  } else {
    response = await httpFn(url, data, { params, ...config });
  }

  if (skipValidation) return response;

  // Look up schema. Absence is itself a kind of drift — fail according to
  // policy so it surfaces.
  const schema = endpointSchemas[operationId];
  if (!schema) {
    const err = {
      issues: [
        {
          code: "missing_schema",
          message: `No zod schema registered for operationId ${operationId}`,
        },
      ],
    };
    if (_failurePolicy() === "throw") {
      throw new ContractViolationError(operationId, err, response);
    }
    _emitViolation(operationId, err, response);
    return response;
  }

  const result = schema.safeParse(response.data);
  if (!result.success) {
    if (_failurePolicy() === "throw") {
      throw new ContractViolationError(operationId, result.error, response);
    }
    _emitViolation(operationId, result.error, response);
    return response;
  }

  // Forward the validated payload (zod parse may coerce / strip — keep the
  // raw response object but swap data for the validated value).
  return { ...response, data: result.data };
}

export default validatedCall;
