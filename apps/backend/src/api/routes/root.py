# -*- coding: utf-8 -*-
# 编码修复: root.py - 已替换Unicode符号避免Windows编码问题
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
