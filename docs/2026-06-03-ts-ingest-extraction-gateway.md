# Ingest 提取迁移至 TypeScript（pi-ai）— 变更文档

> 日期: 2026-06-03 | 本地 OpenSpec 变更名: `migrate-ingest-extraction-to-ts-pi-ai`（`openspec/` 不提交远程，见 `docs/README.md`）

## 概述

将 Ingest 管道的 **LLM 结构化提取** 从 Python LangChain 迁至 TypeScript `@earendil-works/pi-ai` HTTP 网关；Python 仍负责上传、解析、分块、标签查询与 PostgreSQL 事务持久化。

> **说明**：实现已合并进统一包 `packages/agent-ai`（原变更中的 `packages/ingest-ai` 概念）。网关端点：`POST /extract`、`POST /init-tags` 等，默认 `127.0.0.1:8766`。

---

## 动机

- 模型网关与 Agent/Retriever 统一为 TS + pi 生态，避免 Python/TS 双套 LLM 调用逻辑。
- 提取边界清晰：Python = 文档与 DB；TS = prompt 组装 + tool-call 校验 + 模型调用。

---

## 变更摘要

| 领域 | 内容 |
|------|------|
| Node | 要求 **>= 22.19.0**（支持 `@earendil-works/*`） |
| TS 网关 | `POST /extract`：五字段 `emit_extracted_knowledge`（TypeBox + `validateToolCall`） |
| Python | `TsExtractionAdapter` HTTP 调用 TS；`IngestPipelineUseCase` 接入 |
| 分块默认 | `chunk_size=1500`，`chunk_overlap=150`（与文档对齐） |
| 持久化修复 | `effective_range` 写入 `raw_chunks` / `pages`；upload 传递真实 `X-Workspace-ID` |
| Skill | 仍从 `apps/skills/knowledge-extraction/references/` 加载领域 prompt |

---

## 架构边界

```
POST /api/v1/ingest/upload  (Python FastAPI)
  → DocumentLoader + RecursiveChunker
  → serialize_tag_tree (Python DB)
  → HTTP POST :8766/extract  (agent-ai)
       system: 领域 prompt.md
       user: AVAILABLE TAGS + TEXT TO ANALYZE
       tool: emit_extracted_knowledge
  → KnowledgeAsyncRepository 单事务落库
```

`POST /api/v1/init/tags`（Python 固定工作流）内部调用 `:8766/init-tags` 生成标签树，再写 `tags` 表（2026-06-03 检索变更后同时写 `knowledge_domains`）。

---

## 配置

| 变量 | 说明 |
|------|------|
| `INGEST_AI_BASE_URL` | Python 调 TS 提取，默认 `http://127.0.0.1:8766` |
| `AGENT_AI_BASE_URL` | Agent 对话网关，默认同上 |
| `LLM_API_KEY` / 模型相关 | TS 侧 `readModelGatewayConfig()`，需 Node 进程可读 |

---

## 验证

```bash
pnpm serve:agent-ai
cd apps/backend && python run.py

pnpm check:agent-ai
cd apps/backend && python -m pytest tests/test_ingest_pipeline.py tests/test_api_contracts.py -q
```

---

## 与后续 Retrieve 变更的关系

- Ingest 写入的 `workspace_id`、`domain_id`（upload body / header）为检索分区提供数据基础。
- `init_tags` 在检索 MVP 中扩展为注册 `knowledge_domains`；见 [2026-06-03-mvp-retrieve-domains-implementation.md](./2026-06-03-mvp-retrieve-domains-implementation.md)。

---

## 相关文档（远程仓库）

- 本文件与 [2026-05-09-ingest-pipeline-implementation.md](./2026-05-09-ingest-pipeline-implementation.md)
- 开发手册：`docs/dev.md`（命令与接口表）

本地 OpenSpec 归档（不 push）：`openspec/changes/archive/2026-06-03-migrate-ingest-extraction-to-ts-pi-ai/`、`openspec/ingest-pipeline.md`
