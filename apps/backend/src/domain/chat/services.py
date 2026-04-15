from typing import Protocol

from src.domain.wiki.entities import WikiPage


class LLMAdapter(Protocol):
    async def answer(self, question: str, context_pages: list[WikiPage]) -> str: ...
