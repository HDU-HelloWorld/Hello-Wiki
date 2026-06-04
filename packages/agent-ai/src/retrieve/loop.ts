import type { ModelGatewayOptions } from "../utils/model-gateway.js";
import { createRetrieverAgent, type RetrieverAgentOptions } from "./agent.js";
import { createInsightClient, type InsightClient } from "./insight-client.js";
import {
  formatKickoffUserMessage,
  formatRoundUserMessage,
  formatTagTreeUserMessage,
  getLastAssistantText,
} from "./retriever-messages.js";
import {
  parseRetrieverDecision,
  pickRelevantHits,
  type RetrieveExcerpt,
  type RetrieveRequest,
  type RetrieveResponse,
  type RetrieveSessionRound,
  type SearchHit,
  type SearchQuery,
  type SearchRoundBundle,
} from "./schemas.js";
import {
  createRetrieveContextClient,
  type RetrieveContextClient,
} from "./retrieve-context-client.js";
import { createSearchClient, type SearchClient } from "./search-client.js";
import {
  appendRetrieveTrace,
  persistRetrieveSession,
  resolveRetrieverSession,
  type RetrieverSessionContext,
  type SessionStore,
} from "../utils/session-store.js";
import type { RetrieverDecision } from "./schemas.js";

export type RetrieverOptions = ModelGatewayOptions &
  RetrieverAgentOptions & {
    searchClient?: SearchClient;
    retrieveContextClient?: RetrieveContextClient;
    insightClient?: InsightClient;
    createRetrieverAgentFn?: typeof createRetrieverAgent;
    sessionStore?: SessionStore;
    sessionId?: string;
  };

/**
 * Retriever lifecycle:
 * 1. GET domains → kickoff LLM (selectedDomain, no tag tree)
 * 2. GET tag-tree for selectedDomain → second LLM (targetTags + plan)
 * 3. Python search per nextSearchQueries; loop with round results …
 */
export async function runRetriever(
  request: RetrieveRequest,
  options: RetrieverOptions = {},
): Promise<RetrieveResponse> {
  const createAgentFn = options.createRetrieverAgentFn ?? createRetrieverAgent;
  const agent = await createAgentFn(options);
  const searchClient =
    options.searchClient ??
    createSearchClient({
      workspaceId: request.workspaceId,
    });
  const retrieveContextClient =
    options.retrieveContextClient ??
    createRetrieveContextClient({
      workspaceId: request.workspaceId,
    });
  const insightClient = options.insightClient ?? createInsightClient();

  const hitPool = new Map<string, SearchHit>();
  const accumulated: SearchHit[] = [];
  const sessionRounds: RetrieveSessionRound[] = [];
  let activePlan: SearchQuery[] = [...request.searchQueries];
  let sufficient = false;
  let answerGuidance = "";
  let excerpts: RetrieveExcerpt[] = [];
  let promptRound = 0;
  let searchRound = 0;
  const maxSearchCycles = request.maxIterations ?? 8;
  const session = resolveRetrieverSession(request, options);

  await appendRetrieveTrace(session, "start", {
    question: request.question,
    contextSummary: request.contextSummary,
    questionRestatement: request.questionRestatement,
    searchQueries: request.searchQueries,
    maxIterations: maxSearchCycles,
    topK: request.topK,
  });

  const domainsResult = await retrieveContextClient.fetchDomains();
  await appendRetrieveTrace(session, "domains", {
    domainCount: domainsResult.domainCount,
    domains: domainsResult.domains,
  });
  await agent.prompt(await formatKickoffUserMessage(request, domainsResult));
  await agent.waitForIdle();
  promptRound += 1;

  let decision = parseRetrieverDecision(getLastAssistantText(agent));
  recordPromptRound(sessionRounds, {
    kind: "kickoff",
    promptRound,
    searchRound,
    decision,
  });
  await appendRetrieveTrace(session, "llm_kickoff", decisionTracePayload(decision));

  const selectedDomain = decision.selectedDomain?.trim();
  if (!selectedDomain) {
    return await completeRetriever(
      session,
      request,
      finalizeResponse({
        sufficient: false,
        decision,
        accumulated,
        activePlan,
        promptRound,
        sessionRounds,
        answerGuidance:
          "未能选定知识域（selectedDomain），请确认已执行 init_tags 或检查 domains 列表。",
      }),
      {},
    );
  }

  const { tagTree } = await retrieveContextClient.fetchTagTree(selectedDomain);
  await appendRetrieveTrace(session, "tag_tree", {
    domain: selectedDomain,
    tagTreeChars: tagTree.length,
    tagTreePreview: tagTree.slice(0, 500),
  });
  searchClient.setDomain(selectedDomain);

  await agent.prompt(
    await formatTagTreeUserMessage(
      request,
      selectedDomain,
      tagTree,
      resolveSearchPlan(decision, request.searchQueries),
    ),
  );
  await agent.waitForIdle();
  promptRound += 1;

  decision = parseRetrieverDecision(getLastAssistantText(agent));
  recordPromptRound(sessionRounds, {
    kind: "after_search",
    promptRound,
    searchRound,
    decision,
    bundle: undefined,
  });
  await appendRetrieveTrace(session, "llm_plan", {
    ...decisionTracePayload(decision),
    activePlan: resolveSearchPlan(decision, request.searchQueries),
  });

  if (decision.sufficient) {
    applyRelevantHits(accumulated, hitPool, decision);
    return await completeRetriever(
      session,
      request,
      finalizeResponse({
        sufficient: true,
        decision,
        accumulated,
        activePlan: resolveSearchPlan(decision, request.searchQueries),
        promptRound,
        sessionRounds,
      }),
      { selectedDomain, accumulatedPageIds: pageIdsFromHits(accumulated) },
    );
  }

  for (let cycle = 0; cycle < maxSearchCycles; cycle += 1) {
    activePlan = resolveSearchPlan(decision, request.searchQueries);
    if (activePlan.length === 0) {
      break;
    }

    const bundle = await executeSearchPlan(
      searchRound + 1,
      activePlan,
      request.topK!,
      searchClient,
      insightClient,
      accumulated.map((h) => h.pageId),
    );
    searchRound += 1;
    registerHits(hitPool, bundle.hits);
    await appendRetrieveTrace(session, "search_round", searchRoundTracePayload(searchRound, bundle));

    await agent.prompt(await formatRoundUserMessage(bundle));
    await agent.waitForIdle();
    promptRound += 1;

    decision = parseRetrieverDecision(getLastAssistantText(agent));
    recordPromptRound(sessionRounds, {
      kind: "after_search",
      promptRound,
      searchRound,
      bundle,
      decision,
    });
    await appendRetrieveTrace(session, "llm_round", {
      searchRound,
      ...decisionTracePayload(decision),
    });
    applyRelevantHits(accumulated, hitPool, decision);

    if (decision.sufficient) {
      sufficient = true;
      answerGuidance = decision.answerGuidance;
      excerpts =
        decision.excerpts.length > 0
          ? decision.excerpts
          : fallbackExcerpts(accumulated);
      break;
    }

    if (decision.nextSearchQueries.length === 0) {
      break;
    }
  }

  if (!sufficient) {
    answerGuidance =
      decision.answerGuidance ||
      "未检索到足够相关的知识，请尝试换个问法或补充文档。";
    excerpts =
      decision.excerpts.length > 0 ? decision.excerpts : fallbackExcerpts(accumulated);
  }

  return await completeRetriever(
    session,
    request,
    {
      sufficient,
      iterations: promptRound,
      answerGuidance,
      excerpts,
      searchQueries: activePlan,
      sessionRounds,
    },
    {
      selectedDomain,
      accumulatedPageIds: pageIdsFromHits(accumulated),
    },
  );
}

async function completeRetriever(
  session: RetrieverSessionContext,
  request: RetrieveRequest,
  response: RetrieveResponse,
  extra: { selectedDomain?: string; accumulatedPageIds?: string[] },
): Promise<RetrieveResponse> {
  await appendRetrieveTrace(session, "complete", {
    selectedDomain: extra.selectedDomain,
    sufficient: response.sufficient,
    iterations: response.iterations,
    excerptCount: response.excerpts.length,
    accumulatedPageIds: extra.accumulatedPageIds,
    sessionRounds: response.sessionRounds,
  });
  await persistRetrieveSession(session, {
    question: request.question,
    selectedDomain: extra.selectedDomain,
    sufficient: response.sufficient,
    iterations: response.iterations,
    excerptCount: response.excerpts.length,
    sessionRounds: response.sessionRounds,
    answerGuidance: response.answerGuidance,
    searchQueries: response.searchQueries,
    accumulatedPageIds: extra.accumulatedPageIds,
  });
  return response;
}

function decisionTracePayload(decision: RetrieverDecision): Record<string, unknown> {
  return {
    selectedDomain: decision.selectedDomain,
    sufficient: decision.sufficient,
    reason: decision.reason,
    analysis: decision.analysis,
    relevantPageIds: decision.relevantPageIds,
    nextSearchQueries: decision.nextSearchQueries,
    excerptCount: decision.excerpts.length,
  };
}

function searchRoundTracePayload(
  searchRound: number,
  bundle: SearchRoundBundle,
): Record<string, unknown> {
  return {
    searchRound,
    queries: bundle.queries.map((q) => ({
      query: q.query,
      targetTags: q.targetTags,
      purpose: q.purpose,
    })),
    hitCount: bundle.hits.length,
    degraded: bundle.degraded,
    hits: bundle.hits.map((h) => ({
      pageId: h.pageId,
      score: h.score,
      title: h.title,
      tagPaths: h.tagPaths,
    })),
  };
}

function pageIdsFromHits(hits: SearchHit[]): string[] {
  return hits.map((hit) => hit.pageId);
}

function resolveSearchPlan(
  decision: ReturnType<typeof parseRetrieverDecision>,
  fallback: SearchQuery[],
): SearchQuery[] {
  if (decision.nextSearchQueries.length > 0) {
    return decision.nextSearchQueries;
  }
  return fallback;
}

/** @deprecated Use runRetriever */
export const runRetrieveSubAgent = runRetriever;

/** @deprecated Use RetrieverOptions */
export type RetrieveSubAgentOptions = RetrieverOptions;

async function executeSearchPlan(
  roundIndex: number,
  queries: SearchQuery[],
  topK: number,
  searchClient: SearchClient,
  insightClient: InsightClient,
  excludePageIds: string[],
): Promise<SearchRoundBundle> {
  const hits: SearchHit[] = [];
  const degraded = new Set<string>();

  const perQueryResults = await Promise.all(
    queries.map(async (query) => {
      const [slowResult, fastResult] = await Promise.all([
        searchClient.search(query, topK, excludePageIds),
        insightClient.search(query, topK),
      ]);
      return { slowResult, fastResult };
    }),
  );

  for (const { slowResult, fastResult } of perQueryResults) {
    mergeHits(hits, slowResult.hits);
    for (const tag of slowResult.degraded) {
      degraded.add(tag);
    }
    if (!fastResult.skipped && fastResult.hits.length > 0) {
      mergeHits(hits, fastResult.hits);
    }
  }

  return {
    roundIndex,
    queries,
    hits,
    degraded: [...degraded],
  };
}

function registerHits(pool: Map<string, SearchHit>, hits: SearchHit[]): void {
  for (const hit of hits) {
    pool.set(hit.pageId, hit);
  }
}

function applyRelevantHits(
  accumulated: SearchHit[],
  pool: Map<string, SearchHit>,
  decision: ReturnType<typeof parseRetrieverDecision>,
): void {
  mergeHits(accumulated, pickRelevantHits(pool, decision.relevantPageIds));
}

function recordPromptRound(
  sessionRounds: RetrieveSessionRound[],
  input: {
    kind: "kickoff" | "after_search";
    promptRound: number;
    searchRound: number;
    bundle?: SearchRoundBundle;
    decision: ReturnType<typeof parseRetrieverDecision>;
  },
): void {
  sessionRounds.push({
    step: input.searchRound,
    promptRound: input.promptRound,
    kind: input.kind,
    searchQueryCount: input.bundle?.queries.length ?? 0,
    roundHitCount: input.bundle?.hits.length ?? 0,
    relevantCount: input.decision.relevantPageIds.length,
    analysis: input.decision.analysis,
    sufficient: input.decision.sufficient,
    planRevised: input.decision.nextSearchQueries.length > 0,
  });
}

function finalizeResponse(input: {
  sufficient: boolean;
  decision: ReturnType<typeof parseRetrieverDecision>;
  accumulated: SearchHit[];
  activePlan: SearchQuery[];
  promptRound: number;
  sessionRounds: RetrieveSessionRound[];
  answerGuidance?: string;
}): RetrieveResponse {
  return {
    sufficient: input.sufficient,
    iterations: input.promptRound,
    answerGuidance:
      input.answerGuidance ??
      input.decision.answerGuidance ??
      "已整理检索结果，请结合 excerpts 回答用户。",
    excerpts:
      input.decision.excerpts.length > 0
        ? input.decision.excerpts
        : fallbackExcerpts(input.accumulated),
    searchQueries: input.activePlan,
    sessionRounds: input.sessionRounds,
  };
}

function fallbackExcerpts(hits: SearchHit[]): RetrieveExcerpt[] {
  return hits.map((hit) => ({
    pageId: hit.pageId,
    title: hit.title ?? "",
    compiledTruth: hit.compiledTruth,
    originalText: hit.originalText ?? "",
    summary: hit.summary ?? "",
    relevance: "检索子智能体收录的相关证据",
  }));
}

function mergeHits(target: SearchHit[], incoming: SearchHit[]): void {
  const seen = new Set(target.map((hit) => hit.pageId));
  for (const hit of incoming) {
    if (seen.has(hit.pageId)) continue;
    seen.add(hit.pageId);
    target.push(hit);
  }
}
