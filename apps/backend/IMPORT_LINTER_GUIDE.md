# Import-Linter 架构约束检查指南

本文档说明如何在 Hello Wiki 后端项目中使用 import-linter 进行架构检查。

## 快速开始

### 1. 安装依赖
```bash
cd apps/backend
pip install -e ".[dev]"  # 或 poetry install
```

### 2. 运行检查
```bash
# 基本检查
lint-imports

# 详细输出
lint-imports --verbose

# 修复模式（如果有自动修复）
lint-imports --fix
```

### 3. 检查结果示例

**成功输出：**
```
=============
Import Linter
=============

Clean Architecture Layers: ✓ (PASS)
Application modules should be independent: ✓ (PASS)
Core layer should not import upper layers: ✓ (PASS)
Domain layer should not depend on web framework: ✓ (PASS)

All contracts are in compliance.
```

**失败输出（例）：**
```
=============
Import Linter
=============

Clean Architecture Layers: ✗ (FAIL)

src.domain.chat imports from src.api

This violates the contract that higher layers can import lower layers.
```

## 配置说明

### 4 个 Contract（约束规则）

#### 1. Clean Architecture Layers（分层架构）
- **类型**：`layers`
- **目的**：确保依赖关系是单向的，从上到下
- **层级顺序**：
  ```
  api              (最高 - HTTP 入口)
  ↓
  application      (业务编排、查询处理)
  ↓
  domain           (核心业务逻辑、实体定义)
  ↓
  infrastructure   (数据库、外部服务实现)
  ↓
  workers          (异步任务处理)
  ↓
  core             (最低 - 通用工具、配置)
  ```
- **规则**：上层可以导入下层，下层不能导入上层
- **例外处理**：
  - `src.main` 可以导入 `workers` 和 `infrastructure`（启动初始化）
  - `tests` 可以导入所有模块（测试需要）

#### 2. Application Modules Independence（模块独立性）
- **类型**：`independence`
- **目的**：确保应用模块间解耦
- **模块列表**：
  - `src.application.chat`
  - `src.application.wiki`
  - `src.application.ingest`
  - `src.application.maintenance`
- **规则**：这些模块彼此不能依赖（但都可以依赖 `infrastructure` 和 `core`）

#### 3. Core Layer Purity（核心层纯净）
- **类型**：`forbidden`
- **目的**：保持核心层无依赖
- **规则**：`src.core` 不能导入任何业务层模块
- **违例**：若违反，通常意味着设计有问题（应该上移到更高层）

#### 4. Domain Layer Framework Isolation（业务逻辑隔离）
- **类型**：`forbidden`
- **目的**：保持领域层不依赖框架
- **禁止列表**：`fastapi`, `uvicorn`, `sqlmodel`
- **原因**：DDD 原则 - 业务逻辑应该与框架无关
- **例外处理**：若有必要，可在 `ignore_imports` 中添加

## 常见问题

### Q1: 如何临时忽略一个违例？

在 `pyproject.toml` 的相应 contract 中添加 `ignore_imports`：

```toml
[[tool.importlinter.contracts]]
name = "Clean Architecture Layers"
type = "layers"
# ... 其他配置 ...
ignore_imports = [
    "src.domain.wiki -> src.application",  # 临时允许
]
```

### Q2: 如何在 CI/CD 中集成？

**GitLab CI 示例：**
```yaml
lint-architecture:
  stage: check
  script:
    - cd apps/backend
    - pip install -e ".[dev]"
    - lint-imports
```

**Pre-commit Hook 示例：**
在 `.pre-commit-config.yaml` 中添加：
```yaml
- repo: local
  hooks:
    - id: import-linter
      name: Import Linter
      entry: lint-imports
      language: system
      types: [python]
      pass_filenames: false
      stages: [commit]
```

### Q3: 如何处理新增模块的导入问题？

按优先级解决：

1. **首选**：重构代码消除违例（最符合架构原则）
2. **次选**：上移到更高层（如果是新特性）
3. **最后**：在 `ignore_imports` 中明确注释并标记 TODO

### Q4: Domain 层能导入 Infrastructure 吗？

**不推荐**，但在 DDD 仓储模式中可能需要：
- Domain 定义仓储 **接口** (abstract base class)
- Infrastructure 实现仓储
- 这样 Domain 不依赖具体实现

如果代码中有这种需要，在 contract 中添加例外而不是取消 contract。

## 架构可视化

```
┌─────────────────────┐
│    src.api          │  ← HTTP 请求入口
├─────────────────────┤
│  src.application    │  ← 业务流程、查询处理
├─────────────────────┤
│    src.domain       │  ← 核心业务规则、实体
├─────────────────────┤
│ src.infrastructure  │  ← 数据库、缓存、外部服务
│    src.workers      │  ← 异步任务
├─────────────────────┤
│     src.core        │  ← 配置、工具、常量
└─────────────────────┘
```

## 最佳实践

1. **定期检查**：在开发过程中频繁运行 `lint-imports`
2. **明确说明**：违例必须有文档和 TODO，说明何时解决
3. **小步提交**：避免在一个提交中违反多个 contract
4. **团队沟通**：如果需要改变架构，在合并前讨论

## 相关文档

- [Import-Linter 官方文档](https://import-linter.readthedocs.io/)
- [教程参考](Import-linter%E6%9E%B6%E6%9E%84%E7%BA%A6%E6%9D%9F%E5%B7%A5%E5%85%B7%E5%AE%8C%E5%85%A8%E6%8C%87%E5%8D%97%20-%20%E5%AE%88%E6%8A%A4%E4%BB%A3%E7%A0%81%E6%9E%B6%E6%9E%84%20%7C%20%E7%A1%85%E5%9F%BA%E6%97%A5%E5%BF%97.html)
