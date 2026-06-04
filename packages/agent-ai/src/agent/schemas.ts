export type AgentHistoryMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp?: number;
};

export type AgentChatRequest = {
  message: string;
  sessionId: string;
  workspaceId: string;
  history: AgentHistoryMessage[];
};

export type AgentChatResponse = {
  reply: string;
  sessionId: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requireString(value: unknown, field: string, allowEmpty = true): string {
  if (typeof value !== "string") {
    throw new Error(`Invalid agent chat request: ${field} must be a string`);
  }
  if (!allowEmpty && value.trim() === "") {
    throw new Error(`Invalid agent chat request: ${field} must not be empty`);
  }
  return value;
}

export function parseAgentChatRequest(value: unknown): AgentChatRequest {
  if (!isRecord(value)) {
    throw new Error("Invalid agent chat request: expected JSON object");
  }

  const history = Array.isArray(value.history)
    ? value.history.map((item, index): AgentHistoryMessage => {
        if (!isRecord(item)) {
          throw new Error(`Invalid agent chat request: history[${index}] must be an object`);
        }
        const role = requireString(item.role, `history[${index}].role`, false);
        if (role !== "user" && role !== "assistant") {
          throw new Error(`Invalid agent chat request: history[${index}].role is invalid`);
        }
        return {
          role,
          content: requireString(item.content, `history[${index}].content`),
          timestamp:
            typeof item.timestamp === "number" && Number.isFinite(item.timestamp)
              ? item.timestamp
              : undefined,
        };
      })
    : [];

  return {
    message: requireString(value.message, "message", false),
    sessionId: requireString(value.sessionId ?? "default", "sessionId", false),
    workspaceId: requireString(value.workspaceId ?? "default", "workspaceId", false),
    history,
  };
}
