from __future__ import annotations

from taskiq.message import TaskiqMessage
from taskiq.result import TaskiqResult

from hello_wiki_worker.context_middleware import ExecutionContextMiddleware
from src.core.context import get_execution_context, get_trace_id, get_workspace_id
from src.core.task_names import RUN_DEDUPE_TASK_NAME


def _build_message(**kwargs) -> TaskiqMessage:  # noqa: ANN003
    return TaskiqMessage(
        task_id=kwargs.get("task_id", "task-ctx-001"),
        task_name=kwargs.get("task_name", RUN_DEDUPE_TASK_NAME),
        labels=kwargs.get("labels", {}),
        args=kwargs.get("args", []),
        kwargs=kwargs.get(
            "kwargs",
            {
                "workspace_id": "00000000-0000-0000-0000-000000000120",
                "trace_id": "trace-worker-001",
            },
        ),
    )


def _build_result() -> TaskiqResult[str]:
    return TaskiqResult(is_err=False, return_value="ok", execution_time=0.1)


def test_worker_pre_execute_builds_execution_context_from_message_kwargs():
    middleware = ExecutionContextMiddleware()
    message = _build_message()

    middleware.pre_execute(message)

    context = get_execution_context()
    assert context is not None
    assert context.runtime == "worker"
    assert context.component == "taskiq"
    assert context.operation == RUN_DEDUPE_TASK_NAME
    assert str(context.workspace_id) == "00000000-0000-0000-0000-000000000120"
    assert context.trace_id == "trace-worker-001"
    assert get_workspace_id() == context.workspace_id
    assert get_trace_id() == "trace-worker-001"


def test_worker_pre_execute_handles_invalid_workspace_id():
    middleware = ExecutionContextMiddleware()
    message = _build_message(
        kwargs={"workspace_id": "invalid-workspace-id", "trace_id": "trace-worker-002"}
    )

    middleware.pre_execute(message)

    context = get_execution_context()
    assert context is not None
    assert context.workspace_id is None
    assert context.raw_workspace_id == "invalid-workspace-id"
    assert context.workspace_valid is False


def test_worker_post_execute_clears_runtime_context():
    middleware = ExecutionContextMiddleware()
    message = _build_message()

    middleware.pre_execute(message)
    middleware.post_execute(message, _build_result())

    assert get_execution_context() is None
    assert get_workspace_id() is None
    assert get_trace_id() == "no-trace-id"


def test_worker_on_error_clears_runtime_context():
    middleware = ExecutionContextMiddleware()
    message = _build_message()

    middleware.pre_execute(message)
    middleware.on_error(message, _build_result(), RuntimeError("boom"))

    assert get_execution_context() is None
    assert get_workspace_id() is None
    assert get_trace_id() == "no-trace-id"
