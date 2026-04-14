from dataclasses import dataclass
from uuid import UUID

from fastapi import Header, HTTPException, status

from src.application.chat.chat_executor import ChatExecutor
from src.application.ingest.compile_workflow import IngestCompilerUseCase
from src.application.wiki.wiki_commands import WikiCommandService
from src.application.wiki.wiki_queries import WikiQueryService
from src.core.config import settings
from src.core.context import (
    ExecutionContext,
)
from src.core.context import (
    get_execution_context as get_execution_context_from_context,
)
from src.core.context import (
    get_workspace_id as get_workspace_id_from_context,
)
from src.core.tracing import parse_workspace_id
from src.infrastructure.ai.llm_adapter import RuleBasedLLMAdapter
from src.infrastructure.ai.search_engine import KeywordSearchEngine
from src.infrastructure.db.repositories.wiki_repo import FileSystemWikiRepository


@dataclass(frozen=True)
class ServiceContainer:
    wiki_commands: WikiCommandService
    wiki_queries: WikiQueryService
    ingest_compiler: IngestCompilerUseCase
    chat_executor: ChatExecutor


def _build_container() -> ServiceContainer:
    repo = FileSystemWikiRepository(base_path=settings.STORAGE_BASE_PATH)
    search_engine = KeywordSearchEngine()
    llm_adapter = RuleBasedLLMAdapter()

    wiki_commands = WikiCommandService(repository=repo)
    wiki_queries = WikiQueryService(repository=repo, search_engine=search_engine)
    ingest_compiler = IngestCompilerUseCase(repository=repo)
    chat_executor = ChatExecutor(
        repository=repo, search_engine=search_engine, llm_adapter=llm_adapter
    )
    return ServiceContainer(
        wiki_commands=wiki_commands,
        wiki_queries=wiki_queries,
        ingest_compiler=ingest_compiler,
        chat_executor=chat_executor,
    )


_CONTAINER: ServiceContainer | None = None


def get_container() -> ServiceContainer:
    global _CONTAINER
    if _CONTAINER is None:
        _CONTAINER = _build_container()
    return _CONTAINER


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


def get_execution_context() -> ExecutionContext | None:
    return get_execution_context_from_context()
