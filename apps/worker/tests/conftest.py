from __future__ import annotations

import logging
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

WORKER_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKER_ROOT.parents[1]
SHARED_ROOT = REPO_ROOT / "packages" / "py-worker-core" / "src"
BACKEND_ROOT = REPO_ROOT / "apps" / "backend"

sys.path.insert(0, str(SHARED_ROOT))
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(WORKER_ROOT / "src"))

from src.core import logging as logging_module
from src.core.context import clear_execution_context, set_trace_id, set_workspace_id


def reset_runtime_context() -> None:
    clear_execution_context()
    set_trace_id(None)
    set_workspace_id(None)


@pytest.fixture(autouse=True)
def isolated_runtime_context() -> Iterator[None]:
    reset_runtime_context()
    yield
    reset_runtime_context()


@pytest.fixture
def isolated_root_logger() -> Iterator[logging.Logger]:
    root = logging.getLogger()
    previous_handlers = list(root.handlers)
    previous_level = root.level

    for handler in list(root.handlers):
        root.removeHandler(handler)

    logging_module._LOGGING_CONFIGURED = False
    yield root

    for handler in list(root.handlers):
        root.removeHandler(handler)

    for handler in previous_handlers:
        root.addHandler(handler)
    root.setLevel(previous_level)
    logging_module._LOGGING_CONFIGURED = False
