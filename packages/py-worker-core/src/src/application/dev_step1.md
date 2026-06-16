# 任务（历史设计笔记）

> **非规范文档**：早期产品/检索设想。实现以 `application/ingest/pipeline.py`、`application/retrieve/pipeline.py`、`packages/agent-ai/src/retrieve/loop.ts` 及根目录 `README.md` 为准。Insight 逻辑库检索、chunk 级 `summary_vector` 检索等在此描述但 **MVP 未实现**。

## 我们先来构建一个 ingest() 阶段的代码实现，接下来是 ingest() 阶段说明。
step.1: 各类信息来源（PDF 、word、md、txt） ---> 文本信息
策略：Recursive Chunking: The default method using a 5-level delimiter hierarchy
``` TypeScript
const DELIMITERS: string[][] = [
  ['\n\n'],                          // L0: paragraphs
  ['\n'],                            // L1: lines
  ['. ', '! ', '? ', '.\n', '!\n', '?\n'], // L2: sentences
  ['; ', ': ', ', '],                // L3: clauses
  [],                                // L4: words (whitespace split)
];
```
- 根据章节、主题chunksize化文本信息（完整性要求>token限制要求）

step.2: 文本信息 ---LLM> 结构化json （如实体提取、信息摘要等）（填充表单设计中应该由LLM生成的内容）
- 目标数据模板很多时候应当和业务场景相符，因此写成一个skill是必要的任务。
- 构建的结构化json要求能够完整的填充PostgreSQL中设计的各种字段信息。

step.3: 结构化json 和 原文信息 -> PostgreSQL
- 填充对应的字段

# 附录

## PostgreSql 的表单结构

### 已确定部分

查看apps\backend\src\schema.sql

### 未开发部分

// 逻辑层（Insight）

// 冲突层（conflict）

## 检索的逻辑说明
由于我们的ingest阶段肯定是服务于后续的删改查，现在先明确最重要的检索逻辑。
### 检索逻辑概述

主Agent向subAgent调用tool_信息检索loop（iter=4 循环四次）
``` 伪代码
主Agent判断解决这个问题需要哪些方面的内容并进行查询模板生成expandQuery()：
 - （必要知识1）内容： 1. sanitizeQueryForPrompt（一段prompt问题描述，用于向量化查询，同时用于BM25 关键词搜索）2. 匹配的目标Tag字段 3. 时间维度限制
 - （必要知识2）内容： 1. sanitizeQueryForPrompt（一段prompt问题描述，用于向量化查询，同时用于BM25 关键词搜索）2. 匹配的目标Tag字段 3. 时间维度限制
While (LLM认为目前信息不能解答问题):
  1. 异步检索
    1. 信息检索（慢主要原因是LLM的处理）（且信息是未经逻辑处理的信息，还需要subAgent整合）
      - 使用Reciprocal Rank Fusion (RRF)算法策略
      1. 评分参考1：Tag字段匹配度
      目前考虑类似半衰期的评分，随Tag匹配度由1, 1/2, 1/4给出评分。
      2. 评分参考2：语义匹配度
      向量相似性搜索（Vector Similarity Search），针对summary
      3. 评分参考3：关键词匹配度
      BM25 关键词搜索（BM25 Keyword Search），针对original_text_excerpt
      4. 评分参考4：时间维度匹配度
      根据subAgent要求的信息时间戳范围划定(timestamp_start: timestamp_end)
      5. 评分汇总，根据权重给1，2，3，4分配分值，传回top-K
    2. 逻辑检索（快）（信息是已经逻辑结构化后的内容，且有回答参考，可以直接回答问题）
      1. 对逻辑库(insight)直接进行问题语义匹配度和关键词匹配度（和传统RAG相同），传回top-K
      注：若subAgent认为某次逻辑库的返回完全没有参考价值，则直接放弃逻辑检索
  检索结果会随次数传回subAgent，subAgent会判断目前整理的信息是否能够回答问题，若信息已全面，则给主Agent传回回答指导和部分原文信息。
  2. 判断信息是否相关，通过阅读检索到的top-K的uuid对应的description判断
  3. 判断信息是否充分，通过阅读判断为相关的信息的原文original_text_excerpt，提取有效部分，并保留必要部分。若能够完整回答问题，则判断信息充分。
  若信息已充分，subAgent会直接break这个循环loop。
```
### 设计理念
混合检索，目的是为了提高RAG的准确率召回率等指标，提供优秀上下文。
Index Tags我认为是现在热门的所谓的图数据库的优化版本，我通过LLM自己提出的需要的信息索引，通过以这种图的方式链接相关文本
逻辑检索，目的是为了提高重复的问答，或定制化的问答增强，后续继续补充，先进行MVP开发

索引层的设计理念是为了维护某个知识库里面的内容，并提供层级标签结构。
实体层和实体事件时间线是同步维护的，目的是提供类似“蒸馏”的高质量文本，用于向量检索，同时允许根据这个compiled truth 回答一些简单问题（若LLM认为信息已充分）（也是节省token开销的设计）
原始文本层，信息不全面时的最后参考文献，也是数据维护的参考证据
