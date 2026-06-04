# Retrieve 多租户域 + Catalog API + Retriever 编排 — 变更文档

> 日期: 2026-06-03 | 本地 OpenSpec 变更名: `mvp-retrieve-domains`（`openspec/` 不提交远程，见 `docs/README.md`）

## 概述

本次变更打通 **Retriever 端到端检索**：PostgreSQL 按 `(workspace_id, domain_id)` 分区知识数据；Python 提供 **目录 API**（domains / tag-tree / search）；TypeScript `packages/agent-ai` 实现 **两阶段 LLM + 检索循环**，主 Agent 通过 `retrieve` tool 进程内调用。

### 关键数字

| 指标 | 说明 |
|------|------|
| 新增表 | `knowledge_domains` |
| 分区列 | `tags` / `pages` / `raw_chunks` 增加 `workspace_id`、`domain_id` |
| 新增/调整 API | `GET /retrieve/domains`、`GET /retrieve/domains/{domain}/tag-tree`；`POST /retrieve/search` 必填 `domain` |
| 移除 API | `POST /retrieve/context`、`POST /retrieve/tags` |
| BREAKING | Search hit 响应不再包含 `original_text` |
| TS 包 | `packages/agent-ai`（retrieve 子模块 + `retriever-sessions` 调试日志） |

---

## 背景与动机

- 原 `POST /api/v1/retrieve/context` 为 stub，无法按 workspace 列出知识域或加载标签树。
- 知识表无租户/域分区，检索无法限定在正确 `pages` 集合。
- Retriever 编排需与产品约定一致：**先 domains → kickoff 选域 → tag-tree → 第二轮 LLM 规划 → 带 domain 的 search 循环**。

---

## 数据库（`apps/backend/src/schema.sql`）

### 新增 `knowledge_domains`

```sql
PRIMARY KEY (workspace_id, domain_id)
-- label, description, initialized_at, created_at
```

- `init_tags` 成功持久化标签后，在同一事务内写入/更新本表并设置 `initialized_at`。
- `GET /retrieve/domains` 仅读本表（不扫 `tags` 推断域）。

### 分区与约束

| 表 | 变更 |
|----|------|
| `tags` | `workspace_id`, `domain_id`；`UNIQUE (workspace_id, domain_id, path)`；FK → `knowledge_domains` |
| `pages` | `workspace_id`, `domain_id`；FK → `knowledge_domains` |
| `raw_chunks` | `workspace_id`, `domain_id` |

标签 path 仍为 **ltree `foo.bar`**，`domain` 在请求体/列中单独传递，**不**写入 path 前缀。

> MVP 无历史数据迁移脚本；开发库需按 `apps/backend/README.md` 重置 schema 后重新 `init_tags` + ingest。

---

## Python API

### Catalog

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/retrieve/domains` | 返回 `{ domains[], domain_count }`；需 `X-Workspace-ID` |
| GET | `/api/v1/retrieve/domains/{domain}/tag-tree` | 返回 `{ domain, tag_tree }`；域不存在 → 404 |

### Search（变更）

```json
{
  "domain": "university_policy",
  "query": {
    "sanitize_query_for_prompt": "...",
    "target_tags": ["functional_area.academics_double_major"],
    "time_range": null
  },
  "top_k": 10,
  "exclude_page_ids": []
}
```

- 所有检索 SQL 按 `(workspace_id, domain_id)` 过滤。
- 响应 hit：**无** `original_text`；含 `compiled_truth`、`tag_paths`、`score_breakdown` 等。
- `degraded` 示例：`semantic_disabled_no_embeddings`（`pages.truth_embedding` 为空）、`time_channel_skipped`（未传 `time_range`）。

### `init_tags`（`POST /api/v1/init/tags`）

- 从 header 读取 `workspace_id`。
- 在 **同一 DB 事务** 中：先 upsert `knowledge_domains`，再插入 `tags`，最后 `initialized_at`。
- 实现：`application/init/handlers.py` + `knowledge_catalog_repo.upsert_knowledge_domain_on_connection`。

### 主要代码路径

```
api/v1/retrieve.py
application/retrieve/catalog_handlers.py   # ListRetrieveDomains, GetDomainTagTree
application/retrieve/handlers.py         # SearchKnowledge
application/retrieve/pipeline.py         # RRF 四路融合
infrastructure/db/repositories/knowledge_search_repo.py
infrastructure/db/repositories/knowledge_catalog_repo.py
application/init/handlers.py
```

---

## TypeScript（`packages/agent-ai`）

### Retriever 流程

```mermaid
sequenceDiagram
  participant Main as MainAgent
  participant Loop as runRetriever
  participant Py as Python :8000
  participant LLM as RetrieverAgent

  Main->>Loop: retrieve tool（无 domain/tagTree）
  Loop->>Py: GET /retrieve/domains
  Loop->>LLM: kickoff（仅 domains）
  LLM-->>Loop: selectedDomain
  Loop->>Py: GET /domains/{domain}/tag-tree
  Loop->>LLM: tag-tree 轮（规划 targetTags + queries）
  loop 直至 sufficient
    Loop->>Py: POST /retrieve/search { domain, query }
    Loop->>LLM: 本轮 hits 反馈
  end
  Loop-->>Main: answerGuidance + excerpts
```

### 关键文件

| 文件 | 职责 |
|------|------|
| `retrieve/retrieve-context-client.ts` | `fetchDomains()`、`fetchTagTree(domain)` |
| `retrieve/loop.ts` | 编排 + `sessionRounds` + 写入 retriever-sessions |
| `retrieve/search-client.ts` | POST search，body 带 `domain` |
| `retrieve/retriever-messages.ts` | kickoff / tag-tree / round 用户消息 |
| `agent/tools/registry.ts` | 主 Agent `retrieve` tool；传入 chat `sessionId` |
| `utils/session-store.ts` | `data/retriever-sessions/{sessionId}.jsonl` |

### 主 Agent 隔离

- `retrieve` tool schema **不得**包含 `domain`、`tagTree`、`targetTags` 等（仅 `contextSummary`、`questionRestatement`、`searchQueries`）。
- 主 Agent `details` 仅 `{ sufficient, excerptCount }`；完整轮次在 `retriever-sessions` 与 HTTP 响应 `sessionRounds` 中。

### 默认 workspace

- `DEFAULT_WORKSPACE_ID = 00000000-0000-0000-0000-000000000001`（须为 UUID，不可用 `"default"`）。
- Web/联调常用租户示例：`00000000-0000-0000-0000-000000000101`。

---

## 调试与日志

| 用途 | 位置 |
|------|------|
| Retriever 逐步 trace | `packages/agent-ai/data/retriever-sessions/{sessionId}.jsonl` |
| 环境变量 | `AGENT_AI_RETRIEVER_SESSION_DIR` 可覆盖目录 |
| 主 Agent 对话 | `packages/agent-ai/data/agent-sessions/` |
| Python HTTP / 检索 | `apps/backend/data/logs/backend.log`（须从 `apps/backend` 启动 :8000） |

`retrieveTrace` 阶段：`start` → `domains` → `llm_kickoff` → `tag_tree` → `llm_plan` → `search_round` → `llm_round` → `complete`；末尾 `toolResult`（`toolName: "retrieve"`）。

> **注意**：跑 `pnpm check:agent-ai` 会向 `retrieve.jsonl` 写入 **单元测试 mock** 数据，勿与真实 E2E 混淆。真实 Web 会话文件名形如 `web-{uuid}.jsonl`。

---

## 本地验证

```bash
# 1. 启动服务
pnpm serve:agent-ai
cd apps/backend && python run.py

# 2. 初始化域与标签（示例）
curl -X POST http://127.0.0.1:8000/api/v1/init/tags \
  -H "Content-Type: application/json" \
  -H "X-Workspace-ID: 00000000-0000-0000-0000-000000000101" \
  -d '{"domain":"university_policy","description":"高校学籍与选课政策"}'

# 3. 目录 API
curl http://127.0.0.1:8000/api/v1/retrieve/domains \
  -H "X-Workspace-ID: 00000000-0000-0000-0000-000000000101"

# 4. 自动化
cd apps/backend && python -m pytest tests/test_api_contracts.py tests/test_retrieve_pipeline.py tests/test_init_tags_handler.py -q
pnpm check:agent-ai
```

---

## 手动测试结论（2026-06-03）

在 workspace `…000101`、`university_policy` 下 E2E 验证：

| 项 | 结果 |
|----|------|
| `GET /retrieve/domains` | 与 trace 一致，1 个已初始化域 |
| Retriever 选域 | `university_policy` |
| 标签树 | 约 3.7k 字符，真实 DB |
| 检索 | 链路通；`semantic_disabled_no_embeddings` 因 `truth_embedding` 为空 |
| 语料 | 当前仅 1 篇 page（选课操作说明），与「申请辅修双学位」问题匹配度有限 |
| 标签 | 文档 tag 含 `registration_course`，LLM 常筛 `academics_double_major`，易导致第 2+ 轮 0 命中 |

改进检索质量（非本变更代码范围，但联调相关）：

1. 补 ingest 文档并打齐标签。
2. 配置 embedding 并回填 `pages.truth_embedding`。
3. 保证 `init_tags` 与检索使用 **同一** `X-Workspace-ID`。

---

## BREAKING 变更清单

1. 删除 `POST /api/v1/retrieve/context`、`POST /api/v1/retrieve/tags`。
2. `POST /api/v1/retrieve/search` 请求体 **必须** 含 `domain`。
3. Search 响应 hit **移除** `original_text`。
4. 旧库无 `knowledge_domains` / 分区列时需 **重建 schema**，不能热升级旧数据。

---

## 相关文档（远程仓库）

- 本文件：`docs/2026-06-03-mvp-retrieve-domains-implementation.md`
- 后端说明：`apps/backend/README.md`
- Agent-ai：`packages/agent-ai/README.md`
- 开发手册：`docs/dev.md`（接口表与联调）

本地 OpenSpec 归档（不 push）：`openspec/changes/archive/2026-06-03-mvp-retrieve-domains/`、`openspec/retrieve-pipeline.md`
