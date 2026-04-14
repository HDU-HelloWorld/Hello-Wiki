import uuid


def ensure_request_id(raw_request_id: str | None) -> str:
    if raw_request_id:
        return raw_request_id
    return str(uuid.uuid4())
