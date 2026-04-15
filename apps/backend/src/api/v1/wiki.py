from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.assemblers.wiki import (
    to_list_wiki_query,
    to_search_wiki_query,
    to_upsert_wiki_command,
    to_wiki_list_response,
    to_wiki_response,
)
from src.api.deps import (
    get_required_workspace_id,
    get_wiki_command_handler,
    get_wiki_list_handler,
    get_wiki_search_handler,
)
from src.api.schemas.wiki import UpsertWikiRequest, WikiListResponse, WikiResponse
from src.application.wiki.handlers import ListWikiHandler, SearchWikiHandler, UpsertWikiHandler

router = APIRouter(prefix="/wiki", tags=["wiki"])


@router.post("", response_model=WikiResponse)
async def upsert_wiki(
    request: UpsertWikiRequest,
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: UpsertWikiHandler = Depends(get_wiki_command_handler),
) -> WikiResponse:
    page = await handler.handle(to_upsert_wiki_command(request=request, workspace_id=workspace_id))
    return to_wiki_response(page)


@router.get("", response_model=WikiListResponse)
async def list_wiki(
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: ListWikiHandler = Depends(get_wiki_list_handler),
) -> WikiListResponse:
    pages = await handler.handle(to_list_wiki_query(workspace_id=workspace_id))
    return to_wiki_list_response(pages)


@router.get("/search", response_model=WikiListResponse)
async def search_wiki(
    keyword: str = Query(min_length=1),
    top_k: int = Query(default=5, ge=1, le=20),
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: SearchWikiHandler = Depends(get_wiki_search_handler),
) -> WikiListResponse:
    pages = await handler.handle(
        to_search_wiki_query(
            workspace_id=workspace_id,
            keyword=keyword,
            top_k=top_k,
        )
    )
    return to_wiki_list_response(pages)
