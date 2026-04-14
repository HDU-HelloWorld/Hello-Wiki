from dataclasses import dataclass
from uuid import UUID

from src.domain.wiki.entities import WikiPage
from src.domain.wiki.services import WikiRepository, WikiSearchEngine


@dataclass(frozen=True)
class ListWikiQuery:
    workspace_id: UUID


@dataclass(frozen=True)
class SearchWikiQuery:
    workspace_id: UUID
    keyword: str
    top_k: int = 5


class WikiQueryService:
    def __init__(self, repository: WikiRepository, search_engine: WikiSearchEngine) -> None:
        self._repository = repository
        self._search_engine = search_engine

    def list_pages(self, query: ListWikiQuery) -> list[WikiPage]:
        # Wiki 列表查询流程留空，后续由业务小组实现。
        raise NotImplementedError("wiki list query is not implemented yet")

    def search_pages(self, query: SearchWikiQuery) -> list[WikiPage]:
        # Wiki 搜索查询流程留空，后续由业务小组实现。
        raise NotImplementedError("wiki search query is not implemented yet")
