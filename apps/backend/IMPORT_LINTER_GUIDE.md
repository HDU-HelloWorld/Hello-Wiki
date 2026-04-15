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
Application layer should not depend on API schemas: ✓ (PASS)
API v1 routes should not depend on domain: ✓ (PASS)
API assemblers should not depend on infrastructure: ✓ (PASS)
API schemas should be pure HTTP contracts: ✓ (PASS)

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

### 8 个 Contract（约束规则）

#### 1. Clean Architecture Layers（分层架构）
- **类型**：`layers`
- **目的**：确保依赖关系是单向的，从上到下
- **层级顺序**：
  ```
  api              (最高 - HTTP 入口)
  ↓
  workers          (入口 - 异步任务调度)
  ↓
  application      (业务编排、查询处理)
  ↓
  infrastructure   (数据库、外部服务实现)
  ↓
  domain           (核心业务逻辑、实体定义)
  ↓
  core             (最低 - 通用工具、配置)
  ```
- **规则**：上层可以导入下层，下层不能导入上层
- **说明**：以 `pyproject.toml` 为准，新增例外时必须在配置中显式声明并说明原因。

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

#### 5. Application Layer Should Not Depend on API Schemas（应用层不依赖 API Schema）
- **类型**：`forbidden`
- **规则**：`src.application` 不能导入 `src.api.schemas`
- **原因**：Request/Response 是 HTTP 契约，不应进入应用层

#### 6. API v1 Routes Should Not Depend on Domain（路由层不直接依赖领域层）
- **类型**：`forbidden`
- **规则**：`src.api.v1` 不能直接导入 `src.domain`
- **配置**：`allow_indirect_imports = true`，避免误伤经由 application 的合法调用链

#### 7. API Assemblers Should Not Depend on Infrastructure（Assembler 不依赖基础设施）
- **类型**：`forbidden`
- **规则**：`src.api.assemblers` 不能导入 `src.infrastructure`
- **原因**：Assembler 只承担模型转换职责

#### 8. API Schemas Should Be Pure HTTP Contracts（Schema 保持 HTTP 合约纯净）
- **类型**：`forbidden`
- **规则**：`src.api.schemas` 不能导入 `src.application`、`src.domain`、`src.infrastructure`、`src.workers`
- **原因**：API 合约模型应与业务和实现解耦

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
│   src.workers       │  ← 异步任务入口
├─────────────────────┤
│  src.application    │  ← 业务流程、查询处理
├─────────────────────┤
│ src.infrastructure  │  ← 数据库、缓存、外部服务
├─────────────────────┤
│    src.domain       │  ← 核心业务规则、实体
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
