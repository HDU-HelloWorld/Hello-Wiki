from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.api.deps import get_container, get_workspace_id

router = APIRouter(prefix="/versions", tags=["versions"])


@router.get("/pages/{page_id}/versions")
async def get_versions(
    page_id: UUID = Path(..., description="Wiki页面ID"),
    workspace_id: UUID = Depends(get_workspace_id),
    limit: int = Query(10, ge=1, le=100, description="返回的版本数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
) -> list:
    """
    获取Wiki页面的版本列表
    """
    # TODO: 需要实现获取版本列表的方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get versions not implemented yet",
    )


@router.get("/versions/{version_id}")
async def get_version_detail(
    version_id: UUID = Path(..., description="版本ID"),
    workspace_id: UUID = Depends(get_workspace_id),
) -> dict:
    """
    获取特定版本的详细信息
    """
    # TODO: 需要实现获取版本详情的方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get version detail not implemented yet",
    )


@router.get("/compare")
async def compare_versions(
    version_a: UUID = Query(..., description="版本A的ID"),
    version_b: UUID = Query(..., description="版本B的ID"),
    workspace_id: UUID = Depends(get_workspace_id),
) -> dict:
    """
    比较两个版本之间的差异
    """
    # TODO: 需要实现版本比较方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Compare versions not implemented yet",
    )


@router.post("/versions/{version_id}/rollback")
async def rollback(
    version_id: UUID = Path(..., description="要回滚到的版本ID"),
    workspace_id: UUID = Depends(get_workspace_id),
) -> dict:
    """
    将Wiki页面回滚到指定版本
    """
    # TODO: 需要实现回滚方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Rollback not implemented yet",
    )