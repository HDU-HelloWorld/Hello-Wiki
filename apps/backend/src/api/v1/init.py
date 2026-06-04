from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.deps import get_init_tags_handler, get_required_workspace_id
from src.api.schemas.ingest import InitTagsRequest, InitTagsResponse
from src.application.init.commands import InitTagsCommand
from src.application.init.handlers import InitTagsHandler
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/init", tags=["init"])


@router.post("/tags", response_model=InitTagsResponse)
async def init_tags(
    request: InitTagsRequest,
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: InitTagsHandler = Depends(get_init_tags_handler),
) -> InitTagsResponse:
    result = await handler.handle(
        InitTagsCommand(
            workspace_id=workspace_id,
            domain=request.domain,
            description=request.description,
            language=request.language,
        )
    )
    logger.info(
        "init.tags workspace=%s domain=%s categories=%s",
        workspace_id,
        request.domain,
        len(result.categories),
    )
    total_leaves = sum(len(category.leaves) for category in result.categories)
    return InitTagsResponse(
        domain=result.domain,
        categories=len(result.categories),
        leaves=total_leaves,
    )
