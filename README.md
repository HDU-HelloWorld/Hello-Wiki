# hello-wiki

`hello-wiki` 是一个基于 **pnpm workspace** 的 monorepo，当前包含：

- `apps/web`：Next.js 16 + React 19 + TypeScript + Tailwind CSS v4
- `apps/backend`：FastAPI 分层架构 + LangChain Agent + Ingest Pipeline（已可端到端运行）
- `apps/skills/`：LLM Skill 定义（tag-initialize、knowledge-extraction）

## 当前开发进度

### Web（`apps/web`）

- [x] 已完成 Next.js 工程初始化与基础依赖接入
- [x] 已有根页面 `apps/web/src/app/page.tsx`（默认模板内容）
- [x] 已创建路由文件：`/about`、`/home`、`/login`
- [ ] `about/home/login` 页面内容待实现（当前为空文件）

### Backend（`apps/backend`）

- [x] 已完成 FastAPI 分层目录骨架（`api/application/domain/infra/workers/core`）
- [x] PostgreSQL + pgvector + zhparser 数据库（Docker 环境，`deploy/dev/docker-compose.yml`）
- [x] LLM Provider（OpenAI 兼容 / Mock，支持 `json_mode` 结构化输出）
- [x] Agent Loop（LangChain `create_agent`，支持 tool calling，`POST /agent/chat`）
- [x] 标签初始化（tag-initialize skill → LLM 生成 → 写入 `tags` 表，`POST /init/tags`）
- [x] 文档导入管道（PDF/Word/MD/TXT → 分块 → LLM 结构化提取 → 多表事务写入，`POST /ingest/upload`）
- [ ] 现有 `main.py` 有旧模块 import 错误，测试用自包含入口 `run_agent.py`
- [ ] 知识库基础 CRUD（pages/tags 的增删改查接口）
- [ ] 知识检索（多路混合检索 RRF：Tag + 语义 + BM25 + 时间）
- [ ] Wiki / Compile / QA 业务逻辑（占位 stub，待替换为 Agent + 检索驱动）

## 环境要求

建议本地与 CI 保持一致：

- **Node.js** 20
- **pnpm** 10
- **Python** 3.11+（用于 `apps/backend`）

安装 pnpm 参考：[pnpm 安装文档](https://pnpm.io/installation)

## 本地开发

在仓库根目录执行：

| 命令 | 说明 |
|------|------|
| `pnpm install` | 安装 workspace 依赖 |
| `pnpm dev` | 并行启动 web 与 backend 开发服务 |
| `pnpm build` | 构建 web 应用 |
| `pnpm start` | 启动 web 生产服务（需先 build） |
| `pnpm lint` | 运行 web 的 ESLint |

### 访问地址

- Web: <http://localhost:3000>
- Backend API: <http://127.0.0.1:8000/api>
- Backend 健康检查: <http://127.0.0.1:8000/api/health>

## 当前路由与接口状态

### Web 路由

- `/`：默认模板页面（待替换为业务首页）
- `/about`：文件已创建，页面内容待实现
- `/home`：文件已创建，页面内容待实现
- `/login`：文件已创建，页面内容待实现

### Backend 接口

| 端点 | 状态 | 说明 |
|---|---|---|
| `GET /api/health` | ✅ | 健康检查 |
| `POST /agent/chat` | ✅ | Agent 对话（tool calling） |
| `POST /init/tags` | ✅ | LLM 初始化标签体系 |
| `POST /ingest/upload` | ✅ | 文件导入+结构化提取 |
| `GET /ingest/status/{id}` | ✅ | 导入进度查询 |
| `GET /api/wiki` | ⚠️ 501 | 占位接口 |
| `POST /api/compile` | ⚠️ 501 | 占位接口 |
| `POST /api/qa` | ⚠️ 501 | 占位接口 |

> **当前状态**：`main.py` 存在旧模块（`application/chat` / `domain/wiki`）的 import 链断裂故障——这些模块引用了不存在的 `WikiCommandRepositoryPort` / `WikiQueryRepositoryPort`。新增的 Agent、init_tags、ingest_upload 代码尚未集成到 `main.py` 的依赖注入链中。
>
> **测试入口**：`run_agent.py` 是自包含的临时测试服务器，直接构建所有依赖（绕过 `wiring.py` / `deps.py` 的旧 import 问题）。生产集成时需将测试服务器的构建逻辑迁移至 wiring + deps，或修复旧模块后统一入口。

## 项目结构

```
hello-wiki/
├── apps/
│   ├── web/                     # Next.js 前端
│   ├── backend/                 # FastAPI 后端
│   │   ├── deploy/dev/          # Docker 开发环境（PG + Redis）
│   │   └── src/
│   │       ├── api/             # HTTP 路由 + schemas
│   │       ├── application/     # 业务用例（agent/init/ingest/chat/wiki）
│   │       ├── domain/          # 领域实体 + 端口（ai/knowledge/wiki）
│   │       ├── infrastructure/  # 实现（ai/db/parser/storage）
│   │       ├── core/            # 配置/日志/追踪
│   │       └── workers/         # TaskIQ 后台任务
│   └── skills/                  # LLM Skill 定义
│       ├── tag-initialize/      # 标签体系生成
│       └── knowledge-extraction/ # 结构化知识提取
├── .github/workflows/           # CI 工作流
├── package.json
└── pnpm-lock.yaml
```

## 后续任务

| 优先级 | 任务 | 说明 |
|---|---|---|
| **高** | 修复 `main.py` 集成 | 修复旧模块 import + 将 agent/init/ingest 的构建逻辑从 `run_agent.py` 迁移至 `wiring.py`/`deps.py` |
| **高** | Pages 基础 CRUD | `GET/PUT/DELETE /pages/{id}` — 知识实体的增删改查，目前只能通过 ingest 导入 |
| **高** | Tags 管理接口 | `GET /tags`（树形结构）、`PUT /tags/{id}`（重命名/移动）— 标签体系的可视化与管理 |
| **中** | 知识检索（RRF 混合检索） | `POST /search` — 多路融合：Tag 匹配 + 语义向量 + BM25 关键词 + 时间范围 |
| **中** | Embedding 向量生成 | `raw_chunks.summary_vector` / `pages.truth_embedding` 目前为 NULL，需要调用 embedding 模型填充 |
| **中** | 扫描件 PDF 支持 | `PyPDFLoader` 无法处理图片型 PDF，需接入 MinerU OCR 或 `pypdf` + `pdf2image` |
| **低** | Chat / QA 替换 | 用 Agent Loop + 检索驱动替换现有 `ChatExecutor` stub |
| **低** | Tenant 隔离 | `X-Workspace-ID` 过滤 tags/raw_chunks/pages 的读写 |
| **低** | OCR 文本校验提醒 | `effective_range.stale_risk` 前端可视化 + 过期内容标记 |

## 协作与 Pull Request

团队在 GitHub 采用「功能分支 -> Pull Request -> 合并到 `main`」流程，避免直接向 `main` 推送。

1. 同步主分支：`git checkout main` -> `git pull origin main`
2. 从 `main` 拉分支：如 `feat/xxx`、`fix/xxx`、`docs/xxx`
3. 开发与自测：提交前执行 `pnpm lint`、`pnpm build`
4. 推送并创建 PR：说明问题背景、主要改动、是否有迁移/配置影响
5. Review 与合并：CI 绿灯后再合并

## CI 检查说明

CI 位于 `.github/workflows/ci.yml`，在 `push` 与 `pull_request` 上执行：

- `pnpm install --frozen-lockfile`
- `pnpm lint`
- `pnpm build`

## Git Commit 规范

建议使用 Conventional 风格前缀，便于检索与生成变更说明：

- `feat`：新增功能
- `fix`：修复问题
- `docs`：文档更新
- `style`：仅格式调整（不改逻辑）
- `refactor`：重构（无新增功能/无修复）
- `perf`：性能优化
- `test`：测试相关
- `chore`：工程配置/脚手架/依赖维护
- `revert`：回滚提交

示例：`feat: 添加词条搜索`、`docs: 更新项目开发进度`

## 参考文档

- [Next.js 文档](https://nextjs.org/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [pnpm Workspace 文档](https://pnpm.io/workspaces)
- [JS 开发命名规范](https://juejin.cn/post/6844903492415406088)
