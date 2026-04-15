"""
Wiki 领域实体
定义知识库的核心业务对象
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum


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


@dataclass
class WikiPage:
    """Wiki 页面聚合根（完整版，匹配基础设施层）"""

    wiki_id: UUID
    workspace_id: UUID
    title: str
    category: str = "general"
    summary: str = ""
    content: str = ""
    status: WikiStatus = WikiStatus.ACTIVE
    facts: List[WikiFact] = field(default_factory=list)
    parse_references: List[WikiParseReference] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

    def update_content(self, new_content: str) -> None:
        """更新内容"""
        self.content = new_content
        self.updated_at = datetime.now()

    def update_title(self, new_title: str) -> None:
        """更新标题"""
        self.title = new_title
        self.updated_at = datetime.now()

    def add_fact(self, key: str, value: str, confidence: float = 1.0) -> None:
        """添加事实"""
        self.facts.append(WikiFact(key=key, value=value, confidence=confidence))
        self.updated_at = datetime.now()

    def archive(self) -> None:
        """归档页面"""
        self.status = WikiStatus.ARCHIVED
        self.updated_at = datetime.now()

    @classmethod
    def create(cls, workspace_id: UUID, title: str, category: str = "general",
               content: str = "", created_by: Optional[str] = None) -> "WikiPage":
        """工厂方法：创建新页面"""
        return cls(
            wiki_id=uuid4(),
            workspace_id=workspace_id,
            title=title,
            category=category,
            content=content,
            created_by=created_by,
        )