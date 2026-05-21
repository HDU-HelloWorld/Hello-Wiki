"""Minimal FastAPI server for testing — self-contained, no wiring.py."""
import os
import uuid
import tempfile
import traceback
import asyncio

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form

from src.api.schemas.agent import AgentRequest, AgentResponse
from src.api.schemas.ingest import InitTagsRequest, InitTagsResponse
from src.application.agent.agent_loop import AgentLoop
from src.application.agent.commands import AgentCommand
from src.application.agent.handlers import AgentHandler
from src.application.agent.tools.init_tags_tool import create_init_tags_tool
from src.application.ingest.commands import IngestDocumentCommand
from src.application.init.commands import InitTagsCommand
from src.application.ingest.pipeline import IngestPipelineUseCase
from src.application.ingest.handlers import IngestDocumentHandler
from src.application.init.handlers import InitTagsHandler
from src.application.init.init_tags import InitTagsUseCase
from src.core.config import settings
from src.domain.ai.provider import LLMProviderPort
from src.infrastructure.ai.providers.mock_provider import MockLLMProvider
from src.infrastructure.ai.providers.openai_compatible import OpenAICompatibleProvider
from src.infrastructure.db.repositories.knowledge_repo import KnowledgeAsyncRepository

app = FastAPI(title="Hello-Wiki Test")

TASK_STATUS: dict[str, dict] = {}


def _build_provider() -> LLMProviderPort:
    if settings.LLM_MOCK_ENABLED:
        return MockLLMProvider()
    return OpenAICompatibleProvider(
        model=settings.LLM_MODEL_NAME,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=settings.LLM_TEMPERATURE,
    )


def _build_agent_handler() -> AgentHandler:
    provider = _build_provider()
    init_use_case = InitTagsUseCase(provider)
    init_handler = InitTagsHandler(init_use_case)
    tools = [create_init_tags_tool(init_handler)]
    agent_loop = AgentLoop(provider=provider, tools=tools)
    return AgentHandler(agent_loop)


def _build_pipeline() -> IngestPipelineUseCase:
    provider = _build_provider()
    repository = KnowledgeAsyncRepository()
    return IngestPipelineUseCase(provider=provider, repository=repository)


# ── Agent ──────────────────────────────────────────────────────

@app.post("/agent/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest) -> AgentResponse:
    handler = _build_agent_handler()
    command = AgentCommand(user_input=request.message, chat_history=request.history)
    try:
        reply = await handler.handle(command)
        return AgentResponse(reply=reply)
    except Exception:
        traceback.print_exc()
        raise


# ── Init Tags ───────────────────────────────────────────────────

@app.post("/init/tags", response_model=InitTagsResponse)
async def init_tags(request: InitTagsRequest) -> InitTagsResponse:
    provider = _build_provider()
    use_case = InitTagsUseCase(provider)
    handler = InitTagsHandler(use_case)
    result = await handler.handle(InitTagsCommand(
        domain=request.domain, description=request.description,
        language=request.language,
    ))
    total_leaves = sum(len(c.leaves) for c in result.categories)
    return InitTagsResponse(domain=result.domain, categories=len(result.categories), leaves=total_leaves)


# ── Ingest ──────────────────────────────────────────────────────

@app.post("/ingest/upload")
async def ingest_upload(file: UploadFile = File(...), domain: str = Form(default="general")):
    task_id = str(uuid.uuid4())
    TASK_STATUS[task_id] = {"status": "pending", "total_chunks": 0, "successful": 0, "failed": 0}
    suffix = os.path.splitext(file.filename or ".txt")[1]
    content = await file.read()

    async def _run():
        TASK_STATUS[task_id]["status"] = "running"
        tmp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            pipeline = _build_pipeline()
            result = await pipeline.execute(IngestDocumentCommand(
                workspace_id="default", file_path=tmp_path, domain=domain,
            ))
            TASK_STATUS[task_id].update({
                "status": "completed" if result["failed"] == 0 else "partial",
                **result,
            })
        except Exception as exc:
            traceback.print_exc()
            TASK_STATUS[task_id]["status"] = "failed"
            TASK_STATUS[task_id]["error"] = str(exc)
        finally:
            if tmp_path:
                os.unlink(tmp_path)

    asyncio.create_task(_run())
    return {"task_id": task_id, "filename": file.filename}


@app.get("/ingest/status/{task_id}")
async def ingest_status(task_id: str):
    info = TASK_STATUS.get(task_id)
    if info is None:
        return {"error": "task not found"}
    return info


@app.get("/")
async def root():
    return {
        "endpoints": [
            "POST /agent/chat",
            "POST /init/tags",
            "POST /ingest/upload",
            "GET  /ingest/status/{task_id}",
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
