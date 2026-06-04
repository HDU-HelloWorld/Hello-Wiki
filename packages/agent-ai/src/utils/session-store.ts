import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

import type { AgentHistoryMessage } from "../agent/schemas.js";
import { resolvePackageRoot } from "./monorepo-root.js";

export type SessionEvent =
  | {
      type: "user" | "assistant";
      sessionId: string;
      workspaceId: string;
      content: string;
      timestamp: number;
    }
  | {
      type: "toolResult";
      sessionId: string;
      workspaceId: string;
      toolName: string;
      result: unknown;
      timestamp: number;
    }
  | {
      type: "retrieveTrace";
      sessionId: string;
      workspaceId: string;
      phase: string;
      detail: Record<string, unknown>;
      timestamp: number;
    };

export type SessionStore = {
  readHistory(sessionId: string): Promise<AgentHistoryMessage[]>;
  append(event: SessionEvent): Promise<void>;
};

function resolveDefaultSessionDir(): string {
  const override = process.env.AGENT_AI_SESSION_DIR?.trim();
  if (override) {
    return path.resolve(override);
  }
  try {
    return path.join(resolvePackageRoot(), "data", "agent-sessions");
  } catch {
    return path.resolve(process.cwd(), "data", "agent-sessions");
  }
}

export function resolveDefaultRetrieverSessionDir(): string {
  const override = process.env.AGENT_AI_RETRIEVER_SESSION_DIR?.trim();
  if (override) {
    return path.resolve(override);
  }
  try {
    return path.join(resolvePackageRoot(), "data", "retriever-sessions");
  } catch {
    return path.resolve(process.cwd(), "data", "retriever-sessions");
  }
}

function safeSessionId(sessionId: string): string {
  return sessionId.replace(/[^a-zA-Z0-9_.-]/g, "_");
}

export class JsonlSessionStore implements SessionStore {
  constructor(private readonly baseDir = resolveDefaultSessionDir()) {}

  async readHistory(sessionId: string): Promise<AgentHistoryMessage[]> {
    let content = "";
    try {
      content = await readFile(this.sessionPath(sessionId), "utf8");
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === "ENOENT") return [];
      throw error;
    }

    return content
      .split(/\r?\n/)
      .filter(Boolean)
      .map((line) => JSON.parse(line) as SessionEvent)
      .filter(isChatEvent)
      .map((event) => ({
        role: event.type,
        content: event.content,
        timestamp: event.timestamp,
      }));
  }

  async append(event: SessionEvent): Promise<void> {
    await mkdir(this.baseDir, { recursive: true });
    const filePath = this.sessionPath(event.sessionId);
    await writeFile(filePath, `${JSON.stringify(event)}\n`, { flag: "a" });
  }

  private sessionPath(sessionId: string): string {
    return path.join(this.baseDir, `${safeSessionId(sessionId)}.jsonl`);
  }
}

function isChatEvent(
  event: SessionEvent,
): event is Extract<SessionEvent, { type: "user" | "assistant" }> {
  return event.type === "user" || event.type === "assistant";
}

export type RetrieverSessionContext = {
  sessionStore: SessionStore;
  sessionId: string;
  workspaceId: string;
};

export function resolveRetrieverSession(
  request: { workspaceId: string; sessionId?: string },
  options: { sessionStore?: SessionStore; sessionId?: string } = {},
): RetrieverSessionContext {
  return {
    sessionStore:
      options.sessionStore ?? new JsonlSessionStore(resolveDefaultRetrieverSessionDir()),
    sessionId: request.sessionId ?? options.sessionId ?? "retrieve",
    workspaceId: request.workspaceId,
  };
}

/** Step-by-step Retriever trace (domains, LLM, search rounds) in the session JSONL. */
export async function appendRetrieveTrace(
  ctx: RetrieverSessionContext,
  phase: string,
  detail: Record<string, unknown>,
): Promise<void> {
  await ctx.sessionStore.append({
    type: "retrieveTrace",
    sessionId: ctx.sessionId,
    workspaceId: ctx.workspaceId,
    phase,
    detail,
    timestamp: Date.now(),
  });
}

/** Final Retriever summary JSONL under data/retriever-sessions (or AGENT_AI_RETRIEVER_SESSION_DIR). */
export async function persistRetrieveSession(
  ctx: RetrieverSessionContext,
  input: {
    question: string;
    selectedDomain?: string;
    sufficient: boolean;
    iterations: number;
    excerptCount: number;
    sessionRounds: unknown[];
    answerGuidance?: string;
    searchQueries?: unknown[];
    accumulatedPageIds?: string[];
  },
): Promise<void> {
  await ctx.sessionStore.append({
    type: "toolResult",
    sessionId: ctx.sessionId,
    workspaceId: ctx.workspaceId,
    toolName: "retrieve",
    result: {
      selectedDomain: input.selectedDomain,
      sufficient: input.sufficient,
      iterations: input.iterations,
      excerptCount: input.excerptCount,
      sessionRounds: input.sessionRounds,
      answerGuidance: input.answerGuidance,
      searchQueries: input.searchQueries,
      accumulatedPageIds: input.accumulatedPageIds,
      questionPreview: input.question.slice(0, 200),
    },
    timestamp: Date.now(),
  });
}
