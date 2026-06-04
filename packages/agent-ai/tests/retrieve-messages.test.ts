import { test } from "node:test";
import assert from "node:assert/strict";

import {
  formatKickoffUserMessage,
  formatRoundUserMessage,
} from "../src/retrieve/retriever-messages.js";

const baseRequest = {
  question: "原话",
  contextSummary: "语境",
  questionRestatement: "转述",
  workspaceId: "ws",
  searchQueries: [{ query: "子问题一", targetTags: [] }],
};

const mockDomainsResult = {
  domains: [
    { id: "general", label: "general", initialized: true },
    { id: "university_policy", label: "校规", initialized: false },
  ],
  domainCount: 2,
};

test("formatKickoffUserMessage has domains catalog without search results", async () => {
  const text = await formatKickoffUserMessage(baseRequest, mockDomainsResult);

  assert.match(text, /工作区知识域|知识域/);
  assert.match(text, /general/);
  assert.doesNotMatch(text, /第 1 轮检索结果/);
  assert.doesNotMatch(text, /pageId=/);
  assert.doesNotMatch(text, /^## 标签树/m);
});

test("formatRoundUserMessage only adds search results and iteration hint", async () => {
  const text = await formatRoundUserMessage({
    roundIndex: 1,
    queries: [{ query: "子问题二", targetTags: ["tag.a"] }],
    hits: [],
    degraded: ["time_channel_skipped"],
  });

  assert.match(text, /第 1 轮检索结果/);
  assert.match(text, /子问题二/);
  assert.doesNotMatch(text, /^## 工作区知识库目录/m);
  assert.doesNotMatch(text, /^## 任务参数/m);
});
