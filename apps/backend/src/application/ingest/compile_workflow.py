from dataclasses import dataclass
from uuid import UUID

from src.domain.wiki.entities import WikiFact, WikiPage
from src.domain.wiki.services import WikiRepository


@dataclass(frozen=True)
class CompileDocumentCommand:
    workspace_id: UUID
    source_document_id: str
    title: str
    markdown_content: str
    category: str = "general"


class IngestCompilerUseCase:
    """文档编译用例骨架。"""

    def __init__(self, repository: WikiRepository) -> None:
        self._repository = repository

    def execute(self, command: CompileDocumentCommand) -> WikiPage:
        # 文档编译业务逻辑留空，后续由业务小组实现。
        raise NotImplementedError("ingest compile workflow is not implemented yet")

    @staticmethod
    def _extract_facts(markdown_content: str) -> list[WikiFact]:
        # 事实抽取策略留空，后续由业务小组实现。
        raise NotImplementedError("fact extraction is not implemented yet")
