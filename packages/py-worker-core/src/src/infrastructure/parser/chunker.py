from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

DELIMITERS = [
    "\n\n",
    "\n",
    ". ",
    "! ",
    "? ",
    ".\n",
    "!\n",
    "?\n",
    "; ",
    ": ",
    ", ",
    "",
]


@dataclass
class ChunkMetadata:
    chunk_index: int
    total_chunks: int
    source_document: str
    source_page: int | None = None
    char_offset_start: int = 0
    char_offset_end: int = 0


class RecursiveChunker:
    """Wraps LangChain's RecursiveCharacterTextSplitter with 5-level
    Chinese-aware delimiter hierarchy."""

    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 150) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            separators=DELIMITERS,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            keep_separator=True,
        )

    def split(
        self, text: str, source_document: str = "", source_page: int | None = None
    ) -> list[tuple[str, ChunkMetadata]]:
        chunks = self._splitter.split_text(text)
        results: list[tuple[str, ChunkMetadata]] = []
        for i, chunk in enumerate(chunks):
            start = text.find(chunk) if i == 0 else text.find(chunk, results[-1][1].char_offset_end)
            end = start + len(chunk) if start >= 0 else len(chunk)
            results.append(
                (
                    chunk,
                    ChunkMetadata(
                        chunk_index=i,
                        total_chunks=len(chunks),
                        source_document=source_document,
                        source_page=source_page,
                        char_offset_start=start,
                        char_offset_end=end,
                    ),
                )
            )
        return results
