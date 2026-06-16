from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from src.core.config import settings
from src.core.task_names import COMPILE_DOCUMENT_TASK_NAME, RUN_DEDUPE_TASK_NAME

_RESULT_BACKEND: RedisAsyncResultBackend[Any] = RedisAsyncResultBackend(settings.REDIS_URL)
broker = ListQueueBroker(settings.REDIS_URL).with_result_backend(_RESULT_BACKEND)


@broker.task(task_name=COMPILE_DOCUMENT_TASK_NAME)
async def compile_document_async(  # pragma: no cover - producer stub only
    document_id: str,
    file_path: str,
    domain: str,
    workspace_id: str,
    trace_id: str | None = None,
) -> dict[str, object]:
    raise RuntimeError("compile_document_async is a producer stub and must run on worker")


@broker.task(task_name=RUN_DEDUPE_TASK_NAME)
async def run_dedupe_workflow(  # pragma: no cover - producer stub only
    workspace_id: str,
    trace_id: str | None = None,
) -> dict[str, object]:
    raise RuntimeError("run_dedupe_workflow is a producer stub and must run on worker")


@dataclass(frozen=True)
class TaskStatusRecord:
    status: str
    total_chunks: int = 0
    successful: int = 0
    failed: int = 0
    error: str | None = None
    errors: list[dict[str, object]] | None = None
    document_id: str | None = None
    workspace_id: str | None = None
    trace_id: str | None = None
    candidate_count: int | None = None

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": self.status,
            "document_id": self.document_id,
            "workspace_id": self.workspace_id,
            "trace_id": self.trace_id,
            "total_chunks": self.total_chunks,
            "successful": self.successful,
            "failed": self.failed,
            "error": self.error,
            "errors": self.errors or [],
        }
        if self.candidate_count is not None:
            payload["candidate_count"] = self.candidate_count
        return payload


def _coerce_optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _coerce_errors(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []

    errors: list[dict[str, object]] = []
    for item in value:
        if isinstance(item, dict):
            errors.append(cast(dict[str, object], item))
    return errors


async def enqueue_compile_document(
    *,
    document_id: str,
    file_path: str,
    domain: str,
    workspace_id: str,
    trace_id: str | None = None,
) -> str:
    task = await compile_document_async.kiq(
        document_id=document_id,
        file_path=file_path,
        domain=domain,
        workspace_id=workspace_id,
        trace_id=trace_id,
    )
    return str(task.task_id)


async def enqueue_run_dedupe_workflow(
    *,
    workspace_id: str,
    trace_id: str | None = None,
) -> str:
    task = await run_dedupe_workflow.kiq(workspace_id=workspace_id, trace_id=trace_id)
    return str(task.task_id)


def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return default


def _build_error_message(result: Any) -> str:
    for field_name in ("error", "return_value"):
        value = getattr(result, field_name, None)
        if value:
            return str(value)
    return "task failed"


def _coerce_mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    return {}


async def fetch_task_status(task_id: str) -> dict[str, object]:
    result_backend = broker.result_backend
    if result_backend is None:
        raise RuntimeError("TaskIQ result backend is not configured")

    if not await result_backend.is_result_ready(task_id):
        return TaskStatusRecord(status="pending").as_dict()

    result = await result_backend.get_result(task_id, with_logs=True)
    if getattr(result, "is_err", False):
        return TaskStatusRecord(status="failed", error=_build_error_message(result)).as_dict()

    payload = _coerce_mapping(getattr(result, "return_value", None))
    return TaskStatusRecord(
        status=str(payload.get("status", "completed")),
        total_chunks=_coerce_int(payload.get("total_chunks"), 0),
        successful=_coerce_int(payload.get("successful"), 0),
        failed=_coerce_int(payload.get("failed"), 0),
        error=_coerce_optional_str(payload.get("error")),
        errors=_coerce_errors(payload.get("errors")),
        document_id=_coerce_optional_str(payload.get("document_id")),
        workspace_id=_coerce_optional_str(payload.get("workspace_id")),
        trace_id=_coerce_optional_str(payload.get("trace_id")),
        candidate_count=_coerce_int(payload["candidate_count"], 0)
        if payload.get("candidate_count") is not None
        else None,
    ).as_dict()
