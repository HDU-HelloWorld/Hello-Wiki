from dataclasses import dataclass

from src.application.chat.queries import AskChatQuery
from src.domain.chat.services import LLMAdapter
from src.domain.wiki.repository import WikiQueryRepositoryPort
from src.domain.wiki.services import WikiSearchEngine


@dataclass(frozen=True)
class AskResult:
    answer: str
    citations: list[str]


class ChatExecutor:
    def __init__(
        self,
        repository: WikiQueryRepositoryPort,
        search_engine: WikiSearchEngine,
        llm_adapter: LLMAdapter,
    ) -> None:
        self._repository = repository
        self._search_engine = search_engine
        self._llm_adapter = llm_adapter

    async def ask(self, query: AskChatQuery) -> AskResult:
        # 业务问答编排逻辑留空，后续由业务小组实现。
        raise NotImplementedError("chat ask workflow is not implemented yet")
