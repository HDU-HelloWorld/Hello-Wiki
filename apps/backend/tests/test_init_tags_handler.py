from __future__ import annotations

from uuid import UUID

import pytest

from src.application.init.commands import InitTagsCommand
from src.application.init.handlers import InitTagsHandler
from src.application.init.init_tags import Category, LeafTag, TagTreeSchema


class _RecordingConnection:
    def __init__(self) -> None:
        self.queries: list[str] = []

    async def execute(self, query: str, *args: object) -> None:
        self.queries.append(query)

    async def fetchval(self, query: str, *args: object) -> int:
        return 1

    async def close(self) -> None:
        return None

    def transaction(self) -> _RecordingConnection:
        return self

    async def __aenter__(self) -> _RecordingConnection:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None


class _FakeUseCase:
    async def execute(self, command: InitTagsCommand) -> TagTreeSchema:
        return TagTreeSchema(
            domain=command.domain,
            categories=[
                Category(
                    name="functional_area",
                    label="功能区",
                    leaves=[
                        LeafTag(name="registration", label="注册"),
                    ],
                )
            ],
        )


@pytest.mark.asyncio
async def test_persist_writes_knowledge_domains_before_tags(monkeypatch) -> None:
    conn = _RecordingConnection()
    handler = InitTagsHandler(_FakeUseCase())

    async def fake_connect(_dsn: str) -> _RecordingConnection:
        return conn

    async def fake_close(self) -> None:
        return None

    monkeypatch.setattr("src.application.init.handlers.asyncpg.connect", fake_connect)

    command = InitTagsCommand(
        workspace_id=UUID("00000000-0000-0000-0000-000000000101"),
        domain="university_policy",
        description="高校学籍政策",
    )
    tree = await _FakeUseCase().execute(command)
    await handler._persist(command, tree)

    assert any("knowledge_domains" in q for q in conn.queries)
    domain_idx = next(i for i, q in enumerate(conn.queries) if "knowledge_domains" in q)
    tag_idx = next(i for i, q in enumerate(conn.queries) if "INSERT INTO tags" in q)
    assert domain_idx < tag_idx
    assert any("initialized_at" in q and "UPDATE knowledge_domains" in q for q in conn.queries)
