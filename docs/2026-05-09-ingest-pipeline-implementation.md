# Ingest Pipeline 实现变更文档

> 日期: 2026-05-09 | 分支: `feat/database-models` | 关联 openspec: `implement-ingest-pipeline`

## 概述

本次变更实现了 Hello-Wiki 后端核心功能——知识采编管道（Ingest Pipeline），将异构文档（PDF/Word/Markdown/TXT）自动转化为 PostgreSQL 中的结构化知识实体。同时建立了 LLM Provider 抽象层、Agent 对话框架、标签初始化工具和两个可扩展的 Skill 定义。

### 关键数字

| 指标 | 数值 |
|---|---|
| 新增文件 | ~40 个 |
| 修改文件 | ~18 个 |
| 新增代码行 | ~3500 行 |
| 数据库表 | 7 张 (sources, tags, page_tags, raw_chunks, pages, page_timeline, page_versions) |
| API 端点 | 4 个新的 + Agent 1 个 |
| LLM Skill | 2 个 (tag-initialize, knowledge-extraction) |
| import-linter contracts | 4/4 KEPT |

---

## 新手环境搭建指南

> **如果你是新加入的团队成员**，请务必完整阅读本节再开始写代码。环境问题是最常见的卡点。

### 必备软件清单

| 软件 | 版本要求 | 验证命令 | 备注 |
|---|---|---|---|
| Python | 3.11+ | `python --version` | 推荐 3.12，需 conda |
| Docker Desktop | 28+ | `docker --version` | Windows 需启动 Docker Desktop (系统托盘) |
| Git | 2.40+ | `git --version` | Windows 推荐 Git Bash |
| VS Code | 最新版 | — | 推荐，非强制 |

### Python 环境 (Conda)

项目使用 conda 环境 `hw-wiki`。如果你还没有创建：

```powershell
# 1. 确认 conda 已安装 (Anaconda / Miniconda)
conda --version

# 2. 创建 Python 3.12 环境
conda create -n hw-wiki python=3.12 -y

# 3. 激活环境
conda activate hw-wiki

# 4. 安装全部依赖 (仓库根目录有 requirements.txt)
#    requirements.txt 是当前环境 pip freeze 的精确版本快照
pip install -r requirements.txt

# 5. 验证关键依赖
python -c "import fastapi, langchain, asyncpg, pgvector; print('ok')"
```

> **注意**: `requirements.txt` 位于仓库根目录，是 `pip freeze > requirements.txt` 的精确快照。如果遇到版本冲突（特别是 Windows），尝试去掉版本号: `pip install fastapi uvicorn langchain langchain-openai langchain-community langchain-text-splitters asyncpg pgvector pyyaml pydantic-settings`

> **当前环境**: Windows 11, conda `hw-wiki`, Python 3.12.13。其他 OS 或 Python 版本可能需要不同的包版本。

### .env 配置文件

**这是最容易出问题的一步。** 后端启动依赖 `.env` 中的 LLM API Key。

```powershell
# 1. 复制示例文件（在仓库根目录）
copy apps\backend\.env.example .env

# 2. 编辑 .env (在仓库根目录)，修改以下内容：
#   LLM_API_KEY=sk-xxxxxxxxxxxxxxxx     ← 你的 DeepSeek API Key (必填!)
#   LLM_BASE_URL=https://api.deepseek.com/v1
#   DATABASE_URL=postgresql+asyncpg://postgres:vibe_coding@localhost:5432/zhiyuan
#   REDIS_URL=redis://localhost:6379/0
```

**.env 关键配置项说明**:

| 变量 | 默认值 | 说明 | 必填 |
|---|---|---|---|
| `LLM_API_KEY` | `None` | DeepSeek API Key，从 [platform.deepseek.com](https://platform.deepseek.com) 获取 | ✅ 是 |
| `LLM_BASE_URL` | `https://api.deepseek.com/v1` | LLM API 地址，兼容 OpenAI 格式 | 否 |
| `LLM_MODEL_NAME` | `deepseek-chat` | 模型名 | 否 |
| `LLM_MOCK_ENABLED` | `false` | `true` 时使用 Mock Provider（零网络、零费用测试） | 否 |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL 连接串 | 否 |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接串 | 否 |

> **常见问题**: Windows 上 `.env` 文件必须放在仓库根目录 (Git Bash / PowerShell 的当前工作目录)，而不是 `apps/backend/` 下。`pydantic-settings` 从 CWD 查找 `.env`。

### Docker 环境 (PostgreSQL + Redis)

```powershell
# 1. 确认 Docker Desktop 已启动 (Windows 系统托盘 Docker 图标为白色)
docker ps

# 2. 首次启动 (需 --build 编译 zhparser，约 2-3 分钟)
cd apps\backend\deploy\dev
docker compose up -d --build

# 3. 验证 (两个容器均为 healthy)
docker ps --filter "name=hwiki"
# 预期输出:
#   hwiki-pg      Up (healthy)
#   hwiki-redis   Up (healthy)

# 4. 验证数据库扩展和表
docker exec hwiki-pg psql -U postgres -d zhiyuan -c "SELECT extname FROM pg_extension ORDER BY extname;"
# 预期输出: ltree, pg_trgm, pgcrypto, plpgsql, vector, zhparser (6 rows)

docker exec hwiki-pg psql -U postgres -d zhiyuan -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"
# 预期输出: page_tags, page_timeline, page_versions, pages, raw_chunks, sources, tags (7 rows)

# 5. 停止/清理
docker compose down          # 停止容器 (保留数据)
docker compose down -v       # 停止并删除数据卷 (重新初始化)
```

> **如果 `docker compose up` 失败**: 常见原因 —
> (1) Docker Desktop 未启动 (Windows 需要 Docker Desktop 运行中)
> (2) 5432 端口被占用 (本地已有 PostgreSQL)
> (3) 编译 zhparser 时网络超时 (重试或配置镜像加速)

### 启动测试服务器

```powershell
# 1. 确认在仓库根目录
cd D:\python_code\Alchemy5\Hello-Wiki
# 或: cd /d/python_code/Alchemy5/Hello-Wiki (Git Bash)

# 2. 确认 .env 存在且 LLM_API_KEY 已配置
cat .env | grep LLM_API_KEY

# 3. 启动 (python 在 conda hw-wiki 环境中)
python apps\backend\run_agent.py

# 4. 验证
#   浏览器访问 http://localhost:8000/docs → Swagger UI
#   或 curl http://localhost:8000/ → {"endpoints": [...]}
```

### 常见环境问题速查

| 症状 | 可能原因 | 解决方案 |
|---|---|---|
| `ModuleNotFoundError: No module named 'xxx'` | conda 环境缺少依赖 | `pip install xxx`，确认在 `hw-wiki` 环境中 |
| `openai.BadRequestError: This response_format type is unavailable` | DeepSeek 不支持 json_schema | 代码已处理，使用 `method="json_mode"` |
| `openai.OpenAIError: Missing credentials` | `.env` 不在根目录 | 将 `.env` 复制到仓库根目录 |
| `FileNotFoundError: apps\skills\...` | CWD 错误 | 确认从仓库根目录启动 |
| `UnicodeDecodeError: 'gbk' codec` | Windows GBK 编码 | 代码已统一 `encoding="utf-8"` |
| `import-linter BROKEN` | 新模块未注册 | 检查 `pyproject.toml` 的 `ignore_imports` |
| `hwiki-pg Exited (3)` | pg 容器启动失败 | `docker logs hwiki-pg` 查看日志 |
| `docker compose up` 没反应 | Docker Desktop 未启动 | Windows 托盘图标右键 → Start |

---

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│  POST /agent/chat                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ AgentLoop (LangChain create_agent)                   │   │
│  │   ├── SYSTEM_PROMPT (预设规则)                        │   │
│  │   └── Tools: [init_tags]                             │   │
│  │        └── InitTagsHandler → InitTagsUseCase          │   │
│  │             ├── 加载 tag-initialize skill prompt.md   │   │
│  │             └── LLM generate_structured()              │   │
│  │                  └── TagTreeSchema → PostgreSQL       │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  POST /ingest/upload                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ IngestPipelineUseCase (3-step pipeline)              │   │
│  │                                                      │   │
│  │  Step 1: DocumentLoaderAdapter                       │   │
│  │    PDF/Word/MD/TXT → text[]                          │   │
│  │                                                      │   │
│  │  Step 2: RecursiveChunker                            │   │
│  │    5-level delimiter hierarchy:                      │   │
│  │    \n\n → \n → . ! ? → ; : , → whitespace           │   │
│  │                                                      │   │
│  │  Step 3: For each chunk →                            │   │
│  │    a. serialize_tag_tree() → indented text            │   │
│  │    b. SystemMessage(prompt.md) + HumanMessage(tags)   │   │
│  │    c. LLM with_structured_output(ExtractedKnowledge)  │   │
│  │    d. Transactional write:                           │   │
│  │       raw_chunks → pages → tags/page_tags →          │   │
│  │       page_timeline → page_versions                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Clean Architecture 分层

```
Entry │ api/v1/agent.py, api/v1/ingest.py    ← FastAPI 端点
──────┼──────────────────────────────────────────────────
App   │ application/agent/                    ← Agent 编排
      │ application/init/                     ← 标签初始化
      │ application/ingest/                   ← 采编管道
──────┼──────────────────────────────────────────────────
Infra │ infrastructure/ai/providers/          ← LLM 实现
      │ infrastructure/ai/extraction_adapter  ← 提取适配
      │ infrastructure/parser/                ← 文档解析
      │ infrastructure/db/repositories/       ← DB 仓储
      │ infrastructure/db/models/             ← ORM 模型
──────┼──────────────────────────────────────────────────
Domain│ domain/ai/provider.py                 ← LLM 端口
      │ domain/knowledge/                     ← 知识实体
──────┼──────────────────────────────────────────────────
Core  │ core/config.py                        ← 配置
```

---

## 新增模块详情

### 1. LLM Provider (`domain/ai/` + `infrastructure/ai/providers/`)

```
domain/ai/provider.py                    ← LLMProviderPort (ABC)
  ├── generate(messages) → str
  ├── generate_structured(messages, schema) → T
  └── as_runnable() → Runnable

infrastructure/ai/providers/
  ├── openai_compatible.py               ← ChatOpenAI 包装
  │     • with_structured_output(method="json_mode")
  │     • extra_body 禁用 DeepSeek thinking mode
  └── mock_provider.py                   ← 测试用 Mock
        • text_responses: dict[str, str]   关键词→固定回复
        • structured_fixtures: dict[str, T] 关键词→预置对象
        • call_log: list                   调用记录 (可 assert)
```

**配置** (`core/config.py`):
- `LLM_MODEL_NAME` (默认 `deepseek-chat`)
- `LLM_TEMPERATURE` (默认 `0.0`)
- `LLM_MAX_TOKENS` (默认 `4096`)
- `LLM_MOCK_ENABLED` (默认 `false`)

### 2. Agent Loop (`application/agent/`)

```
agent_loop.py           ← AgentLoop (LangChain create_agent)
commands.py             ← AgentCommand
handlers.py             ← AgentHandler
tools/
  ├── init_tags_tool.py ← LangChain @tool 包装 InitTagsHandler
  └── ingest_tool.py    ← 预留 (ingest 走 REST API，不走 agent tool)
```

**System Prompt**: 定义为 Hello-Wiki 知识库管理助手，支持初始化标签、导入文档、检索问答。根据用户意图自动调用 tool。

### 3. 标签初始化 (`application/init/`)

```
commands.py   ← InitTagsCommand (domain, description, language)
init_tags.py  ← InitTagsUseCase + TagTreeSchema (Pydantic)
handlers.py   ← InitTagsHandler (LLM → DB 写入)
```

**流程**:
1. 匹配 domain → 加载 `apps/skills/tag-initialize/references/{domain}/prompt.md`
2. System prompt: 领域标签生成规则
3. User prompt: 知识库描述
4. `provider.generate_structured(messages, TagTreeSchema)` → 验证的 JSON
5. `asyncpg` 写入 `tags` 表: categories (level=0, is_leaf=false) + leaves (level=1, is_leaf=true)
6. ltree path: `{category_name}.{leaf_name}`

**已测试结果**: 8 个分类维度 × 110 个叶子标签写入成功。

### 4. 采编管道 (`application/ingest/`)

```
commands.py   ← IngestDocumentCommand (workspace_id, file_path, domain)
pipeline.py   ← IngestPipelineUseCase (3-step orchestrator)
handlers.py   ← IngestDocumentHandler
```

**3 步管道**:

```
Step 1: DocumentLoaderAdapter
  PDF → PyPDFLoader (仅文本型 PDF，扫描件无法处理)
  DOCX → Docx2txtLoader
  MD → UnstructuredMarkdownLoader
  TXT → TextLoader

Step 2: RecursiveChunker
  5级分隔符: "\n\n" → "\n" → ". ! ?" → "; : ," → ""
  chunk_size=1500, chunk_overlap=150

Step 3: Per-chunk Extraction + Persistence (事务性)
  a. 查询 Tag 树 → serialize_tag_tree() → 缩进文本
  b. 双消息 LLM 调用:
     System: 领域 prompt.md (提取规则 + 输出格式)
     User:   AVAILABLE TAGS\n{缩进标签树}\n\nTEXT TO ANALYZE\n{chunk_text}
  c. 5-field ExtractedKnowledge (全部 REQUIRED):
     chunk_summary, page_title, compiled_truth,
     suggested_tags (2-6个), effective_range
  d. 单个事务写入 5 张表
```

**错误处理**: 单个 chunk 失败不影响其他 chunk, 返回 `{total_chunks, successful, failed, errors}`。

### 5. 提取适配器 (`infrastructure/ai/extraction_adapter.py`)

```
ExtractedKnowledge (Pydantic, 5 字段):
  chunk_summary: str = Field(min_length=1)
  page_title: str = Field(min_length=1)
  compiled_truth: str = Field(min_length=1)
  suggested_tags: list[SuggestedTag] = Field(min_length=2, max_length=6)
  effective_range: EffectiveRange

SkillPromptLoader:
  load(domain) → 读取 knowledge-extraction references/{domain}/prompt.md

StructuredExtractionAdapter:
  extract(domain, chunk_text, tag_tree, ...) → ExtractedKnowledge
```

### 6. 解析器 (`infrastructure/parser/`)

```
document_loader.py:
  DocumentLoaderAdapter.load(file_path) → list[str]
  支持: .pdf .docx .md .txt

chunker.py:
  RecursiveChunker(chunk_size, chunk_overlap).split(text) → list[tuple[str, ChunkMetadata]]
  5-level 中文感知分隔符层级
```

### 7. 领域实体 (`domain/knowledge/`)

```
value_objects.py  ← PageStatus, ChunkStatus, EventType (StrEnum)
entities.py       ← RawChunk, Page, Tag, PageTag, PageTimeline, PageVersion
repository.py     ← KnowledgeRepositoryPort (ABC, 10 async methods)
```

### 8. 数据库

#### 表结构 (`schema.sql`, 7 张表)

| 表 | 用途 | 关键列 |
|---|---|---|
| `sources` | 多源配置 | id, config(JSONB) |
| `tags` | 层级标签树 | path(ltree), level, is_leaf |
| `page_tags` | 标签-实体关联 | page_id(UUID), tag_id(INT) |
| `raw_chunks` | 原始文本 | fulltext_search(tsvector), summary_vector(vector) |
| `pages` | 编译实体 | compiled_truth, truth_embedding(vector), effective_range(tstzrange) |
| `page_timeline` | 追加事件日志 | event_type, source_description |
| `page_versions` | 快照历史 | version, page_state(JSONB), timeline_state(JSONB) |

#### ORM Models (`infrastructure/db/models/knowledge.py`)

7 个 SQLAlchemy ORM 模型，含完整索引定义（HNSW 向量索引、GIN 全文搜索、GiST 时间范围、GIN trigram 模糊搜索）。

#### Repository (`infrastructure/db/repositories/`)

```
knowledge_repo.py    ← KnowledgeAsyncRepository (asyncpg 实现)
  • 共享连接模式: optional conn parameter
  • transactional_extraction_persist(): 单事务 6 步写入
  • ON CONFLICT (path) DO NOTHING 幂等

tag_serializer.py   ← serialize_tag_tree()
  • ORDER BY path → 深度优先缩进文本
  • level * 2 空格缩进，leaf 附加 — label
```

#### 启动方式

```bash
cd apps/backend/deploy/dev
docker compose up -d --build     # PostgreSQL + zhparser + Redis
```

Dockerfile 基于 `pgvector/pgvector:pg15`，编译安装了 `zhparser`（SCWS 中文分词）。

### 9. LLM Skills (`apps/skills/`)

```
skills/
├── tag-initialize/                       ← 生成初始标签体系
│   ├── SKILL.md
│   └── references/
│       ├── index.yaml                    ← 领域注册
│       ├── general/prompt.md             ← 通用标签生成
│       └── university_policy/prompt.md   ← 高校 8 维度标签
│
└── knowledge-extraction/                 ← 结构化知识提取
    ├── SKILL.md
    └── references/
        ├── index.yaml
        ├── general/
        │   ├── template.json             ← 5 字段 JSON Schema
        │   └── prompt.md                 ← System prompt
        └── university_policy/
            ├── template.json             ← 高校定制 + academic_year/semester
            └── prompt.md
```

**设计特征**:
- `references/index.yaml` 注册领域，fallback 到 `default: true`
- 每个领域可独立定制 prompt.md + template.json
- Prompts 使用 `{domain}` 等占位符，运行时 `str.replace()` 注入
- 新领域只需添加 reference 目录（如 `legal-regulation/`）

---

## API 端点

| 方法 | 路径 | 说明 | 状态 |
|---|---|---|---|
| POST | `/agent/chat` | Agent 对话 | ✅ |
| POST | `/init/tags` | LLM 生成标签体系 | ✅ |
| POST | `/ingest/upload` | 文件上传+知识提取 | ✅ |
| GET | `/ingest/status/{id}` | 导入进度查询 | ✅ |
| GET | `/api/health` | 健康检查 | ✅ |
| GET | `/api/wiki` | Wiki 查询 | ⚠️ 501 |
| POST | `/api/compile` | 文档编译 | ⚠️ 501 |
| POST | `/api/qa` | 问答 | ⚠️ 501 |

### 请求/响应示例

**初始化标签**:
```bash
curl -X POST http://localhost:8000/init/tags \
  -H "Content-Type: application/json" \
  -d '{"domain": "university_policy", "description": "中国高校行政管理制度知识库"}'
# → {"domain": "university_policy", "categories": 8, "leaves": 110}
```

**导入文档**:
```bash
curl -X POST http://localhost:8000/ingest/upload \
  -F "file=@选课管理办法.pdf" \
  -F "domain=university_policy"
# → {"task_id": "...", "filename": "选课管理办法.pdf"}

curl http://localhost:8000/ingest/status/{task_id}
# → {"status": "completed", "total_chunks": 1, "successful": 1, "failed": 0}
```

---

## 配置变更

### `core/config.py` 新增

```python
LLM_MODEL_NAME: str = "deepseek-chat"
LLM_TEMPERATURE: float = 0.0
LLM_MAX_TOKENS: int = 4096
LLM_MOCK_ENABLED: bool = False
```

### `pyproject.toml` 新增依赖

```
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
langchain-text-splitters>=0.3.0
```

### `pyproject.toml` import-linter 修改

- 新增 `ignore_imports` 豁免 wiring 跨层导入
- `Application modules` independence 合约纳入 `application/init`
- `agent` 模块豁免 independence 检查（编排器角色）

---

## 关键设计决策

| 决策 | 选择 | 理由 |
|---|---|---|
| LLM 框架 | LangChain | 成熟的 loader/splitter/agent 生态 |
| DB 驱动 | asyncpg (直接) | 简单、可控，MVP 不过度架构 |
| 结构化输出 | `json_mode` | DeepSeek 不支持 `json_schema` |
| Agent 引擎 | `create_agent` (LangGraph) | LangChain 1.x 标准 API |
| Prompt 注入 | `str.replace()` | 避免 `str.format()` 与 JSON `{}` 冲突 |
| 标签树序列化 | `level * 2` 缩进 | 不依赖深度，LLM 自然理解 |
| Thinking mode | `extra_body` 禁用 | DeepSeek 特有错误 |

---

## 已知限制

1. **`main.py` 无法启动**: 旧模块 (`application/chat/compile_workflow.py`) 引用了不存在的 `WikiCommandRepositoryPort`。临时入口为 `run_agent.py`（自包含构建），需后续整合。
2. **扫描件 PDF**: `PyPDFLoader` 无法提取文字，需接入 OCR（项目已有 `mineru_client.py` stub）。
3. **Embedding 向量**: `summary_vector` / `truth_embedding` 字段目前为 NULL，检索功能依赖这些向量。
4. **See_also / Open_threads**: 字段已建表但 ingest 阶段填写 NULL——属于后续图谱逻辑和 RAG 更新管线。
5. **无基础 CRUD**: pages/tags 缺少独立的增删改查接口。

---

## 后续任务

详见 `README.md` 的「后续任务」章节，高优先级为:
1. 修复 `main.py` 集成
2. Pages/Tags 基础 CRUD
3. RRF 多路混合检索
4. Embedding 向量生成
5. 扫描件 PDF OCR 支持