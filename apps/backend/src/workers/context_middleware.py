from __future__ import annotations

from taskiq import TaskiqMessage, TaskiqMiddleware
from taskiq.result import TaskiqResult

from src.core.context import (
    ExecutionContext,
    clear_execution_context,
    set_execution_context,
    set_trace_id,
    set_workspace_id,
)
from src.core.tracing import parse_workspace_id


class ExecutionContextMiddleware(TaskiqMiddleware):
    @staticmethod
    def _parse_int_label(value: object | None, default: int | None = None) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return default

    def _build_context(self, message: TaskiqMessage) -> ExecutionContext:
        labels = message.labels
        workspace_id_raw = (
            message.kwargs.get("workspace_id") if isinstance(message.kwargs, dict) else None
        )
        trace_id = message.kwargs.get("trace_id") if isinstance(message.kwargs, dict) else None
        if trace_id is not None and not isinstance(trace_id, str):
            trace_id = str(trace_id)

        workspace_id = (
            parse_workspace_id(str(workspace_id_raw)) if workspace_id_raw is not None else None
        )
        retry_count = self._parse_int_label(labels.get("_retries"), 0) or 0
        max_retries = self._parse_int_label(labels.get("max_retries"), None)
        retry_on_error_raw = labels.get("retry_on_error")
        retry_on_error = False
        if isinstance(retry_on_error_raw, bool):
            retry_on_error = retry_on_error_raw
        elif isinstance(retry_on_error_raw, str):
            retry_on_error = retry_on_error_raw.lower() == "true"

        return ExecutionContext(
            trace_id=trace_id,
            workspace_id=workspace_id,
            raw_workspace_id=str(workspace_id_raw) if workspace_id_raw is not None else None,
            workspace_valid=workspace_id is not None or workspace_id_raw is None,
            runtime="worker",
            component="taskiq",
            operation=message.task_name,
            task_name=message.task_name,
            task_id=message.task_id,
            task_queue=str(labels.get("queue") or "default"),
            retry_count=retry_count,
            max_retries=max_retries,
            retry_on_error=retry_on_error,
        )

    def pre_execute(self, message: TaskiqMessage) -> TaskiqMessage:
        context = self._build_context(message)
        set_execution_context(context)
        set_trace_id(context.trace_id)
        set_workspace_id(context.workspace_id)
        return message

    def post_execute(self, message: TaskiqMessage, result: TaskiqResult[object]) -> None:
        clear_execution_context()
        set_trace_id(None)
        set_workspace_id(None)

    def on_error(
        self, message: TaskiqMessage, result: TaskiqResult[object], exception: BaseException
    ) -> None:
        clear_execution_context()
        set_trace_id(None)
        set_workspace_id(None)
