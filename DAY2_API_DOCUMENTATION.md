# Day2 API 接口文档

本文档描述Day2任务中实现的API接口。所有API都需要`X-Workspace-ID`请求头（通过`get_workspace_id`依赖注入）。

## 基础信息

- **Base URL**: `http://127.0.0.1:8000/api`
- **API前缀**: 所有路由通过FastAPI路由器注册
- **认证**: 通过`X-Workspace-ID`请求头识别工作空间

## 1. Wiki API (`/wiki`)

Wiki页面管理接口，提供CRUD操作和目录树查询。

### 1.1 创建Wiki页面
- **端点**: `POST /wiki/pages`
- **描述**: 创建新的Wiki页面
- **请求体**:
  ```json
  {
    "title": "string",
    "category": "string",
    "summary": "string",
    "content": "string",
    "source_doc_id": "string | null"
  }
  ```
- **响应**: `WikiItem`对象
- **状态码**: 201 (成功创建)
- **实现状态**: 部分实现（依赖底层服务实现）

### 1.2 获取Wiki页面
- **端点**: `GET /wiki/pages/{page_id}`
- **描述**: 根据ID获取Wiki页面
- **路径参数**:
  - `page_id`: Wiki页面UUID
- **响应**: `WikiItem`对象
- **实现状态**: 待实现

### 1.3 更新Wiki页面
- **端点**: `PUT /wiki/pages/{page_id}`
- **描述**: 更新Wiki页面
- **路径参数**:
  - `page_id`: Wiki页面UUID
- **请求体**: 同创建接口
- **响应**: `WikiItem`对象
- **实现状态**: 待实现

### 1.4 删除Wiki页面
- **端点**: `DELETE /wiki/pages/{page_id}`
- **描述**: 删除Wiki页面
- **路径参数**:
  - `page_id`: Wiki页面UUID
- **响应**: 204 No Content
- **实现状态**: 待实现

### 1.5 获取Wiki目录树
- **端点**: `GET /wiki/tree`
- **描述**: 获取Wiki页面目录树
- **查询参数**:
  - `category`: 按分类过滤（可选）
- **响应**: 目录树结构（待定义）
- **实现状态**: 待实现

## 2. 版本管理 API (`/versions`)

Wiki页面版本管理接口，提供版本历史、比较和回滚功能。

### 2.1 获取版本列表
- **端点**: `GET /versions/pages/{page_id}/versions`
- **描述**: 获取Wiki页面的版本列表
- **路径参数**:
  - `page_id`: Wiki页面UUID
- **查询参数**:
  - `limit`: 返回的版本数量（默认10，最大100）
  - `offset`: 偏移量（默认0）
- **响应**: 版本列表
- **实现状态**: 待实现

### 2.2 获取版本详情
- **端点**: `GET /versions/versions/{version_id}`
- **描述**: 获取特定版本的详细信息
- **路径参数**:
  - `version_id`: 版本UUID
- **响应**: 版本详情对象
- **实现状态**: 待实现

### 2.3 比较版本
- **端点**: `GET /versions/compare`
- **描述**: 比较两个版本之间的差异
- **查询参数**:
  - `version_a`: 版本A的ID
  - `version_b`: 版本B的ID
- **响应**: 差异比较结果
- **实现状态**: 待实现

### 2.4 回滚到指定版本
- **端点**: `POST /versions/versions/{version_id}/rollback`
- **描述**: 将Wiki页面回滚到指定版本
- **路径参数**:
  - `version_id`: 要回滚到的版本ID
- **响应**: 回滚结果
- **实现状态**: 待实现

## 3. 标签 API (`/tags`)

标签管理接口，提供标签查询和按标签过滤功能。

### 3.1 获取所有标签
- **端点**: `GET /tags/`
- **描述**: 获取所有标签列表
- **查询参数**:
  - `limit`: 返回的标签数量（默认50，最大200）
  - `offset`: 偏移量（默认0）
- **响应**: 标签列表
- **实现状态**: 待实现

### 3.2 根据标签获取页面
- **端点**: `GET /tags/{tag}/pages`
- **描述**: 根据标签获取相关的Wiki页面
- **路径参数**:
  - `tag`: 标签名称
- **查询参数**:
  - `limit`: 返回的页面数量（默认20，最大100）
  - `offset`: 偏移量（默认0）
- **响应**: Wiki页面列表
- **实现状态**: 待实现

## 应用服务层

### 3.1 Wiki应用服务 (`WikiApplicationService`)
位于 `src/application/wiki_application.py`，提供版本管理相关方法：
- `get_page_versions()`: 获取页面版本列表
- `get_version_by_id()`: 根据ID获取版本
- `compare_versions()`: 比较两个版本
- `rollback_to_version()`: 回滚到指定版本

### 3.2 标签应用服务 (`TagApplicationService`)
位于 `src/application/tag_application.py`，提供标签管理功能：
- `get_all_tags()`: 获取所有标签
- `get_pages_by_tag()`: 根据标签获取页面
- `add_tag_to_page()`: 为页面添加标签
- `remove_tag_from_page()`: 从页面移除标签
- `get_tags_for_page()`: 获取页面的所有标签

## 数据模型

### WikiItem
```python
class WikiItem(BaseModel):
    title: str
    category: str
    summary: str
    status: str
```

### UpsertWikiRequest
```python
class UpsertWikiRequest(BaseModel):
    title: str
    category: str
    summary: str
    content: str
    source_doc_id: str | None
```

## 错误处理

所有API使用标准HTTP状态码：
- `200`: 成功
- `201`: 创建成功
- `204`: 删除成功（无内容）
- `400`: 请求参数错误
- `404`: 资源未找到
- `500`: 服务器内部错误
- `501`: 功能未实现

## 使用示例

### 创建Wiki页面
```bash
curl -X POST "http://127.0.0.1:8000/api/wiki/pages" \
  -H "X-Workspace-ID: your-workspace-id" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hello World",
    "category": "tutorial",
    "summary": "A simple hello world example",
    "content": "# Hello World\n\nThis is a test page.",
    "source_doc_id": null
  }'
```

### 获取版本列表
```bash
curl -X GET "http://127.0.0.1:8000/api/versions/pages/{page_id}/versions?limit=5" \
  -H "X-Workspace-ID: your-workspace-id"
```

## 注意事项

1. 当前实现为占位符，实际业务逻辑需要后续实现
2. 版本管理需要扩展WikiPage实体以支持版本历史
3. 标签功能需要与Wiki页面存储集成
4. 所有待实现的方法返回501状态码

## 文件位置

- 路由文件: `apps/backend/src/api/routes/` (wiki.py, versions.py, tags.py)
- 应用服务: `apps/backend/src/application/` (wiki_application.py, tag_application.py)
- 领域实体: `apps/backend/src/domain/wiki/entities.py`
- 命令/查询服务: `apps/backend/src/application/wiki/` (wiki_commands.py, wiki_queries.py)