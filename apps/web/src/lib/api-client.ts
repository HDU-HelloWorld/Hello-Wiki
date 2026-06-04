const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000101";

function resolveApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_BASE_URL ?? "/backend";
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL;
}

export const API_BASE_URL = resolveApiBaseUrl();

export const WORKSPACE_ID =
  process.env.NEXT_PUBLIC_WORKSPACE_ID ?? DEFAULT_WORKSPACE_ID;

export type BackendHealth = {
  status: string;
  service: string;
};

export type WorkspaceContext = {
  workspace_id: string;
  trace_id: string;
};

export type WikiPage = {
  id: number;
  title: string;
  content: string;
  tags: string[];
  parent_id: number | null;
  version: number;
  created_at: string;
  updated_at: string;
  created_by: string | null;
};

export type WikiPagesResponse = {
  items: WikiPage[];
  total: number;
};

export type WikiStats = {
  total_pages: number;
  total_tags: number;
  max_version: number;
};

type ApiResult<T> = {
  data: T | null;
  error: string | null;
};

async function parseErrorResponse(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string | object };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // ignore non-json error bodies
  }
  return `${response.status} ${response.statusText}`;
}

async function request<T>(
  path: string,
  init?: RequestInit & { workspace?: boolean; timeoutMs?: number },
): Promise<ApiResult<T>> {
  const headers = new Headers(init?.headers);
  headers.set("Accept", "application/json");

  if (init?.workspace !== false) {
    headers.set("X-Workspace-ID", WORKSPACE_ID);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(init?.timeoutMs ?? 1800),
    });

    if (!response.ok) {
      return { data: null, error: await parseErrorResponse(response) };
    }

    return { data: (await response.json()) as T, error: null };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : "request failed",
    };
  }
}

export async function getBackendHealth() {
  return request<BackendHealth>("/health", { workspace: false });
}

export async function getWorkspaceContext() {
  return request<WorkspaceContext>("/api/v1/workspace/context");
}

export async function getWikiPages() {
  return request<WikiPagesResponse>("/api/v1/wiki/pages?limit=100");
}

export async function getWikiTree() {
  return request<Array<{ id: number; title: string; children: unknown[] }>>(
    "/api/v1/wiki/tree",
  );
}

export async function getWikiStats() {
  return request<WikiStats>("/api/v1/wiki/stats");
}

export type InitTagsResponse = {
  domain: string;
  categories: number;
  leaves: number;
};

export type IngestUploadResponse = {
  document_id: string;
  filename: string;
  status: "pending";
};

export type IngestDocumentItem = {
  document_id: string;
  filename: string;
  domain: string;
  status: "pending" | "compiling" | "compiled" | "partial" | "failed";
  wiki_pages: number;
  uploaded_at: string;
  compile_task_id?: string | null;
  error?: string | null;
};

export type IngestDocumentListResponse = {
  items: IngestDocumentItem[];
  total: number;
};

export type CompileDocumentJobResponse = {
  document_id: string;
  task_id: string;
  status: "compiling";
};

export type IngestStatusResponse = {
  status: "pending" | "running" | "completed" | "failed" | "partial";
  total_chunks: number;
  successful: number;
  failed: number;
  error?: string | null;
  errors?: Array<{ chunk_index?: number; error?: string }>;
};

export async function initTags({
  domain,
  description,
  language = "zh",
}: {
  domain: string;
  description: string;
  language?: string;
}) {
  return request<InitTagsResponse>("/api/v1/init/tags", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ domain, description, language }),
    timeoutMs: 120_000,
  });
}

export async function uploadIngestFile({
  file,
  domain = "general",
}: {
  file: File;
  domain?: string;
}): Promise<ApiResult<IngestUploadResponse>> {
  const formData = new FormData();
  formData.set("file", file);
  formData.set("domain", domain);

  const headers = new Headers();
  headers.set("Accept", "application/json");
  headers.set("X-Workspace-ID", WORKSPACE_ID);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/ingest/upload`, {
      method: "POST",
      headers,
      body: formData,
      signal: AbortSignal.timeout(120_000),
    });

    if (!response.ok) {
      return { data: null, error: await parseErrorResponse(response) };
    }

    return {
      data: (await response.json()) as IngestUploadResponse,
      error: null,
    };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : "request failed",
    };
  }
}

export async function listIngestDocuments(status?: string) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request<IngestDocumentListResponse>(
    `/api/v1/ingest/documents${query}`,
  );
}

export async function compileIngestDocument(documentId: string) {
  return request<CompileDocumentJobResponse>(
    `/api/v1/ingest/documents/${documentId}/compile`,
    {
      method: "POST",
      timeoutMs: 30_000,
    },
  );
}

export async function getIngestStatus(taskId: string) {
  return request<IngestStatusResponse>(`/api/v1/ingest/status/${taskId}`, {
    workspace: false,
    timeoutMs: 10_000,
  });
}
