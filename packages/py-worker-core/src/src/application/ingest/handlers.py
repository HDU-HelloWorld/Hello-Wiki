from src.application.ingest.commands import IngestDocumentCommand
from src.application.ingest.pipeline import IngestPipelineUseCase


class IngestDocumentHandler:
    def __init__(self, use_case: IngestPipelineUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: IngestDocumentCommand) -> dict[str, object]:
        return await self._use_case.execute(command)
