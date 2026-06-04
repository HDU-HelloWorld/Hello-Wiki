# Hello-Wiki 开发与联调指南

> 原仓库根目录 `README.md` 的开发说明已迁移至此。快速了解项目见根目录 [README.md](../README.md)。

`hello-wiki` 是面向**特定领域的 RAG 知识助手** monorepo（设计说明与检索逻辑见根目录 [**README.md**](../README.md)）。

基于 **pnpm workspace**：

| 路径 | 说明 |
|------|------|
| `apps/web` | Next.js 16 + React 19 + TypeScript + Tailwind CSS v4 |
| `apps/backend` | FastAPI（Clean Architecture + CQRS + DDD）+ Ingest + Retrieve API |
| `packages/agent-ai` | 统一 TS LLM 网关（Agent、Ingest 提取、Retriever、会话 JSONL） |
| `apps/skills/` | 可定制 Skill（`tag-initialize`、`knowledge-extraction`） |

---

## 职责边界（主规范）

**Python（`apps/backend`）** 只负责两类事：

1. **Wiki 界面所需的数据与展示 API** — 文件 Wiki 的 CRUD/树/统计（`api/v1/wiki`），以及 Web 管理端依赖的 workspace、文档列表、任务状态等 HTTP 契约。
2. **数据库与确定性能力** — PostgreSQL 读写、Ingest 管道编排（分块、落库、embedding 回填）、`init_tags` 落库、`retrieve` 的 catalog/search（RRF，无 LLM）。需要模型输出时，Python **只转发 HTTP** 到 TS，不在本进程内调 Chat/Completion。

**TypeScript（`packages/agent-ai`）** 负责所有 **LLM 与上下文**：

- 主 Agent 对话、工具循环、Retriever 多轮编排与 prompt 组装。
- Ingest 结构化提取、`init-tags` 标签树生成。
- 会话与检索 trace 的 JSONL（`agent-sessions`、`retriever-sessions`）。

| 放在哪 | 典型能力 | 禁止 |
|--------|----------|------|
| Python | Wiki API、ingest/upload+compile 触发、retrieve domains/tag-tree/search、向量回填脚本 | 在 Python 内直接调 LLM 做业务推理（应用层应走 TS 网关） |
| TS | `/agent/chat`、`/extract`、`/init-tags`、`runRetriever` | 直连 DB、拼 SQL/ltree、携带表结构进主 Agent tool 参数 |
| Web | UI；`/chat` 可直连 `:8766`；其余业务调 `:8000` | 把 DB 字段名/检索实现细节写进 Agent prompt |

联调时默认 **两个进程**：`:8000`（Python）+ `:8766`（TS）。`POST /api/v1/agent/chat` 是 Python 对 TS 的代理，便于统一带 `X-Workspace-ID`；与 `/chat` 直连 TS 等价，均不得绕过上述边界。

---

## 当前开发进度

### Web（`apps/web`）

- [x] Next.js 工程、shadcn 侧边栏、12 个业务模块路由
- [x] 前端 API 客户端（Python 固定工作流 + TS Agent Chat）
- [x] `/chat`：`AgentChatConsole` 直连 `agent-ai` `/agent/chat`（主对话路径）
- [x] `/knowledge`：上传 + `POST /api/v1/ingest/documents/{id}/compile` 触发采编管道
- [x] `/` → `/home`，`/login`、`/about`；`/compile` 重定向至 `/knowledge`

### Backend（`apps/backend`）

- [x] 分层骨架、PostgreSQL + pgvector（`deploy/dev/docker-compose.yml`）
- [x] Ingest：`/ingest/upload`、文档列表、`/ingest/documents/{id}/compile`（异步跑完整 ingest 管道）
- [x] `POST /api/v1/init/tags`（同事务写入 `knowledge_domains` + `tags`）
- [x] **智能对话**：`POST /api/v1/agent/chat` → TS Agent（`retrieve` 等 tool 在 TS 内执行）
- [x] Retrieve：`GET /retrieve/domains`、`GET .../tag-tree`、`POST /retrieve/search`（必填 `domain`，按 workspace 分区）
- [x] 已移除遗留 `chat/ask`、`chat/stream`、`ingest/compile`（Markdown 直编）路由

### Agent-ai（`packages/agent-ai`）

- [x] `/agent/chat`、JSONL 会话（`data/agent-sessions/`）
- [x] `/extract`、`/init-tags`
- [x] `runRetriever`：domains → kickoff 选域 → tag-tree → 检索循环；trace 写入 `data/retriever-sessions/`
- [x] Insight **编排已接入**：每轮 search 与 Python 慢路径并行调用 `insightClient.search`
- [ ] Insight **库检索未实现**：`insight-client.ts` 恒 `skipped: true`、无 hits（预留接口，不影响主路径 RRF）

### 主路径入口

| 能力 | 入口 |
|------|------|
| 智能问答 | Web `/chat` 或 `POST /api/v1/agent/chat`（转发 TS） |
| 文档采编 | `/knowledge` + `POST /api/v1/ingest/documents/{id}/compile` |

---

## 环境要求

- **Node.js** >= 22.19.0
- **pnpm** 10
- **Python** 3.11+（`apps/backend`）
- **Docker**（本地 PostgreSQL / Redis，见 `apps/backend/deploy/dev`）

安装 pnpm：[pnpm 安装文档](https://pnpm.io/installation)

---

## 本地开发

在仓库根目录：

| 命令 | 说明 |
|------|------|
| `pnpm install` | 安装 workspace 依赖 |
| `pnpm dev` | 并行启动 web + backend |
| `pnpm serve:agent-ai` | TS 网关（默认 `127.0.0.1:8766`） |
| `pnpm check:agent-ai` | agent-ai 类型检查 + 测试 |
| `pnpm build` / `pnpm lint` | Web 构建 / ESLint |

### 推荐联调顺序

完整步骤见根目录 [**README.md — 快速开始**](../README.md#快速开始)（**仓库根**执行 Docker / uv / 启动命令）。简要顺序：

1. `docker compose -f apps/backend/deploy/dev/docker-compose.yml up -d`
2. `cp apps/backend/.env.example apps/backend/.env`，配置 `LLM_API_KEY`
3. `uv sync --directory apps/backend --extra dev`（或 pip 安装，见 README）
4. 仓库根：`pnpm install && pnpm --filter agent-ai build`
5. `pnpm serve:agent-ai`（`:8766`）
6. `uv run --directory apps/backend python run.py`（`:8000`；日志 `apps/backend/data/logs/backend.log`）
7. `pnpm dev`（Web `:3000`）

### 访问地址

| 服务 | URL |
|------|-----|
| Web | http://localhost:3000 |
| Backend API | http://127.0.0.1:8000/api/v1 |
| Backend health | http://127.0.0.1:8000/health |
| Agent-ai | http://127.0.0.1:8766/health |

### 多租户 Header

请求 Python API 时携带 UUID：

```http
X-Workspace-ID: 00000000-0000-0000-0000-000000000001
```

联调示例租户：`00000000-0000-0000-0000-000000000101`。`init_tags`、ingest、retrieve 须使用**同一** workspace。

---

## API 与路由速查

### Web 路由

`/home`、`/knowledge`、`/chat`、`/wiki`、`/ops`、`/audit`、`/simulation`、`/channels`、`/permissions`、`/devops`、`/settings`、`/login`、`/about` 等（`/compile` → `/knowledge`）。

### Backend（`:8000`）

| 端点 | 状态 | 说明 |
|------|------|------|
| `GET /health` | ✅ | 健康检查 |
| `POST /api/v1/agent/chat` | ✅ | **主对话**（转发 TS Agent，含 retrieve） |
| `POST /api/v1/ingest/upload` | ✅ | 文件上传 |
| `GET /api/v1/ingest/documents` | ✅ | 采编文档列表 |
| `POST /api/v1/ingest/documents/{id}/compile` | ✅ | **主采编**（触发 ingest 管道） |
| `GET /api/v1/ingest/status/{task_id}` | ✅ | 任务进度 |
| `POST /api/v1/init/tags` | ✅ | 标签树 + `knowledge_domains` |
| `GET /api/v1/retrieve/domains` | ✅ | 知识域列表 |
| `GET /api/v1/retrieve/domains/{domain}/tag-tree` | ✅ | 域内标签树 |
| `POST /api/v1/retrieve/search` | ✅ | RRF 检索（body 必填 `domain`） |
| Wiki CRUD / tree / stats | ✅ | 文件 Wiki 层 |

Search 响应 hit **不含** `original_text`。`degraded` 常见：`semantic_disabled_no_embeddings`（未回填 `truth_embedding`）、`time_channel_skipped`。

### TS Gateway（`:8766`）

| 端点 | 说明 |
|------|------|
| `POST /agent/chat` | 主 Agent |
| `POST /extract` | Ingest 结构化提取 |
| `POST /init-tags` | 标签树生成 |
| `POST /retrieve` | Retriever（主 Agent 也可进程内 `runRetriever`） |

**边界（同上）**：Python 提供 Wiki + DB API；TS 提供全部 LLM 与上下文。领域 prompt 在 `apps/skills/`；内置模板在 `packages/agent-ai/prompts/`。

---

## 项目结构

```
hello-wiki/
├── apps/
│   ├── web/
│   ├── backend/
│   │   ├── deploy/dev/       # Docker PG + Redis
│   │   └── src/
│   │       ├── api/
│   │       ├── application/  # agent, init, ingest, retrieve, chat, wiki
│   │       ├── domain/
│   │       ├── infrastructure/
│   │       └── core/
│   └── skills/
├── packages/agent-ai/
│   ├── prompts/
│   ├── src/retrieve/
│   └── data/                 # agent-sessions / retriever-sessions（本地，勿提交）
├── docs/                     # 变更文档 + 本文件
└── package.json
```

---

## 调试

| 用途 | 路径 |
|------|------|
| Retriever 逐步 trace | `packages/agent-ai/data/retriever-sessions/{sessionId}.jsonl` |
| 主 Agent 会话 | `packages/agent-ai/data/agent-sessions/` |
| Python 请求日志 | `apps/backend/data/logs/backend.log`（从 `apps/backend` 启动） |

环境变量：`AGENT_AI_RETRIEVER_SESSION_DIR`、`AGENT_AI_SESSION_DIR`、`LOG_FILE_PATH` 等见各包 README。

---

## 后续任务

| 优先级 | 任务 | 说明 |
|--------|------|------|
| **高** | Embedding 回填 | 填充 `pages.truth_embedding`，启用语义检索通道 |
| **高** | 知识库内容 | 按域 ingest 政策类文档，标签与 Retriever `target_tags` 对齐 |
| **中** | Pages/Tags 管理 API | 除 ingest/init 外的可视化 CRUD |
| **中** | 扫描件 PDF | MinerU / OCR 接入 |
| **低** | Insight 库 | 实现 insight 库语义/关键词检索，替代 `insight_fast_path_not_implemented` |

---

## 协作、CI 与提交

### Pull Request

1. `git checkout main && git pull`
2. 分支：`feat/`、`fix/`、`docs/`
3. 自测：`pnpm lint`、`pnpm build`、`pnpm check:agent-ai`；backend：`pnpm check:backend`（或 `cd apps/backend && mypy src`）、`pytest`、`lint-imports`
4. 提 PR，等 CI 绿灯后合并

### CI（`.github/workflows/ci.yml`）

`pnpm install --frozen-lockfile` → `lint` → `build` → `check:agent-ai`（backend 检查以 workflow 为准）。

### Commit 前缀

`feat` / `fix` / `docs` / `refactor` / `test` / `chore` 等（Conventional Commits）。

**勿提交**：`openspec/`（已 gitignore）、`*-sessions/*.jsonl`、`apps/backend/data/logs/`。

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [docs/README.md](./README.md) | 变更文档索引 |
| [2026-05-09-ingest-pipeline-implementation.md](./2026-05-09-ingest-pipeline-implementation.md) | 首版 Ingest |
| [2026-06-03-ts-ingest-extraction-gateway.md](./2026-06-03-ts-ingest-extraction-gateway.md) | TS 提取网关 |
| [2026-06-03-mvp-retrieve-domains-implementation.md](./2026-06-03-mvp-retrieve-domains-implementation.md) | Retrieve MVP |
| [apps/backend/README.md](../apps/backend/README.md) | 后端架构与 schema |
| [packages/agent-ai/README.md](../packages/agent-ai/README.md) | Retriever 隔离原则 |

---

## 外部参考

- [Next.js 文档](https://nextjs.org/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [pnpm Workspace](https://pnpm.io/workspaces)
