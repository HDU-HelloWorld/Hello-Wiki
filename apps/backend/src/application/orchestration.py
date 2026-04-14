# -*- coding: utf-8 -*-
# 编码修复: orchestration.py - 已替换Unicode符号避免Windows编码问题
from dataclasses import dataclass
from typing import Protocol

from application.compile_application import CompileApplicationService
from application.qa_application import QAApplicationService
from application.wiki_application import WikiApplicationService


class ApplicationOrchestrator(Protocol):
    def compile_document(self, source_uri: str) -> str: ...

    def ask(self, question: str) -> str: ...

    def list_pages(self, workspace_id: str) -> list[object]: ...


@dataclass(frozen=True)
class ApplicationContainer:
    """Read-only application service graph exposed to interface layers."""

    compile_service: CompileApplicationService
    qa_service: QAApplicationService
    wiki_service: WikiApplicationService


class DefaultApplicationOrchestrator(ApplicationOrchestrator):
    """Application-level orchestration that delegates to use-case services."""

    def __init__(self, container: ApplicationContainer) -> None:
        self._container = container

    def compile_document(self, source_uri: str) -> str:
        return self._container.compile_service.compile_document(source_uri=source_uri)

    def ask(self, question: str) -> str:
        return self._container.qa_service.ask(question=question)

    def list_pages(self, workspace_id: str) -> list[object]:
        return self._container.wiki_service.list_pages(workspace_id=workspace_id)
