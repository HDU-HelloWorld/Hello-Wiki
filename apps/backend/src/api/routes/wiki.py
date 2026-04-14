# -*- coding: utf-8 -*-
# 编码修复: wiki.py - 已替换Unicode符号避免Windows编码问题
from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.deps import WorkspaceId, get_wiki_application_service
from application.wiki_application import WikiApplicationService

router = APIRouter(prefix="/wiki", tags=["wiki"])


@router.get("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_wiki_pages(
    workspace_id: WorkspaceId,
    app_service: Annotated[WikiApplicationService, Depends(get_wiki_application_service)],
) -> dict[str, str]:
    _ = app_service.list_pages(workspace_id=workspace_id)
    return {"detail": "MVP scaffold only, wiki listing is not implemented."}
