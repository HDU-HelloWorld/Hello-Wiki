from dataclasses import dataclass
from uuid import UUID

from src.domain.wiki.entities import WikiFact, WikiPage
from src.domain.wiki.services import WikiRepository


@dataclass(frozen=True)
class UpsertWikiCommand:
    workspace_id: UUID
    title: str
    category: str
    summary: str
    content: str
    source_doc_id: str | None = None


class WikiCommandService:
    def __init__(self, repository: WikiRepository) -> None:
        self._repository = repository

    def upsert_page(self, command: UpsertWikiCommand) -> WikiPage:
        # Wiki 写入命令流程留空，后续由业务小组实现。
        raise NotImplementedError("wiki upsert command is not implemented yet")

    def add_fact(self, workspace_id: UUID, title: str, fact: WikiFact) -> WikiPage:
        # Fact 维护流程留空，后续由业务小组实现。
        raise NotImplementedError("wiki add_fact command is not implemented yet")
