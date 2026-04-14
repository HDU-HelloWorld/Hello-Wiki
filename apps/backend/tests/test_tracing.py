from __future__ import annotations

from uuid import UUID

from src.core.context import get_trace_id, get_workspace_id
from src.core.tracing import (
    apply_async_context,
    apply_request_context,
    build_trace_id,
    parse_workspace_id,
)


def test_build_trace_id_generates_when_missing():
    trace_id = build_trace_id(None)
    assert UUID(trace_id)


def test_parse_workspace_id_handles_valid_and_invalid_values():
    valid = parse_workspace_id("00000000-0000-0000-0000-000000000050")
    invalid = parse_workspace_id("not-a-uuid")

    assert str(valid) == "00000000-0000-0000-0000-000000000050"
    assert invalid is None


def test_apply_request_context_sets_trace_and_workspace_context():
    trace_id = apply_request_context(
        "trace-request-1",
        "00000000-0000-0000-0000-000000000051",
    )

    assert trace_id == "trace-request-1"
    assert get_trace_id() == "trace-request-1"
    assert str(get_workspace_id()) == "00000000-0000-0000-0000-000000000051"


def test_apply_request_context_clears_workspace_when_header_invalid():
    trace_id = apply_request_context("trace-request-2", "bad-workspace")

    assert trace_id == "trace-request-2"
    assert get_trace_id() == "trace-request-2"
    assert get_workspace_id() is None


def test_apply_async_context_supports_uuid_and_string_workspace_ids():
    trace_id_from_uuid = apply_async_context(
        "trace-async-1",
        UUID("00000000-0000-0000-0000-000000000052"),
    )
    assert trace_id_from_uuid == "trace-async-1"
    assert get_trace_id() == "trace-async-1"
    assert str(get_workspace_id()) == "00000000-0000-0000-0000-000000000052"

    trace_id_from_str = apply_async_context(
        None,
        "00000000-0000-0000-0000-000000000053",
    )
    assert UUID(trace_id_from_str)
    assert get_trace_id() == trace_id_from_str
    assert str(get_workspace_id()) == "00000000-0000-0000-0000-000000000053"


def test_apply_async_context_clears_workspace_on_invalid_input():
    apply_async_context("trace-async-3", "invalid-workspace")

    assert get_trace_id() == "trace-async-3"
    assert get_workspace_id() is None
