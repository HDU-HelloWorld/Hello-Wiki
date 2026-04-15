from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.assemblers.ingest import to_compile_document_command, to_compile_response
from src.api.deps import (
    get_ingest_compile_handler,
    get_required_workspace_id,
)
from src.api.schemas.ingest import CompileRequest, CompileResponse
from src.application.ingest.handlers import CompileDocumentHandler

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/compile", response_model=CompileResponse)
async def compile_document(
    request: CompileRequest,
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: CompileDocumentHandler = Depends(get_ingest_compile_handler),
) -> CompileResponse:
    try:
        page = await handler.handle(
            to_compile_document_command(request=request, workspace_id=workspace_id)
        )
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail="ingest compile endpoint is not implemented yet",
        ) from exc

    return to_compile_response(page)
