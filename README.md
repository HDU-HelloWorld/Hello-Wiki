# Hello-Wiki（知原）

**领域 RAG 知识助手** monorepo：面向**特定领域**（高校政策、行业规章等）构建可检索、可对话的结构化知识库，通过「采编 → 标签体系 → 多路检索 → 子智能体迭代 → 主 Agent 作答」完成问答。当前以 **workspace + knowledge domain** 隔离租户与领域；**长期记忆**（跨会话用户画像、任务状态等）计划在后续版本接入，与现有 JSONL 会话并存。

---

## 设计目标

| 目标 | 当前实现 |
|------|----------|
| **领域化** | 每个 `domain` 独立标签树与 `pages` 分区；Retriever 先选域再检索，避免跨域噪声 |
| **结构化知识** | Ingest 将文档分块后经 TS LLM 提取为 `pages`（`compiled_truth`）、`tags`、时间线等，写入 PostgreSQL |
| **可解释检索** | Python 侧四路候选 + RRF 融合，返回 `score_breakdown`；Retriever 多轮阅读 hit 并输出 `answerGuidance` |
| **对话** | 主 Agent 调用 `retrieve` 工具（进程内 `runRetriever`），不把 DB 结构暴露给主 Agent |
| **长期记忆** | **未实现**；规划为 TS 侧记忆层，与 `agent-sessions` / 未来用户级 store 集成 |

---

## 职责边界

| 运行时 | 负责 |
|--------|------|
| **Python** (`apps/backend`) | Wiki 展示 API、PostgreSQL、Ingest 编排与落库、**混合检索（RRF，无 LLM）** |
| **TypeScript** (`packages/agent-ai`) | **全部 LLM** 与 **上下文**（主 Agent、Retriever、提取、`init-tags`、JSONL 会话/trace） |
| **Web** (`apps/web`) | 管理端；`/chat` 可直连 `:8766`，其余业务调 `:8000` |

细则见 [`docs/dev.md`](docs/dev.md#职责边界主规范)。

---

## 端到端数据流

```mermaid
flowchart LR
  subgraph ingest [采编 Python + TS]
    Upload[上传文档] --> Chunk[分块]
    Chunk --> Extract[TS /extract]
    Extract --> PG[(PostgreSQL pages/tags)]
  end
  subgraph catalog [目录 Python]
    Init[TS /init-tags + 落库] --> Domains[GET /retrieve/domains]
    Domains --> TagTree[GET .../tag-tree]
  end
  subgraph retrieve [检索 TS 编排 + Python RRF]
    Main[主 Agent] --> Ret[runRetriever]
    Ret --> Domains
    Ret --> TagTree
    Ret --> Search[POST /retrieve/search]
    Search --> PG
    Ret --> Main
  end
  ingest --> catalog
  catalog --> retrieve
```

1. **`POST /api/v1/init/tags`**：TS 生成标签树 → Python 同一事务写入 `knowledge_domains` + `tags`。
2. **`POST /api/v1/ingest/documents/{id}/compile`**：解析 → 分块 → 每块 TS 提取 → 写入 `raw_chunks` / `pages` / 关联标签（可选 embedding 回填 `pages.truth_embedding`）。
3. **对话**：主 Agent 生成 `searchQueries` → `retrieve` → 下文检索链 → 将 `answerGuidance` 与摘录交回主 Agent 组织用户可见回答。

---

## 检索逻辑（核心）

检索分为 **编排层（TS）** 与 **召回层（Python）**。主 Agent **不**接收 `domain`、`tagTree`、`targetTags` 等 DB 字段（见 `packages/agent-ai/src/agent/tools/registry.ts`）。

### 1. Retriever 编排（`runRetriever`）

| 阶段 | 动作 | 代码入口 |
|------|------|----------|
| 目录 | `GET /api/v1/retrieve/domains` | `retrieve-context-client.ts` |
| Kickoff LLM | 仅看域列表，输出 `selectedDomain` | `formatKickoffUserMessage` → `parseRetrieverDecision` |
| 标签树 | `GET /api/v1/retrieve/domains/{domain}/tag-tree` | 同上 |
| 规划 LLM | 结合 tag 树修订 `targetTags` + `nextSearchQueries` | `formatTagTreeUserMessage` |
| 搜索循环 | 对每个 query 并行：**慢路径** Python search + **快路径** Insight（占位） | `executeSearchPlan` in `loop.ts` |
| 反馈 LLM | 每轮将 hits 摘要喂给 Retriever，判断 `sufficient` / 修订 query | `formatRoundUserMessage` |
| 结束 | 返回 `answerGuidance`、`excerpts`；trace 写入 `data/retriever-sessions/{sessionId}.jsonl` | `session-store.ts` |

默认最多 **8** 轮搜索循环（`maxIterations`）。未选域或 domains 为空时直接结束并提示检查 `init_tags`。

### 2. 单次查询模板（`SearchQuery`）

主 Agent / Retriever 为每路检索提供：

- `sanitize_query_for_prompt`：用于 **BM25**（`raw_chunks.fulltext_search`）与 **语义** query embedding
- `target_tags`：ltree 风格路径，如 `functional_area.academics`（**不含** domain 前缀）
- `time_range`（可选）：用于时间通道；未传则标记 `time_channel_skipped`

`domain` 由 Retriever 在选域后固定在 `search-client` 上，随 `POST /retrieve/search` body 传给 Python。

### 3. Python 四路召回 + RRF（`RetrieveSearchUseCase`）

在 `(workspace_id, domain_id)` 分区内**并行**拉候选，再 **Reciprocal Rank Fusion**（`k=60`，可调权重）：

| 通道 | 默认权重 | 实现要点 |
|------|----------|----------|
| **Tag** | 0.30 | `tag_score`：精确匹配 1.0、子标签 0.5、父级 0.25，单 query 封顶 3.0 |
| **Semantic** | 0.35 | query embedding vs `pages.truth_embedding`（pgvector）；无向量时 `semantic_disabled_no_embeddings` |
| **BM25** | 0.20 | `plainto_tsquery` + `ts_rank` on `raw_chunks.fulltext_search` |
| **Time** | 0.15 | `pages.effective_range` 与 query 时间窗重叠度；未传时间则跳过 |

融合后取 top-K `page_id`，再批量加载 hit 字段（含 `compiled_truth`、`tag_paths`、`score_breakdown`）。响应 **不含** `original_text`（BREAKING，见变更文档）。

`raw_chunks.summary_vector` 的 chunk 级向量检索已在 repo 预留 **未接入** MVP 管道。

### 4. Insight 快路径（预留）

`insight-client.ts` 与慢路径并行调用，当前恒返回 `skipped: true`（`insight_fast_path_not_implemented`），不贡献 hits。对应产品概念中的「逻辑库 / 已结构化 insight」检索，与 `application/dev_step1.md` 中的设想一致，**尚未落地**。

### 5. 联调常见 `degraded` 标记

| 标记 | 含义 |
|------|------|
| `semantic_disabled_no_embeddings` | 该域 `pages.truth_embedding` 未回填 |
| `semantic_disabled_no_embedding_provider` | Python 未配置 embedding 适配器 |
| `time_channel_skipped` | 未提供 `time_range` |

改进检索质量：同 workspace 下执行 `init_tags` → ingest 文档 → `python scripts/backfill_embeddings.py`（见 `apps/backend/README.md`）。

---

## 能做什么（产品能力）

- **知识采编**：`/knowledge` 上传，`documents/{id}/compile` 跑完整 ingest 管道。
- **标签体系**：按领域 `init_tags`，注册 `knowledge_domains`。
- **智能对话**：`/chat` 或 `POST /api/v1/agent/chat`（TS Agent + `retrieve` 工具）。
- **Wiki 浏览**：Python 文件 Wiki API（`api/v1/wiki`），与 PG 知识库并行存在。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js 16、React 19、Tailwind CSS v4 |
| 后端 API | FastAPI、asyncpg、PostgreSQL + pgvector |
| AI 网关 | `packages/agent-ai`（`@earendil-works/pi-ai` / `pi-agent-core`） |
| 包管理 | pnpm workspace |

---

## 快速开始

### 环境要求

- **Node.js** >= 22.19.0、**pnpm** 10
- **Python** 3.11+，推荐安装 **[uv](https://docs.astral.sh/uv/getting-started/installation/)**（管理后端虚拟环境与依赖）
- **Docker**（本地 PostgreSQL + Redis）
- **LLM API Key**（DeepSeek 等 OpenAI 兼容接口；写入 `apps/backend/.env`，TS 网关会读取）

以下步骤均在**仓库根目录**执行（除非注明）。

### 1. 启动数据库（Docker）

```bash
docker compose -f apps/backend/deploy/dev/docker-compose.yml up -d
```

- **PostgreSQL**：`localhost:5432`，库名 `zhiyuan`，用户/密码 `postgres` / `vibe_coding`
- 首次启动会自动执行 `init-extensions.sql` 与 `src/schema.sql`（pgvector + 业务表）
- **Redis**：`localhost:6379`（可选）

检查：`docker compose -f apps/backend/deploy/dev/docker-compose.yml ps` 中 `hwiki-pg` 为 healthy。

### 2. 配置 Python 后端环境

复制并编辑后端环境变量（路径固定在后端包内，便于 agent-ai 读取）：

```bash
# Windows PowerShell
Copy-Item apps/backend/.env.example apps/backend/.env
# macOS / Linux
# cp apps/backend/.env.example apps/backend/.env
```

至少配置 `LLM_API_KEY`；`DATABASE_URL` 默认已与 Docker 一致：

```env
DATABASE_URL=postgresql+asyncpg://postgres:vibe_coding@localhost:5432/zhiyuan
```

#### 方式 A：uv（推荐）

[uv](https://docs.astral.sh/uv/) 会在 `apps/backend` 下创建 `.venv` 并解析 `pyproject.toml`：

```bash
# 安装后端依赖（含 dev 可选组：pytest、ruff 等）
uv sync --directory apps/backend --extra dev

# 在仓库根启动 API（uv 以 apps/backend 为项目根，.env / 日志路径正确）
uv run --directory apps/backend python run.py
```

常用命令（均在仓库根）：

```bash
uv run --directory apps/backend pytest tests/ -q
uv run --directory apps/backend python scripts/backfill_embeddings.py
```

#### 方式 B：pip + venv

```bash
python -m venv apps/backend/.venv
# 激活 apps/backend/.venv 后，在仓库根执行：
pip install -e "./apps/backend[dev]"

# 仍在仓库根启动（把后端目录加入 PYTHONPATH）
# PowerShell:
$env:PYTHONPATH = "$PWD/apps/backend"
python apps/backend/run.py
```

### 3. 安装 Node 依赖并构建 agent-ai

```bash
pnpm install
pnpm --filter agent-ai build
```

### 4. 启动三个服务（建议开三个终端，均在仓库根）

| 顺序 | 命令 | 端口 |
|------|------|------|
| ① | `pnpm serve:agent-ai` | **8766**（LLM / Retriever） |
| ② | `uv run --directory apps/backend python run.py`（或已激活 venv 时 `python apps/backend/run.py` + `PYTHONPATH`） | **8000**（API / 检索） |
| ③ | `pnpm dev`（Web + 若 workspace 含 backend 脚本则并行；否则 `pnpm --filter web dev`） | **3000** |

健康检查：

- http://127.0.0.1:8000/health — Python
- http://127.0.0.1:8766/health — agent-ai
- http://localhost:3000 — Web

### 5. 最小联调（可选）

需先 `init_tags` 与 ingest 才有检索语料，详见 [`docs/dev.md`](docs/dev.md)。请求 Python API 时带上租户头：

```http
X-Workspace-ID: 00000000-0000-0000-0000-000000000101
```

更完整的 API 表、日志路径、embedding 回填与 CI：**[`docs/dev.md`](docs/dev.md)**、[`apps/backend/README.md`](apps/backend/README.md)。

后端类型检查（与 CI 一致）：

```bash
pnpm check:backend
# 或：cd apps/backend && mypy src
# 仓库根目录：mypy apps/backend/src（读取根目录 mypy.ini，忽略 asyncpg/pgvector 等无 stub 依赖）
```

---

## 文档

| 文档 | 说明 |
|------|------|
| [**docs/dev.md**](docs/dev.md) | 开发手册（边界、进度、API、调试） |
| [**docs/README.md**](docs/README.md) | 里程碑变更索引 |
| [2026-06-03 — Retrieve 域与 Catalog](docs/2026-06-03-mvp-retrieve-domains-implementation.md) | 多租户检索、API BREAKING、E2E 结论 |
| [2026-06-03 — Ingest 提取迁 TS](docs/2026-06-03-ts-ingest-extraction-gateway.md) | `/extract` 网关 |
| [2026-05-09 — Ingest 首版](docs/2026-05-09-ingest-pipeline-implementation.md) | 历史背景（**部分 API 表已过时**，见文首说明） |
| [apps/backend/README.md](apps/backend/README.md) | Schema、测试、embedding 回填 |
| [packages/agent-ai/README.md](packages/agent-ai/README.md) | Retriever 序列图、主 Agent 隔离 |

`openspec/` 仅本地工作流（`.gitignore`），不随 git 推送。

---

## 仓库结构

```
apps/web              → 管理端 UI
apps/backend          → Wiki + DB API + RRF 检索（:8000）
packages/agent-ai     → LLM + 上下文 + Retriever（:8766）
apps/skills           → 领域 Prompt / 提取与标签模板（TS loader 读取）
docs/                 → 开发指南与按日变更说明
```

---

## 协作

功能分支 + Pull Request；合并前见 `docs/dev.md`（`pnpm lint`、`pnpm build`、`pnpm check:agent-ai`、backend `pytest` 等）。
