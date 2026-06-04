import { readFile } from "node:fs/promises";
import path from "node:path";
import { parse } from "yaml";

import { resolvePromptsDir } from "./monorepo-root.js";

export type PromptBundle = {
  system?: string;
  user?: string;
};

type PromptEntry = {
  id: string;
  system?: string;
  user?: string;
};

type PromptIndex = {
  prompts?: PromptEntry[];
};

const fileCache = new Map<string, string>();
let indexCache: PromptEntry[] | null = null;

export function renderTemplate(template: string, vars: Record<string, string> = {}): string {
  let result = template;
  for (const [key, value] of Object.entries(vars)) {
    result = result.replaceAll(`{{${key}}}`, value);
  }
  return result;
}

export async function loadPrompt(
  id: string,
  vars: Record<string, string> = {},
): Promise<PromptBundle> {
  const entry = (await loadIndex()).find((item) => item.id === id);
  if (!entry) {
    throw new Error(`Unknown prompt id '${id}'`);
  }

  const promptsDir = resolvePromptsDir();
  const bundle: PromptBundle = {};

  if (entry.system) {
    const raw = await readPromptFile(path.join(promptsDir, entry.system));
    bundle.system = renderTemplate(raw, vars);
  }
  if (entry.user) {
    const raw = await readPromptFile(path.join(promptsDir, entry.user));
    bundle.user = renderTemplate(raw, vars);
  }

  return bundle;
}

async function loadIndex(): Promise<PromptEntry[]> {
  if (indexCache) return indexCache;

  const indexPath = path.join(resolvePromptsDir(), "index.yaml");
  const index = parse(await readFile(indexPath, "utf8")) as PromptIndex;
  indexCache = index.prompts ?? [];
  return indexCache;
}

async function readPromptFile(filePath: string): Promise<string> {
  const cached = fileCache.get(filePath);
  if (cached !== undefined) return cached;

  const content = await readFile(filePath, "utf8");
  fileCache.set(filePath, content);
  return content;
}

/** Clear caches (for tests). */
export function resetPromptLoaderCache(): void {
  fileCache.clear();
  indexCache = null;
}
