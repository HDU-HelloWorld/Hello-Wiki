from typing import Protocol
from pathlib import Path

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

from src.core.config import settings
from src.domain.ingest.constants import SUPPORTED_INGEST_EXTENSIONS

PARSER_BACKEND_CPU = "cpu"
PARSER_BACKEND_GPU = "gpu"

LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".md": UnstructuredMarkdownLoader,
    ".txt": TextLoader,
}


class DocumentLoaderPort(Protocol):
    def load(self, file_path: str) -> list[str]: ...


class DocumentLoaderAdapter:
    """Factory that selects a LangChain loader based on file extension."""

    SUPPORTED = SUPPORTED_INGEST_EXTENSIONS

    def load(self, file_path: str) -> list[str]:
        ext = Path(file_path).suffix.lower()
        if ext not in LOADER_MAP:
            raise ValueError(f"Unsupported file format: {ext}. Supported: {sorted(self.SUPPORTED)}")
        loader_cls = LOADER_MAP[ext]
        if ext == ".txt":
            docs = loader_cls(file_path, encoding="utf-8", autodetect_encoding=True).load()
        else:
            docs = loader_cls(file_path).load()
        return [d.page_content for d in docs]


def build_document_loader(parser_backend: str | None = None) -> DocumentLoaderPort:
    backend = parser_backend or settings.DOCUMENT_PARSER_BACKEND
    if backend == PARSER_BACKEND_CPU:
        return DocumentLoaderAdapter()
    if backend == PARSER_BACKEND_GPU:
        raise RuntimeError(
            "DOCUMENT_PARSER_BACKEND=gpu is configured, "
            "but the GPU document parser is not implemented yet."
        )
    raise ValueError(f"Unsupported document parser backend: {backend}")
