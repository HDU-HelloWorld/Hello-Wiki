# Hello Wiki Backend

**框架交付版本**：清洁架构 + CQRS + DDD 多层隔离框架，配套完整测试与可观测性基础设施。

## 开发指南与约束

请优先阅读并遵守统一规范文档：

- `DEVELOPMENT_GUIDE.md`

## 快速开始

### 1. 环境准备

```bash
# Python 3.11+ 虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -e ".[dev]"
```

如果你在当前目录下运行脚本，请先把当前目录加进 Python 导入路径。

fish：

```fish
set -x PYTHONPATH (pwd)
```

zsh：

```bash
export PYTHONPATH="$PWD"
```

### 2. 启动应用

```bash
# 启动 API 服务（localhost:8000）
python run.py

# 可选：启动 Worker 进程（后台异步任务）
python worker.py

# MVP 阶段统一默认租户启动（自动注入 X-Workspace-ID）
PYTHONPATH="$PWD" python scripts/mvp.py
```

### 3. 健康检查

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/workspace/context
```

## 测试与本地检查（提交前必做！！！）

### 单元测试

```bash
# 运行全部测试
python3 -m pytest tests/ -q

# 运行特定测试类
python3 -m pytest tests/test_gateway.py -v
python3 -m pytest tests/test_logging.py -v

# 运行特定测试（关键字过滤）
python3 -m pytest tests/test_gateway.py -k workspace_valid -v
```

### 本地检查

```bash
# 架构隔离检查（import-linter）
lint-imports

# 代码检查
ruff check src/ tests/
mypy src/

# 代码修复
ruff check --fix src/ tests/

# 格式检查
ruff format --check src/ tests/ 

# 格式修复
ruff format src/ tests/ 

```

## MVP 默认租户

如果你在 MVP 阶段不想手动处理 `X-Workspace-ID`，可以直接使用统一默认租户注入器。

```bash
PYTHONPATH="$PWD" python scripts/mvp.py
```

默认租户 ID 为 `00000000-0000-0000-0000-000000000001`，也可以通过 `--workspace-id` 覆盖。

**测试覆盖范围**：
- ✅ 网关层（请求拦截、链路注入、租户隔离、权限检查）
- ✅ 日志与可观测性（结构化日志、OTel spans）
- ✅ Worker 上下文（TaskIQ 消息处理、多租户上下文）
- ✅ workspace_valid 边界（无 header、合法 header、非法 header）
- ✅ 架构隔离（lint-imports contract 检查）

## 当前项目结构

```
├── .env.example             ← 环境变量示例
├── README.md                ← 项目说明
├── pyproject.toml           ← Python 构建与工具配置
├── run.py                   ← API 启动入口
├── worker.py                ← Worker 启动入口
├── scripts/
│   └── mvp.py               ← MVP 本地开发注入器
├── deploy/
│   └── observability/       ← 本地可观测性栈配置
├── data/
│   └── logs/                ← 本地日志输出目录
├── src/
│   ├── api/
│   │   ├── gateway.py       ← 请求网关：租户、Trace、基础中间件
│   │   ├── router.py        ← 路由聚合器
│   │   ├── deps.py          ← FastAPI 依赖与 DI 容器
│   │   ├── schemas/         ← API 层请求/响应模型（Pydantic）
│   │   │   ├── chat.py
│   │   │   ├── ingest.py
│   │   │   ├── wiki.py
│   │   │   └── workspace.py
│   │   └── v1/
│   │       ├── chat.py
│   │       ├── ingest.py
│   │       ├── wiki.py
│   │       └── workspace.py
│   ├── application/
│   │   ├── chat/
│   │   │   ├── chat_executor.py
│   │   │   └── stream_handler.py
│   │   ├── ingest/
│   │   │   └── compile_workflow.py
│   │   ├── maintenance/
│   │   │   └── dedupe_workflow.py
│   │   └── wiki/
│   │       ├── wiki_commands.py
│   │       └── wiki_queries.py
│   ├── core/
│   │   ├── config.py
│   │   ├── context.py
│   │   ├── logging.py
│   │   ├── observability.py
│   │   ├── security.py
│   │   └── tracing.py
│   ├── domain/
│   │   ├── chat/
│   │   ├── document/
│   │   ├── maintenance/
│   │   ├── settlement/
│   │   ├── wiki/
│   │   └── workspace/
│   ├── infrastructure/
│   │   ├── ai/
│   │   │   ├── llm_adapter.py
│   │   │   └── search_engine.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── repositories/
│   │   │   │   ├── chat_repo.py
│   │   │   │   └── wiki_repo.py
│   │   │   └── session.py
│   │   ├── observability/
│   │   │   └── otel_runtime.py
│   │   ├── parser/
│   │   │   └── mineru_client.py
│   │   └── storage/
│   │       └── file_system.py
│   └── workers/
│       ├── broker.py
│       ├── context_middleware.py
│       └── tasks.py
├── tests/
│   ├── conftest.py
│   ├── helpers.py
│   ├── test_api_deps.py
│   ├── test_gateway.py
│   ├── test_logging.py
│   ├── test_main.py
│   ├── test_observability.py
│   ├── test_tracing.py
│   ├── test_worker_broker.py
│   └── test_worker_context.py
```

## API 端点示例

```bash
# 健康检查
curl http://localhost:8000/health

# 获取当前租户信息
curl http://localhost:8000/api/v1/workspace/context \
  -H "X-Workspace-ID: 00000000-0000-0000-0000-000000000001"

# Wiki 端点（框架示例，返回 501 Not Implemented）
curl -X POST http://localhost:8000/api/v1/wiki \
  -H "Content-Type: application/json" \
  -d '{"title": "Example", "content": "..."}'

# Chat 流端点（SSE）
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this wiki?"}'
```

## 可观测性（OTel + Phoenix + Loki/Grafana）

### 1. 启用日志文件输出

```bash
export LOG_TO_FILE=true
export LOG_FILE_PATH=./data/logs/backend.log
```

### 2. 启动本地可观测性栈

```bash
cd deploy/observability
docker compose up -d
```

### 3. 配置 OTel 导出端点

```bash
export OBSERVABILITY_ENABLED=true
export OTEL_ENABLED=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:6006/v1/traces
```

### 4. 访问仪表板

- **Phoenix Traces**: http://localhost:6006 （链路详情、延迟分析）
- **Grafana**: http://localhost:3000 （admin/admin）
- **Loki 日志查询**: http://localhost:3100

## 多租户支持

所有请求通过 `X-Workspace-ID` header 传递租户标识：

```bash
curl http://localhost:8000/api/v1/workspace/context \
  -H "X-Workspace-ID: 00000000-0000-0000-0000-000000000001"
```

**框架层实现**：
- ✅ 网关自动解析并验证 workspace ID
- ✅ ContextVars 全局注入（所有异步层自动获取）
- ✅ OTel spans 自动标记 workspace_valid / workspace_id
- ✅ Worker 上下文中间件传递多租户信息

## 关键设计决策

| 组件 | 技术栈 | 理由 |
|------|--------|------|
| Web 框架 | FastAPI | 类型安全 + 自动 OpenAPI 文档 + async 原生 |
| ORM | SQLModel | SQLAlchemy + Pydantic 合一，schema 一致 |
| 任务队列 | TaskIQ 0.12.1 | 轻量级 + Redis 后端 + 多工作进程 |
| 可观测性 | OTel + Phoenix | 标准化链路追踪 + 开源仪表板 |
| 存储（MVP） | 文件系统 JSON | 快速原型 + 零运维成本 |
| 存储（生产） | PostgreSQL | BM25 全文搜索 + pg_search 插件 |
| 缓存 | Redis | Chat 会话缓存 + 高速访问 |

## 对团队成员的指导

### 1. 理解框架 vs 业务逻辑分离

**框架代码**（禁止修改业务逻辑）：
- `src/api/gateway.py` — 请求拦截、认证、链路
- `src/core/*` — 上下文、日志、可观测性
- `src/api/schemas/*` — API 入参/出参模型
- `tests/helpers.py` — 测试基础设施

**业务代码**（这里实现 domain model）：
- `src/domain/` — 领域聚合根、值对象、domain services
- `src/application/` — Use case 实现
- `src/infrastructure/` — Repository 实现、LLM/搜索适配

### 2. 新增用例的流程

1. **定义 domain model** (`src/domain/*/`)
2. **实现应用层流程**（按能力放在 `src/application/<feature>/`，例如 `commands/queries/workflow`）
3. **实现基础设施适配** (`src/infrastructure/*/`)
4. **定义 API schema** (`src/api/schemas/<feature>.py`)
5. **添加 API 端点** (`src/api/v1/<feature>.py`)
6. **补充依赖注入/上下文** (`src/api/deps.py`)
7. **编写测试** (`tests/test_<feature>.py`)

### 3. 遵循的模式

- ✅ 所有异步操作走 TaskIQ worker
- ✅ 所有数据库访问通过 Repository 抽象
- ✅ 所有外部服务通过 Port 接口
- ✅ 所有日志通过 structured logger（自动带 trace ID）
- ✅ 业务异常在 API 层统一映射为 HTTP status codes

## 存储策略

**当前 MVP**：
- 文件系统 JSON index（`STORAGE_BASE_PATH`）
- 快速迭代 + 零基础设施

**迁移计划**：
- Phase 1: PostgreSQL + ORM 层（已建立但未激活）
- Phase 2: 全文搜索升级（pg_search → pgvector）
- Phase 3: Redis 会话缓存启用

## 常见问题

**Q: 如何添加新的依赖？**
A: 优先编辑 `pyproject.toml`，然后执行 `pip install -e ".[dev]"`（或使用项目统一的包管理流程）。

**Q: Worker 如何测试？**
A: 查看 `tests/test_worker_context.py` 中的 TaskIQ 消息结构，添加 worker 特定的测试。

**Q: 如何调试链路跟踪？**
A: Phoenix 仪表板显示所有 spans，每个 span 包含 workspace_id、duration、错误信息。

**Q: 如何扩展权限检查？**
A: 在 `src/api/gateway.py` 的 `AuthGatewayHook` 中补充实现；所有请求都会经过网关。
