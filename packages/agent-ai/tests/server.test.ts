import { test } from "node:test";
import assert from "node:assert/strict";
import type { AddressInfo } from "node:net";

import { createAgentAiServer, type AgentRunner, type Extractor, type TagInitializer, type RetrieveRunner } from "../src/server.js";
import type { RetrieveResponse } from "../src/retrieve/schemas.js";

async function withServer<T>(
  options: {
    agentRunner?: AgentRunner;
    extractor?: Extractor;
    tagInitializer?: TagInitializer;
    retrieveRunner?: RetrieveRunner;
  },
  fn: (baseUrl: string) => Promise<T>,
): Promise<T> {
  const server = createAgentAiServer(options);
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address() as AddressInfo | null;
  assert(address);
  try {
    return await fn(`http://127.0.0.1:${address.port}`);
  } finally {
    await new Promise<void>((resolve, reject) => {
      server.close((error) => (error ? reject(error) : resolve()));
    });
  }
}

test("serves health checks", async () => {
  await withServer({}, async (baseUrl) => {
    const response = await fetch(`${baseUrl}/health`);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { status: "ok", service: "agent-ai" });
  });
});

test("serves agent chat over HTTP", async () => {
  await withServer(
    {
      agentRunner: async (request) => {
        assert.deepEqual(request, {
          message: "你好",
          sessionId: "session-1",
          workspaceId: "workspace-1",
          history: [{ role: "user", content: "之前的问题" }],
        });
        return { reply: "Hello from agent", sessionId: "session-1" };
      },
    },
    async (baseUrl) => {
      const response = await fetch(`${baseUrl}/agent/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          message: "你好",
          sessionId: "session-1",
          workspaceId: "workspace-1",
          history: [{ role: "user", content: "之前的问题" }],
        }),
      });

      assert.equal(response.status, 200);
      assert.deepEqual(await response.json(), {
        reply: "Hello from agent",
        sessionId: "session-1",
      });
    },
  );
});

test("serves ingest extract and init-tags routes", async () => {
  await withServer(
    {
      extractor: async () => ({
        chunk_summary: "summary",
        page_title: "title",
        compiled_truth: "truth",
        suggested_tags: [
          { name: "registration_course", label: "选课注册", parent_hint: "functional_area" },
          { name: "academic_affairs", label: "教务管理", parent_hint: "functional_area" },
        ],
        effective_range: {
          start: null,
          end: null,
          description: "No dates",
          stale_risk: "unknown",
        },
      }),
      tagInitializer: async () => ({
        domain: "general",
        generated_at: "2026-05-25T00:00:00.000Z",
        categories: [],
      }),
    },
    async (baseUrl) => {
      const extractResponse = await fetch(`${baseUrl}/extract`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          domain: "general",
          chunkText: "content",
          tagTree: "functional_area",
          sourceDocument: "policy.txt",
          sourcePage: "",
          chunkIndex: 0,
          totalChunks: 1,
        }),
      });
      assert.equal(extractResponse.status, 200);

      const initResponse = await fetch(`${baseUrl}/init-tags`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          domain: "general",
          description: "university policies",
          language: "zh",
        }),
      });
      assert.equal(initResponse.status, 200);
    },
  );
});

test("serves retrieve route", async () => {
  await withServer(
    {
      retrieveRunner: async (payload) => {
        const request = payload as { question: string };
        return {
          sufficient: true,
          iterations: 1,
          answerGuidance: `guidance for ${request.question}`,
          excerpts: [],
          searchQueries: [],
          sessionRounds: [],
        } satisfies RetrieveResponse;
      },
    },
    async (baseUrl) => {
      const response = await fetch(`${baseUrl}/retrieve`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          question: "辅修选课流程是什么？",
          workspaceId: "00000000-0000-0000-0000-000000000001",
          contextSummary: "选课咨询",
          questionRestatement: "辅修选课流程与条件",
          searchQueries: [{ query: "辅修选课流程与条件" }],
        }),
      });

      assert.equal(response.status, 200);
      const payload = (await response.json()) as RetrieveResponse;
      assert.match(payload.answerGuidance, /辅修选课流程/);
    },
  );
});

test("returns JSON errors for agent failures", async () => {
  await withServer(
    {
      agentRunner: async () => {
        throw new Error("bad agent");
      },
    },
    async (baseUrl) => {
      const response = await fetch(`${baseUrl}/agent/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ message: "hello" }),
      });

      assert.equal(response.status, 500);
      assert.deepEqual(await response.json(), { error: "bad agent" });
    },
  );
});
