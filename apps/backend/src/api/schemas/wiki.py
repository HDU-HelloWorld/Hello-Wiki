from pydantic import BaseModel, Field


class UpsertWikiRequest(BaseModel):
    title: str = Field(min_length=1)
    category: str = Field(default="general", min_length=1)
    summary: str = Field(default="")
    content: str = Field(min_length=1)
    source_doc_id: str | None = None


class WikiResponse(BaseModel):
    title: str
    category: str
    summary: str
    status: str


class WikiListResponse(BaseModel):
    items: list[WikiResponse]
