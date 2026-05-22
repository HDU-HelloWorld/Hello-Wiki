from fastapi import APIRouter

from src.api.v1.chat import router as chat_router
from src.api.v1.ingest import router as ingest_router
from src.api.v1.wiki import router as wiki_router
from src.api.v1.workspace import router as workspace_router
from src.api.routes.wiki import router as wiki_routes_router
from src.api.routes.versions import router as versions_router
from src.api.routes.tags import router as tags_router

api_router = APIRouter()
api_router.include_router(workspace_router)
api_router.include_router(wiki_router)
api_router.include_router(ingest_router)
api_router.include_router(chat_router)
api_router.include_router(wiki_routes_router)
api_router.include_router(versions_router)
api_router.include_router(tags_router)
