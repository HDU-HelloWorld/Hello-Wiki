from pydantic import BaseModel, Field


class IngestUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str = "pending"


class IngestDocumentItem(BaseModel):
    document_id: str
    filename: str
    domain: str
    status: str  # pending / compiling / compiled / partial / failed
    wiki_pages: int = 0
    uploaded_at: str
    compile_task_id: str | None = None
    error: str | None = None


class IngestDocumentListResponse(BaseModel):
    items: list[IngestDocumentItem]
    total: int


class CompileDocumentJobResponse(BaseModel):
    document_id: str
    task_id: str
    status: str = "compiling"


class IngestStatusResponse(BaseModel):
    status: str  # pending / running / completed / failed / partial
    total_chunks: int = 0
    successful: int = 0
    failed: int = 0
    error: str | None = None
    errors: list[dict[str, object]] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "running",
                    "total_chunks": 0,
                    "successful": 0,
                    "failed": 0,
                    "error": None,
                },
                {
                    "status": "completed",
                    "total_chunks": 3,
                    "successful": 3,
                    "failed": 0,
                    "error": None,
                },
            ]
        }
    }


class InitTagsRequest(BaseModel):
    domain: str = Field(default="general", min_length=1)
    description: str = Field(min_length=1)
    language: str = Field(default="zh")


class InitTagsResponse(BaseModel):
    domain: str
    categories: int
    leaves: int
