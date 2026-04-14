from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.api.gateway import (
    CompositeGatewayHook,
    build_default_gateway_hook,
    register_gateway_middleware,
)
from src.core.context import get_execution_context, get_trace_id, get_workspace_id
from tests.helpers import RecordingGatewayHook


def _build_app_with_hook(hook: RecordingGatewayHook) -> FastAPI:
    app = FastAPI()
    register_gateway_middleware(app, hook=hook)

    @app.get("/ok")
    async def ok(request: Request):
        context = get_execution_context()
        return {
            "trace_id": get_trace_id(),
            "workspace_id": str(get_workspace_id()) if get_workspace_id() else None,
            "context_operation": context.operation if context else None,
            "raw_workspace_id": context.raw_workspace_id if context else None,
            "workspace_valid": context.workspace_valid if context else None,
            "state_workspace_valid": getattr(request.state, "workspace_valid", None),
        }

    @app.get("/boom")
    async def boom():
        raise RuntimeError("intentional")

    return app


def test_build_default_gateway_hook_contains_expected_extensions():
    hook = build_default_gateway_hook()

    assert isinstance(hook, CompositeGatewayHook)
    assert len(hook._hooks) == 5  # noqa: SLF001


def test_gateway_injects_trace_workspace_and_triggers_hook_events():
    recorder = RecordingGatewayHook()
    app = _build_app_with_hook(recorder)
    client = TestClient(app)

    workspace_id = "00000000-0000-0000-0000-000000000010"
    response = client.get(
        "/ok",
        headers={
            "X-Trace-ID": "trace-gateway-001",
            "X-Workspace-ID": workspace_id,
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Trace-ID"] == "trace-gateway-001"
    assert response.json()["trace_id"] == "trace-gateway-001"
    assert response.json()["workspace_id"] == workspace_id
    assert response.json()["context_operation"] == "GET /ok"
    assert response.json()["raw_workspace_id"] == workspace_id
    assert response.json()["workspace_valid"] is True
    assert response.json()["state_workspace_valid"] is True

    assert [event.kind for event in recorder.events] == ["start", "finish"]
    assert recorder.events[1].status_code == 200
    assert recorder.events[1].duration_ms is not None and recorder.events[1].duration_ms >= 0

    assert get_execution_context() is None
    assert get_workspace_id() is None
    assert get_trace_id() == "no-trace-id"


def test_gateway_generates_trace_id_when_missing():
    recorder = RecordingGatewayHook()
    app = _build_app_with_hook(recorder)
    client = TestClient(app)

    response = client.get("/ok")

    assert response.status_code == 200
    generated_trace_id = response.headers["X-Trace-ID"]
    assert UUID(generated_trace_id)
    assert response.json()["trace_id"] == generated_trace_id
    assert [event.kind for event in recorder.events] == ["start", "finish"]


def test_gateway_keeps_raw_workspace_id_when_invalid():
    recorder = RecordingGatewayHook()
    app = _build_app_with_hook(recorder)
    client = TestClient(app)

    response = client.get("/ok", headers={"X-Workspace-ID": "bad-workspace-id"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid X-Workspace-ID header"
    assert [event.kind for event in recorder.events] == ["start", "finish"]
    assert recorder.events[1].status_code == 400


def test_gateway_calls_error_hook_on_exception():
    recorder = RecordingGatewayHook()
    app = _build_app_with_hook(recorder)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom")

    assert response.status_code == 500
    assert [event.kind for event in recorder.events] == ["start", "error"]
    assert recorder.events[1].error == "RuntimeError"


def test_gateway_workspace_valid_true_when_no_header():
    """边界测试：无 X-Workspace-ID header，workspace_valid 应为 True"""
    recorder = RecordingGatewayHook()
    app = _build_app_with_hook(recorder)
    client = TestClient(app)

    response = client.get("/ok")

    assert response.status_code == 200
    assert response.json()["workspace_id"] is None
    assert response.json()["raw_workspace_id"] is None
    assert response.json()["workspace_valid"] is True
    assert response.json()["state_workspace_valid"] is True


def test_gateway_workspace_valid_true_when_valid_header():
    """边界测试：有合法 UUID X-Workspace-ID header，workspace_valid 应为 True"""
    recorder = RecordingGatewayHook()
    app = _build_app_with_hook(recorder)
    client = TestClient(app)

    workspace_id = "00000000-0000-0000-0000-000000000020"
    response = client.get("/ok", headers={"X-Workspace-ID": workspace_id})

    assert response.status_code == 200
    assert response.json()["workspace_id"] == workspace_id
    assert response.json()["raw_workspace_id"] == workspace_id
    assert response.json()["workspace_valid"] is True
    assert response.json()["state_workspace_valid"] is True


def test_gateway_workspace_valid_false_when_invalid_header():
    """边界测试：有非法 X-Workspace-ID header，workspace_valid 应为 False，并返回 400"""
    recorder = RecordingGatewayHook()
    app = _build_app_with_hook(recorder)
    client = TestClient(app)

    response = client.get("/ok", headers={"X-Workspace-ID": "not-a-uuid"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid X-Workspace-ID header"
    assert recorder.events[1].status_code == 400
    assert recorder.events[1].duration_ms is not None and recorder.events[1].duration_ms >= 0
