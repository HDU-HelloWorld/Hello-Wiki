from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from src.core.config import settings
from src.core.context import ExecutionContext, set_execution_context, set_trace_id, set_workspace_id
from src.core.logging import ContextFormatter, build_log_context, configure_logging


def test_build_log_context_prefers_execution_context():
    set_workspace_id(UUID("00000000-0000-0000-0000-000000000020"))
    set_trace_id("trace-from-contextvar")
    set_execution_context(
        ExecutionContext(
            trace_id="trace-from-execution-context",
            workspace_id=UUID("00000000-0000-0000-0000-000000000021"),
        )
    )

    context = build_log_context()

    assert context.trace_id == "trace-from-execution-context"
    assert context.workspace_id == "00000000-0000-0000-0000-000000000021"
    assert context.service_name == settings.PROJECT_NAME


def test_build_log_context_falls_back_to_defaults_when_empty():
    context = build_log_context()

    assert context.trace_id == "no-trace-id"
    assert context.workspace_id == "-"
    assert context.service_name == settings.PROJECT_NAME


def test_context_formatter_injects_default_fields():
    formatter = ContextFormatter("%(trace_id)s|%(workspace_id)s|%(service_name)s|%(message)s")
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )

    rendered = formatter.format(record)

    assert rendered == f"no-trace-id|-|{settings.PROJECT_NAME}|hello"


def test_configure_logging_adds_stream_and_file_handlers_once(
    tmp_path: Path, isolated_root_logger: logging.Logger
):
    original_log_to_file = settings.LOG_TO_FILE
    original_log_path = settings.LOG_FILE_PATH
    original_log_level = settings.LOG_LEVEL
    try:
        settings.LOG_TO_FILE = True
        settings.LOG_FILE_PATH = str(tmp_path / "backend-test.log")
        settings.LOG_LEVEL = "INFO"

        configure_logging()
        configure_logging()

        stream_handlers = [
            handler
            for handler in isolated_root_logger.handlers
            if getattr(handler, "_hello_wiki_logging", False)
        ]
        file_handlers = [
            handler
            for handler in isolated_root_logger.handlers
            if getattr(handler, "_hello_wiki_file_logging", False)
        ]

        assert len(stream_handlers) == 1
        assert len(file_handlers) == 1

        logger = logging.getLogger("tests.logging")
        logger.info("test-log-message")

        log_content = (tmp_path / "backend-test.log").read_text(encoding="utf-8")
        assert "test-log-message" in log_content
        assert "trace=" in log_content
        assert "workspace=" in log_content
    finally:
        settings.LOG_TO_FILE = original_log_to_file
        settings.LOG_FILE_PATH = original_log_path
        settings.LOG_LEVEL = original_log_level


def test_configure_logging_respects_log_level(isolated_root_logger: logging.Logger):
    original_log_to_file = settings.LOG_TO_FILE
    original_log_level = settings.LOG_LEVEL
    try:
        settings.LOG_TO_FILE = False
        settings.LOG_LEVEL = "WARNING"

        configure_logging(level="ERROR")

        assert isolated_root_logger.level == logging.ERROR
        uvicorn_logger = logging.getLogger("uvicorn")
        assert uvicorn_logger.level == logging.ERROR
    finally:
        settings.LOG_TO_FILE = original_log_to_file
        settings.LOG_LEVEL = original_log_level
