from __future__ import annotations

from src.core.config import settings
from src.domain.ai.provider import LLMProviderPort
from src.infrastructure.ai.providers.mock_provider import MockLLMProvider
from src.infrastructure.ai.providers.openai_compatible import OpenAICompatibleProvider
from src.infrastructure.ai.search_engine import KeywordSearchEngine
from src.infrastructure.db.repositories.async_wiki_repo_adapter import AsyncWikiRepositoryAdapter
from src.infrastructure.db.repositories.wiki_repo import FileSystemWikiRepository


def build_wiki_repository() -> FileSystemWikiRepository:
    return FileSystemWikiRepository(base_path=settings.STORAGE_BASE_PATH)


def build_async_wiki_repository() -> AsyncWikiRepositoryAdapter:
    return AsyncWikiRepositoryAdapter(build_wiki_repository())


def build_search_engine() -> KeywordSearchEngine:
    return KeywordSearchEngine()


def build_llm_provider() -> LLMProviderPort:
    if settings.LLM_MOCK_ENABLED:
        return MockLLMProvider()
    return OpenAICompatibleProvider(
        model=settings.LLM_MODEL_NAME,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=settings.LLM_TEMPERATURE,
    )


def build_init_tags_handler() -> InitTagsHandler:  # noqa: F821  # type: ignore
    from src.application.init.handlers import InitTagsHandler
    from src.application.init.init_tags import InitTagsUseCase

    provider = build_llm_provider()
    use_case = InitTagsUseCase(provider)
    return InitTagsHandler(use_case)


def build_agent_loop() -> AgentLoop:  # noqa: F821  # type: ignore
    from src.application.agent.agent_loop import AgentLoop
    from src.application.agent.tools.init_tags_tool import create_init_tags_tool

    provider = build_llm_provider()
    init_handler = build_init_tags_handler()
    tools = [create_init_tags_tool(init_handler)]
    return AgentLoop(provider=provider, tools=tools)


def build_agent_handler() -> AgentHandler:  # noqa: F821  # type: ignore
    from src.application.agent.handlers import AgentHandler

    return AgentHandler(build_agent_loop())


def build_ingest_pipeline() -> IngestPipelineUseCase:  # noqa: F821  # type: ignore
    from src.application.ingest.pipeline import IngestPipelineUseCase
    from src.infrastructure.db.repositories.knowledge_repo import KnowledgeAsyncRepository

    provider = build_llm_provider()
    repository = KnowledgeAsyncRepository()
    return IngestPipelineUseCase(provider=provider, repository=repository)


def build_ingest_pipeline_handler() -> IngestDocumentHandler:  # noqa: F821  # type: ignore
    from src.application.ingest.handlers import IngestDocumentHandler

    return IngestDocumentHandler(build_ingest_pipeline())
