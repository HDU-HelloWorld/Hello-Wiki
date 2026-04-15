"""
Wiki API 端点
提供知识库页面的 CRUD 操作（使用文件系统存储）
"""

import json
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from src.api.deps import get_workspace_id


# ========== Request/Response Schemas ==========

class WikiPageCreateRequest(BaseModel):
    """创建 Wiki 页面请求"""
    title: str = Field(..., min_length=1, max_length=500, description="页面标题")
    content: str = Field(default="", description="Markdown 内容")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    parent_id: Optional[int] = Field(default=None, description="父页面 ID")


class WikiPageUpdateRequest(BaseModel):
    """更新 Wiki 页面请求"""
    title: Optional[str] = Field(None, max_length=500, description="页面标题")
    content: Optional[str] = Field(None, description="Markdown 内容")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    parent_id: Optional[int] = Field(None, description="父页面 ID")


class WikiPageResponse(BaseModel):
    """Wiki 页面响应"""
    id: int
    title: str
    content: str
    tags: List[str]
    parent_id: Optional[int]
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WikiPageListResponse(BaseModel):
    """Wiki 页面列表响应"""
    items: List[WikiPageResponse]
    total: int


# ========== 文件存储辅助函数 ==========

def get_storage_path(workspace_id: UUID) -> str:
    """获取工作区存储路径"""
    safe_workspace_id = str(workspace_id).replace("-", "_")
    storage_dir = f"./data/workspaces/{safe_workspace_id}/wiki"
    os.makedirs(storage_dir, exist_ok=True)
    return storage_dir


def get_index_path(workspace_id: UUID) -> str:
    """获取索引文件路径"""
    return os.path.join(get_storage_path(workspace_id), "pages.json")


def read_pages(workspace_id: UUID) -> List[dict]:
    """读取所有页面"""
    index_path = get_index_path(workspace_id)
    if not os.path.exists(index_path):
        return []
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_pages(workspace_id: UUID, pages: List[dict]) -> None:
    """写入所有页面"""
    index_path = get_index_path(workspace_id)
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=2, default=str)


def get_next_id(pages: List[dict]) -> int:
    """获取下一个可用 ID"""
    if not pages:
        return 1
    return max(p.get("id", 0) for p in pages) + 1


# ========== Router ==========

router = APIRouter(prefix="/wiki", tags=["Wiki"])


@router.get("/pages", response_model=WikiPageListResponse)
async def list_pages(
    workspace_id: UUID = Depends(get_workspace_id),
    limit: int = Query(100, ge=1, le=1000, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
) -> WikiPageListResponse:
    """
    获取 Wiki 页面列表
    
    - **workspace_id**: 租户 ID（自动从 Header 获取）
    - **limit**: 每页数量（默认 100，最大 1000）
    - **offset**: 偏移量（默认 0）
    """
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header required")
    
    pages_data = read_pages(workspace_id)
    total = len(pages_data)
    
    # 分页
    paginated = pages_data[offset:offset + limit]
    
    # 转换 datetime 字符串为 datetime 对象
    for p in paginated:
        if isinstance(p.get("created_at"), str):
            p["created_at"] = datetime.fromisoformat(p["created_at"])
        if isinstance(p.get("updated_at"), str):
            p["updated_at"] = datetime.fromisoformat(p["updated_at"])
    
    return WikiPageListResponse(
        items=[WikiPageResponse(**p) for p in paginated],
        total=total,
    )


@router.get("/pages/{page_id}", response_model=WikiPageResponse)
async def get_page(
    page_id: int,
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiPageResponse:
    """
    获取单个 Wiki 页面
    
    - **page_id**: 页面 ID
    """
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header required")
    
    pages_data = read_pages(workspace_id)
    
    for page in pages_data:
        if page.get("id") == page_id:
            if isinstance(page.get("created_at"), str):
                page["created_at"] = datetime.fromisoformat(page["created_at"])
            if isinstance(page.get("updated_at"), str):
                page["updated_at"] = datetime.fromisoformat(page["updated_at"])
            return WikiPageResponse(**page)
    
    raise HTTPException(status_code=404, detail=f"Page {page_id} not found")


@router.post("/pages", response_model=WikiPageResponse, status_code=201)
async def create_page(
    request: WikiPageCreateRequest,
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiPageResponse:
    """
    创建新的 Wiki 页面
    
    - **title**: 页面标题（必填）
    - **content**: Markdown 内容
    - **tags**: 标签列表
    - **parent_id**: 父页面 ID
    """
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header required")
    
    pages_data = read_pages(workspace_id)
    
    # 检查标题是否重复
    for page in pages_data:
        if page.get("title") == request.title:
            raise HTTPException(
                status_code=400, 
                detail=f"Page with title '{request.title}' already exists"
            )
    
    now = datetime.now()
    new_page = {
        "id": get_next_id(pages_data),
        "title": request.title,
        "content": request.content,
        "tags": request.tags,
        "parent_id": request.parent_id,
        "version": 1,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "created_by": None,
    }
    
    pages_data.append(new_page)
    write_pages(workspace_id, pages_data)
    
    # 转换回 datetime 对象用于响应
    new_page["created_at"] = now
    new_page["updated_at"] = now
    
    return WikiPageResponse(**new_page)


@router.put("/pages/{page_id}", response_model=WikiPageResponse)
async def update_page(
    page_id: int,
    request: WikiPageUpdateRequest,
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiPageResponse:
    """
    更新 Wiki 页面
    
    - **page_id**: 页面 ID
    - **title**: 新标题
    - **content**: 新内容
    - **tags**: 新标签列表
    - **parent_id**: 新父页面 ID
    """
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header required")
    
    pages_data = read_pages(workspace_id)
    
    for i, page in enumerate(pages_data):
        if page.get("id") == page_id:
            # 更新字段
            if request.title is not None:
                # 检查新标题是否与其他页面重复
                for other in pages_data:
                    if other.get("id") != page_id and other.get("title") == request.title:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Page with title '{request.title}' already exists"
                        )
                page["title"] = request.title
            
            if request.content is not None:
                page["content"] = request.content
                page["version"] = page.get("version", 0) + 1
            
            if request.tags is not None:
                page["tags"] = request.tags
            
            if request.parent_id is not None:
                # 防止循环引用
                if request.parent_id == page_id:
                    raise HTTPException(
                        status_code=400, 
                        detail="Cannot set parent_id to self"
                    )
                page["parent_id"] = request.parent_id
            
            page["updated_at"] = datetime.now().isoformat()
            
            pages_data[i] = page
            write_pages(workspace_id, pages_data)
            
            # 转换回 datetime 对象用于响应
            page["created_at"] = datetime.fromisoformat(page["created_at"]) if isinstance(page.get("created_at"), str) else page.get("created_at")
            page["updated_at"] = datetime.fromisoformat(page["updated_at"]) if isinstance(page.get("updated_at"), str) else page.get("updated_at")
            
            return WikiPageResponse(**page)
    
    raise HTTPException(status_code=404, detail=f"Page {page_id} not found")


@router.delete("/pages/{page_id}", status_code=204)
async def delete_page(
    page_id: int,
    workspace_id: UUID = Depends(get_workspace_id),
) -> None:
    """
    删除 Wiki 页面
    
    - **page_id**: 页面 ID
    """
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header required")
    
    pages_data = read_pages(workspace_id)
    
    for i, page in enumerate(pages_data):
        if page.get("id") == page_id:
            pages_data.pop(i)
            write_pages(workspace_id, pages_data)
            return
    
    raise HTTPException(status_code=404, detail=f"Page {page_id} not found")


@router.get("/search", response_model=List[WikiPageResponse])
async def search_pages(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    workspace_id: UUID = Depends(get_workspace_id),
) -> List[WikiPageResponse]:
    """
    搜索 Wiki 页面
    
    - **q**: 搜索关键词（在标题和内容中搜索）
    """
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header required")
    
    pages_data = read_pages(workspace_id)
    
    keyword_lower = q.lower()
    matched = []
    
    for page in pages_data:
        title = page.get("title", "").lower()
        content = page.get("content", "").lower()
        
        if keyword_lower in title or keyword_lower in content:
            if isinstance(page.get("created_at"), str):
                page["created_at"] = datetime.fromisoformat(page["created_at"])
            if isinstance(page.get("updated_at"), str):
                page["updated_at"] = datetime.fromisoformat(page["updated_at"])
            matched.append(WikiPageResponse(**page))
    
    return matched


@router.get("/tree", response_model=List[dict])
async def get_tree(
    workspace_id: UUID = Depends(get_workspace_id),
) -> List[dict]:
    """
    获取目录树结构
    
    返回嵌套的目录树，每个节点包含：
    - id: 页面 ID
    - title: 页面标题
    - children: 子页面列表（递归）
    """
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header required")
    
    pages_data = read_pages(workspace_id)
    
    def build_tree(parent_id: Optional[int] = None) -> List[dict]:
        result = []
        for page in pages_data:
            if page.get("parent_id") == parent_id:
                result.append({
                    "id": page["id"],
                    "title": page["title"],
                    "children": build_tree(page["id"]),
                })
        return result
    
    return build_tree(None)


@router.get("/stats", response_model=dict)
async def get_stats(
    workspace_id: UUID = Depends(get_workspace_id),
) -> dict:
    """
    获取 Wiki 统计信息
    
    返回：
    - total_pages: 总页面数
    - total_tags: 总标签数（去重）
    - max_version: 最高版本号
    """
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header required")
    
    pages_data = read_pages(workspace_id)
    
    total_pages = len(pages_data)
    
    # 收集所有标签
    all_tags = set()
    max_version = 0
    for page in pages_data:
        tags = page.get("tags", [])
        if isinstance(tags, list):
            all_tags.update(tags)
        version = page.get("version", 0)
        if version > max_version:
            max_version = version
    
    return {
        "total_pages": total_pages,
        "total_tags": len(all_tags),
        "max_version": max_version,
    }