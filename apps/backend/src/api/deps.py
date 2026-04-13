from typing import Protocol


class HealthCheckPort(Protocol):
    def ping(self) -> bool: ...


def get_workspace_id() -> str:
    # Static placeholder for MVP wiring only.
    return "default"
