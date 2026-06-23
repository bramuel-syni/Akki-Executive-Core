/**
 * Phase 3.2 — operationId resolver
 *
 * Maps a runtime (method, url) pair to the FastAPI operationId via the
 * generated `endpoints` array from `schemas.gen.ts`. Used by `apiV2` to
 * route validated calls through `validatedCall` without manual
 * per-call-site operationId threading.
 *
 * The generated endpoint paths come pre-prefixed with `/api/...` and use
 * `:var` placeholders. Runtime URLs from the existing axios `api` client
 * are typically passed WITHOUT the `/api/` prefix because `api`'s
 * baseURL handles that. We auto-prefix `/api` when missing so both work.
 */

// eslint-disable-next-line import/no-unresolved
import { endpoints } from "./schemas.gen";

// Pre-compile a matcher per endpoint. `path` has shape "/api/contexts/:id/..."
// → regex "^/api/contexts/[^/]+/...$".
const _matchers = (endpoints || []).map((e) => {
  const re = new RegExp(
    "^" +
      e.path
        .replace(/[.+?^${}()|[\]\\]/g, "\\$&")
        .replace(/:([a-zA-Z_][a-zA-Z_0-9]*)/g, "[^/]+") +
      "$"
  );
  return {
    method: String(e.method).toLowerCase(),
    path: e.path,
    regex: re,
    alias: e.alias,
  };
});

/**
 * Resolve the FastAPI operationId for a (method, url) call.
 *
 * @param {string} method  — "get" | "post" | "put" | "patch" | "delete"
 * @param {string} url     — request URL, with or without /api prefix; query
 *                            params are tolerated and stripped
 * @returns {string | null} — operationId if matched, else null
 */
export function resolveOperationId(method, url) {
  if (!method || !url) return null;
  const m = String(method).toLowerCase();
  let path = String(url);
  // Strip query / hash
  const q = path.indexOf("?");
  if (q !== -1) path = path.slice(0, q);
  const h = path.indexOf("#");
  if (h !== -1) path = path.slice(0, h);
  // Auto-prefix /api when missing (existing axios `api` client strips it).
  const prefixed = path.startsWith("/api/") || path === "/api" ? path : "/api" + (path.startsWith("/") ? path : "/" + path);
  for (const e of _matchers) {
    if (e.method === m && e.regex.test(prefixed)) {
      return e.alias;
    }
  }
  return null;
}

export default resolveOperationId;
