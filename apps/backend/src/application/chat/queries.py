from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AskChatQuery:
    workspace_id: UUID
    question: str
    top_k: int = 3


@dataclass(frozen=True)
class StreamChatQuery:
    workspace_id: UUID
    question: str
    top_k: int = 3
