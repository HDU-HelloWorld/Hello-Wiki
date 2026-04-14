# -*- coding: utf-8 -*-
# 编码修复: tracing.py - 已替换Unicode符号避免Windows编码问题
import uuid


def ensure_request_id(raw_request_id: str | None) -> str:
    if raw_request_id:
        return raw_request_id
    return str(uuid.uuid4())
