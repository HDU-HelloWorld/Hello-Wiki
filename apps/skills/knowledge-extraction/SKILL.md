---
name: knowledge-extraction
description: Extract structured knowledge (summary, compiled truth, tags, temporal range) from text chunks during ingest Step 2. Uses domain-specific references that customize the output schema and prompt. The prompt is composed from the reference's system prompt plus the tag hierarchy injected into the user message.
license: MIT
compatibility: Requires the TypeScript ingest extraction gateway (`packages/ingest-ai`) with `@earendil-works/pi-ai` tool-call support.
metadata:
  author: Hello-Wiki
  version: "0.2.0"
  stage: mvp
---

# Knowledge Extraction Skill

Extract structured knowledge from a single text chunk. Invoked once per chunk during the ingest pipeline (Text → Structured JSON). The TypeScript gateway builds `pi-ai` context and requires the model to call `emit_extracted_knowledge`. The output fills schema.sql columns that require LLM population: `raw_chunks.summary`, `pages.title`, `pages.compiled_truth`, `raw_chunks.effective_range` / `pages.effective_range`, and `tags` (via `suggested_tags` → `page_tags`). `raw_chunks.extra_metadata` is populated by the parser/persistence layer with file metadata — the LLM does not touch it.

---

## Prompt Composition

The LLM call uses a two-message structure:

```
┌────────────────────────────────────────────────┐
│ SYSTEM PROMPT (reference/prompt.md)            │
│                                                │
│ • Domain knowledge & extraction rules          │
│ • Output format specification (JSON example    │
│   matching the template.json schema)           │
│ • Guardrails                                   │
│ • Context placeholders filled at runtime:      │
│   {source_document}, {source_page},            │
│   {chunk_index}, {total_chunks}                │
├────────────────────────────────────────────────┤
│ USER PROMPT (built at runtime)                 │
│                                                │
│ AVAILABLE TAGS                                 │
│ ──────────────                                 │
│ {indented tag tree from serialize_tag_tree()}  │
│                                                │
│ TEXT TO ANALYZE                                │
│ ────────────────                               │
│ {chunk_text}                                   │
└────────────────────────────────────────────────┘
```

**System prompt**: the preset rules from the selected reference's `prompt.md`. Contains extraction rules and an output format example. Context variables (`{source_document}`, `{source_page}`, `{chunk_index}`, `{total_chunks}`) are injected at runtime.

**User prompt**: the tag tree (queried from `SELECT name, label, level, is_leaf, path FROM tags ORDER BY path` and serialized with `serialize_tag_tree()`) + the chunk text.

**Structured output**: `packages/ingest-ai` exposes a TypeBox schema as the `emit_extracted_knowledge` tool and validates the model tool call before returning JSON to Python. The model MUST call that tool with valid arguments matching the schema.

---

## Domain Reference Selection

The skill resolves the reference by matching `domain` against `references/index.yaml`:

| Reference | When |
|---|---|
| `general` | Mixed-content or unspecified domain (default fallback) |
| `university_policy` | Higher education administration documents |

**Selection logic**: match `domain` → reference `id`. No match → fallback to `default: true`.

Each reference provides:
- `template.json` — JSON Schema documentation for the extraction output contract. The runtime TypeScript schema in `packages/ingest-ai` enforces the shared fields used by Python persistence.
- `prompt.md` — System prompt with domain-specific extraction rules.

---

## Output Fields

| Field | Required | Schema.sql Target |
|---|---|---|
| `chunk_summary` | ✅ | `raw_chunks.summary` — also shared to `page_timeline.source_description` |
| `page_title` | ✅ | `pages.title` — trigram fuzzy search index |
| `compiled_truth` | ✅ | `pages.compiled_truth` — primary vector search + QA |
| `suggested_tags[]` | ✅ (2–6) | `tags` table + `page_tags` junction |
| `effective_range{}` | ✅ | `raw_chunks.effective_range` + `pages.effective_range` |

---

## Mapping to Schema.sql Tables

```
chunk_summary  ──→ raw_chunks.summary ──→ page_timeline.source_description (copy)
page_title     ──→ pages.title
compiled_truth ──→ pages.compiled_truth ──→ page_versions.compiled_truth (snapshot)
suggested_tags ──→ tags table ──→ page_tags.page_id + page_tags.tag_id
effective_range──→ raw_chunks.effective_range (tstzrange)
              ──→ pages.effective_range (tstzrange)
```

---

## Guardrails

- **No fabrication**: all 5 fields are REQUIRED. Use `null` for unknown dates in `effective_range`, but always provide a `description` and `stale_risk` assessment. Select at least 2 tags even for ambiguous content — prefer `unknown`/`general` tags over fabrication
- **No evaluation**: extract and synthesize facts as written — do not judge correctness
- **Single-chunk scope**: only extract from THIS chunk
- **Language follows source**: output in the same language as the input
- **Tag tree is authoritative**: use tag names from the injected hierarchy. Propose new leaves only when genuinely needed
