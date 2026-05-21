from pathlib import Path

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".md": UnstructuredMarkdownLoader,
    ".txt": TextLoader,
}


class DocumentLoaderAdapter:
    """Factory that selects a LangChain loader based on file extension."""

    SUPPORTED = frozenset(LOADER_MAP)

    def load(self, file_path: str) -> list[str]:
        ext = Path(file_path).suffix.lower()
        if ext not in LOADER_MAP:
            raise ValueError(f"Unsupported file format: {ext}. Supported: {sorted(self.SUPPORTED)}")
        loader_cls = LOADER_MAP[ext]
        docs = loader_cls(file_path).load()
        return [d.page_content for d in docs]
