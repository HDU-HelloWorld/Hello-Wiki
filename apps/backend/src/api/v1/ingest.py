from typing import TypedDict, cast
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from src.api.deps import get_required_workspace_id
from src.api.schemas.ingest import (
    CompileDocumentJobResponse,
    IngestDocumentItem,
    IngestDocumentListResponse,
    IngestStatusResponse,
    IngestUploadResponse,
)
from src.api.task_queue import enqueue_compile_document, fetch_task_status
from src.core.config import settings
from src.domain.ingest.constants import SUPPORTED_INGEST_EXTENSIONS

router = APIRouter(prefix="/ingest", tags=["ingest"])


class DocumentRecord(TypedDict, total=False):
    workspace_id: str
    filename: str
    domain: str
    status: str
    wiki_pages: int
    uploaded_at: str
    compile_task_id: str | None
    error: str | None
    stored_path: str


DOCUMENTS: dict[str, DocumentRecord] = {}


def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return default


def _utc_now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


def _document_item(document_id: str) -> IngestDocumentItem:
    info = DOCUMENTS[document_id]
    return IngestDocumentItem(
        document_id=document_id,
        filename=str(info["filename"]),
        domain=str(info["domain"]),
        status=str(info["status"]),
        wiki_pages=_coerce_int(info.get("wiki_pages"), 0),
        uploaded_at=str(info["uploaded_at"]),
        compile_task_id=(str(info["compile_task_id"]) if info.get("compile_task_id") else None),
        error=str(info["error"]) if info.get("error") else None,
    )


def _coerce_optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


async def _sync_document_from_task(document_id: str, task_id: str) -> None:
    task = await fetch_task_status(task_id)
    document = DOCUMENTS.get(document_id)
    if task is None or document is None:
        return

    task_status = str(task.get("status", "unknown"))
    if task_status in {"pending", "running"}:
        document["status"] = "compiling"
        return

    if task_status == "completed":
        document["status"] = "compiled"
        document["wiki_pages"] = _coerce_int(task.get("successful"), 0)
        document["error"] = None
    elif task_status == "partial":
        document["status"] = "partial"
        document["wiki_pages"] = _coerce_int(task.get("successful"), 0)
        document["error"] = _coerce_optional_str(task.get("error"))
    elif task_status == "failed":
        document["status"] = "failed"
        document["error"] = _coerce_optional_str(task.get("error"))
    else:
        document["status"] = task_status


@router.get("/documents", response_model=IngestDocumentListResponse)
async def list_documents(
    workspace_id: UUID = Depends(get_required_workspace_id),
    status: str | None = Query(default=None),
) -> IngestDocumentListResponse:
    workspace = str(workspace_id)
    items: list[IngestDocumentItem] = []
    for document_id, info in DOCUMENTS.items():
        if info.get("workspace_id") != workspace:
            continue
        compile_task_id = info.get("compile_task_id")
        if isinstance(compile_task_id, str):
            await _sync_document_from_task(document_id, compile_task_id)
        if status and info.get("status") != status:
            continue
        items.append(_document_item(document_id))

    items.sort(key=lambda item: item.uploaded_at, reverse=True)
    return IngestDocumentListResponse(items=items, total=len(items))


@router.post("/upload", response_model=IngestUploadResponse)
async def ingest_upload(
    file: UploadFile = File(...),
    domain: str = Form(default="general"),
    workspace_id: UUID = Depends(get_required_workspace_id),
) -> IngestUploadResponse:
    import os
    import uuid
    from pathlib import Path

    suffix = os.path.splitext(file.filename or ".txt")[1].lower()
    if suffix not in SUPPORTED_INGEST_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_INGEST_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file format {suffix or '(none)'}. "
                f"Supported: {supported}. "
                "Legacy .doc files must be saved as .docx first."
            ),
        )

    filename = file.filename or f"upload{suffix}"
    document_id = str(uuid.uuid4())
    upload_dir = Path(settings.STORAGE_BASE_PATH) / "uploads" / str(workspace_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = upload_dir / f"{document_id}{suffix}"
    content = await file.read()
    stored_path.write_bytes(content)

    DOCUMENTS[document_id] = {
        "workspace_id": str(workspace_id),
        "filename": filename,
        "domain": domain,
        "stored_path": str(stored_path),
        "status": "pending",
        "wiki_pages": 0,
        "uploaded_at": _utc_now_iso(),
        "compile_task_id": None,
        "error": None,
    }

    return IngestUploadResponse(
        document_id=document_id,
        filename=filename,
        status="pending",
    )


@router.post("/documents/{document_id}/compile", response_model=CompileDocumentJobResponse)
async def compile_queued_document(
    document_id: str,
    workspace_id: UUID = Depends(get_required_workspace_id),
) -> CompileDocumentJobResponse:
    info = DOCUMENTS.get(document_id)
    if info is None or info.get("workspace_id") != str(workspace_id):
        raise HTTPException(status_code=404, detail="document not found")

    current_status = str(info.get("status", "pending"))
    if current_status == "compiling":
        compile_task_id = info.get("compile_task_id")
        if isinstance(compile_task_id, str):
            return CompileDocumentJobResponse(
                document_id=document_id,
                task_id=compile_task_id,
                status="compiling",
            )
    if current_status in {"compiling", "compiled"}:
        raise HTTPException(
            status_code=409,
            detail=f"document is already {current_status}",
        )

    stored_path = str(info["stored_path"])
    task_id = await enqueue_compile_document(
        document_id=document_id,
        file_path=stored_path,
        domain=str(info["domain"]),
        workspace_id=str(workspace_id),
    )
    info["compile_task_id"] = task_id
    info["status"] = "compiling"
    info["error"] = None
    return CompileDocumentJobResponse(
        document_id=document_id,
        task_id=task_id,
        status="compiling",
    )


@router.get("/status/{task_id}", response_model=IngestStatusResponse)
async def ingest_status(task_id: str) -> IngestStatusResponse:
    info = await fetch_task_status(task_id)
    if info.get("document_id") is None:
        for document_id, document in DOCUMENTS.items():
            if document.get("compile_task_id") == task_id:
                info["document_id"] = document_id
                workspace_value = document.get("workspace_id")
                info["workspace_id"] = (
                    str(workspace_value) if workspace_value is not None else None
                )
                break

    result_document_id = info.get("document_id")
    if isinstance(result_document_id, str) and result_document_id in DOCUMENTS:
        await _sync_document_from_task(result_document_id, task_id)

    errors_raw = info.get("errors")
    error_value = info.get("error")
    return IngestStatusResponse(
        status=str(info.get("status", "unknown")),
        document_id=str(info["document_id"]) if info.get("document_id") else None,
        workspace_id=str(info["workspace_id"]) if info.get("workspace_id") else None,
        trace_id=str(info["trace_id"]) if info.get("trace_id") else None,
        total_chunks=_coerce_int(info.get("total_chunks"), 0),
        successful=_coerce_int(info.get("successful"), 0),
        failed=_coerce_int(info.get("failed"), 0),
        error=_coerce_optional_str(error_value),
        errors=cast(list[dict[str, object]], errors_raw) if isinstance(errors_raw, list) else [],
    )
