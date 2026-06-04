import type { SearchQuery, SearchHit } from "./schemas.js";

export type InsightSearchResult = {
  hits: SearchHit[];
  skipped: boolean;
  reason: string;
};

export type InsightClient = {
  search: (query: SearchQuery, topK: number) => Promise<InsightSearchResult>;
};

/**
 * Insight fast path (semantic + keyword on insight library).
 * Reserved for a larger future integration — not implemented in TypeScript yet.
 */
export function createInsightClient(): InsightClient {
  return {
    async search(_query, _topK) {
      return {
        hits: [],
        skipped: true,
        reason: "insight_fast_path_not_implemented",
      };
    },
  };
}
