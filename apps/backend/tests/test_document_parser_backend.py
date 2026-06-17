from __future__ import annotations

import pytest
from test_ingest_pipeline import FakeExtractor, FakeKnowledgeRepository

from src.application.ingest.pipeline import IngestPipelineUseCase
from src.infrastructure.parser.document_loader import (
    DocumentLoaderAdapter,
    build_document_loader,
)


def test_build_document_loader_defaults_to_cpu_backend() -> None:
    loader = build_document_loader("cpu")

    assert isinstance(loader, DocumentLoaderAdapter)


def test_build_document_loader_rejects_gpu_backend_until_implemented() -> None:
    with pytest.raises(RuntimeError, match="DOCUMENT_PARSER_BACKEND=gpu"):
        build_document_loader("gpu")


def test_ingest_pipeline_accepts_injected_document_loader() -> None:
    loader = DocumentLoaderAdapter()

    pipeline = IngestPipelineUseCase(
        repository=FakeKnowledgeRepository(),
        extractor=FakeExtractor(),
        document_loader=loader,
    )

    assert pipeline._loader is loader
