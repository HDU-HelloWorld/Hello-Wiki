-- ============================================================================
-- Hello-Wiki Knowledge Base — Core Schema
-- ============================================================================
-- Required extensions:
--   ltree    : hierarchical label paths (materialized tree)
--   vector   : pgvector embeddings for semantic search
--   pg_trgm  : trigram indexes for fuzzy title matching
--   pgcrypto : gen_random_uuid() fallback
--   zhparser : Chinese full-text parser
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS zhparser;

-- ============================================================================
-- 1. Sources — configurable data origins (federated gateways, uploads, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sources (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    config     JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE sources IS 'Configurable data sources for multi-origin ingestion.';
COMMENT ON COLUMN sources.config IS 'Arbitrary source-level configuration (e.g. federated flags, auth).';

-- Seed the default source so foreign keys resolve out of the box.
INSERT INTO sources (id, name, config)
VALUES ('default', 'default', '{"federated": true}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 2. Knowledge domains — per-workspace domain registry (Retriever catalog)
-- ============================================================================
CREATE TABLE knowledge_domains (
    workspace_id   UUID NOT NULL,
    domain_id      TEXT NOT NULL,
    label          TEXT,
    description    TEXT,
    initialized_at TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (workspace_id, domain_id)
);

COMMENT ON TABLE knowledge_domains IS 'Queryable knowledge domains per workspace; registered on init_tags.';

-- ============================================================================
-- 3. Tags — hierarchical label tree (ltree path without domain prefix)
-- ============================================================================
CREATE TABLE tags (
    id             INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    workspace_id   UUID NOT NULL,
    domain_id      TEXT NOT NULL,
    name           VARCHAR(128) NOT NULL,
    label          VARCHAR(256),
    description    TEXT,
    parent_id      INT REFERENCES tags(id),
    level          SMALLINT NOT NULL DEFAULT 0,
    path           LTREE NOT NULL,
    document_count INT NOT NULL DEFAULT 0,
    is_leaf        BOOLEAN NOT NULL DEFAULT true,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_tags_domain
        FOREIGN KEY (workspace_id, domain_id)
        REFERENCES knowledge_domains (workspace_id, domain_id),
    CONSTRAINT uq_tags_partition_path UNIQUE (workspace_id, domain_id, path)
);

COMMENT ON TABLE tags IS 'Hierarchical tag tree. Only leaf tags should be assigned to pages.';
COMMENT ON COLUMN tags.path IS 'ltree path within domain, e.g. functional_area.registration (no domain prefix)';
COMMENT ON COLUMN tags.document_count IS 'Denormalised count of associated pages (cache for split decisions).';
COMMENT ON COLUMN tags.is_leaf IS 'Only leaf tags may be directly linked to pages.';

-- ----------------------------------------------------------------------------
-- 2a. Page–Tag junction (M:N) — deferred FK to pages (see §4).
-- ----------------------------------------------------------------------------
CREATE TABLE page_tags (
    page_id    UUID NOT NULL,
    tag_id     INT  NOT NULL REFERENCES tags(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (page_id, tag_id)
);

COMMENT ON TABLE page_tags IS 'Many-to-many link between pages and leaf tags.';

CREATE INDEX idx_page_tags_tag ON page_tags(tag_id);

-- ============================================================================
-- 4. Raw Chunks — ingested source text layer
-- ============================================================================
CREATE TABLE raw_chunks (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id     UUID NOT NULL,
    domain_id        TEXT NOT NULL,
    source_id        TEXT NOT NULL DEFAULT 'default' REFERENCES sources(id),
    original_text    TEXT NOT NULL,
    summary          TEXT,
    summary_vector   vector(1536),
    content_hash     TEXT,
    fulltext_search  tsvector GENERATED ALWAYS AS
                       (to_tsvector('zhparser', coalesce(original_text, ''))) STORED,
    source_url       TEXT,
    source_page      TEXT,
    source_document  TEXT,
    extra_metadata   JSONB,
    effective_range  tstzrange,
    last_reviewed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at       TIMESTAMPTZ,
    status           VARCHAR(32) DEFAULT 'active',
    CONSTRAINT fk_raw_chunks_domain
        FOREIGN KEY (workspace_id, domain_id)
        REFERENCES knowledge_domains (workspace_id, domain_id)
);

COMMENT ON TABLE raw_chunks IS 'Raw ingested text. Each row is one chunk from a source document.';
COMMENT ON COLUMN raw_chunks.summary IS 'Short LLM-generated summary; shared with page_timeline.source_description.';
COMMENT ON COLUMN raw_chunks.summary_vector IS 'Semantic embedding of summary (1536-d). Secondary retrieval path.';
COMMENT ON COLUMN raw_chunks.content_hash IS 'Hash of original_text — used to detect staleness and avoid redundant re-summarisation.';
COMMENT ON COLUMN raw_chunks.fulltext_search IS 'Auto-maintained tsvector for Chinese full-text search (zhparser).';
COMMENT ON COLUMN raw_chunks.effective_range IS 'Temporal validity window of this chunk.';
COMMENT ON COLUMN raw_chunks.deleted_at IS 'Soft-delete marker.';

-- Full-text search index
CREATE INDEX idx_raw_fulltext ON raw_chunks USING GIN(fulltext_search);

-- Semantic (vector) search index
CREATE INDEX idx_raw_summary_vector ON raw_chunks USING hnsw (summary_vector vector_cosine_ops);

-- Temporal range index
CREATE INDEX idx_raw_effective_range ON raw_chunks USING GIST (effective_range);

CREATE INDEX idx_raw_chunks_partition ON raw_chunks (workspace_id, domain_id);

-- ============================================================================
-- 5. Pages — compiled entity layer (the "Wiki page")
-- ============================================================================
CREATE TABLE pages (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id     UUID NOT NULL,
    domain_id        TEXT NOT NULL,
    source_id        TEXT NOT NULL DEFAULT 'default' REFERENCES sources(id),
    raw_id           UUID NOT NULL REFERENCES raw_chunks(id) ON DELETE RESTRICT,
    title            TEXT,
    compiled_truth   TEXT NOT NULL,
    truth_embedding  vector(1536),
    open_threads     JSONB,
    see_also         UUID[],
    effective_range  tstzrange,
    status           VARCHAR(32) DEFAULT 'active',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    version          INT NOT NULL DEFAULT 1,
    last_timeline_id UUID,
    deleted_at       TIMESTAMPTZ,
    CONSTRAINT fk_pages_domain
        FOREIGN KEY (workspace_id, domain_id)
        REFERENCES knowledge_domains (workspace_id, domain_id)
);

COMMENT ON TABLE pages IS 'Compiled entity — the current canonical view synthesised from raw chunks.';
COMMENT ON COLUMN pages.raw_id IS 'The raw chunk that seeded this page.';
COMMENT ON COLUMN pages.compiled_truth IS 'Dynamic summary synthesised by LLM from all attached sources.';
COMMENT ON COLUMN pages.truth_embedding IS 'Primary semantic-search vector (1536-d cosine).';
COMMENT ON COLUMN pages.open_threads IS 'Active discussion threads, e.g. ["awaiting_confirmation", "conflicts_with_v2025"].';
COMMENT ON COLUMN pages.see_also IS 'Cross-reference links to other pages (UUID array).';
COMMENT ON COLUMN pages.effective_range IS 'Merged temporal validity window across all linked raw chunks.';
COMMENT ON COLUMN pages.version IS 'Monotonic counter incremented on every compiled_truth update.';
COMMENT ON COLUMN pages.last_timeline_id IS 'Points to the most recent timeline event.';

-- Semantic search index (primary retrieval path)
CREATE INDEX idx_pages_truth_vector ON pages USING hnsw (truth_embedding vector_cosine_ops);

-- Temporal range index
CREATE INDEX idx_pages_effective_range ON pages USING GIST (effective_range);

-- Trigram index for fuzzy title lookup
CREATE INDEX idx_pages_title_trgm ON pages USING GIN (title gin_trgm_ops);

CREATE INDEX idx_pages_ws_domain_active ON pages (workspace_id, domain_id)
    WHERE deleted_at IS NULL AND status = 'active';

-- ============================================================================
-- 6. Page Timeline — append-only event log
-- ============================================================================
CREATE TABLE page_timeline (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id            UUID NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    event_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    event_type         VARCHAR(32) NOT NULL CHECK (event_type IN (
                           'creation', 'update', 'merge', 'observation', 'source_added'
                       )),
    source_raw_id      UUID REFERENCES raw_chunks(id),
    source_description TEXT,
    summary            TEXT NOT NULL
);

COMMENT ON TABLE page_timeline IS 'Append-only event log. Records every mutation to a page.';
COMMENT ON COLUMN page_timeline.event_type IS 'creation | update | merge | observation | source_added';
COMMENT ON COLUMN page_timeline.source_raw_id IS 'Optional raw chunk that triggered this event.';
COMMENT ON COLUMN page_timeline.source_description IS 'Human-readable origin description; mirrors raw_chunks.summary.';
COMMENT ON COLUMN page_timeline.summary IS 'Human-readable description of what changed and why.';

CREATE INDEX idx_timeline_page_time ON page_timeline(page_id, event_at DESC);

-- ============================================================================
-- 7. Page Versions — full snapshot of page state + triggering timeline event
-- ============================================================================
CREATE TABLE page_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id         UUID NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    version         INT NOT NULL,
    compiled_truth  TEXT NOT NULL,
    page_state      JSONB NOT NULL DEFAULT '{}',
    timeline_id     UUID NOT NULL REFERENCES page_timeline(id),
    timeline_state  JSONB NOT NULL DEFAULT '{}',
    snapshot_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE page_versions IS 'Immutable snapshot capturing the full page state and the triggering timeline event at each version bump. Enables historical audit and point-in-time rollback.';
COMMENT ON COLUMN page_versions.version IS 'Page version number at snapshot time (matches pages.version).';
COMMENT ON COLUMN page_versions.compiled_truth IS 'Core compiled truth at this version. Kept as a dedicated column for direct text comparison across versions.';
COMMENT ON COLUMN page_versions.page_state IS 'Full page state frozen at snapshot time: {title, effective_range, open_threads, see_also, status}.';
COMMENT ON COLUMN page_versions.timeline_id IS 'FK to the page_timeline event that triggered this version snapshot.';
COMMENT ON COLUMN page_versions.timeline_state IS 'Timeline event state frozen at snapshot time: {event_type, summary, source_description, event_at}.';

CREATE INDEX idx_versions_page ON page_versions(page_id, version DESC);
CREATE INDEX idx_versions_timeline ON page_versions(timeline_id);

-- ============================================================================
-- 8. Deferred foreign keys & triggers
-- ============================================================================

-- page_tags → pages FK (deferred because pages is created after page_tags)
ALTER TABLE page_tags
    ADD CONSTRAINT fk_page_tags_page
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE;

-- pages.last_timeline_id → page_timeline FK
-- SET NULL on timeline deletion so the page survives even if the event is pruned.
ALTER TABLE pages
    ADD CONSTRAINT fk_pages_last_timeline
    FOREIGN KEY (last_timeline_id) REFERENCES page_timeline(id) ON DELETE SET NULL;

-- ----------------------------------------------------------------------------
-- Trigger: auto-increment page.version and update metadata on timeline insert
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_page_on_timeline() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.event_type IN ('update', 'merge') THEN
        UPDATE pages
           SET version          = version + 1,
               updated_at       = NEW.event_at,
               last_timeline_id = NEW.id
         WHERE id = NEW.page_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_page_on_timeline() IS
    'On every creation/update/merge timeline event, bump the page version, touch updated_at, and set last_timeline_id.';

CREATE TRIGGER trg_timeline_update_page
    AFTER INSERT ON page_timeline
    FOR EACH ROW
    EXECUTE FUNCTION update_page_on_timeline();