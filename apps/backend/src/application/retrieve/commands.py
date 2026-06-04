from dataclasses import dataclass
from uuid import UUID

from src.domain.knowledge.retrieve_vo import QueryTemplate


@dataclass(frozen=True)
class SearchKnowledgeCommand:
    workspace_id: UUID
    domain_id: str
    query: QueryTemplate
    top_k: int = 10
    exclude_page_ids: frozenset[UUID] = frozenset()
