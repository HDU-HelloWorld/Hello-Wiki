import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  appendRetrieveTrace,
  JsonlSessionStore,
  persistRetrieveSession,
  resolveRetrieverSession,
} from "../src/utils/session-store.js";

test("persistRetrieveSession appends retrieve toolResult to session JSONL", async () => {
  const dir = mkdtempSync(path.join(tmpdir(), "retriever-sessions-"));
  const ctx = resolveRetrieverSession(
    { workspaceId: "00000000-0000-0000-0000-000000000001", sessionId: "session-1" },
    { sessionStore: new JsonlSessionStore(dir) },
  );

  try {
    await persistRetrieveSession(ctx, {
      question: "什么是 RRF？",
      selectedDomain: "demo",
      sufficient: true,
      iterations: 2,
      excerptCount: 1,
      sessionRounds: [{ kind: "kickoff", promptRound: 1 }],
    });

    const lines = readFileSync(path.join(dir, "session-1.jsonl"), "utf8").trim().split("\n");
    assert.equal(lines.length, 1);
    const event = JSON.parse(lines[0]!) as {
      type: string;
      toolName: string;
      result: { selectedDomain?: string; sessionRounds: unknown[] };
    };
    assert.equal(event.type, "toolResult");
    assert.equal(event.toolName, "retrieve");
    assert.equal(event.result.selectedDomain, "demo");
    assert.equal(event.result.sessionRounds.length, 1);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("appendRetrieveTrace writes retrieveTrace lines to retriever session file", async () => {
  const dir = mkdtempSync(path.join(tmpdir(), "retriever-sessions-"));
  const ctx = resolveRetrieverSession(
    { workspaceId: "00000000-0000-0000-0000-000000000001" },
    { sessionStore: new JsonlSessionStore(dir) },
  );

  try {
    await appendRetrieveTrace(ctx, "search_round", { hitCount: 0, degraded: ["semantic_disabled"] });
    const lines = readFileSync(path.join(dir, "retrieve.jsonl"), "utf8").trim().split("\n");
    assert.equal(lines.length, 1);
    const event = JSON.parse(lines[0]!) as { type: string; phase: string };
    assert.equal(event.type, "retrieveTrace");
    assert.equal(event.phase, "search_round");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
