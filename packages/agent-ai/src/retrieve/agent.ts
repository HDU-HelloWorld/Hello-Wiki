import { Agent, type AgentMessage } from "@earendil-works/pi-agent-core";
import type { Api, Model } from "@earendil-works/pi-ai";

import { loadPrompt } from "../utils/prompt-loader.js";
import {
  readModelGatewayConfig,
  resolveApiKey,
  resolveModel,
  type ModelGatewayConfig,
} from "../utils/model-gateway.js";

export type RetrieverAgentOptions = ModelGatewayConfig & {
  modelOverride?: Model<Api>;
};

export async function createRetrieverAgent(
  options: RetrieverAgentOptions = {},
): Promise<Agent> {
  const config = { ...readModelGatewayConfig(), ...options };
  const model = options.modelOverride ?? resolveModel(config);
  const apiKey = resolveApiKey(model, config);
  const { system: systemPrompt } = await loadPrompt("retriever.main");

  return new Agent({
    initialState: {
      systemPrompt: systemPrompt ?? "",
      model,
      thinkingLevel: "off",
      tools: [],
      messages: [],
    },
    convertToLlm: (messages) =>
      messages.filter(
        (message): message is AgentMessage & { role: "user" | "assistant" } =>
          message.role === "user" || message.role === "assistant",
      ),
    transformContext: async (messages) => messages,
    getApiKey: async () => apiKey,
  });
}
