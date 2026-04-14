# -*- coding: utf-8 -*-
# 编码修复: qa.py - 已替换Unicode符号避免Windows编码问题
from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.deps import get_qa_application_service
from application.qa_application import QAApplicationService

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def ask_question(
    app_service: Annotated[QAApplicationService, Depends(get_qa_application_service)],
) -> dict[str, str]:
    _ = app_service.ask(question="")
    return {"detail": "MVP scaffold only, QA workflow is not implemented."}
