from fastapi import APIRouter

from api.routes import compile, health, qa, root, wiki

api_router = APIRouter()
api_router.include_router(root.router)
api_router.include_router(health.router)
api_router.include_router(wiki.router)
api_router.include_router(compile.router)
api_router.include_router(qa.router)
