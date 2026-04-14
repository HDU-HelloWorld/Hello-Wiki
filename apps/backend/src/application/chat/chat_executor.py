from dataclasses import dataclass
from uuid import UUID

from src.domain.chat.services import LLMAdapter
from src.domain.wiki.services import WikiRepository, WikiSearchEngine


@dataclass(frozen=True)
class AskQuery:
    workspace_id: UUID
    question: str
    top_k: int = 3


@dataclass(frozen=True)
class AskResult:
    answer: str
    citations: list[str]


class ChatExecutor:
    def __init__(
        self,
        repository: WikiRepository,
        search_engine: WikiSearchEngine,
        llm_adapter: LLMAdapter,
    ) -> None:
        self._repository = repository
        self._search_engine = search_engine
        self._llm_adapter = llm_adapter

    def ask(self, query: AskQuery) -> AskResult:
        # 业务问答编排逻辑留空，后续由业务小组实现。
        raise NotImplementedError("chat ask workflow is not implemented yet")
