"""
Wiki 页面仓库实现
使用文件系统存储
"""

import json
import os
from uuid import UUID
from typing import Optional

from src.domain.wiki.entities import WikiPage
from src.domain.wiki.repository import WikiPageRepository


class FileSystemWikiPageRepository(WikiPageRepository):
    """文件系统实现的 Wiki 页面仓库"""

    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path

    def _get_storage_path(self, workspace_id: UUID) -> str:
        storage_dir = f"{self.base_path}/workspaces/{workspace_id}/wiki"
        os.makedirs(storage_dir, exist_ok=True)
        return storage_dir

    def _get_index_path(self, workspace_id: UUID) -> str:
        return f"{self._get_storage_path(workspace_id)}/pages.json"

    def _read_pages(self, workspace_id: UUID) -> list[dict]:
        index_path = self._get_index_path(workspace_id)
        if not os.path.exists(index_path):
            return []
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []

    def _write_pages(self, workspace_id: UUID, pages: list[dict]) -> None:
        index_path = self._get_index_path(workspace_id)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(pages, f, ensure_ascii=False, indent=2, default=str)

    def save(self, page: WikiPage) -> UUID:
        pages = self._read_pages(page.workspace_id)
        
        # 查找并更新或添加
        found = False
        for i, p in enumerate(pages):
            if p.get("wiki_id") == str(page.wiki_id):
                pages[i] = {
                    "wiki_id": str(page.wiki_id),
                    "title": page.title,
                    "content": page.content,
                    "category": page.category,
                    "summary": page.summary,
                    "updated_at": page.updated_at.isoformat(),
                }
                found = True
                break
        
        if not found:
            pages.append({
                "wiki_id": str(page.wiki_id),
                "title": page.title,
                "content": page.content,
                "category": page.category,
                "summary": page.summary,
                "created_at": page.created_at.isoformat(),
                "updated_at": page.updated_at.isoformat(),
            })
        
        self._write_pages(page.workspace_id, pages)
        return page.wiki_id

    def get_by_id(self, wiki_id: UUID) -> Optional[WikiPage]:
        # 需要遍历所有 workspace，简化实现
        return None

    def get_by_workspace(self, workspace_id: UUID) -> list[WikiPage]:
        pages_data = self._read_pages(workspace_id)
        result = []
        for p in pages_data:
            result.append(WikiPage(
                wiki_id=UUID(p["wiki_id"]),
                workspace_id=workspace_id,
                title=p["title"],
                content=p["content"],
                category=p.get("category", "general"),
                summary=p.get("summary", ""),
            ))
        return result