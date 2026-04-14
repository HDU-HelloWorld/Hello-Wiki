from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class MessageRole(StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"
    TOOL = "TOOL"


@dataclass
class ContentBlock:
    block_type: str
    raw_content: str
    sequence_order: int


@dataclass
class ChatMessage:
    message_id: UUID
    role: MessageRole
    sent_at: datetime
    trace_id: str
    blocks: list[ContentBlock] = field(default_factory=list)

    @staticmethod
    def create(role: MessageRole, trace_id: str, content: str) -> "ChatMessage":
        return ChatMessage(
            message_id=uuid4(),
            role=role,
            sent_at=datetime.now(UTC),
            trace_id=trace_id,
            blocks=[ContentBlock(block_type="TEXT", raw_content=content, sequence_order=0)],
        )
