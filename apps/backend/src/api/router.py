from fastapi import APIRouter

from src.api.v1.agent import router as agent_router
from src.api.v1.ingest import router as ingest_router
from src.api.v1.init import router as init_router
from src.api.v1.retrieve import router as retrieve_router
from src.api.v1.wiki import router as wiki_router
from src.api.v1.workspace import router as workspace_router

api_router = APIRouter()
api_router.include_router(workspace_router)
api_router.include_router(wiki_router)
api_router.include_router(ingest_router)
api_router.include_router(init_router)
api_router.include_router(retrieve_router)
api_router.include_router(agent_router)
