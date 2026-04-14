from domain.entities.wiki import WikiPageEntity
from domain.ports.wiki_repository_port import WikiRepositoryPort


class ScaffoldWikiRepository(WikiRepositoryPort):
    def list_pages(self, workspace_id: str) -> list[WikiPageEntity]:
        raise NotImplementedError("Wiki repository adapter is intentionally not implemented in MVP scaffold.")
