## 任务参数

对话语境：{{contextSummary}}

用户问题（精准转述）：{{questionRestatement}}

用户原话：{{question}}

## 工作区知识库目录（由后端从 PostgreSQL 加载）

{{dbCatalog}}

## 主 Agent 建议的检索分解（可参考、合并或重写）

{{suggestedSearchPlan}}

---

{{analysisHint}}

尚未执行任何 Python 检索，也尚未加载标签树。请根据上方列出的可用知识域，在 JSON 中填写 `selectedDomain`，并可先给出初步 `nextSearchQueries`（`targetTags` 可在收到标签树后下一轮再填）。此轮 `relevantPageIds` 应为空数组，`sufficient` 通常为 false。
