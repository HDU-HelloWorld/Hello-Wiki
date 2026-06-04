-- Extensions auto-created on first database start
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS zhparser;

-- Chinese full-text search configuration (IF NOT EXISTS not supported for text search configs)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'zhparser') THEN
        CREATE TEXT SEARCH CONFIGURATION zhparser (PARSER = zhparser);
    END IF;
END
$$;
ALTER TEXT SEARCH CONFIGURATION zhparser
    ADD MAPPING FOR n, v, a, i, e, l WITH simple;
