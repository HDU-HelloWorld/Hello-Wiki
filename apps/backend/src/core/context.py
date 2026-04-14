# -*- coding: utf-8 -*-
# 编码修复: context.py - 已替换Unicode符号避免Windows编码问题
from contextvars import ContextVar
from dataclasses import dataclass

workspace_id_ctx: ContextVar[str] = ContextVar("workspace_id", default="default")
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="unknown-request")
actor_id_ctx: ContextVar[str] = ContextVar("actor_id", default="anonymous")


@dataclass(frozen=True)
class RequestContext:
    workspace_id: str
    request_id: str
    actor_id: str


def set_workspace_id(workspace_id: str) -> None:
    workspace_id_ctx.set(workspace_id)


def get_workspace_id() -> str:
    return workspace_id_ctx.get()


def set_request_id(request_id: str) -> None:
    request_id_ctx.set(request_id)


def get_request_id() -> str:
    return request_id_ctx.get()


def set_actor_id(actor_id: str) -> None:
    actor_id_ctx.set(actor_id)


def get_actor_id() -> str:
    return actor_id_ctx.get()


def set_request_context(context: RequestContext) -> None:
    set_workspace_id(context.workspace_id)
    set_request_id(context.request_id)
    set_actor_id(context.actor_id)


def get_request_context() -> RequestContext:
    return RequestContext(
        workspace_id=get_workspace_id(),
        request_id=get_request_id(),
        actor_id=get_actor_id(),
    )
