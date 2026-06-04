import { test } from "node:test";
import assert from "node:assert/strict";

import {
  createRetrieveContextClient,
  parseDomainTagTreeResponse,
  parseRetrieveDomainsResponse,
} from "../src/retrieve/retrieve-context-client.js";

test("parseRetrieveDomainsResponse normalizes fields", () => {
  const ctx = parseRetrieveDomainsResponse({
    domains: [
      { id: "general", label: "通用", initialized: true },
      { id: "university_policy", label: "校规", initialized: false },
    ],
    domain_count: 2,
  });
  assert.equal(ctx.domainCount, 2);
  assert.equal(ctx.domains.length, 2);
  assert.equal(ctx.domains[0]!.id, "general");
});

test("parseDomainTagTreeResponse normalizes tag_tree", () => {
  const ctx = parseDomainTagTreeResponse("general", {
    domain: "general",
    tag_tree: "functional_area.registration",
  });
  assert.equal(ctx.domain, "general");
  assert.match(ctx.tagTree, /registration/);
});

test("createRetrieveContextClient uses GET domains and tag-tree", async () => {
  const calls: { url: string; workspaceId: string }[] = [];
  const client = createRetrieveContextClient({
    pythonApiBaseUrl: "http://py.test",
    workspaceId: "00000000-0000-0000-0000-000000000001",
    fetchFn: async (url, init) => {
      calls.push({
        url: String(url),
        workspaceId: String(
          (init?.headers as Record<string, string>)["x-workspace-id"],
        ),
      });
      if (String(url).endsWith("/domains")) {
        return new Response(
          JSON.stringify({
            domains: [{ id: "general", label: "general", initialized: true }],
            domain_count: 1,
          }),
          { status: 200, headers: { "content-type": "application/json" } },
        );
      }
      return new Response(
        JSON.stringify({ domain: "general", tag_tree: "tag.a" }),
        { status: 200, headers: { "content-type": "application/json" } },
      );
    },
  });

  const domains = await client.fetchDomains();
  assert.equal(domains.domainCount, 1);
  const tree = await client.fetchTagTree("general");
  assert.equal(tree.tagTree, "tag.a");
  assert.equal(calls.length, 2);
  assert.match(calls[0]!.url, /\/api\/v1\/retrieve\/domains$/);
  assert.match(calls[1]!.url, /\/api\/v1\/retrieve\/domains\/general\/tag-tree$/);
  assert.equal(calls[0]!.workspaceId, "00000000-0000-0000-0000-000000000001");
});
