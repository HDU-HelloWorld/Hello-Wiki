from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass

from src.core.config import settings
from src.core.context import get_execution_context, get_trace_id, get_workspace_id

_LOGGING_CONFIGURED = False


@dataclass(frozen=True)
class LogContext:
    trace_id: str
    workspace_id: str
    service_name: str


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        context = build_log_context()
        record.trace_id = context.trace_id
        record.workspace_id = context.workspace_id
        record.service_name = context.service_name
        return True


class ContextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "trace_id"):
            record.trace_id = "no-trace-id"
        if not hasattr(record, "workspace_id"):
            record.workspace_id = "-"
        if not hasattr(record, "service_name"):
            record.service_name = settings.PROJECT_NAME
        return super().format(record)


def build_log_context() -> LogContext:
    execution_context = get_execution_context()
    workspace_id = (
        execution_context.workspace_id if execution_context is not None else get_workspace_id()
    )
    return LogContext(
        trace_id=execution_context.trace_id
        if execution_context is not None and execution_context.trace_id
        else get_trace_id(),
        workspace_id=str(workspace_id) if workspace_id else "-",
        service_name=settings.PROJECT_NAME,
    )


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)


def configure_logging(level: str | None = None) -> None:
    global _LOGGING_CONFIGURED

    resolved_level = (level or settings.LOG_LEVEL).upper()
    root_logger = logging.getLogger()
    root_logger.setLevel(resolved_level)

    log_format = (
        "%(asctime)s | %(levelname)s | %(service_name)s | trace=%(trace_id)s | "
        "workspace=%(workspace_id)s | %(name)s | %(message)s"
    )

    existing_handler = None
    for handler in root_logger.handlers:
        if getattr(handler, "_hello_wiki_logging", False):
            existing_handler = handler
            break

    if existing_handler is None:
        handler = logging.StreamHandler(sys.stdout)
        handler._hello_wiki_logging = True  # type: ignore[attr-defined]
        handler.setFormatter(ContextFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S"))
        handler.addFilter(ContextFilter())
        root_logger.addHandler(handler)
    else:
        existing_handler.setFormatter(ContextFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S"))

    if settings.LOG_TO_FILE:
        file_handler = None
        for handler in root_logger.handlers:
            if getattr(handler, "_hello_wiki_file_logging", False):
                file_handler = handler
                break

        if file_handler is None:
            log_dir = os.path.dirname(settings.LOG_FILE_PATH)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(settings.LOG_FILE_PATH)
            file_handler._hello_wiki_file_logging = True  # type: ignore[attr-defined]
            file_handler.setFormatter(ContextFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S"))
            file_handler.addFilter(ContextFilter())
            root_logger.addHandler(file_handler)
        else:
            file_handler.setFormatter(ContextFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S"))

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "taskiq"):
        logger = logging.getLogger(logger_name)
        logger.propagate = True
        logger.setLevel(resolved_level)

    logging.captureWarnings(True)
    _LOGGING_CONFIGURED = True
