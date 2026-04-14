from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from src.core.context import ExecutionContext, set_trace_id, set_workspace_id
from src.core.logging import get_logger
from src.core.observability import (
    annotate_current_span,
    clear_current_execution_context,
    set_current_execution_context,
)
from src.core.tracing import apply_request_context, parse_workspace_id

logger = get_logger(__name__)


@dataclass(frozen=True)
class GatewayContext:
    method: str
    path: str
    trace_id: str
    started_at: float


class GatewayHook(Protocol):
    def on_request_start(self, request: Request, context: GatewayContext) -> None: ...

    def on_request_finish(
        self, request: Request, context: GatewayContext, status_code: int, duration_ms: float
    ) -> None: ...

    def on_request_error(
        self, request: Request, context: GatewayContext, error: Exception
    ) -> None: ...


class NoopGatewayHook:
    def on_request_start(self, request: Request, context: GatewayContext) -> None:
        return None

    def on_request_finish(
        self, request: Request, context: GatewayContext, status_code: int, duration_ms: float
    ) -> None:
        return None

    def on_request_error(self, request: Request, context: GatewayContext, error: Exception) -> None:
        return None


class CompositeGatewayHook:
    def __init__(self, hooks: Iterable[GatewayHook]) -> None:
        self._hooks = list(hooks)

    def on_request_start(self, request: Request, context: GatewayContext) -> None:
        for hook in self._hooks:
            hook.on_request_start(request, context)

    def on_request_finish(
        self, request: Request, context: GatewayContext, status_code: int, duration_ms: float
    ) -> None:
        for hook in self._hooks:
            hook.on_request_finish(request, context, status_code, duration_ms)

    def on_request_error(self, request: Request, context: GatewayContext, error: Exception) -> None:
        for hook in self._hooks:
            hook.on_request_error(request, context, error)


class TenantGatewayHook(NoopGatewayHook):
    """租户扩展点：预留租户访问策略和限制校验。"""


class TracingGatewayHook(NoopGatewayHook):
    """链路扩展点：预留 tracing/span 上报。"""


class AuthGatewayHook(NoopGatewayHook):
    """鉴权扩展点：预留认证策略接入。"""


class RbacGatewayHook(NoopGatewayHook):
    """权限扩展点：预留角色权限检查。"""


class UsageGatewayHook(NoopGatewayHook):
    """用量扩展点：预留配额/计费统计。"""


def build_default_gateway_hook() -> GatewayHook:
    return CompositeGatewayHook(
        [
            TenantGatewayHook(),
            TracingGatewayHook(),
            AuthGatewayHook(),
            RbacGatewayHook(),
            UsageGatewayHook(),
        ]
    )


def register_gateway_middleware(app: FastAPI, hook: GatewayHook | None = None) -> None:
    resolved_hook = hook or build_default_gateway_hook()

    @app.middleware("http")
    async def gateway_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
        """统一请求入口：注入租户、trace，并记录基础访问统计。"""
        started_at = perf_counter()
        trace_id = request.headers.get("X-Trace-ID")
        workspace_id_header = request.headers.get("X-Workspace-ID")
        parsed_workspace_id = parse_workspace_id(workspace_id_header)
        workspace_valid = workspace_id_header is None or parsed_workspace_id is not None

        resolved_trace_id = apply_request_context(trace_id, workspace_id_header)
        request.state.trace_id = resolved_trace_id
        request.state.workspace_id = parsed_workspace_id
        request.state.workspace_valid = workspace_valid
        execution_context = ExecutionContext(
            trace_id=resolved_trace_id,
            workspace_id=parsed_workspace_id,
            raw_workspace_id=workspace_id_header,
            workspace_valid=workspace_valid,
            runtime="api",
            component="gateway",
            operation=f"{request.method} {request.url.path}",
            request_method=request.method,
            request_path=request.url.path,
        )
        set_current_execution_context(execution_context)
        context = GatewayContext(
            method=request.method,
            path=request.url.path,
            trace_id=resolved_trace_id,
            started_at=started_at,
        )
        resolved_hook.on_request_start(request, context)
        annotate_current_span(
            execution_context,
            {
                "http.method": request.method,
                "http.route": request.url.path,
            },
        )

        logger.info("Gateway request started: %s %s", request.method, request.url.path)

        if workspace_id_header is not None and parsed_workspace_id is None:
            elapsed_ms = (perf_counter() - started_at) * 1000
            invalid_response = JSONResponse(
                status_code=400,
                content={"detail": "Invalid X-Workspace-ID header"},
            )
            resolved_hook.on_request_finish(
                request, context, invalid_response.status_code, elapsed_ms
            )
            logger.warning(
                "Gateway request rejected: %s %s status=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                invalid_response.status_code,
                elapsed_ms,
            )
            invalid_response.headers["X-Trace-ID"] = resolved_trace_id
            return invalid_response

        try:
            response = await call_next(request)
        except Exception as error:
            resolved_hook.on_request_error(request, context, error)
            logger.exception("Gateway request failed: %s %s", request.method, request.url.path)
            raise
        else:
            elapsed_ms = (perf_counter() - started_at) * 1000
            finished_execution_context = ExecutionContext(
                trace_id=resolved_trace_id,
                workspace_id=parsed_workspace_id,
                raw_workspace_id=workspace_id_header,
                workspace_valid=workspace_valid,
                runtime="api",
                component="gateway",
                operation=f"{request.method} {request.url.path}",
                request_method=request.method,
                request_path=request.url.path,
                request_status_code=response.status_code,
            )
            annotate_current_span(
                finished_execution_context,
                {
                    "http.duration_ms": elapsed_ms,
                },
            )
            resolved_hook.on_request_finish(request, context, response.status_code, elapsed_ms)
            logger.info(
                "Gateway request finished: %s %s status=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )
            response.headers["X-Trace-ID"] = resolved_trace_id
            return response
        finally:
            clear_current_execution_context()
            set_trace_id(None)
            set_workspace_id(None)
