from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpsertWikiCommand:
    workspace_id: UUID
    title: str
    category: str
    summary: str
    content: str
    source_doc_id: str | None = None
