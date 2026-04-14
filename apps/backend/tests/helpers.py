from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from src.api.gateway import GatewayContext, GatewayHook
from src.core.context import clear_execution_context, set_trace_id, set_workspace_id


@dataclass(frozen=True)
class GatewayRecordedEvent:
    kind: str
    context: GatewayContext
    status_code: int | None = None
    duration_ms: float | None = None
    error: str | None = None


class RecordingGatewayHook(GatewayHook):
    """统一测试 hook：记录 gateway 生命周期事件，便于断言。"""

    def __init__(self) -> None:
        self.events: list[GatewayRecordedEvent] = []

    def on_request_start(self, request: Request, context: GatewayContext) -> None:
        self.events.append(GatewayRecordedEvent(kind="start", context=context))

    def on_request_finish(
        self, request: Request, context: GatewayContext, status_code: int, duration_ms: float
    ) -> None:
        self.events.append(
            GatewayRecordedEvent(
                kind="finish",
                context=context,
                status_code=status_code,
                duration_ms=duration_ms,
            )
        )

    def on_request_error(self, request: Request, context: GatewayContext, error: Exception) -> None:
        self.events.append(
            GatewayRecordedEvent(
                kind="error",
                context=context,
                error=type(error).__name__,
            )
        )


def reset_runtime_context() -> None:
    """统一重置运行时上下文，避免测试相互污染。"""
    clear_execution_context()
    set_trace_id(None)
    set_workspace_id(None)
