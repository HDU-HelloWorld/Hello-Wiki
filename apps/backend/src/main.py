from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from src.api.gateway import register_gateway_middleware
from src.api.router import api_router
from src.core.logging import configure_logging, get_logger
from src.infrastructure.observability.otel_runtime import configure_observability_runtime

logger = get_logger(__name__)


def _get_broker() -> Any:
    from src.workers.broker import broker

    return broker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("Initializing Hello Wiki Backend services...")
    broker = _get_broker()
    if not broker.is_worker_process:
        await broker.startup()

    yield

    logger.info("Shutting down Hello Wiki Backend services...")
    broker = _get_broker()
    if not broker.is_worker_process:
        await broker.shutdown()


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="ZhiYuan Backend",
        version="0.1.0",
        lifespan=lifespan,
    )

    register_gateway_middleware(app)
    configure_observability_runtime(app=app, runtime="api")

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "zhiyuan-backend"}

    return app


app = create_app()
