from __future__ import annotations

from uuid import UUID

import pytest
from fastapi import HTTPException

from src.api import deps
from src.application.agent.handlers import AgentHandler
from src.application.init.handlers import InitTagsHandler
from src.application.wiki.handlers import ListWikiHandler, SearchWikiHandler, UpsertWikiHandler
from src.core.context import (
    ExecutionContext,
    clear_execution_context,
    set_execution_context,
    set_workspace_id,
)


def test_get_wiki_command_handler_returns_handler_instance():
    handler = deps.get_wiki_command_handler()
    assert isinstance(handler, UpsertWikiHandler)


def test_get_wiki_list_handler_returns_handler_instance():
    handler = deps.get_wiki_list_handler()
    assert isinstance(handler, ListWikiHandler)


def test_get_wiki_search_handler_returns_handler_instance():
    handler = deps.get_wiki_search_handler()
    assert isinstance(handler, SearchWikiHandler)


def test_get_agent_handler_returns_handler_instance():
    handler = deps.get_agent_handler()
    assert isinstance(handler, AgentHandler)


def test_get_init_tags_handler_returns_handler_instance():
    handler = deps.get_init_tags_handler()
    assert isinstance(handler, InitTagsHandler)


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
