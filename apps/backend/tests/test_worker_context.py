from __future__ import annotations

from taskiq.message import TaskiqMessage
from taskiq.result import TaskiqResult

from src.core.context import get_execution_context, get_trace_id, get_workspace_id
from src.workers.context_middleware import ExecutionContextMiddleware


def _build_message(**kwargs):
    return TaskiqMessage(
        task_id=kwargs.get("task_id", "task-001"),
        task_name=kwargs.get("task_name", "src.workers.tasks.run_dedupe_workflow"),
        labels=kwargs.get("labels", {}),
        args=kwargs.get("args", []),
        kwargs=kwargs.get("message_kwargs", {}),
    )


def _build_result() -> TaskiqResult[str]:
    return TaskiqResult(is_err=False, return_value="ok", execution_time=0.1)


def test_worker_pre_execute_builds_execution_context_from_message_kwargs():
    middleware = ExecutionContextMiddleware()
    message = _build_message(
        labels={"_retries": "2", "max_retries": "5", "retry_on_error": "true", "queue": "priority"},
        message_kwargs={
            "workspace_id": "00000000-0000-0000-0000-000000000030",
            "trace_id": "trace-worker-001",
        },
    )

    middleware.pre_execute(message)

    context = get_execution_context()
    assert context is not None
    assert context.runtime == "worker"
    assert context.component == "taskiq"
    assert context.operation == "src.workers.tasks.run_dedupe_workflow"
    assert context.task_id == "task-001"
    assert context.task_queue == "priority"
    assert context.retry_count == 2
    assert context.max_retries == 5
    assert context.retry_on_error is True
    assert context.raw_workspace_id == "00000000-0000-0000-0000-000000000030"
    assert str(context.workspace_id) == "00000000-0000-0000-0000-000000000030"
    assert get_workspace_id() == context.workspace_id
    assert get_trace_id() == "trace-worker-001"


def test_worker_pre_execute_handles_invalid_workspace_id():
    middleware = ExecutionContextMiddleware()
    message = _build_message(message_kwargs={"workspace_id": "bad-id", "trace_id": 12345})

    middleware.pre_execute(message)

    context = get_execution_context()
    assert context is not None
    assert context.workspace_id is None
    assert context.workspace_valid is False
    assert context.raw_workspace_id == "bad-id"
    assert get_workspace_id() is None
    assert get_trace_id() == "12345"


def test_worker_post_execute_clears_runtime_context():
    middleware = ExecutionContextMiddleware()
    message = _build_message(
        message_kwargs={"workspace_id": "00000000-0000-0000-0000-000000000031"}
    )

    middleware.pre_execute(message)
    middleware.post_execute(message, _build_result())

    assert get_execution_context() is None
    assert get_workspace_id() is None
    assert get_trace_id() == "no-trace-id"


def test_worker_on_error_clears_runtime_context():
    middleware = ExecutionContextMiddleware()
    message = _build_message(
        message_kwargs={"workspace_id": "00000000-0000-0000-0000-000000000032"}
    )

    middleware.pre_execute(message)
    middleware.on_error(message, _build_result(), RuntimeError("boom"))

    assert get_execution_context() is None
    assert get_workspace_id() is None
    assert get_trace_id() == "no-trace-id"
