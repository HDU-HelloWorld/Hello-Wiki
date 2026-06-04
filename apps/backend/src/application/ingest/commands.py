from dataclasses import dataclass


@dataclass(frozen=True)
class IngestDocumentCommand:
    workspace_id: str
    file_path: str
    domain: str = "general"
