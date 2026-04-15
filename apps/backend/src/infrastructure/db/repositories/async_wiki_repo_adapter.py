"""同步仓储到异步 Port 的适配器。"""

from uuid import UUID

from src.domain.wiki.entities import WikiPage
from src.domain.wiki.repository import WikiCommandRepositoryPort, WikiQueryRepositoryPort
from src.infrastructure.db.repositories.wiki_repo import FileSystemWikiRepository


class AsyncWikiRepositoryAdapter(WikiCommandRepositoryPort, WikiQueryRepositoryPort):
    """将同步 FileSystemWikiRepository 适配为异步仓储接口。"""

    def __init__(self, repository: FileSystemWikiRepository) -> None:
        self._repository = repository

    async def upsert(self, page: WikiPage) -> WikiPage:
        return self._repository.upsert(page)

    async def delete(self, workspace_id: UUID, wiki_id: UUID) -> bool:
        return self._repository.delete(workspace_id=workspace_id, wiki_id=wiki_id)

    async def get_by_id(self, workspace_id: UUID, wiki_id: UUID) -> WikiPage | None:
        return self._repository.get_by_id(workspace_id=workspace_id, wiki_id=wiki_id)

    async def get_by_title(self, workspace_id: UUID, title: str) -> WikiPage | None:
        return self._repository.get_by_title(workspace_id=workspace_id, title=title)

    async def list_by_workspace(
        self, workspace_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[WikiPage]:
        pages = self._repository.list_by_workspace(workspace_id=workspace_id)
        return pages[skip : skip + limit]

    async def count_by_workspace(self, workspace_id: UUID) -> int:
        return self._repository.count_by_workspace(workspace_id=workspace_id)
