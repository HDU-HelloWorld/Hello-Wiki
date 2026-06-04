import {
  validateToolCall,
  type Api,
  type AssistantMessage,
  type Context,
  type Model,
} from "@earendil-works/pi-ai";

import { resolveSkillReferencesDir } from "../utils/monorepo-root.js";
import { completeWithGateway, type CompleteFn, type ModelGatewayOptions } from "../utils/model-gateway.js";
import {
  EMIT_TAG_TREE_TOOL,
  parseInitTagsRequest,
  tagTreeTool,
  type InitTagsRequest,
  type TagTree,
} from "./schemas.js";
import { loadSkillPrompt } from "./skill-loader.js";

export type InitTagsOptions = ModelGatewayOptions & {
  referencesDir?: string;
  modelOverride?: Model<Api>;
  completeFn?: CompleteFn;
};

const DEFAULT_TAG_REFERENCES_DIR = resolveSkillReferencesDir(
  "apps",
  "skills",
  "tag-initialize",
  "references",
);

export async function initializeTags(
  rawRequest: unknown,
  options: InitTagsOptions = {},
): Promise<TagTree> {
  const request: InitTagsRequest = parseInitTagsRequest(rawRequest);
  const { prompt } = await loadSkillPrompt(
    request.domain,
    options.referencesDir ?? DEFAULT_TAG_REFERENCES_DIR,
  );
  const assistant = await completeWithGateway(buildInitTagsContext(request, prompt), options);
  return extractTagTreeResult(assistant);
}

function buildInitTagsContext(request: InitTagsRequest, promptTemplate: string): Context {
  const systemPrompt = promptTemplate
    .replaceAll("{domain}", request.domain)
    .replaceAll("{description}", request.description)
    .replaceAll("{language}", request.language)
    .replaceAll("{existing_tags}", JSON.stringify(request.existingTags));

  return {
    systemPrompt,
    messages: [
      {
        role: "user" as const,
        content: request.description,
        timestamp: Date.now(),
      },
    ],
    tools: [tagTreeTool],
  };
}

export function extractTagTreeResult(assistant: AssistantMessage): TagTree {
  const toolCall = assistant.content.find(
    (block) => block.type === "toolCall" && block.name === EMIT_TAG_TREE_TOOL,
  );

  if (!toolCall || toolCall.type !== "toolCall") {
    throw new Error(`Model did not call ${EMIT_TAG_TREE_TOOL}`);
  }

  return validateToolCall([tagTreeTool], toolCall) as TagTree;
}
