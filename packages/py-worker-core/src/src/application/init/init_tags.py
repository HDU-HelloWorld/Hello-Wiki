import asyncio
import json
from typing import cast
from urllib import error, request

from pydantic import BaseModel, Field

from src.application.init.commands import InitTagsCommand
from src.core.config import settings


class LeafTag(BaseModel):
    name: str
    label: str
    description: str = ""


class Category(BaseModel):
    name: str
    label: str
    description: str = ""
    leaves: list[LeafTag] = Field(default_factory=list)


class TagTreeSchema(BaseModel):
    domain: str
    generated_at: str = ""
    categories: list[Category] = Field(default_factory=list)


class InitTagsUseCase:
    """Generate initial tags through the TypeScript ingest-ai LLM gateway.

    The Python workflow remains responsible for orchestration and persistence;
    the LLM prompt/context is owned by the TS service and can be discarded.
    """

    def __init__(self, base_url: str | None = None, timeout_seconds: float | None = None) -> None:
        self._base_url = (base_url or settings.INGEST_AI_BASE_URL).rstrip("/")
        self._timeout_seconds = timeout_seconds or settings.INGEST_AI_TIMEOUT_SECONDS

    async def execute(self, command: InitTagsCommand) -> TagTreeSchema:
        payload = cast(
            dict[str, object],
            {
                "domain": command.domain,
                "description": command.description,
                "language": command.language,
                "existingTags": [],
            },
        )
        raw_output = await asyncio.to_thread(self._post_init_tags, payload)
        try:
            response = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise RuntimeError("ingest-ai init-tags gateway returned invalid JSON") from exc
        return TagTreeSchema.model_validate(response)

    def _post_init_tags(self, payload: dict[str, object]) -> str:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = request.Request(
            f"{self._base_url}/init-tags",
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
            raise RuntimeError(f"ingest-ai init-tags gateway request failed: {exc.reason}") from exc


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
