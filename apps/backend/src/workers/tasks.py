from uuid import UUID

from taskiq import Context as TaskiqContext
from taskiq import TaskiqDepends

from src.application.maintenance.dedupe_workflow import DedupeWorkflow, RunDedupeWorkflowCommand
from src.core.config import settings
from src.core.context import (
    ExecutionContext,
    clear_execution_context,
    set_trace_id,
    set_workspace_id,
)
from src.core.observability import (
    annotate_current_span,
    clear_current_execution_context,
    set_current_execution_context,
    start_observability_span,
)
from src.core.tracing import apply_async_context
from src.infrastructure.wiring import build_async_wiki_repository, build_search_engine
from src.workers.broker import broker

# 提示：在这里不需要手动 import src.workers.tasks
# 因为 worker.py 里的 modules 参数会自动加载它们


@broker.task
async def ping_worker() -> str:
    return "pong"


TaskContext = ExecutionContext


def _parse_bool_label(value: object | None) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def _parse_int_label(value: object | None, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def build_task_context(
    taskiq_context: TaskiqContext | None = None,
    workspace_id: str | UUID | None = None,
    trace_id: str | None = None,
    task_queue: str = "default",
) -> TaskContext:
    task_id = taskiq_context.message.task_id if taskiq_context is not None else "unknown-task-id"
    task_name = taskiq_context.message.task_name if taskiq_context is not None else "unknown-task"
    labels = taskiq_context.message.labels if taskiq_context is not None else {}
    retry_count = _parse_int_label(labels.get("_retries"), 0)
    max_retries = labels.get("max_retries")
    parsed_max_retries = None
    if max_retries is not None:
        parsed_max_retries = _parse_int_label(max_retries, 0)
    retry_on_error = _parse_bool_label(labels.get("retry_on_error"))

    parsed_workspace_id: UUID | None = None
    raw_workspace_id = str(workspace_id) if workspace_id is not None else None
    workspace_valid = True

    if isinstance(workspace_id, UUID):
        parsed_workspace_id = workspace_id
    elif isinstance(workspace_id, str):
        try:
            parsed_workspace_id = UUID(workspace_id)
        except ValueError:
            workspace_valid = False

    resolved_trace_id = apply_async_context(trace_id, parsed_workspace_id)
    return TaskContext(
        task_id=task_id,
        task_name=task_name,
        task_queue=task_queue,
        retry_count=retry_count,
        max_retries=parsed_max_retries,
        retry_on_error=retry_on_error,
        workspace_id=parsed_workspace_id,
        trace_id=resolved_trace_id,
        workspace_valid=workspace_valid,
        raw_workspace_id=raw_workspace_id,
    )


@broker.task
async def compile_document_async(
    source_document_id: str,
    title: str,
    workspace_id: str | None = None,
    trace_id: str | None = None,
    context: TaskiqContext = TaskiqDepends(),
) -> dict[str, object]:
    task_context = build_task_context(context, workspace_id, trace_id)
    set_current_execution_context(task_context)
    set_trace_id(task_context.trace_id)
    set_workspace_id(task_context.workspace_id)
    try:
        with start_observability_span(
            "taskiq",
            "execute.compile_document_async",
            trace_id=task_context.trace_id,
            workspace_id=task_context.workspace_id,
            raw_workspace_id=task_context.raw_workspace_id,
            workspace_valid=task_context.workspace_valid,
            runtime="worker",
            task_name=task_context.task_name,
            task_id=task_context.task_id,
            task_queue=task_context.task_queue,
            task_retry_count=task_context.retry_count,
            task_retry_max=task_context.max_retries,
            task_retry_on_error=task_context.retry_on_error,
            extra_attributes={
                "source_document_id": source_document_id,
                "document.title": title,
                "document.workflow": "compile",
                "hello_wiki.workspace_valid": task_context.workspace_valid,
            },
        ):
            annotate_current_span(
                ExecutionContext(
                    trace_id=task_context.trace_id,
                    workspace_id=task_context.workspace_id,
                    raw_workspace_id=task_context.raw_workspace_id,
                    workspace_valid=task_context.workspace_valid,
                    runtime="worker",
                    component="taskiq",
                    operation="execute.compile_document_async",
                    task_name=task_context.task_name,
                    task_id=task_context.task_id,
                    task_queue=task_context.task_queue,
                    retry_count=task_context.retry_count,
                    max_retries=task_context.max_retries,
                    retry_on_error=task_context.retry_on_error,
                ),
                {
                    "source_document_id": source_document_id,
                    "document.title": title,
                },
            )
            return {
                "source_document_id": source_document_id,
                "title": title,
                "workspace_id": task_context.raw_workspace_id or "",
                "trace_id": task_context.trace_id,
                "workspace_valid": str(task_context.workspace_valid).lower(),
                "task_id": task_context.task_id,
                "task_name": task_context.task_name,
                "task_queue": task_context.task_queue,
                "retry_count": str(task_context.retry_count),
                "max_retries": str(task_context.max_retries)
                if task_context.max_retries is not None
                else "",
                "retry_on_error": str(task_context.retry_on_error).lower(),
                "status": "queued",
                "redis": settings.REDIS_URL,
            }
    finally:
        clear_current_execution_context()
        clear_execution_context()
        set_trace_id(None)
        set_workspace_id(None)


@broker.task
async def run_dedupe_workflow(
    workspace_id: str,
    trace_id: str | None = None,
    context: TaskiqContext = TaskiqDepends(),
) -> dict[str, object]:
    task_context = build_task_context(context, workspace_id, trace_id)
    set_current_execution_context(task_context)
    set_trace_id(task_context.trace_id)
    set_workspace_id(task_context.workspace_id)
    try:
        with start_observability_span(
            "taskiq",
            "execute.run_dedupe_workflow",
            trace_id=task_context.trace_id,
            workspace_id=task_context.workspace_id,
            raw_workspace_id=task_context.raw_workspace_id,
            workspace_valid=task_context.workspace_valid,
            runtime="worker",
            task_name=task_context.task_name,
            task_id=task_context.task_id,
            task_queue=task_context.task_queue,
            task_retry_count=task_context.retry_count,
            task_retry_max=task_context.max_retries,
            task_retry_on_error=task_context.retry_on_error,
            extra_attributes={
                "hello_wiki.workspace_valid": task_context.workspace_valid,
            },
        ):
            annotate_current_span(
                ExecutionContext(
                    trace_id=task_context.trace_id,
                    workspace_id=task_context.workspace_id,
                    raw_workspace_id=task_context.raw_workspace_id,
                    workspace_valid=task_context.workspace_valid,
                    runtime="worker",
                    component="taskiq",
                    operation="execute.run_dedupe_workflow",
                    task_name=task_context.task_name,
                    task_id=task_context.task_id,
                    task_queue=task_context.task_queue,
                    retry_count=task_context.retry_count,
                    max_retries=task_context.max_retries,
                    retry_on_error=task_context.retry_on_error,
                ),
                {},
            )
            if not task_context.workspace_valid or task_context.workspace_id is None:
                return {
                    "status": "failed",
                    "error": "invalid workspace_id",
                    "workspace_id": workspace_id,
                    "trace_id": task_context.trace_id,
                    "task_id": task_context.task_id,
                    "task_name": task_context.task_name,
                    "task_queue": task_context.task_queue,
                    "retry_count": task_context.retry_count,
                    "max_retries": task_context.max_retries,
                    "retry_on_error": task_context.retry_on_error,
                }

            workflow = DedupeWorkflow(
                repository=build_async_wiki_repository(),
                search_engine=build_search_engine(),
            )

            result = await workflow.execute(
                RunDedupeWorkflowCommand(workspace_id=task_context.workspace_id)
            )
            return {
                "task_id": str(result.task.task_id),
                "task_type": result.task.task_type.value,
                "status": result.task.status.value,
                "workspace_id": str(result.task.workspace_id),
                "trace_id": task_context.trace_id,
                "task_name": task_context.task_name,
                "task_queue": task_context.task_queue,
                "retry_count": task_context.retry_count,
                "max_retries": task_context.max_retries,
                "retry_on_error": task_context.retry_on_error,
                "candidate_count": len(result.candidates),
            }
    finally:
        clear_current_execution_context()
        clear_execution_context()
        set_trace_id(None)
        set_workspace_id(None)
