# -*- coding: utf-8 -*-
# 编码修复: scaffold_compile_service.py - 已替换Unicode符号避免Windows编码问题
from domain.ports.compile_port import CompilePort


class ScaffoldCompileService(CompilePort):
    def enqueue_compile(self, source_uri: str) -> str:
        raise NotImplementedError("Compile adapter is intentionally not implemented in MVP scaffold.")
