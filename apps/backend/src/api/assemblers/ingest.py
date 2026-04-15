from uuid import UUID

from src.api.schemas.ingest import CompileRequest, CompileResponse
from src.application.ingest.commands import CompileDocumentCommand
from src.domain.wiki.entities import WikiPage


def to_compile_document_command(
    request: CompileRequest,
    workspace_id: UUID,
) -> CompileDocumentCommand:
    return CompileDocumentCommand(
        workspace_id=workspace_id,
        source_document_id=request.source_document_id,
        title=request.title,
        markdown_content=request.markdown_content,
        category=request.category,
    )


def to_compile_response(page: WikiPage) -> CompileResponse:
    return CompileResponse(
        title=page.title,
        status=page.status.value,
        fact_count=len(page.facts),
    )
