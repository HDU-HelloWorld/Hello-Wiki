from typing import Protocol

from src.domain.wiki.entities import WikiPage


class WikiSearchEngine(Protocol):
    async def search(
        self,
        pages: list[WikiPage],
        keyword: str,
        top_k: int,
    ) -> list[WikiPage]: ...
