import { Agent, type AgentMessage } from "@earendil-works/pi-agent-core";
import type { Api, Model } from "@earendil-works/pi-ai";

import {
  readModelGatewayConfig,
  resolveApiKey,
  resolveModel,
  type ModelGatewayConfig,
} from "../utils/model-gateway.js";
import { loadPrompt } from "../utils/prompt-loader.js";
import { contentToText } from "../utils/content.js";
import { JsonlSessionStore, type SessionStore } from "../utils/session-store.js";
import { historyToAgentMessages } from "./history.js";
import { parseAgentChatRequest, type AgentChatResponse } from "./schemas.js";
import { buildAgentTools } from "./tools/registry.js";

export type AgentLoopOptions = ModelGatewayConfig & {
  modelOverride?: Model<Api>;
  sessionId?: string;
  sessionStore?: SessionStore;
};

export async function runAgentChat(
  rawRequest: unknown,
  options: AgentLoopOptions = {},
): Promise<AgentChatResponse> {
  const request = parseAgentChatRequest(rawRequest);
  const config = { ...readModelGatewayConfig(), ...options };
  const model = options.modelOverride ?? resolveModel(config);
  const apiKey = resolveApiKey(model, config);
  const sessionStore = options.sessionStore ?? new JsonlSessionStore();
  const sessionId = request.sessionId || options.sessionId || "default";
  const persistedHistory = await sessionStore.readHistory(sessionId);
  const history = persistedHistory.length > 0 ? persistedHistory : request.history;
  const seedMessages = historyToAgentMessages(history);
  const { system: systemPrompt } = await loadPrompt("agent.main");

  const agent = new Agent({
    initialState: {
      systemPrompt: systemPrompt ?? "",
      model,
      thinkingLevel: "off",
      tools: buildAgentTools({
        workspaceId: request.workspaceId,
        sessionId,
      }),
      messages: seedMessages,
    },
    convertToLlm: (messages) =>
      messages.filter(
        (message): message is AgentMessage & { role: "user" | "assistant" | "toolResult" } =>
          message.role === "user" || message.role === "assistant" || message.role === "toolResult",
      ),
    transformContext: async (messages) => messages,
    toolExecution: "parallel",
    sessionId,
    getApiKey: async () => apiKey,
  });

  await sessionStore.append({
    type: "user",
    sessionId,
    workspaceId: request.workspaceId,
    content: request.message,
    timestamp: Date.now(),
  });

  await agent.prompt(request.message);
  await agent.waitForIdle();

  const assistant = [...agent.state.messages]
    .reverse()
    .find((message) => message.role === "assistant");
  if (!assistant) {
    throw new Error("Agent did not produce an assistant reply");
  }

  const reply = contentToText(assistant.content);
  await sessionStore.append({
    type: "assistant",
    sessionId,
    workspaceId: request.workspaceId,
    content: reply,
    timestamp: Date.now(),
  });

  return { reply, sessionId };
}
