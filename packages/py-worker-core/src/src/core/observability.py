from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import UUID

from opentelemetry import baggage, trace
from opentelemetry import context as otel_context
from opentelemetry.trace import Span

from src.core.context import (
    ExecutionContext,
    clear_execution_context,
    get_execution_context,
    set_execution_context,
)

logger = logging.getLogger(__name__)

OBSERVABILITY_NAMESPACE = "hello-wiki"
ATTR_TRACE_ID = "hello_wiki.trace_id"
ATTR_WORKSPACE_ID = "hello_wiki.workspace_id"
ATTR_RUNTIME = "hello_wiki.runtime"
ATTR_COMPONENT = "hello_wiki.component"
ATTR_OPERATION = "hello_wiki.operation"
ATTR_TASK_NAME = "taskiq.task_name"
ATTR_TASK_QUEUE = "taskiq.task_queue"
ATTR_TASK_ID = "taskiq.task_id"
ATTR_TASK_RETRY_COUNT = "taskiq.retry.count"
ATTR_TASK_RETRY_MAX = "taskiq.retry.max"
ATTR_TASK_RETRY_ON_ERROR = "taskiq.retry.on_error"
ATTR_HTTP_METHOD = "http.method"
ATTR_HTTP_ROUTE = "http.route"
ATTR_HTTP_STATUS_CODE = "http.status_code"
ATTR_WORKFLOW_NAME = "llamaindex.workflow.name"
ATTR_WORKFLOW_KIND = "llamaindex.workflow.kind"
ATTR_REPOSITORY_NAME = "llamaindex.repository.name"
ATTR_SEARCH_ENGINE_NAME = "llamaindex.search_engine.name"


ObservabilityContext = ExecutionContext


def build_span_name(component: str, operation: str) -> str:
    return f"{component}.{operation}"


def _stringify_workspace_id(workspace_id: UUID | str | None) -> str | None:
    if workspace_id is None:
        return None
    return str(workspace_id)


def _parse_workspace_id(workspace_id: UUID | str | None) -> UUID | None:
    if workspace_id is None:
        return None
    if isinstance(workspace_id, UUID):
        return workspace_id
    try:
        return UUID(str(workspace_id))
    except ValueError:
        return None


def _set_span_attribute(span: Span, key: str, value: Any | None) -> None:
    if value is None:
        return
    span.set_attribute(key, value)


def annotate_span(
    span: Span, context: ExecutionContext, extra_attributes: dict[str, object] | None = None
) -> None:
    _set_span_attribute(span, ATTR_TRACE_ID, context.trace_id)
    _set_span_attribute(span, ATTR_WORKSPACE_ID, _stringify_workspace_id(context.workspace_id))
    _set_span_attribute(span, "hello_wiki.workspace_raw_id", context.raw_workspace_id)
    _set_span_attribute(span, "hello_wiki.workspace_valid", context.workspace_valid)
    _set_span_attribute(span, ATTR_RUNTIME, context.runtime)
    _set_span_attribute(span, ATTR_COMPONENT, context.component)
    _set_span_attribute(span, ATTR_OPERATION, context.operation)
    _set_span_attribute(span, ATTR_HTTP_METHOD, context.request_method)
    _set_span_attribute(span, ATTR_HTTP_ROUTE, context.request_path)
    _set_span_attribute(span, ATTR_HTTP_STATUS_CODE, context.request_status_code)
    _set_span_attribute(span, ATTR_TASK_NAME, context.task_name)
    _set_span_attribute(span, ATTR_TASK_ID, context.task_id)
    _set_span_attribute(span, ATTR_TASK_QUEUE, context.task_queue)
    _set_span_attribute(span, ATTR_TASK_RETRY_COUNT, context.retry_count)
    _set_span_attribute(span, ATTR_TASK_RETRY_MAX, context.max_retries)
    _set_span_attribute(span, ATTR_TASK_RETRY_ON_ERROR, context.retry_on_error)
    _set_span_attribute(span, ATTR_WORKFLOW_NAME, context.workflow_name)
    _set_span_attribute(span, ATTR_WORKFLOW_KIND, context.workflow_kind)

    if extra_attributes:
        for key, value in extra_attributes.items():
            _set_span_attribute(span, key, value)


def annotate_current_span(
    context: ExecutionContext, extra_attributes: dict[str, object] | None = None
) -> None:
    span = trace.get_current_span()
    if span is None or not span.is_recording():
        return
    annotate_span(span, context, extra_attributes)


def set_current_execution_context(context: ExecutionContext | None) -> None:
    set_execution_context(context)


def get_current_execution_context() -> ExecutionContext | None:
    return get_execution_context()


def clear_current_execution_context() -> None:
    clear_execution_context()


@contextmanager
def start_observability_span(
    component: str,
    operation: str,
    *,
    trace_id: str | None = None,
    workspace_id: UUID | str | None = None,
    raw_workspace_id: str | None = None,
    workspace_valid: bool | None = None,
    runtime: str | None = None,
    request_method: str | None = None,
    request_path: str | None = None,
    request_status_code: int | None = None,
    task_name: str | None = None,
    task_id: str | None = None,
    task_queue: str | None = None,
    task_retry_count: int | None = None,
    task_retry_max: int | None = None,
    task_retry_on_error: bool | None = None,
    workflow_name: str | None = None,
    workflow_kind: str | None = None,
    extra_attributes: dict[str, object] | None = None,
) -> Iterator[Span]:
    tracer = trace.get_tracer(f"{OBSERVABILITY_NAMESPACE}.{component}")
    span_name = build_span_name(component, operation)
    parsed_workspace_id = _parse_workspace_id(workspace_id)
    context = ExecutionContext(
        trace_id=trace_id,
        workspace_id=parsed_workspace_id,
        raw_workspace_id=raw_workspace_id,
        workspace_valid=workspace_valid,
        runtime=runtime,
        component=component,
        operation=operation,
        request_method=request_method,
        request_path=request_path,
        request_status_code=request_status_code,
        task_name=task_name,
        task_id=task_id,
        task_queue=task_queue,
        retry_count=task_retry_count,
        max_retries=task_retry_max,
        retry_on_error=task_retry_on_error,
        workflow_name=workflow_name,
        workflow_kind=workflow_kind,
    )
    baggage_context = otel_context.get_current()
    if trace_id:
        baggage_context = baggage.set_baggage(ATTR_TRACE_ID, trace_id, baggage_context)
    workspace_value = _stringify_workspace_id(parsed_workspace_id)
    if workspace_value:
        baggage_context = baggage.set_baggage(ATTR_WORKSPACE_ID, workspace_value, baggage_context)

    previous_context = get_execution_context()
    set_execution_context(context)
    token = otel_context.attach(baggage_context)
    try:
        with tracer.start_as_current_span(span_name) as span:
            annotate_span(span, context, extra_attributes)
            yield span
    finally:
        otel_context.detach(token)
        set_execution_context(previous_context)


def _parse_otlp_headers(raw_headers: str | None) -> dict[str, str] | None:
    if not raw_headers:
        return None

    pairs = [segment.strip() for segment in raw_headers.split(",") if segment.strip()]
    headers: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        headers[key.strip()] = value.strip()
    return headers or None
