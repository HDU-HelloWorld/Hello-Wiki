from __future__ import annotations

import asyncio
from contextlib import nullcontext
from types import SimpleNamespace

from src.domain.maintenance.entities import MaintenanceTask, TaskType
from src.infrastructure.db.repositories.async_wiki_repo_adapter import AsyncWikiRepositoryAdapter
from src.workers import tasks


def _build_taskiq_context() -> object:
    return SimpleNamespace(
        message=SimpleNamespace(
            task_id="task-async-001",
            task_name="src.workers.tasks.run_dedupe_workflow",
            labels={},
        )
    )


def test_run_dedupe_workflow_awaits_execute(monkeypatch) -> None:
    awaited = {"called": False}
    captured = {"repository": None}

    class FakeWorkflow:
        def __init__(self, repository, search_engine) -> None:
            captured["repository"] = repository
            self._repository = repository
            self._search_engine = search_engine

        async def execute(self, command):
            awaited["called"] = True
            task = MaintenanceTask.create(command.workspace_id, TaskType.SEMANTIC_DEDUP)
            return SimpleNamespace(task=task, candidates=[])

    monkeypatch.setattr(tasks, "DedupeWorkflow", FakeWorkflow)
    monkeypatch.setattr(tasks, "start_observability_span", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(tasks, "annotate_current_span", lambda *args, **kwargs: None)

    result = asyncio.run(
        tasks.run_dedupe_workflow(
            workspace_id="00000000-0000-0000-0000-000000000120",
            trace_id="trace-worker-async-001",
            context=_build_taskiq_context(),
        )
    )

    assert awaited["called"] is True
    assert result["status"] == "PENDING"
    assert result["candidate_count"] == 0
    assert isinstance(captured["repository"], AsyncWikiRepositoryAdapter)


def test_run_dedupe_workflow_uses_shared_repository_builder(monkeypatch) -> None:
    called = {"count": 0}
    original_builder = tasks.build_async_wiki_repository

    def _wrapped_builder():
        called["count"] += 1
        return original_builder()

    class FakeWorkflow:
        def __init__(self, repository, search_engine) -> None:
            self._repository = repository
            self._search_engine = search_engine

        async def execute(self, command):
            task = MaintenanceTask.create(command.workspace_id, TaskType.SEMANTIC_DEDUP)
            return SimpleNamespace(task=task, candidates=[])

    monkeypatch.setattr(tasks, "build_async_wiki_repository", _wrapped_builder)
    monkeypatch.setattr(tasks, "DedupeWorkflow", FakeWorkflow)
    monkeypatch.setattr(tasks, "start_observability_span", lambda *args, **kwargs: nullcontext())
    monkeypatch.setattr(tasks, "annotate_current_span", lambda *args, **kwargs: None)

    asyncio.run(
        tasks.run_dedupe_workflow(
            workspace_id="00000000-0000-0000-0000-000000000121",
            trace_id="trace-worker-builder-001",
            context=_build_taskiq_context(),
        )
    )

    assert called["count"] == 1
