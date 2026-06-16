from __future__ import annotations

import uuid
from uuid import UUID

from src.core.context import set_trace_id, set_workspace_id


def build_trace_id(raw_trace_id: str | None) -> str:
    return raw_trace_id or str(uuid.uuid4())


def parse_workspace_id(raw_workspace_id: str | None) -> UUID | None:
    if not raw_workspace_id:
        return None
    try:
        return uuid.UUID(raw_workspace_id)
    except ValueError:
        return None


def apply_request_context(trace_id: str | None, workspace_id: str | None) -> str:
    resolved_trace_id = build_trace_id(trace_id)
    set_trace_id(resolved_trace_id)
    set_workspace_id(None)

    resolved_workspace_id = parse_workspace_id(workspace_id)
    if resolved_workspace_id:
        set_workspace_id(resolved_workspace_id)

    return resolved_trace_id


def apply_async_context(trace_id: str | None, workspace_id: UUID | str | None = None) -> str:
    resolved_trace_id = build_trace_id(trace_id)
    set_trace_id(resolved_trace_id)

    if isinstance(workspace_id, UUID):
        set_workspace_id(workspace_id)
    elif isinstance(workspace_id, str):
        set_workspace_id(parse_workspace_id(workspace_id))
    else:
        set_workspace_id(None)

    return resolved_trace_id
