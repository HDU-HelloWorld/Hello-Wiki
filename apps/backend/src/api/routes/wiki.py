from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.api.deps import get_container, get_workspace_id
from src.api.schemas.wiki import UpsertWikiRequest, WikiItem
from src.application.wiki.wiki_commands import UpsertWikiCommand
from src.application.wiki.wiki_queries import ListWikiQuery

router = APIRouter(prefix="/wiki", tags=["wiki"])


@router.post("/pages", response_model=WikiItem, status_code=status.HTTP_201_CREATED)
async def create_page(
    request: UpsertWikiRequest,
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiItem:
    """
    创建新的Wiki页面
    """
    container = get_container()
    command = UpsertWikiCommand(
        workspace_id=workspace_id,
        title=request.title,
        category=request.category,
        summary=request.summary,
        content=request.content,
        source_doc_id=request.source_doc_id,
    )
    try:
        page = container.wiki_commands.upsert_page(command)
        return WikiItem(
            title=page.title,
            category=page.category,
            summary=page.summary,
            status=page.status.value,
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Wiki create page not implemented yet",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create page: {str(e)}",
        )


@router.get("/pages/{page_id}", response_model=WikiItem)
async def get_page(
    page_id: UUID = Path(..., description="Wiki页面ID"),
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiItem:
    """
    根据ID获取Wiki页面
    """
    # TODO: 需要实现通过ID获取页面的方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get page by ID not implemented yet",
    )


@router.put("/pages/{page_id}", response_model=WikiItem)
async def update_page(
    page_id: UUID = Path(..., description="Wiki页面ID"),
    request: UpsertWikiRequest = ...,
    workspace_id: UUID = Depends(get_workspace_id),
) -> WikiItem:
    """
    更新Wiki页面
    """
    # TODO: 需要实现更新页面的方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update page not implemented yet",
    )


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: UUID = Path(..., description="Wiki页面ID"),
    workspace_id: UUID = Depends(get_workspace_id),
) -> None:
    """
    删除Wiki页面
    """
    # TODO: 需要实现删除页面的方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete page not implemented yet",
    )


@router.get("/tree", response_model=list)
async def get_tree(
    workspace_id: UUID = Depends(get_workspace_id),
    category: str = Query(None, description="按分类过滤"),
) -> list:
    """
    获取Wiki页面目录树
    """
    # TODO: 需要实现目录树查询方法
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get wiki tree not implemented yet",
    )