from datetime import datetime

from pydantic import BaseModel, Field


class TimeRangeRequest(BaseModel):
    start: datetime | None = None
    end: datetime | None = None


class QueryTemplateRequest(BaseModel):
    sanitize_query_for_prompt: str = Field(min_length=1)
    target_tags: list[str] = Field(default_factory=list)
    time_range: TimeRangeRequest | None = None


class SearchKnowledgeRequest(BaseModel):
    domain: str = Field(min_length=1, description="Knowledge domain id for this search")
    query: QueryTemplateRequest
    top_k: int = Field(default=10, ge=1, le=50)
    exclude_page_ids: list[str] = Field(default_factory=list, max_length=200)


class ScoreBreakdownResponse(BaseModel):
    tag_rank: int | None = None
    semantic_rank: int | None = None
    bm25_rank: int | None = None
    time_rank: int | None = None


class SearchHitResponse(BaseModel):
    page_id: str
    score: float
    title: str | None
    compiled_truth: str
    summary: str | None
    tag_paths: list[str]
    score_breakdown: ScoreBreakdownResponse


class SearchKnowledgeResponse(BaseModel):
    hits: list[SearchHitResponse]
    degraded: list[str] = Field(default_factory=list)


class RetrieveDomainItem(BaseModel):
    id: str
    label: str
    initialized: bool = False


class RetrieveDomainsResponse(BaseModel):
    domains: list[RetrieveDomainItem]
    domain_count: int = Field(ge=0)


class DomainTagTreeResponse(BaseModel):
    domain: str
    tag_tree: str = Field(default="", description="Serialized tag tree for the domain")
