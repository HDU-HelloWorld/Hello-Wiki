from uuid import UUID

from src.domain.chat.entities import ChatMessage


class InMemoryChatRepository:
    def __init__(self) -> None:
        self._messages: dict[UUID, list[ChatMessage]] = {}

    def append(self, session_id: UUID, message: ChatMessage) -> None:
        if session_id not in self._messages:
            self._messages[session_id] = []
        self._messages[session_id].append(message)

    def list_messages(self, session_id: UUID) -> list[ChatMessage]:
        return list(self._messages.get(session_id, []))
