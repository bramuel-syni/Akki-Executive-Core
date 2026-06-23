/**
 * Phase 3.2 — apiV2 wrapper smoke tests.
 *
 * Confirms the import-line drop-in works: same shape as raw axios `api`,
 * but routes through validatedCall when a matching operationId resolves.
 */

// Mock the underlying axios client BEFORE pulling apiV2.
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

import { api } from "../lib/api";
import apiV2 from "../lib/api/apiV2";

describe("Phase 3.2 — apiV2 wrapper", () => {
  beforeEach(() => {
    api.get.mockReset();
    api.post.mockReset();
    api.patch.mockReset();
    api.delete.mockReset();
  });

  test("apiV2.get falls through to raw axios when no operationId resolves", async () => {
    api.get.mockResolvedValueOnce({
      data: { fake: true },
      status: 200,
      headers: {},
      config: { url: "/nowhere" },
    });
    const r = await apiV2.get("/this/does/not/exist/anywhere");
    expect(r.data).toEqual({ fake: true });
    expect(api.get).toHaveBeenCalledWith(
      "/this/does/not/exist/anywhere",
      undefined
    );
  });

  test("apiV2.get with valid response on a known operationId returns the data", async () => {
    api.get.mockResolvedValueOnce({
      data: { default_model_id: "x", models: [] },
      status: 200,
      headers: {},
      config: { url: "/chat/models" },
    });
    const r = await apiV2.get("/chat/models");
    expect(r.data).toEqual({ default_model_id: "x", models: [] });
    // validatedCall calls api.get(url, { params, ...config })
    expect(api.get).toHaveBeenCalledWith("/chat/models", { params: undefined });
  });

  test("apiV2.post forwards body unchanged when operationId resolves", async () => {
    api.post.mockResolvedValueOnce({
      data: { id: "share-123" },
      status: 200,
      headers: {},
      config: { url: "/contexts/c/documents/d/share" },
    });
    const r = await apiV2.post("/contexts/c/documents/d/share", {
      recipient_emails: ["a@b.com"],
    });
    expect(r.data).toEqual({ id: "share-123" });
    expect(api.post).toHaveBeenCalledWith(
      "/contexts/c/documents/d/share",
      { recipient_emails: ["a@b.com"] },
      { params: undefined }
    );
  });

  test("apiV2.patch matches templated paths", async () => {
    api.patch.mockResolvedValueOnce({
      data: { task_id: "t", contributor_id: "c", readiness_score: 0.5, team: [] },
      status: 200,
      headers: {},
      config: { url: "/tasks/t/contributions/c" },
    });
    const r = await apiV2.patch("/tasks/t/contributions/c", { foo: 1 });
    expect(r.data.task_id).toBe("t");
  });

  test("apiV2.__raw exposes the underlying axios client", () => {
    expect(apiV2.__raw).toBe(api);
  });
});
