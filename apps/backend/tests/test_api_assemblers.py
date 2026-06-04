from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

from src.api.assemblers.wiki import (
    to_list_wiki_query,
    to_search_wiki_query,
    to_upsert_wiki_command,
    to_wiki_list_response,
    to_wiki_response,
)
from src.api.schemas.wiki import UpsertWikiRequest
from src.domain.wiki.entities import WikiStatus


def test_wiki_assemblers_map_commands_queries_and_responses() -> None:
    workspace_id = UUID("00000000-0000-0000-0000-000000000203")
    request = UpsertWikiRequest(
        title="T",
        category="general",
        summary="S",
        content="C",
        source_doc_id="doc-9",
    )
    page = SimpleNamespace(title="T", category="general", summary="S", status=WikiStatus.ACTIVE)

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
    assert response.status == "active"
    assert len(list_response.items) == 1
    assert list_response.items[0].title == "T"
