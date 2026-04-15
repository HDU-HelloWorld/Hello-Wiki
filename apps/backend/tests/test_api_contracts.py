from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.v1.chat import router as chat_router
from src.api.v1.ingest import router as ingest_router


def _build_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(ingest_router, prefix="/api/v1")
    return TestClient(app)


def test_chat_ask_requires_workspace_id() -> None:
    client = _build_test_client()

    response = client.post(
        "/api/v1/chat/ask",
        json={"question": "hello", "top_k": 3},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "workspace_id is required"


def test_chat_ask_returns_not_implemented() -> None:
    client = _build_test_client()

    response = client.post(
        "/api/v1/chat/ask",
        headers={"X-Workspace-ID": "00000000-0000-0000-0000-000000000101"},
        json={"question": "hello", "top_k": 3},
    )

    assert response.status_code == 501
    assert response.json()["detail"] == "chat ask endpoint is not implemented yet"


def test_chat_stream_returns_event_stream() -> None:
    client = _build_test_client()

    response = client.post(
        "/api/v1/chat/stream",
        headers={"X-Workspace-ID": "00000000-0000-0000-0000-000000000102"},
        json={"question": "hello", "top_k": 3},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: start" in response.text
    assert "event: end" in response.text


def test_ingest_compile_requires_workspace_id() -> None:
    client = _build_test_client()

    response = client.post(
        "/api/v1/ingest/compile",
        json={
            "source_document_id": "doc-1",
            "title": "Doc",
            "markdown_content": "content",
            "category": "general",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "workspace_id is required"


def test_ingest_compile_returns_not_implemented() -> None:
    client = _build_test_client()

    response = client.post(
        "/api/v1/ingest/compile",
        headers={"X-Workspace-ID": "00000000-0000-0000-0000-000000000103"},
        json={
            "source_document_id": "doc-1",
            "title": "Doc",
            "markdown_content": "content",
            "category": "general",
        },
    )

    assert response.status_code == 501
    assert response.json()["detail"] == "ingest compile endpoint is not implemented yet"
