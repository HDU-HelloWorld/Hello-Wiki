import type { Agent } from "@earendil-works/pi-agent-core";

import { contentToText } from "../utils/content.js";
import { loadPrompt } from "../utils/prompt-loader.js";
import type { RetrieveDomainsResult } from "./retrieve-context-client.js";
import type {
  RetrieveRequest,
  SearchHit,
  SearchQuery,
  SearchRoundBundle,
} from "./schemas.js";

const INITIAL_ANALYSIS_HINT =
  "请从可用知识域中选择 selectedDomain，审视主 Agent 的分解是否覆盖问题要点、措辞是否利于向量检索。";

const TAG_TREE_ANALYSIS_HINT =
  "请结合下方标签树审视分解是否覆盖问题要点，为 nextSearchQueries 填写 targetTags（路径不含 domain 前缀），必要时重写检索陈述句。";

const ROUND_ANALYSIS_HINT =
  "请根据本轮召回评估：是否需改写子问题、是否遗漏信息维度、累计证据是否已能回答用户问题。";

export function formatDomainsCatalog(domainsResult: RetrieveDomainsResult): string {
  if (domainsResult.domains.length === 0) {
    return "（无可用 domain）";
  }
  return domainsResult.domains
    .map((d) => `${d.id}${d.label !== d.id ? ` — ${d.label}` : ""}`)
    .join("\n");
}

export function formatSearchPlan(searchQueries: SearchQuery[]): string {
  return searchQueries
    .map((item, index) => {
      const purpose = item.purpose ? `；意图：${item.purpose}` : "";
      const tags =
        item.targetTags.length > 0 ? `；标签：${item.targetTags.join(", ")}` : "";
      return `${index + 1}. ${item.query}${purpose}${tags}`;
    })
    .join("\n");
}

export function formatHitsForRetriever(hits: SearchHit[]): string {
  if (hits.length === 0) {
    return "（本轮无召回）";
  }
  return hits
    .map(
      (hit) =>
        `- pageId=${hit.pageId}; title=${hit.title ?? "无标题"}; tags=${hit.tagPaths.join(", ") || "无"}; summary=${(hit.summary ?? hit.compiledTruth).slice(0, 300)}`,
    )
    .join("\n");
}

/** Kickoff user turn: domains only (no tag tree yet). */
export async function formatKickoffUserMessage(
  request: RetrieveRequest,
  domainsResult: RetrieveDomainsResult,
): Promise<string> {
  const dbCatalog = [
    `可用知识域（共 ${domainsResult.domainCount} 个）：`,
    formatDomainsCatalog(domainsResult),
  ].join("\n");

  const { user } = await loadPrompt("retriever.user_initial", {
    contextSummary: request.contextSummary || "（未提供）",
    questionRestatement: request.questionRestatement,
    question: request.question,
    dbCatalog,
    suggestedSearchPlan: formatSearchPlan(request.searchQueries),
    analysisHint: INITIAL_ANALYSIS_HINT,
  });
  if (user?.trim()) {
    return user;
  }

  return [
    "## 任务参数",
    `对话语境：${request.contextSummary || "（未提供）"}`,
    `用户问题（精准转述）：${request.questionRestatement}`,
    `用户原话：${request.question}`,
    "",
    "## 工作区知识域（PostgreSQL / 后端接口）",
    dbCatalog,
    "",
    "## 主 Agent 建议的检索分解",
    formatSearchPlan(request.searchQueries),
    "",
    INITIAL_ANALYSIS_HINT,
  ].join("\n");
}

/** Second user turn after selectedDomain: inject tag tree before first search. */
export async function formatTagTreeUserMessage(
  request: RetrieveRequest,
  selectedDomain: string,
  tagTree: string,
  suggestedPlan: SearchQuery[],
): Promise<string> {
  const tagTreeText = tagTree.trim() || "（未从后端加载到标签树）";

  const { user } = await loadPrompt("retriever.user_tag_tree", {
    selectedDomain,
    tagTree: tagTreeText,
    suggestedSearchPlan: formatSearchPlan(suggestedPlan),
    analysisHint: TAG_TREE_ANALYSIS_HINT,
  });
  if (user?.trim()) {
    return user;
  }

  return [
    "## 已选定知识域",
    selectedDomain,
    "",
    "## 标签树",
    tagTreeText,
    "",
    "## 主 Agent 建议的检索分解",
    formatSearchPlan(suggestedPlan),
    "",
    TAG_TREE_ANALYSIS_HINT,
  ].join("\n");
}

/** Loop user turn: round N search results + iteration analysis hint. */
export async function formatRoundUserMessage(bundle: SearchRoundBundle): Promise<string> {
  const degradedLine =
    bundle.degraded.length > 0 ? `降级说明：${bundle.degraded.join(", ")}` : "";

  const { user } = await loadPrompt("retriever.user_round", {
    roundIndex: String(bundle.roundIndex),
    executedPlan: formatSearchPlan(bundle.queries),
    hits: formatHitsForRetriever(bundle.hits),
    degradedLine,
    analysisHint: ROUND_ANALYSIS_HINT,
  });
  if (user?.trim()) {
    return user;
  }

  return [
    `## 第 ${bundle.roundIndex} 轮检索结果`,
    "本轮执行的子问题：",
    formatSearchPlan(bundle.queries),
    "",
    formatHitsForRetriever(bundle.hits),
    degradedLine,
    "",
    ROUND_ANALYSIS_HINT,
  ].join("\n");
}

/** @deprecated Use formatKickoffUserMessage with RetrieveDomainsResult. */
export async function formatInitialUserMessage(
  request: RetrieveRequest,
  _bundle: SearchRoundBundle,
  dbContext?: { domains: string[]; domainCount: number; tagTree: string },
): Promise<string> {
  const domainsResult = {
    domains: (dbContext?.domains ?? []).map((id) => ({
      id,
      label: id,
      initialized: true,
    })),
    domainCount: dbContext?.domainCount ?? 0,
  };
  return formatKickoffUserMessage(request, domainsResult);
}

export function getLastAssistantText(agent: Agent): string {
  const assistant = [...agent.state.messages]
    .reverse()
    .find((message) => message.role === "assistant");
  if (!assistant) {
    throw new Error("Retriever agent did not produce an assistant reply");
  }
  return contentToText(assistant.content);
}
