/**
 * Phase 3.2 — apiV2 + resolveOperationId smoke tests.
 *
 * These pin the (method, url) → operationId resolver against the
 * committed OpenAPI snapshot so future codegen drift is caught.
 */
import { resolveOperationId } from "../lib/api/resolveOperation";

describe("Phase 3.2 — resolveOperationId", () => {
  test("matches a literal path: GET /chat/models", () => {
    const opid = resolveOperationId("get", "/chat/models");
    expect(opid).toBeTruthy();
    expect(opid).toMatch(/chat.*models/i);
  });

  test("matches a templated path: GET /contexts/abc-123/documents", () => {
    const opid = resolveOperationId("get", "/contexts/abc-123/documents");
    expect(opid).toBeTruthy();
    expect(opid).toMatch(/list.*documents/i);
  });

  test("matches deep templated path: GET /contexts/c1/documents/d2/paragraphs", () => {
    const opid = resolveOperationId(
      "get",
      "/contexts/c1/documents/d2/paragraphs"
    );
    expect(opid).toBeTruthy();
  });

  test("matches a POST path: POST /chats/{chat_id}/attach", () => {
    const opid = resolveOperationId("post", "/chats/xyz/attach");
    expect(opid).toBeTruthy();
  });

  test("matches DELETE on /contexts/{cid}/documents/{doc_id}", () => {
    const opid = resolveOperationId(
      "delete",
      "/contexts/c1/documents/d1"
    );
    expect(opid).toBeTruthy();
  });

  test("tolerates query strings", () => {
    const opid = resolveOperationId(
      "get",
      "/contexts/c1/documents?limit=10&cursor=abc"
    );
    expect(opid).toBeTruthy();
  });

  test("tolerates already-prefixed /api/ URLs", () => {
    const opid = resolveOperationId("get", "/api/chat/models");
    expect(opid).toBeTruthy();
  });

  test("returns null for a fully unknown URL", () => {
    const opid = resolveOperationId("get", "/this/does/not/exist/anywhere");
    expect(opid).toBeNull();
  });

  test("returns null for method-mismatch on a known path", () => {
    // /chat/models is GET-only; POST should not match.
    const opid = resolveOperationId("post", "/chat/models");
    expect(opid).toBeNull();
  });
});
