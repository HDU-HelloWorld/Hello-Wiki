from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class KnowledgeDomain:
    domain_id: str
    label: str | None = None
    initialized: bool = False


@dataclass(frozen=True)
class KnowledgePartition:
    workspace_id: UUID
    domain_id: str
