# Worker 架构约束

适用范围：`apps/worker`。

## 角色定位

`apps/worker` 是 **异步任务入口层**，负责：

- 接收 TaskIQ 消息
- 组装任务运行时上下文
- 调用共享用例 / wiring
- 返回任务结果

它不是业务实现层，也不是基础设施实现层。

## 分层约束

### 1. Worker 入口不得依赖 API 层

- `hello_wiki_worker/*` 禁止导入 `src.api`
- 原因：worker 与 HTTP 入口解耦，避免把 FastAPI / schema / route 契约带进任务执行端

### 2. Worker tasks 必须复用 wiring

- `hello_wiki_worker.tasks` 可以调用 `src.infrastructure.wiring`
- 禁止直接导入 `src.infrastructure.db` / `src.infrastructure.ai` / `src.infrastructure.parser`
- 原因：依赖构建统一收口在 wiring，避免 worker 自己拼装实现链

### 3. Broker / Middleware 保持轻量

- `hello_wiki_worker.broker`
- `hello_wiki_worker.context_middleware`

以上模块禁止依赖：

- `src.application`
- `src.domain`
- `src.infrastructure`

原因：这两个模块只负责消息入口和上下文注入，不应承载业务流程或底层实现细节。

## 本地检查

在仓库根执行：

```bash
uv sync --directory apps/worker --extra dev
uv run --directory apps/worker lint-imports
```

查看详细输出：

```bash
uv run --directory apps/worker lint-imports --verbose
```
