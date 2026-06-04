import {
  complete,
  getEnvApiKey,
  getModel,
  getModels,
  type Api,
  type AssistantMessage,
  type Context,
  type Model,
  type Provider,
} from "@earendil-works/pi-ai";

import { loadBackendEnv } from "./env.js";

export type ModelGatewayConfig = {
  provider?: Provider;
  model?: string;
  apiKey?: string;
  temperature?: number;
  maxTokens?: number;
};

export type CompleteFn = (
  model: Model<Api>,
  context: Context,
  options?: { apiKey?: string; temperature?: number; maxTokens?: number },
) => Promise<AssistantMessage>;

export type ModelGatewayOptions = ModelGatewayConfig & {
  modelOverride?: Model<Api>;
  completeFn?: CompleteFn;
};

export function readModelGatewayConfig(env: NodeJS.ProcessEnv = process.env): ModelGatewayConfig {
  loadBackendEnv();

  return {
    provider:
      env.AGENT_AI_PROVIDER ??
      env.INGEST_AI_PROVIDER ??
      env.RETRIEVE_AI_PROVIDER ??
      env.LLM_PROVIDER ??
      "deepseek",
    model:
      env.AGENT_AI_MODEL ??
      env.INGEST_AI_MODEL ??
      env.RETRIEVE_AI_MODEL ??
      env.LLM_MODEL_NAME ??
      "deepseek-chat",
    apiKey:
      env.AGENT_AI_API_KEY ??
      env.INGEST_AI_API_KEY ??
      env.RETRIEVE_AI_API_KEY ??
      env.DEEPSEEK_API_KEY ??
      env.LLM_API_KEY,
    temperature: parseOptionalNumber(
      env.AGENT_AI_TEMPERATURE ??
        env.INGEST_AI_TEMPERATURE ??
        env.RETRIEVE_AI_TEMPERATURE ??
        env.LLM_TEMPERATURE,
    ),
    maxTokens: parseOptionalNumber(
      env.AGENT_AI_MAX_TOKENS ??
        env.INGEST_AI_MAX_TOKENS ??
        env.RETRIEVE_AI_MAX_TOKENS ??
        env.LLM_MAX_TOKENS,
    ),
  };
}

function parseOptionalNumber(value: string | undefined): number | undefined {
  if (value === undefined || value.trim() === "") return undefined;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Invalid numeric model gateway option: ${value}`);
  }
  return parsed;
}

export function resolveModel(config: ModelGatewayConfig = readModelGatewayConfig()): Model<Api> {
  const provider = config.provider ?? "deepseek";
  const modelId = config.model ?? "deepseek-chat";

  const builtInModel = getModels(provider as never).find((model) => model.id === modelId);
  if (builtInModel) return builtInModel as Model<Api>;

  try {
    return getModel(provider as never, modelId as never) as Model<Api>;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Unknown pi-ai model '${provider}/${modelId}': ${message}`);
  }
}

export function resolveApiKey(model: Model<Api>, config: ModelGatewayConfig): string | undefined {
  return config.apiKey ?? getEnvApiKey(model.provider);
}

export async function completeWithGateway(
  context: Context,
  options: ModelGatewayOptions = {},
): Promise<AssistantMessage> {
  const config = { ...readModelGatewayConfig(), ...options };
  const model = options.modelOverride ?? resolveModel(config);
  const apiKey = config.apiKey ?? getEnvApiKey(model.provider);
  const completeFn = options.completeFn ?? (complete as CompleteFn);

  return completeFn(model, context, {
    apiKey,
    temperature: config.temperature,
    maxTokens: config.maxTokens,
  });
}
