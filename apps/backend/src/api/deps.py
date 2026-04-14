from typing import Annotated, Protocol

from fastapi import Depends, Header, Request

from application.compile_application import CompileApplicationService
from application.orchestration import ApplicationContainer
from application.qa_application import QAApplicationService
from application.wiki_application import WikiApplicationService
from core.auth import ScaffoldAuthenticator
from core.context import RequestContext, get_workspace_id as get_workspace_id_from_context
from core.context import set_request_context
from core.tracing import ensure_request_id


class HealthCheckPort(Protocol):
    def ping(self) -> bool: ...


def bind_workspace_context(
    x_workspace_id: Annotated[str | None, Header(alias="X-Workspace-Id")] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-Id")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> str:
    workspace_id = x_workspace_id or "default"
    principal = ScaffoldAuthenticator().authenticate(authorization)
    context = RequestContext(
        workspace_id=workspace_id,
        request_id=ensure_request_id(x_request_id),
        actor_id=principal.principal_id,
    )
    set_request_context(context)
    return workspace_id


WorkspaceId = Annotated[str, Depends(bind_workspace_context)]


def get_workspace_id() -> str:
    return get_workspace_id_from_context()


def get_application_container(request: Request) -> ApplicationContainer:
    container: ApplicationContainer = request.app.state.application_container
    return container


def get_compile_application_service(
    container: Annotated[ApplicationContainer, Depends(get_application_container)],
) -> CompileApplicationService:
    return container.compile_service


def get_qa_application_service(
    container: Annotated[ApplicationContainer, Depends(get_application_container)],
) -> QAApplicationService:
    return container.qa_service


def get_wiki_application_service(
    container: Annotated[ApplicationContainer, Depends(get_application_container)],
) -> WikiApplicationService:
    return container.wiki_service
