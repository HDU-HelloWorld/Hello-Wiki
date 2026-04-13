from fastapi import FastAPI

from api.router import api_router
from core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Hello Wiki backend MVP scaffold (no business logic).",
)
app.include_router(api_router, prefix="/api")
