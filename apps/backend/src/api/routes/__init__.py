# API routes package
from src.api.routes.wiki import router as wiki_router
from src.api.routes.versions import router as versions_router
from src.api.routes.tags import router as tags_router

__all__ = ["wiki_router", "versions_router", "tags_router"]