import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TSTZRANGE, TSVECTOR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class SourceModel(Base):
    __tablename__ = "sources"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    config = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)


class TagModel(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    label = Column(String(256))
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("tags.id"))
    level = Column(SmallInteger, nullable=False, default=0)
    path = Column(Text, nullable=False)
    document_count = Column(Integer, nullable=False, default=0)
    is_leaf = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)

    __table_args__ = (UniqueConstraint("path", name="uq_tags_path"),)


class PageTagModel(Base):
    __tablename__ = "page_tags"

    page_id = Column(PG_UUID, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint("page_id", "tag_id"),
        Index("idx_page_tags_tag", "tag_id"),
    )


class RawChunkModel(Base):
    __tablename__ = "raw_chunks"

    id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    source_id = Column(Text, ForeignKey("sources.id"), nullable=False, default="default")
    original_text = Column(Text, nullable=False)
    summary = Column(Text)
    summary_vector = Column(Vector(1536))
    content_hash = Column(Text)
    fulltext_search = Column(TSVECTOR)
    source_url = Column(Text)
    source_page = Column(Text)
    source_document = Column(Text)
    extra_metadata = Column(JSONB)
    effective_range = Column(TSTZRANGE)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    deleted_at = Column(DateTime(timezone=True))
    status = Column(String(32), default="active")

    __table_args__ = (
        Index("idx_raw_fulltext", "fulltext_search", postgresql_using="gin"),
        Index(
            "idx_raw_summary_vector",
            "summary_vector",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 200},
            postgresql_ops={"summary_vector": "vector_cosine_ops"},
        ),
        Index("idx_raw_effective_range", "effective_range", postgresql_using="gist"),
    )


class PageModel(Base):
    __tablename__ = "pages"

    id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    source_id = Column(Text, ForeignKey("sources.id"), nullable=False, default="default")
    raw_id = Column(PG_UUID, ForeignKey("raw_chunks.id", ondelete="RESTRICT"), nullable=False)
    title = Column(Text)
    compiled_truth = Column(Text, nullable=False)
    truth_embedding = Column(Vector(1536))
    open_threads = Column(JSONB)
    see_also = Column(Text)  # UUID[] stored as text, parsed at app layer
    effective_range = Column(TSTZRANGE)
    status = Column(String(32), default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    version = Column(Integer, nullable=False, default=1)
    last_timeline_id = Column(PG_UUID)
    deleted_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index(
            "idx_pages_truth_vector",
            "truth_embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 200},
            postgresql_ops={"truth_embedding": "vector_cosine_ops"},
        ),
        Index("idx_pages_effective_range", "effective_range", postgresql_using="gist"),
        Index(
            "idx_pages_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
    )


class PageTimelineModel(Base):
    __tablename__ = "page_timeline"

    id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    page_id = Column(PG_UUID, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    event_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    event_type = Column(String(32), nullable=False)
    source_raw_id = Column(PG_UUID, ForeignKey("raw_chunks.id"))
    source_description = Column(Text)
    summary = Column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('creation','update','merge','observation','source_added')",
            name="page_timeline_event_type_check",
        ),
        Index("idx_timeline_page_time", "page_id", "event_at"),
    )


class PageVersionModel(Base):
    __tablename__ = "page_versions"

    id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    page_id = Column(PG_UUID, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    compiled_truth = Column(Text, nullable=False)
    page_state = Column(JSONB, nullable=False, default={})
    timeline_id = Column(PG_UUID, ForeignKey("page_timeline.id"), nullable=False)
    timeline_state = Column(JSONB, nullable=False, default={})
    snapshot_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)

    __table_args__ = (
        Index("idx_versions_page", "page_id", "version"),
        Index("idx_versions_timeline", "timeline_id"),
    )
