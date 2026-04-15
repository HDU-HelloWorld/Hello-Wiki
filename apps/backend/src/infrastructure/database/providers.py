# -*- coding: utf-8 -*-
# 编码修复: providers.py - 已替换Unicode符号避免Windows编码问题
from application.compile_application import CompileApplicationService
from application.orchestration import (
    ApplicationContainer,
    ApplicationOrchestrator,
    DefaultApplicationOrchestrator,
)
from application.qa_application import QAApplicationService
from application.wiki_application import WikiApplicationService
from domain.services.wiki_domain_service import WikiDomainService
from infrastructure.database.repositories.scaffold_wiki_repository import ScaffoldWikiRepository
from infrastructure.database.services.scaffold_compile_service import ScaffoldCompileService
from infrastructure.database.services.scaffold_qa_service import ScaffoldQAService


def provide_compile_application_service() -> CompileApplicationService:
    return CompileApplicationService(compile_port=ScaffoldCompileService())


def provide_qa_application_service() -> QAApplicationService:
    return QAApplicationService(qa_port=ScaffoldQAService())


def provide_wiki_application_service() -> WikiApplicationService:
    return WikiApplicationService(
        repository=ScaffoldWikiRepository(),
        domain_service=WikiDomainService(),
    )


def provide_application_container() -> ApplicationContainer:
    return ApplicationContainer(
        compile_service=provide_compile_application_service(),
        qa_service=provide_qa_application_service(),
        wiki_service=provide_wiki_application_service(),
    )


def provide_application_orchestrator(
    container: ApplicationContainer,
) -> ApplicationOrchestrator:
    return DefaultApplicationOrchestrator(container=container)
