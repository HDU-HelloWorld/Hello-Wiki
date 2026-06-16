from pathlib import Path

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

from src.domain.ingest.constants import SUPPORTED_INGEST_EXTENSIONS

LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".md": UnstructuredMarkdownLoader,
    ".txt": TextLoader,
}


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
