from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import get_workspace_id
from src.api.schemas.wiki import UpsertWikiRequest, WikiItem, WikiListResponse

router = APIRouter(prefix="/wiki", tags=["wiki"])


@router.post("", response_model=WikiItem)
def upsert_wiki(
    request: UpsertWikiRequest,
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiItem:
    # 占位：保留接口示例，不包含业务实现。
    raise HTTPException(status_code=501, detail="wiki upsert endpoint is not implemented yet")


@router.get("", response_model=WikiListResponse)
def list_wiki(
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiListResponse:
    # 占位：保留接口示例，不包含业务实现。
    raise HTTPException(status_code=501, detail="wiki list endpoint is not implemented yet")


@router.get("/search", response_model=WikiListResponse)
def search_wiki(
    keyword: str = Query(min_length=1),
    top_k: int = Query(default=5, ge=1, le=20),
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiListResponse:
    # 占位：保留接口示例，不包含业务实现。
    raise HTTPException(status_code=501, detail="wiki search endpoint is not implemented yet")
