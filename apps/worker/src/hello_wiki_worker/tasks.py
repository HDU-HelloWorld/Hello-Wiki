from uuid import UUID

from taskiq import Context as TaskiqContext
from taskiq import TaskiqDepends

from hello_wiki_worker.broker import broker
from src.application.ingest.commands import IngestDocumentCommand
from src.application.maintenance.dedupe_workflow import DedupeWorkflow, RunDedupeWorkflowCommand
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
from src.core.task_names import COMPILE_DOCUMENT_TASK_NAME, RUN_DEDUPE_TASK_NAME
from src.core.tracing import apply_async_context
from src.infrastructure.wiring import (
    build_async_wiki_repository,
    build_ingest_pipeline,
    build_search_engine,
)

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


@broker.task(task_name=COMPILE_DOCUMENT_TASK_NAME)
async def compile_document_async(
    document_id: str,
    file_path: str,
    domain: str,
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
                "document_id": document_id,
                "document.path": file_path,
                "document.domain": domain,
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
                    "document_id": document_id,
                    "document.path": file_path,
                    "document.domain": domain,
                },
            )
            pipeline = build_ingest_pipeline()
            result = await pipeline.execute(
                IngestDocumentCommand(
                    workspace_id=workspace_id,
                    file_path=file_path,
                    domain=domain,
                )
            )
            failed_count = _parse_int_label(result.get("failed"), 0)
            return {
                "status": "completed" if failed_count == 0 else "partial",
                "document_id": document_id,
                "workspace_id": workspace_id,
                "trace_id": task_context.trace_id,
                "total_chunks": _parse_int_label(result.get("total_chunks"), 0),
                "successful": _parse_int_label(result.get("successful"), 0),
                "failed": failed_count,
                "error": None,
                "errors": result.get("errors") if isinstance(result.get("errors"), list) else [],
            }
    finally:
        clear_current_execution_context()
        clear_execution_context()
        set_trace_id(None)
        set_workspace_id(None)


@broker.task(task_name=RUN_DEDUPE_TASK_NAME)
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
            extra_attributes={"hello_wiki.workspace_valid": task_context.workspace_valid},
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
                    "workspace_id": workspace_id,
                    "trace_id": task_context.trace_id,
                    "candidate_count": 0,
                    "error": "invalid workspace_id",
                    "errors": [],
                }

            workflow = DedupeWorkflow(
                repository=build_async_wiki_repository(),
                search_engine=build_search_engine(),
            )
            result = await workflow.execute(
                RunDedupeWorkflowCommand(workspace_id=task_context.workspace_id)
            )
            return {
                "status": result.task.status.value,
                "workspace_id": str(result.task.workspace_id),
                "trace_id": task_context.trace_id,
                "candidate_count": len(result.candidates),
                "error": None,
                "errors": [],
            }
    finally:
        clear_current_execution_context()
        clear_execution_context()
        set_trace_id(None)
        set_workspace_id(None)
