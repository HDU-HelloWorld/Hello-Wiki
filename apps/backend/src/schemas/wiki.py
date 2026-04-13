from pydantic import BaseModel


class WikiPageSummary(BaseModel):
    id: int
    title: str
    status: str
