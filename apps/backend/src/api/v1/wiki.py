from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import (
    get_wiki_command_handler,
    get_wiki_list_handler,
    get_wiki_search_handler,
    get_workspace_id,
)
from src.api.schemas.wiki import UpsertWikiRequest, WikiItem, WikiListResponse
from src.application.wiki.commands import UpsertWikiCommand
from src.application.wiki.handlers import ListWikiHandler, SearchWikiHandler, UpsertWikiHandler
from src.application.wiki.queries import ListWikiQuery, SearchWikiQuery
from src.domain.wiki.entities import WikiPage

router = APIRouter(prefix="/wiki", tags=["wiki"])


def _to_wiki_item(page: WikiPage) -> WikiItem:
    return WikiItem(
        title=page.title,
        category=page.category,
        summary=page.summary,
        status=page.status.value,
    )


@router.post("", response_model=WikiItem)
async def upsert_wiki(
    request: UpsertWikiRequest,
    workspace_id: UUID | None = Depends(get_workspace_id),
    handler: UpsertWikiHandler = Depends(get_wiki_command_handler),
) -> WikiItem:
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    page = await handler.handle(
        UpsertWikiCommand(
            workspace_id=workspace_id,
            title=request.title,
            category=request.category,
            summary=request.summary,
            content=request.content,
            source_doc_id=request.source_doc_id,
        )
    )
    return _to_wiki_item(page)


@router.get("", response_model=WikiListResponse)
async def list_wiki(
    workspace_id: UUID | None = Depends(get_workspace_id),
    handler: ListWikiHandler = Depends(get_wiki_list_handler),
) -> WikiListResponse:
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    pages = await handler.handle(ListWikiQuery(workspace_id=workspace_id))
    return WikiListResponse(items=[_to_wiki_item(page) for page in pages])


@router.get("/search", response_model=WikiListResponse)
async def search_wiki(
    keyword: str = Query(min_length=1),
    top_k: int = Query(default=5, ge=1, le=20),
    workspace_id: UUID | None = Depends(get_workspace_id),
    handler: SearchWikiHandler = Depends(get_wiki_search_handler),
) -> WikiListResponse:
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    pages = await handler.handle(
        SearchWikiQuery(workspace_id=workspace_id, keyword=keyword, top_k=top_k)
    )
    return WikiListResponse(items=[_to_wiki_item(page) for page in pages])
