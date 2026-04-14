from typing import Protocol

from domain.entities.wiki import WikiPageEntity


class WikiRepositoryPort(Protocol):
    def list_pages(self, workspace_id: str) -> list[WikiPageEntity]: ...
