from typing import Protocol
from uuid import UUID

from src.domain.wiki.entities import WikiPage


class WikiRepository(Protocol):
    def upsert(self, page: WikiPage) -> None: ...

    def get_by_title(self, workspace_id: UUID, title: str) -> WikiPage | None: ...

    def list_by_workspace(self, workspace_id: UUID) -> list[WikiPage]: ...


class WikiSearchEngine(Protocol):
    def search(self, pages: list[WikiPage], keyword: str, top_k: int) -> list[WikiPage]: ...
