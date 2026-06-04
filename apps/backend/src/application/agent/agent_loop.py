import asyncio
import json
from typing import cast
from urllib import error, request

from src.application.agent.commands import AgentCommand
from src.core.config import settings


class AgentLoop:
    """Adapter that delegates agent chat to the TypeScript pi-agent-core service."""

    def __init__(self, base_url: str | None = None, timeout_seconds: float | None = None) -> None:
        self._base_url = (base_url or settings.AGENT_AI_BASE_URL).rstrip("/")
        self._timeout_seconds = timeout_seconds or settings.AGENT_AI_TIMEOUT_SECONDS

    async def run(self, command: AgentCommand) -> str:
        payload = cast(
            dict[str, object],
            {
                "message": command.user_input,
                "workspaceId": command.workspace_id,
                "sessionId": command.session_id,
                "history": command.chat_history or [],
            },
        )
        raw_output = await asyncio.to_thread(self._post_chat, payload)
        try:
            response = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise RuntimeError("agent-ai HTTP gateway returned invalid JSON") from exc

        reply = response.get("reply") if isinstance(response, dict) else None
        if not isinstance(reply, str):
            raise RuntimeError("agent-ai HTTP gateway returned invalid reply")
        return reply

    def _post_chat(self, payload: dict[str, object]) -> str:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = request.Request(
            f"{self._base_url}/agent/chat",
            data=body,
            headers={"content-type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self._timeout_seconds) as response:
                raw: bytes = response.read()
                return raw.decode("utf-8")
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(_error_message(response_body) or str(exc)) from exc
        except error.URLError as exc:
            raise RuntimeError(f"agent-ai HTTP gateway request failed: {exc.reason}") from exc


def _error_message(response_body: str) -> str:
    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError:
        return response_body
    if isinstance(payload, dict):
        error_value = payload.get("error")
        if isinstance(error_value, str):
            return error_value
    return response_body
