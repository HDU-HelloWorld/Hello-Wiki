from __future__ import annotations

from uuid import UUID

import pytest
from fastapi import HTTPException

from src.api import deps
from src.application.chat.handlers import AskChatHandler, StreamChatHandler
from src.application.ingest.handlers import CompileDocumentHandler
from src.application.wiki.handlers import ListWikiHandler, SearchWikiHandler, UpsertWikiHandler
from src.core.context import (
    ExecutionContext,
    clear_execution_context,
    set_execution_context,
    set_workspace_id,
)
from src.infrastructure.db.repositories.async_wiki_repo_adapter import AsyncWikiRepositoryAdapter


def test_get_wiki_command_handler_returns_handler_instance():
    handler = deps.get_wiki_command_handler()
    assert isinstance(handler, UpsertWikiHandler)


def test_get_wiki_list_handler_returns_handler_instance():
    handler = deps.get_wiki_list_handler()
    assert isinstance(handler, ListWikiHandler)


def test_get_wiki_search_handler_returns_handler_instance():
    handler = deps.get_wiki_search_handler()
    assert isinstance(handler, SearchWikiHandler)


def test_get_chat_ask_handler_returns_handler_instance():
    handler = deps.get_chat_ask_handler()
    assert isinstance(handler, AskChatHandler)
    assert isinstance(handler._executor._repository, AsyncWikiRepositoryAdapter)  # noqa: SLF001


def test_get_chat_stream_handler_returns_handler_instance():
    handler = deps.get_chat_stream_handler()
    assert isinstance(handler, StreamChatHandler)
    assert isinstance(handler._executor._repository, AsyncWikiRepositoryAdapter)  # noqa: SLF001


def test_get_ingest_compile_handler_returns_handler_instance():
    handler = deps.get_ingest_compile_handler()
    assert isinstance(handler, CompileDocumentHandler)
    assert isinstance(handler._use_case._repository, AsyncWikiRepositoryAdapter)  # noqa: SLF001


def test_get_workspace_id_prefers_header_value():
    result = deps.get_workspace_id("00000000-0000-0000-0000-000000000060")

    assert result == UUID("00000000-0000-0000-0000-000000000060")


def test_get_workspace_id_falls_back_to_execution_context():
    set_execution_context(
        ExecutionContext(
            trace_id="trace-api-deps",
            workspace_id=UUID("00000000-0000-0000-0000-000000000061"),
        )
    )

    result = deps.get_workspace_id(None)

    assert result == UUID("00000000-0000-0000-0000-000000000061")


def test_get_workspace_id_uses_default_when_inputs_missing():
    clear_execution_context()
    set_workspace_id(None)

    result = deps.get_workspace_id(None)

    assert result is None


def test_get_workspace_id_ignores_invalid_header_and_uses_context():
    set_execution_context(
        ExecutionContext(
            trace_id="trace-api-deps",
            workspace_id=UUID("00000000-0000-0000-0000-000000000062"),
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        deps.get_workspace_id("invalid-workspace-id")

    assert exc_info.value.status_code == 400


def test_get_wiki_list_handler_uses_shared_async_repository_builder(monkeypatch):
    called = {"count": 0}
    original_builder = deps.wiring.build_async_wiki_repository

    def _wrapped_builder():
        called["count"] += 1
        return original_builder()

    monkeypatch.setattr(deps.wiring, "build_async_wiki_repository", _wrapped_builder)

    deps.get_wiki_list_handler()

    assert called["count"] == 1
