from pydantic import BaseModel, Field


class CompileRequest(BaseModel):
    source_document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    markdown_content: str = Field(min_length=1, description="示例字段：编译原文")
    category: str = Field(default="general", min_length=1)


class CompileResponse(BaseModel):
    title: str
    status: str
    fact_count: int
