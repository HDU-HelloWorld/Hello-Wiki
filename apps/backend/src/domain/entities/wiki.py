from dataclasses import dataclass


@dataclass(frozen=True)
class WikiPageEntity:
    id: int | None
    workspace_id: str
    title: str
    status: str = "draft"
