from __future__ import annotations

from uuid import UUID

from fastapi import Header, HTTPException, status

from src.application.agent.handlers import AgentHandler
from src.application.ingest.handlers import IngestDocumentHandler
from src.application.init.handlers import InitTagsHandler
from src.application.retrieve.catalog_handlers import (
    GetDomainTagTreeHandler,
    ListRetrieveDomainsHandler,
)
from src.application.retrieve.handlers import SearchKnowledgeHandler
from src.application.wiki.handlers import ListWikiHandler, SearchWikiHandler, UpsertWikiHandler
from src.core.context import ExecutionContext
from src.core.context import get_execution_context as get_execution_context_from_context
from src.core.context import get_workspace_id as get_workspace_id_from_context
from src.core.tracing import parse_workspace_id
from src.infrastructure import wiring


def get_wiki_command_handler() -> UpsertWikiHandler:
    async_repository = wiring.build_async_wiki_repository()
    return UpsertWikiHandler(command_repo=async_repository, query_repo=async_repository)


def get_wiki_list_handler() -> ListWikiHandler:
    async_repository = wiring.build_async_wiki_repository()
    return ListWikiHandler(query_repo=async_repository)


def get_wiki_search_handler() -> SearchWikiHandler:
    return SearchWikiHandler(
        query_repo=wiring.build_async_wiki_repository(),
        search_engine=wiring.build_search_engine(),
    )


def get_init_tags_handler() -> InitTagsHandler:
    return wiring.build_init_tags_handler()


def get_agent_handler() -> AgentHandler:
    return wiring.build_agent_handler()


def get_ingest_pipeline_handler() -> IngestDocumentHandler:
    return wiring.build_ingest_pipeline_handler()


def get_search_knowledge_handler() -> SearchKnowledgeHandler:
    return wiring.build_search_knowledge_handler()


def get_list_retrieve_domains_handler() -> ListRetrieveDomainsHandler:
    return wiring.build_list_retrieve_domains_handler()


def get_domain_tag_tree_handler() -> GetDomainTagTreeHandler:
    return wiring.build_domain_tag_tree_handler()


def get_workspace_id(x_workspace_id: str | None = Header(default=None)) -> UUID | None:
    if x_workspace_id is not None:
        parsed = parse_workspace_id(x_workspace_id)
        if parsed:
            return parsed
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Workspace-ID header",
        )

    ctx_workspace_id = get_workspace_id_from_context()
    if ctx_workspace_id:
        return ctx_workspace_id

    return None


def get_required_workspace_id(x_workspace_id: str | None = Header(default=None)) -> UUID:
    workspace_id = get_workspace_id(x_workspace_id=x_workspace_id)
    if workspace_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="workspace_id is required",
        )
    return workspace_id


def get_execution_context() -> ExecutionContext | None:
    return get_execution_context_from_context()
