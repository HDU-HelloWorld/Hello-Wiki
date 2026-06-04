export type RetrieveContextClientOptions = {
  pythonApiBaseUrl?: string;
  workspaceId?: string;
  fetchFn?: typeof fetch;
};

const DEFAULT_PYTHON_API_BASE_URL = "http://127.0.0.1:8000";
export const DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001";

export type RetrieveDomain = {
  id: string;
  label: string;
  initialized: boolean;
};

export type RetrieveDomainsResult = {
  domains: RetrieveDomain[];
  domainCount: number;
};

export type DomainTagTreeResult = {
  domain: string;
  tagTree: string;
};

export type RetrieveContextClient = {
  fetchDomains: () => Promise<RetrieveDomainsResult>;
  fetchTagTree: (domain: string) => Promise<DomainTagTreeResult>;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function parseRetrieveDomainsResponse(value: unknown): RetrieveDomainsResult {
  if (!isRecord(value)) {
    throw new Error("Invalid retrieve domains response from Python API");
  }
  const rawDomains = Array.isArray(value.domains) ? value.domains : [];
  const domains: RetrieveDomain[] = rawDomains.map((item, index) => {
    if (!isRecord(item)) {
      throw new Error(`domains[${index}] must be an object`);
    }
    const id = typeof item.id === "string" ? item.id : "";
    if (!id) {
      throw new Error(`domains[${index}].id must be a non-empty string`);
    }
    return {
      id,
      label: typeof item.label === "string" ? item.label : id,
      initialized: item.initialized === true,
    };
  });
  const domainCount =
    typeof value.domain_count === "number" && Number.isFinite(value.domain_count)
      ? Math.trunc(value.domain_count)
      : typeof value.domainCount === "number" && Number.isFinite(value.domainCount)
        ? Math.trunc(value.domainCount)
        : domains.length;
  return { domains, domainCount };
}

export function parseDomainTagTreeResponse(
  domain: string,
  value: unknown,
): DomainTagTreeResult {
  if (!isRecord(value)) {
    throw new Error("Invalid domain tag-tree response from Python API");
  }
  const tagTree =
    typeof value.tag_tree === "string"
      ? value.tag_tree
      : typeof value.tagTree === "string"
        ? value.tagTree
        : "";
  return {
    domain: typeof value.domain === "string" ? value.domain : domain,
    tagTree,
  };
}

/** Load workspace domain catalog and per-domain tag trees from Python (Retriever-only). */
export function createRetrieveContextClient(
  options: RetrieveContextClientOptions = {},
): RetrieveContextClient {
  const pythonApiBaseUrl =
    options.pythonApiBaseUrl ??
    process.env.AGENT_AI_PYTHON_API_BASE_URL ??
    process.env.RETRIEVE_AI_PYTHON_API_BASE_URL ??
    DEFAULT_PYTHON_API_BASE_URL;
  const workspaceId =
    options.workspaceId ??
    process.env.AGENT_AI_WORKSPACE_ID ??
    DEFAULT_WORKSPACE_ID;
  const fetchFn = options.fetchFn ?? fetch;

  const headers = {
    "x-workspace-id": workspaceId,
  };

  return {
    async fetchDomains(): Promise<RetrieveDomainsResult> {
      const response = await fetchFn(`${pythonApiBaseUrl}/api/v1/retrieve/domains`, {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        const body = await response.text();
        throw new Error(`retrieve domains failed: ${response.status} ${body}`);
      }

      return parseRetrieveDomainsResponse(await response.json());
    },

    async fetchTagTree(domain: string): Promise<DomainTagTreeResult> {
      const encoded = encodeURIComponent(domain);
      const response = await fetchFn(
        `${pythonApiBaseUrl}/api/v1/retrieve/domains/${encoded}/tag-tree`,
        {
          method: "GET",
          headers,
        },
      );

      if (!response.ok) {
        const body = await response.text();
        throw new Error(`retrieve tag-tree failed: ${response.status} ${body}`);
      }

      return parseDomainTagTreeResponse(domain, await response.json());
    },
  };
}
