/**
 * Phase 3.2 — `apiV2` wrapper
 *
 * Drop-in replacement for the existing axios `api` client. Same shape
 * (`apiV2.get / post / put / patch / delete`) so call sites swap a
 * single import line and immediately route through `validatedCall` with
 * the matching FastAPI operationId resolved at runtime.
 *
 * Behaviour:
 *  - If the (method, url) pair resolves to a known operationId, the
 *    call is routed through `validatedCall` (zod-schema-validated
 *    response, hybrid fail-mode per `_failurePolicy`).
 *  - If no operationId matches (e.g. cross-origin marketing endpoint,
 *    custom public path that isn't in the OpenAPI snapshot), the call
 *    falls through to the raw axios `api` client unchanged.
 *
 * Call shape — identical to the legacy `api`:
 *   await apiV2.get(url, axiosConfig)
 *   await apiV2.post(url, data, axiosConfig)
 *   await apiV2.patch(url, data, axiosConfig)
 *   await apiV2.put(url, data, axiosConfig)
 *   await apiV2.delete(url, axiosConfig)
 *
 * Used by Phase 3.2 hot-path migration. See `validatedCall.js` for the
 * underlying validation + failure-mode contract.
 */
import { api } from "../api";
import { validatedCall } from "./validatedCall";
import { resolveOperationId } from "./resolveOperation";

async function _call(method, url, data, config) {
  const operationId = resolveOperationId(method, url);
  if (!operationId) {
    // No matching operation in OpenAPI — fall through to raw axios.
    // (Public marketing endpoints, sandbox seed, csrf-mint path, etc.)
    const m = String(method).toLowerCase();
    return m === "get" || m === "delete"
      ? api[m](url, config)
      : api[m](url, data, config);
  }
  return validatedCall({ operationId, method, url, data, config });
}

const apiV2 = {
  get: (url, config) => _call("get", url, undefined, config),
  delete: (url, config) => _call("delete", url, undefined, config),
  post: (url, data, config) => _call("post", url, data, config),
  put: (url, data, config) => _call("put", url, data, config),
  patch: (url, data, config) => _call("patch", url, data, config),
  // For escape hatches (interceptors, defaults manipulation, raw axios
  // instance access) expose the underlying client unchanged.
  __raw: api,
};

export default apiV2;
export { apiV2, validatedCall, resolveOperationId };
