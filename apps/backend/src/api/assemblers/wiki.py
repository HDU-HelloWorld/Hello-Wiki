from uuid import UUID

from src.api.schemas.wiki import UpsertWikiRequest, WikiListResponse, WikiResponse
from src.application.wiki.commands import UpsertWikiCommand
from src.application.wiki.queries import ListWikiQuery, SearchWikiQuery
from src.domain.wiki.entities import WikiPage


def to_upsert_wiki_command(request: UpsertWikiRequest, workspace_id: UUID) -> UpsertWikiCommand:
    return UpsertWikiCommand(
        workspace_id=workspace_id,
        title=request.title,
        category=request.category,
        summary=request.summary,
        content=request.content,
        source_doc_id=request.source_doc_id,
    )


def to_list_wiki_query(workspace_id: UUID) -> ListWikiQuery:
    return ListWikiQuery(workspace_id=workspace_id)


def to_search_wiki_query(
    workspace_id: UUID,
    keyword: str,
    top_k: int,
) -> SearchWikiQuery:
    return SearchWikiQuery(workspace_id=workspace_id, keyword=keyword, top_k=top_k)


def to_wiki_response(page: WikiPage) -> WikiResponse:
    return WikiResponse(
        title=page.title,
        category=page.category,
        summary=page.summary,
        status=page.status.value,
    )


def to_wiki_list_response(pages: list[WikiPage]) -> WikiListResponse:
    return WikiListResponse(items=[to_wiki_response(page) for page in pages])
