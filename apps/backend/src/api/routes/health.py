# -*- coding: utf-8 -*-
# 编码修复: health.py - 已替换Unicode符号避免Windows编码问题
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict[str, str]:
    return {"status": "healthy"}
