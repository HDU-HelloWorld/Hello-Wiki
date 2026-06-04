import { createServer, type IncomingMessage, type Server, type ServerResponse } from "node:http";
import { pathToFileURL } from "node:url";

import { runAgentChat } from "./agent/loop.js";
import type { AgentChatResponse } from "./agent/schemas.js";
import { extractKnowledge } from "./ingest/extract-knowledge.js";
import { initializeTags } from "./ingest/init-tags.js";
import type { ExtractedKnowledge, TagTree } from "./ingest/schemas.js";
import { runRetriever } from "./retrieve/loop.js";
import { parseRetrieveRequest, type RetrieveResponse } from "./retrieve/schemas.js";

export type AgentRunner = (request: unknown) => Promise<AgentChatResponse>;
export type Extractor = (request: unknown) => Promise<ExtractedKnowledge>;
export type TagInitializer = (request: unknown) => Promise<TagTree>;
export type RetrieveRunner = (request: unknown) => Promise<RetrieveResponse>;

export type ServerOptions = {
  agentRunner?: AgentRunner;
  extractor?: Extractor;
  tagInitializer?: TagInitializer;
  retrieveRunner?: RetrieveRunner;
};

const MAX_BODY_BYTES = 5 * 1024 * 1024;

function writeCorsHeaders(response: ServerResponse): void {
  response.setHeader("access-control-allow-origin", process.env.AGENT_AI_CORS_ORIGIN ?? "*");
  response.setHeader("access-control-allow-methods", "GET,POST,OPTIONS");
  response.setHeader("access-control-allow-headers", "content-type,x-workspace-id");
}

function sendJson(response: ServerResponse, statusCode: number, payload: unknown): void {
  const body = JSON.stringify(payload);
  writeCorsHeaders(response);
  response.writeHead(statusCode, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(body),
  });
  response.end(body);
}

async function readJsonBody(request: IncomingMessage, maxBytes = MAX_BODY_BYTES): Promise<unknown> {
  const chunks: Buffer[] = [];
  let totalBytes = 0;

  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk));
    totalBytes += buffer.byteLength;
    if (totalBytes > maxBytes) {
      throw new Error("Request body too large");
    }
    chunks.push(buffer);
  }

  const rawBody = Buffer.concat(chunks).toString("utf8");
  if (!rawBody.trim()) {
    throw new Error("Request body is required");
  }
  return JSON.parse(rawBody);
}

export function createAgentAiServer(options: ServerOptions = {}): Server {
  const agentRunner = options.agentRunner ?? runAgentChat;
  const extractor = options.extractor ?? extractKnowledge;
  const tagInitializer = options.tagInitializer ?? initializeTags;
  const retrieveRunner =
    options.retrieveRunner ?? ((payload) => runRetriever(parseRetrieveRequest(payload)));

  return createServer(async (request, response) => {
    try {
      if (request.method === "OPTIONS") {
        writeCorsHeaders(response);
        response.writeHead(204);
        response.end();
        return;
      }

      if (request.method === "GET" && request.url === "/health") {
        sendJson(response, 200, { status: "ok", service: "agent-ai" });
        return;
      }

      if (request.method === "POST" && request.url === "/agent/chat") {
        const payload = await readJsonBody(request, 1024 * 1024);
        const result = await agentRunner(payload);
        sendJson(response, 200, result);
        return;
      }

      if (request.method === "POST" && request.url === "/extract") {
        const payload = await readJsonBody(request);
        const result = await extractor(payload);
        sendJson(response, 200, result);
        return;
      }

      if (request.method === "POST" && request.url === "/init-tags") {
        const payload = await readJsonBody(request);
        const result = await tagInitializer(payload);
        sendJson(response, 200, result);
        return;
      }

      if (request.method === "POST" && request.url === "/retrieve") {
        const payload = await readJsonBody(request, 1024 * 1024);
        const result = await retrieveRunner(payload);
        sendJson(response, 200, result);
        return;
      }

      sendJson(response, 404, { error: "not found" });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      sendJson(response, 500, { error: message });
    }
  });
}

export async function startServer(): Promise<Server> {
  const host = process.env.AGENT_AI_HOST ?? "127.0.0.1";
  const port = Number(process.env.AGENT_AI_PORT ?? "8766");
  const server = createAgentAiServer();

  await new Promise<void>((resolve) => {
    server.listen(port, host, resolve);
  });

  console.error(`agent-ai server listening on http://${host}:${port}`);
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  startServer().catch((error: unknown) => {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    process.exitCode = 1;
  });
}
