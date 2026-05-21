from dataclasses import dataclass


@dataclass(frozen=True)
class CompileDocumentCommand:
    workspace_id: str
    source_document_id: str
    title: str
    markdown_content: str
    category: str = "general"


@dataclass(frozen=True)
class IngestDocumentCommand:
    workspace_id: str
    file_path: str
    domain: str = "general"
