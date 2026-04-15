"""
Wiki 领域实体
定义知识库的核心业务对象
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import StrEnum


class WikiStatus(StrEnum):
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
    reference_type: str


@dataclass
class WikiPage:
    """Wiki 页面聚合根"""

    wiki_id: UUID
    workspace_id: UUID
    title: str
    category: str = "general"
    summary: str = ""
    content: str = ""
    status: WikiStatus = WikiStatus.ACTIVE
    facts: list[WikiFact] = field(default_factory=list)
    parse_references: list[WikiParseReference] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

    def update_content(self, new_content: str) -> None:
        self.content = new_content
        self.updated_at = datetime.now()

    def update_title(self, new_title: str) -> None:
        self.title = new_title
        self.updated_at = datetime.now()

    @classmethod
    def create(cls, workspace_id: UUID, title: str, category: str = "general",
               content: str = "", created_by: Optional[str] = None) -> "WikiPage":
        return cls(
            wiki_id=uuid4(),
            workspace_id=workspace_id,
            title=title,
            category=category,
            content=content,
            created_by=created_by,
        )