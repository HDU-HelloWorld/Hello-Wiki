import { StringEnum, Type, type Static, type Tool } from "@earendil-works/pi-ai";

export const EffectiveRangeSchema = Type.Object({
  start: Type.Union([Type.String(), Type.Null()], {
    description: "Earliest applicable date as YYYY-MM-DD, or null when unknown.",
  }),
  end: Type.Union([Type.String(), Type.Null()], {
    description: "End-of-validity date as YYYY-MM-DD, or null when unknown.",
  }),
  description: Type.String({
    minLength: 1,
    description: "Human-readable description of the effective range.",
  }),
  stale_risk: StringEnum(["low", "medium", "high", "unknown"] as const, {
    description: "Freshness risk for the extracted knowledge.",
    default: "unknown",
  }),
});

export const SuggestedTagSchema = Type.Object({
  name: Type.String({
    minLength: 1,
    pattern: "^[a-z][a-z0-9_]*$",
    description: "Machine-readable tag name using lowercase snake_case.",
  }),
  label: Type.String({
    minLength: 1,
    description: "Human-readable tag label.",
  }),
  description: Type.Optional(Type.String({ description: "Tag scope description." })),
  parent_hint: Type.Optional(Type.String({ description: "Suggested parent ltree path." })),
});

export const ExtractedKnowledgeSchema = Type.Object({
  chunk_summary: Type.String({ minLength: 1 }),
  page_title: Type.String({ minLength: 1, maxLength: 256 }),
  compiled_truth: Type.String({ minLength: 1 }),
  suggested_tags: Type.Array(SuggestedTagSchema, { minItems: 2, maxItems: 6 }),
  effective_range: EffectiveRangeSchema,
});

export const ExtractionRequestSchema = Type.Object({
  domain: Type.String({ minLength: 1 }),
  chunkText: Type.String({ minLength: 1 }),
  tagTree: Type.String(),
  sourceDocument: Type.String(),
  sourcePage: Type.String(),
  chunkIndex: Type.Number(),
  totalChunks: Type.Number(),
});

export const LeafTagSchema = Type.Object({
  name: Type.String({
    minLength: 1,
    pattern: "^[a-z][a-z0-9_]*$",
  }),
  label: Type.String({ minLength: 1 }),
  description: Type.Optional(Type.String()),
});

export const TagCategorySchema = Type.Object({
  name: Type.String({
    minLength: 1,
    pattern: "^[a-z][a-z0-9_]*$",
  }),
  label: Type.String({ minLength: 1 }),
  description: Type.Optional(Type.String()),
  leaves: Type.Array(LeafTagSchema, { minItems: 1 }),
});

export const TagTreeSchema = Type.Object({
  domain: Type.String({ minLength: 1 }),
  generated_at: Type.String(),
  categories: Type.Array(TagCategorySchema, { minItems: 1 }),
});

export const InitTagsRequestSchema = Type.Object({
  domain: Type.String({ minLength: 1 }),
  description: Type.String({ minLength: 1 }),
  language: Type.String({ minLength: 1 }),
  existingTags: Type.Array(Type.String()),
});

export type EffectiveRange = Static<typeof EffectiveRangeSchema>;
export type SuggestedTag = Static<typeof SuggestedTagSchema>;
export type ExtractedKnowledge = Static<typeof ExtractedKnowledgeSchema>;
export type ExtractionRequest = Static<typeof ExtractionRequestSchema>;
export type LeafTag = Static<typeof LeafTagSchema>;
export type TagCategory = Static<typeof TagCategorySchema>;
export type TagTree = Static<typeof TagTreeSchema>;
export type InitTagsRequest = Static<typeof InitTagsRequestSchema>;

export const EMIT_EXTRACTED_KNOWLEDGE_TOOL = "emit_extracted_knowledge";

export const extractionTool: Tool<typeof ExtractedKnowledgeSchema> = {
  name: EMIT_EXTRACTED_KNOWLEDGE_TOOL,
  description:
    "Emit the validated five-field knowledge extraction result for the current chunk.",
  parameters: ExtractedKnowledgeSchema,
};

export const EMIT_TAG_TREE_TOOL = "emit_tag_tree";

export const tagTreeTool: Tool<typeof TagTreeSchema> = {
  name: EMIT_TAG_TREE_TOOL,
  description: "Emit the validated tag taxonomy tree for the requested domain.",
  parameters: TagTreeSchema,
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requireString(value: unknown, field: string, allowEmpty = true): string {
  if (typeof value !== "string") {
    throw new Error(`Invalid extraction request: ${field} must be a string`);
  }
  if (!allowEmpty && value.trim() === "") {
    throw new Error(`Invalid extraction request: ${field} must not be empty`);
  }
  return value;
}

function requireNumber(value: unknown, field: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`Invalid extraction request: ${field} must be a finite number`);
  }
  return value;
}

export function parseExtractionRequest(value: unknown): ExtractionRequest {
  if (!isRecord(value)) {
    throw new Error("Invalid extraction request: expected JSON object");
  }
  return {
    domain: requireString(value.domain, "domain", false),
    chunkText: requireString(value.chunkText, "chunkText", false),
    tagTree: requireString(value.tagTree, "tagTree"),
    sourceDocument: requireString(value.sourceDocument, "sourceDocument"),
    sourcePage: requireString(value.sourcePage, "sourcePage"),
    chunkIndex: requireNumber(value.chunkIndex, "chunkIndex"),
    totalChunks: requireNumber(value.totalChunks, "totalChunks"),
  };
}

export function parseInitTagsRequest(value: unknown): InitTagsRequest {
  if (!isRecord(value)) {
    throw new Error("Invalid init-tags request: expected JSON object");
  }
  const existingTags = Array.isArray(value.existingTags)
    ? value.existingTags.map((item, index) => requireString(item, `existingTags[${index}]`))
    : [];
  return {
    domain: requireString(value.domain ?? "general", "domain", false),
    description: requireString(value.description, "description", false),
    language: requireString(value.language ?? "zh", "language", false),
    existingTags,
  };
}
