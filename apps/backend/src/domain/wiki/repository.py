"""
Wiki 页面仓库接口
定义数据访问的抽象契约
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.wiki.entities import WikiPage


class WikiPageRepository(ABC):
    """Wiki 页面仓库接口"""

    @abstractmethod
    def save(self, page: WikiPage) -> UUID:
        pass

    @abstractmethod
    def get_by_id(self, wiki_id: UUID) -> Optional[WikiPage]:
        pass

    @abstractmethod
    def get_by_workspace(self, workspace_id: UUID) -> list[WikiPage]:
        pass