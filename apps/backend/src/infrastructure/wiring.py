from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.config import settings
from src.infrastructure.ai.search_engine import KeywordSearchEngine
from src.infrastructure.db.repositories.async_wiki_repo_adapter import AsyncWikiRepositoryAdapter
from src.infrastructure.db.repositories.wiki_repo import FileSystemWikiRepository

if TYPE_CHECKING:
    from src.application.agent.agent_loop import AgentLoop
    from src.application.agent.handlers import AgentHandler
    from src.application.ingest.handlers import IngestDocumentHandler
    from src.application.ingest.pipeline import IngestPipelineUseCase
    from src.application.init.handlers import InitTagsHandler
    from src.application.retrieve.catalog_handlers import (
        GetDomainTagTreeHandler,
        ListRetrieveDomainsHandler,
    )
    from src.application.retrieve.handlers import SearchKnowledgeHandler
    from src.infrastructure.db.repositories.knowledge_catalog_repo import (
        KnowledgeCatalogRepository,
    )


def build_wiki_repository() -> FileSystemWikiRepository:
    return FileSystemWikiRepository(base_path=settings.STORAGE_BASE_PATH)


def build_async_wiki_repository() -> AsyncWikiRepositoryAdapter:
    return AsyncWikiRepositoryAdapter(build_wiki_repository())


def build_search_engine() -> KeywordSearchEngine:
    return KeywordSearchEngine()


def build_knowledge_catalog_repo() -> KnowledgeCatalogRepository:
    from src.infrastructure.db.repositories.knowledge_catalog_repo import (
        KnowledgeCatalogRepository,
    )

    return KnowledgeCatalogRepository()


def build_list_retrieve_domains_handler() -> ListRetrieveDomainsHandler:
    from src.application.retrieve.catalog_handlers import ListRetrieveDomainsHandler

    return ListRetrieveDomainsHandler(build_knowledge_catalog_repo())


def build_domain_tag_tree_handler() -> GetDomainTagTreeHandler:
    from src.application.retrieve.catalog_handlers import GetDomainTagTreeHandler

    return GetDomainTagTreeHandler(build_knowledge_catalog_repo())


def build_init_tags_handler() -> InitTagsHandler:
    from src.application.init.handlers import InitTagsHandler
    from src.application.init.init_tags import InitTagsUseCase

    return InitTagsHandler(InitTagsUseCase())


def build_agent_loop() -> AgentLoop:
    from src.application.agent.agent_loop import AgentLoop

    return AgentLoop()


def build_agent_handler() -> AgentHandler:
    from src.application.agent.handlers import AgentHandler

    return AgentHandler(build_agent_loop())


def build_ingest_pipeline() -> IngestPipelineUseCase:
    from src.application.ingest.embedding_service import EmbeddingBackfillService
    from src.application.ingest.pipeline import IngestPipelineUseCase
    from src.infrastructure.ai.embedding_adapter import OpenAICompatibleEmbeddingAdapter
    from src.infrastructure.ai.extraction_adapter import TsExtractionAdapter
    from src.infrastructure.db.repositories.knowledge_repo import KnowledgeAsyncRepository
    from src.infrastructure.db.repositories.knowledge_search_repo import KnowledgeSearchRepository

    repository = KnowledgeAsyncRepository()
    search_repo = KnowledgeSearchRepository()
    embedding_service = EmbeddingBackfillService(
        embedding_port=OpenAICompatibleEmbeddingAdapter(),
        search_repo=search_repo,
    )
    return IngestPipelineUseCase(
        repository=repository,
        extractor=TsExtractionAdapter(),
        embedding_service=embedding_service,
    )


def build_ingest_pipeline_handler() -> IngestDocumentHandler:
    from src.application.ingest.handlers import IngestDocumentHandler

    return IngestDocumentHandler(build_ingest_pipeline())


def build_search_knowledge_handler() -> SearchKnowledgeHandler:
    from src.application.retrieve.handlers import SearchKnowledgeHandler
    from src.application.retrieve.pipeline import RetrieveSearchUseCase
    from src.infrastructure.ai.embedding_adapter import OpenAICompatibleEmbeddingAdapter
    from src.infrastructure.db.repositories.knowledge_search_repo import KnowledgeSearchRepository

    return SearchKnowledgeHandler(
        RetrieveSearchUseCase(
            search_repo=KnowledgeSearchRepository(),
            embedding_port=OpenAICompatibleEmbeddingAdapter(),
        )
    )
