"""
Wiki 页面仓库接口
定义数据访问的抽象契约
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.wiki.entities import WikiPage


class WikiPageRepository(ABC):
    """Wiki 页面仓库接口"""

    @abstractmethod
    def save(self, page: WikiPage) -> UUID:
        pass

    @abstractmethod
    def get_by_id(self, wiki_id: UUID) -> WikiPage | None:
        pass

    @abstractmethod
    def get_by_workspace(self, workspace_id: UUID) -> list[WikiPage]:
        pass


# Aliases required by existing modules (compile_workflow, async_wiki_repo_adapter)
# Must be distinct classes (not same class) to avoid duplicate-bases TypeError
class WikiQueryRepositoryPort(WikiPageRepository):
    pass


class WikiCommandRepositoryPort(WikiPageRepository):
    pass
