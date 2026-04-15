# 架构隔离与约束文档

## 概述

本项目使用 import-linter 作为架构导入检查工具，确保遵循 Clean Architecture + CQRS + DDD 的分层原则，防止层与层之间出现不必要的耦合。
另外，项目还约定了 API Assembler 与共享 Wiring 的实现边界，用于保持路由层简洁和依赖构建一致性。

## 当前配置

- 配置文件：`apps/backend/pyproject.toml`
- 检查命令：`lint-imports`
- CI 入口：`.github/workflows/ci.yml`

## 架构规则

当前定义了 8 个 contract：

1. `Clean Architecture Layers`
   - 用 `layers` 约束分层依赖方向
   - 当前顺序：`src.api` -> `src.workers` -> `src.application` -> `src.infrastructure` -> `src.domain` -> `src.core`

2. `Application modules should be independent`
   - 确保 `src.application.chat`、`src.application.wiki`、`src.application.ingest`、`src.application.maintenance` 彼此独立

3. `Core layer should not import upper layers`
   - 保持 `src.core` 纯净，不反向依赖上层模块

4. `Domain layer should not depend on web framework`
   - 防止领域层直接依赖 `fastapi`、`uvicorn`、`sqlmodel`

5. `Application layer should not depend on API schemas`
   - 防止 `src.application` 直接依赖 `src.api.schemas`
   - 确保 API Request/Response 模型不泄露到应用层

6. `API v1 routes should not depend on domain`
   - 约束 `src.api.v1` 不直接导入 `src.domain`
   - 配置 `allow_indirect_imports = true`，允许经由 application/deps 的合法调用链

7. `API assemblers should not depend on infrastructure`
   - 保证 assembler 只做模型转换，不引入基础设施实现依赖

8. `API schemas should be pure HTTP contracts`
   - 约束 `src.api.schemas` 不依赖 `application/domain/infrastructure/workers`
   - 保持 Request/Response 模型的边界纯净

## 实现约束（非 import-linter）

### API Assembler 约束

- 路由层只做编排，不内联复杂映射。
- `src/api/assemblers/*` 负责：
  - Request -> Command/Query
  - Domain/Application Result -> Response

### 共享 Wiring 约束

- 依赖构建统一放在 `src/infrastructure/wiring.py`。
- `src/api/deps.py` 与 `src/workers/tasks.py` 必须复用 wiring，禁止重复构建相同依赖链。

### workspace_id 处理约束

- Header 合法性（是否为有效 UUID）由网关统一处理。
- 业务必填由依赖层 `get_required_workspace_id` 统一处理。

## 本地运行

在 `apps/backend` 目录下执行：

```bash
lint-imports
```

如果需要查看更详细的输出：

```bash
lint-imports --verbose
```

## CI 集成

GitHub Actions 里的后端检查步骤已经改为直接运行 `lint-imports`，与本地命令保持一致。

## 常见问题

### 如果 lint-imports 报错怎么办？

优先检查是否真的违反了分层依赖。如果不是，再考虑是否需要在 `pyproject.toml` 里补充或调整 contract。

## 相关文件

- [pyproject.toml](pyproject.toml)
- [.github/workflows/ci.yml](../../.github/workflows/ci.yml)
- [IMPORT_LINTER_GUIDE.md](IMPORT_LINTER_GUIDE.md)
