from src.application.ingest.commands import CompileDocumentCommand
from src.application.ingest.compile_workflow import IngestCompilerUseCase
from src.domain.wiki.entities import WikiPage


class CompileDocumentHandler:
    """Ingest 写路径应用服务（Command Handler）。"""

    def __init__(self, use_case: IngestCompilerUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: CompileDocumentCommand) -> WikiPage:
        return await self._use_case.execute(command)
