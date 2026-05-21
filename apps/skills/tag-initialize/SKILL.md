---
name: tag-initialize
description: Generate an initial hierarchical tag taxonomy for a knowledge base domain by calling LLM once. Uses domain-specific references (general, university-policy, etc.) that customize the generation prompt. The output maps to the tags table (ltree paths). The generated 2-level tree is the starting point — deeper nesting emerges naturally during ingest as the extraction LLM splits overcrowded leaf tags into sub-leaves.
license: MIT
compatibility: Requires schema.sql tags table with ltree extension.
metadata:
  author: Hello-Wiki
  version: "0.1.0"
  stage: mvp
---

# Tag Initialize Skill

Generate a domain-specific hierarchical tag taxonomy. Invoked **once** when setting up a new knowledge base. Selects the appropriate domain reference, calls an LLM with the domain-specific prompt, and produces a JSON tag tree ready for insertion into the `tags` table.

---

## Domain Reference Selection

The skill resolves the reference by matching the user's `domain` against `references/index.yaml`:

| Reference | When |
|---|---|
| `general` | Mixed-content or unspecified domain (default fallback) |
| `university_policy` | Higher education administration documents |

**Selection logic**: match `domain` → reference `id`. No match → fallback to the reference with `default: true`.

---

## Input

```json
{
  "domain": "string — domain identifier (e.g. 'university_policy')",
  "description": "string — what content the knowledge base will contain",
  "language": "string — primary language ('zh', 'en', 'mixed')",
  "existing_tags": ["string — tag names already in the system (avoid duplicates)"]
}
```

---

## Output

```json
{
  "domain": "university_policy",
  "generated_at": "2026-05-08T10:00:00Z",
  "categories": [
    {
      "name": "document_type",
      "label": "文档类型",
      "description": "The type or genre of the document, independent of its topic.",
      "leaves": [
        { "name": "policy", "label": "政策文件", "description": "Formal policy documents establishing rules or principles." },
        { "name": "regulation", "label": "管理规定", "description": "Detailed regulations implementing policies." }
      ]
    }
  ]
}
```

---

## Mapping to `tags` Table

The output maps to `tags` as a **2-level hierarchy** (this is the starting point — deeper levels emerge during ingest splitting):

```
Category (level=0, is_leaf=false):
  INSERT INTO tags (name, label, description, parent_id, level, path, is_leaf)
  VALUES ('document_type', '文档类型', '...', NULL, 0, 'document_type', false)

Leaf (level=1, is_leaf=true):
  INSERT INTO tags (name, label, description, parent_id, level, path, is_leaf)
  VALUES ('policy', '政策文件', '...', <category.id>, 1, 'document_type.policy', true)
```

The persistence layer:
1. Inserts category rows (level=0, is_leaf=false, path=name)
2. For each leaf: inserts leaf row (level=1, is_leaf=true, path=`{category_name}.{leaf_name}`, parent_id=category.id)
3. Uses `ON CONFLICT (path) DO NOTHING` for idempotency

---

## How the Tree Grows During Ingest (Not This Skill's Job)

The initial 2-level tree provides the classification backbone. During ingest, the extraction LLM can **split** a leaf that becomes too broad. For example, if `functional_area.examinations` accumulates 200+ documents, the extraction LLM proposes sub-leaves (`makeup`, `midterm`, `final`) and the parent becomes a non-leaf node. This is handled by the ingest persistence layer, not this initialization skill.

---

## Guardrails

- **Domain-driven**: The LLM designs the taxonomy from the domain description + reference prompt, not from a fixed template
- **Initial structure is 2-level**: categories (level 0) → leaves (level 1). Deeper nesting emerges from ingest splitting
- **Idempotent**: Running twice with the same input produces compatible output; `ON CONFLICT (path)` prevents duplicates
- **Naming**: All tag names match `^[a-z][a-z0-9_]*$`
