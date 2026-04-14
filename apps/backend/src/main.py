from fastapi import FastAPI

from api.router import api_router
from core.config import settings
from infra.providers import (
    provide_application_container,
    provide_application_orchestrator,
)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Hello Wiki backend layered MVP scaffold (no business logic).",
)
application_container = provide_application_container()
app.state.application_container = application_container
app.state.application_orchestrator = provide_application_orchestrator(application_container)
app.include_router(api_router, prefix="/api")
