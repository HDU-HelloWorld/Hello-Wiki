import asyncio
import json
from urllib import error, request

from pydantic import BaseModel, Field

from src.core.config import settings


class SuggestedTag(BaseModel):
    name: str
    label: str
    description: str = ""
    parent_hint: str = ""


class EffectiveRange(BaseModel):
    start: str | None = None
    end: str | None = None
    description: str = ""
    stale_risk: str = "unknown"


class ExtractedKnowledge(BaseModel):
    """5-field REQUIRED extraction template."""

    chunk_summary: str = Field(min_length=1)
    page_title: str = Field(min_length=1)
    compiled_truth: str = Field(min_length=1)
    suggested_tags: list[SuggestedTag] = Field(min_length=2, max_length=6)
    effective_range: EffectiveRange


class TsExtractionAdapter:
    """Adapter that delegates chunk extraction to the TypeScript pi-ai HTTP gateway."""

    def __init__(self, base_url: str | None = None, timeout_seconds: float | None = None) -> None:
        self._base_url = (base_url or settings.INGEST_AI_BASE_URL).rstrip("/")
        self._timeout_seconds = timeout_seconds or settings.INGEST_AI_TIMEOUT_SECONDS

    async def extract(
        self,
        domain: str,
        chunk_text: str,
        tag_tree: str,
        source_document: str = "",
        source_page: str = "",
        chunk_index: int = 0,
        total_chunks: int = 1,
    ) -> ExtractedKnowledge:
        request = {
            "domain": domain,
            "chunkText": chunk_text,
            "tagTree": tag_tree,
            "sourceDocument": source_document,
            "sourcePage": source_page,
            "chunkIndex": chunk_index,
            "totalChunks": total_chunks,
        }
        raw_output = await asyncio.to_thread(self._post_extract, request)
        try:
            payload = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise RuntimeError("ingest-ai HTTP gateway returned invalid JSON") from exc
        return ExtractedKnowledge.model_validate(payload)

    def _post_extract(self, payload: dict[str, object]) -> str:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = request.Request(
            f"{self._base_url}/extract",
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
            raise RuntimeError(f"ingest-ai HTTP gateway request failed: {exc.reason}") from exc


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
