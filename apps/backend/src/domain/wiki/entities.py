"""
Wiki 领域实体
定义核心业务对象
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum


# ========== 新增：wiki_repo.py 需要的类 ==========

class WikiStatus(str, Enum):
    """Wiki 页面状态"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class WikiFact:
    """Wiki 事实（结构化知识）"""
    key: str
    value: str
    confidence: float = 1.0


@dataclass
class WikiParseReference:
    """Wiki 解析引用（来源文档）"""
    source_document_id: str
    reference_type: str  # e.g., "exact", "summary", "related"


# ========== 原有的 WikiPage 类 ==========

@dataclass
class WikiPage:
    """Wiki 页面聚合根"""

    id: int
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    parent_id: Optional[int] = None
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

    def update_content(self, new_content: str) -> None:
        """更新内容（版本号+1）"""
        self.content = new_content
        self.version += 1
        self.updated_at = datetime.now()

    def update_title(self, new_title: str) -> None:
        """更新标题"""
        self.title = new_title
        self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def move_to(self, new_parent_id: Optional[int]) -> None:
        """移动到新位置"""
        self.parent_id = new_parent_id
        self.updated_at = datetime.now()

    @property
    def tags_json(self) -> str:
        """标签转为 JSON 字符串（用于存储）"""
        import json
        return json.dumps(self.tags, ensure_ascii=False)

    @classmethod
    def create(cls, title: str, content: str = "", tags: List[str] = None,
               parent_id: Optional[int] = None, created_by: Optional[str] = None) -> "WikiPage":
        """工厂方法：创建新页面"""
        return cls(
            id=0,  # ID 将由数据库生成
            title=title,
            content=content,
            tags=tags or [],
            parent_id=parent_id,
            version=1,
            created_by=created_by
        )