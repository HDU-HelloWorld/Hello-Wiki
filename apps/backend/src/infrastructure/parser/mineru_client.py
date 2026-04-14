from dataclasses import dataclass


@dataclass(frozen=True)
class MinerUParseResult:
    markdown: str
    metadata: dict[str, str]


class MinerUClient:
    """Stub parser adapter; replace with real MinerU integration later."""

    def parse(self, raw_content: bytes, filename: str) -> MinerUParseResult:
        text = raw_content.decode("utf-8", errors="ignore")
        return MinerUParseResult(markdown=text, metadata={"filename": filename})
