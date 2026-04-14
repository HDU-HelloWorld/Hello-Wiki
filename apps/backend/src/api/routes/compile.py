# -*- coding: utf-8 -*-
# 编码修复: compile.py - 已替换Unicode符号避免Windows编码问题
from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.deps import get_compile_application_service
from application.compile_application import CompileApplicationService

router = APIRouter(prefix="/compile", tags=["compile"])


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def compile_document(
    app_service: Annotated[CompileApplicationService, Depends(get_compile_application_service)],
) -> dict[str, str]:
    _ = app_service.compile_document(source_uri="")
    return {"detail": "MVP scaffold only, compile workflow is not implemented."}
