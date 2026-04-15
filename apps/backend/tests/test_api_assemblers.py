from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

from src.api.assemblers.chat import to_ask_chat_query, to_ask_response, to_stream_chat_query
from src.api.assemblers.ingest import to_compile_document_command, to_compile_response
from src.api.assemblers.wiki import (
    to_list_wiki_query,
    to_search_wiki_query,
    to_upsert_wiki_command,
    to_wiki_list_response,
    to_wiki_response,
)
from src.api.schemas.chat import AskRequest
from src.api.schemas.ingest import CompileRequest
from src.api.schemas.wiki import UpsertWikiRequest
from src.application.chat.chat_executor import AskResult
from src.domain.wiki.entities import WikiStatus


def test_chat_assemblers_map_request_and_result() -> None:
    workspace_id = UUID("00000000-0000-0000-0000-000000000201")
    request = AskRequest(question="hello", top_k=5)

    ask_query = to_ask_chat_query(request, workspace_id)
    stream_query = to_stream_chat_query(request, workspace_id)
    response = to_ask_response(AskResult(answer="ok", citations=["c1"]))

    assert ask_query.workspace_id == workspace_id
    assert ask_query.question == "hello"
    assert ask_query.top_k == 5
    assert stream_query.workspace_id == workspace_id
    assert stream_query.question == "hello"
    assert stream_query.top_k == 5
    assert response.answer == "ok"
    assert response.citations == ["c1"]


def test_ingest_assemblers_map_request_and_response() -> None:
    workspace_id = UUID("00000000-0000-0000-0000-000000000202")
    request = CompileRequest(
        source_document_id="doc-1",
        title="Doc",
        markdown_content="content",
        category="general",
    )
    page = SimpleNamespace(title="Doc", status=WikiStatus.DRAFT, facts=[object(), object()])

    command = to_compile_document_command(request, workspace_id)
    response = to_compile_response(page)

    assert command.workspace_id == workspace_id
    assert command.source_document_id == "doc-1"
    assert command.title == "Doc"
    assert command.markdown_content == "content"
    assert command.category == "general"
    assert response.title == "Doc"
    assert response.status == "DRAFT"
    assert response.fact_count == 2


def test_wiki_assemblers_map_commands_queries_and_responses() -> None:
    workspace_id = UUID("00000000-0000-0000-0000-000000000203")
    request = UpsertWikiRequest(
        title="T",
        category="general",
        summary="S",
        content="C",
        source_doc_id="doc-9",
    )
    page = SimpleNamespace(title="T", category="general", summary="S", status=WikiStatus.PUBLISHED)

    command = to_upsert_wiki_command(request, workspace_id)
    list_query = to_list_wiki_query(workspace_id)
    search_query = to_search_wiki_query(workspace_id, keyword="k", top_k=4)
    response = to_wiki_response(page)
    list_response = to_wiki_list_response([page])

    assert command.workspace_id == workspace_id
    assert command.title == "T"
    assert command.source_doc_id == "doc-9"
    assert list_query.workspace_id == workspace_id
    assert search_query.workspace_id == workspace_id
    assert search_query.keyword == "k"
    assert search_query.top_k == 4
    assert response.title == "T"
    assert response.status == "PUBLISHED"
    assert len(list_response.items) == 1
    assert list_response.items[0].title == "T"
