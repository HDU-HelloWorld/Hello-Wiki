from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class InitTagsCommand:
    workspace_id: UUID
    domain: str
    description: str
    language: str = "zh"
