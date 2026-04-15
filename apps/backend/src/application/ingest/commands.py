from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CompileDocumentCommand:
    workspace_id: UUID
    source_document_id: str
    title: str
    markdown_content: str
    category: str = "general"
