/**
 * Main Agent tool registry.
 * Retrieve isolation: see packages/agent-ai/README.md §「主 Agent / Retriever 隔离原则」.
 * Do not add domain, tagTree, targetTags, or pageId to the retrieve tool schema.
 */
import type { AgentTool } from "@earendil-works/pi-agent-core";
import { Type } from "@earendil-works/pi-ai";

import { DEFAULT_WORKSPACE_ID } from "../../retrieve/retrieve-context-client.js";
import { runRetriever } from "../../retrieve/loop.js";
import { parseRetrieveRequest, type RetrieveResponse } from "../../retrieve/schemas.js";
export type ToolRegistryOptions = {
  pythonApiBaseUrl?: string;
  workspaceId?: string;
  sessionId?: string;
};

const DEFAULT_PYTHON_API_BASE_URL = "http://127.0.0.1:8000";

function summarizeRetrieveForMainAgent(result: RetrieveResponse) {
  return {
    sufficient: result.sufficient,
    excerptCount: result.excerpts.length,
  };
}

export function buildAgentTools(options: ToolRegistryOptions = {}): AgentTool[] {
  const pythonApiBaseUrl =
    options.pythonApiBaseUrl ??
    process.env.AGENT_AI_PYTHON_API_BASE_URL ??
    DEFAULT_PYTHON_API_BASE_URL;
  const workspaceId =
    options.workspaceId ??
    process.env.AGENT_AI_WORKSPACE_ID ??
    DEFAULT_WORKSPACE_ID;
  const sessionId = options.sessionId;

  return [
    {
      name: "init_tags",
      label: "Initialize Tags",
      description:
        "Initialize and persist the domain tag taxonomy through the Python fixed workflow.",
      parameters: Type.Object({
        domain: Type.String({
          minLength: 1,
          description: "Domain id, for example general or university_policy.",
        }),
        description: Type.String({
          minLength: 1,
          description: "Natural language description of the knowledge domain.",
        }),
        language: Type.Optional(
          Type.String({
            description: "Primary language for generated labels. Defaults to zh.",
          }),
        ),
      }),
      executionMode: "sequential",
      execute: async (_toolCallId, params, signal, onUpdate) => {
        const payload = coerceInitTagsParams(params);
        onUpdate?.({
          content: [{ type: "text", text: "正在初始化标签体系..." }],
          details: payload,
        });

        const response = await fetch(`${pythonApiBaseUrl}/api/v1/init/tags`, {
          method: "POST",
          headers: {
            "content-type": "application/json",
            "x-workspace-id": workspaceId,
          },
          body: JSON.stringify(payload),
          signal,
        });

        if (!response.ok) {
          const body = await response.text();
          throw new Error(`init_tags failed: ${response.status} ${body}`);
        }

        const result = (await response.json()) as unknown;
        return {
          content: [
            {
              type: "text",
              text: `标签初始化完成：${JSON.stringify(result)}`,
            },
          ],
          details: result,
        };
      },
    },
    {
      name: "retrieve",
      label: "Retrieve Knowledge",
      description:
        "Run the Retriever sub-agent. Provide contextSummary, questionRestatement, and searchQueries (sub-questions) only (no domain or tag paths). Retriever loads DB catalog internally and returns answer guidance plus excerpts.",
      parameters: Type.Object({
        question: Type.String({
          minLength: 1,
          description: "User question (short form; also supply questionRestatement).",
        }),
        contextSummary: Type.String({
          description:
            "Brief summary of conversation context relevant to this retrieval (topic, constraints, prior turns).",
        }),
        questionRestatement: Type.String({
          minLength: 1,
          description:
            "Precise restatement of what the user wants to know, disambiguated using context.",
        }),
        searchQueries: Type.Array(
          Type.Object({
            query: Type.String({
              minLength: 1,
              description:
                "One decomposed sub-question for semantic/vector search (not a compound question).",
            }),
            purpose: Type.Optional(
              Type.String({
                description: "Why this statement was split out; helps the Retriever.",
              }),
            ),
          }),
          { minItems: 1 },
        ),
      }),
      executionMode: "sequential",
      execute: async (_toolCallId, params, _signal, onUpdate) => {
        const payload = coerceRetrieveParams(params);
        onUpdate?.({
          content: [{ type: "text", text: "正在检索知识库..." }],
          details: { question: payload.question },
        });

        const result = await runRetriever(
          parseRetrieveRequest({ ...payload, workspaceId, sessionId }),
          { sessionId },
        );

        return {
          content: [
            {
              type: "text",
              text: [
                `检索完成（充分性：${result.sufficient ? "是" : "否"}）。`,
                result.answerGuidance,
                result.excerpts.length
                  ? `引用片段数：${result.excerpts.length}`
                  : "未找到可用引用片段。",
              ].join("\n"),
            },
          ],
          details: summarizeRetrieveForMainAgent(result),
        };
      },
    },
  ];
}

function coerceRetrieveParams(params: unknown): {
  question: string;
  contextSummary: string;
  questionRestatement: string;
  searchQueries: unknown;
} {
  if (typeof params !== "object" || params === null || Array.isArray(params)) {
    throw new Error("retrieve params must be an object");
  }
  const record = params as Record<string, unknown>;
  const question = requireString(record.question, "question");
  return {
    question,
    contextSummary:
      typeof record.contextSummary === "string" ? record.contextSummary.trim() : "",
    questionRestatement:
      typeof record.questionRestatement === "string" && record.questionRestatement.trim()
        ? record.questionRestatement.trim()
        : question,
    searchQueries: record.searchQueries,
  };
}

function coerceInitTagsParams(params: unknown) {
  if (typeof params !== "object" || params === null || Array.isArray(params)) {
    throw new Error("init_tags params must be an object");
  }
  const record = params as Record<string, unknown>;
  return {
    domain: requireString(record.domain, "domain"),
    description: requireString(record.description, "description"),
    language:
      typeof record.language === "string" && record.language.trim()
        ? record.language
        : "zh",
  };
}

function requireString(value: unknown, field: string): string {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${field} must be a non-empty string`);
  }
  return value;
}
