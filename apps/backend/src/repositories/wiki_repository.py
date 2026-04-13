from typing import Protocol

from models.wiki import WikiPage


class WikiRepository(Protocol):
    def list_pages(self, workspace_id: str) -> list[WikiPage]: ...
