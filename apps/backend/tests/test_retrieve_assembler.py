from uuid import UUID

import pytest

from src.api.assemblers.retrieve import to_search_knowledge_command
from src.api.schemas.retrieve import QueryTemplateRequest, SearchKnowledgeRequest


def test_to_search_knowledge_command_parses_exclude_page_ids() -> None:
    command = to_search_knowledge_command(
        SearchKnowledgeRequest(
            domain="general",
            query=QueryTemplateRequest(sanitize_query_for_prompt="test query"),
            top_k=3,
            exclude_page_ids=[
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
            ],
        ),
        workspace_id=UUID("00000000-0000-0000-0000-000000000104"),
    )

    assert len(command.exclude_page_ids) == 2
    assert UUID("00000000-0000-0000-0000-000000000001") in command.exclude_page_ids


def test_to_search_knowledge_command_rejects_invalid_exclude_uuid() -> None:
    with pytest.raises(ValueError, match="exclude_page_ids"):
        to_search_knowledge_command(
            SearchKnowledgeRequest(
                domain="general",
                query=QueryTemplateRequest(sanitize_query_for_prompt="q"),
                exclude_page_ids=["not-a-uuid"],
            ),
            workspace_id=UUID("00000000-0000-0000-0000-000000000104"),
        )
