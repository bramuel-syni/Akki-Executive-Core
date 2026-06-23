/**
 * Phase 3.1 — Deliberate-drift smoke test.
 *
 * Proves the drift-catch system has TEETH: forces a fake response that
 * VIOLATES a registered zod schema and asserts:
 *   - dev / staging / preview policy → `validatedCall` throws
 *     `ContractViolationError`
 *   - production policy             → `validatedCall` forwards the
 *     payload AND dispatches `akki:contract-violation` CustomEvent
 *
 * Same shape as Phase 0's deliberate-violation smokes — confirms the
 * wrapper actually catches what it claims to catch.
 *
 * Phase 3.2 will migrate hot-path call sites to `validatedCall`. This
 * test ensures the wrapper itself works BEFORE that migration.
 */

import { z } from "zod";

// Mock the underlying axios `api` client so we control the response shape.
// Path is `../lib/api` since the test file is at src/__tests__/ and the
// canonical client is at src/lib/api.js. `validatedCall.js` imports the
// `api` named export from `../api` (relative to src/lib/api/) — we mock
// the same module with a matching named export.
jest.mock("../lib/api", () => {
  const handlers = {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    patch: jest.fn(),
    delete: jest.fn(),
  };
  return {
    __esModule: true,
    api: handlers,
    default: handlers,
  };
});

// Mock the endpointSchemas to inject a deliberate zod schema we control.
jest.mock("../lib/api/endpointSchemas", () => ({
  endpointSchemas: {
    smoke_drift_op: require("zod").z.object({
      ok: require("zod").z.boolean(),
      id: require("zod").z.string(),
    }),
  },
  endpointSchemaCount: 1,
}));

// Pull the wrapper AFTER the mocks are wired.
import { api } from "../lib/api";
import {
  validatedCall,
  ContractViolationError,
  _failurePolicy,
} from "../lib/api/validatedCall";

describe("Phase 3.1 deliberate-drift smoke", () => {
  beforeEach(() => {
    api.get.mockReset();
    api.post.mockReset();
  });

  test("dev policy throws on drift (missing required field)", async () => {
    // Force dev policy: NODE_ENV is "test" in jest, _failurePolicy returns "throw".
    expect(_failurePolicy()).toBe("throw");

    // Mock the underlying axios call to return a SHAPE-WRONG payload.
    // Schema demands `{ok: boolean, id: string}`; we return `{ok: "yes", id: 7}`.
    api.get.mockResolvedValueOnce({
      data: { ok: "yes", id: 7 },
      status: 200,
      headers: {},
      config: { url: "/smoke/drift" },
    });

    let threw = null;
    try {
      await validatedCall({
        operationId: "smoke_drift_op",
        method: "get",
        url: "/smoke/drift",
      });
    } catch (e) {
      threw = e;
    }

    expect(threw).toBeInstanceOf(ContractViolationError);
    expect(threw.operationId).toBe("smoke_drift_op");
    expect(threw.zodError).toBeDefined();
    expect(threw.zodError.issues.length).toBeGreaterThan(0);
  });

  test("prod policy forwards payload + dispatches CustomEvent", async () => {
    // Force prod policy via mocked _failurePolicy.
    const origNodeEnv = process.env.NODE_ENV;
    const origBackendUrl = process.env.REACT_APP_BACKEND_URL;
    Object.defineProperty(process.env, "NODE_ENV", {
      value: "production",
      configurable: true,
    });
    Object.defineProperty(process.env, "REACT_APP_BACKEND_URL", {
      value: "https://syni.live",
      configurable: true,
    });

    try {
      expect(_failurePolicy()).toBe("log");

      api.get.mockResolvedValueOnce({
        data: { ok: "yes", id: 7 },
        status: 200,
        headers: {},
        config: { url: "/smoke/drift" },
      });

      const events = [];
      const listener = (ev) => events.push(ev);
      window.addEventListener("akki:contract-violation", listener);

      const result = await validatedCall({
        operationId: "smoke_drift_op",
        method: "get",
        url: "/smoke/drift",
      });

      window.removeEventListener("akki:contract-violation", listener);

      // Payload forwarded unchanged
      expect(result.data).toEqual({ ok: "yes", id: 7 });
      expect(result.status).toBe(200);

      // CustomEvent dispatched
      expect(events.length).toBe(1);
      expect(events[0].detail.operationId).toBe("smoke_drift_op");
      expect(events[0].detail.issues.length).toBeGreaterThan(0);
    } finally {
      Object.defineProperty(process.env, "NODE_ENV", {
        value: origNodeEnv,
        configurable: true,
      });
      Object.defineProperty(process.env, "REACT_APP_BACKEND_URL", {
        value: origBackendUrl,
        configurable: true,
      });
    }
  });

  test("valid payload passes through unchanged in dev policy", async () => {
    expect(_failurePolicy()).toBe("throw");

    api.get.mockResolvedValueOnce({
      data: { ok: true, id: "x-123" },
      status: 200,
      headers: {},
      config: { url: "/smoke/ok" },
    });

    const result = await validatedCall({
      operationId: "smoke_drift_op",
      method: "get",
      url: "/smoke/ok",
    });

    expect(result.data).toEqual({ ok: true, id: "x-123" });
  });

  test("missing schema in dev policy throws", async () => {
    expect(_failurePolicy()).toBe("throw");

    api.get.mockResolvedValueOnce({
      data: { anything: 1 },
      status: 200,
      headers: {},
      config: { url: "/nope" },
    });

    let threw = null;
    try {
      await validatedCall({
        operationId: "operationId_with_no_registered_schema",
        method: "get",
        url: "/nope",
      });
    } catch (e) {
      threw = e;
    }
    expect(threw).toBeInstanceOf(ContractViolationError);
    expect(threw.zodError.issues[0].code).toBe("missing_schema");
  });

  test("skipValidation escape hatch bypasses schema check", async () => {
    api.get.mockResolvedValueOnce({
      data: { ok: "broken", id: 999 },
      status: 200,
      headers: {},
      config: { url: "/smoke/escape" },
    });

    const result = await validatedCall({
      operationId: "smoke_drift_op",
      method: "get",
      url: "/smoke/escape",
      skipValidation: true,
    });

    expect(result.data).toEqual({ ok: "broken", id: 999 });
  });
});
