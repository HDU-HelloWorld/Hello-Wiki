from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.api.deps import get_container, get_workspace_id

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/")
async def get_all_tags(
    workspace_id: UUID = Depends(get_workspace_id),
    limit: int = Query(50, ge=1, le=200, description="返回的标签数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
) -> list:
    """
    获取所有标签列表
    """
    # TODO: 需要实现获取所有标签的方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get all tags not implemented yet",
    )


@router.get("/{tag}/pages")
async def get_pages_by_tag(
    tag: str = Path(..., description="标签名称"),
    workspace_id: UUID = Depends(get_workspace_id),
    limit: int = Query(20, ge=1, le=100, description="返回的页面数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
) -> list:
    """
    根据标签获取相关的Wiki页面
    """
    # TODO: 需要实现根据标签获取页面的方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get pages by tag not implemented yet",
    )