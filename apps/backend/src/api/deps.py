from uuid import UUID

from fastapi import Header, HTTPException, status

from src.application.chat.chat_executor import ChatExecutor
from src.application.chat.handlers import AskChatHandler, StreamChatHandler
from src.application.ingest.compile_workflow import IngestCompilerUseCase
from src.application.ingest.handlers import CompileDocumentHandler
from src.application.wiki.handlers import ListWikiHandler, SearchWikiHandler, UpsertWikiHandler
from src.core.context import ExecutionContext
from src.core.context import get_execution_context as get_execution_context_from_context
from src.core.context import get_workspace_id as get_workspace_id_from_context
from src.core.tracing import parse_workspace_id
from src.infrastructure import wiring
from src.infrastructure.ai.llm_adapter import RuleBasedLLMAdapter


def _build_chat_executor() -> ChatExecutor:
    return ChatExecutor(
        repository=wiring.build_async_wiki_repository(),
        search_engine=wiring.build_search_engine(),
        llm_adapter=RuleBasedLLMAdapter(),
    )


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


def get_chat_ask_handler() -> AskChatHandler:
    return AskChatHandler(executor=_build_chat_executor())


def get_chat_stream_handler() -> StreamChatHandler:
    return StreamChatHandler(executor=_build_chat_executor())


def get_ingest_compile_handler() -> CompileDocumentHandler:
    use_case = IngestCompilerUseCase(repository=wiring.build_async_wiki_repository())
    return CompileDocumentHandler(use_case=use_case)


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
