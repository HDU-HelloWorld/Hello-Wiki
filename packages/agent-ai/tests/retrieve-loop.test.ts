import { test } from "node:test";
import assert from "node:assert/strict";
import { Agent } from "@earendil-works/pi-agent-core";

import { runRetriever } from "../src/retrieve/loop.js";
import type { SearchClient } from "../src/retrieve/search-client.js";

const baseRequest = {
  question: "辅修选课流程是什么？",
  contextSummary: "用户在咨询教务处学籍与选课政策。",
  questionRestatement: "用户想了解辅修专业的选课流程与申请条件。",
  workspaceId: "00000000-0000-0000-0000-000000000001",
  topK: 5,
};

const mockRetrieveContextClient = {
  async fetchDomains() {
    return {
      domains: [{ id: "general", label: "general", initialized: true }],
      domainCount: 1,
    };
  },
  async fetchTagTree(domain: string) {
    return {
      domain,
      tagTree: "functional_area.registration\nfunctional_area.exam",
    };
  },
};

function mockRetrieverAgent(responses: string[]): () => Promise<Agent> {
  let index = 0;
  return async () => {
    const agent = new Agent({
      initialState: {
        systemPrompt: "test",
        model: "mock" as never,
        thinkingLevel: "off",
        tools: [],
        messages: [],
      },
      convertToLlm: (messages) =>
        messages.filter((m) => m.role === "user" || m.role === "assistant"),
      transformContext: async (messages) => messages,
      getApiKey: async () => "test-key",
    });

    agent.prompt = async (input) => {
      const text =
        typeof input === "string"
          ? input
          : Array.isArray(input)
            ? ""
            : "";
      agent.state.messages.push({
        role: "user",
        content: [{ type: "text", text }],
        timestamp: Date.now(),
      });
      const reply = responses[index] ?? responses[responses.length - 1]!;
      index += 1;
      agent.state.messages.push({
        role: "assistant",
        content: [{ type: "text", text: reply }],
        timestamp: Date.now(),
        api: "openai-responses",
        provider: "openai",
        model: "mock",
        usage: {
          input: 0,
          output: 0,
          cacheRead: 0,
          cacheWrite: 0,
          totalTokens: 0,
          cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 },
        },
        stopReason: "stop",
      });
    };

    return agent;
  };
}

test("runRetriever kickoff, tag-tree, search, then feedback", async () => {
  const userMessages: string[] = [];
  let searchCalls = 0;
  const searchClient: SearchClient = {
    setDomain() {},
    async search() {
      searchCalls += 1;
      return {
        hits: [
          {
            pageId: "page-1",
            score: 0.9,
            title: "辅修说明",
            compiledTruth: "truth",
            summary: "summary",
            tagPaths: [],
          },
        ],
        degraded: [],
      };
    },
  };

  const agentFactory = mockRetrieverAgent([
    JSON.stringify({
      relevantPageIds: [],
      sufficient: false,
      reason: "pick domain",
      selectedDomain: "general",
      nextSearchQueries: [{ query: "辅修选课流程与条件", targetTags: [] }],
      answerGuidance: "",
      excerpts: [],
    }),
    JSON.stringify({
      relevantPageIds: [],
      sufficient: false,
      reason: "plan with tags",
      selectedDomain: "general",
      nextSearchQueries: [
        { query: "辅修选课流程与条件", targetTags: ["functional_area.registration"] },
      ],
      answerGuidance: "",
      excerpts: [],
    }),
    JSON.stringify({
      relevantPageIds: ["page-1"],
      sufficient: true,
      reason: "enough",
      selectedDomain: "general",
      nextSearchQueries: [],
      answerGuidance: "可以直接回答",
      excerpts: [],
    }),
  ]);

  const createRetrieverAgentFn = async () => {
    const agent = await agentFactory();
    const originalPrompt = agent.prompt.bind(agent);
    agent.prompt = async (input) => {
      if (typeof input === "string") {
        userMessages.push(input);
        return originalPrompt(input);
      }
      return originalPrompt(input);
    };
    return agent;
  };

  const result = await runRetriever(
    {
      ...baseRequest,
      searchQueries: [{ query: "主Agent建议句", targetTags: [] }],
      maxIterations: 4,
    },
    {
      createRetrieverAgentFn,
      searchClient,
      retrieveContextClient: mockRetrieveContextClient,
    },
  );

  assert.equal(result.sufficient, true);
  assert.equal(searchCalls, 1);
  assert.equal(userMessages.length, 3);
  assert.match(userMessages[0]!, /知识域/);
  assert.doesNotMatch(userMessages[0]!, /pageId=/);
  assert.match(userMessages[1]!, /标签树/);
  assert.match(userMessages[2]!, /第 1 轮检索结果/);
  assert.equal(result.sessionRounds[0]?.kind, "kickoff");
});

test("runRetriever uses kickoff plan then revised plan on second cycle", async () => {
  const queries: string[] = [];
  const searchClient: SearchClient = {
    setDomain() {},
    async search(searchQuery) {
      queries.push(searchQuery.query);
      return {
        hits: [
          {
            pageId: `page-${queries.length}`,
            score: 0.5,
            title: "doc",
            compiledTruth: "truth",
            summary: "s",
            tagPaths: [],
          },
        ],
        degraded: [],
      };
    },
  };

  const result = await runRetriever(
    {
      ...baseRequest,
      searchQueries: [{ query: "主Agent初稿", targetTags: [] }],
      maxIterations: 6,
    },
    {
      createRetrieverAgentFn: mockRetrieverAgent([
        JSON.stringify({
          relevantPageIds: [],
          sufficient: false,
          selectedDomain: "general",
          nextSearchQueries: [{ query: "首轮子问题", targetTags: [] }],
          answerGuidance: "",
          excerpts: [],
        }),
        JSON.stringify({
          relevantPageIds: [],
          sufficient: false,
          nextSearchQueries: [{ query: "首轮子问题", targetTags: [] }],
          answerGuidance: "",
          excerpts: [],
        }),
        JSON.stringify({
          relevantPageIds: [],
          sufficient: false,
          nextSearchQueries: [{ query: "优化后子问题", targetTags: [] }],
          answerGuidance: "",
          excerpts: [],
        }),
        JSON.stringify({
          relevantPageIds: ["page-2"],
          sufficient: true,
          nextSearchQueries: [],
          answerGuidance: "完成",
          excerpts: [],
        }),
      ]),
      searchClient,
      retrieveContextClient: mockRetrieveContextClient,
    },
  );

  assert.equal(result.sufficient, true);
  assert.equal(queries[0], "首轮子问题");
  assert.equal(queries[1], "优化后子问题");
});
