from src.application.ingest.commands import CompileDocumentCommand, IngestDocumentCommand
from src.application.ingest.compile_workflow import IngestCompilerUseCase
from src.application.ingest.pipeline import IngestPipelineUseCase
from src.domain.wiki.entities import WikiPage


class CompileDocumentHandler:
    def __init__(self, use_case: IngestCompilerUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: CompileDocumentCommand) -> WikiPage:
        return await self._use_case.execute(command)


class IngestDocumentHandler:
    def __init__(self, use_case: IngestPipelineUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: IngestDocumentCommand) -> dict[str, object]:
        return await self._use_case.execute(command)
