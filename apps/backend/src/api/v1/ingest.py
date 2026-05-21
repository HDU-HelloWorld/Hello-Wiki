from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.api.deps import get_ingest_compile_handler, get_ingest_pipeline_handler, get_workspace_id
from src.api.schemas.ingest import (
    CompileRequest,
    CompileResponse,
    IngestStatusResponse,
    IngestUploadResponse,
)
from src.application.ingest.commands import CompileDocumentCommand, IngestDocumentCommand
from src.application.ingest.handlers import CompileDocumentHandler, IngestDocumentHandler

router = APIRouter(prefix="/ingest", tags=["ingest"])

TASK_STATUS: dict[str, dict[str, object]] = {}


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
                workspace_id=str(workspace_id),
                source_document_id=request.source_document_id,
                title=request.title,
                markdown_content=request.markdown_content,
                category=request.category,
            )
        )
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501, detail="ingest compile endpoint is not implemented yet"
        ) from exc
    return CompileResponse(title=page.title, status=page.status.value, fact_count=len(page.facts))


@router.post("/upload", response_model=IngestUploadResponse)
async def ingest_upload(
    file: UploadFile = File(...),
    domain: str = Form(default="general"),
    handler: IngestDocumentHandler = Depends(get_ingest_pipeline_handler),
) -> IngestUploadResponse:
    import asyncio
    import os
    import tempfile
    import uuid

    task_id = str(uuid.uuid4())
    TASK_STATUS[task_id] = {"status": "pending", "total_chunks": 0, "successful": 0, "failed": 0}

    # Read file content before background task starts (avoid race on UploadFile close)
    suffix = os.path.splitext(file.filename or ".txt")[1]
    content = await file.read()

    async def _run() -> None:
        TASK_STATUS[task_id]["status"] = "running"
        tmp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            result = await handler.handle(
                IngestDocumentCommand(
                    workspace_id="default",
                    file_path=tmp_path,
                    domain=domain,
                )
            )
            TASK_STATUS[task_id].update(
                {"status": "completed" if result["failed"] == 0 else "partial", **result}
            )
        except Exception as exc:
            TASK_STATUS[task_id]["status"] = "failed"
            TASK_STATUS[task_id]["error"] = str(exc)
        finally:
            if tmp_path:
                os.unlink(tmp_path)

    asyncio.create_task(_run())
    return IngestUploadResponse(task_id=task_id)


@router.get("/status/{task_id}", response_model=IngestStatusResponse)
async def ingest_status(task_id: str) -> IngestStatusResponse:
    info = TASK_STATUS.get(task_id)
    if info is None:
        raise HTTPException(status_code=404, detail="task not found")
    return IngestStatusResponse(**info)
