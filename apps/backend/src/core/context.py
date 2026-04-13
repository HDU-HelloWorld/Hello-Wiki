from contextvars import ContextVar

workspace_id_ctx: ContextVar[str] = ContextVar("workspace_id", default="default")


def set_workspace_id(workspace_id: str) -> None:
    workspace_id_ctx.set(workspace_id)


def get_workspace_id() -> str:
    return workspace_id_ctx.get()
