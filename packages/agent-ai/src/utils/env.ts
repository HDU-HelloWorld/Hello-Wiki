import { existsSync } from "node:fs";
import path from "node:path";

import { config } from "dotenv";

let loaded = false;

export function loadBackendEnv(cwd = process.cwd()): void {
  if (loaded) return;
  loaded = true;

  for (const envPath of candidateEnvPaths(cwd)) {
    if (existsSync(envPath)) {
      config({ path: envPath, quiet: true });
    }
  }
}

function candidateEnvPaths(cwd: string): string[] {
  return [
    path.resolve(cwd, "apps/backend/.env"),
    path.resolve(cwd, ".env"),
    path.resolve(cwd, "../../apps/backend/.env"),
  ];
}
