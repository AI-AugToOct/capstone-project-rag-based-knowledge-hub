-- ---------- Extensions ----------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ---------- Identity & Membership ----------
CREATE TABLE IF NOT EXISTS employees (
  employee_id UUID PRIMARY KEY,                 -- map to Supabase auth.uid()
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  department TEXT,
  is_contractor BOOLEAN DEFAULT FALSE,
  has_clearance BOOLEAN DEFAULT FALSE,          -- for 'Restricted' docs
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS projects (
  project_id TEXT PRIMARY KEY,                  -- e.g. 'Atlas'
  name TEXT,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS employee_projects (
  employee_id UUID REFERENCES employees(employee_id) ON DELETE CASCADE,
  project_id TEXT  REFERENCES projects(project_id)  ON DELETE CASCADE,
  role TEXT,                                     -- 'viewer'|'editor'|'owner'
  PRIMARY KEY (employee_id, project_id)
);

-- (Optional groups; add later if you need them)
-- CREATE TABLE groups (...);
-- CREATE TABLE employee_groups (...);

-- ---------- External Sources & Uploads ----------
CREATE TABLE IF NOT EXISTS sources (
  source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider TEXT NOT NULL,                       -- 'notion'|'slack'|'gdrive'|...
  name TEXT,
  scope TEXT NOT NULL DEFAULT 'ORG',            -- 'ORG' | 'USER'
  owner_employee_id UUID REFERENCES employees(employee_id), -- for USER scope
  oauth_provider TEXT,
  oauth_account_id TEXT,                        -- workspace/team id
  oauth_scopes TEXT[],
  token_encrypted TEXT,                         -- encrypted token
  config JSONB,                                 -- selected roots (db ids, folder ids, channels)
  sync_cursor TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  last_synced_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS uploads (
  upload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_employee_id UUID REFERENCES employees(employee_id) NOT NULL,
  filename TEXT NOT NULL,
  blob_uri TEXT NOT NULL,                       -- Supabase Storage/S3 URL
  project_id TEXT REFERENCES projects(project_id),
  visibility TEXT NOT NULL CHECK (visibility IN ('Public','Private')),
  classification TEXT NOT NULL DEFAULT 'Internal', -- 'Internal'|'Restricted'
  status TEXT NOT NULL DEFAULT 'queued',        -- queued|processing|indexed|failed
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  indexed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ingestion_jobs (
  job_id BIGSERIAL PRIMARY KEY,
  source_id UUID REFERENCES sources(source_id),
  upload_id UUID REFERENCES uploads(upload_id),
  mode TEXT,                                    -- 'full'|'incremental'
  priority INT DEFAULT 50,                      -- 10=high, 50=normal
  status TEXT DEFAULT 'queued',                 -- queued|running|done|failed
  attempts INT DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ---------- Documents, ACL, Chunks (pgvector) ----------
CREATE TABLE IF NOT EXISTS documents (
  doc_id BIGSERIAL PRIMARY KEY,
  source_id UUID REFERENCES sources(source_id),
  external_id TEXT,                              -- provider's id (page id, file id)
  owner_employee_id UUID REFERENCES employees(employee_id), -- owner's user docs/uploads
  uri TEXT,                                      -- deep link for click-through
  title TEXT,
  mime_type TEXT,                                -- 'text/markdown','application/pdf',...
  language TEXT,                                 -- 'en','ar',...
  project_id TEXT REFERENCES projects(project_id),
  visibility TEXT NOT NULL CHECK (visibility IN ('Public','Private')),
  classification TEXT NOT NULL DEFAULT 'Internal', -- 'Internal'|'Restricted'
  owner_email TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  content_hash TEXT,                             -- hash of normalized markdown
  embedding_model TEXT DEFAULT 'bge-large-en-v1.5',
  deleted_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS documents_source_idx   ON documents(source_id);
CREATE INDEX IF NOT EXISTS documents_project_idx  ON documents(project_id);
CREATE INDEX IF NOT EXISTS documents_external_idx ON documents(external_id);

CREATE TABLE IF NOT EXISTS doc_acl (
  doc_id BIGINT REFERENCES documents(doc_id) ON DELETE CASCADE,
  allow_user UUID,
  allow_group UUID,
  allow_project TEXT,
  CHECK (allow_user IS NOT NULL OR allow_group IS NOT NULL OR allow_project IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS doc_acl_doc_idx ON doc_acl(doc_id);

-- Set dim to your embedding model (1536 is common; change if needed)
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id BIGSERIAL PRIMARY KEY,
  doc_id BIGINT REFERENCES documents(doc_id) ON DELETE CASCADE,
  section_type TEXT,                             -- 'heading'|'paragraph'|'table'|'code'|'list'|'summary'
  heading_path TEXT[],                           -- ['Handover','On-Call','Incidents']
  order_in_doc INT,
  page INT,                                      -- page/slide where applicable
  text TEXT NOT NULL,
  tsv tsvector,
  embedding VECTOR(1536),                        -- pgvector column
  token_count INT,
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_doc_order_idx  ON chunks(doc_id, order_in_doc);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx        ON chunks USING GIN (tsv);

-- ---------- Auditing ----------
CREATE TABLE IF NOT EXISTS audit_queries (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES employees(employee_id),
  query TEXT,
  used_doc_ids BIGINT[],
  created_at TIMESTAMPTZ DEFAULT now()
);
