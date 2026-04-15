from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListWikiQuery:
    workspace_id: UUID
    skip: int = 0
    limit: int = 100


@dataclass(frozen=True)
class SearchWikiQuery:
    workspace_id: UUID
    keyword: str
    top_k: int = 5
