from __future__ import annotations

import json
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

import pytest

from src.application.agent.agent_loop import AgentLoop
from src.application.agent.commands import AgentCommand


class RecordingHandler(BaseHTTPRequestHandler):
    response_status = 200
    response_payload: dict[str, Any] = {}
    recorded_request: dict[str, Any] | None = None
    base_url = ""

    def do_POST(self) -> None:
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        type(self).recorded_request = json.loads(body)
        payload = json.dumps(type(self).response_payload).encode("utf-8")
        self.send_response(type(self).response_status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        return None


@pytest.fixture
def agent_server() -> Iterator[type[RecordingHandler]]:
    RecordingHandler.response_status = 200
    RecordingHandler.response_payload = {}
    RecordingHandler.recorded_request = None
    server = ThreadingHTTPServer(("127.0.0.1", 0), RecordingHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    RecordingHandler.base_url = f"http://{host}:{port}"
    try:
        yield RecordingHandler
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.mark.asyncio
async def test_agent_loop_posts_to_agent_ai_and_returns_reply(
    agent_server: type[RecordingHandler],
) -> None:
    agent_server.response_payload = {"reply": "你好，可以使用 /api/v1/ingest/upload 导入文档。"}
    loop = AgentLoop(base_url=agent_server.base_url, timeout_seconds=5)

    reply = await loop.run(
        AgentCommand(
            user_input="我要导入文档",
            workspace_id="00000000-0000-0000-0000-000000000101",
            session_id="session-1",
            chat_history=[{"role": "assistant", "content": "你好"}],
        )
    )

    assert reply == "你好，可以使用 /api/v1/ingest/upload 导入文档。"
    assert agent_server.recorded_request == {
        "message": "我要导入文档",
        "workspaceId": "00000000-0000-0000-0000-000000000101",
        "sessionId": "session-1",
        "history": [{"role": "assistant", "content": "你好"}],
    }


@pytest.mark.asyncio
async def test_agent_loop_raises_on_agent_ai_failure(
    agent_server: type[RecordingHandler],
) -> None:
    agent_server.response_status = 500
    agent_server.response_payload = {"error": "bad agent"}
    loop = AgentLoop(base_url=agent_server.base_url, timeout_seconds=5)

    with pytest.raises(RuntimeError, match="bad agent"):
        await loop.run(AgentCommand(user_input="hello"))
