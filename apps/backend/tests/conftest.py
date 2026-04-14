from __future__ import annotations

import logging
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core import logging as logging_module
from tests.helpers import reset_runtime_context


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
