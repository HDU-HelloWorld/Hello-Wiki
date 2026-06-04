import { mkdtemp, mkdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { test } from "node:test";
import assert from "node:assert/strict";

import {
  loadPrompt,
  renderTemplate,
  resetPromptLoaderCache,
} from "../src/utils/prompt-loader.js";

test("renderTemplate substitutes variables", () => {
  assert.equal(renderTemplate("Hello {{name}}", { name: "Wiki" }), "Hello Wiki");
});

test("loadPrompt reads system and user templates", async () => {
  resetPromptLoaderCache();
  const root = await mkdtemp(path.join(tmpdir(), "agent-ai-prompts-"));
  await mkdir(path.join(root, "test"), { recursive: true });
  await writeFile(
    path.join(root, "index.yaml"),
    `prompts:
  - id: test.prompt
    system: test/system.md
    user: test/user.md
`,
    "utf8",
  );
  await writeFile(path.join(root, "test", "system.md"), "System {{role}}", "utf8");
  await writeFile(path.join(root, "test", "user.md"), "User {{question}}", "utf8");

  const previous = process.env.AGENT_AI_PROMPTS_DIR;
  process.env.AGENT_AI_PROMPTS_DIR = root;
  resetPromptLoaderCache();

  try {
    const bundle = await loadPrompt("test.prompt", { role: "agent", question: "辅修选课" });
    assert.equal(bundle.system, "System agent");
    assert.equal(bundle.user, "User 辅修选课");
  } finally {
    if (previous === undefined) {
      delete process.env.AGENT_AI_PROMPTS_DIR;
    } else {
      process.env.AGENT_AI_PROMPTS_DIR = previous;
    }
    resetPromptLoaderCache();
  }
});
