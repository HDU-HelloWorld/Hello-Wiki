import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SKILLS_MARKER = path.join("apps", "skills");
const PACKAGE_MARKER = "package.json";

export function resolveMonorepoRoot(startDir = path.dirname(fileURLToPath(import.meta.url))): string {
  let current = startDir;
  while (true) {
    if (existsSync(path.join(current, SKILLS_MARKER))) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }

  throw new Error(
    `Could not locate monorepo root (missing '${SKILLS_MARKER}'). ` +
      "Set INGEST_AI_REFERENCES_DIR or run from the Hello-Wiki repository.",
  );
}

/** Resolve packages/agent-ai root (contains package.json + prompts/). */
export function resolvePackageRoot(startDir = path.dirname(fileURLToPath(import.meta.url))): string {
  let current = startDir;
  while (true) {
    const pkgJson = path.join(current, PACKAGE_MARKER);
    if (existsSync(pkgJson) && existsSync(path.join(current, "prompts", "index.yaml"))) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }

  throw new Error(
    "Could not locate agent-ai package root (missing prompts/index.yaml). " +
      "Set AGENT_AI_PROMPTS_DIR or run from the Hello-Wiki repository.",
  );
}

/** User-customizable skill prompts under apps/skills (ingest, tag-init). */
export function resolveSkillReferencesDir(...segments: string[]): string {
  const override = process.env.INGEST_AI_REFERENCES_DIR?.trim();
  if (override) {
    return path.resolve(override);
  }
  return path.join(resolveMonorepoRoot(), ...segments);
}

/** Built-in operational prompts shipped with agent-ai (not user skills). */
export function resolvePromptsDir(): string {
  const override = process.env.AGENT_AI_PROMPTS_DIR?.trim();
  if (override) {
    return path.resolve(override);
  }
  return path.join(resolvePackageRoot(), "prompts");
}
