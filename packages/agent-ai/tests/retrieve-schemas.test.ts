import { test } from "node:test";
import assert from "node:assert/strict";

import {
  parseRetrieveRequest,
  parseRetrieverDecision,
  pickRelevantHits,
} from "../src/retrieve/schemas.js";
import type { SearchHit } from "../src/retrieve/schemas.js";

test("parseRetrieveRequest requires searchQueries", () => {
  assert.throws(
    () =>
      parseRetrieveRequest({
        question: "q",
        workspaceId: "ws-1",
      }),
    /searchQueries/,
  );
});

test("parseRetrieveRequest does not require domain", () => {
  const request = parseRetrieveRequest({
    question: "去年投诉与改进？",
    contextSummary: "2025商城客服",
    questionRestatement: "投诉TOP3及改进措施",
    workspaceId: "ws-1",
    searchQueries: [{ query: "2025年商城投诉排名前三" }],
  });

  assert.equal(request.question, "去年投诉与改进？");
  assert.equal(request.maxIterations, 8);
  assert.equal("domain" in request, false);
});

test("parseRetrieverDecision parses selectedDomain and nextSearchQueries", () => {
  const pool = new Map<string, SearchHit>([
    [
      "page-1",
      {
        pageId: "page-1",
        score: 1,
        title: "t",
        compiledTruth: "c",
        summary: "s",
        originalText: "o",
        tagPaths: [],
      },
    ],
  ]);

  const decision = parseRetrieverDecision(
    JSON.stringify({
      relevantPageIds: ["page-1"],
      sufficient: true,
      reason: "done",
      selectedDomain: "university_policy",
      nextSearchQueries: [],
      answerGuidance: "guidance",
      excerpts: [
        {
          pageId: "page-1",
          title: "t",
          compiledTruth: "c",
          originalText: "o",
          summary: "s",
          relevance: "r",
        },
      ],
    }),
  );

  assert.equal(decision.sufficient, true);
  assert.equal(decision.selectedDomain, "university_policy");
  assert.equal(pickRelevantHits(pool, decision.relevantPageIds).length, 1);
  assert.equal(decision.answerGuidance, "guidance");
});
