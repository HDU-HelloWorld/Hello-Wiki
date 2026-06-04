/**
 * Loads user-customizable domain prompts from apps/skills/ (ingest, tag-init).
 * Built-in operational prompts use utils/prompt-loader.ts + packages/agent-ai/prompts/.
 */
import { readFile } from "node:fs/promises";
import path from "node:path";
import { parse } from "yaml";

import { resolveSkillReferencesDir } from "../utils/monorepo-root.js";

export type SkillReference = {
  id: string;
  name?: string;
  description?: string;
  template?: string;
  prompt: string;
  default?: boolean;
};

type ReferenceIndex = {
  references?: SkillReference[];
};

export type SkillPrompt = {
  reference: SkillReference;
  prompt: string;
};

export function defaultReferencesDir(): string {
  return resolveSkillReferencesDir("apps", "skills", "knowledge-extraction", "references");
}

export async function loadSkillPrompt(
  domain: string,
  referencesDir = defaultReferencesDir(),
): Promise<SkillPrompt> {
  const indexPath = path.join(referencesDir, "index.yaml");
  const index = parse(await readFile(indexPath, "utf8")) as ReferenceIndex;
  const references = index.references ?? [];
  const reference =
    references.find((item) => item.id === domain) ??
    references.find((item) => item.default === true);

  if (!reference) {
    throw new Error(`No knowledge-extraction reference found for domain '${domain}'`);
  }

  const promptPath = path.join(referencesDir, reference.prompt);
  return {
    reference,
    prompt: await readFile(promptPath, "utf8"),
  };
}
