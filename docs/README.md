# Hello-Wiki 变更文档索引

本目录（`docs/`）是**会提交到远程仓库**的变更说明；供 onboarding 与发布前核对。

日常开发、联调与 API 速查见 **[dev.md](./dev.md)**（由原根目录 `README.md` 迁移并更新）。

## 与 OpenSpec 的关系

仓库根目录的 `openspec/` 已列入 `.gitignore`，**不会 push**（含 `openspec/changes/archive/`、`openspec/ingest-pipeline.md`、`openspec/retrieve-pipeline.md` 等）。OpenSpec 仅作本地提案/归档工作流；对外以本目录文档为准。

| 文档 | 说明 |
|------|------|
| [dev.md](./dev.md) | 开发进度、本地启动、API/路由、调试、CI 与协作（主开发手册） |

### 里程碑变更说明

| 日期 | 文档 | 说明 |
|------|------|------|
| 2026-05-09 | [ingest-pipeline-implementation.md](./2026-05-09-ingest-pipeline-implementation.md) | 首版 Ingest 背景（**文内 API 表部分过时**，文首已标注） |
| 2026-06-03 | [ts-ingest-extraction-gateway.md](./2026-06-03-ts-ingest-extraction-gateway.md) | Ingest 提取迁至 TS（pi-ai），Node 22，effective_range / workspace 修复 |
| 2026-06-03 | [mvp-retrieve-domains-implementation.md](./2026-06-03-mvp-retrieve-domains-implementation.md) | 多租户 knowledge_domains、Retrieve Catalog API、Retriever 两阶段 LLM 编排 |

## 提交建议

- **建议纳入版本库**：`docs/` 下变更文档 + 对应实现代码。
- **勿提交**：`openspec/`（已 ignore）、`packages/agent-ai/data/*-sessions/*.jsonl`、`apps/backend/data/logs/`。
