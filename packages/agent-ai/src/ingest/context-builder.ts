import type { Context } from "@earendil-works/pi-ai";

import { extractionTool, type ExtractionRequest } from "./schemas.js";

function injectPromptVariables(prompt: string, request: ExtractionRequest): string {
  return prompt
    .replaceAll("{source_document}", request.sourceDocument)
    .replaceAll("{source_page}", request.sourcePage)
    .replaceAll("{chunk_index}", String(request.chunkIndex))
    .replaceAll("{total_chunks}", String(request.totalChunks));
}

export function buildExtractionContext(
  request: ExtractionRequest,
  systemPromptTemplate: string,
): Context {
  const systemPrompt = injectPromptVariables(systemPromptTemplate, request);
  const userPrompt = [
    "AVAILABLE TAGS",
    request.tagTree,
    "",
    "TEXT TO ANALYZE",
    request.chunkText,
  ].join("\n");

  return {
    systemPrompt,
    messages: [
      {
        role: "user",
        content: userPrompt,
        timestamp: Date.now(),
      },
    ],
    tools: [extractionTool],
  };
}
