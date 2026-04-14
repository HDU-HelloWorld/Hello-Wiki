from __future__ import annotations

from uuid import UUID

import pytest
from fastapi import HTTPException

from src.api import deps
from src.core.context import (
    ExecutionContext,
    clear_execution_context,
    set_execution_context,
    set_workspace_id,
)


def test_get_container_is_cached(monkeypatch):
    sentinel = object()
    build_calls: list[str] = []

    def fake_build_container():
        build_calls.append("called")
        return sentinel

    monkeypatch.setattr(deps, "_build_container", fake_build_container)
    deps._CONTAINER = None

    first = deps.get_container()
    second = deps.get_container()

    assert first is sentinel
    assert second is sentinel
    assert build_calls == ["called"]


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
