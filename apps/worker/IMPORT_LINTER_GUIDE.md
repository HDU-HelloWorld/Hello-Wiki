# Worker Import-Linter 使用说明

适用范围：`apps/worker`。

## 安装

```bash
uv sync --directory apps/worker --extra dev
```

## 运行

```bash
uv run --directory apps/worker lint-imports
```

详细模式：

```bash
uv run --directory apps/worker lint-imports --verbose
```

## 当前规则

### 1. Worker package should not depend on API layer

- `hello_wiki_worker` 禁止依赖 `src.api`

### 2. Worker tasks should reuse wiring instead of direct infrastructure implementations

- `hello_wiki_worker.tasks` 禁止直接依赖：
  - `src.infrastructure.ai`
  - `src.infrastructure.db`
  - `src.infrastructure.parser`
- 允许通过 `src.infrastructure.wiring` 复用统一依赖构建入口

### 3. Worker broker and middleware should stay lightweight

- `hello_wiki_worker.broker`
- `hello_wiki_worker.context_middleware`

以上模块禁止依赖：

- `src.application`
- `src.domain`
- `src.infrastructure`

## 失败时怎么处理

优先判断是否真的违反边界：

1. 如果 worker 直接导入了 API 层，改成调用共享 use case / port
2. 如果 tasks 直接 new 了基础设施实现，改为复用 `src.infrastructure.wiring`
3. 如果 broker / middleware 开始承载业务逻辑，把逻辑下沉回共享层
