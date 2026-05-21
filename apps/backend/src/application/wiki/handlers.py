from src.application.wiki.commands import UpsertWikiCommand
from src.application.wiki.queries import ListWikiQuery, SearchWikiQuery
from src.domain.wiki.entities import WikiPage, WikiParseReference, WikiStatus
from src.domain.wiki.repository import WikiCommandRepositoryPort, WikiQueryRepositoryPort
from src.domain.wiki.services import WikiSearchEngine


class UpsertWikiHandler:
    """Wiki 写路径应用服务（Command Handler）— stub, pending real implementation."""

    def __init__(
        self,
        command_repo: WikiCommandRepositoryPort,
        query_repo: WikiQueryRepositoryPort,
    ) -> None:
        self._command_repo = command_repo
        self._query_repo = query_repo

    async def handle(self, command: UpsertWikiCommand) -> WikiPage:
        existing = await self._query_repo.get_by_title(command.workspace_id, command.title)  # type: ignore[attr-defined]
        parse_references: list[WikiParseReference] = []
        if command.source_doc_id:
            parse_references.append(WikiParseReference(source_document_id=command.source_doc_id))  # type: ignore[call-arg]
        page = WikiPage.create_or_update(  # type: ignore[attr-defined]
            workspace_id=command.workspace_id,
            title=command.title,
            category=command.category,
            summary=command.summary,
            content=command.content,
            facts=[],
            parse_references=parse_references,
            status=WikiStatus.DRAFT,  # type: ignore[attr-defined]
            existing_id=existing.wiki_id if existing else None,
        )
        return await self._command_repo.upsert(page)  # type: ignore[attr-defined,no-any-return]


class ListWikiHandler:
    """Wiki 读路径应用服务（Query Handler）— stub."""

    def __init__(self, query_repo: WikiQueryRepositoryPort) -> None:
        self._query_repo = query_repo

    async def handle(self, query: ListWikiQuery) -> list[WikiPage]:
        result: list[WikiPage] = await self._query_repo.list_by_workspace(  # type: ignore[attr-defined]
            workspace_id=query.workspace_id,
            skip=query.skip,
            limit=query.limit,
        )
        return result


class SearchWikiHandler:
    """Wiki 检索查询应用服务（Query Handler）— stub."""

    def __init__(
        self,
        query_repo: WikiQueryRepositoryPort,
        search_engine: WikiSearchEngine,
    ) -> None:
        self._query_repo = query_repo
        self._search_engine = search_engine

    async def handle(self, query: SearchWikiQuery) -> list[WikiPage]:
        pages = await self._query_repo.list_by_workspace(workspace_id=query.workspace_id)  # type: ignore[attr-defined]
        return await self._search_engine.search(
            pages=pages,
            keyword=query.keyword,
            top_k=query.top_k,
        )
