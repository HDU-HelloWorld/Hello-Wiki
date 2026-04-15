from src.application.ingest.commands import CompileDocumentCommand
from src.domain.wiki.entities import WikiFact, WikiPage
from src.domain.wiki.repository import WikiCommandRepositoryPort


class IngestCompilerUseCase:
    """文档编译用例骨架。"""

    def __init__(self, repository: WikiCommandRepositoryPort) -> None:
        self._repository = repository

    async def execute(self, command: CompileDocumentCommand) -> WikiPage:
        # 文档编译业务逻辑留空，后续由业务小组实现。
        raise NotImplementedError("ingest compile workflow is not implemented yet")

    @staticmethod
    def _extract_facts(markdown_content: str) -> list[WikiFact]:
        # 事实抽取策略留空，后续由业务小组实现。
        raise NotImplementedError("fact extraction is not implemented yet")
