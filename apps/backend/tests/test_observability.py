from __future__ import annotations

from contextlib import contextmanager
from typing import cast
from uuid import UUID

from opentelemetry.trace import Span

from src.core.context import ExecutionContext, get_execution_context, set_execution_context
from src.core.observability import (
    ATTR_HTTP_METHOD,
    ATTR_HTTP_ROUTE,
    ATTR_HTTP_STATUS_CODE,
    ATTR_OPERATION,
    ATTR_RUNTIME,
    ATTR_TASK_ID,
    ATTR_TASK_NAME,
    ATTR_TASK_QUEUE,
    ATTR_TRACE_ID,
    ATTR_WORKFLOW_KIND,
    ATTR_WORKFLOW_NAME,
    ATTR_WORKSPACE_ID,
    annotate_current_span,
    annotate_span,
    build_span_name,
    clear_current_execution_context,
    get_current_execution_context,
    start_observability_span,
)


class _FakeSpan:
    def __init__(self) -> None:
        self.attributes: dict[str, object] = {}

    def is_recording(self) -> bool:
        return True

    def set_attribute(self, key: str, value: object) -> None:
        self.attributes[key] = value


class _FakeTracer:
    def __init__(self) -> None:
        self.names: list[str] = []
        self.spans: list[_FakeSpan] = []

    @contextmanager
    def start_as_current_span(self, name: str):
        self.names.append(name)
        span = _FakeSpan()
        self.spans.append(span)
        yield span


def test_build_span_name_combines_component_and_operation():
    assert build_span_name("taskiq", "run_dedupe_workflow") == "taskiq.run_dedupe_workflow"


def test_annotate_span_writes_execution_context_attributes():
    span = _FakeSpan()
    context = ExecutionContext(
        trace_id="trace-obs-1",
        workspace_id=UUID("00000000-0000-0000-0000-000000000040"),
        raw_workspace_id="00000000-0000-0000-0000-000000000040",
        workspace_valid=True,
        runtime="worker",
        component="taskiq",
        operation="execute",
        request_method="POST",
        request_path="/api/v1/test",
        request_status_code=201,
        task_name="run_task",
        task_id="task-1",
        task_queue="default",
        retry_count=2,
        max_retries=5,
        retry_on_error=True,
        workflow_name="dedupe",
        workflow_kind="maintenance",
    )

    annotate_span(
        cast(Span, span),
        context,
        extra_attributes={"custom.flag": True},
    )

    assert span.attributes[ATTR_TRACE_ID] == "trace-obs-1"
    assert span.attributes[ATTR_WORKSPACE_ID] == "00000000-0000-0000-0000-000000000040"
    assert span.attributes[ATTR_RUNTIME] == "worker"
    assert span.attributes[ATTR_OPERATION] == "execute"
    assert span.attributes[ATTR_HTTP_METHOD] == "POST"
    assert span.attributes[ATTR_HTTP_ROUTE] == "/api/v1/test"
    assert span.attributes[ATTR_HTTP_STATUS_CODE] == 201
    assert span.attributes[ATTR_TASK_NAME] == "run_task"
    assert span.attributes[ATTR_TASK_ID] == "task-1"
    assert span.attributes[ATTR_TASK_QUEUE] == "default"
    assert span.attributes[ATTR_WORKFLOW_NAME] == "dedupe"
    assert span.attributes[ATTR_WORKFLOW_KIND] == "maintenance"
    assert span.attributes["custom.flag"] is True


def test_start_observability_span_sets_and_restores_execution_context(monkeypatch):
    fake_tracer = _FakeTracer()
    monkeypatch.setattr("src.core.observability.trace.get_tracer", lambda name: fake_tracer)

    previous_context = ExecutionContext(
        trace_id="trace-outer",
        workspace_id=UUID("00000000-0000-0000-0000-000000000041"),
        runtime="api",
        component="outer",
        operation="outer-op",
    )
    set_execution_context(previous_context)

    with start_observability_span(
        "taskiq",
        "run_dedupe_workflow",
        trace_id="trace-inner",
        workspace_id=UUID("00000000-0000-0000-0000-000000000042"),
        runtime="worker",
        task_name="run_dedupe_workflow",
        task_id="task-2",
        task_queue="default",
        workflow_name="dedupe",
        workflow_kind="maintenance",
        extra_attributes={"hello_wiki.test_flag": True},
    ) as span:
        assert span is fake_tracer.spans[0]
        current_context = get_current_execution_context()
        assert current_context is not None
        assert current_context.trace_id == "trace-inner"
        assert str(current_context.workspace_id) == "00000000-0000-0000-0000-000000000042"

    assert fake_tracer.names == ["taskiq.run_dedupe_workflow"]
    assert fake_tracer.spans[0].attributes[ATTR_TRACE_ID] == "trace-inner"
    assert (
        fake_tracer.spans[0].attributes[ATTR_WORKSPACE_ID] == "00000000-0000-0000-0000-000000000042"
    )
    assert fake_tracer.spans[0].attributes[ATTR_TASK_NAME] == "run_dedupe_workflow"
    assert fake_tracer.spans[0].attributes[ATTR_TASK_ID] == "task-2"
    assert fake_tracer.spans[0].attributes["hello_wiki.test_flag"] is True

    restored_context = get_current_execution_context()
    assert restored_context == previous_context


def test_annotate_current_span_is_noop_without_recording_span(monkeypatch):
    monkeypatch.setattr("src.core.observability.trace.get_current_span", lambda: None)

    annotate_current_span(
        ExecutionContext(
            trace_id="trace-noop",
            workspace_id=UUID("00000000-0000-0000-0000-000000000043"),
        ),
        {"flag": False},
    )

    assert get_execution_context() is None
    clear_current_execution_context()
