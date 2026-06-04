import type { AgentMessage } from "@earendil-works/pi-agent-core";

import type { AgentHistoryMessage } from "./schemas.js";

export function historyToAgentMessages(history: AgentHistoryMessage[]): AgentMessage[] {
  return history.map((item, index) => {
    const timestamp = item.timestamp ?? Date.now() + index;
    const content = [{ type: "text" as const, text: item.content }];
    if (item.role === "assistant") {
      return {
        role: "assistant" as const,
        content,
        timestamp,
        api: "openai-responses" as const,
        provider: "openai" as const,
        model: "history",
        usage: {
          input: 0,
          output: 0,
          cacheRead: 0,
          cacheWrite: 0,
          totalTokens: 0,
          cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 },
        },
        stopReason: "stop" as const,
      };
    }
    return {
      role: "user" as const,
      content,
      timestamp,
    };
  });
}
