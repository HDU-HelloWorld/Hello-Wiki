import {
  validateToolCall,
  type Api,
  type AssistantMessage,
  type Model,
} from "@earendil-works/pi-ai";

import { completeWithGateway, type CompleteFn, type ModelGatewayOptions } from "../utils/model-gateway.js";
import { buildExtractionContext } from "./context-builder.js";
import {
  EMIT_EXTRACTED_KNOWLEDGE_TOOL,
  extractionTool,
  parseExtractionRequest,
  type ExtractedKnowledge,
  type ExtractionRequest,
} from "./schemas.js";
import { loadSkillPrompt } from "./skill-loader.js";

export type ExtractKnowledgeOptions = ModelGatewayOptions & {
  referencesDir?: string;
  modelOverride?: Model<Api>;
  completeFn?: CompleteFn;
};

export async function extractKnowledge(
  rawRequest: unknown,
  options: ExtractKnowledgeOptions = {},
): Promise<ExtractedKnowledge> {
  const request: ExtractionRequest = parseExtractionRequest(rawRequest);
  const { prompt } = await loadSkillPrompt(request.domain, options.referencesDir);
  const context = buildExtractionContext(request, prompt);
  const assistant = await completeWithGateway(context, options);
  return extractToolResult(assistant);
}

export function extractToolResult(assistant: AssistantMessage): ExtractedKnowledge {
  const toolCall = assistant.content.find(
    (block) => block.type === "toolCall" && block.name === EMIT_EXTRACTED_KNOWLEDGE_TOOL,
  );

  if (!toolCall || toolCall.type !== "toolCall") {
    throw new Error(`Model did not call ${EMIT_EXTRACTED_KNOWLEDGE_TOOL}`);
  }

  return validateToolCall([extractionTool], toolCall) as ExtractedKnowledge;
}
