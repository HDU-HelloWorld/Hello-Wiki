export type TimeRange = {
  start?: string;
  end?: string;
};

/** One decomposed sub-question for semantic / vector search (from main Agent tool params). */
export type SearchQuery = {
  query: string;
  targetTags: string[];
  timeRange?: TimeRange;
  purpose?: string;
};

export type RetrieveRequest = {
  question: string;
  contextSummary: string;
  questionRestatement: string;
  workspaceId: string;
  /** File stem under data/retriever-sessions; main Agent passes its sessionId for correlation. */
  sessionId?: string;
  searchQueries: SearchQuery[];
  /** Max retriever agent.prompt rounds (including first analysis). Default 8. */
  maxIterations?: number;
  topK?: number;
};

export type RetrieveSessionRound = {
  step: number;
  promptRound: number;
  kind: "kickoff" | "after_search";
  searchQueryCount: number;
  roundHitCount: number;
  relevantCount: number;
  analysis?: string;
  sufficient: boolean;
  planRevised: boolean;
  selectedDomain?: string;
  searchQueries?: SearchQuery[];
  nextSearchQueries?: SearchQuery[];
  degraded?: string[];
  reason?: string;
};

export type RetrieverDecision = {
  relevantPageIds: string[];
  sufficient: boolean;
  reason: string;
  analysis?: string;
  /** Chosen on kickoff from workspace catalog; Retriever-only. */
  selectedDomain?: string;
  nextSearchQueries: SearchQuery[];
  answerGuidance: string;
  excerpts: RetrieveExcerpt[];
};

/** @deprecated Use RetrieverDecision */
export type JudgeRoundResult = {
  relevantHits: SearchHit[];
  sufficient: boolean;
  reason: string;
  analysis?: string;
  revisedSearchQueries?: SearchQuery[];
};

export type RetrieveExcerpt = {
  pageId: string;
  title: string;
  compiledTruth: string;
  originalText: string;
  summary: string;
  relevance: string;
};

export type RetrieveResponse = {
  sufficient: boolean;
  iterations: number;
  answerGuidance: string;
  excerpts: RetrieveExcerpt[];
  searchQueries: SearchQuery[];
  sessionRounds: RetrieveSessionRound[];
};

export type SearchHit = {
  pageId: string;
  score: number;
  title: string | null;
  compiledTruth: string;
  summary: string | null;
  originalText?: string;
  tagPaths: string[];
};

export type SearchResponse = {
  hits: SearchHit[];
  degraded: string[];
};

export type SearchRoundBundle = {
  roundIndex: number;
  queries: SearchQuery[];
  hits: SearchHit[];
  degraded: string[];
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requireString(value: unknown, field: string, allowEmpty = false): string {
  if (typeof value !== "string") {
    throw new Error(`Invalid retrieve request: ${field} must be a string`);
  }
  if (!allowEmpty && value.trim() === "") {
    throw new Error(`Invalid retrieve request: ${field} must not be empty`);
  }
  return value;
}

export function parseSearchQueries(value: unknown, options?: { allowEmpty?: boolean }): SearchQuery[] {
  if (!Array.isArray(value)) {
    throw new Error("searchQueries must be an array");
  }
  if (value.length === 0 && !options?.allowEmpty) {
    throw new Error("Invalid retrieve request: searchQueries must be a non-empty array");
  }

  return value.map((item, index) => {
    if (!isRecord(item)) {
      throw new Error(`searchQueries[${index}] must be an object`);
    }

    const legacyQuery =
      typeof item.query === "string"
        ? item.query
        : typeof item.sanitizeQueryForPrompt === "string"
          ? item.sanitizeQueryForPrompt
          : undefined;

    const timeRange = isRecord(item.timeRange)
      ? {
          start: typeof item.timeRange.start === "string" ? item.timeRange.start : undefined,
          end: typeof item.timeRange.end === "string" ? item.timeRange.end : undefined,
        }
      : undefined;

    return {
      query: requireString(legacyQuery, `searchQueries[${index}].query`, false),
      targetTags: Array.isArray(item.targetTags)
        ? item.targetTags.filter((tag): tag is string => typeof tag === "string")
        : [],
      timeRange,
      purpose:
        typeof item.purpose === "string" && item.purpose.trim()
          ? item.purpose.trim()
          : undefined,
    };
  });
}

export function parseRetrieveRequest(value: unknown): RetrieveRequest {
  if (!isRecord(value)) {
    throw new Error("Invalid retrieve request: expected JSON object");
  }

  const rawQueries = value.searchQueries ?? value.queryTemplates;
  const searchQueries = parseSearchQueries(rawQueries);

  const questionRaw = requireString(value.question, "question", false);
  const questionRestatement =
    typeof value.questionRestatement === "string" && value.questionRestatement.trim()
      ? value.questionRestatement.trim()
      : questionRaw;
  const contextSummary =
    typeof value.contextSummary === "string" ? value.contextSummary.trim() : "";
  const maxIterations =
    typeof value.maxIterations === "number" && Number.isFinite(value.maxIterations)
      ? Math.max(1, Math.min(8, Math.trunc(value.maxIterations)))
      : 8;

  const sessionId =
    typeof value.sessionId === "string" && value.sessionId.trim()
      ? value.sessionId.trim()
      : undefined;

  return {
    question: questionRaw,
    contextSummary,
    questionRestatement,
    workspaceId: requireString(value.workspaceId ?? "default", "workspaceId", false),
    sessionId,
    searchQueries,
    maxIterations,
    topK:
      typeof value.topK === "number" && Number.isFinite(value.topK)
        ? Math.max(1, Math.min(50, Math.trunc(value.topK)))
        : 10,
  };
}

export function parseSearchResponse(value: unknown): SearchResponse {
  if (!isRecord(value) || !Array.isArray(value.hits)) {
    throw new Error("Invalid search response from Python API");
  }

  const hits = value.hits.map((item, index): SearchHit => {
    if (!isRecord(item)) {
      throw new Error(`search hits[${index}] must be an object`);
    }
    return {
      pageId: requireString(item.page_id ?? item.pageId, `hits[${index}].page_id`, false),
      score: typeof item.score === "number" ? item.score : 0,
      title: typeof item.title === "string" ? item.title : null,
      compiledTruth: requireString(
        item.compiled_truth ?? item.compiledTruth,
        `hits[${index}].compiled_truth`,
        true,
      ),
      summary: typeof item.summary === "string" ? item.summary : null,
      originalText:
        typeof item.original_text === "string"
          ? item.original_text
          : typeof item.originalText === "string"
            ? item.originalText
            : "",
      tagPaths: (() => {
        const rawTags = item.tag_paths ?? item.tagPaths;
        return Array.isArray(rawTags)
          ? rawTags.filter((tag: unknown): tag is string => typeof tag === "string")
          : [];
      })(),
    };
  });

  const degraded = Array.isArray(value.degraded)
    ? value.degraded.filter((item): item is string => typeof item === "string")
    : [];

  return { hits, degraded };
}

export function parseRetrieverDecision(text: string): RetrieverDecision {
  const payload = JSON.parse(extractJsonObject(text)) as unknown;
  if (!isRecord(payload)) {
    throw new Error("retriever decision must be a JSON object");
  }

  const legacyRevised = payload.revisedSearchQueries ?? payload.nextSearchQueries;
  let nextSearchQueries: SearchQuery[] = [];
  if (Array.isArray(legacyRevised) && legacyRevised.length > 0) {
    nextSearchQueries = parseSearchQueries(legacyRevised, { allowEmpty: true });
  }

  const excerpts = Array.isArray(payload.excerpts)
    ? payload.excerpts.map((item, index): RetrieveExcerpt => {
        if (!isRecord(item)) {
          throw new Error(`excerpts[${index}] must be an object`);
        }
        return {
          pageId: requireString(item.pageId ?? item.page_id, `excerpts[${index}].pageId`, false),
          title: requireString(item.title, `excerpts[${index}].title`, true),
          compiledTruth: requireString(
            item.compiledTruth ?? item.compiled_truth,
            `excerpts[${index}].compiledTruth`,
            true,
          ),
          originalText: requireString(
            item.originalText ?? item.original_text,
            `excerpts[${index}].originalText`,
            true,
          ),
          summary: requireString(item.summary, `excerpts[${index}].summary`, true),
          relevance: requireString(item.relevance, `excerpts[${index}].relevance`, true),
        };
      })
    : [];

  const selectedDomain =
    typeof payload.selectedDomain === "string" && payload.selectedDomain.trim()
      ? payload.selectedDomain.trim()
      : undefined;

  return {
    relevantPageIds: Array.isArray(payload.relevantPageIds)
      ? payload.relevantPageIds.filter((id): id is string => typeof id === "string")
      : [],
    sufficient: payload.sufficient === true,
    reason: typeof payload.reason === "string" ? payload.reason : "",
    analysis: typeof payload.analysis === "string" ? payload.analysis : undefined,
    selectedDomain,
    nextSearchQueries,
    answerGuidance:
      typeof payload.answerGuidance === "string" ? payload.answerGuidance : "",
    excerpts,
  };
}

/** @deprecated Use parseRetrieverDecision */
export function parseJudgeRoundResult(text: string, roundHits: SearchHit[]): JudgeRoundResult {
  const decision = parseRetrieverDecision(text);
  const relevantIds = new Set(decision.relevantPageIds);
  return {
    relevantHits: roundHits.filter((hit) => relevantIds.has(hit.pageId)),
    sufficient: decision.sufficient,
    reason: decision.reason,
    analysis: decision.analysis,
    revisedSearchQueries:
      decision.nextSearchQueries.length > 0 ? decision.nextSearchQueries : undefined,
  };
}

function extractJsonObject(text: string): string {
  const start = text.indexOf("{");
  if (start < 0) {
    throw new Error("retriever decision JSON not found in model output");
  }
  const end = text.lastIndexOf("}");
  if (end <= start) {
    throw new Error("retriever decision JSON not found in model output");
  }
  return text.slice(start, end + 1);
}

export function pickRelevantHits(pool: Map<string, SearchHit>, pageIds: string[]): SearchHit[] {
  return pageIds
    .map((id) => pool.get(id))
    .filter((hit): hit is SearchHit => hit !== undefined);
}
