from __future__ import annotations

import json
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

import pytest

from src.infrastructure.ai.extraction_adapter import TsExtractionAdapter


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
def extraction_server() -> Iterator[type[RecordingHandler]]:
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
async def test_ts_extraction_adapter_posts_to_http_gateway_and_parses_result(
    extraction_server: type[RecordingHandler],
) -> None:
    extraction_server.response_payload = {
        "chunk_summary": "summary:general",
        "page_title": "Policy Page",
        "compiled_truth": "Students may register for courses.",
        "suggested_tags": [
            {"name": "registration_course", "label": "选课注册", "parent_hint": "functional_area"},
            {"name": "academic_affairs", "label": "教务管理", "parent_hint": "functional_area"},
        ],
        "effective_range": {
            "start": "2024-09-01",
            "end": None,
            "description": "2024 academic year",
            "stale_risk": "medium",
        },
    }
    adapter = TsExtractionAdapter(
        base_url=extraction_server.base_url,
        timeout_seconds=5,
    )

    result = await adapter.extract(
        domain="general",
        chunk_text="content",
        tag_tree="functional_area",
        source_document="policy.pdf",
        source_page="1",
        chunk_index=0,
        total_chunks=1,
    )

    assert result.chunk_summary == "summary:general"
    assert result.page_title == "Policy Page"
    assert result.effective_range.start == "2024-09-01"
    assert extraction_server.recorded_request is not None
    assert extraction_server.recorded_request["domain"] == "general"
    assert extraction_server.recorded_request["chunkText"] == "content"


@pytest.mark.asyncio
async def test_ts_extraction_adapter_raises_on_http_failure(
    extraction_server: type[RecordingHandler],
) -> None:
    extraction_server.response_status = 500
    extraction_server.response_payload = {"error": "bad extraction"}
    adapter = TsExtractionAdapter(
        base_url=extraction_server.base_url,
        timeout_seconds=5,
    )

    with pytest.raises(RuntimeError, match="bad extraction"):
        await adapter.extract(
            domain="general",
            chunk_text="content",
            tag_tree="functional_area",
        )
