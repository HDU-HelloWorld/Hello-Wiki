# 架构隔离配置文档

## 概述

本项目使用 import-linter 作为架构导入检查工具，确保遵循 Clean Architecture + CQRS + DDD 的分层原则，防止层与层之间出现不必要的耦合。

## 当前配置

- 配置文件：`apps/backend/pyproject.toml`
- 检查命令：`lint-imports`
- CI 入口：`.github/workflows/ci.yml`

## 架构规则

当前定义了 4 个 contract：

1. `Clean Architecture Layers`
   - 用 `layers` 约束分层依赖方向
   - 当前顺序：`src.api` -> `src.workers` -> `src.application` -> `src.infrastructure` -> `src.domain` -> `src.core`

2. `Application modules should be independent`
   - 确保 `src.application.chat`、`src.application.wiki`、`src.application.ingest`、`src.application.maintenance` 彼此独立

3. `Core layer should not import upper layers`
   - 保持 `src.core` 纯净，不反向依赖上层模块

4. `Domain layer should not depend on web framework`
   - 防止领域层直接依赖 `fastapi`、`uvicorn`、`sqlmodel`

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
