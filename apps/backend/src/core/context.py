from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID

# 租户隔离上下文 (Workspace ID)
_workspace_id_ctx: ContextVar[UUID | None] = ContextVar("workspace_id", default=None)

# 全链路追踪上下文 (Trace ID)
_trace_id_ctx: ContextVar[str | None] = ContextVar("trace_id", default=None)


@dataclass(frozen=True)
class ExecutionContext:
    trace_id: str | None
    workspace_id: UUID | None
    raw_workspace_id: str | None = None
    workspace_valid: bool | None = None
    runtime: str | None = None
    component: str | None = None
    operation: str | None = None
    request_method: str | None = None
    request_path: str | None = None
    request_status_code: int | None = None
    task_name: str | None = None
    task_id: str | None = None
    task_queue: str | None = None
    retry_count: int | None = None
    max_retries: int | None = None
    retry_on_error: bool | None = None
    workflow_name: str | None = None
    workflow_kind: str | None = None

    @property
    def task_retry_count(self) -> int | None:
        return self.retry_count

    @property
    def task_retry_max(self) -> int | None:
        return self.max_retries

    @property
    def task_retry_on_error(self) -> bool | None:
        return self.retry_on_error


_execution_context_ctx: ContextVar[ExecutionContext | None] = ContextVar(
    "execution_context", default=None
)


def set_workspace_id(workspace_id: UUID | None) -> None:
    _workspace_id_ctx.set(workspace_id)


def get_workspace_id() -> UUID | None:
    workspace_id = _workspace_id_ctx.get()
    if workspace_id is not None:
        return workspace_id

    execution_context = _execution_context_ctx.get()
    if execution_context is not None:
        return execution_context.workspace_id

    return None


def set_trace_id(trace_id: str | None) -> None:
    _trace_id_ctx.set(trace_id)


def get_trace_id() -> str:
    trace_id = _trace_id_ctx.get()
    if trace_id:
        return trace_id

    execution_context = _execution_context_ctx.get()
    if execution_context is not None and execution_context.trace_id:
        return execution_context.trace_id

    return "no-trace-id"


def set_execution_context(execution_context: ExecutionContext | None) -> None:
    _execution_context_ctx.set(execution_context)


def get_execution_context() -> ExecutionContext | None:
    return _execution_context_ctx.get()


def clear_execution_context() -> None:
    _execution_context_ctx.set(None)
