import json
from collections.abc import Iterator


def sse_event(event: str, data: dict[str, object]) -> str:
    payload = json.dumps(data, ensure_ascii=True)
    return f"event: {event}\\ndata: {payload}\\n\\n"


def token_stream(text: str) -> Iterator[str]:
    yield from text.split()
