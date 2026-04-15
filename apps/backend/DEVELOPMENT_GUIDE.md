# Hello Wiki Backend 开发指南与约束

本文档是后端开发的统一规范，目标是：
- 保持骨架阶段的架构稳定性
- 降低协作冲突与回归风险
- 让新增功能在可验证、可回滚的前提下落地

适用范围：`apps/backend`。

## 1. 环境与启动

### 1.1 Python 环境

要求：Python 3.11+。

```bash
cd apps/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

如果你使用 fish：

```fish
cd apps/backend
python3.11 -m venv .venv
source .venv/bin/activate.fish
pip install -e ".[dev]"
```

### 1.2 本地启动

```bash
cd apps/backend
export PYTHONPATH="$PWD"
python run.py
```

Worker：

```bash
cd apps/backend
export PYTHONPATH="$PWD"
python worker.py
```

### 1.3 常用验证命令

```bash
cd apps/backend

# 测试
pytest -q

# 类型与静态检查
mypy src/
ruff check src/ tests/

# 自动修复与格式化
ruff check --fix src/ tests/
ruff format src/ tests/

# 架构依赖约束
lint-imports
```

## 2. 目录与分层约束（必须遵守）

### 2.1 Backend 目录约束

- 后端根目录固定为：`apps/backend`。
- 允许的额外目录层只有 `src`。
- 功能目录应直接落在 `src` 下（例如：`api`、`application`、`domain`、`infrastructure`、`workers`、`core`）。
- 禁止新增无价值的包装目录（例如 `src/app/...`、`src/hello_wiki_backend/...`）。

### 2.2 Clean Architecture 分层依赖

依赖方向必须单向且可被 `lint-imports` 验证：

- `api` / `workers`（入口层）
- `application`（用例编排层）
- `infrastructure`（实现层）
- `domain`（业务规则与协议层）
- `core`（最底层通用能力）

规则：
- 禁止低层反向依赖高层。
- `domain` 禁止依赖 FastAPI、Uvicorn 等 Web 框架。
- `application` 内各子模块保持独立（chat/wiki/ingest/maintenance 不互相直接依赖）。

## 3. CQRS 与骨架阶段实现约束

### 3.1 模块组织约定

每个功能模块建议采用以下结构：

- `commands.py`：写模型
- `queries.py`：读模型
- `handlers.py`：应用层处理器
- `*_workflow.py` / `*_executor.py`：流程编排

### 3.2 骨架阶段事项

- 必须保证 API 行为契约稳定（如 400、SSE 响应类型）。
- 必须保证依赖注入链路可运行、可测试。

### 3.3 async 一致性约束

- Domain port 定义为 async 时，调用链必须全 async。
- 同步仓储实现必须通过适配器再注入 async port。
- 禁止把同步仓储直接注入 async 协议。

## 4. 依赖注入与 Wiring 约束

### 4.1 共享构建入口

共享构建逻辑统一放在：`src/infrastructure/wiring.py`。

当前统一构建函数：
- `build_wiki_repository`
- `build_async_wiki_repository`
- `build_search_engine`

### 4.2 禁止重复构建逻辑

- `src/api/deps.py` 与 `src/workers/tasks.py` 不得重复 new 相同依赖链。
- 依赖构建应优先调用 wiring 中的共享函数。

### 4.3 可测试性要求

- 对关键 DI 路径必须有测试断言。
- 至少覆盖：
  - handler 内部注入的是 async 适配器
  - worker 路径使用共享 builder

## 5. 代码风格与类型约束

### 5.1 风格

- 统一使用 4 空格缩进。
- `__all__`、导入顺序、格式化由 ruff 统一。
- 注释优先使用简体中文，描述意图和约束。

### 5.2 类型

- 对外函数必须有明确类型标注。
- 避免裸 `Any`；若必须使用，应在边界处显式收敛并说明原因。
- mypy 严格模式下必须通过，新增代码不得引入新的类型错误。

### 5.3 错误处理

- API 层负责把异常映射为 HTTP 语义。
- 应用层负责业务流程，避免夹杂 HTTP 细节。
- 基础设施错误可上抛，由上层统一处理与记录。

## 6. 测试策略与覆盖要求

### 6.1 骨架阶段最小测试集（必须）

每次改动至少保证以下类别不退化：

- API 契约测试：400/501/SSE content-type
- DI 测试：handler 注入类型正确
- Worker 测试：任务上下文与 async 调用链正确
- 主入口测试：app 创建与生命周期无回归

### 6.2 新增功能时测试要求

新增一个功能点，至少补充：

- 1 条成功路径测试
- 1 条参数/边界测试
- 1 条错误路径测试

如果仅改 wiring/协议层，也必须补“路径已生效”的断言测试。

## 7. 提交流程（建议）

1. 小步提交：每次改动聚焦一个目标。
2. 本地验证：`pytest -q`、`mypy src/`、`ruff check src/ tests/`。
3. 架构检查：`lint-imports`。
4. 变更说明：记录改动动机、影响范围、验证结果。

## 8. 禁止事项

- 禁止跨层随意导入以图“快速可用”。
- 禁止在 `api`/`workers` 内堆业务规则。
- 禁止复制粘贴依赖构建逻辑（应复用 wiring）。
- 禁止跳过类型检查与测试直接合并。
- 禁止未评估地引入新框架或大型依赖。

## 9. 代码评审检查清单

PR 审查至少确认：

- 分层依赖方向是否正确
- CQRS 读写职责是否清晰
- async 协议与实现是否一致
- wiring 是否复用而非重复
- 测试是否覆盖改动核心路径
- mypy/ruff/pytest 是否通过

## 10. 迭代建议（骨架到实现）

推荐按以下顺序推进业务实现：

1. 先补 Wiki 主路径（读写闭环）
2. 再补 Chat 问答主路径
3. 最后补 Ingest 编译与 Maintenance 策略

每阶段都保持“可运行 + 可测试 + 可回滚”。
