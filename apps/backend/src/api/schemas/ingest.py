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


class IngestUploadResponse(BaseModel):
    task_id: str


class IngestStatusResponse(BaseModel):
    status: str  # pending / running / completed / failed / partial
    total_chunks: int = 0
    successful: int = 0
    failed: int = 0


class InitTagsRequest(BaseModel):
    domain: str = Field(default="general", min_length=1)
    description: str = Field(min_length=1)
    language: str = Field(default="zh")


class InitTagsResponse(BaseModel):
    domain: str
    categories: int
    leaves: int
