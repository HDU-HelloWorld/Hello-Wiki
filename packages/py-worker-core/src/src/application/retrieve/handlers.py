from src.application.retrieve.commands import SearchKnowledgeCommand
from src.application.retrieve.pipeline import RetrieveSearchUseCase
from src.domain.knowledge.retrieve_vo import SearchHit


class SearchKnowledgeHandler:
    def __init__(self, use_case: RetrieveSearchUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: SearchKnowledgeCommand) -> tuple[list[SearchHit], list[str]]:
        return await self._use_case.execute(command)
