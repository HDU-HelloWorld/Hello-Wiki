from sqlmodel import Field, SQLModel


class WikiPage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workspace_id: str = Field(index=True)
    title: str = Field(index=True)
    status: str = Field(default="draft", index=True)
