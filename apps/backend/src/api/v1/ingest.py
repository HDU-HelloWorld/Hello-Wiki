from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_workspace_id
from src.api.schemas.ingest import CompileRequest, CompileResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/compile", response_model=CompileResponse)
def compile_document(
    request: CompileRequest,
    workspace_id: UUID = Depends(get_workspace_id),
) -> CompileResponse:
    # 占位：保留接口示例，不包含业务实现。
    raise HTTPException(status_code=501, detail="ingest compile endpoint is not implemented yet")
