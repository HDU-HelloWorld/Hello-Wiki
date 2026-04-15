from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_ingest_compile_handler, get_workspace_id
from src.api.schemas.ingest import CompileRequest, CompileResponse
from src.application.ingest.commands import CompileDocumentCommand
from src.application.ingest.handlers import CompileDocumentHandler

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/compile", response_model=CompileResponse)
async def compile_document(
    request: CompileRequest,
    workspace_id: UUID | None = Depends(get_workspace_id),
    handler: CompileDocumentHandler = Depends(get_ingest_compile_handler),
) -> CompileResponse:
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    try:
        page = await handler.handle(
            CompileDocumentCommand(
                workspace_id=workspace_id,
                source_document_id=request.source_document_id,
                title=request.title,
                markdown_content=request.markdown_content,
                category=request.category,
            )
        )
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail="ingest compile endpoint is not implemented yet",
        ) from exc

    return CompileResponse(
        title=page.title,
        status=page.status.value,
        fact_count=len(page.facts),
    )
